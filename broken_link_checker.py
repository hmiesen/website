from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import traceback
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import time
from collections import namedtuple
from urllib.parse import urlparse

# Domain
full_domain = 'https://tilburgsciencehub.com/'

# Data containers
list_pages_raw = []
list_pages = []
all_extracted_links = []
unique_http_links_to_check = []
broken_links_dict = {'link': [], 'statusCode': []}
broken_link_tuple = namedtuple("broken_link_tuple", ["page_url", "broken_url", "anchor_text", "status_code"])

# Configs
user_agent = {'User-Agent': 'Mozilla/5.0'}
skipped_prefixes = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}

token = os.environ['GIT_TOKEN']
def get_headers(url):
    if "api.github.com" in url:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        }
    else:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

username = 'hmiesen'
repository_name = 'website'
url = f"https://api.github.com/repos/{username}/{repository_name}/issues"

def is_skipped_for_reporting(link):
    return any(link.startswith(prefix) for prefix in skipped_prefixes)

def get_pages_from_sitemap(full_domain, max_pages=10):
    list_pages_raw.clear()
    tree = sitemap_tree_for_homepage(full_domain)
    pages = tree.all_pages() if max_pages == "all" else list(tree.all_pages())[:max_pages]
    for page in pages:
        list_pages_raw.append(page.url)
    print(f"🔍 Loaded {len(list_pages_raw)} pages from sitemap (limit = {max_pages})")

def get_list_unique_pages():
    list_pages.clear()
    list_pages.extend(sorted(set(list_pages_raw)))
    print(f"🔍 Unique pages: {len(list_pages)}")

async def async_extract_all_http_links(list_pages, full_domain, session):
    all_extracted_links.clear()
    for url in list_pages:
        try:
            async with session.get(url, headers=user_agent, allow_redirects=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all("a")
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            continue

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if not href or href.startswith("#") or ('.py' in href and 'http' not in href):
                continue
            absolute_url = urljoin(url, href)
            if "github.com" in absolute_url and "/issues/new" in absolute_url:
                continue
            if absolute_url == url:
                all_extracted_links.append([url, 'Same destination as page', text])
            else:
                all_extracted_links.append([url, absolute_url, text])

def filter_unique_http_links(all_extracted_links):
    unique_http_links_to_check.clear()
    seen = set()
    for _, link, _ in all_extracted_links:
        if not link.startswith("http") or is_skipped_for_reporting(link):
            continue
        if "linkedin.com/company" in link:
            continue
        if any(bad in link for bad in ["linkedin.com/sharing", "twitter.com/intent", "facebook.com/sharer", "mailto:", "javascript:"]):
            continue
        if link not in seen:
            unique_http_links_to_check.append(link)
            seen.add(link)
    print(f"✅ Filtered links: {len(unique_http_links_to_check)}")

async def async_check_url(session, url, headers):
    domain = urlparse(url).netloc.lower()

    try:
        await asyncio.sleep(0.5)

        # For domains known to block HEAD (like LinkedIn), skip straight to GET
        use_head = not any(bad in domain for bad in ["linkedin.com", "akamai.net"])

        if use_head:
            try:
                async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
                    if response.status >= 500:
                        await asyncio.sleep(1)
                        async with session.get(url, ...) as retry_response:
                            return {"link": url, "statusCode": retry_response.status, "errorType": None}
            except:
                pass  # fallback to GET

        async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
            return {"link": url, "statusCode": response.status, "errorType": None}

    except Exception as e:
        return {"link": url, "statusCode": None, "errorType": repr(e)}

async def check_all_urls(urls, concurrency=10, user_agent=None):
    # Set timeout and connection limits
    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
    headers = user_agent or {"User-Agent": "MyBot/1.0"}

    # Semaphore limits concurrent tasks
    semaphore = asyncio.Semaphore(concurrency)

    # Inner function to wrap each request with semaphore
    async def limited_check(session, url):
        async with semaphore:
            try:
                headers = get_headers(url)
                return await async_check_url(session, url, headers=headers)
            # Capture any error to avoid crashing the run
            except Exception as e:
                return {"link": url, "statusCode": None, "errorType": str(e)}

    # Create async session and run all URL checks concurrently
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [limited_check(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def check_links_for_errors(links_to_check):
    print(f"🚀 Checking {len(links_to_check)} URLs...")

     # First pass: check all URLs concurrently
    initial_results = await check_all_urls(links_to_check, concurrency=4)

    # Identify links that failed for unclear reasons (bot protection, timeout, etc.)
    retry_candidates = [
        r["link"] for r in initial_results
        if r["statusCode"] in [403, 429, 999] or r["statusCode"] is None
    ]

    retry_results = []
    if retry_candidates:
        print(f"🔁 Retrying {len(retry_candidates)} links serially to reduce false positives...")
        # Second pass: recheck problematic links one by one (concurrency = 1)
        retry_results = await check_all_urls(retry_candidates, concurrency=1)

    # Merge results, where retry results overwrite initial results if present
    results_map = {r["link"]: r for r in initial_results}
    results_map.update({r["link"]: r for r in retry_results})
    results = list(results_map.values())

    own_domain = urlparse(full_domain).netloc.replace("www.", "")

    # Process and classify results
    for result in results:
        link = result["link"]
        status = result["statusCode"]
        error = result["errorType"]

        if is_skipped_for_reporting(link):
            continue

        is_internal = own_domain in urlparse(link).netloc
        is_external = not is_internal

        # Skip known bot protection codes
        if isinstance(status, int):
            if status == 403 and is_external:
                print(f"⏭️ Skipping external 403 (likely bot protection): {link}")
                continue
            if is_external and status == 999:
                print(f"⏭️ Skipping external 999 (bot protection): {link}")
                continue
            if is_internal and 400 <= status <= 599:
                print(f"❌ Internal [{status}] {link}")
                broken_links_dict['link'].append(link)
                broken_links_dict['statusCode'].append(status)
            elif is_external and (status in [404, 410] or status >= 500):
                print(f"❌ External [{status}] {link}")
                broken_links_dict['link'].append(link)
                broken_links_dict['statusCode'].append(status)
            else:
                print(f"✅ [{status}] {link}")
        elif error:
            print(f"⚠️ Skipped (non-HTTP): {link} → {error}")

def match_broken_links(external_links_list_raw):
    matched_broken = [
        broken_link_tuple(source, link, anchor, broken_links_dict['statusCode'][i])
        for source, link, anchor in external_links_list_raw
        for i, b in enumerate(broken_links_dict['link'])
        if link == b
    ]
    
    own_domain = urlparse(full_domain).netloc.replace("www.", "")
    
    df_internal = [entry for entry in matched_broken if own_domain in urlparse(entry.broken_url).netloc]
    df_external = [entry for entry in matched_broken if own_domain not in urlparse(entry.broken_url).netloc]
    
    return df_internal, df_external

def chunk_list(lst, chunk_size):
    """Helper to split list into chunks."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

async def push_issue_git_batched(internal_links, external_links, batch_size=500, max_issues=10):
    if not internal_links and not external_links:
        print("✅ No broken links found.")
        return

    combined = list({(link.page_url, link.broken_url, link.anchor_text, link.status_code): link for link in (internal_links + external_links)}.values())
    total_batches = min((len(combined) - 1) // batch_size + 1, max_issues)

    async with aiohttp.ClientSession(headers=get_headers(url)) as session:
        for batch_num, batch in enumerate(chunk_list(combined, batch_size)):
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            title = f'Broken Links (Batch {batch_num + 1}) - {dt_string}'

            def build_table(title, entries):
                table = f"\n### {title}\n| Page URL | Broken Link URL | Anchor Text | Status Code |\n|---|---|---|---|\n"
                for entry in entries:
                    anchortext = entry.anchor_text.replace("\n", ' ') if isinstance(entry.anchor_text, str) else ''
                    table += f"| {entry.page_url} | {entry.broken_url} | {anchortext} | {entry.status_code} |\n"
                return table

            internal_batch = [entry for entry in batch if urlparse(entry.broken_url).netloc.endswith("tilburgsciencehub.com")]
            external_batch = [entry for entry in batch if not urlparse(entry.broken_url).netloc.endswith("tilburgsciencehub.com")]

            issue_body = f"Batch {batch_num + 1}: {len(batch)} broken links found.\n"
            if internal_batch:
                issue_body += build_table("🔁 Internal Broken Links", internal_batch)
            if external_batch:
                issue_body += build_table("🌍 External Broken Links", external_batch)

            data = {"title": title, "body": issue_body[:65000]}

            try:
                async with session.post(url, json=data) as response:
                    if response.status == 201:
                        print(f"✅ Issue created for batch {batch_num + 1}")
                    else:
                        print(f"❌ Failed to create issue {batch_num + 1}: {response.status} - {await response.text()}")
            except Exception as e:
                print(f"❌ Error creating issue for batch {batch_num + 1}: {str(e)}")
            await asyncio.sleep(1)  # respect rate limit

async def main_async_scraper():
    get_pages_from_sitemap(full_domain, max_pages="all")
    get_list_unique_pages()

    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        await async_extract_all_http_links(list_pages, full_domain, session)

    filter_unique_http_links(all_extracted_links)
    await check_links_for_errors(unique_http_links_to_check)
    df_internal, df_external = match_broken_links(all_extracted_links)
    await push_issue_git_batched(df_internal, df_external)

if __name__ == "__main__":
    asyncio.run(main_async_scraper())
