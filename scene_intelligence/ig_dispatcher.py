"""IG Ops Dispatcher — the deterministic morning brain (T-003, design
plans/ig-ops-autopilot.md, Amir-approved 2026-08-27; law locked 2026-08-30).

One run per morning (~09:30 Berlin via launchd). Zero Claude tokens, zero
human memory required. It decides what today needs and either runs THE one
right job or does nothing — and every decision, run or skip, is appended to
docs/reports/dispatch-log.md with the reason.

Decision rules, in priority order (all state-driven):
  1. HARD GATES: Amir's pause -> do nothing. Detection cooldown -> do
     nothing. Outside daytime hours -> do nothing. (ig_ops_guards — the
     gates that review finding L1 said nothing enforced.)
  2. Export freshness: if the newest IG data export is older than
     EXPORT_CADENCE_DAYS (30), notify Amir to pull one (zero-API path).
     This replaces the retired routine follow-back checker.
  3. Session day (Mon/Wed/Fri/Sat): reserve the day for the 15:00 browser
     session — no API job runs. (Sessions spend zero API budget.)
  4. Quiet day (Tue/Thu): exactly ONE maintenance job, by need:
       a. vetted reach pool < POOL_MIN (30) -> freshness audit, sized to the
          profile_reads budget
       b. else queue builder age > BUILDER_MAX_AGE_DAYS (14) -> queue builder
       c. else nothing ("nothing needed" is a valid, logged decision)
  5. Sunday: off.

The dispatcher never overrides the ledger: jobs it launches claim their own
budgeted slot and can still refuse (that refusal is logged too). It never
clears pauses, never resumes anything — resume is Amir's alone.

Run modes:
  python3 scene_intelligence/ig_dispatcher.py            # decide + execute
  python3 scene_intelligence/ig_dispatcher.py --dry-run  # decide + print only
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SI_DIR = Path(__file__).parent
REPO = SI_DIR.parent
LOG_PATH = REPO / "docs" / "reports" / "dispatch-log.md"
QUEUE_PATH = SI_DIR / "ig_target_list.json"
EXPORTS_GLOB = "instagram-inch_of_shadow-*"
DATA_DIR = REPO / "data"

SESSION_DAYS = {"Monday", "Wednesday", "Friday", "Saturday"}
QUIET_DAYS = {"Tuesday", "Thursday"}
POOL_MIN = 30
BUILDER_MAX_AGE_DAYS = 14
EXPORT_CADENCE_DAYS = 30
AUDIT_MAX_COUNT = 30  # = profile_reads daily budget
GENTLE_FIRST_AUDIT = 10  # 2026-09-11: first API touch after a quiet week reads 10, not 30


def api_runs_in_last_days(today: date, days: int = 7) -> int:
    """API-kind ledger runs in the `days` days before `today` (exclusive)."""
    try:
        from scene_intelligence.ig_daily_ledger import runs_on
    except ImportError:
        from ig_daily_ledger import runs_on
    n = 0
    for i in range(1, days + 1):
        d = (today - timedelta(days=i)).isoformat()
        n += sum(1 for r in runs_on(d) if r.get("kind", "api") == "api")
    return n


def audit_count(today: date) -> int:
    """30 normally; 10 when no API job ran in the last 7 days (first touch
    after a throttle or a long pause — a gentle re-entry, Amir 2026-09-11)."""
    return GENTLE_FIRST_AUDIT if api_runs_in_last_days(today) == 0 else AUDIT_MAX_COUNT
SEEDS_PER_RUN = 8           # T-013: seed slice per builder run. 14 -> 8 on 2026-09-02 (~40 est calls)
MAX_JOB_EST_CALLS = 50      # 2026-09-02 "more calculated": never schedule a job estimated above the ~50 normal-day target
REST_DAY_AFTER_BULK = True  # 2026-09-02: the day after a builder crawl is an API rest day — every throttle so far (08-27, 08-29, 09-02) followed bulk enumeration
REENRICH_BATCH = 40         # registry Part 4: contacts refreshed per quiet day
REENRICH_STALE_DAYS = 90
REENRICH_MIN_BATCH = 5       # below this the re-check waits for a roomier day
FOLLOW_LISTS_MAX_AGE_DAYS = 7   # M-13: weekly, so follow-back verification stays fresh for the sweep (was 30, M-12)
FOLLOW_FLAGS_CALLS = 85         # = si_follow_flags.FETCH_BUDGET (claim size)
BACKUPS_KEEP_DAYS = 60      # registry: backups/ retention window
LOG_ARCHIVE_TRIGGER_KB = 1500  # registry: engagement_log archival trigger


def bulk_job_yesterday(today: date) -> str | None:
    """Name of a bulk-enumeration job (queue builder) that ran yesterday, else None.
    Read from the ledger. Used for REST_DAY_AFTER_BULK."""
    try:
        led = json.loads((SI_DIR / "ig_daily_ledger.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    yday = (today - timedelta(days=1)).isoformat()
    for r in led.get("runs", []):
        if r.get("date") == yday and "builder" in str(r.get("script", "")):
            return r.get("script")
    return None


def stale_contacts_count(today: date) -> int:
    """Registry Part 4 trigger: contacts whose ig_enriched_at is > 90d old."""
    try:
        blob = json.loads((SI_DIR / "enriched_contacts.json").read_text(encoding="utf-8"))
        cs = blob if isinstance(blob, list) else blob.get("contacts", [])
    except Exception:
        return 0
    n = 0
    for x in cs:
        if not x.get("ig_username") or x.get("ig_handle_dead"):
            continue
        iso = str(x.get("ig_enriched_at") or "")[:10]
        try:
            if (today - date.fromisoformat(iso)).days > REENRICH_STALE_DAYS:
                n += 1
        except ValueError:
            n += 1
    return n


def seed_yield(data: dict) -> list[tuple[str, int, int]]:
    """[(seed, candidates, followed)] ranked best yield first, from queue
    provenance (2026-09-14: shared by the report and the provider builder)."""
    from collections import defaultdict
    tot: dict = defaultdict(int); good: dict = defaultdict(int)
    for e in data.get("queue", []):
        src = e.get("source") or e.get("discovery_source") or ""
        for sd in str(src).split(","):
            sd = sd.strip().replace("followers_", "")
            if not sd:
                continue
            tot[sd] += 1
            if e.get("status") in ("followed", "already_following"):
                good[sd] += 1
    return sorted(((sd, tot[sd], good[sd]) for sd in tot),
                  key=lambda t: (-(t[2] / max(t[1], 1)), -t[2]))


def unvetted_pending() -> int:
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    return sum(1 for e in data.get("queue", [])
               if e.get("status", "pending") == "pending" and not e.get("audit_date"))


def provider_plan(pool: int | None, unvetted: int, seeds_ranked: list, all_seeds: list) -> dict:
    """Decide today's provider jobs (2026-09-14, Amir approved).
    - audit: pool < POOL_MIN -> 100/day while the unchecked backlog is large,
      else 60. Any weekday. No IG timing law.
    - builder: only when unchecked names run low (< floor), best-yield seeds
      first, seeds never crawled yet interleaved so new ones get a chance."""
    try:
        from scene_intelligence import ig_engagement_config as cfg
    except ImportError:
        import ig_engagement_config as cfg
    P = getattr(cfg, "PROVIDER", {}) or {}
    plan: dict = {"audit": 0, "builder": []}
    if pool is not None and pool < POOL_MIN:
        plan["audit"] = int(P.get("audit_per_day_backlog", 100)) \
            if unvetted > int(P.get("backlog_threshold", 300)) else int(P.get("audit_per_day", 60))
    if unvetted < int(P.get("builder_unvetted_floor", 200)):
        n = int(P.get("builder_seeds_per_run", 8))
        known = [sd for sd, _t, _g in seeds_ranked if sd in all_seeds]
        fresh = [sd for sd in all_seeds if sd not in known]
        order: list = []
        while (known or fresh) and len(order) < n:
            if known:
                order.append(known.pop(0))
            if fresh and len(order) < n:
                order.append(fresh.pop(0))
        plan["builder"] = order
    return plan


def _seed_yield_report(today: date) -> None:
    """Registry job (T-016): after every builder run, recompute per-seed yield
    from queue provenance so retire/keep decisions are always data-backed
    (the 2026-08-31 analysis found the famous anchors converting at 3%).
    Zero API. Failures never propagate."""
    try:
        from collections import defaultdict
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        tot: dict = defaultdict(int); good: dict = defaultdict(int)
        for e in data.get("queue", []):
            src = e.get("source") or e.get("discovery_source") or ""
            for sd in str(src).split(","):
                sd = sd.strip().replace("followers_", "")
                if not sd:
                    continue
                tot[sd] += 1
                if e.get("status") in ("followed", "already_following"):
                    good[sd] += 1
        lines = [f"# Seed yield — auto after builder run {today}", "",
                 "| seed | candidates | followed | yield |", "|---|---|---|---|"]
        for sd in sorted(tot, key=lambda x: -(good[x] / max(tot[x], 1))):
            if tot[sd] < 5:
                continue
            lines.append(f"| {sd} | {tot[sd]} | {good[sd]} | {100 * good[sd] / tot[sd]:.1f}% |")
        lines.append("")
        lines.append("Rule of thumb (2026-08-31 analysis): sustained <5% => retire candidate; new seeds need 2+ builder cycles before judging.")
        out = REPO / "docs" / "reports" / f"seed-yield-{today.isoformat()}.md"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _log("hygiene: seed-yield", f"report written ({len(lines) - 5} seeds) -> {out.name}")
    except Exception as exc:
        _log("hygiene: seed-yield FAILED", str(exc))


def _local_hygiene(today: date, dry_run: bool) -> None:
    """Zero-API housekeeping (registry amendments 2026-08-31). Runs after the
    day's decision on quiet days; costs nothing, claims no ledger slot, and
    every action lands in the dispatch log. Failures never propagate."""
    # backups/ retention: compress files older than the keep window.
    try:
        import tarfile, time as _time
        bdir = SI_DIR / "backups"
        cut = _time.time() - BACKUPS_KEEP_DAYS * 86400
        old = [f for f in bdir.iterdir()
               if f.is_file() and not f.name.endswith(".tar.gz")
               and f.stat().st_mtime < cut]
        if old and not dry_run:
            arch = bdir / f"archive_pre_{today.isoformat()}.tar.gz"
            with tarfile.open(arch, "w:gz") as t:
                for f in old:
                    t.add(f, arcname=f.name)
            with tarfile.open(arch) as t:          # verify before deleting
                assert len(t.getnames()) == len(old)
            for f in old:
                f.unlink()
            _log("hygiene: backups", f"archived {len(old)} files > {BACKUPS_KEEP_DAYS}d "
                                     f"into {arch.name}")
        elif old:
            _log("hygiene: backups (dry)", f"{len(old)} files would archive")
    except Exception as exc:
        _log("hygiene: backups FAILED", str(exc))

    # engagement_log size watch: notify when the archival trigger fires
    # (the archival itself is a supervised job, not an unattended one).
    try:
        kb = (SI_DIR / "engagement_log.json").stat().st_size // 1024
        if kb > LOG_ARCHIVE_TRIGGER_KB:
            msg = f"engagement_log.json at {kb}KB > {LOG_ARCHIVE_TRIGGER_KB}KB — schedule the archival job"
            _notify("IG dispatcher", msg)
            _log("notify-amir", msg)
    except Exception as exc:
        _log("hygiene: log-size FAILED", str(exc))


def _notify(title: str, message: str) -> None:
    """Mac notification, same pattern the loop closer uses. Best-effort."""
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message}" with title "{title}"'],
            capture_output=True, timeout=10)
    except Exception:
        pass


def _log(decision: str, why: str, outcome: str = "") -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"- {stamp} — **{decision}** — {why}"
    if outcome:
        line += f" — {outcome}"
    if not LOG_PATH.exists():
        LOG_PATH.write_text(
            "# IG dispatch log\n\nEvery dispatcher decision, run or skip, "
            "one line each. Newest at the bottom.\n\n", encoding="utf-8")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def newest_export_age_days(today: date) -> int | None:
    """Days since the newest IG data export folder, None if none exists."""
    best = None
    for p in DATA_DIR.glob(EXPORTS_GLOB):
        parts = p.name.split("-")
        # instagram-inch_of_shadow-YYYY-MM-DD-suffix
        try:
            d = date.fromisoformat("-".join(parts[-4:-1]))
        except (ValueError, IndexError):
            continue
        if best is None or d > best:
            best = d
    return (today - best).days if best else None


def vetted_pool_depth() -> int | None:
    """Followable pool: pending + audited AND passing the engine's reach
    filter (2026-09-21; the raw count said 16 when the plan could follow 0,
    so refills never triggered). Falls back to the raw count on error."""
    try:
        try:
            from scene_intelligence.ig_engagement import followable_pool_size
        except ImportError:
            from ig_engagement import followable_pool_size  # type: ignore
        return followable_pool_size()
    except Exception:
        pass
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return sum(1 for e in data.get("queue", [])
               if e.get("status") == "pending" and e.get("audit_date"))


def builder_age_days(today: date) -> int | None:
    """Days since the queue builder last refreshed (meta stamp)."""
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    meta = data.get("_meta", {})
    # "last_builder_run" is the key ig_queue_builder.py actually writes —
    # the original list guessed four names that never existed, so this
    # returned None forever and the builder trigger could not fire (caught
    # 2026-08-31 in a dispatch simulation, with the builder 16 days stale).
    for key in ("last_builder_run", "last_updated",
                "last_built", "built_at", "last_refresh", "generated"):
        raw = str(meta.get(key, ""))[:10]
        try:
            return (today - date.fromisoformat(raw)).days
        except ValueError:
            continue
    return None


def _run_job(cmd: list[str], label: str, dry_run: bool) -> str:
    if dry_run:
        return f"DRY-RUN: would execute `{' '.join(cmd)}`"
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                          timeout=3600)
    # Keep stderr on failure: a SystemExit("[AUDIT] ... 401/429") lands on
    # stderr while stdout holds "[1/30] checking ..." -- on 2026-09-05 the
    # `stdout or stderr` form lost the actual reason for the exit.
    tail = (proc.stdout or "").strip().splitlines()[-3:]
    if proc.returncode != 0:
        err = (proc.stderr or "").strip().splitlines()[-2:]
        tail = (tail + [f"stderr: {e}" for e in err])[-4:]
    outcome = f"exit {proc.returncode}; " + " / ".join(tail)
    if proc.returncode != 0:
        _notify("IG dispatcher", f"{label} exited {proc.returncode}")
    return outcome


def provider_requests_left() -> int | None:
    """Remaining prepaid requests at the provider, or None if unknown."""
    try:
        from scene_intelligence.ig_data_provider import Provider
    except ImportError:
        from ig_data_provider import Provider
    try:
        bal = Provider().balance() or {}
        return int(bal.get("requests")) if bal.get("requests") is not None else None
    except Exception:
        return None


def _provider_day(today: date, dry_run: bool) -> int:
    """Provider-mode day (2026-09-14): reads never touch Instagram as Amir, so
    no cooldown, no daytime, no rest day, no session-day reservation. Both
    jobs may run; the ledger's provider cap is the only brake."""
    try:
        from scene_intelligence.ig_queue_builder import DEFAULT_SEEDS
    except ImportError:
        from ig_queue_builder import DEFAULT_SEEDS
    pool = vetted_pool_depth()
    unv = unvetted_pending()
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {"queue": []}
    plan = provider_plan(pool, unv, seed_yield(data), list(DEFAULT_SEEDS))
    # Balance guard (2026-09-14): shrink the day to what is paid for, and say
    # so, instead of dying halfway. 2 calls per audited candidate, ~10 per seed.
    remaining = provider_requests_left()
    if remaining is not None:
        need = 2 * plan["audit"] + 10 * len(plan["builder"])
        if need > remaining:
            plan["builder"] = plan["builder"][: max(0, (remaining - 2 * plan["audit"]) // 10)] \
                if remaining >= 2 * plan["audit"] else []
            plan["audit"] = min(plan["audit"], max(0, remaining // 2))
            msg = (f"provider balance low: {remaining} requests left, needed ~{need} — "
                   f"today shrunk to audit {plan['audit']} / builder {len(plan['builder'])} seeds. "
                   f"Top up at hikerapi.com ($5 ≈ 4 months).")
            _notify("IG dispatcher", msg)
            _log("notify-amir", msg)
    ran = False
    if plan["builder"]:
        why = (f"unchecked names {unv} < floor — builder on best-yield seeds "
               f"{','.join(plan['builder'])} (provider)")
        outcome = _run_job([sys.executable, "scene_intelligence/ig_queue_builder.py",
                            "--seeds", ",".join(plan["builder"])], "queue builder", dry_run)
        _log("run: queue builder (provider)", why, outcome)
        if not dry_run:
            _seed_yield_report(today)
        ran = True
    if plan["audit"]:
        why = f"vetted pool {pool} < {POOL_MIN}, unchecked {unv} — audit --count {plan['audit']} (provider)"
        outcome = _run_job([sys.executable, "scene_intelligence/ig_audit_queue_freshness.py",
                            "--count", str(plan["audit"])], "freshness audit", dry_run)
        _log("run: freshness audit (provider)", why, outcome)
        ran = True
    spent = 2 * plan["audit"] + 10 * len(plan["builder"])
    ran = _provider_si_upkeep(today, dry_run,
                              None if remaining is None else max(0, remaining - spent)) or ran
    if not ran:
        _log("skip", f"provider mode — pool {pool} >= {POOL_MIN} and unchecked {unv} above floor; nothing to do")
    _local_hygiene(today, dry_run)
    return 0


def provider_budget_left(today: date) -> int:
    """Calls left under PROVIDER.daily_call_cap after today's claims."""
    try:
        from scene_intelligence import ig_daily_ledger as L
    except ImportError:
        import ig_daily_ledger as L
    return max(0, L.provider_cap() - L.provider_calls_today(today.isoformat()))


def follow_lists_age_days(today: date) -> int | None:
    try:
        from scene_intelligence.si_follow_flags import lists_age_days
    except ImportError:
        from si_follow_flags import lists_age_days
    return lists_age_days(today)


def _provider_si_upkeep(today: date, dry_run: bool, balance: int | None) -> bool:
    """SI-01/SI-02 (2026-11-04, Amir "y"): after the queue jobs, spend what the
    day's cap leaves on keeping Scene Intelligence fresh. Monthly own-list
    fetch + follow flags first (small, ~50 calls), then the contact re-check
    (1 call per contact, up to REENRICH_BATCH). Never above the cap."""
    ran = False
    left = provider_budget_left(today)
    if balance is not None:
        left = min(left, balance)
    age = follow_lists_age_days(today)
    if (age is None or age >= FOLLOW_LISTS_MAX_AGE_DAYS) and left >= FOLLOW_FLAGS_CALLS:
        why = f"own follower lists {age if age is not None else 'missing'}d old — refresh SI follow flags"
        outcome = _run_job([sys.executable, "scene_intelligence/si_follow_flags.py",
                            "--fetch", "--apply"], "SI follow flags", dry_run)
        _log("run: SI follow flags (provider)", why, outcome)
        rec = _run_job([sys.executable, "scene_intelligence/ig_reciprocity_from_lists.py",
                        "--apply"], "follow-back verification", dry_run)
        _log("run: follow-back verification (from lists)", "fresh follower list -> tracker (0 calls)", rec)
        left -= FOLLOW_FLAGS_CALLS
        ran = True
    stale = stale_contacts_count(today)
    n = min(REENRICH_BATCH, stale, left)
    if n >= REENRICH_MIN_BATCH:
        why = f"{stale} contacts with enrichment > {REENRICH_STALE_DAYS}d — re-check {n} (provider, {left} calls left)"
        outcome = _run_job([sys.executable, "scene_intelligence/ig_reenrich_contacts.py",
                            "--batch", str(n)], "contact re-enrichment", dry_run)
        _log("run: contact re-enrichment (provider)", why, outcome)
        ran = True
    elif stale:
        _log("note", f"{stale} stale contacts, only {left} provider calls left today — re-check waits")
    return ran


def decide_and_run(now: datetime | None = None, dry_run: bool = False) -> int:
    now = now or datetime.now()
    today = now.date()
    weekday = now.strftime("%A")

    # 1. Hard gates — a refusal is a logged decision, not an error.
    try:
        from scene_intelligence.ig_ops_guards import (
            get_pause, active_detection_cooldown, is_daytime)
    except ImportError:
        from ig_ops_guards import get_pause, active_detection_cooldown, is_daytime

    pause = get_pause("ig")
    try:
        from scene_intelligence.ig_ops_guards import blocks_api_jobs
    except ImportError:
        from ig_ops_guards import blocks_api_jobs
    if pause and blocks_api_jobs(pause):
        _log("skip", f"paused by {pause.get('paused_by', '?')} since "
                     f"{pause.get('at', '?')} — dispatcher never resumes")
        return 0
    if pause:
        # sessions-scoped pause: maintenance continues, and session days are
        # free for API work while no sessions run (2026-09-01).
        _log("note", f"sessions-scoped pause active ({pause.get('paused_by','?')}); "
                     f"API maintenance continues, session days treated as quiet")
    try:
        from scene_intelligence.ig_data_provider import available as _prov_available
    except ImportError:
        from ig_data_provider import available as _prov_available
    if _prov_available():
        return _provider_day(today, dry_run)

    cooldown = active_detection_cooldown(now)
    if cooldown:
        ev, until = cooldown
        _log("skip", f"detection cooldown ({ev.get('date')} "
                     f"{ev.get('type', '?')}) until {until:%Y-%m-%d %H:%M}")
        return 0
    if not is_daytime(now):
        _log("skip", f"outside daytime window at {now:%H:%M} — law: API work "
                     f"09:00-21:00 only")
        return 0

    # 2. Export freshness (replaces the retired routine checker).
    age = newest_export_age_days(today)
    if age is None or age > EXPORT_CADENCE_DAYS:
        msg = (f"IG data export is {age if age is not None else 'MISSING'} "
               f"days old (cadence {EXPORT_CADENCE_DAYS}d) — pull a fresh one "
               f"(Accounts Center -> Download your information, ALL TIME)")
        _notify("IG dispatcher", msg)
        _log("notify-amir", msg)
        # An overdue export never blocks the rest of the day's decision.

    # 2b. REST DAY AFTER BULK (2026-09-02): a builder crawl yesterday means no
    # API job today, whatever the triggers say. Instagram throttled us after
    # every bulk enumeration so far; spacing them is cheaper than cooldowns.
    if REST_DAY_AFTER_BULK:
        bulk = bulk_job_yesterday(today)
        if bulk:
            _log("skip", f"rest day — {bulk} ran yesterday; no API job the day after a bulk crawl")
            _local_hygiene(today, dry_run)
            return 0

    # 3-5. Day type.
    if weekday == "Sunday":
        _log("skip", "Sunday — off day")
        return 0
    if weekday in SESSION_DAYS and not pause:
        _log("skip", "session day — day reserved for the 15:00 browser "
                     "session; no API job")
        return 0

    # Quiet day: ONE maintenance job by need.
    # ORDER (fixed 2026-08-31): builder BEFORE audit. When both fire, the
    # audit must vet the builder's fresh candidates, not the stale tail —
    # on 2026-09-01 both triggers were live (pool 19, builder 15d) and the
    # old order would have spent the day's budget auditing pre-seed-refresh
    # leftovers while six new seeds sat uncrawled.
    pool = vetted_pool_depth()
    b_age = builder_age_days(today)

    if b_age is not None and b_age > BUILDER_MAX_AGE_DAYS:
        # T-013 BATCHING CURSOR (2026-09-01): a full 33-seed run estimates
        # ~165 calls and can NEVER fit the 150 absolute ceiling — on 09-01
        # the builder lawfully refused itself and would have forever. Each
        # run now takes the next SEEDS_PER_RUN slice of DEFAULT_SEEDS
        # (rotating cursor persisted in the queue meta), so the full list
        # is covered across consecutive builder days.
        try:
            from scene_intelligence.ig_queue_builder import DEFAULT_SEEDS
        except ImportError:
            from ig_queue_builder import DEFAULT_SEEDS
        qd = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        cur = int(qd.get("_meta", {}).get("builder_seed_cursor", 0)) % max(len(DEFAULT_SEEDS), 1)
        batch = [DEFAULT_SEEDS[(cur + i) % len(DEFAULT_SEEDS)]
                 for i in range(min(SEEDS_PER_RUN, len(DEFAULT_SEEDS)))]
        est = len(batch) * 5  # builder's own estimate: ~5 calls per seed
        if est > MAX_JOB_EST_CALLS:
            batch = batch[: max(1, MAX_JOB_EST_CALLS // 5)]
        why = (f"queue builder {b_age}d old > {BUILDER_MAX_AGE_DAYS}d — slice "
               f"[{cur}:{cur + len(batch)}] of {len(DEFAULT_SEEDS)} seeds (~{len(batch) * 5} calls)")
        outcome = _run_job(
            [sys.executable, "scene_intelligence/ig_queue_builder.py",
             "--seeds", ",".join(batch)], "queue builder", dry_run)
        if not dry_run and "exit" not in outcome.lower():
            qd = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))  # re-read post-run
            qd.setdefault("_meta", {})["builder_seed_cursor"] = (cur + len(batch)) % len(DEFAULT_SEEDS)
            tmp = QUEUE_PATH.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(qd, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(QUEUE_PATH)
        _log("run: queue builder", why, outcome)
        if not dry_run:
            _seed_yield_report(today)
        _local_hygiene(today, dry_run)
        return 0

    if pool is not None and pool < POOL_MIN:
        n = audit_count(today)
        why = (f"vetted pool {pool} < {POOL_MIN} — freshness audit --count {n}"
               + (" (gentle first touch after a quiet week)" if n == GENTLE_FIRST_AUDIT else ""))
        outcome = _run_job(
            [sys.executable, "scene_intelligence/ig_audit_queue_freshness.py",
             "--count", str(n)], "freshness audit", dry_run)
        _log("run: freshness audit", why, outcome)
        _local_hygiene(today, dry_run)
        return 0

    # Registry Part 4 (2026-08-31): contact re-enrichment batches whenever
    # queue supply is healthy — 40/day until the stale estate (472 contacts
    # at 90-180d when the registry landed) is refreshed, then it idles.
    stale = stale_contacts_count(today)
    if stale > 0:
        why = f"{stale} contacts with enrichment > {REENRICH_STALE_DAYS}d — batch of {REENRICH_BATCH}"
        outcome = _run_job(
            [sys.executable, "scene_intelligence/ig_reenrich_contacts.py",
             "--batch", str(REENRICH_BATCH)], "contact re-enrichment", dry_run)
        _log("run: contact re-enrichment", why, outcome)
        _local_hygiene(today, dry_run)
        return 0

    _log("skip", f"nothing needed (pool {pool if pool is not None else '?'}"
                 f"/{POOL_MIN}, builder age "
                 f"{b_age if b_age is not None else '?'}d, stale contacts 0)")
    _local_hygiene(today, dry_run)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="decide and log, execute nothing")
    args = ap.parse_args()
    return decide_and_run(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
