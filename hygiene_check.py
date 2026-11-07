#!/usr/bin/env python3
"""Read-only project hygiene check (Temporary Files Rule, 2026-10-24).

Finds what research and reference runs should not leave behind:
  RED    saved web pages with a remote-code loader (eval of fetched or
         base64-decoded code), like the hacked inverted-audio.com pages
         found on 2026-10-24
  WARN   leftover scratch-* folders
  WARN   saved copies of external web pages that still carry <script> tags
Our own pages (Release Manager templates, music tools, HyperFrames
compositions) are not saved external pages and are not flagged.
Moves and deletes nothing. Exit code: 0 clean, 1 warnings, 2 red.

Usage: python3 hygiene_check.py [--root DIR]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "venv", ".venv", "node_modules", "__pycache__", "data",
             "release_manager", "backups"}
REMOTE_EVAL = [
    re.compile(r"eval\s*\(\s*atob\s*\(", re.I),
    re.compile(r"\.then\s*\([^)]*\)\s*=>\s*\{?\s*eval\s*\(", re.I),
    re.compile(r"fetch\s*\(\s*atob\s*\(", re.I),
    re.compile(r"new\s+Function\s*\(\s*atob\s*\(", re.I),
]
SAVED_PAGE = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']https?://'
    r'|<meta[^>]+property=["\']og:url["\'][^>]+content=["\']https?://', re.I)
SCRIPT = re.compile(r"<script\b", re.I)


def scan(root: Path) -> dict:
    found = {"red": [], "scratch": [], "saved_pages": []}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_dir() and path.name.startswith("scratch-"):
            found["scratch"].append(str(rel))
            continue
        if path.is_file() and path.suffix.lower() in (".html", ".htm"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(p.search(text) for p in REMOTE_EVAL):
                found["red"].append(str(rel))
            elif SAVED_PAGE.search(text) and SCRIPT.search(text):
                found["saved_pages"].append(str(rel))
    # A scratch folder's contents are reported once, as the folder.
    found["saved_pages"] = [p for p in found["saved_pages"]
                            if not any(p.startswith(s + "/") for s in found["scratch"])]
    return found


def report(found: dict) -> tuple[str, int]:
    lines = []
    if found["red"]:
        lines.append(f"RED  remote-code loader in {len(found['red'])} saved page(s), do not open in a browser:")
        lines += [f"     {p}" for p in found["red"]]
    if found["scratch"]:
        lines.append(f"WARN {len(found['scratch'])} leftover scratch folder(s), move to Trash once results are saved:")
        lines += [f"     {p}" for p in found["scratch"]]
    if found["saved_pages"]:
        lines.append(f"WARN {len(found['saved_pages'])} saved external page(s) still carrying scripts:")
        lines += [f"     {p}" for p in found["saved_pages"]]
    code = 2 if found["red"] else (1 if found["scratch"] or found["saved_pages"] else 0)
    if not lines:
        lines.append("OK   no scratch folders, no saved pages with scripts")
    return "\n".join(lines), code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args(argv)
    text, code = report(scan(Path(args.root)))
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
