"""Gap Radar weekly schedule (GR-05, 2026-11-05).

  python3 gap_radar/schedule.py --dry-run     # the plan for today, with cost estimates; no calls
  python3 gap_radar/schedule.py               # run it (launchd calls this once a week)
  python3 gap_radar/schedule.py --monthly     # also run the monthly list + crowding checks now

gap_radar/schedule.json holds the lists and the two caps Amir sets:
  radar_cap_usd_month    the most the radar may spend on Claude in one calendar month
  ios_reserve_usd_month  Claude credit kept free for Inch of Shadow work: the radar stops
                         when the month's TOTAL spend + the next run would cut into it
While either cap is null nothing runs (exit 0 with a note). Inch of Shadow first: HikerAPI is
already limited to the leftover of the 300/day cap inside gap_radar.collect().

Weekly list every run. The monthly list and the crowding checks (~90% of the cost: about
$6-7 per product profile) only on the first run of a month (day 1-7) or with --monthly.
A profile is skipped, never cut short, when its estimate would cross a cap.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEDULE = HERE / "schedule.json"
STATE = HERE / "schedule_state.json"     # {"last_run": "YYYY-MM-DD"}: written after each profile that ran
LOCK = HERE / "schedule.lock"             # one run at a time (gate review 2026-11-07: 11-06 runs overlapped)
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def load_schedule(path: Path = SCHEDULE) -> dict:
    s = json.loads(path.read_text())
    for k in ("weekly", "monthly", "estimate_usd"):
        if k not in s:
            raise SystemExit(f"schedule.json: missing {k}")
    return s


def radar_spend(ledger: dict, ym: str) -> float:
    """This month's Claude spend by the radar: every ledger tool name that starts with gap_radar."""
    by = ((ledger.get("months") or {}).get(ym) or {}).get("by") or {}
    return round(sum(float(v.get("usd") or 0) for k, v in by.items() if k.startswith("gap_radar")), 4)


def total_spend(ledger: dict, ym: str) -> float:
    return round(float(((ledger.get("months") or {}).get(ym) or {}).get("usd") or 0), 4)


def too_soon(state: dict, today: date, min_days: int) -> str:
    """Empty string = OK; else why the scheduled run waits (a manual run happened a few days ago)."""
    last = (state or {}).get("last_run")
    if not last or not min_days:
        return ""
    gap = (today - date.fromisoformat(last)).days
    return f"last run {last}, {gap} day(s) ago (< {min_days})" if 0 <= gap < min_days else ""


def is_monthly_run(today: date, force: bool = False) -> bool:
    return force or today.day <= 7


def estimate(p: dict, est: dict, crowding_now: bool) -> float:
    return float(est["analysis"]) + (float(est["crowding"]) if (p["crowding"] and crowding_now) else 0.0)


def gate(s: dict, radar: float, total: float, limit: float, cost: float) -> str:
    """Empty string = OK to run; else the reason it may not."""
    cap, reserve = s.get("radar_cap_usd_month"), s.get("ios_reserve_usd_month")
    if cap is None or reserve is None:
        return "caps not set in schedule.json (Amir decides radar_cap_usd_month + ios_reserve_usd_month)"
    if radar + cost > float(cap):
        return f"radar cap: ${radar:.2f} spent + ~${cost:.2f} > ${float(cap):.2f}"
    if total + cost > limit - float(reserve):
        return (f"Inch of Shadow reserve: month total ${total:.2f} + ~${cost:.2f} > "
                f"${limit:.2f} limit - ${float(reserve):.2f} reserve")
    return ""


def plan(s: dict, today: date, force_monthly: bool = False) -> tuple[list, bool]:
    monthly = is_monthly_run(today, force_monthly)
    names = list(s["weekly"]) + (list(s.get("monthly") or []) if monthly else [])
    return names, monthly and s.get("crowding", "monthly") != "never"


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gap Radar weekly schedule")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--monthly", action="store_true")
    ap.add_argument("--force", action="store_true", help="run even if the last run was only days ago")
    a = ap.parse_args(argv)

    import gap_radar as gr
    root = gr.main_root()
    import claude_api
    claude_api.LEDGER = root / "stats_snapshots" / "claude_spend.json"
    s = load_schedule()
    today = date.today()
    ym = today.strftime("%Y-%m")
    names, crowding_now = plan(s, today, a.monthly)
    print(f"Gap Radar schedule {today} ({'monthly' if crowding_now else 'weekly'} run, "
          f"schedule status: {s.get('status', '?')})")

    try:
        state = json.loads(STATE.read_text())
    except (OSError, ValueError):
        state = {}
    wait = "" if a.force else too_soon(state, today, int(s.get("min_days_between_runs") or 0))
    if wait:
        print(f"Waiting: {wait}. Use --force to run anyway.")
        return 0
    lock = None
    if not a.dry_run:
        lock = open(LOCK, "w")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)   # released when the process ends, even on a crash
        except OSError:
            print("Another Gap Radar run is going. Not starting a second one.")
            return 0

    def ledger() -> dict:
        try:
            return json.loads(claude_api.LEDGER.read_text())
        except (OSError, ValueError):
            return {"months": {}}

    if not a.dry_run:
        from dotenv import load_dotenv
        load_dotenv(root / ".env")
    ran = 0
    for name in names:
        if name.endswith(".json") and not Path(name).expanduser().is_file():
            print(f"  skip {name}: file not found (Life lane not merged yet?)")
            continue
        p = gr.load_profile(name)
        cost = estimate(p, s["estimate_usd"], crowding_now)
        led = ledger()
        why = gate(s, radar_spend(led, ym), total_spend(led, ym), claude_api.LIMIT_USD, cost)
        if a.dry_run:
            print(f"  {'blocked' if why else 'would run'} {p['name']}: ~${cost:.2f}"
                  f"{' incl. crowding' if p['crowding'] and crowding_now else ''}{' (' + why + ')' if why else ''}")
            continue
        if why:
            print(f"  skip {p['name']}: {why}")
            if "caps not set" in why:
                return 0
            continue
        try:
            raw = gr.collect(p)
            md = gr.analyze(raw, profile=p)
            if p["crowding"] and crowding_now:
                gr.check_report(p, md.with_suffix(".json"))
            ran += 1
            STATE.write_text(json.dumps({"last_run": today.isoformat()}) + "\n")   # paid work is recorded at once
        except SystemExit as e:              # one bad profile never stops the rest
            print(f"  {p['name']} stopped: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  {p['name']} failed: {type(e).__name__}: {str(e)[:200]}")
    led = ledger()
    print(f"Done: {ran} profiles. Radar this month ${radar_spend(led, ym):.2f}, "
          f"all Claude ${total_spend(led, ym):.2f} of ${claude_api.LIMIT_USD:.0f}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
