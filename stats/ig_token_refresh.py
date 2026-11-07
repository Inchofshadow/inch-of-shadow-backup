"""Keep META_IG_ACCESS_TOKEN alive (ticket M-09, Amir 2026-11-03 "Yes, build it").

Instagram-login long-lived tokens last 60 days and can only be refreshed while
still valid. The old token silently expired on 2026-10-15. This runs daily
from launchd; it does NOTHING (no network call) until the token is
REFRESH_AFTER_DAYS old, then makes one ledger-claimed refresh call and writes
the new token into .env in place (only that one line changes).

If the ledger refuses (09:00-21:00 rule, or another API job already ran today)
it just tries again tomorrow: 50 days leaves 10 days of slack. When fewer than
WARN_DAYS remain and it still has not worked, a macOS notification tells Amir.

State: stats/ig_token_state.json {"issued": "YYYY-MM-DD", "expires": "YYYY-MM-DD"}.
The token itself is never printed or logged.

Usage:
  python3 stats/ig_token_refresh.py            # daily check (launchd)
  python3 stats/ig_token_refresh.py --status   # show age, no network
  python3 stats/ig_token_refresh.py --force    # refresh now (one call), e.g. to test
  python3 stats/ig_token_refresh.py --mark-issued 2026-11-03   # after a manual renew
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
STATE_PATH = ROOT / "stats" / "ig_token_state.json"
KEY = "META_IG_ACCESS_TOKEN"
REFRESH_URL = "https://graph.instagram.com/refresh_access_token"
REFRESH_AFTER_DAYS = 50
LIFETIME_DAYS = 60
WARN_DAYS = 7


def read_token(env_path: Path | None = None) -> str:
    env_path = env_path or ENV_PATH
    for line in env_path.read_text().splitlines():
        if line.startswith(KEY + "="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def write_token(new: str, env_path: Path | None = None) -> None:
    """Replace only the KEY line, atomically, keeping the file's permissions."""
    env_path = env_path or ENV_PATH
    if not new or any(c in new for c in "\r\n \t\"'"):
        raise ValueError("refusing to write an empty/invalid token")
    lines = env_path.read_text().splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.startswith(KEY + "=")]
    if len(hits) != 1:
        raise ValueError(f"expected exactly one {KEY}= line in .env, found {len(hits)}")
    i = hits[0]
    end = "\n" if lines[i].endswith("\n") else ""
    lines[i] = f"{KEY}={new}{end}"
    mode = env_path.stat().st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=str(env_path.parent), prefix=".env.tmp.")
    try:
        with os.fdopen(fd, "w") as f:
            f.writelines(lines)
        os.chmod(tmp, mode)
        os.replace(tmp, env_path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_state(path: Path | None = None) -> dict:
    path = path or STATE_PATH
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return {}


def save_state(state: dict, path: Path | None = None) -> None:
    path = path or STATE_PATH
    path.write_text(json.dumps(state, indent=2) + "\n")


def mark_issued(day: date, path: Path | None = None, expires_in: int | None = None) -> dict:
    exp = day + timedelta(seconds=expires_in) if expires_in else day + timedelta(days=LIFETIME_DAYS)
    state = {"issued": day.isoformat(), "expires": exp.isoformat()}
    save_state(state, path)
    return state


def plan(state: dict, today: date) -> tuple[str, int, int]:
    """-> (action, age_days, days_left). action: 'wait' | 'refresh' | 'unknown'."""
    if not state.get("issued"):
        return "unknown", -1, -1
    issued = date.fromisoformat(state["issued"])
    expires = date.fromisoformat(state.get("expires") or (issued + timedelta(days=LIFETIME_DAYS)).isoformat())
    age, left = (today - issued).days, (expires - today).days
    return ("refresh" if age >= REFRESH_AFTER_DAYS else "wait"), age, left


def notify(msg: str) -> None:
    try:
        subprocess.run(["osascript", "-e",
                        f'display notification {json.dumps(msg)} with title "Inch of Shadow: IG token"'],
                       check=False, timeout=10)
    except Exception:
        pass


def call_refresh(token: str) -> dict:
    url = REFRESH_URL + "?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300].replace(token, "<token>")
        raise RuntimeError(f"HTTP {e.code}: {body}") from None


def claim() -> None:
    sys.path.insert(0, str(ROOT / "scene_intelligence"))
    from ig_daily_ledger import check_and_claim
    check_and_claim(script="ig_token_refresh", kind="api", est_calls=1, endpoint="graph_insights",
                    reason="M-09 scheduled long-lived token refresh")


def run(today: date | None = None, force: bool = False) -> int:
    today = today or date.today()
    state = load_state()
    action, age, left = plan(state, today)
    if action == "unknown":
        print(f"[ig_token_refresh] no state file; run --mark-issued YYYY-MM-DD once")
        return 1
    if action == "wait" and not force:
        print(f"[ig_token_refresh] {today}: token {age} days old, {left} left, refresh at day {REFRESH_AFTER_DAYS}. No call.")
        return 0
    token = read_token()
    if not token:
        print("[ig_token_refresh] no token in .env")
        notify("No Instagram token in .env. Generate a new one in the Meta dashboard.")
        return 1
    try:
        claim()
    except SystemExit as e:  # OpsGate / LedgerRefused: try again tomorrow
        print(f"[ig_token_refresh] {today}: ledger said not now ({e}); retry tomorrow, {left} days left")
        if left <= WARN_DAYS:
            notify(f"Token refresh keeps waiting, {left} days left.")
        return 0
    try:
        data = call_refresh(token)
        new = data.get("access_token", "")
        write_token(new)
    except Exception as e:
        print(f"[ig_token_refresh] {today}: refresh FAILED: {e}")
        if left <= WARN_DAYS or "190" in str(e):
            notify(f"Token refresh failed, {left} days left. Renew it in the Meta dashboard.")
        return 2
    st = mark_issued(today, expires_in=data.get("expires_in"))
    print(f"[ig_token_refresh] {today}: refreshed OK, new token valid until {st['expires']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--mark-issued", metavar="YYYY-MM-DD")
    ap.add_argument("--force", action="store_true",
                    help="refresh now even before day 50 (still ledger-claimed; Meta needs the token >= 24h old)")
    a = ap.parse_args()
    if a.mark_issued:
        st = mark_issued(date.fromisoformat(a.mark_issued))
        print(f"[ig_token_refresh] marked issued {st['issued']}, expires {st['expires']}")
        return 0
    if a.status:
        action, age, left = plan(load_state(), date.today())
        print(f"[ig_token_refresh] {action}: age {age} days, {left} days left")
        return 0
    return run(force=a.force)


if __name__ == "__main__":
    raise SystemExit(main())
