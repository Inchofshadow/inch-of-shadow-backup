#!/usr/bin/env python3
"""Fetch a web page as TEXT only, for research runs (Temporary Files Rule, 2026-10-24).

Raw pages carry the site's scripts; on 2026-10-21 two saved Inverted Audio
pages held a hacked remote-code loader. This tool downloads a page, throws
away every script, style, iframe and embed, and returns readable text plus
the links and email addresses a contact search needs. It never writes HTML.

Usage:
    python3 fetch_text.py URL                 # print text to stdout
    python3 fetch_text.py URL -o notes.md     # write text (must end .md or .txt)
    python3 fetch_text.py URL --links         # also list links and emails
"""
from __future__ import annotations

import argparse
import ipaddress
import re
import socket
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

TIMEOUT = 15
MAX_REDIRECTS = 5
MAX_BYTES = 5 * 1024 * 1024
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
DROP_TAGS = ("script", "style", "noscript", "iframe", "object", "embed",
             "template", "svg", "canvas", "form")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_OUT = (".md", ".txt")


class FetchError(Exception):
    pass


def check_url(url: str) -> str:
    """Only public http(s) URLs. Blocks file://, localhost and private ranges."""
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise FetchError(f"only http(s) URLs are allowed: {url!r}")
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror as exc:
        raise FetchError(f"cannot resolve {p.hostname}: {exc}") from exc
    for info in infos:
        _check_ip(info[4][0], p.hostname)
    return url


def _check_ip(addr: str, host: str = "") -> None:
    ip = ipaddress.ip_address(addr.split("%")[0])
    if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
            or ip.is_multicast or ip.is_unspecified):
        raise FetchError(f"refusing a non-public address ({ip}) for {host or addr}")


def _peer_ip(r) -> str | None:
    """Best effort: the address the open connection really went to (closes
    the DNS-rebinding gap between check_url and connect). None if urllib3
    does not expose it."""
    try:
        return r.raw._connection.sock.getpeername()[0]
    except Exception:
        return None


def html_to_text(html: str, base_url: str = "") -> dict:
    """Strip every active element; return {'title', 'text', 'links', 'emails'}."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(DROP_TAGS):
        tag.decompose()
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("javascript:"):
            continue
        links.append(urljoin(base_url, href) if base_url else href)
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    emails = sorted({m.lower() for m in EMAIL_RE.findall(text)}
                    | {h[7:].split("?")[0].lower() for h in links if h.lower().startswith("mailto:")})
    return {"title": title, "text": text, "links": list(dict.fromkeys(links)), "emails": emails}


def fetch_text(url: str) -> dict:
    # Redirects are followed by hand so every hop is checked (a public page
    # must not bounce the request to localhost or the LAN).
    for _ in range(MAX_REDIRECTS + 1):
        check_url(url)
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT,
                             stream=True, allow_redirects=False)
        except requests.RequestException as exc:
            raise FetchError(f"request failed: {exc}") from exc
        peer = _peer_ip(r)
        if peer:
            _check_ip(peer, urlparse(url).hostname or "")
        if r.is_redirect or r.status_code in (301, 302, 303, 307, 308):
            loc = r.headers.get("Location")
            r.close()
            if not loc:
                raise FetchError(f"redirect without a Location from {url}")
            url = urljoin(url, loc)
            continue
        break
    else:
        raise FetchError(f"more than {MAX_REDIRECTS} redirects")
    body = b""
    for chunk in r.iter_content(65536):
        body += chunk
        if len(body) > MAX_BYTES:
            raise FetchError("page larger than 5 MB, stopped")
    if r.status_code != 200:
        raise FetchError(f"HTTP {r.status_code} for {url}")
    ctype = r.headers.get("Content-Type", "")
    if "html" not in ctype and "text" not in ctype:
        raise FetchError(f"not a text/html page ({ctype or 'no content type'})")
    html = body.decode(page_charset(ctype, body), errors="replace")
    out = html_to_text(html, base_url=r.url)
    out["url"] = r.url
    return out


def page_charset(ctype: str, body: bytes) -> str:
    """The header charset if given, else the page's <meta charset>, else UTF-8.
    Gate review 2026-11-07: requests falls back to ISO-8859-1 for text/* without a
    charset, which turned UTF-8 pages into mojibake in saved notes."""
    import codecs
    m = re.search(r"charset=[\"']?([\w.:-]+)", ctype or "", re.I)
    if not m:
        m = re.search(rb"<meta[^>]+charset=[\"']?([\w.:-]+)", body[:4096], re.I)
    name = m.group(1) if m else "utf-8"
    name = name.decode("ascii", "ignore") if isinstance(name, bytes) else name
    try:
        return codecs.lookup(name).name
    except LookupError:
        return "utf-8"


def render(page: dict, with_links: bool) -> str:
    parts = [f"# {page['title'] or page['url']}", f"Source: {page['url']}", "", page["text"]]
    if with_links:
        parts += ["", "## Emails"] + [f"- {e}" for e in page["emails"]]
        parts += ["", "## Links"] + [f"- {h}" for h in page["links"]]
    return "\n".join(parts) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("-o", "--out", help="write to this .md/.txt file instead of stdout")
    ap.add_argument("--links", action="store_true", help="append links and emails")
    args = ap.parse_args(argv)
    try:
        page = fetch_text(args.url)
    except FetchError as exc:
        print(f"fetch_text: {exc}", file=sys.stderr)
        return 1
    text = render(page, args.links)
    if args.out:
        out = Path(args.out)
        if out.suffix.lower() not in ALLOWED_OUT:
            print("fetch_text: output must be .md or .txt (never raw HTML)", file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"saved text -> {out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
