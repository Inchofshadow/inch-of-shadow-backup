"""
ig_follower_audit.py
--------------------
Audit @inch_of_shadow's OWN Instagram followers to find notable / high-reach
accounts that follow IoS. Purpose: identify the best seed accounts for the
mutual-follow social-proof growth strategy (target the followers of notable
accounts that already follow you -> triadic-closure follow-back lift + a
visible "Followed by <notable>" social-proof line on your profile).

Strategy basis (researched 2026-06-14): a mutual connection roughly doubles
follow-back rate (~14% vs ~7% in a comparable audio-platform study); IG shows
viewer-specific "Followed by X you follow" social proof; IG suggestions weigh
mutual/indirect connections. INSTAGRAM-ONLY (no SoundCloud equivalent).

Method (minimal IG calls):
  1. Resolve inch_of_shadow user_id (1 call).
  2. Paginate /api/v1/friendships/<uid>/followers/ to enumerate ALL followers.
     Each entry comes with: pk, username, full_name, is_verified, is_private
     -- is_verified is a FREE "notable" signal.
  3. Cross-reference each follower against enriched_contacts.json (462 of which
     already have ig_followers counts + category/score) -- NO extra IG call.
  4. Rank: verified first, then by known ig_followers, then scene category.
  5. Save full roster + a notable shortlist; print the shortlist.

Credentials: IG_SESSION_ID, IG_CSRF_TOKEN from .env (same as the other
ig_*.py private-API scripts).

Usage:
  python3 scene_intelligence/ig_follower_audit.py            # full audit
  python3 scene_intelligence/ig_follower_audit.py --max 200  # cap enumeration
"""
from __future__ import annotations
import os, sys, json, time, random, argparse
from pathlib import Path
from typing import Optional
import requests

BASE = Path(__file__).parent.parent
SI = BASE / "scene_intelligence"
ENV = BASE / ".env"
CONTACTS = SI / "enriched_contacts.json"
OUT_ROSTER = SI / "ig_follower_roster.json"
OUT_SHORTLIST = SI / "ig_notable_followers.json"

IG_API = "https://www.instagram.com/api/v1"
IG_WEB = "https://www.instagram.com"
APP_ID = "936619743392459"
TARGET = "inch_of_shadow"


def _load_env():
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    sid = os.getenv("IG_SESSION_ID", "").strip()
    csrf = os.getenv("IG_CSRF_TOKEN", "").strip()
    if not sid or not csrf:
        raise SystemExit("[AUDIT] Missing IG_SESSION_ID / IG_CSRF_TOKEN in .env")
    return sid, csrf


def _session(sid, csrf):
    s = requests.Session()
    s.headers.update({
        "X-IG-App-ID": APP_ID,
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0.0.0 Safari/537.36"),
        "X-CSRFToken": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "en-US,en;q=0.9",
    })
    s.cookies.set("sessionid", sid, domain=".instagram.com")
    s.cookies.set("csrftoken", csrf, domain=".instagram.com")
    return s


def _resolve_uid(s) -> tuple[str, int]:
    r = s.get(f"{IG_API}/users/web_profile_info/", params={"username": TARGET},
              headers={"Referer": f"{IG_WEB}/{TARGET}/"}, timeout=15)
    r.raise_for_status()
    u = r.json().get("data", {}).get("user", {})
    return u.get("id"), (u.get("edge_followed_by") or {}).get("count")


def _fetch_followers(s, uid, max_accounts=10000):
    out, next_max, calls = [], None, 0
    while len(out) < max_accounts:
        params = {"count": 100}
        if next_max:
            params["max_id"] = next_max
        r = s.get(f"{IG_API}/friendships/{uid}/followers/", params=params,
                  headers={"Referer": f"{IG_WEB}/{TARGET}/followers/"}, timeout=20)
        calls += 1
        if r.status_code == 401:
            raise SystemExit("[AUDIT] Session expired (401). Re-extract cookies.")
        if r.status_code == 429:
            print(f"[AUDIT] Rate-limited (429) after {calls} calls -- stopping with {len(out)} collected.", file=sys.stderr)
            break
        if r.status_code != 200:
            print(f"[AUDIT] HTTP {r.status_code} on page {calls} -- stopping.", file=sys.stderr)
            break
        data = r.json()
        for u in data.get("users", []):
            out.append({
                "username": (u.get("username") or "").lower(),
                "full_name": u.get("full_name") or "",
                "is_verified": bool(u.get("is_verified")),
                "is_private": bool(u.get("is_private")),
                "pk": str(u.get("pk") or u.get("id") or ""),
            })
        next_max = data.get("next_max_id")
        print(f"  page {calls}: +{len(data.get('users', []))} (total {len(out)})", flush=True)
        if not next_max:
            break
        time.sleep(random.uniform(1.5, 3.0))
    return out, calls


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=10000, help="cap enumeration")
    try:
        from scene_intelligence.ig_daily_ledger import add_ledger_argument, check_and_claim
    except ImportError:
        from ig_daily_ledger import add_ledger_argument, check_and_claim
    add_ledger_argument(ap)
    args = ap.parse_args()

    # Audit P1-7: one IG API script per day across the whole toolchain.
    check_and_claim("ig_follower_audit", override=args.override_ledger,
                    reason=getattr(args, 'override_reason', None))

    sid, csrf = _load_env()
    s = _session(sid, csrf)

    print(f"=== IG Follower Audit: @{TARGET} ===")
    uid, count = _resolve_uid(s)
    print(f"user_id={uid}  follower_count={count}")
    print(f"Enumerating followers (≈{(count or 800)//100 + 1} pages)...")

    followers, calls = _fetch_followers(s, uid, args.max)
    print(f"\nEnumerated {len(followers)} followers in {calls} pages (+1 resolve = {calls+1} IG calls).")

    # Cross-reference local DB (no IG calls)
    db = json.loads(CONTACTS.read_text())
    db = [c for c in (db if isinstance(db, list) else db.values()) if isinstance(c, dict)]
    by_handle = {}
    for c in db:
        h = (c.get("ig_username") or "").lower().lstrip("@")
        if h:
            by_handle[h] = c

    enriched = []
    for f in followers:
        c = by_handle.get(f["username"])
        f["known_ig_followers"] = (c or {}).get("ig_followers")
        f["category"] = (c or {}).get("category")
        f["match_score"] = (c or {}).get("match_score") or (c or {}).get("score")
        f["in_si_db"] = c is not None
        enriched.append(f)

    OUT_ROSTER.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))

    # Notable shortlist: verified OR known followers >= 3000, rank by reach
    def reach(f):
        return f.get("known_ig_followers") or (10_000_000 if f["is_verified"] else 0)
    notable = [f for f in enriched if f["is_verified"] or (f.get("known_ig_followers") or 0) >= 3000]
    notable.sort(key=lambda f: (not f["is_verified"], -(f.get("known_ig_followers") or 0)))
    OUT_SHORTLIST.write_text(json.dumps(notable, indent=2, ensure_ascii=False))

    verified_ct = sum(1 for f in enriched if f["is_verified"])
    indb_ct = sum(1 for f in enriched if f["in_si_db"])
    print(f"\n=== Summary ===")
    print(f"  total followers enumerated: {len(enriched)}")
    print(f"  verified followers:         {verified_ct}")
    print(f"  followers in SI DB:         {indb_ct} (have category/score/follower data)")
    print(f"  notable shortlist:          {len(notable)} (verified or >=3000 known followers)")
    print(f"\n  saved roster -> {OUT_ROSTER.name}")
    print(f"  saved shortlist -> {OUT_SHORTLIST.name}")

    print(f"\n=== Top notable followers ===")
    for f in notable[:40]:
        vf = "VERIFIED" if f["is_verified"] else ""
        kf = f.get("known_ig_followers")
        kfs = f"{kf:,}f" if kf else "?f"
        cat = f.get("category") or ""
        print(f"  @{f['username']:30s} {kfs:>10}  {vf:8s} {cat}")


if __name__ == "__main__":
    main()
