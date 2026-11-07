"""Shared JSON state I/O: atomic writes + loud corrupt-file failures.

Audit P2-10 (finding 12). Two rules for every state file (trackers,
engagement log, enriched contacts, releases, manual stats):

1. WRITES are atomic — dump to a temp file in the same directory, then
   os.replace(). A crash or full disk mid-write can no longer leave a
   half-written tracker behind.

2. A file that EXISTS but cannot be parsed is a hard stop, never an empty
   default. The old pattern (`except JSONDecodeError: return {}`) meant a
   corrupt sc_follow_tracker.json loaded as "nothing ever followed" — and
   the next save then OVERWROTE the corrupt-but-recoverable file with that
   empty state. For enriched_contacts.json that would have clobbered all
   938 contacts. Missing files still return the default: first-run
   bootstrap is legitimate.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

EXIT_CORRUPT = 5


class CorruptStateFile(SystemExit):
    """Raised (exit 5) when an existing state file cannot be parsed.

    Prints its message on raise — SystemExit with an int code is otherwise
    silent, and the operator must see WHICH file to restore.
    """

    def __init__(self, message: str):
        self.message = message
        print(message)
        super().__init__(EXIT_CORRUPT)


def load_json_checked(path, default, what: str = "state file"):
    """Load JSON state. Missing file -> default. Corrupt file -> hard stop."""
    p = Path(path)
    if not p.exists():
        return default
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        raise CorruptStateFile(
            f"[CORRUPT STATE] {p} exists but cannot be parsed ({exc}).\n"
            f"Refusing to continue with an empty {what} — a later save would "
            f"overwrite recoverable data. Restore the file from git or a "
            f".bak, then retry."
        )


def atomic_write_json(path, data, *, indent: int = 2) -> None:
    """Write JSON via temp-file + os.replace() in the target directory."""
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
