from usp.tree import sitemap_tree_for_homepage
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import json
from datetime import datetime
import os
from itertools import islice
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import pandas as pd
import traceback
import asyncio
import aiohttp
from aiohttp import ClientTimeout
import time

# Domain
fullDomain = 'https://tilburgsciencehub.com/'

# Sitemap listpages
listPages_Raw = []
listPages = []

# Links on pages
allExtractedLinks = []
uniqueHttpLinksToCheck = []

# Simulate a real browser
user_agent = {'User-Agent': 'Mozilla/5.0'}

# Skip the following URL's
skippedPrefixes = {
    "https://tilburgsciencehub.com/tour",
    "https://tilburgsciencehub.com/researcher-tour",
}

def is_skipped_for_reporting(link):
    return any(link.startswith(prefix) for prefix in skippedPrefixes)

# Broken link dict
brokenLinksDict = {'link':[],'statusCode':[]}

# Git token by git secret
token = os.environ['GIT_TOKEN']

# Git headers authorization
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json"
}

# Generate target repositoryURL using Github API
username = 'hmiesen'
Repositoryname = 'website'
url = "https://api.github.com/repos/{}/{}/issues".format(username,Repositoryname)

# Github table setup
tablehead = "| Page URL | Broken Link URL | Anchor Text | Status Code |\n|---|---|---|---|\n"

## Functions
def getPagesFromSitemap(fullDomain, max_pages=10):
    listPages_Raw.clear()
    tree = sitemap_tree_for_homepage(fullDomain)

    if max_pages == "all":
        pages = tree.all_pages()
    else:
        pages = islice(tree.all_pages(), max_pages)

    for page in pages:
        listPages_Raw.append(page.url)

    print(f"🔍 Loaded {len(listPages_Raw)} pages from sitemap (limit = {max_pages})")

def getListUniquePages():
    listPages.clear()
    listPages.extend(sorted(set(listPages_Raw)))
    print(f"🔍 The following unique pages have been generated ({len(listPages)} total):")
    for page in listPages:
        print(f" - {page}")

def extractAllHttpLinks(listPages, fullDomain):
    allExtractedLinks.clear()
    
    for url in listPages:
        try:
            response = requests.get(url, headers=user_agent, allow_redirects=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all("a")
        except Exception as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            continue

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Skip anchors
            if not href or href.startswith("#") or ('.py' in href and 'http' not in href):
                continue

            # Resolve relative URLs
            absolute_url = urljoin(url, href)

            # Skip GitHub forms
            if "github.com" in absolute_url and "/issues/new" in absolute_url:
               continue

            # Skip if same as page
            if absolute_url == url:
                allExtractedLinks.append([url, 'Same destination as page', text])
            else:
                allExtractedLinks.append([url, absolute_url, text])

for entry in allExtractedLinks[:5]:
    print("🔗", entry)

def filterUniqueHttpLinks(allExtractedLinks):
    uniqueHttpLinksToCheck.clear()
    seen = set()

    for _, link, _ in allExtractedLinks:
        if not link.startswith("http"):
            continue

        if is_skipped_for_reporting(link):
            continue

        if any(bad in link for bad in [
            "linkedin.com/sharing",
            "twitter.com/intent",
            "facebook.com/sharer",
            "mailto:",
            "javascript:",
        ]):
            continue

        if link not in seen:
            uniqueHttpLinksToCheck.append(link)
            seen.add(link)

    print(f"✅ Remaining unique links after filtering: {len(uniqueHttpLinksToCheck)}")
    for link in uniqueHttpLinksToCheck:
        print("🔗", link)

# Clear previous results
brokenLinksDict.clear()
brokenLinksDict.update({'link': [], 'statusCode': []})

async def async_check_url(session, url):
    try:
        # Try HEAD-request
        try:
            async with session.head(url, allow_redirects=True, timeout=8) as response:
                return {"link": url, "statusCode": response.status, "errorType": None}
        except (aiohttp.ClientError, asyncio.TimeoutError) as head_error:
            # HEAD failed → fallback on GET
            try:
                async with session.get(url, allow_redirects=True, timeout=8) as response:
                    return {"link": url, "statusCode": response.status, "errorType": None}
            except Exception as get_error:
                return {"link": url, "statusCode": None, "errorType": f"GET error: {repr(get_error)}"}

    except asyncio.TimeoutError:
        return {"link": url, "statusCode": None, "errorType": "Timeout"}
    except aiohttp.ClientConnectorError as e:
        return {"link": url, "statusCode": None, "errorType": f"Connection error: {repr(e)}"}
    except aiohttp.ClientSSLError as e:
        return {"link": url, "statusCode": None, "errorType": f"SSL error: {repr(e)}"}
    except aiohttp.ClientResponseError as e:
        return {"link": url, "statusCode": None, "errorType": f"Invalid response: {repr(e)}"}
    except aiohttp.ClientError as e:
        return {"link": url, "statusCode": None, "errorType": f"Client error: {repr(e)}"}
    except Exception as e:
        return {"link": url, "statusCode": None, "errorType": f"Unknown error: {repr(e)}"}
    
async def check_all_urls(urls, concurrency=100):
    timeout = ClientTimeout(total=8)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency, ssl=False)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://google.com"
        }
    ) as session:
        tasks = [async_check_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

from urllib.parse import urlparse

def identifyBrokenLinks(uniqueExternalLinks):
    print(f"🚀 Starting async link check for {len(uniqueExternalLinks)} URLs...\n")

    results = asyncio.run(check_all_urls(uniqueExternalLinks, concurrency=50))

    for result in results:
        link = result["link"]
        status = result["statusCode"]
        error = result["errorType"]

        if isinstance(status, int):
            if status == 403:
                print(f"⏭️ Skipping 403 (likely bot protection): {link}")
                continue  # do not report
            elif 400 <= status <= 599:
                if is_skipped_for_reporting(link):
                    print(f"ℹ️  [{status}] {link} (ignored from reporting)")
                    continue
                print(f"❌ [{status}] {link}")
                brokenLinksDict['link'].append(link)
                brokenLinksDict['statusCode'].append(status)
            elif status in [301, 302]:
                continue  # redirects negeren
            else:
                print(f"✅ [{status}] {link}")

        elif error:
            print(f"⚠️ Skipped (non-HTTP): {link} → {error}")

# Identify unique broken links and match them to original list of all external links
def matchBrokenLinks(externalLinksListRaw):
    matched_broken = [
        [source, link, anchor, status]
        for source, link, anchor in externalLinksListRaw
        for i, b in enumerate(brokenLinksDict['link'])
        if link == b and (status := brokenLinksDict['statusCode'][i])
    ]

    all_matched = matched_broken
    df_all = pd.DataFrame(all_matched, columns=["Page URL", "Broken Link URL", "Anchor Text", "statusCode"])

    # Separate internal and external links
    own_domain = urlparse(fullDomain).netloc.replace("www.", "")
    df_internal = df_all[df_all["Broken Link URL"].apply(lambda x: own_domain in urlparse(x).netloc)]
    df_external = df_all[df_all["Broken Link URL"].apply(lambda x: own_domain not in urlparse(x).netloc)]

    print("🧪 Columns in df_external:", df_external.columns.tolist())
    print("🔢 Rows in df_external:", len(df_external))
    print(df_external.head(3))

    return df_internal, df_external

def push_issue_git_batched(df_internal, df_external, batch_size=500, max_issues=10):
    if df_internal.empty and df_external.empty:
        print("✅ No broken links found.")
        return

    df_combined = pd.concat([df_internal, df_external], ignore_index=True)
    df_combined = df_combined.reset_index(drop=True).drop_duplicates()

    if 'statusCode' not in df_combined.columns:
        print("⚠️ No 'statusCode' column found in combined DataFrame. Skipping issue creation.")
        print(f"Columns present: {df_combined.columns.tolist()}")
        return

    df_combined['statusCode'] = df_combined['statusCode'].astype(str)
    df_combined = df_combined.sort_values(by=['statusCode', 'Page URL'])

    if df_combined.empty:
        print("✅ No broken links found.")
        return

    total_batches = (len(df_combined) - 1) // batch_size + 1
    total_batches = min(total_batches, max_issues)

    for batch_num in range(total_batches):
        df_batch = df_combined.iloc[batch_num * batch_size:(batch_num + 1) * batch_size]
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        titleissue = f'Broken/Error Links (Batch {batch_num + 1}/{total_batches}) - {dt_string}'

        def build_section(title, df):
            section = f"\n### {title}\n"
            section += "| Page URL | Broken Link URL | Anchor Text | Status Code |\n"
            section += "|---|---|---|---|\n"
            for _, row in df.iterrows():
                anchortext = row['Anchor Text'].replace("\n", ' ') if isinstance(row['Anchor Text'], str) else ''
                section += f"| {row['Page URL']} | {row['Broken Link URL']} | {anchortext} | {row['statusCode']} |\n"
            return section

        df_internal_batch = df_batch[df_batch["Broken Link URL"].apply(lambda x: urlparse(x).netloc.endswith("tilburgsciencehub.com"))]
        df_external_batch = df_batch[df_batch["Broken Link URL"].apply(lambda x: not urlparse(x).netloc.endswith("tilburgsciencehub.com"))]

        table = ""
        if not df_internal_batch.empty:
            table += build_section("🔁 Internal Broken Links", df_internal_batch)
        if not df_external_batch.empty:
            table += build_section("🌍 External Broken Links", df_external_batch)

        issuebody = (
            f"Batch {batch_num + 1} of {total_batches}: {len(df_batch)} broken link(s) found.\n"
            f"The following errors were detected:\n{table}"
        )

        max_length = 65536
        if len(issuebody) > max_length:
            print(f"⚠️ Issue body exceeded 65536 characters — truncating.")
            issuebody = issuebody[:max_length - 100] + "\n\n... (truncated)"

        data = {"title": titleissue, "body": issuebody}

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                print(f'✅ Issue created for batch {batch_num + 1}/{total_batches}')
            elif response.status_code == 403 and "rate limit" in response.text.lower():
                print(f"⛔ Rate limit hit — stopping after batch {batch_num + 1}")
                break
            else:
                print(f'❌ Failed to create issue for batch {batch_num + 1}: {response.status_code} - {response.text}')
        except Exception as e:
            print(f'❌ Error for batch {batch_num + 1}: {str(e)}')
            traceback.print_exc()

        time.sleep(1)

# # Execute Functions
getPagesFromSitemap(fullDomain, max_pages="all")
getListUniquePages()
extractAllHttpLinks(listPages, fullDomain)
filterUniqueHttpLinks(allExtractedLinks)
identifyBrokenLinks(uniqueHttpLinksToCheck)
df_internal, df_external = matchBrokenLinks(allExtractedLinks)
push_issue_git_batched(df_internal, df_external)