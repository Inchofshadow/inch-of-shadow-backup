"""Shortlist demo-safe label targets for a release from enriched_contacts.json.

Buckets labels into email-pitchable / DM-only / skipped (NO-DEMOS), reusing the DJ
helper's genre_match. The promotion-expert agent drafts per-label hooks and routes
sending through Tool 4; this helper does the mechanical filter only. Stdlib only.
"""
NO_DEMO_PHRASES = (
    "no demos", "not accepting demos", "do not respond to demo", "don't accept demo",
)


def is_email(value):
    """A real address, not the 'DM ONLY' / 'NO DEMOS' sentinels stored in demo_email."""
    v = (value or "").strip()
    return "@" in v and v.upper() not in ("DM ONLY", "NO DEMOS")


def demo_route(label):
    """Route a label: 'email' | 'dm' | 'skip' from demo_email + SC-description signals."""
    de = (label.get("demo_email") or "").strip()
    desc = ((label.get("soundcloud_description") or "") + " "
            + (label.get("soundcloud_description_full") or "")).lower()
    if de.upper() == "NO DEMOS" or any(p in desc for p in NO_DEMO_PHRASES):
        return "skip"
    if de.upper() == "DM ONLY":
        return "dm"
    if is_email(de):
        return "email"
    if is_email(label.get("discogs_email", "")):
        return "email"
    return "skip"


import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene_intelligence.promo_dj_shortlist import genre_match, contact_genre_text  # noqa: E402

TIER_RANK = {"big": 0, "mid": 1, "small": 2}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def shortlist(labels, existing_names, release_genre, limit=30):
    """Bucket in-scene, not-already-pitched labels into email / dm_only / skipped."""
    existing = {n.lower() for n in existing_names}
    email, dm_only, skipped = [], [], 0
    for c in labels:
        if c.get("category") != "label":
            continue
        if (c.get("name") or "").lower() in existing:
            continue
        if not genre_match(release_genre, contact_genre_text(c)):
            continue
        route = demo_route(c)
        if route == "email":
            email.append(c)
        elif route == "dm":
            dm_only.append(c.get("name"))
        else:
            skipped += 1
    email.sort(key=lambda c: (TIER_RANK.get((c.get("tier") or "").lower(), 3),
                              -_num(c.get("relevance_score"))))
    return {"email": email[:limit], "dm_only": dm_only, "skipped": skipped}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Shortlist demo-safe label targets for a release")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--base-dir", default=".")
    args = ap.parse_args()

    contacts = _load(os.path.join(args.base_dir, "scene_intelligence", "enriched_contacts.json"))
    contacts = contacts if isinstance(contacts, list) else (contacts.get("contacts") or list(contacts.values()))
    labels = [c for c in contacts if isinstance(c, dict)]

    release = _load(os.path.join(args.base_dir, "releases", f"{args.slug}.json"))
    md = release.get("metadata", {})
    genre = md.get("genre") or md.get("genre_primary") or release.get("genre_primary") or ""

    plog = _load(os.path.join(args.base_dir, "scene_intelligence", "promotion_log.json"))
    camp = (plog.get("campaigns", {}) or {}).get(args.slug, {})
    existing = [t.get("name", "") for t in camp.get("targets", [])]

    out = shortlist(labels, existing, genre, args.limit)
    print(f"Release genre: {genre!r}")
    print(f"  email targets ({len(out['email'])}):")
    for c in out["email"]:
        print(f"    {c['name']} | {c.get('tier','?')} | {c.get('genre_main','?')} | {c.get('demo_email')}")
    print(f"  DM-only ({len(out['dm_only'])}): {', '.join(out['dm_only'])}")
    print(f"  skipped NO-DEMOS (in-scene): {out['skipped']}")


if __name__ == "__main__":
    main()
