#!/usr/bin/env python3
"""Claude Code hook for the Chrome queue (ticket System 67, G-25).

PreToolUse on Chrome tools (mcp__claude-in-chrome__*, mcp__Control_Chrome__*):
  - this session holds Chrome  -> touch, allow (exit 0, no output)
  - nobody holds Chrome        -> claim for this session (title = cwd folder name), allow
  - another session holds it   -> join the line, print a deny decision with the reason
SessionEnd: release this session's lock and drop it from the line.
Any other tool: exit 0 at once.

Fails OPEN: any internal error allows the call and is appended to
<root>/hook-errors.log, so a bug never blocks Amir's own work.
The allow path prints nothing, so the normal permission prompts still apply.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

CHROME_PREFIXES = ("mcp__claude-in-chrome__", "mcp__Control_Chrome__")


def _root(root: Optional[str]) -> Path:
    if root:
        return Path(root).expanduser()
    env = os.environ.get("CHROME_QUEUE_ROOT")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".claude" / "chrome-queue"


def _log_error(root: Path, exc: BaseException) -> None:
    try:
        root.mkdir(parents=True, exist_ok=True)
        with open(str(root / "hook-errors.log"), "a", encoding="utf-8") as fh:
            fh.write("%s %s: %s\n%s\n" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), type(exc).__name__, exc,
                "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).rstrip()))
    except Exception:
        pass


def _profile_from_input(tool_name: str, tool_input) -> str:
    """select_browser / switch_browser name the profile; record it when we see it."""
    if not isinstance(tool_input, dict):
        return ""
    if tool_name.endswith("select_browser") or tool_name.endswith("switch_browser"):
        for key in ("deviceId", "device_id", "browser", "name"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def _deny(reason: str) -> str:
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }})


def handle(payload: dict, root: Path, now: Optional[float] = None) -> Optional[str]:
    """Return the stdout text (None = allow silently)."""
    event = payload.get("hook_event_name") or ""
    tool_name = str(payload.get("tool_name") or "")
    if event != "SessionEnd" and not tool_name.startswith(CHROME_PREFIXES):
        return None  # not a Chrome tool: out at once
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import chrome_queue as cq

    now = time.time() if now is None else now
    session = str(payload.get("session_id") or "")

    if event == "SessionEnd":
        if session:
            with cq.locked_state(root, now) as st:
                cq.end_session(st, session, now=now)
        return None

    if not session:
        return None  # nothing to queue on; fail open

    cwd = str(payload.get("cwd") or "")
    title = os.path.basename(cwd.rstrip("/")) or session[:8]
    profile = _profile_from_input(tool_name, payload.get("tool_input"))
    prio = cq.is_priority(title, cwd)

    with cq.locked_state(root, now) as st:
        h = st.holder
        if h and h["session"] == session:
            h["last_touch"] = now
            if profile:
                h["profile"] = profile
            return None
        if h is None:
            cq.do_claim(st, session, title, profile or "not named yet (auto-claim)", now=now, priority=prio)
            return None
        place = cq.do_wait(st, session, title, now=now, priority=prio, profile=profile)
        if place == 0:
            return None
        reason = ("Chrome is held by %s since %s (profile %s). You are number %d in line. "
                  "Wait, or ask Amir to say 'Chrome is free'." % (
                      h.get("title") or h["session"], cq.hhmm(h.get("since")),
                      h.get("profile") or "?", place))
        return _deny(reason)


def main(stdin_text: Optional[str] = None, root: Optional[str] = None,
         now: Optional[float] = None, out=None) -> int:
    out = out or sys.stdout
    r = _root(root)
    try:
        text = sys.stdin.read() if stdin_text is None else stdin_text
        payload = json.loads(text) if text.strip() else {}
        if not isinstance(payload, dict):
            raise ValueError("hook input is not a JSON object")
        result = handle(payload, r, now)
        if result:
            out.write(result + "\n")
    except Exception as exc:  # fail open
        _log_error(r, exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
