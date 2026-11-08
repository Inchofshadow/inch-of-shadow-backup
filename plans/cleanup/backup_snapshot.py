#!/usr/bin/env python3
"""Backup snapshot for the GitHub copy (System 62). DRY RUN ONLY for now.

Sorts every file in the code folder into one of the BACKUP-MAP.md categories
and prints counts + sizes. It reads files, never changes, moves or uploads anything.

Categories:
  PLAIN    goes up readable
  LOCKED   goes up encrypted (other people's contact data, DM-related info, IG exports)
  NEVER    secrets + private DM messages: never leave the Mac
  MEDIA    big media for the off-site media backup (System 63), not GitHub
  SKIP     git internals and OS junk
  REVIEW   not decided in BACKUP-MAP.md yet

Usage:
  python3 plans/cleanup/backup_snapshot.py [--json OUT]              dry run
  python3 plans/cleanup/backup_snapshot.py --build DEST --key KEY    build the snapshot folder

Build: PLAIN files are copied to DEST, LOCKED files become DEST/<path>.enc
(openssl aes-256-cbc, pbkdf2, key file KEY). A LOCKED file is only re-encrypted
when its content changed (sha256 kept in KEY's folder, state.json), so pushes stay small.
Files in DEST that are no longer in the source are removed from DEST (never from the source).
After a build, commit in DEST with `git add -A -f` (the copied .gitignore files would
otherwise hide data/, generated_images/ etc.; DEST only holds PLAIN + .enc files).
"""
import argparse
import fnmatch
import hashlib
import shutil
import subprocess
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SECRET_NAMES = {".env", "credentials.json", "youtube_token.json", "youtube_oauth.json",
                ".sc_user_token.json", ".sc_browser_state.json", ".flask_secret"}
SECRET_GLOBS = ["*_browser_state.json", ".env.*", "*token*.json", "*recovery-codes*", "*recovery_codes*"]
DM_GLOBS = ["data/instagram-*/your_instagram_activity/messages/*",
            "plans/passwords-2fa/*",  # account list (Amir 11-06): never leaves the Mac
            "plans/voice-study/my-english-dm-lines.json"]
SKIP_DIRS = {".git", ".venv"}  # .venv added 2026-11-08 (System 69): 609 MB, rebuilt from requirements-lock.txt
SKIP_NAMES = {".DS_Store"}
REVIEW_PREFIXES = []
SKIP_PREFIXES = [".claude/worktrees/"]  # other chats' git worktrees = copies of this repo
# Goes up even though it is media (Amir 11-05, BACKUP-MAP 4b)
MEDIA_UP_PREFIXES = ["data/", "generated_images/", "docs/brand/fonts/trials/"]
MEDIA_PREFIXES = ["artwork/", "resized/", "resized_video/", "videos/", "EPK/", "references/",
                  "styled/", "brand/", "music-tools/drumrack/serum_sort/backups/"]
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".tif", ".tiff", ".psd",
             ".mp4", ".mov", ".m4v", ".webm", ".wav", ".mp3", ".aif", ".aiff", ".flac",
             ".m4a", ".ogg", ".pdf", ".zip"}
SI_ARCHIVE_GLOB = "scene_intelligence/backups/*.tar.gz"
# docs/reports/ added 2026-11-08: reports carry bare contact handles the marker scan misses (si-cleanup plan).
LOCKED_PREFIXES = ["data/", "plans/outreach-page/", "scene_intelligence/backups/", "docs/reports/"]
# Every SI data file (trackers, rosters, logs, contact lists) is locked; only its code goes plain
LOCKED_UNLESS_CODE_PREFIXES = ["scene_intelligence/"]
CODE_EXT = {".py", ".sh", ".command"}
# Handle lists without emails: lock a text file with this many profile markers
HANDLE_MARKERS = (b'"username"', b'"handle"', b'"user_id"', b"instagram.com/", b"soundcloud.com/")
HANDLE_LIMIT = 20
LOCKED_FILES = {"plans/voice-study/amir-dm-voice.md"}
TEXT_EXT = {".json", ".md", ".txt", ".csv", ".py", ".html", ".js", ".yaml", ".yml", ".tsv",
            ".jsonl", ".log", ".xml", ".bak", ""}
EMAIL_RE = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(rb"\+\d{2,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{2,5}")
# Emails that are not other people's data
OWN_EMAILS = {b"inchofshadow@gmail.com", b"noreply@anthropic.com"}
BIG = 50 * 1024 * 1024


def has_people_data(path, ext):
    # Scan every file that is not binary (sniff NUL bytes, never trust the extension:
    # "x.json.bak.20261106_reenrich" leaked plain on 11-06/07 because of that)
    try:
        with open(path, "rb") as f:
            data = f.read(30 * 1024 * 1024)
    except OSError:
        return False
    if b"\x00" in data[:8192]:
        return False
    if sum(data.count(m) for m in HANDLE_MARKERS) >= HANDLE_LIMIT:
        return True
    for m in EMAIL_RE.finditer(data):
        e = m.group(0).lower()
        if e in OWN_EMAILS or e.endswith((b".png", b".jpg", b".webp", b".svg")) \
                or b"example." in e or e.startswith(b"noreply@"):
            continue
        return True
    return bool(PHONE_RE.search(data))


def classify(rel, full):
    name = os.path.basename(rel)
    ext = os.path.splitext(name)[1].lower()
    if name in SKIP_NAMES or any(rel.startswith(p) for p in SKIP_PREFIXES):
        return "SKIP"
    if name in SECRET_NAMES or any(fnmatch.fnmatch(name, g) for g in SECRET_GLOBS):
        return "NEVER"
    if any(fnmatch.fnmatch(rel, g) for g in DM_GLOBS) or "/your_instagram_activity/messages/" in rel:
        return "NEVER"
    if any(rel.startswith(p) for p in REVIEW_PREFIXES):
        return "REVIEW"
    if rel in LOCKED_FILES or any(rel.startswith(p) for p in LOCKED_PREFIXES):
        return "LOCKED"
    if any(rel.startswith(p) for p in LOCKED_UNLESS_CODE_PREFIXES) and ext not in CODE_EXT \
            and ext not in MEDIA_EXT:
        return "LOCKED"
    up_media = any(rel.startswith(p) for p in MEDIA_UP_PREFIXES)
    if not up_media:
        if any(rel.startswith(p) for p in MEDIA_PREFIXES) or fnmatch.fnmatch(rel, SI_ARCHIVE_GLOB):
            return "MEDIA"
        if ext in MEDIA_EXT and not rel.startswith("release_manager/static/"):
            return "MEDIA"
    if has_people_data(full, ext):
        return "LOCKED"
    return "PLAIN"


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if os.path.islink(full):
                continue
            rel = os.path.relpath(full, ROOT)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            yield rel, full, size


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


README = """# Inch of Shadow code backup

Snapshot of the Inchofshadowcode folder, no git history from the Mac repo.
Built by plans/cleanup/backup_snapshot.py. The Mac copy is the original; this is an extra copy.

- Plain files: readable as they are.
- `*.enc` files: hold other people's contact data or IG exports. Encrypted with
  openssl aes-256-cbc + pbkdf2 (200000 rounds). The key is only on the Mac and on the Intenso drive.
  Decrypt one: `openssl enc -d -aes-256-cbc -md sha256 -pbkdf2 -iter 200000 -pass file:KEY -in X.enc -out X`
- Not in here: secrets (.env, tokens, OAuth files, login cookies), private DM messages, big media.
"""
KEEP_IN_DEST = {".git", "README-BACKUP.md"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(rows, dest, key):
    dest = os.path.abspath(dest)
    if dest == ROOT or dest.startswith(ROOT + os.sep) or ROOT.startswith(dest + os.sep):
        sys.exit("DEST must be outside the code folder and must not contain it")
    if os.path.exists(dest) and os.listdir(dest) and not (
            os.path.isdir(os.path.join(dest, ".git"))
            or os.path.exists(os.path.join(dest, "README-BACKUP.md"))):
        sys.exit("DEST is not empty and is not a backup snapshot; refusing to delete in it")
    if not os.path.isfile(key):
        sys.exit(f"key file missing: {key}")
    state_path = os.path.join(os.path.dirname(os.path.abspath(key)), "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    os.makedirs(dest, exist_ok=True)
    expected = set()
    copied = encrypted = unchanged = 0
    for r in rows:
        if r["cat"] not in ("PLAIN", "LOCKED"):
            continue
        rel = r["path"]
        src = os.path.join(ROOT, rel)
        if os.path.basename(rel) in SECRET_NAMES:
            sys.exit(f"STOP: secret sorted as {r['cat']}: {rel}")
        if r["cat"] == "PLAIN":
            out_rel = rel
            out = os.path.join(dest, out_rel)
            st = os.stat(src)
            if os.path.exists(out) and os.path.getsize(out) == st.st_size \
                    and int(os.path.getmtime(out)) == int(st.st_mtime):
                unchanged += 1
            else:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.copy2(src, out)
                copied += 1
        else:
            out_rel = rel + ".enc"
            out = os.path.join(dest, out_rel)
            digest = sha256(src)
            if os.path.exists(out) and state.get(rel) == digest:
                unchanged += 1
            else:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                subprocess.run(["openssl", "enc", "-aes-256-cbc", "-md", "sha256", "-pbkdf2", "-iter", "200000",
                                "-salt", "-in", src, "-out", out, "-pass", f"file:{key}"],
                               check=True)
                state[rel] = digest
                encrypted += 1
        expected.add(out_rel)
    removed = 0
    for dirpath, dirnames, filenames in os.walk(dest):
        dirnames[:] = [d for d in dirnames if not (dirpath == dest and d in KEEP_IN_DEST)]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), dest)
            if rel in KEEP_IN_DEST or rel in expected:
                continue
            os.remove(os.path.join(dest, rel))
            state.pop(rel[:-4] if rel.endswith(".enc") else rel, None)
            removed += 1
    with open(os.path.join(dest, "README-BACKUP.md"), "w") as f:
        f.write(README)
    with open(state_path, "w") as f:
        json.dump(state, f)
    os.chmod(state_path, 0o600)
    print(f"\nBUILD {dest}: copied {copied}, encrypted {encrypted}, unchanged {unchanged}, "
          f"removed from snapshot {removed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the full file list here")
    ap.add_argument("--build", metavar="DEST", help="build the snapshot into DEST")
    ap.add_argument("--key", help="key file for LOCKED files (needed with --build)")
    args = ap.parse_args()

    totals = defaultdict(lambda: [0, 0])
    by_top = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    big, rows = [], []
    for rel, full, size in walk():
        cat = classify(rel, full)
        totals[cat][0] += 1
        totals[cat][1] += size
        top = rel.split(os.sep)[0] if os.sep in rel else "(root files)"
        by_top[cat][top][0] += 1
        by_top[cat][top][1] += size
        if size > BIG and cat in ("PLAIN", "LOCKED"):
            big.append((rel, size, cat))
        rows.append({"path": rel, "size": size, "cat": cat})

    order = ["PLAIN", "LOCKED", "NEVER", "MEDIA", "REVIEW", "SKIP"]
    print(("BUILD" if args.build else "DRY RUN - nothing copied, encrypted or uploaded") + "\n")
    print(f"{'category':8} {'files':>7} {'size':>10}")
    for c in order:
        n, s = totals.get(c, [0, 0])
        print(f"{c:8} {n:7d} {human(s):>10}")
    up = totals["PLAIN"][1] + totals["LOCKED"][1]
    print(f"\nGoes to GitHub (PLAIN + LOCKED): {human(up)}")
    for c in order:
        if c == "SKIP" or c not in by_top:
            continue
        print(f"\n{c} by top folder:")
        for top, (n, s) in sorted(by_top[c].items(), key=lambda kv: -kv[1][1])[:12]:
            print(f"  {top:32} {n:6d} {human(s):>10}")
    print(f"\nFiles over 50 MB going up: {len(big)}")
    for rel, size, cat in sorted(big, key=lambda x: -x[1]):
        print(f"  {human(size):>10}  {cat}  {rel}")
    if args.json:
        with open(args.json, "w") as f:
            json.dump(rows, f, indent=0)
        print(f"\nFull list: {args.json}")
    if args.build:
        if not args.key:
            sys.exit("--build needs --key")
        build(rows, args.build, args.key)


if __name__ == "__main__":
    sys.exit(main())
