"""Fetch HikerAPI profiles for the picks list, a batch per day (Amir "Yes, fetch them" 11-12).
Read-only on Instagram and on engine files; writes profiles.json in this folder only.
    python3 plans/ig-sweep-2026-11/fetch_profiles.py --max 100
"""
import argparse, json, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SI = HERE.parents[1] / "scene_intelligence"
sys.path.insert(0, str(SI))
OUT = HERE / "profiles.json"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max", type=int, required=True); a = ap.parse_args()
    cands = json.loads((HERE / "candidates.json").read_text())["candidates"]
    have = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = [r for r in cands if r["username"] not in have][: a.max]
    print(f"done {len(have)}, this run {len(todo)}, left after {len(cands) - len(have) - len(todo)}")
    if not todo:
        return 0
    import ig_daily_ledger as L
    from ig_data_provider import Provider, ProviderError
    L.check_and_claim(f"ig_sweep_profiles", kind="provider", est_calls=len(todo), endpoint="provider_profile")
    p = Provider(sleep=0.3); errors = 0
    for r in todo:
        try:
            prof = p.profile(r["username"])
        except ProviderError as exc:
            errors += 1; print("error", r["username"], str(exc)[:80])
            if errors >= 5: print("[BREAKER] 5 errors, stopping"); break
            continue
        have[r["username"]] = ({"status": "gone"} if not prof else {
            "status": "ok", "followers": prof["follower_count"], "following": prof["following_count"],
            "posts": prof["media_count"], "category": prof["category_name"], "bio": prof["biography"][:200],
            "private": prof["is_private"], "verified": prof["is_verified"], "city": prof["city_name"],
            "external_url": prof["external_url"], "fetched": date.today().isoformat()})
        OUT.write_text(json.dumps(have, indent=1, ensure_ascii=False) + "\n")
    print("calls", p.calls, "saved", len(have))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
