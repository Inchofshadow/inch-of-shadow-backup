"""Read-only check of the IG scene like targets (Socials 27, 2026-11-06).

Reads SI contacts that fit like tiers T1-T3, checks each on HikerAPI
(profile + newest post), and writes results to this folder ONLY.
Never writes enriched_contacts.json, engagement_log.json or config.

    python3 plans/ig-like-list-2026-11/check_like_targets.py --dry-run
    python3 plans/ig-like-list-2026-11/check_like_targets.py
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scene_intelligence")); sys.path.insert(0, str(REPO))
import ig_engagement as E  # noqa: E402

OUT = HERE / "like_targets_check.json"


def targets():
    cfg = E._import_config()
    contacts = E.load_enriched_contacts(cfg)
    eng = E.load_engagement_log(cfg)
    blocked = E.load_blocked_accounts(cfg)
    personal, _ = E.load_personal_network(cfg)
    hidden = {E.normalise_handle(h) for h in eng.get("hidden", []) if isinstance(h, str)}
    out = []
    for c in contacts:
        if E.contact_is_always_skip(c, cfg, blocked, personal, hidden)[0]:
            continue
        for t in cfg.ENGAGEMENT_TIERS[:3]:
            if E.matches_tier(c, t):
                h = E.contact_ig_handle(c)
                last = E.last_like_date_for_handle(eng, h)
                out.append({"handle": h, "name": c.get("name"), "tier": t["tier"],
                            "category": c.get("category"), "score": E.parse_score(c.get("match_score")),
                            "si_followers": c.get("ig_followers"),
                            "si_enriched_at": str(c.get("ig_enriched_at") or "")[:10],
                            "last_liked": str(last) if last else None})
                break
    # Budget: all T1/T2; T3 only those off the 40d cooldown, max 40 (oldest like first).
    t12 = [t for t in out if t["tier"] < 3]
    t3 = [t for t in out if t["tier"] == 3 and (not t["last_liked"] or
          (date.today() - date.fromisoformat(t["last_liked"])).days >= 40)]
    t3.sort(key=lambda t: t["last_liked"] or "")
    return t12 + t3[:40]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ts = targets()
    print(f"targets: {len(ts)} (T1 {sum(t['tier']==1 for t in ts)}, T2 {sum(t['tier']==2 for t in ts)}, T3 {sum(t['tier']==3 for t in ts)})")
    est = len(ts) * 2
    print(f"est calls: <= {est}")
    if a.dry_run:
        return 0
    import ig_daily_ledger as ledger
    from ig_data_provider import Provider, ProviderError
    ledger.check_and_claim("ig_like_list_check", kind="provider", est_calls=est,
                           endpoint="provider_profile+media")
    p = Provider(sleep=0.3)
    now = time.time()
    for i, t in enumerate(ts, 1):
        try:
            prof = p.profile(t["handle"])
        except ProviderError as exc:
            t["status"] = "error"; t["error"] = str(exc)[:120]; print(i, t["handle"], "error"); continue
        if not prof:
            t["status"] = "gone"; print(i, t["handle"], "gone"); continue
        t.update(live_followers=prof["follower_count"], live_posts=prof["media_count"],
                 private=prof["is_private"], bio=prof["biography"][:160], category_name=prof["category_name"])
        if prof["is_private"]:
            t["status"] = "private"; print(i, t["handle"], "private"); continue
        if not prof["media_count"]:
            t["status"] = "no_posts"; print(i, t["handle"], "no posts"); continue
        try:
            ep = p.newest_post_epoch(prof["id"])
        except ProviderError as exc:
            t["status"] = "error"; t["error"] = str(exc)[:120]; continue
        t["newest_post"] = datetime.fromtimestamp(ep, timezone.utc).date().isoformat() if ep else None
        age = (now - ep) / 86400 if ep else None
        t["post_age_days"] = round(age) if age is not None else None
        t["status"] = "active" if age is not None and age <= 90 else "inactive"
        print(i, t["handle"], t["status"], t.get("post_age_days"))
    OUT.write_text(json.dumps({"checked_at": date.today().isoformat(), "calls": p.calls,
                               "targets": ts}, indent=2, ensure_ascii=False) + "\n")
    print(f"calls used: {p.calls} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
