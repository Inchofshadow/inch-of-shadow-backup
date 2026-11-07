#!/usr/bin/env python3
"""Shadow Archive helper (docs/brand/shadow-archive/).

    python3 shadow_archive.py check            validate index.json and that every note, thumb and child exists
    python3 shadow_archive.py render           write README.md from index.json
    python3 shadow_archive.py next-id          print the next free R-number

Claude runs these at intake. The Release Manager page reads the same index.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from release_manager import archive  # noqa: E402


def check() -> int:
    try:
        data = archive.load_index(ROOT)
    except archive.ArchiveError as exc:
        print(f"index.json: {exc}")
        return 1
    base = archive.archive_dir(ROOT)
    problems = 0
    for r in data["references"]:
        for key in ("notes", "thumb"):
            rel = r.get(key)
            if rel and not (base / rel).is_file():
                print(f"{r['id']}: {key} missing: {rel}")
                problems += 1
        for c in r.get("children") or []:
            if not (base / c["path"]).exists():
                print(f"{r['id']}: child missing: {c['path']}")
                problems += 1
    print(f"{len(data['references'])} references, {problems} problems")
    return 1 if problems else 0


def render() -> int:
    data = archive.load_index(ROOT)
    out = archive.archive_dir(ROOT) / "README.md"
    out.write_text(archive.render_readme(data), encoding="utf-8")
    print(f"wrote {out} ({len(data['references'])} references)")
    return 0


def next_id() -> int:
    data = archive.load_index(ROOT)
    n = max((int(r["id"].split("-")[1]) for r in data["references"]), default=0) + 1
    print(f"R-{n:03d}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit({"check": check, "render": render, "next-id": next_id}.get(cmd, check)())
