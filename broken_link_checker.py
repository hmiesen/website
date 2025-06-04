import os
import asyncio
import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import namedtuple
from usp.tree import sitemap_tree_for_homepage

# Configuration constants
DOMAIN = 'https://tilburgsciencehub.com/'
SKIPPED_PREFIXES = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}
USER_AGENT = {'User-Agent': 'Mozilla/5.0'}
TOKEN = os.environ.get('GIT_TOKEN')
GITHUB_REPO = "hmiesen/website"
BROKEN_LINK = namedtuple("BrokenLink", ["page_url", "broken_url", "anchor_text", "status_code"])

class SitemapLoader:
    def __init__(self, domain):
        self.domain = domain
        self.pages = []

    def load(self, max_pages="all"):
        tree = sitemap_tree_for_homepage(self.domain)
        raw_pages = list(tree.all_pages()) if max_pages == "all" else list(tree.all_pages())[:max_pages]
        self.pages = sorted(set(page.url for page in raw_pages))
        print(f"🔍 Loaded {len(self.pages)} unique pages from sitemap")


class LinkExtractor:
    def __init__(self, domain):
        self.domain = domain
        self.all_links = []

    async def extract_links(self, pages):
        self.all_links.clear()
        timeout = ClientTimeout(total=8)
        connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            for page_url in pages:
                try:
                    async with session.get(page_url, headers=USER_AGENT) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        links = soup.find_all("a")
                        for tag in links:
                            href = tag.get("href", "")
                            if not href or href.startswith("#"):
                                continue
                            absolute = urljoin(page_url, href)
                            text = tag.get_text(strip=True)
                            if absolute != page_url:
                                self.all_links.append([page_url, absolute, text])
                except Exception as e:
                    print(f"⚠️ Failed to fetch {page_url}: {e}")

    def get_http_links(self):
        seen = set()
        valid_links = []
        for _, link, _ in self.all_links:
            if not link.startswith("http"):
                continue
            if any(link.startswith(prefix) for prefix in SKIPPED_PREFIXES):
                continue
            if any(bad in link for bad in ["mailto:", "javascript:", "linkedin.com/sharing", "twitter.com/intent"]):
                continue
            if link not in seen:
                seen.add(link)
                valid_links.append(link)
        print(f"✅ Filtered {len(valid_links)} valid HTTP links")
        return valid_links

    def split_links_by_domain(self, links):
        own_domain = urlparse(self.domain).netloc.replace("www.", "")
        internal = [url for url in links if own_domain in urlparse(url).netloc]
        external = [url for url in links if own_domain not in urlparse(url).netloc]
        return internal, external


class LinkChecker:
    def __init__(self):
        self.broken = []

    def _headers(self, url):
        if "api.github.com" in url:
            return {
                "Authorization": f"Bearer {TOKEN}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            }
        return USER_AGENT

    async def check_url(self, session, url, retries=1):
        headers = self._headers(url)
        for attempt in range(retries + 1):
            try:
                async with session.get(url, headers=headers, timeout=ClientTimeout(total=8)) as response:
                    return url, response.status
            except Exception as e:
                error = str(e)
                if attempt < retries:
                    await asyncio.sleep(1)
                else:
                    print(f"⚠️ Error fetching {url}: {error}")
                    return url, None

    async def check_all(self, urls, concurrency=10):
        semaphore = asyncio.Semaphore(concurrency)
        connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
        results = []

        async with aiohttp.ClientSession(connector=connector) as session:
            async def bound_check(url):
                async with semaphore:
                    return await self.check_url(session, url)

            tasks = [bound_check(url) for url in urls]
            for result in await asyncio.gather(*tasks):
                results.append(result)

        return results


class Reporter:
    def __init__(self, repo_url):
        self.repo_url = repo_url

    async def create_issue(self, broken_links):
        if not broken_links:
            print("✅ No broken links found.")
            return

        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"Broken Links Report - {dt}"

        own_domain = urlparse(DOMAIN).netloc.replace("www.", "")
        internal = [link for link in broken_links if own_domain in urlparse(link.broken_url).netloc]
        external = [link for link in broken_links if own_domain not in urlparse(link.broken_url).netloc]

        def format_table(links):
            rows = ["| Page URL | Broken URL | Anchor Text | Status Code |", "|---|---|---|---|"]
            for link in links:
                if link.status_code is not None:
                    rows.append(f"| {link.page_url} | {link.broken_url} | {link.anchor_text} | {link.status_code} |")
            return "\n".join(rows)

        body = ""
        if internal:
            body += "### 🔁 Internal Broken Links\n" + format_table(internal) + "\n\n"
        if external:
            body += "### 🌍 External Broken Links\n" + format_table(external) + "\n"

        data = {"title": title, "body": body[:65000]}
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.repo_url, json=data) as response:
                if response.status == 201:
                    print("✅ GitHub issue created.")
                else:
                    print(f"❌ Failed to create issue: {response.status} - {await response.text()}")


async def main():
    sitemap = SitemapLoader(DOMAIN)
    sitemap.load(max_pages="all")

    extractor = LinkExtractor(DOMAIN)
    await extractor.extract_links(sitemap.pages)
    http_links = extractor.get_http_links()

    internal_links, external_links = extractor.split_links_by_domain(http_links)

    checker = LinkChecker()
    print(f"⚡ Checking {len(internal_links)} internal links with concurrency=10...")
    internal_results = await checker.check_all(internal_links, concurrency=10)

    print(f"🐢 Checking {len(external_links)} external links with concurrency=1...")
    external_results = await checker.check_all(external_links, concurrency=1)

    all_results = internal_results + external_results
    broken_links = []
    for page_url, broken_url, anchor_text in extractor.all_links:
        for url, status in all_results:
            if broken_url == url and isinstance(status, int) and status >= 400:
                broken_links.append(BROKEN_LINK(page_url, broken_url, anchor_text, status))
                break

    reporter = Reporter(f"https://api.github.com/repos/{GITHUB_REPO}/issues")
    await reporter.create_issue(broken_links)


if __name__ == "__main__":
    asyncio.run(main())
