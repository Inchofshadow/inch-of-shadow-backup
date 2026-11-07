"""Shared IG daily ledger — the enforcement point of the 2.0 API law.

LAW (Amir-approved 2026-08-30, TICKETS.md T-003/T-004; replaces BOTH the old
"one IG script per day" prose rule and the flat 150-call cap):

- ONE API job per day (the timing layer). A second same-day API claim is
  refused unless --override-ledger (the single deliberate escape hatch).
- PER-ENDPOINT budgets, not one big number: profile reads <= 30/day,
  friendship checks <= 20/day, roster walks 0 (banned), ~50 calls = a normal
  day (soft warning), 150 = absolute never-cross ceiling (hard refusal).
- DAYTIME only (09:00-21:00 local) — enforced here at the chokepoint.
- Browser sessions claim the ledger too (kind="browser", 0 API calls) so the
  day's record finally shows ALL activity (review finding L2); browser claims
  do not consume the one-API-job slot.

Every IG API entrypoint calls check_and_claim() BEFORE its first API call,
with est_calls + endpoint. The claim is written immediately (a crashed run
still counts). Writes are atomic + flock-guarded: two assistants share these
files (review atomicity class).

Ledger file: scene_intelligence/ig_daily_ledger.json
    {"runs": [{"date": "2026-08-31", "script": "ig_audit_queue_freshness",
               "ts": "...", "override": false, "override_reason": "...", "kind": "api",
               "est_calls": 42, "endpoint": "profile_reads"}, ...]}

CLI (for sessions and inspection):
    python3 scene_intelligence/ig_daily_ledger.py --claim ig_session --kind browser
    python3 scene_intelligence/ig_daily_ledger.py --show
"""
from __future__ import annotations

import fcntl
import json
from datetime import date, datetime, timedelta
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "ig_daily_ledger.json"
KEEP_DAYS = 60
EXIT_REFUSED = 4

# --- the law's numbers (config may override; these are the canonical defaults)
ENDPOINT_BUDGETS = {
    "profile_reads": 30,       # web_profile_info-class reads (freshness audit)
    "friendship_checks": 20,   # friendships/show (checker — exceptional-only)
    "roster_walk": 0,          # follower-list enumeration: BANNED (2026-08-29)
    "graph_insights": 40,      # official Graph API, own account (safe surface)
}
DAY_SOFT_CALLS = 50            # a normal day stays under this (warn past it)
DAY_HARD_CALLS = 150           # absolute never-cross ceiling (refuse)

# Bulk crawls: many profile reads in one run. 2026-09-01 the builder ran
# TWICE in one day via --override-ledger; IG answered 429 the next morning
# and the 48h cooldown cost two sessions. Amendment (Amir, 2026-09-03):
#   - no override ever re-runs the SAME script on the same day;
#   - no override stacks a second BULK job on a day that already had one;
#   - every override carries a logged reason (--override-reason "...").
BULK_SCRIPTS = frozenset({
    "ig_queue_builder", "ig_audit_queue_freshness", "ig_reenrich_contacts",
    "ig_backfill_reciprocity", "ig_reconcile_followings", "ig_follower_audit",
})


def _law():
    """Budgets from config when present (single source), else defaults."""
    try:
        from scene_intelligence import ig_engagement_config as cfg
    except ImportError:
        try:
            import ig_engagement_config as cfg
        except ImportError:
            cfg = None
    budgets = dict(ENDPOINT_BUDGETS)
    budgets.update(getattr(cfg, "IG_ENDPOINT_BUDGETS", {}) if cfg else {})
    soft = getattr(cfg, "IG_DAY_SOFT_CALLS", DAY_SOFT_CALLS) if cfg else DAY_SOFT_CALLS
    hard = getattr(cfg, "IG_DAY_HARD_CALLS", DAY_HARD_CALLS) if cfg else DAY_HARD_CALLS
    return budgets, int(soft), int(hard)


class LedgerRefused(SystemExit):
    """Raised (exit 4) when the law refuses this run. Prints on raise."""

    def __init__(self, message: str):
        self.message = message
        print(message)
        super().__init__(EXIT_REFUSED)


def _load(path: Path) -> dict:
    if not path.exists():
        return {"runs": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        # Fail CLOSED: an unreadable ledger cannot prove no script ran today.
        raise LedgerRefused(
            f"[DAILY LEDGER] {path.name} exists but is unreadable — refusing "
            f"to run (fail closed). Inspect or delete the file, then retry."
        )
    if not isinstance(data, dict) or not isinstance(data.get("runs"), list):
        raise LedgerRefused(
            f"[DAILY LEDGER] {path.name} has an unexpected shape — refusing "
            f"to run (fail closed). Inspect or delete the file, then retry."
        )
    return data


def runs_on(day: str, path: Path = LEDGER_PATH) -> list[dict]:
    """Ledger entries for an ISO date. Read-only helper for audits/reports."""
    return [r for r in _load(path).get("runs", []) if r.get("date") == day]


def day_call_totals(day: str, path: Path = LEDGER_PATH):
    """(total_est_calls, {endpoint: est_calls}) for the day's api entries."""
    total = 0
    per: dict[str, int] = {}
    for r in runs_on(day, path):
        if r.get("kind", "api") != "api":
            continue
        calls = int(r.get("est_calls") or 0)
        total += calls
        ep = r.get("endpoint")
        if ep:
            per[ep] = per.get(ep, 0) + calls
    return total, per


def _atomic_write(path: Path, data: dict) -> None:
    try:
        from scene_intelligence.json_io import atomic_write_json
    except ImportError:
        from json_io import atomic_write_json  # script-dir invocation
    atomic_write_json(path, data)


def check_and_claim(script: str, *, override: bool = False,
                    reason: str | None = None,
                    path: Path = LEDGER_PATH,
                    today: str | None = None,
                    kind: str = "api",
                    est_calls: int | None = None,
                    endpoint: str | None = None,
                    now: datetime | None = None) -> None:
    """Claim today's slot for `script`, or refuse (exit 4) per the law.

    Call BEFORE the first IG API request. `override` (--override-ledger) is
    the one deliberate escape hatch: it bypasses the one-API-job rule and the
    daytime rule — never the roster ban, the 150 hard ceiling, a same-script
    rerun, or a second bulk crawl on a bulk day (2026-09-03 amendment). An
    override that actually bypasses something must carry a `reason`.
    """
    if kind not in ("api", "browser", "provider"):
        raise ValueError(f"unknown ledger kind: {kind!r}")
    day = today or date.today().isoformat()
    budgets, soft, hard = _law()

    if kind == "provider":
        # 2026-09-14: third-party reads. No IG timing law (it protected the
        # account; these never touch it). Own daily cap = money guard. Same
        # script still only once a day (no accidental double runs).
        return _claim_provider(script, path=path, day=day, est_calls=est_calls,
                               endpoint=endpoint or "provider")

    if kind == "api":
        # Daytime law at the chokepoint (guards module owns the hours).
        try:
            from scene_intelligence.ig_ops_guards import require_daytime
        except ImportError:
            from ig_ops_guards import require_daytime
        require_daytime(now, override=override)

        if endpoint is not None and endpoint in budgets:
            cap = budgets[endpoint]
            if cap <= 0:
                raise LedgerRefused(
                    f"[DAILY LEDGER] endpoint '{endpoint}' is BANNED "
                    f"(budget 0 — the 2026-08-29 roster-walk token kill). "
                    f"Use the IG data export instead. No override exists."
                )

    lock_path = path.with_suffix(".lock")
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            data = _load(path)
            prior_api = [r for r in data["runs"]
                         if r.get("date") == day and r.get("kind", "api") == "api"]

            if kind == "api":
                if prior_api and not override:
                    ran = ", ".join(
                        f"{r.get('script', '?')} at {r.get('ts', '?')}"
                        for r in prior_api)
                    raise LedgerRefused(
                        f"[DAILY LEDGER] An IG API job already ran today: {ran}.\n"
                        f"LAW: one API job per day (2.0 law, 2026-08-30).\n"
                        f"If this second run is deliberate and planned as one "
                        f"budget, re-run with --override-ledger "
                        f"--override-reason \"...\" (not for the same script, "
                        f"not for a second bulk crawl)."
                    )
                if prior_api and override:
                    same = [r for r in prior_api if r.get("script") == script]
                    if same:
                        raise LedgerRefused(
                            f"[DAILY LEDGER] {script} already ran today at "
                            f"{same[0].get('ts', '?')}. No override re-runs the "
                            f"same script on the same day (2026-09-03 "
                            f"amendment: the 09-01 double builder run -> 429 "
                            f"-> 48h lost). Tomorrow."
                        )
                    prior_bulk = [r for r in prior_api
                                  if r.get("script") in BULK_SCRIPTS]
                    if script in BULK_SCRIPTS and prior_bulk:
                        raise LedgerRefused(
                            f"[DAILY LEDGER] bulk job {script} refused: "
                            f"{prior_bulk[0].get('script')} already crawled "
                            f"today. One bulk crawl per day, no override "
                            f"(2026-09-03 amendment)."
                        )
                    if not (reason and reason.strip()):
                        raise LedgerRefused(
                            f"[DAILY LEDGER] --override-ledger needs "
                            f"--override-reason \"...\" (who said go, and "
                            f"why). Overrides are logged, never silent."
                        )
                claim = int(est_calls or 0)
                total, per = day_call_totals(day, path)
                if total + claim > hard:
                    raise LedgerRefused(
                        f"[DAILY LEDGER] {total} est. calls already today; "
                        f"+{claim} would cross the {hard} absolute ceiling. "
                        f"Refused — no override crosses the ceiling."
                    )
                if endpoint is not None and endpoint in budgets:
                    used = per.get(endpoint, 0)
                    if used + claim > budgets[endpoint]:
                        raise LedgerRefused(
                            f"[DAILY LEDGER] endpoint '{endpoint}' budget "
                            f"{budgets[endpoint]}/day; {used} used, +{claim} "
                            f"refused. Split across days or shrink the run."
                        )
                if total + claim > soft:
                    print(f"[DAILY LEDGER] note: {total + claim} est. calls "
                          f"today exceeds the ~{soft} normal-day target "
                          f"(hard ceiling {hard}).")

            cutoff = (date.fromisoformat(day)
                      - timedelta(days=KEEP_DAYS)).isoformat()
            kept = [r for r in data["runs"] if str(r.get("date", "")) >= cutoff]
            entry = {
                "date": day,
                "script": script,
                "ts": datetime.now().isoformat(timespec="seconds"),
                "override": bool(override and (prior_api if kind == "api" else False)),
                "kind": kind,
            }
            if entry["override"]:
                entry["override_reason"] = reason.strip()
            if est_calls is not None:
                entry["est_calls"] = int(est_calls)
            if endpoint is not None:
                entry["endpoint"] = endpoint
            kept.append(entry)
            _atomic_write(path, {"runs": kept})
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def release_claim(script: str, day: str, path: Path = LEDGER_PATH) -> int:
    """Drop today's entries for `script`. Returns how many were removed.

    2026-09-26: a browser session that halts at the confirm gate with zero
    clicks had already claimed ig_session; the claim then read as "ran
    today" and blocked the real session. The loop-closer releases it on a
    zero-click halt. Browser kind only -- API claims are never released
    (a refused/throttled API call still touched Instagram)."""
    lock_path = path.with_suffix(".lock")
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            data = _load(path)
            keep, dropped = [], 0
            for r in data["runs"]:
                if (r.get("date") == day and r.get("script") == script
                        and r.get("kind") == "browser"):
                    dropped += 1
                    continue
                keep.append(r)
            if dropped:
                _atomic_write(path, {"runs": keep})
            return dropped
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def provider_cap() -> int:
    try:
        from scene_intelligence import ig_engagement_config as cfg
    except ImportError:
        try:
            import ig_engagement_config as cfg
        except ImportError:
            return 300
    return int((getattr(cfg, "PROVIDER", {}) or {}).get("daily_call_cap", 300))


def provider_calls_today(day: str, path: Path = LEDGER_PATH) -> int:
    return sum(int(r.get("est_calls") or 0) for r in runs_on(day, path)
               if r.get("kind") == "provider")


def _claim_provider(script: str, *, path: Path, day: str, est_calls, endpoint: str) -> None:
    cap = provider_cap()
    claim = int(est_calls or 0)
    lock_path = path.with_suffix(".lock")
    with open(lock_path, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            data = _load(path)
            same = [r for r in data["runs"] if r.get("date") == day
                    and r.get("kind") == "provider" and r.get("script") == script]
            if same:
                raise LedgerRefused(
                    f"[DAILY LEDGER] {script} already ran today at "
                    f"{same[0].get('ts', '?')} (provider). Once a day per script.")
            used = sum(int(r.get("est_calls") or 0) for r in data["runs"]
                       if r.get("date") == day and r.get("kind") == "provider")
            if used + claim > cap:
                raise LedgerRefused(
                    f"[DAILY LEDGER] provider cap {cap}/day: {used} used, "
                    f"+{claim} refused (cost guard, config PROVIDER.daily_call_cap).")
            cutoff = (date.fromisoformat(day) - timedelta(days=KEEP_DAYS)).isoformat()
            kept = [r for r in data["runs"] if str(r.get("date", "")) >= cutoff]
            kept.append({"date": day, "script": script,
                         "ts": datetime.now().isoformat(timespec="seconds"),
                         "override": False, "kind": "provider",
                         "est_calls": claim, "endpoint": endpoint})
            _atomic_write(path, {"runs": kept})
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def add_ledger_argument(parser) -> None:
    """Attach the uniform --override-ledger / --override-reason flags."""
    parser.add_argument(
        "--override-ledger", action="store_true",
        help="deliberate escape hatch: bypass the one-API-job/day rule and "
             "the daytime rule (never the roster ban, the 150 ceiling, a "
             "same-script rerun, or a second bulk crawl). Needs "
             "--override-reason.")
    parser.add_argument(
        "--override-reason", default=None, metavar="TEXT",
        help="required with --override-ledger: who said go and why "
             "(logged in the ledger entry)")


def override_kwargs(args) -> dict:
    """Uniform kwargs for check_and_claim from a parsed argparse namespace."""
    return {"override": bool(getattr(args, "override_ledger", False)),
            "reason": getattr(args, "override_reason", None)}


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--claim", metavar="NAME",
                   help="claim today's ledger slot as NAME (e.g. ig_session)")
    p.add_argument("--kind", choices=("api", "browser", "provider"), default="browser",
                   help="claim kind; sessions use 'browser' (default)")
    p.add_argument("--est-calls", type=int, default=None)
    p.add_argument("--endpoint", default=None)
    p.add_argument("--show", action="store_true",
                   help="print today's entries + budget totals")
    add_ledger_argument(p)
    args = p.parse_args()

    day = date.today().isoformat()
    if args.claim:
        check_and_claim(args.claim, kind=args.kind, **override_kwargs(args), est_calls=args.est_calls,
                        endpoint=args.endpoint)
        print(f"[DAILY LEDGER] claimed: {args.claim} ({args.kind}) on {day}")
    if args.show or not args.claim:
        entries = runs_on(day)
        total, per = day_call_totals(day)
        budgets, soft, hard = _law()
        print(f"[DAILY LEDGER] {day}: {len(entries)} entries, "
              f"~{total} est. calls (soft {soft} / hard {hard})")
        for r in entries:
            print(f"  - {r.get('script')} [{r.get('kind', 'api')}] "
                  f"at {r.get('ts')} calls={r.get('est_calls', '?')} "
                  f"endpoint={r.get('endpoint', '-')}"
                  f"{' OVERRIDE' if r.get('override') else ''}")
        for ep, used in sorted(per.items()):
            print(f"  budget {ep}: {used}/{budgets.get(ep, '-')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
