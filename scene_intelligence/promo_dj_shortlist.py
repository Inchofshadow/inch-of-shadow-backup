"""Shortlist DJ candidates for a release from enriched_contacts.json.

Mechanical filter only: dark-electronic family genre match + SoundCloud reach +
not already in the DJ promo pool. The promotion-expert agent applies protection
exclusions (friends / own-release labels / no-engage) as a judgment step on top.
Stdlib only, no network.
"""
import json
import os
import re
import argparse

# The dark-electronic scene is one adjacent family; a coarse "in the family" match
# is the right filter for this niche. The agent ranks finer within the shortlist.
# 2026-07-05 (audit P3-16): added "electronic" (extract_contacts/extract_ra set
# genre_main="Electronic" with the specific genre in genre_sub, so 167 DJs were
# silently excluded) plus downtempo/slowmo/ambient (the planned Downtempo EP
# would have yielded zero candidates).
DARK_ELECTRONIC = {
    "ebm", "acid", "electro", "techno", "disco", "industrial", "wave", "synth",
    "trance", "coldwave", "darkwave", "minimal", "breakbeat", "electronica", "house",
    "electronic", "downtempo", "slowmo", "ambient",
}


def _tokens(s):
    return set(re.findall(r"[a-z]+", (s or "").lower()))


def _in_scene(genre):
    return bool(_tokens(genre) & DARK_ELECTRONIC)


def genre_match(release_genre, dj_genre):
    """True when BOTH the release and the DJ sit in the dark-electronic family."""
    return _in_scene(release_genre) and _in_scene(dj_genre)


def contact_genre_text(c):
    """genre_main + genre_sub combined for matching (audit P3-16): the
    extract/RA sources store the specific genre in genre_sub with
    genre_main just 'Electronic', so matching genre_main alone skewed
    all three promo lanes toward Rekordbox-sourced contacts."""
    return f"{c.get('genre_main', '')} {c.get('genre_sub', '')}"


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def shortlist(djs, existing_names, release_genre, min_sc_followers=200, limit=25):
    """DJ candidates: in-scene genre + SC reach + not already in the pool.

    Protection (friends / own-release labels / no-engage) is applied by the agent, not here.
    """
    existing = {n.lower() for n in existing_names}
    out = []
    for c in djs:
        if c.get("category") != "dj":
            continue
        if (c.get("name") or "").lower() in existing:
            continue
        if not genre_match(release_genre, contact_genre_text(c)):
            continue
        if _num(c.get("soundcloud_followers")) < min_sc_followers:
            continue
        out.append(c)
    out.sort(key=lambda c: (-_num(c.get("relevance_score")), -_num(c.get("soundcloud_followers"))))
    return out[:limit]


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Shortlist DJ candidates for a release")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--min-followers", type=int, default=200)
    ap.add_argument("--base-dir", default=".")
    args = ap.parse_args()

    contacts = _load(os.path.join(args.base_dir, "scene_intelligence", "enriched_contacts.json"))
    contacts = contacts if isinstance(contacts, list) else (contacts.get("contacts") or list(contacts.values()))
    djs = [c for c in contacts if isinstance(c, dict)]

    release = _load(os.path.join(args.base_dir, "releases", f"{args.slug}.json"))
    md = release.get("metadata", {})
    genre = md.get("genre") or md.get("genre_primary") or release.get("genre_primary") or ""

    pool_path = os.path.join(args.base_dir, "scene_intelligence", "dj_promo_targets.json")
    pool = _load(pool_path) if os.path.exists(pool_path) else {"targets": []}
    existing = [t.get("name", "") for t in pool.get("targets", [])]

    out = shortlist(djs, existing, genre, args.min_followers, args.limit)
    print(f"Release genre: {genre!r} | {len(out)} candidates not already in pool:\n")
    for c in out:
        print(f"  {c['name']} | {c.get('genre_main','?')} | SC {int(_num(c.get('soundcloud_followers')))} | score {c.get('relevance_score','?')}")


if __name__ == "__main__":
    main()
