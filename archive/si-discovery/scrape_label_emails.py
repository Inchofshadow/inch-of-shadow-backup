"""
scene_intelligence/scrape_label_emails.py
------------------------------------------
Scrape publicly available contact/demo emails from label websites
and Bandcamp pages. Only fetches pages the labels themselves publish.

Usage:
    python3 scene_intelligence/scrape_label_emails.py
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

CONTACTS_FILE = Path(__file__).parent / "enriched_contacts.json"
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

# Skip these common false-positive emails
SKIP_EMAILS = {
    'wixpress.com', 'sentry.io', 'cloudflare.com', 'example.com',
    'wordpress.com', 'google.com', 'apple.com', 'facebook.com',
    'twitter.com', 'instagram.com', 'youtube.com', 'schema.org',
    'w3.org', 'xmlns.com', 'jquery.com', 'mozilla.org',
    'recaptcha.net', 'gstatic.com', 'googleapis.com',
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


def is_valid_email(email: str) -> bool:
    """Filter out junk emails."""
    domain = email.split('@')[-1].lower()
    if any(skip in domain for skip in SKIP_EMAILS):
        return False
    if len(email) > 60:
        return False
    # Skip image/file extensions
    if re.search(r'\.(png|jpg|gif|svg|css|js)$', email, re.I):
        return False
    return True


def pick_best_email(emails: list) -> str:
    """Pick the most relevant email from a list."""
    demo = [e for e in emails if 'demo' in e.lower()]
    info = [e for e in emails if any(k in e.lower() for k in ('info', 'contact', 'hello', 'label', 'music', 'record'))]
    return (demo or info or emails)[0]


def fetch_page(url: str, timeout: int = 10) -> str:
    """Fetch a page, return text content or empty string."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return ""


def scrape_bandcamp(url: str) -> list:
    """Scrape a Bandcamp page for emails (about section)."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    emails = set()
    text = fetch_page(base)
    if text:
        found = EMAIL_RE.findall(text)
        emails.update(e for e in found if is_valid_email(e))

    return list(emails)


def scrape_website(url: str) -> list:
    """Scrape a label website for emails. Checks main page + common subpages."""
    if not url or 'myspace.com' in url or 'archive.org' in url or 'wikipedia' in url:
        return []

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    emails = set()

    pages = [url]
    for subpage in ('/contact', '/about', '/demos', '/demo', '/submit', '/info'):
        pages.append(base + subpage)

    for page_url in pages:
        text = fetch_page(page_url, timeout=8)
        if text:
            found = EMAIL_RE.findall(text)
            emails.update(e for e in found if is_valid_email(e))
        time.sleep(0.3)

    return list(emails)


def main():
    with open(CONTACTS_FILE) as f:
        contacts = json.load(f)

    labels = [c for c in contacts if c.get('category') == 'label' and not c.get('demo_email')]
    print(f"\nScene Intelligence -- Label Email Scraper")
    print(f"=" * 50)
    print(f"  Labels without email: {len(labels)}")
    print()

    found_count = 0
    not_found = []

    for i, c in enumerate(labels, 1):
        name = c['name']
        website = c.get('discogs_official_website') or c.get('discogs_website') or ''
        bandcamp = c.get('discogs_bandcamp') or ''

        if not website and not bandcamp:
            not_found.append(name)
            print(f"  [{i:3d}/{len(labels)}] {name:40s} -- no URLs")
            continue

        emails = []

        if website and 'myspace' not in website and 'archive.org' not in website and 'wikipedia' not in website:
            emails = scrape_website(website)

        if not emails and bandcamp:
            emails = scrape_bandcamp(bandcamp)

        if emails:
            best = pick_best_email(emails)
            c['demo_email'] = best
            found_count += 1
            all_str = ' / '.join(emails[:3])
            print(f"  [{i:3d}/{len(labels)}] {name:40s} FOUND  {all_str}")
        else:
            not_found.append(name)
            tried = []
            if website:
                tried.append('web')
            if bandcamp:
                tried.append('bc')
            print(f"  [{i:3d}/{len(labels)}] {name:40s} -- ({'+'.join(tried) or 'no URLs'})")

    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print()
    print(f"=" * 50)
    print(f"  New emails found: {found_count}")
    print(f"  Still missing: {len(not_found)}")
    print(f"  Saved to: {CONTACTS_FILE.name}")

    all_labels = [c for c in contacts if c.get('category') == 'label']
    with_email = [c for c in all_labels if c.get('demo_email')]
    print(f"  Total label emails: {len(with_email)}/{len(all_labels)}")


if __name__ == "__main__":
    main()
