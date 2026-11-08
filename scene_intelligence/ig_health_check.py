#!/usr/bin/env python3
"""ig_health_check.py — silent-failure detector for the IG automation.

READ-ONLY. Never writes a file, never makes a network call. Safe to run any
time, including during a detection cooldown.

Why this exists (2026-08-19): every serious bug found in this system was
SILENT. The skip-cooldown matched an action string the engine never writes and
returned 0 for months. The reach planner ignored `audit_date` and served
unfollowable junk. The scorer punished the circuit breaker for firing. None of
them raised an error — the reports looked fine while the automation quietly did
the wrong thing.

Scheduling scripts does not catch that. Checking INVARIANTS against live data
does. Each check below corresponds to a real incident.

Exit codes: 0 healthy · 1 warnings · 2 critical
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

SI = Path(__file__).parent
BASE = SI.parent

CRITICAL: list[str] = []
WARN: list[str] = []
OK: list[str] = []


def load(name: str, default=None):
    try:
        return json.loads((SI / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def days_since(iso: str | None) -> int | None:
    try:
        return (date.today() - date.fromisoformat(str(iso)[:10])).days
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
tracker = load("ig_follow_tracker.json", {}) or {}
queue = load("ig_target_list.json", {}) or {}
eng_log = (load("engagement_log.json", {}) or {}).get("log", {})
autonomy = load("autonomy_state.json", {}) or {}
ledger = load("ig_daily_ledger.json", {}) or {}

stats = tracker.get("stats", {})
active = tracker.get("active_follows", [])
q = queue.get("queue", [])


# --- 1. Autonomy / pause state ---------------------------------------------
# 2.0 (review L1): a pause is CRITICAL, never a warning — the old wording
# ("warnings only — safe to run") described a live pause as runnable.
pause = (autonomy.get("pauses") or {}).get("ig") or (
    {"reason": "legacy global pause"} if autonomy.get("paused") else None)
if pause:
    CRITICAL.append(
        f"IG autonomy is PAUSED (nothing may run; resume is Amir's alone): "
        f"{str(pause.get('reason'))[:90]}")
else:
    OK.append("IG autonomy running")


# --- 2. Unmerged sessions (tracker drift) ----------------------------------
unmerged = sorted(p.name for p in SI.glob("ig_session_*.jsonl"))
if unmerged:
    CRITICAL.append(f"UNMERGED session logs (tracker is stale): {unmerged}")
else:
    OK.append("no unmerged sessions")


# --- 3. Vetted reach pool depth --------------------------------------------
pending = [e for e in q if e.get("status") == "pending"]
vetted = [e for e in pending if e.get("audit_date")]
if len(vetted) < 10:
    CRITICAL.append(f"vetted pool {len(vetted)} — below a single session's follows")
elif len(vetted) < 30:
    WARN.append(f"vetted pool {len(vetted)} (threshold 30) — schedule an audit")
else:
    OK.append(f"vetted pool {len(vetted)}")


# --- 4. Skip-cooldown actually firing --------------------------------------
# 2026-08-17: matched "skipped" while the engine writes "ig_skip" -> dead for
# months, so dead accounts were re-served every session until the breaker fired.
try:
    import sys
    sys.path.insert(0, str(BASE))
    from scene_intelligence import ig_engagement as _eng  # type: ignore
    skip_actions = getattr(_eng, "IG_SKIP_ACTIONS", None)
except Exception:
    skip_actions = None

if not skip_actions:
    WARN.append("could not import IG_SKIP_ACTIONS — skip-cooldown unverifiable")
else:
    log_actions = {e.get("action") for es in eng_log.values() for e in es
                   if isinstance(e, dict) and e.get("action")}
    if not (skip_actions & log_actions):
        CRITICAL.append(
            f"skip-cooldown is DEAD: IG_SKIP_ACTIONS {sorted(skip_actions)} "
            f"matches nothing in the log")
    else:
        # is it benching anyone it should be?
        cutoff = date.today() - timedelta(days=7)
        repeat = 0
        for h, es in eng_log.items():
            n = sum(1 for e in es if isinstance(e, dict)
                    and e.get("action") in skip_actions
                    and e.get("date") and str(e["date"])[:10] >= cutoff.isoformat())
            if n >= 2:
                repeat += 1
        OK.append(f"skip-cooldown live ({repeat} accounts currently benchable)")


# --- 5. Reciprocator churn (must never lose one) ---------------------------
recips = [x for x in active if x.get("followed_back")]
hist = tracker.get("unfollowed_history", [])
churned = [x.get("username") for x in hist
           if x.get("follow_back") is True or x.get("followed_back") is True]  # Socials 38: both keys
if churned:
    WARN.append(f"{len(churned)} reciprocators in unfollowed_history (past churn): "
                f"{churned[:4]}{'...' if len(churned) > 4 else ''}")
OK.append(f"{len(recips)} reciprocators currently held")


# --- 6. Protected accounts still flagged -----------------------------------
protected = [x.get("username") for x in active if x.get("keep_following")]
OK.append(f"{len(protected)} protected accounts: {protected}")


# --- 7. Follow-back data freshness -----------------------------------------
age = days_since(stats.get("last_checked"))
if age is None:
    WARN.append("follow-back data: no last_checked recorded")
elif age > 7:
    CRITICAL.append(f"follow-back data {age}d stale — an unfollow sweep now risks churn")
elif age > 3:
    WARN.append(f"follow-back data {age}d old — refresh before the next sweep")
else:
    OK.append(f"follow-back data {age}d old")


# --- 8. SCRIPT FREQUENCY (the 2026-08-19 detection cause) -------------------
# Ran 2.9/wk safely for months, spiked to 7.0/wk in the 9 days before IG's
# (historical note removed 2026-08-25 — the cited warning never happened.)
runs = ledger.get("runs", [])
# 2026-11-03: count only kind "api" (legacy rows have no kind). Provider
# (HikerAPI) and browser rows are not IG API scripts and never fall under the
# one-per-day rule; counting them raised a false SCRIPT SPIKE.
last7 = [r for r in runs
         if r.get("kind", "api") == "api"
         and (days_since(r.get("date")) is not None and days_since(r["date"]) <= 7)]
per_day = Counter(r.get("date") for r in last7)
doubles = [d for d, n in per_day.items() if n > 1]
# The only HARD script rule is the daily ledger: one IG API script per day
# (enforced in code since 2026-07-19, audit P1-7). More than 7 runs in 7 days
# means that rule was overridden repeatedly — flag it. A prior "weekly budget"
# rationale citing an Aug 19 IG warning was removed 2026-08-25: Amir confirmed
# that warning never happened (fabricated record).
if len(last7) > 7:
    CRITICAL.append(f"SCRIPT SPIKE: {len(last7)} IG script runs in 7 days "
                    f"(the one-script-per-day ledger rule was overridden repeatedly)")
elif len(last7) > 5:
    WARN.append(f"{len(last7)} script runs in 7 days (heavy week — ledger allows max 1/day)")
else:
    OK.append(f"{len(last7)} script runs in 7 days")
if doubles:
    WARN.append(f"two IG scripts on the same day: {doubles}")


# --- 9. Recent session scores ----------------------------------------------
recent_ig = [r for r in autonomy.get("recent", []) if r.get("platform") == "ig"]
if recent_ig:
    last = recent_ig[-3:]
    OK.append("recent scores: " + ", ".join(f"{r['date']}={r['score']}" for r in last))
    if len(last) >= 2 and all(r["score"] <= 5 for r in last[-2:]):
        WARN.append("two consecutive scores <=5 — trend pause will arm")


# --- report ----------------------------------------------------------------
print(f"=== IG HEALTH CHECK  [{date.today()}] ===  (read-only, no API)\n")
for label, items, mark in (("CRITICAL", CRITICAL, "!!"),
                           ("WARNING", WARN, " !"),
                           ("OK", OK, " .")):
    if items:
        print(f"{label}:")
        for i in items:
            print(f" {mark} {i}")
        print()

if CRITICAL:
    print("VERDICT: CRITICAL — fix before the next session.")
    raise SystemExit(2)
if WARN:
    print("VERDICT: warnings only — safe to run, review above.")
    raise SystemExit(1)
print("VERDICT: healthy.")
raise SystemExit(0)
