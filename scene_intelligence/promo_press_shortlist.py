"""Shortlist press / premiere / radio targets for a release from enriched_contacts.json.

The media+radio pool is mixed: blogs/magazines (press), SC/YT premiere channels
(premiere), and radio shows (radio). This helper sorts contacts into those lanes and
routes each by reachability - a real email (draftable via Tool 4), a website-only contact
(use their submission form), or unreachable (skip). The promotion-expert agent drafts the
register-appropriate pitch and runs the one-premiere-at-a-time ladder discipline; this
helper does the mechanical filter only. Stdlib only.

Note on the premiere lane: the strongest premiere targets (THE BRVTALIST etc.) carry their
emails in plans/premiere-pitch-template.md, not always in the contact DB - the agent layers
that ladder on top of whatever this helper surfaces.
"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene_intelligence.promo_dj_shortlist import genre_match, contact_genre_text  # noqa: E402

# sub_type -> lane. Anything unmapped falls through to "skip" (e.g. shop, production, channel).
LANE_BY_SUBTYPE = {
    "premiere": "premiere",
    "press": "press",
    "magazine": "press",
    "blog": "press",
    "radio": "radio",
    "mix_series": "radio",
}
LANE_ORDER = {"premiere": 0, "press": 1, "radio": 2}

EMAIL_FIELDS = ("contact_email", "demo_email", "email", "discogs_email")
WEB_FIELDS = ("discogs_website", "soundcloud_website", "url", "discogs_url", "soundcloud_url")


def _clean(v):
    return (v or "").strip()


def find_email(contact):
    """Return a real address from any known email field, else ''. Skips DM/NO-DEMO sentinels."""
    for k in EMAIL_FIELDS:
        v = _clean(contact.get(k))
        if "@" in v and v.upper() not in ("DM ONLY", "NO DEMOS"):
            return v
    return ""


def find_website(contact):
    """Return the first http(s) website/profile URL, else ''."""
    for k in WEB_FIELDS:
        v = _clean(contact.get(k))
        if v.startswith("http"):
            return v
    return ""


def route(contact):
    """Route a press contact: 'email' | 'form' | 'skip' by reachability."""
    if find_email(contact):
        return "email"
    if find_website(contact):
        return "form"
    return "skip"


def lane(contact):
    """Lane a press contact by sub_type: 'premiere' | 'press' | 'radio' | None."""
    return LANE_BY_SUBTYPE.get((contact.get("sub_type") or "").strip().lower())


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def shortlist(contacts, existing_names, release_genre, limit=40):
    """Bucket in-scene, not-already-pitched press/premiere/radio contacts.

    Returns {"email": [...], "form": [...names...], "skipped": int}. Email targets carry
    a resolved `_email` + `_lane`; form targets carry `_website` + `_lane` (so the agent
    can flag the submission URL). Both lists are sorted premiere -> press -> radio, then by
    descending relevance_score.
    """
    existing = {n.lower() for n in existing_names}
    email, form, skipped = [], [], 0
    for c in contacts:
        if c.get("category") not in ("media", "radio"):
            continue
        ln = lane(c)
        if ln is None:
            continue
        if (c.get("name") or "").lower() in existing:
            continue
        if not genre_match(release_genre, contact_genre_text(c)):
            continue
        r = route(c)
        if r == "email":
            email.append({**c, "_email": find_email(c), "_lane": ln})
        elif r == "form":
            form.append({**c, "_website": find_website(c), "_lane": ln})
        else:
            skipped += 1
    key = lambda c: (LANE_ORDER.get(c["_lane"], 9), -_num(c.get("relevance_score")))
    email.sort(key=key)
    form.sort(key=key)
    return {"email": email[:limit], "form": form[:limit], "skipped": skipped}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(
        description="Shortlist press / premiere / radio targets for a release")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--base-dir", default=".")
    args = ap.parse_args()

    contacts = _load(os.path.join(args.base_dir, "scene_intelligence", "enriched_contacts.json"))
    contacts = contacts if isinstance(contacts, list) else (contacts.get("contacts") or list(contacts.values()))
    contacts = [c for c in contacts if isinstance(c, dict)]

    release = _load(os.path.join(args.base_dir, "releases", f"{args.slug}.json"))
    md = release.get("metadata", {})
    genre = md.get("genre") or md.get("genre_primary") or release.get("genre_primary") or ""

    plog = _load(os.path.join(args.base_dir, "scene_intelligence", "promotion_log.json"))
    camp = (plog.get("campaigns", {}) or {}).get(args.slug, {})
    existing = [t.get("name", "") for t in camp.get("targets", [])]

    out = shortlist(contacts, existing, genre, args.limit)
    print(f"Release genre: {genre!r}")
    print(f"  email targets ({len(out['email'])}):")
    for c in out["email"]:
        print(f"    [{c['_lane']:8}] {c['name']} | {c.get('genre_main','?')} | {c['_email']}")
    print(f"  website-only / use form ({len(out['form'])}):")
    for c in out["form"]:
        print(f"    [{c['_lane']:8}] {c['name']} | {c['_website']}")
    print(f"  skipped (unreachable / off-lane in-scene): {out['skipped']}")
    print("\nPremiere lane: layer plans/premiere-pitch-template.md ladder on top "
          "(THE BRVTALIST etc. carry emails there, one channel at a time).")


if __name__ == "__main__":
    main()
