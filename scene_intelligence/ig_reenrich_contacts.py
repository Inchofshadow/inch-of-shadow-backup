"""
scene_intelligence/ig_reenrich_contacts.py
------------------------------------------
Registry job: contact re-enrichment in small daily batches (Part 4 of
plans/ig-ops-autopilot.md, Amir-approved 2026-08-31).

Why: 472 of 488 IG contacts had 90-180 day old enrichment — follower counts,
bios and dead-flags all drifted (@eskimorecordings: stored 4,654 / live 5,066,
which is over the 5K label ceiling). Nothing owned this rot.

How it stays safe (the May-03 incident was ~238 fetches in one run):
  - BATCH_SIZE profiles per run, oldest ig_enriched_at first — the whole
    estate refreshes in ~10 quiet days and then cycles.
  - Guard-held borderline labels (LABEL_CEILING_STALE_GUARD) jump the queue:
    they are excluded from Scene likes until re-checked, so freshness gives
    back like-supply immediately.
  - Claims the daily IG ledger slot; refuses to run if anything else ran.
  - Class A breaker: MAX_CONSECUTIVE_FAILURES failed fetches in a row stop
    the run (SOP 4.3), partial progress is saved, no retry the same day.
  - Human pacing between calls; atomic write + backup.

Run:
    python3 scene_intelligence/ig_reenrich_contacts.py --dry-run
    python3 scene_intelligence/ig_reenrich_contacts.py
    python3 scene_intelligence/ig_reenrich_contacts.py --batch 40
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent
REPO = SI_DIR.parent
sys.path.insert(0, str(SI_DIR))

CONTACTS_FILE = SI_DIR / "enriched_contacts.json"
BATCH_SIZE = 40
MAX_CONSECUTIVE_FAILURES = 5
STALE_AFTER_DAYS = 90


def _age_days(iso: str | None, today: date) -> int:
    if not iso:
        return 10_000
    try:
        return (today - date.fromisoformat(str(iso)[:10])).days
    except (ValueError, TypeError):
        return 10_000


def _is_guard_held(x: dict, cfg) -> bool:
    guard = getattr(cfg, "LABEL_CEILING_STALE_GUARD", None) or {}
    if not guard.get("enabled") or str(x.get("category", "")).lower() != "label":
        return False
    f = x.get("ig_followers") or 0
    ceiling = int(cfg.ALWAYS_SKIP_RULES["skip_labels_above_followers"])
    return f >= ceiling * (1.0 - float(guard.get("margin_pct", 0.10)))


def pick_batch(contacts: list[dict], today: date, batch: int, cfg) -> list[dict]:
    """Stalest first; guard-held borderline labels jump the queue."""
    cands = [
        x for x in contacts
        if x.get("ig_username")
        and not x.get("ig_handle_dead")
        and _age_days(x.get("ig_enriched_at"), today) > STALE_AFTER_DAYS
    ]
    cands.sort(key=lambda x: (not _is_guard_held(x, cfg),
                              -_age_days(x.get("ig_enriched_at"), today)))
    return cands[:batch]


def apply_profile(x: dict, prof: dict, now_iso: str) -> None:
    """Write a fresh profile onto a contact (normalised provider shape)."""
    x["ig_followers"] = prof["follower_count"]
    if prof.get("following_count") is not None:
        x["ig_following"] = prof["following_count"]
    if prof.get("media_count") is not None:
        x["ig_posts"] = prof["media_count"]
    for src, dst in (("is_private", "ig_is_private"), ("is_verified", "ig_is_verified"),
                     ("biography", "ig_bio")):
        if prof.get(src) is not None:
            x[dst] = prof[src]
    x["ig_enriched_at"] = now_iso
    x.pop("ig_reenrich_failed_at", None)


def run_batch(batch: list[dict], fetch, today: date, now_iso: str, pace) -> tuple[int, int, int]:
    """fetch(username) -> ("ok", profile) | ("missing", None) | ("error", None).
    "missing" twice (on two different days) flags the handle dead; "error" is
    transient (provider/network) and never flags anything."""
    ok = fail = dead = consecutive = 0
    for i, x in enumerate(batch):
        u = x["ig_username"]
        status, prof = fetch(u)
        tag = f"  [{i+1}/{len(batch)}] @{u}:"
        if status == "ok" and prof and prof.get("follower_count") is not None:
            consecutive = 0
            apply_profile(x, prof, now_iso)
            ok += 1
            print(f"{tag} {prof['follower_count']} followers — refreshed")
        elif status == "missing":
            consecutive = 0
            fail += 1
            prev = x.get("ig_reenrich_failed_at")
            if prev and prev != str(today):
                x["ig_handle_dead"] = True
                x["ig_handle_dead_at"] = str(today)
                dead += 1
                print(f"{tag} not found twice — flagged dead")
            else:
                x["ig_reenrich_failed_at"] = str(today)
                print(f"{tag} not found (will retry once)")
        else:
            consecutive += 1; fail += 1
            print(f"{tag} fetch error")
        if consecutive >= MAX_CONSECUTIVE_FAILURES:
            print(f"\n[BREAKER] {consecutive} consecutive errors — stopping "
                  f"(SOP 4.3). Partial progress saves below; do not retry today.")
            break
        if i < len(batch) - 1:
            pace()
    return ok, fail, dead


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-enrich stale IG contacts in one daily batch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, default=BATCH_SIZE)
    ap.add_argument("--override-ledger", action="store_true")
    ap.add_argument("--override-reason", default=None, metavar="TEXT",
                    help="required with --override-ledger (logged)")
    args = ap.parse_args()

    import ig_engagement_config as cfg
    import ig_audit_queue_freshness as auditmod

    today = date.today()
    contacts_blob = json.loads(CONTACTS_FILE.read_text(encoding="utf-8"))
    contacts = contacts_blob if isinstance(contacts_blob, list) else contacts_blob.get("contacts", [])

    batch = pick_batch(contacts, today, args.batch, cfg)
    stale_total = len([x for x in contacts if x.get("ig_username")
                       and _age_days(x.get("ig_enriched_at"), today) > STALE_AFTER_DAYS
                       and not x.get("ig_handle_dead")])
    held = sum(1 for x in batch if _is_guard_held(x, cfg))
    print(f"=== IG contact re-enrichment [{today}] ===")
    print(f"stale total: {stale_total} | this batch: {len(batch)} "
          f"(guard-held labels first: {held})")

    if not batch:
        print("Nothing stale. Done.")
        return 0
    if args.dry_run:
        for x in batch[:10]:
            print(f"  would refresh @{x['ig_username']} "
                  f"(enriched {str(x.get('ig_enriched_at'))[:10]})")
        print("[DRY-RUN] no API calls made, nothing written.")
        return 0

    import ig_daily_ledger as ledger
    from ig_data_provider import available as provider_available

    now_iso = datetime.now(timezone.utc).isoformat()
    if provider_available():
        # Provider path (2026-11-04, Amir "y"): reads via HikerAPI, Instagram
        # never contacted as Amir. 1 call per contact, inside the 300/day cap.
        from ig_data_provider import Provider, ProviderError
        from ig_ops_guards import get_pause, blocks_api_jobs
        pause = get_pause("ig")
        if pause and blocks_api_jobs(pause):
            raise SystemExit("[REENRICH] IG automation is paused (scope: all). Nothing runs.")
        ledger.check_and_claim("ig_reenrich_contacts", kind="provider",
                               est_calls=len(batch), endpoint="provider_profile")
        prov = Provider(sleep=0.3)
        print("[REENRICH] provider mode: reads via HikerAPI")

        def fetch(u):
            try:
                prof = prov.profile(u)
            except ProviderError as exc:
                print(f"  [PROVIDER ERROR] @{u}: {exc}", file=sys.stderr)
                return "error", None
            return ("ok", prof) if prof else ("missing", None)
        pace = lambda: None
    else:
        if not getattr(cfg, "IG_DIRECT_API_ENABLED", True):
            raise SystemExit("[REENRICH] Direct Instagram reads are OFF and no HIKERAPI_KEY "
                             "in .env. Nothing runs.")
        ledger.check_and_claim("ig_reenrich_contacts", **ledger.override_kwargs(args))
        sid, csrf = auditmod._load_credentials()
        session = auditmod._build_session(sid, csrf)

        def fetch(u):
            body = auditmod._fetch_profile(session, u)   # raises on 401/429
            user = auditmod._walk_for_user(body) if body else None
            if not user or (user.get("edge_followed_by") or {}).get("count") is None:
                return "missing", None
            return "ok", {
                "follower_count": (user.get("edge_followed_by") or {}).get("count"),
                "following_count": (user.get("edge_follow") or {}).get("count"),
                "media_count": (user.get("edge_owner_to_timeline_media") or {}).get("count"),
                "is_private": user.get("is_private"), "is_verified": user.get("is_verified"),
                "biography": user.get("biography")}
        pace = lambda: time.sleep(random.uniform(3, 7))

    ok, fail, dead = run_batch(batch, fetch, today, now_iso, pace)

    backup = SI_DIR / "backups" / f"enriched_contacts.json.bak.{today.strftime('%Y%m%d')}_reenrich"
    backup.write_text(CONTACTS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    fd, tmp = tempfile.mkstemp(dir=str(SI_DIR), prefix=".ec_tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(contacts_blob, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, CONTACTS_FILE)
    print(f"\n[OK] saved. refreshed {ok}, failed {fail} (newly dead {dead}). "
          f"~{max(stale_total - ok, 0)} stale remain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
