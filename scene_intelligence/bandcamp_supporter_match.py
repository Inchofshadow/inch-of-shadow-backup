"""
bandcamp_supporter_match.py
---------------------------
Ticket BC-10. Match Bandcamp supporter names that Amir reads BY HAND
(data/bandcamp/supporter-notes.md) against our own local data:
Scene Intelligence, the latest Instagram export, the IG follower roster,
IG enriched contacts and the SC follow tracker.

Why this exists:
  Buyers of similar artists are the best targets for the IG/SC sessions,
  but Bandcamp's Acceptable Use Policy bans automated reading. So Amir
  reads the pages himself and this script only works on local files.

What it never does:
  - no network calls (no Bandcamp, no IG/SC, no HikerAPI)
  - no writes to engagement code, config, queues or trackers
  Every match is a NAME match and must be checked on the real profile
  before any public action (verify-handles rule).

Usage:
  python3 scene_intelligence/bandcamp_supporter_match.py
  python3 scene_intelligence/bandcamp_supporter_match.py --mailing-list data/bandcamp/<export>.csv
  python3 scene_intelligence/bandcamp_supporter_match.py --dry-run   # print only, no output file

Output: data/bandcamp/supporter-candidates.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SI_DIR = BASE_DIR / "scene_intelligence"
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "bandcamp" / "supporter-notes.md"
OUT_FILE = DATA_DIR / "bandcamp" / "supporter-candidates.json"

MIN_KEY_LEN = 4
BC_FAN_URL = re.compile(r"(?:https?://)?(?:www\.)?bandcamp\.com/([A-Za-z0-9_\-]+)", re.I)


def norm(text: str | None) -> str:
    """Lowercase and keep only a-z0-9, so 'Mira Leo', 'mira.leo' and 'mira_leo' meet."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def slug_from_url(url: str | None) -> str:
    """Last path part of a profile URL (instagram.com/x, soundcloud.com/x)."""
    if not url:
        return ""
    path = re.sub(r"^https?://[^/]+", "", url.split("?")[0]).strip("/")
    parts = [p for p in path.split("/") if p and p != "_u"]
    return parts[0] if parts else ""


# ---------------------------------------------------------------- intake

def parse_notes(text: str) -> list[dict]:
    """Parse the notes file into supporters, merged across releases."""
    people: dict[str, dict] = {}
    release = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(">"):
            continue
        if line.startswith("## "):
            release = line[3:].strip()
            continue
        if line.startswith("#") or not release:
            continue  # title or text above the first release block
        slug = ""
        m = BC_FAN_URL.search(line)
        if m:
            slug = m.group(1)
            line = (line[:m.start()] + line[m.end():]).strip(" -|,\t")
        name = line or slug
        key = norm(slug) or norm(name)
        if len(key) < MIN_KEY_LEN and not slug:
            continue
        person = people.setdefault(key, {"name": name, "bandcamp_user": slug, "releases": []})
        if slug and not person["bandcamp_user"]:
            person["bandcamp_user"] = slug
        if release not in person["releases"]:
            person["releases"].append(release)
    return list(people.values())


def parse_mailing_list(path: Path) -> list[dict]:
    """Official Bandcamp mailing-list export. Column names are matched loosely."""
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for n, row in enumerate(csv.DictReader(f), 1):
            low = {k.lower().strip(): (v or "").strip() for k, v in row.items() if k}
            name = low.get("fullname") or low.get("full name") or low.get("name") or " ".join(
                x for x in (low.get("firstname", ""), low.get("lastname", "")) if x)
            email = low.get("email") or low.get("email address") or ""
            if name or email:
                # The email (and its user part, which people often reuse as a handle) is
                # used for matching only and never written out.
                out.append({"name": name or f"(mailing list entry {n}, no name)", "bandcamp_user": "",
                            "releases": ["own mailing list"], "_email": email.lower(),
                            "_key": email.split("@")[0]})
    return out


# ---------------------------------------------------------------- index

def _load(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def latest_ig_export(data_dir: Path = DATA_DIR) -> Path | None:
    dirs = sorted(data_dir.glob("instagram-inch_of_shadow-*"))
    return dirs[-1] if dirs else None


class Index:
    def __init__(self) -> None:
        self.by_key: dict[str, list[dict]] = {}
        self.emails: set[str] = set()
        self.sources: dict[str, int] = {}

    def add(self, key_text: str, hit: dict) -> None:
        key = norm(key_text)
        if len(key) < MIN_KEY_LEN:
            return
        bucket = self.by_key.setdefault(key, [])
        if hit not in bucket:
            bucket.append(hit)

    def count(self, source: str, n: int) -> None:
        self.sources[source] = n


def build_index(si_dir: Path = SI_DIR, data_dir: Path = DATA_DIR) -> Index:
    idx = Index()

    contacts = _load(si_dir / "enriched_contacts.json") or []
    for c in contacts:
        ig = c.get("ig_username") or slug_from_url(c.get("instagram_url") or c.get("instagram"))
        sc = slug_from_url(c.get("soundcloud_url"))
        hit = {"source": "si", "name": c.get("name", ""), "ig": ig or "", "sc": sc or "",
               "category": c.get("category", ""), "ig_follows_me": bool(c.get("ig_follows_me")),
               "ig_i_follow": bool(c.get("ig_i_follow"))}
        for key in (c.get("name"), ig, sc):
            idx.add(key, hit)
        for field in ("email", "discogs_email"):
            if c.get(field):
                idx.emails.add(str(c[field]).lower().strip())
    idx.count("si", len(contacts))

    enriched = _load(si_dir / "ig_enriched_contacts.json") or []
    for c in enriched:
        hit = {"source": "ig_enriched", "ig": c.get("ig_username") or c.get("handle", ""),
               "name": c.get("ig_full_name") or ""}
        idx.add(hit["ig"], hit)
        idx.add(hit["name"], hit)
    idx.count("ig_enriched", len(enriched))

    roster = _load(si_dir / "ig_follower_roster.json") or []
    for r in roster:
        hit = {"source": "ig_roster_follower", "ig": r.get("username", ""), "name": r.get("full_name", "")}
        idx.add(hit["ig"], hit)
        idx.add(hit["name"], hit)
    idx.count("ig_roster_follower", len(roster))

    export = latest_ig_export(data_dir)
    if export:
        conn = export / "connections" / "followers_and_following"
        n = 0
        for fp in sorted(conn.glob("followers_*.json")):
            for item in _load(fp) or []:
                for s in item.get("string_list_data", []):
                    user = s.get("value") or slug_from_url(s.get("href"))
                    idx.add(user, {"source": "ig_export_follower", "ig": user})
                    n += 1
        idx.count("ig_export_follower", n)
        following = (_load(conn / "following.json") or {}).get("relationships_following", [])
        for item in following:
            user = item.get("title") or slug_from_url((item.get("string_list_data") or [{}])[0].get("href"))
            idx.add(user, {"source": "ig_export_following", "ig": user})
        idx.count("ig_export_following", len(following))
        idx.sources["ig_export_dir"] = export.name  # type: ignore[assignment]

    sc = (_load(si_dir / "sc_follow_tracker.json") or {}).get("follows", [])
    for f in sc:
        slug = slug_from_url(f.get("url"))
        hit = {"source": "sc_tracker", "sc": slug or f.get("name", ""), "name": f.get("name", ""),
               "followed_back": bool(f.get("followed_back"))}
        idx.add(f.get("name"), hit)
        idx.add(slug, hit)
    idx.count("sc_tracker", len(sc))

    return idx


# ---------------------------------------------------------------- match

def classify(hits: list[dict], email_in_si: bool = False) -> str:
    srcs = {h["source"] for h in hits}
    if not hits and not email_in_si:
        return "no_match"
    if "ig_export_follower" in srcs or "ig_roster_follower" in srcs or any(h.get("ig_follows_me") for h in hits):
        return "already_follows_us_ig"
    if "ig_export_following" in srcs or any(h.get("ig_i_follow") for h in hits):
        return "we_follow_ig"
    if "sc_tracker" in srcs:
        return "in_sc_tracker"
    return "in_si"


def match(people: list[dict], idx: Index) -> list[dict]:
    rows = []
    for p in people:
        keys = {norm(p.get("bandcamp_user")), norm(p.get("name")), norm(p.pop("_key", ""))} - {""}
        hits: list[dict] = []
        for k in keys:
            for h in idx.by_key.get(k, []):
                if h not in hits:
                    hits.append(h)
        email = p.pop("_email", "")
        email_in_si = bool(email) and email in idx.emails
        rows.append({**p, "status": classify(hits, email_in_si), "email_in_si": email_in_si,
                     "matches": hits, "verify": bool(hits) or email_in_si})
    order = {"already_follows_us_ig": 0, "we_follow_ig": 1, "in_sc_tracker": 2, "in_si": 3, "no_match": 4}
    rows.sort(key=lambda r: (order[r["status"]], -len(r["releases"]), r["name"].lower()))
    return rows


def summary_lines(rows: list[dict]) -> list[str]:
    lines = [f"{'name':<26} {'releases':>8}  {'status':<22} handles"]
    for r in rows:
        handles = sorted({("ig:" + h["ig"]) if h.get("ig") else ("sc:" + h["sc"]) if h.get("sc") else h["source"]
                          for h in r["matches"]})
        lines.append(f"{r['name'][:26]:<26} {len(r['releases']):>8}  {r['status']:<22} {', '.join(handles)}")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines.append("")
    lines.append("totals: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    lines.append("All matches are by name only: check the real profile before any action.")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Match hand-read Bandcamp supporters against local IG/SC/SI data.")
    ap.add_argument("--notes", type=Path, default=NOTES_FILE)
    ap.add_argument("--mailing-list", type=Path, help="official Bandcamp mailing-list export (CSV)")
    ap.add_argument("--out", type=Path, default=OUT_FILE)
    ap.add_argument("--dry-run", action="store_true", help="print only, write nothing")
    args = ap.parse_args(argv)

    people = parse_notes(args.notes.read_text(encoding="utf-8")) if args.notes.exists() else []
    if args.mailing_list:
        people += parse_mailing_list(args.mailing_list)
    if not people:
        print(f"No supporters found in {args.notes}")
        return 1

    idx = build_index()
    rows = match(people, idx)
    print("\n".join(summary_lines(rows)))

    if not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = {"generated": date.today().isoformat(), "ticket": "BC-10",
                   "note": "Name matches only. Verify each profile before any action.",
                   "sources": idx.sources, "supporters": rows}
        args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {args.out.relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
