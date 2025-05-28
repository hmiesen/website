from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import traceback
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import time

# Domain
full_domain = 'https://tilburgsciencehub.com/'

# Data containers
list_pages_raw = []
list_pages = []
all_extracted_links = []
unique_http_links_to_check = []
broken_links_dict = {'link': [], 'statusCode': []}

# Configs
user_agent = {'User-Agent': 'Mozilla/5.0'}
skipped_prefixes = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}

token = os.environ['GIT_TOKEN']
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json"
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
        if any(bad in link for bad in ["linkedin.com/sharing", "twitter.com/intent", "facebook.com/sharer", "mailto:", "javascript:"]):
            continue
        if link not in seen:
            unique_http_links_to_check.append(link)
            seen.add(link)
    print(f"✅ Filtered links: {len(unique_http_links_to_check)}")

async def async_check_url(session, url):
    try:
        try:
            async with session.head(url, allow_redirects=True, timeout=8) as response:
                return {"link": url, "statusCode": response.status, "errorType": None}
        except:
            async with session.get(url, allow_redirects=True, timeout=8) as response:
                return {"link": url, "statusCode": response.status, "errorType": None}
    except Exception as e:
        return {"link": url, "statusCode": None, "errorType": repr(e)}

async def check_all_urls(urls, concurrency=50):
    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=user_agent) as session:
        tasks = [async_check_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def identify_broken_links(unique_external_links):
    print(f"🚀 Checking {len(unique_external_links)} URLs...")
    results = await check_all_urls(unique_external_links, concurrency=50)

    for result in results:
        link = result["link"]
        status = result["statusCode"]
        error = result["errorType"]

        if isinstance(status, int) and 400 <= status <= 599:
            if is_skipped_for_reporting(link):
                continue
            print(f"❌ [{status}] {link}")
            broken_links_dict['link'].append(link)
            broken_links_dict['statusCode'].append(status)
        elif error:
            print(f"⚠️ {link} → {error}")

def match_broken_links(external_links_list_raw):
    matched_broken = [
        [source, link, anchor, status]
        for source, link, anchor in external_links_list_raw
        for i, b in enumerate(broken_links_dict['link'])
        if link == b and (status := broken_links_dict['statusCode'][i])
    ]
    df_all = pd.DataFrame(matched_broken, columns=["Page URL", "Broken Link URL", "Anchor Text", "statusCode"])
    own_domain = urlparse(full_domain).netloc.replace("www.", "")
    df_internal = df_all[df_all["Broken Link URL"].apply(lambda x: own_domain in urlparse(x).netloc)]
    df_external = df_all[df_all["Broken Link URL"].apply(lambda x: own_domain not in urlparse(x).netloc)]
    return df_internal, df_external

async def push_issue_git_batched(df_internal, df_external, batch_size=500, max_issues=10):
    if df_internal.empty and df_external.empty:
        print("✅ No broken links found.")
        return

    df_combined = pd.concat([df_internal, df_external], ignore_index=True).drop_duplicates()
    df_combined['statusCode'] = df_combined['statusCode'].astype(str)

    total_batches = min((len(df_combined) - 1) // batch_size + 1, max_issues)

    async with aiohttp.ClientSession(headers=headers) as session:
        for batch_num in range(total_batches):
            df_batch = df_combined.iloc[batch_num * batch_size:(batch_num + 1) * batch_size]
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            title = f'Broken Links (Batch {batch_num + 1}) - {dt_string}'

            def build_table(title, df):
                table = f"\n### {title}\n| Page URL | Broken Link URL | Anchor Text | Status Code |\n|---|---|---|---|\n"
                for _, row in df.iterrows():
                    anchortext = row['Anchor Text'].replace("\n", ' ') if isinstance(row['Anchor Text'], str) else ''
                    table += f"| {row['Page URL']} | {row['Broken Link URL']} | {anchortext} | {row['statusCode']} |\n"
                return table

            df_internal_batch = df_batch[df_batch["Broken Link URL"].apply(lambda x: urlparse(x).netloc.endswith("tilburgsciencehub.com"))]
            df_external_batch = df_batch[df_batch["Broken Link URL"].apply(lambda x: not urlparse(x).netloc.endswith("tilburgsciencehub.com"))]

            issue_body = f"Batch {batch_num + 1}: {len(df_batch)} broken links found.\n"
            if not df_internal_batch.empty:
                issue_body += build_table("🔁 Internal Broken Links", df_internal_batch)
            if not df_external_batch.empty:
                issue_body += build_table("🌍 External Broken Links", df_external_batch)

            data = {"title": title, "body": issue_body[:65000]}  # truncate if needed

            try:
                async with session.post(url, json=data) as response:
                    if response.status == 201:
                        print(f"✅ Issue created for batch {batch_num + 1}")
                    else:
                        print(f"❌ Failed to create issue {batch_num + 1}: {response.status} - {await response.text()}")
            except Exception as e:
                print(f"❌ Error creating issue for batch {batch_num + 1}: {str(e)}")
            await asyncio.sleep(1)  # respectful pause

async def main_async_scraper():
    get_pages_from_sitemap(full_domain, max_pages="all")
    get_list_unique_pages()

    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=10, ssl=False)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        await async_extract_all_http_links(list_pages, full_domain, session)

    filter_unique_http_links(all_extracted_links)
    await identify_broken_links(unique_http_links_to_check)
    df_internal, df_external = match_broken_links(all_extracted_links)
    push_issue_git_batched(df_internal, df_external)

if __name__ == "__main__":
    asyncio.run(main_async_scraper())
