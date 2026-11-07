#!/usr/bin/env python3
"""Chrome queue: one chat in Chrome at a time (ticket System 67, G-25).

A chat claims Chrome before any Chrome work and names the profile. Other chats
wait in line. Amir frees Chrome with "Chrome is free" = `release --force`.
Inch of Shadow chats go ahead of other chats in the line (not ahead of the holder).

State lives in ~/.claude/chrome-queue/ (or --root):
  lock.json   the holder: session, title, profile, note, since, last_touch, priority
  queue.json  the line: list of {session, title, joined, priority}
Every change runs under an fcntl lock on .mutex and writes tmp + os.replace.

Stale rule: a holder with no touch for 20 minutes is released on the next command,
and the head of the line is promoted. Every release (normal, force, stale,
session end) promotes the head of the line.

Commands:
  claim   --session ID --title TEXT --profile DEVICEID_OR_NAME [--note TEXT]
  release --session ID | --force
  status
  wait    --session ID --title TEXT
  touch   --session ID

Python 3.9, stdlib only.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

DEFAULT_ROOT = Path.home() / ".claude" / "chrome-queue"
STALE_SECONDS = 20 * 60
PRIORITY_MARKERS = ("inch of shadow", "inchofshadow")


class QueueError(Exception):
    """A command that cannot be done (shown to the user, exit 1)."""


def resolve_root(root: Optional[str] = None) -> Path:
    if root:
        return Path(root).expanduser()
    env = os.environ.get("CHROME_QUEUE_ROOT")
    if env:
        return Path(env).expanduser()
    return DEFAULT_ROOT


def is_priority(*texts: Optional[str]) -> bool:
    """Inch of Shadow work has priority for now: matched on title or cwd."""
    for text in texts:
        low = (text or "").lower()
        if any(m in low for m in PRIORITY_MARKERS):
            return True
    return False


def hhmm(ts: Optional[float]) -> str:
    if not ts:
        return "--:--"
    return time.strftime("%H:%M", time.localtime(ts))


# ---------- storage ----------

def _read_json(path: Path, default):
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return default
    return json.loads(text)


def _write_json(path: Path, data) -> None:
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, str(path))
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


class State:
    """Lock + queue, loaded under the mutex. save() writes both atomically."""

    def __init__(self, root: Path):
        self.root = root
        self.lock_path = root / "lock.json"
        self.queue_path = root / "queue.json"
        lock = _read_json(self.lock_path, {})
        queue = _read_json(self.queue_path, [])
        if not isinstance(lock, dict):
            raise ValueError("lock.json is not an object")
        if not isinstance(queue, list) or not all(isinstance(e, dict) for e in queue):
            raise ValueError("queue.json is not a list of objects")
        self.holder: Optional[dict] = lock if lock.get("session") else None
        self.queue: List[dict] = queue
        self.events: List[str] = []

    def save(self) -> None:
        _write_json(self.lock_path, self.holder or {})
        _write_json(self.queue_path, self.queue)


@contextlib.contextmanager
def locked_state(root: Path, now: Optional[float] = None) -> Iterator[State]:
    """Open state under the fcntl mutex, apply the stale rule, save on exit."""
    root.mkdir(parents=True, exist_ok=True)
    now = time.time() if now is None else now
    with open(str(root / ".mutex"), "a") as mutex:
        fcntl.flock(mutex.fileno(), fcntl.LOCK_EX)
        try:
            state = State(root)
            normalize(state, now)
            yield state
            state.save()
        finally:
            fcntl.flock(mutex.fileno(), fcntl.LOCK_UN)


# ---------- core rules ----------

def _sort_queue(state: State) -> None:
    state.queue.sort(key=lambda e: (0 if e.get("priority") else 1, e.get("joined", 0)))


def position(state: State, session: str) -> Optional[int]:
    for i, entry in enumerate(state.queue, start=1):
        if entry.get("session") == session:
            return i
    return None


def _promote(state: State, now: float) -> None:
    if state.holder or not state.queue:
        return
    nxt = state.queue.pop(0)
    state.holder = {
        "session": nxt["session"],
        "title": nxt.get("title", ""),
        "profile": nxt.get("profile") or "not named yet",
        "note": nxt.get("note", ""),
        "since": now,
        "last_touch": now,
        "priority": bool(nxt.get("priority")),
        "promoted": True,
    }
    state.events.append("promoted %s from the line" % (nxt.get("title") or nxt["session"]))


def normalize(state: State, now: float) -> None:
    """Stale holder out, head of the line in."""
    h = state.holder
    if h and now - float(h.get("last_touch") or h.get("since") or 0) >= STALE_SECONDS:
        state.events.append(
            "released stale holder %s (no call since %s)" % (h.get("title") or h["session"], hhmm(h.get("last_touch")))
        )
        state.holder = None
    # a holder never waits in its own line
    if state.holder:
        state.queue = [e for e in state.queue if e.get("session") != state.holder["session"]]
    _promote(state, now)


def _release(state: State, now: float) -> None:
    state.holder = None
    _promote(state, now)


def do_claim(state: State, session: str, title: str, profile: str, note: str = "",
             now: Optional[float] = None, priority: Optional[bool] = None) -> Tuple[bool, Optional[int]]:
    """Return (holds, place_in_line). Holds = True when this session now holds Chrome."""
    now = time.time() if now is None else now
    prio = is_priority(title) if priority is None else priority
    h = state.holder
    if h and h["session"] == session:
        h.update({"title": title or h.get("title", ""), "profile": profile or h.get("profile", ""),
                  "last_touch": now})
        if note:
            h["note"] = note
        return True, None
    if h is None:
        state.queue = [e for e in state.queue if e.get("session") != session]
        state.holder = {"session": session, "title": title, "profile": profile, "note": note,
                        "since": now, "last_touch": now, "priority": prio}
        return True, None
    return False, do_wait(state, session, title, now=now, priority=prio, profile=profile, note=note)


def do_wait(state: State, session: str, title: str, now: Optional[float] = None,
            priority: Optional[bool] = None, profile: str = "", note: str = "") -> int:
    """Join the line (or stay in it). Returns the place in line, 0 = holds Chrome."""
    now = time.time() if now is None else now
    if state.holder and state.holder["session"] == session:
        return 0
    prio = is_priority(title) if priority is None else priority
    for entry in state.queue:
        if entry.get("session") == session:
            entry["last_seen"] = now
            if profile:
                entry["profile"] = profile
            if note:
                entry["note"] = note
            return position(state, session) or 0
    state.queue.append({"session": session, "title": title, "joined": now, "last_seen": now,
                        "priority": prio, "profile": profile, "note": note})
    _sort_queue(state)
    if state.holder is None:
        _promote(state, now)
        if state.holder and state.holder["session"] == session:
            return 0
    return position(state, session) or 0


def do_touch(state: State, session: str, now: Optional[float] = None) -> None:
    now = time.time() if now is None else now
    if not state.holder or state.holder["session"] != session:
        raise QueueError("session %s does not hold Chrome" % session)
    state.holder["last_touch"] = now


def do_release(state: State, session: Optional[str] = None, force: bool = False,
               now: Optional[float] = None) -> str:
    now = time.time() if now is None else now
    if force:
        was = state.holder
        _release(state, now)
        if was:
            return "Chrome is free: released %s." % (was.get("title") or was["session"])
        return "Chrome was already free."
    if not session:
        raise QueueError("release needs --session or --force")
    if state.holder and state.holder["session"] == session:
        _release(state, now)
        return "released."
    before = len(state.queue)
    state.queue = [e for e in state.queue if e.get("session") != session]
    if len(state.queue) < before:
        return "left the line."
    return "nothing to release for this session."


def end_session(state: State, session: str, now: Optional[float] = None) -> None:
    """SessionEnd: release if holding, leave the line if waiting."""
    now = time.time() if now is None else now
    state.queue = [e for e in state.queue if e.get("session") != session]
    if state.holder and state.holder["session"] == session:
        _release(state, now)


def format_status(state: State, now: Optional[float] = None) -> str:
    now = time.time() if now is None else now
    lines = []
    h = state.holder
    if h:
        ago = int((now - float(h.get("last_touch") or h.get("since") or now)) // 60)
        lines.append("Holder: %s (session %s)" % (h.get("title") or "?", h["session"]))
        lines.append("  profile: %s" % (h.get("profile") or "?"))
        lines.append("  since: %s" % hhmm(h.get("since")))
        lines.append("  last call: %s (%d min ago, stale at 20)" % (hhmm(h.get("last_touch")), ago))
        if h.get("note"):
            lines.append("  note: %s" % h["note"])
    else:
        lines.append("Holder: none, Chrome is free")
    if state.queue:
        lines.append("Queue:")
        for i, e in enumerate(state.queue, start=1):
            lines.append("  %d. %s (session %s) joined %s%s" % (
                i, e.get("title") or "?", e.get("session"), hhmm(e.get("joined")),
                " [priority]" if e.get("priority") else ""))
    else:
        lines.append("Queue: empty")
    return "\n".join(lines)


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chrome_queue.py", description="One chat in Chrome at a time.")
    p.add_argument("--root", help="state folder (default ~/.claude/chrome-queue)")
    p.add_argument("--now", type=float, help=argparse.SUPPRESS)  # tests only
    sub = p.add_subparsers(dest="cmd")
    sub.required = True

    c = sub.add_parser("claim", help="claim Chrome before any Chrome work")
    c.add_argument("--session", required=True)
    c.add_argument("--title", required=True)
    c.add_argument("--profile", required=True, help="deviceId or profile name")
    c.add_argument("--note", default="")
    c.add_argument("--priority", action="store_true", help="force priority in the line")

    r = sub.add_parser("release", help="release Chrome (--force = 'Chrome is free')")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--session")
    g.add_argument("--force", action="store_true")

    sub.add_parser("status", help="holder, since, last call, the line")

    w = sub.add_parser("wait", help="join the line, print the place")
    w.add_argument("--session", required=True)
    w.add_argument("--title", required=True)
    w.add_argument("--priority", action="store_true")

    t = sub.add_parser("touch", help="holder heartbeat")
    t.add_argument("--session", required=True)
    return p


def main(argv: Optional[List[str]] = None, out=None) -> int:
    out = out or sys.stdout
    args = build_parser().parse_args(argv)
    root = resolve_root(args.root)
    now = args.now if args.now is not None else time.time()
    code = 0
    try:
        with locked_state(root, now) as st:
            if args.cmd == "claim":
                holds, place = do_claim(st, args.session, args.title, args.profile, args.note, now=now,
                                        priority=True if args.priority else None)
                if holds:
                    msg = "You hold Chrome (profile %s)." % st.holder.get("profile")
                else:
                    h = st.holder
                    msg = "Chrome is held by %s since %s (profile %s). You are number %d in line." % (
                        h.get("title"), hhmm(h.get("since")), h.get("profile"), place)
                    code = 2
            elif args.cmd == "release":
                msg = do_release(st, args.session, args.force, now=now)
            elif args.cmd == "status":
                msg = format_status(st, now)
            elif args.cmd == "wait":
                place = do_wait(st, args.session, args.title, now=now,
                                priority=True if args.priority else None)
                msg = "You hold Chrome." if place == 0 else "You are number %d in line." % place
            elif args.cmd == "touch":
                do_touch(st, args.session, now=now)
                msg = "touched."
            events = list(st.events)
    except QueueError as exc:
        print("error: %s" % exc, file=out)
        return 1
    for ev in events:
        print("(%s)" % ev, file=out)
    print(msg, file=out)
    return code


if __name__ == "__main__":
    sys.exit(main())
