"""
scene_intelligence/ig_heartbeat.py
----------------------------------
The watchdog (registry: "silence means broken", 2026-08-31, Amir-approved).

Everything else in the stack assumes silence = success. This is the one
piece that assumes silence = broken. Runs nightly via its own launchd agent
(independent of the dispatcher it watches). Zero API calls, zero ledger.

Checks:
  1. Dispatcher liveness: docs/reports/dispatch-log.md must have an entry
     within MAX_SILENT_HOURS (default 30h -- the dispatcher logs every
     morning, run or skip, so >30h of silence means launchd died, the Mac
     slept through 09:30 repeatedly, or the script is crashing before _log).
  2. Session cadence: on the evening of an action day (Mon/Wed/Fri/Sat),
     autonomy_state.json processed.ig should contain today or the scorecard
     a row -- if the last processed session is > 4 days old, sessions have
     been silently failing (task disabled, permission-stalled, browser gone).
  3. Test suite: runs pytest -q (fast, ~0.5s). A red suite at night is a
     broken tool discovered before the morning dispatcher uses it.

On any failure: macOS notification + a line in dispatch-log.md. On all-green
it logs one heartbeat line (so the watchdog itself is provably alive) and
stays silent toward Amir.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent
REPO = SI_DIR.parent
DISPATCH_LOG = REPO / "docs" / "reports" / "dispatch-log.md"
STATE = SI_DIR / "autonomy_state.json"
MAX_SILENT_HOURS = 30
MAX_SESSION_GAP_DAYS = 4
SESSION_DAYS = {"Monday", "Wednesday", "Friday", "Saturday"}


def _notify(msg: str) -> None:
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{msg}" with title "IG watchdog"'],
            capture_output=True, timeout=10)
    except Exception:
        pass


def _log(line: str) -> None:
    try:
        with open(DISPATCH_LOG, "a", encoding="utf-8") as f:
            f.write(f"- {datetime.now().isoformat(timespec='seconds')} — "
                    f"**watchdog** — {line}\n")
    except Exception:
        pass


def main() -> int:
    now = datetime.now()
    problems: list[str] = []

    # 1. Dispatcher liveness (file mtime is enough -- every run appends).
    try:
        age_h = (now.timestamp() - DISPATCH_LOG.stat().st_mtime) / 3600
        if age_h > MAX_SILENT_HOURS:
            problems.append(f"dispatcher silent {age_h:.0f}h (> {MAX_SILENT_HOURS}h) — "
                            f"launchd agent dead, Mac asleep at 09:30, or crash before logging")
    except OSError:
        problems.append("dispatch-log.md missing entirely")

    # 2. Session cadence.
    try:
        st = json.loads(STATE.read_text(encoding="utf-8"))
        done = sorted(st.get("processed", {}).get("ig", []))
        if done:
            gap = (now.date() - date.fromisoformat(done[-1])).days
            paused = (st.get("pauses") or {}).get("ig")
            if gap > MAX_SESSION_GAP_DAYS and not paused:
                problems.append(f"no IG session processed for {gap}d "
                                f"(last {done[-1]}, no pause set) — sessions are "
                                f"silently failing (task disabled? permission-stalled?)")
    except Exception as exc:
        problems.append(f"autonomy_state unreadable: {exc}")

    # 3. Nightly test suite.
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        tail = (r.stdout or r.stderr).strip().splitlines()[-1:]
        problems.append(f"TEST SUITE RED: {' '.join(tail)}")

    if problems:
        for p in problems:
            _log(f"ALERT — {p}")
        _notify(problems[0][:180] + (" (+more)" if len(problems) > 1 else ""))
        return 1

    _log(f"heartbeat ok (dispatch fresh, sessions on cadence, tests green)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
