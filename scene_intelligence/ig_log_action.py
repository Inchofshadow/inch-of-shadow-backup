"""Single entry point for writing IG session JSONL lines (added 2026-09-18).

Why: the session used to append each line with a raw shell one-liner
(`cd ... && TS=$(python3 -c ...) && echo "{...}" >> ...jsonl`). Every call
was a DIFFERENT command string (handle, action and sequence change each
time), and Claude Code approvals are exact-match, so every single log line
raised a fresh permission prompt. On 2026-09-18 the scheduled session sat
frozen on four of those prompts for ~7 hours and landed 1 follow.

SoundCloud never had this problem because it logs through one script with a
stable prefix (`sc_engagement.py --log-action ...`), covered by one
wildcard allow rule. This is the IG twin of that, so one rule

    Bash(python3 scene_intelligence/ig_log_action.py *)

covers every click the session will ever log.

Bonus safety: the timestamp is read from the real Berlin clock INSIDE this
script, so a session can no longer synthesize or project one (STRICT rule
4), and `sequence` auto-increments from the file so it can never drift.

Usage (mirrors sc_engagement.py --log-action):
  python3 scene_intelligence/ig_log_action.py --action-type ig_like \
      --handle bovaflux --track reach --pre-warm \
      --post-url https://www.instagram.com/p/XXXX/

  python3 scene_intelligence/ig_log_action.py --action-type ig_follow \
      --handle bovaflux --track reach --source "galaxianmusic,orson_records"

  python3 scene_intelligence/ig_log_action.py --action-type ig_skip \
      --handle nervecollect --track scene --reason all_recent_sponsored \
      --tier T2 --category label

  python3 scene_intelligence/ig_log_action.py --action-type ig_vet \
      --handle korboira --followers 972 --following 1698 --posts 53 \
      --public --last-post-days 41 --bio "Producer & Mastering Engineer"

  python3 scene_intelligence/ig_log_action.py --action-type session_halt \
      --reason "safety: 22:00 cutoff passed"
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SI_DIR = Path(__file__).parent
BERLIN = ZoneInfo("Europe/Berlin")

CLICK_ACTIONS = {
    "ig_like", "ig_follow", "ig_unfollow", "ig_skip", "ig_like_skipped",
    "ig_unfollow_aborted",
}
OTHER_ACTIONS = {"ig_vet", "session_halt", "session_interrupted"}
ACTIONS = CLICK_ACTIONS | OTHER_ACTIONS
SESSION_EVENTS = {"session_halt", "session_interrupted"}

# The merge rejects a vet entry that carries follower data without a bio
# (2026-09-08) -- fail here instead, where it is still fixable.
VET_REQUIRED = ("followers", "following", "posts", "bio")


def session_path(today: str | None = None, now: datetime | None = None) -> Path:
    now = now or datetime.now(BERLIN)
    day = today or now.date().isoformat()
    return SI_DIR / f"ig_session_{day}.jsonl"


def next_sequence(path: Path) -> int:
    """One past the highest sequence already in the file (1 on a new file)."""
    if not path.exists():
        return 1
    highest = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            seq = json.loads(line).get("sequence")
        except ValueError:
            continue
        if isinstance(seq, int) and seq > highest:
            highest = seq
    return highest + 1


def build_record(args, now: datetime, sequence: int) -> dict:
    rec: dict = {
        "ts": now.isoformat(timespec="seconds"),
        "action": args.action_type,
    }
    if args.handle:
        rec["handle"] = args.handle.lstrip("@")
    rec["track"] = args.track or ("session" if args.action_type in SESSION_EVENTS
                                  else "reach")
    if args.pre_warm:
        rec["pre_warm"] = True
    if args.post_url:
        rec["post_url"] = args.post_url
    if args.source:
        rec["source"] = args.source
    if args.reason:
        rec["reason"] = args.reason
    if args.tier:
        rec["tier"] = args.tier
    if args.category:
        rec["category"] = args.category
    if args.follow_back:
        rec["follow_back"] = True

    if args.action_type == "ig_vet":
        rec["followers"] = args.followers
        rec["following"] = args.following
        rec["posts"] = args.posts
        rec["private"] = bool(args.private)
        if args.last_post_days is not None:
            rec["last_post_days"] = args.last_post_days
        rec["bio"] = args.bio if args.bio is not None else ""

    rec["sequence"] = sequence
    return rec


def validate(args) -> str | None:
    """Return an error message, or None when the arguments are loggable."""
    if args.action_type not in ACTIONS:
        return (f"unknown --action-type {args.action_type!r}; "
                f"allowed: {', '.join(sorted(ACTIONS))}")
    if args.action_type in SESSION_EVENTS:
        if not args.reason:
            return f"{args.action_type} needs --reason"
        return None
    if not args.handle:
        return f"{args.action_type} needs --handle"
    if args.action_type in {"ig_skip", "ig_like_skipped", "ig_unfollow_aborted"} \
            and not args.reason:
        return f"{args.action_type} needs --reason"
    if args.action_type == "ig_vet":
        if args.private:
            return None  # a private profile has no counts to read
        missing = [f for f in VET_REQUIRED
                   if getattr(args, f.replace("-", "_")) is None]
        if missing:
            return ("ig_vet needs " + ", ".join("--" + m.replace("_", "-")
                                                for m in missing)
                    + " (the merge drops a vet line missing any of them; "
                      "an account with no bio is --bio \"\")")
    return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--action-type", required=True,
                   help="ig_like | ig_follow | ig_unfollow | ig_skip | "
                        "ig_like_skipped | ig_unfollow_aborted | ig_vet | "
                        "session_halt | session_interrupted")
    p.add_argument("--handle", help="target handle, with or without @")
    p.add_argument("--track", help="reach | scene | prominent | unfollow | session")
    p.add_argument("--pre-warm", action="store_true",
                   help="this like is the pre-warm before a follow")
    p.add_argument("--post-url", help="URL of the liked post")
    p.add_argument("--source", help="seed handles the candidate came from")
    p.add_argument("--reason", help="skip/halt reason")
    p.add_argument("--tier", help="T1 | T2 | T3")
    p.add_argument("--category", help="dj | label | artist | ...")
    p.add_argument("--follow-back", action="store_true",
                   help="they already followed us")
    # vet fields
    p.add_argument("--followers", type=int)
    p.add_argument("--following", type=int)
    p.add_argument("--posts", type=int)
    p.add_argument("--last-post-days", type=int)
    p.add_argument("--bio", help='bio text verbatim; "" when there is none')
    g = p.add_mutually_exclusive_group()
    g.add_argument("--private", action="store_true", help="profile is private")
    g.add_argument("--public", action="store_true", help="profile is public")
    # plumbing
    p.add_argument("--file", help="session log path (default: today's)")
    p.add_argument("--sequence", type=int,
                   help="override the auto-incremented sequence")
    args = p.parse_args(argv)

    err = validate(args)
    if err:
        print(f"[REFUSED] {err}", file=sys.stderr)
        return 2

    now = datetime.now(BERLIN)
    path = Path(args.file) if args.file else session_path(now=now)
    sequence = args.sequence if args.sequence is not None else next_sequence(path)
    rec = build_record(args, now, sequence)

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as exc:
        # STRICT rule: a failed JSONL write stops the session, never a
        # silent skip or a batched rewrite later (2026-05-08 lost 10 names).
        print(f"[FAILED] could not append to {path}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(rec, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
