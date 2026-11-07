"""Gap Radar extra sources (GR-04, 2026-11-05). Free official APIs only, light use.

Each function returns items in the same shape as gap_radar.reddit():
  {"src", "title", "text", "url", "date"} (+ optional extra fields).

  stackexchange()  Stack Exchange API 2.3, no key (300 requests/day per IP).
  youtube()        YouTube Data API v3 with YOUTUBE_API_KEY from .env (~650 quota units/run).
  github()         GitHub issue search, unauthenticated (10 searches/minute).
  balance()        caps every source family at MAX_SHARE of the final sample.

Chrome Web Store reviews are NOT collected: Google offers no public reviews API (the
Chrome Web Store API only manages your own listings), and the store loads reviews
through an undocumented internal RPC, which would be scraping.
G2, Capterra, Trustpilot are out: their terms forbid scraping.
"""
from __future__ import annotations

import html
import os
import re
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

UA = "Mozilla/5.0 (Macintosh) gap-radar/0.1 (private research)"
ROOT = Path(__file__).resolve().parent.parent

SE_SITES = ["superuser", "webapps", "softwarerecs", "music", "avp"]
SE_PHRASES = ["is there a tool", "is there an app", "alternative to", "software that can"]
SE_PAUSE = 1.0

YT_QUERIES = ["best app for small business", "notion alternative", "best music production app",
              "best DJ software", "best video editing app for youtubers", "best invoicing app freelancers"]
YT_VIDEOS = 5             # videos per query (search.list = 100 units per query)
YT_COMMENTS = 40          # top comments per video (commentThreads.list = 1 unit)
YT_MIN_CHARS = 40         # skip "great video" comments

GH_LABELS = ["enhancement", "feature request", "feature-request", "type: feature"]
GH_MIN_REACTIONS = 30
GH_PAUSE = 7              # unauthenticated search: 10 requests/minute

MAX_SHARE = 0.5           # no source family above half of the sample


def _clean(s: str, n: int = 700) -> str:
    """Same cleaner as gap_radar.clean (copied to avoid a circular import)."""
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def _get(url: str, pause: float, **kw) -> requests.Response:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=25, **kw)
    time.sleep(pause)
    r.raise_for_status()
    return r


def stackexchange(sites=SE_SITES, phrases=SE_PHRASES, days: int = 365) -> list[dict]:
    out, since = [], int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    for site in sites:
        for phrase in phrases:
            try:
                data = _get("https://api.stackexchange.com/2.3/search/advanced", SE_PAUSE,
                            params={"site": site, "q": phrase, "fromdate": since, "sort": "votes",
                                    "order": "desc", "pagesize": 30, "filter": "withbody"}).json()
            except Exception as e:  # one bad query never stops the run
                print(f"  stackexchange {site} '{phrase}': {e}")
                continue
            for q in data.get("items", []):
                out.append({"src": f"stackexchange {site}", "title": _clean(q.get("title", ""), 200),
                            "text": _clean(q.get("body", "")), "url": q.get("link", ""),
                            "date": datetime.fromtimestamp(q.get("creation_date", 0), timezone.utc)
                            .strftime("%Y-%m-%d"), "score": q.get("score")})
            if data.get("backoff"):          # API asks us to wait
                time.sleep(int(data["backoff"]))
            if data.get("quota_remaining", 1) <= 5:
                print("  stackexchange: daily quota nearly used, stopping")
                return out
        print(f"  stackexchange {site}: {len(out)} total")
    return out


def youtube(queries=YT_QUERIES, key: str | None = None) -> list[dict]:
    if key is None:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        print("  youtube: no YOUTUBE_API_KEY in .env, skipped")
        return []
    out, api = [], "https://www.googleapis.com/youtube/v3"
    after = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for q in queries:
        try:
            vids = _get(f"{api}/search", 0.5, params={
                "key": key, "part": "snippet", "q": q, "type": "video", "order": "relevance",
                "maxResults": YT_VIDEOS, "publishedAfter": after, "relevanceLanguage": "en"}).json()
        except Exception as e:
            print(f"  youtube search '{q}': {type(e).__name__}")   # never print the key-bearing URL
            continue
        for v in vids.get("items", []):
            vid = v.get("id", {}).get("videoId")
            if not vid:
                continue
            vtitle = _clean(v.get("snippet", {}).get("title", ""), 200)
            try:
                threads = _get(f"{api}/commentThreads", 0.5, params={
                    "key": key, "part": "snippet", "videoId": vid, "order": "relevance",
                    "maxResults": YT_COMMENTS, "textFormat": "plainText"}).json()
            except Exception as e:   # comments disabled -> 403, skip the video
                print(f"  youtube comments {vid}: {type(e).__name__}")
                continue
            for t in threads.get("items", []):
                c = t.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                text = _clean(c.get("textDisplay", ""))
                if len(text) < YT_MIN_CHARS:
                    continue
                out.append({"src": f"youtube '{q}'", "title": vtitle, "text": text,
                            "url": f"https://www.youtube.com/watch?v={vid}&lc={t.get('id', '')}",
                            "date": (c.get("publishedAt") or "")[:10], "likes": c.get("likeCount")})
        print(f"  youtube '{q}': {len(out)} total")
    return out


def github(labels=GH_LABELS, min_reactions: int = GH_MIN_REACTIONS, days: int = 730,
           queries=None) -> list[dict]:
    """Open issues by label, or by free search `queries` (GR-03 profiles), e.g.
    'repo:VCVRack/Rack label:enhancement reactions:>=5'. A query without its own
    reactions: filter gets reactions:>=min_reactions."""
    out, since = [], (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    searches = queries if queries else [f'label:"{lb}"' for lb in labels]
    for label in searches:
        react = "" if "reactions:" in label else f" reactions:>={min_reactions}"
        q = f'is:issue is:open {label}{react} created:>{since}'
        try:
            data = _get("https://api.github.com/search/issues", GH_PAUSE,
                        params={"q": q, "sort": "reactions", "order": "desc", "per_page": 100}).json()
        except Exception as e:
            print(f"  github '{label}': {e}")
            continue
        for i in data.get("items", []):
            repo = "/".join(i.get("repository_url", "").split("/")[-2:])
            out.append({"src": f"github {repo}", "title": _clean(i.get("title", ""), 200),
                        "text": _clean(i.get("body") or ""), "url": i.get("html_url", ""),
                        "date": (i.get("created_at") or "")[:10],
                        "reactions": (i.get("reactions") or {}).get("total_count")})
        print(f"  github '{label}': {len(out)} total")
    return out


def family(item: dict) -> str:
    """Source family: 'appstore Notion (Productivity)' -> 'appstore'."""
    return item["src"].split(" ", 1)[0]


def balance(items: list[dict], max_share: float = MAX_SHARE) -> list[dict]:
    """Cap each source family so none is above max_share of the result.

    Trimmed families keep items round-robin across their sub-sources (apps, subreddits,
    sites), so a cap never drops whole categories. Order of kept items is preserved.
    """
    fams: dict[str, list[int]] = OrderedDict()
    for i, it in enumerate(items):
        fams.setdefault(family(it), []).append(i)
    if len(fams) < 2:
        return list(items)
    counts = {f: len(ix) for f, ix in fams.items()}
    cap = max(counts.values())
    while cap > 0 and cap > max_share * sum(min(n, cap) for n in counts.values()):
        cap -= 1
    keep: set[int] = set()
    for f, ix in fams.items():
        if len(ix) <= cap:
            keep.update(ix)
            continue
        subs: dict[str, list[int]] = OrderedDict()
        for i in ix:
            subs.setdefault(items[i]["src"], []).append(i)
        queues, picked = [list(v) for v in subs.values()], []
        while len(picked) < cap:
            for qu in queues:
                if qu and len(picked) < cap:
                    picked.append(qu.pop(0))
        keep.update(picked)
        print(f"  balance: {f} {len(ix)} -> {cap}")
    return [it for i, it in enumerate(items) if i in keep]
