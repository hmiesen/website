import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import pandas as pd

# Normalize URL: https enforced, trailing slash removed, fragments stripped
def normalize_url(url):
    parsed = urlparse(url)
    scheme = "https"
    netloc = parsed.netloc
    path = parsed.path.rstrip("/") or "/"
    path = path.lower()
    return urlunparse((scheme, netloc, path, "", "", ""))

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def is_same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc

# Get all normalized links from a page
def get_links(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for tag in soup.find_all('a', href=True):
            raw_url = urljoin(url, tag['href'])
            normalized = normalize_url(raw_url)
            if is_valid_url(normalized):
                links.add(normalized)
        return links
    except Exception as e:
        print(f"[ERROR] Skipping {url}: {e}")
        return set()

# Link checker using GET with stream=True and headers
def check_url(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LinkCheckerBot/1.0; +https://example.com/bot)"
    }

    def safe_get(url):
        try:
            session = requests.Session()
            session.max_redirects = 10
            response = session.get(url, allow_redirects=True, timeout=10, headers=headers, stream=True)
            final_url = response.url
            status = response.status_code
            response.close()
            return status, final_url
        except requests.TooManyRedirects:
            return "Too many redirects", None
        except Exception as e:
            return str(e), None

    # First try original link
    status, final = safe_get(link)

    # Retry with trailing slash if we got redirect issues
    if status == "Too many redirects" and not link.endswith("/"):
        retry_link = link + "/"
        retry_status, retry_final = safe_get(retry_link)
        if isinstance(retry_status, int) and retry_status < 400:
            return True, retry_status
        return False, retry_status

    if isinstance(status, int) and status < 400:
        return True, status
    return False, status

# Crawl the site recursively
def crawl_site(start_url):
    visited_pages = set()
    seen_links = set()
    broken_links = []
    to_visit = set([normalize_url(start_url)])

    while to_visit:
        current_url = to_visit.pop()
        print(f"[CRAWL] Visiting: {current_url}")
        visited_pages.add(current_url)

        links = get_links(current_url)
        for link in links:
            if link not in seen_links:
                seen_links.add(link)

                # Crawl deeper if it's same domain and not yet visited
                if is_same_domain(start_url, link) and link not in visited_pages:
                    to_visit.add(link)

                is_ok, status = check_url(link)
                if not is_ok:
                    # Skip 403, 999, and 429 status codes
                    if status in [403, 999, 429]:
                        print(f"[SKIPPED] {link} - Ignored status code {status}")
                        continue
                    print(f"[BROKEN] {link} - {status}")
                    broken_links.append({
                        "Source Page": current_url,
                        "Broken Link": link,
                        "Error/Status Code": status
                    })
                else:
                    print(f"[OK] {link} ({status})")

    return broken_links

# Save to Excel
def export_to_excel(data, filename="broken_links_report.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"\n[INFO] Report saved to: {filename}")

# Entry point
if __name__ == "__main__":
    website = input("Enter the website URL: ").strip()
    if website.startswith("http://"):
        website = website.replace("http://", "https://")
    broken = crawl_site(website)
    export_to_excel(broken)