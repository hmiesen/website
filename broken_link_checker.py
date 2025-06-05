from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from collections import namedtuple
from urllib.parse import urlparse

# Configuration constants
DOMAIN = 'https://tilburgsciencehub.com/'
USER_AGENT = {'User-Agent': 'Mozilla/5.0'}
SKIPPED_PREFIXES = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}
USER_AGENT = {'User-Agent': 'Mozilla/5.0'}
TOKEN = os.environ.get('GIT_TOKEN')
GITHUB_REPO = "hmiesen/website"

# Data containers
list_pages_raw = []
list_pages = []
all_extracted_links = []
unique_http_links_to_check = []
broken_links_dict = {'link': [], 'statusCode': []}
broken_link_tuple = namedtuple("broken_link_tuple", ["page_url", "broken_url", "anchor_text", "status_code"])

def get_headers(url, user_agent_override=None):
    if "api.github.com" in url:
        return {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "User-Agent": user_agent_override or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        return headers

def is_skipped_for_reporting(link):
    return any(link.startswith(prefix) for prefix in SKIPPED_PREFIXES)

def split_internal_external(links, domain):
    own_domain = urlparse(domain).netloc.replace("www.", "")
    internal = [link for link in links if own_domain in urlparse(link).netloc]
    external = [link for link in links if own_domain not in urlparse(link).netloc]
    return internal, external

class SitemapLoader:
    def __init__(self, domain):
        self.domain = domain
        self.pages = []

    def load(self, max_pages="all"):
        tree = sitemap_tree_for_homepage(self.domain)
        raw_pages = list(tree.all_pages()) if max_pages == "all" else list(tree.all_pages())[:max_pages]
        self.pages = sorted(set(page.url for page in raw_pages))
        print(f"🔍 Loaded {len(self.pages)} unique pages from sitemap (limit = {max_pages})")


class LinkExtractor:
    def __init__(self, domain):
        self.domain = domain
        self.all_extracted_links = []
        self.unique_http_links_to_check = []

    async def extract_all_http_links(self, list_pages, session):
        self.all_extracted_links.clear()
        for url in list_pages:
            try:
                async with session.get(url, headers=USER_AGENT, allow_redirects=False) as response:
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
                    self.all_extracted_links.append([url, 'Same destination as page', text])
                else:
                    self.all_extracted_links.append([url, absolute_url, text])

    def filter_unique_http_links(self):
        self.unique_http_links_to_check.clear()
        seen = set()
        for _, link, _ in self.all_extracted_links:
            if not link.startswith("http") or is_skipped_for_reporting(link):
                continue
            if "linkedin.com/company" in link:
                continue
            if any(bad in link for bad in ["linkedin.com/sharing", "twitter.com/intent", "facebook.com/sharer", "mailto:", "javascript:"]):
                continue
            if link not in seen:
                self.unique_http_links_to_check.append(link)
                seen.add(link)
        print(f"✅ Filtered links: {len(self.unique_http_links_to_check)}")

    def match_broken_links(self, broken_links_dict):
        matches = []
        for page_url, broken_url, anchor_text in self.all_extracted_links:
            if broken_url in broken_links_dict['link']:
                idx = broken_links_dict['link'].index(broken_url)
                status = broken_links_dict['statusCode'][idx]
                matches.append(broken_link_tuple(page_url, broken_url, anchor_text, status))
        internal, external = split_internal_external([m.broken_url for m in matches], self.domain)
        internal_matches = [m for m in matches if m.broken_url in internal]
        external_matches = [m for m in matches if m.broken_url in external]
        return internal_matches, external_matches


class LinkErrorChecker:
    def __init__(self, domain, is_skipped_func, broken_links_dict):
        self.domain = domain
        self.is_skipped = is_skipped_func
        self.broken_links_dict = broken_links_dict

    async def check_links_for_errors(self, links_to_check):
        print(f"🚀 Checking {len(links_to_check)} URLs...")

        internal_links, external_links = split_internal_external(links_to_check, self.domain)

        print(f"⚡ Checking {len(internal_links)} internal links with concurrency=10...")
        internal_results = await self._check_all_urls(internal_links, concurrency=10)

        print(f"🐢 Checking {len(external_links)} external links with concurrency=1...")
        external_results = await self._check_all_urls(external_links, concurrency=1)

        retry_candidates = [
            r["link"] for r in external_results
            if r["statusCode"] in [403, 429, 999] or r["statusCode"] is None
        ]
        retry_results = []
        if retry_candidates:
            print(f"🔁 Retrying {len(retry_candidates)} external failures serially...")
            retry_results = await self._check_all_urls(retry_candidates, concurrency=1)

        all_results = internal_results + external_results
        all_results_map = {r["link"]: r for r in all_results}
        all_results_map.update({r["link"]: r for r in retry_results})
        results = list(all_results_map.values())

        own_domain = urlparse(self.domain).netloc.replace("www.", "")

        for result in results:
            link = result["link"]
            status = result["statusCode"]
            error = result["errorType"]

            if self.is_skipped(link):
                continue

            is_internal = own_domain in urlparse(link).netloc
            is_external = not is_internal

            if isinstance(status, int):
                if status == 403 and is_external:
                    print(f"⏭️ Skipping external 403 (likely bot protection): {link}")
                    continue
                if is_external and status == 999:
                    print(f"⏭️ Skipping external 999 (bot protection): {link}")
                    continue
                if is_internal and 400 <= status <= 599:
                    print(f"❌ Internal [{status}] {link}")
                    self.broken_links_dict['link'].append(link)
                    self.broken_links_dict['statusCode'].append(status)
                elif is_external and (status in [404, 410] or status >= 500):
                    print(f"❌ External [{status}] {link}")
                    self.broken_links_dict['link'].append(link)
                    self.broken_links_dict['statusCode'].append(status)
                else:
                    print(f"✅ [{status}] {link}")
            elif error:
                print(f"⚠️ Skipped (non-HTTP): {link} → {error}")

    async def _check_all_urls(self, urls, concurrency=10):
        timeout = ClientTimeout(total=8)
        connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_check(session, url):
            async with semaphore:
                try:
                    headers = get_headers(url)
                    return await self._check_url(session, url, headers=headers)
                except Exception as e:
                    return {"link": url, "statusCode": None, "errorType": str(e)}

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = [limited_check(session, url) for url in urls]
            return await asyncio.gather(*tasks)

    async def _check_url(self, session, url, headers):
        domain = urlparse(url).netloc.lower()
        await asyncio.sleep(0.1)

        use_head = not any(bad in domain for bad in ["linkedin.com", "akamai.net"])

        try:
            if use_head:
                try:
                    async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
                        if response.status >= 500:
                            await asyncio.sleep(1)
                            async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as retry_response:
                                return {"link": url, "statusCode": retry_response.status, "errorType": None}
                        return {"link": url, "statusCode": response.status, "errorType": None}
                except:
                    pass  # fallback

            async with session.get(url, allow_redirects=True, timeout=8, headers=headers) as response:
                return {"link": url, "statusCode": response.status, "errorType": None}

        except Exception as e:
            return {"link": url, "statusCode": None, "errorType": repr(e)}


class Reporter:
    def __init__(self, github_repo_url, token):
        self.github_repo_url = github_repo_url
        self.token = token

    async def push_issue_git_batched(self, internal_links, external_links, batch_size=500, max_issues=10):
        all_links = internal_links + external_links
        if not all_links:
            print("✅ No broken links found.")
            return

        combined = list({
            (link.page_url, link.broken_url, link.anchor_text, link.status_code): link
            for link in all_links
        }.values())
        total_batches = min((len(combined) - 1) // batch_size + 1, max_issues)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            for i in range(total_batches):
                batch = combined[i * batch_size:(i + 1) * batch_size]
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                title = f"Broken Links (Batch {i + 1}) - {dt_string}"

                internal = [link for link in batch if "tilburgsciencehub.com" in urlparse(link.broken_url).netloc]
                external = [link for link in batch if "tilburgsciencehub.com" not in urlparse(link.broken_url).netloc]

                body = f"Batch {i + 1}: {len(batch)} broken links found.\n"
                if internal:
                    body += self._build_table("🔁 Internal Broken Links", internal)
                if external:
                    body += self._build_table("🌍 External Broken Links", external)

                data = {"title": title, "body": body[:65000]}

                try:
                    async with session.post(self.github_repo_url, json=data) as resp:
                        if resp.status == 201:
                            print(f"✅ Issue created for batch {i + 1}")
                        else:
                            print(f"❌ Failed to create issue {i + 1}: {resp.status} - {await resp.text()}")
                except Exception as e:
                    print(f"❌ Error creating issue for batch {i + 1}: {str(e)}")
                await asyncio.sleep(1)

    def _build_table(self, title, entries):
        lines = [
            f"\n### {title}",
            "| Page URL | Broken Link URL | Anchor Text | Status Code |",
            "|---|---|---|---|"
        ]
        for e in entries:
            anchor = e.anchor_text.replace("\n", " ") if isinstance(e.anchor_text, str) else ""
            lines.append(f"| {e.page_url} | {e.broken_url} | {anchor} | {e.status_code} |")
        return "\n".join(lines) + "\n"

async def main_async_scraper():
    sitemap = SitemapLoader(DOMAIN)
    sitemap.load(max_pages=20)

    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)

    extractor = LinkExtractor(DOMAIN)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        await extractor.extract_all_http_links(sitemap.pages, session)

    extractor.filter_unique_http_links()

    checker = LinkErrorChecker(DOMAIN, is_skipped_for_reporting, broken_links_dict)
    await checker.check_links_for_errors(extractor.unique_http_links_to_check)

    internal_links, external_links = extractor.match_broken_links(broken_links_dict)

    reporter = Reporter(f"https://api.github.com/repos/{GITHUB_REPO}/issues", TOKEN)
    await reporter.push_issue_git_batched(internal_links, external_links)


if __name__ == "__main__":
    try:
        asyncio.run(main_async_scraper())
    except Exception as e:
        print(f"❌ Uncaught error in scraper: {e}")
        import sys
        sys.exit(1)


