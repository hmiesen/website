from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from collections import namedtuple

# Domain
FULL_DOMAIN = 'https://tilburgsciencehub.com/'
GITHUB_API_URL = "https://api.github.com/repos/tilburgsciencehub/website/issues"
USER_AGENT_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

# Data containers
list_pages_raw = []
list_pages = []
all_extracted_links = []
unique_http_links_to_check = []
broken_links_dict = {'link': [], 'statusCode': []}
broken_link_tuple = namedtuple("broken_link_tuple", ["page_url", "broken_url", "anchor_text", "status_code"])

# Configs
SKIPPED_PREFIXES = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}
token = os.environ['GIT_TOKEN']

def get_headers(url, user_agent_override=None):
    """
    Returns the appropriate HTTP headers based on the target URL.
    
    Args:
        url (str): The URL to determine which headers to use.
        user_agent_override (str, optional): Optional custom User-Agent string.

    Returns:
        dict: Dictionary of headers to include in the HTTP request.
    """
    if "api.github.com" in url:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        }
    return {
        "User-Agent": user_agent_override or USER_AGENT_HEADER["User-Agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

def is_skipped_for_reporting(link):
    """
    Checks whether a given link should be excluded from broken link reporting.

    Args:
        link (str): The URL to check.

    Returns:
        bool: True if the link should be skipped, False otherwise.
    """
    return any(link.startswith(prefix) for prefix in SKIPPED_PREFIXES)

def get_pages_from_sitemap(domain, max_pages=10):
    """
    Loads pages from a sitemap and populates the raw pages list.

    Args:
        domain (str): The domain to fetch the sitemap from.
        max_pages (int or str): The maximum number of pages to load, or 'all' for unlimited.
    """
    list_pages_raw.clear()
    tree = sitemap_tree_for_homepage(domain)
    pages = tree.all_pages() if max_pages == "all" else list(tree.all_pages())[:max_pages]
    list_pages_raw.extend(page.url for page in pages)
    print(f"🔍 Loaded {len(list_pages_raw)} pages from sitemap (limit = {max_pages})")

def get_list_unique_pages():
    """
    Filters the list of raw pages to only include unique entries.
    Updates the global `list_pages` variable.
    """
    list_pages.clear()
    list_pages.extend(sorted(set(list_pages_raw)))
    print(f"🔍 Unique pages: {len(list_pages)}")

async def async_extract_all_http_links(pages, domain, session):
    """
    Asynchronously extracts all HTTP links from a list of pages and stores them in the global list `all_extracted_links`.

    Args:
        pages (list): List of page URLs to scan for links.
        domain (str): The base domain (not currently used in the function but could be useful for filtering).
        session (aiohttp.ClientSession): An active aiohttp session for making asynchronous requests.
    """
    all_extracted_links.clear()
    for url in pages:
        try:
            # Attempt to fetch the page content
            async with session.get(url, headers=USER_AGENT_HEADER, allow_redirects=False) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                links = soup.find_all("a")
        except Exception as e:
            # Log and skip pages that failed to load
            print(f"⚠️ Failed to fetch {url}: {e}")
            continue

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Skip empty links, anchor links, or relative .py files
            if not href or href.startswith("#") or ('.py' in href and 'http' not in href):
                continue

            # Convert relative URLs to absolute
            absolute_url = urljoin(url, href)

            # Skip GitHub issue links for new issues
            if "github.com" in absolute_url and "/issues/new" in absolute_url:
                continue

            # If the link points to the same page, note it; otherwise, save the actual link
            if absolute_url == url:
                all_extracted_links.append([url, 'Same destination as page', text])
            else:
                all_extracted_links.append([url, absolute_url, text])

def split_internal_external(links, base_domain):
    """
    Splits a list of URLs into internal and external links based on the base domain.

    Args:
        links (list): List of URLs (strings) to be classified.
        base_domain (str): The base domain to compare against (e.g., "https://tilburgsciencehub.com").

    Returns:
        tuple: A tuple containing two lists:
            - internal (list): URLs that match the base domain.
            - external (list): URLs that do not match the base domain.
    """
    # Extract the domain part from the base URL (e.g., 'tilburgsciencehub.com')
    domain = urlparse(base_domain).netloc.replace("www.", "")
    # Classify links based on whether their domain matches the base domain
    internal = [link for link in links if domain in urlparse(link).netloc]
    external = [link for link in links if domain not in urlparse(link).netloc]
    return internal, external

def filter_unique_http_links(links):
    """
    Filters a list of extracted links to include only unique, valid HTTP(S) URLs for checking.
    Updates the global list `unique_http_links_to_check`.

    Args:
        links (list): A list of [source_url, link_url, anchor_text] entries.

    Side Effects:
        Populates the global `unique_http_links_to_check` list with filtered links.
    """
    unique_http_links_to_check.clear()
    seen = set()
    for _, link, _ in links:
        # Skip non-HTTP links or those that should not be reported
        if not link.startswith("http") or is_skipped_for_reporting(link):
            continue

        # Exclude common social media share and mailto/javascript links
        if any(x in link for x in ["linkedin.com/company", "linkedin.com/sharing", "twitter.com/intent", "facebook.com/sharer", "mailto:", "javascript:"]):
            continue

        # Add to results only if the link hasn't been seen yet
        if link not in seen:
            unique_http_links_to_check.append(link)
            seen.add(link)
    print(f"✅ Filtered links: {len(unique_http_links_to_check)}")

async def async_check_url(session, url, headers):
    """
    Asynchronously checks the HTTP status of a given URL.

    Args:
        session (aiohttp.ClientSession): An active aiohttp session used for making the request.
        url (str): The URL to check.
        headers (dict): HTTP headers to include in the request.

    Returns:
        dict: A dictionary containing:
            - 'link' (str): The original URL.
            - 'statusCode' (int or None): The HTTP response status code, if successful.
            - 'errorType' (str or None): A string representation of the exception if an error occurred.
    """
    try:
        # Throttle requests slightly to avoid rate-limiting or server overload
        await asyncio.sleep(0.1)

        # Make an HTTP GET request with redirect handling and timeout
        async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
            return {"link": url, "statusCode": response.status, "errorType": None}
        
    # Return exception info if the request fails
    except Exception as e:
        return {"link": url, "statusCode": None, "errorType": repr(e)}

async def check_all_urls(urls, concurrency=10, user_agent=None):
    """
    Asynchronously checks the status of multiple URLs with limited concurrency.

    Args:
        urls (list): List of URL strings to be checked.
        concurrency (int): Maximum number of concurrent requests per host.
        user_agent (str, optional): Optional User-Agent string to override the default.

    Returns:
        list: A list of dictionaries, each containing:
            - 'link': The checked URL.
            - 'statusCode': The HTTP status code if successful, or None.
            - 'errorType': The error description if the request failed.
    """
    # Set global timeout for each request
    timeout = ClientTimeout(total=8)

    # Limit concurrent connections per host; disable SSL verification for flexibility
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)

    # Semaphore to control total concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_check(session, url):
        # Limit the number of concurrent checks using the semaphore
        async with semaphore:
            headers = get_headers(url, user_agent_override=user_agent)
            return await async_check_url(session, url, headers)

    # Create a shared session and run all limited checks concurrently
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        return await asyncio.gather(*(limited_check(session, url) for url in urls))

async def check_links_for_errors(links_to_check):
    """
    Asynchronously checks a list of links for HTTP errors, handling internal and external links differently.
    
    Internal links are checked with higher concurrency. External links are retried if they return
    status codes often related to bot protection or rate limiting.

    Args:
        links_to_check (list): List of URL strings to check.

    Side Effects:
        - Updates the global `broken_links_dict` with broken links and their status codes.
        - Logs results to the console.
    """
    print(f"🚀 Checking {len(links_to_check)} URLs...")

    # Separate internal and external links based on the FULL_DOMAIN
    internal, external = split_internal_external(links_to_check, FULL_DOMAIN)

    # Internal links are usually more stable → higher concurrency
    print(f"⚡ Checking {len(internal)} internal links with concurrency=10...")
    internal_results = await check_all_urls(internal, concurrency=10)

    # External links are more fragile / bot-protected → lower concurrency
    print(f"🐢 Checking {len(external)} external links with concurrency=1...")
    external_results = await check_all_urls(external, concurrency=1)

    # Retry logic for known bot protection or failed checks
    retry_candidates = [
        r["link"] for r in external_results
        if r["statusCode"] in [403, 429, 999] or r["statusCode"] is None
    ]
    retry_results = await check_all_urls(retry_candidates, concurrency=1) if retry_candidates else []

    # Combine all results in a dictionary keyed by URL for easy lookup
    all_results_map = {r["link"]: r for r in internal_results + external_results}
    all_results_map.update({r["link"]: r for r in retry_results})

    domain = urlparse(FULL_DOMAIN).netloc.replace("www.", "")

    # Evaluate results
    for result in all_results_map.values():
        link, status, error = result["link"], result["statusCode"], result["errorType"]

        if is_skipped_for_reporting(link):
            continue

        is_internal = domain in urlparse(link).netloc
        is_external = not is_internal

        if isinstance(status, int):
            # Skip some external links that are likely bot-protected
            if is_external and status in [403, 999]:
                print(f"⏭️ Skipping external bot-protected: {link}")
                continue

            # Flag as broken if internal (4xx–5xx) or external (404/410/5xx)
            if (is_internal and 400 <= status < 600) or (is_external and status in [404, 410] or status >= 500):
                print(f"❌ [{status}] {link}")
                broken_links_dict['link'].append(link)
                broken_links_dict['statusCode'].append(status)
            else:
                print(f"✅ [{status}] {link}")
        elif error:
            print(f"⚠️ Skipped (non-HTTP): {link} → {error}")

def match_broken_links(raw_links):
    """
    Matches broken links from the global `broken_links_dict` with their source page and anchor text,
    based on the raw extracted links list.

    Args:
        raw_links (list): List of [source_page_url, link_url, anchor_text] entries.

    Returns:
        tuple: A tuple containing two lists:
            - internal (list): Named tuples of broken internal links.
            - external (list): Named tuples of broken external links.
    """
    # Match each broken link to its original (source, link, anchor) tuple
    matched = [
        broken_link_tuple(src, link, anchor, broken_links_dict['statusCode'][i])
        for src, link, anchor in raw_links
        for i, b in enumerate(broken_links_dict['link']) if link == b
    ]

    # Split matched links into internal and external based on FULL_DOMAIN
    domain = urlparse(FULL_DOMAIN).netloc.replace("www.", "")
    internal = [m for m in matched if domain in urlparse(m.broken_url).netloc]
    external = [m for m in matched if domain not in urlparse(m.broken_url).netloc]
    return internal, external

def chunk_list(lst, size):
    """
    Splits a list into smaller chunks of a specified size.

    Args:
        lst (list): The input list to be divided.
        size (int): The maximum size of each chunk.

    Yields:
        list: A sublist of at most `size` elements from the original list.
    """
    for i in range(0, len(lst), size):
        # Yield a slice of the list from index i to i + size
        yield lst[i:i + size]

async def push_issue_git_batched(internal_links, external_links, batch_size=500, max_issues=10):
    """
    Asynchronously pushes batched GitHub issues containing broken link reports.

    Args:
        internal_links (list): List of internal broken_link_tuple objects.
        external_links (list): List of external broken_link_tuple objects.
        batch_size (int): Maximum number of links per GitHub issue.
        max_issues (int): Maximum number of GitHub issues to create.

    Side Effects:
        - Creates GitHub issues via the GitHub API.
        - Logs success or failure to the console.
    """
    # Remove duplicates by converting to dict and back to list
    combined = list({(l.page_url, l.broken_url, l.anchor_text, l.status_code): l for l in internal_links + external_links}.values())
    if not combined:
        print("✅ No broken links found.")
        return

    # Determine how many batches (limited by max_issues)
    total_batches = min((len(combined) - 1) // batch_size + 1, max_issues)

    # Open a GitHub API session
    async with aiohttp.ClientSession(headers=get_headers(GITHUB_API_URL)) as session:
        for batch_num, batch in enumerate(chunk_list(combined, batch_size)):
            dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            title = f"Broken Links (Batch {batch_num + 1}) - {dt}"


            # Helper function: builds a markdown table for GitHub issue body
            def build_table(title, entries):
                lines = [f"\n### {title}", "| Page URL | Broken Link URL | Anchor Text | Status Code |", "|---|---|---|---|"]
                for e in entries:
                    anchortext = e.anchor_text.replace("\n", ' ') if isinstance(e.anchor_text, str) else ''
                    lines.append(f"| {e.page_url} | {e.broken_url} | {anchortext} | {e.status_code} |")
                return "\n".join(lines)

            # Separate current batch into internal vs external for clearer reporting
            internal_batch = [e for e in batch if urlparse(e.broken_url).netloc.endswith("tilburgsciencehub.com")]
            external_batch = [e for e in batch if not urlparse(e.broken_url).netloc.endswith("tilburgsciencehub.com")]

            # Build issue body text
            body = f"Batch {batch_num + 1}: {len(batch)} broken links found.\n"
            if internal_batch:
                body += build_table("🔁 Internal Broken Links", internal_batch)
            if external_batch:
                body += build_table("🌍 External Broken Links", external_batch)

            # GitHub's API limit for issue body is 65536 characters
            try:
                async with session.post(GITHUB_API_URL, json={"title": title, "body": body[:65000]}) as response:
                    if response.status == 201:
                        print(f"✅ Issue created for batch {batch_num + 1}")
                    else:
                        print(f"❌ Failed to create issue {batch_num + 1}: {response.status} - {await response.text()}")
            except Exception as e:
                print(f"❌ Error creating issue for batch {batch_num + 1}: {str(e)}")

            # Throttle issue creation to avoid hitting rate limits
            await asyncio.sleep(1)

async def main_async_scraper():
    """
    Main orchestration function for the asynchronous broken link checker.

    Workflow:
        1. Load all sitemap pages from the domain.
        2. Extract unique page URLs.
        3. Asynchronously extract all HTTP links from the pages.
        4. Filter and deduplicate relevant HTTP links for checking.
        5. Check each link for availability/errors.
        6. Match broken links back to their source locations.
        7. Push batched GitHub issues reporting the broken links.
    """
    # Step 1: Fetch all pages from the sitemap
    get_pages_from_sitemap(FULL_DOMAIN, max_pages="all")

    # Step 2: Deduplicate the list of pages
    get_list_unique_pages()

    # Step 3: Open session and extract all links from all pages
    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        await async_extract_all_http_links(list_pages, FULL_DOMAIN, session)

    # Step 4: Filter for unique and relevant HTTP links
    filter_unique_http_links(all_extracted_links)

    # Step 5: Check all filtered links for errors
    await check_links_for_errors(unique_http_links_to_check)

    # Step 6: Match broken links back to their original source pages
    internal, external = match_broken_links(all_extracted_links)

    # Step 7: Report the results via GitHub Issues in batches
    await push_issue_git_batched(internal, external)

# Run the async scraper when the script is executed directly
if __name__ == "__main__":
    asyncio.run(main_async_scraper())
