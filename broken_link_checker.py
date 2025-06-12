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
    return any(link.startswith(prefix) for prefix in SKIPPED_PREFIXES)

def get_pages_from_sitemap(domain, max_pages=10):
    list_pages_raw.clear()
    tree = sitemap_tree_for_homepage(domain)
    pages = tree.all_pages() if max_pages == "all" else list(tree.all_pages())[:max_pages]
    list_pages_raw.extend(page.url for page in pages)
    print(f"🔍 Loaded {len(list_pages_raw)} pages from sitemap (limit = {max_pages})")

def get_list_unique_pages():
    list_pages.clear()
    list_pages.extend(sorted(set(list_pages_raw)))
    print(f"🔍 Unique pages: {len(list_pages)}")

async def async_extract_all_http_links(pages, domain, session):
    all_extracted_links.clear()
    for url in pages:
        try:
            async with session.get(url, headers=USER_AGENT_HEADER, allow_redirects=False) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
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

def split_internal_external(links, base_domain):
    domain = urlparse(base_domain).netloc.replace("www.", "")
    internal = [link for link in links if domain in urlparse(link).netloc]
    external = [link for link in links if domain not in urlparse(link).netloc]
    return internal, external

def filter_unique_http_links(links):
    unique_http_links_to_check.clear()
    seen = set()
    for _, link, _ in links:
        if not link.startswith("http") or is_skipped_for_reporting(link):
            continue
        if any(x in link for x in ["linkedin.com/company", "linkedin.com/sharing", "twitter.com/intent", "facebook.com/sharer", "mailto:", "javascript:"]):
            continue
        if link not in seen:
            unique_http_links_to_check.append(link)
            seen.add(link)
    print(f"✅ Filtered links: {len(unique_http_links_to_check)}")

async def async_check_url(session, url, headers):
    try:
        await asyncio.sleep(0.1)
        async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
            return {"link": url, "statusCode": response.status, "errorType": None}
    except Exception as e:
        return {"link": url, "statusCode": None, "errorType": repr(e)}

async def check_all_urls(urls, concurrency=10, user_agent=None):
    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_check(session, url):
        async with semaphore:
            headers = get_headers(url, user_agent_override=user_agent)
            return await async_check_url(session, url, headers)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        return await asyncio.gather(*(limited_check(session, url) for url in urls))

async def check_links_for_errors(links_to_check):
    print(f"🚀 Checking {len(links_to_check)} URLs...")
    internal, external = split_internal_external(links_to_check, FULL_DOMAIN)

    print(f"⚡ Checking {len(internal)} internal links with concurrency=10...")
    internal_results = await check_all_urls(internal, concurrency=10)

    print(f"🐢 Checking {len(external)} external links with concurrency=1...")
    external_results = await check_all_urls(external, concurrency=1)

    retry_candidates = [r["link"] for r in external_results if r["statusCode"] in [403, 429, 999] or r["statusCode"] is None]
    retry_results = await check_all_urls(retry_candidates, concurrency=1) if retry_candidates else []

    all_results_map = {r["link"]: r for r in internal_results + external_results}
    all_results_map.update({r["link"]: r for r in retry_results})

    domain = urlparse(FULL_DOMAIN).netloc.replace("www.", "")

    for result in all_results_map.values():
        link, status, error = result["link"], result["statusCode"], result["errorType"]

        if is_skipped_for_reporting(link):
            continue

        is_internal = domain in urlparse(link).netloc
        is_external = not is_internal

        if isinstance(status, int):
            if is_external and status in [403, 999]:
                print(f"⏭️ Skipping external bot-protected: {link}")
                continue
            if (is_internal and 400 <= status < 600) or (is_external and status in [404, 410] or status >= 500):
                print(f"❌ [{status}] {link}")
                broken_links_dict['link'].append(link)
                broken_links_dict['statusCode'].append(status)
            else:
                print(f"✅ [{status}] {link}")
        elif error:
            print(f"⚠️ Skipped (non-HTTP): {link} → {error}")

def match_broken_links(raw_links):
    matched = [
        broken_link_tuple(src, link, anchor, broken_links_dict['statusCode'][i])
        for src, link, anchor in raw_links
        for i, b in enumerate(broken_links_dict['link']) if link == b
    ]
    domain = urlparse(FULL_DOMAIN).netloc.replace("www.", "")
    internal = [m for m in matched if domain in urlparse(m.broken_url).netloc]
    external = [m for m in matched if domain not in urlparse(m.broken_url).netloc]
    return internal, external

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

async def push_issue_git_batched(internal_links, external_links, batch_size=500, max_issues=10):
    combined = list({(l.page_url, l.broken_url, l.anchor_text, l.status_code): l for l in internal_links + external_links}.values())
    if not combined:
        print("✅ No broken links found.")
        return

    total_batches = min((len(combined) - 1) // batch_size + 1, max_issues)

    async with aiohttp.ClientSession(headers=get_headers(GITHUB_API_URL)) as session:
        for batch_num, batch in enumerate(chunk_list(combined, batch_size)):
            dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            title = f"Broken Links (Batch {batch_num + 1}) - {dt}"

            def build_table(title, entries):
                lines = [f"\n### {title}", "| Page URL | Broken Link URL | Anchor Text | Status Code |", "|---|---|---|---|"]
                for e in entries:
                    anchortext = e.anchor_text.replace("\n", ' ') if isinstance(e.anchor_text, str) else ''
                    lines.append(f"| {e.page_url} | {e.broken_url} | {anchortext} | {e.status_code} |")
                return "\n".join(lines)

            internal_batch = [e for e in batch if urlparse(e.broken_url).netloc.endswith("tilburgsciencehub.com")]
            external_batch = [e for e in batch if not urlparse(e.broken_url).netloc.endswith("tilburgsciencehub.com")]

            body = f"Batch {batch_num + 1}: {len(batch)} broken links found.\n"
            if internal_batch:
                body += build_table("🔁 Internal Broken Links", internal_batch)
            if external_batch:
                body += build_table("🌍 External Broken Links", external_batch)

            try:
                async with session.post(GITHUB_API_URL, json={"title": title, "body": body[:65000]}) as response:
                    if response.status == 201:
                        print(f"✅ Issue created for batch {batch_num + 1}")
                    else:
                        print(f"❌ Failed to create issue {batch_num + 1}: {response.status} - {await response.text()}")
            except Exception as e:
                print(f"❌ Error creating issue for batch {batch_num + 1}: {str(e)}")
            await asyncio.sleep(1)

async def main_async_scraper():
    get_pages_from_sitemap(FULL_DOMAIN, max_pages="all")
    get_list_unique_pages()

    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        await async_extract_all_http_links(list_pages, FULL_DOMAIN, session)

    filter_unique_http_links(all_extracted_links)
    await check_links_for_errors(unique_http_links_to_check)
    internal, external = match_broken_links(all_extracted_links)
    await push_issue_git_batched(internal, external)

if __name__ == "__main__":
    asyncio.run(main_async_scraper())
