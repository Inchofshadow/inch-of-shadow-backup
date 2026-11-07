"""
bandcamp_links.py
-----------------
Ticket BC-07. Bandcamp campaign links: one tracked link per channel, so the
official sales report shows which channel sold.

Format checked on Amir's Tools page (Campaign Tracking) 2026-10-21:
  <track or album URL>?campaign=<name>
  name = lowercase letters, numbers and dashes only.
Visits show in the Campaign Tracker on the Tools page (after the first
visit); sales show in the "referrer" column of the sales report.

Usage:
  python3 bandcamp_links.py                       # all channels for every catalog release
  python3 bandcamp_links.py the-deceiver-single   # one release by slug
  python3 bandcamp_links.py <bandcamp url> --channel sc-buy
  python3 bandcamp_links.py --write               # save links into releases/<slug>.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Channel -> where the link is placed. Names are permanent: changing one
# splits that channel's history in the sales report.
CHANNELS: dict[str, str] = {
    "sc-buy": "SoundCloud track buy link",
    "sc-inbox": "SoundCloud inbox replies",
    "sc-desc": "SoundCloud track description",
    "sc-mix": "SoundCloud DJ set / mix buy link (own track in the tracklist)",
    "yt-desc": "YouTube video description",
    "ig-bio": "Instagram bio / link hub",
    "ig-story": "Instagram story link sticker",
    "smartlink": "Release smart link",
    "outreach": "Outreach emails and DMs",
    "bc-friday": "Bandcamp Friday follower message",
    "press": "EPK / press kit",
}

# Live Bandcamp catalog as read from inchofshadow.bandcamp.com/music on 2026-10-21.
# Releases with a releases/<slug>.json take their URL from that file instead.
CATALOG: dict[str, str] = {
    "the-deceiver": "https://inchofshadow.bandcamp.com/track/the-deceiver",
    "farewell": "https://inchofshadow.bandcamp.com/track/farewell",
    "the-tour-remix": "https://inchofshadow.bandcamp.com/album/the-tour-remix",
    "meltscape": "https://inchofshadow.bandcamp.com/album/meltscape",
    "eastern-stars": "https://inchofshadow.bandcamp.com/album/eastern-stars",
}

_NAME_OK = re.compile(r"^[a-z0-9-]+$")
_BC_PAGE = re.compile(r"^https://[a-z0-9-]+\.bandcamp\.com/(track|album)/[A-Za-z0-9_-]+/?$")


def campaign_url(url: str, channel: str) -> str:
    """Return the Bandcamp URL with ?campaign=<channel>, replacing any old campaign."""
    if not _NAME_OK.match(channel or ""):
        raise ValueError(f"campaign name must be lowercase letters, numbers and dashes: {channel!r}")
    parts = urlsplit((url or "").strip())
    base = urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, "", ""))
    if not _BC_PAGE.match(base):
        raise ValueError(f"not a Bandcamp track or album URL: {url!r}")
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "campaign"]
    query.append(("campaign", channel))
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, urlencode(query), ""))


def links_for(url: str, channels: list[str] | None = None) -> dict[str, str]:
    return {ch: campaign_url(url, ch) for ch in (channels or list(CHANNELS))}


def _release_url(slug: str) -> str:
    from release_manager.storage import load_release
    rel = load_release(slug)
    return (rel or {}).get("platform_links", {}).get("bandcamp", "") if rel else ""


def _targets(arg: str | None) -> dict[str, str]:
    """name -> bandcamp URL for the CLI argument (URL, release slug, catalog key or all)."""
    if arg and arg.startswith("http"):
        return {arg: arg}
    if arg:
        url = _release_url(arg) or CATALOG.get(arg, "")
        if not url:
            raise SystemExit(f"No Bandcamp URL for {arg!r} (release file or CATALOG).")
        return {arg: url}
    return dict(CATALOG)


def write_release_links(channels: list[str] | None = None) -> list[str]:
    """Store links under bandcamp_campaign_links in every release that has a Bandcamp URL.

    Writes the raw file directly instead of save_release(): that one runs
    reconcile_release(), which would also flip timeline items. Only this one
    key changes here.
    """
    from release_manager.storage import iter_release_paths
    from scene_intelligence.json_io import atomic_write_json
    written = []
    for path in iter_release_paths():
        try:
            with open(path, encoding="utf-8") as f:
                rel = json.load(f)
        except (OSError, ValueError):
            continue
        url = rel.get("platform_links", {}).get("bandcamp", "")
        if not url:
            continue
        links = links_for(url, channels)
        if rel.get("bandcamp_campaign_links") == links:
            continue
        rel["bandcamp_campaign_links"] = links
        atomic_write_json(path, rel)
        written.append(rel.get("slug", path.stem))
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bandcamp campaign links per channel (BC-07).")
    ap.add_argument("target", nargs="?", help="Bandcamp URL, release slug or catalog key (default: whole catalog)")
    ap.add_argument("--channel", action="append", choices=sorted(CHANNELS), help="limit to channel(s)")
    ap.add_argument("--write", action="store_true", help="save links into releases/<slug>.json")
    args = ap.parse_args(argv)

    if args.write:
        slugs = write_release_links(args.channel)
        print("Saved bandcamp_campaign_links in: " + (", ".join(slugs) or "no release with a Bandcamp URL"))
        return 0

    for name, url in _targets(args.target).items():
        print(name)
        for ch, link in links_for(url, args.channel).items():
            print(f"  {ch:<10} {link}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
