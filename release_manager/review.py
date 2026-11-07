"""
release_manager/review.py
--------------------------
The review flow (System 82, card M10, 2026-11-06): a file is identified by its path
and its SHA-256, never by a folder or a name. Approval is a field in the release
JSON. The agent writes files and records, Amir decides, nothing moves, nothing
posts, nothing is deleted.

Spec: plans/strategy/gero-cp-deep-dive-2026-11-06.md section C.
Placement: plans/strategy/rm2-dry-run-2026-11-06.md section 1c.
Schema: plans/review-flow-schema.md.

Shape, inside releases/<slug>.json:

    "review": {
        "version": 1,
        "updated_at": "2026-11-06T18:02:00",
        "consumed_ticks": ["<page db doc id>", "..."],   # phone ticks already looked at, never twice
        "items": {
            "r-001": {
                "id": "r-001",
                "kind": "render",                 # render / cover / caption / post-draft / canvas
                "label": "reel, 9:16, cut 3",
                "area": "socials",
                "destination": ["reel_instagram"],   # video_resizer / artwork_resizer preset keys
                "path": "videos/half-the-night/renders/reel-v3.mp4",
                "sha256": "...", "bytes": 48213340,  # the bound hash, written once at submit
                "observed_sha256": "...",             # what the last re-hash saw on disk
                "created": "2026-11-06T13:10:00", "made_by": "claude",
                "text": null,                    # captions and post drafts carry their text here
                "text_boxes": [],                # optional [x, y, w, h] of readable type, for safe-zone
                "version": 3, "supersedes": "r-000", "superseded_by": null,
                "state": "needs-you",
                "note": "",
                "checks": [{"name": "hash", "pass": true, "reason": ""}],
                "approved": null,                # {"by", "at", "sha256"} once he says yes
                "proposed": null,                # {"action", "note", "by": "phone", "at", "tick_id"} a phone tick; state does not move until he confirms locally
                "used": null,                    # {"where", "at", "by", "ref"} only from his words
                "history": [{"state": "draft", "by": "claude", "at": "...", "via": "chat", "note": ""}]
            }
        }
    }

Rules the code keeps by construction: it never posts, moves, renames, deletes,
approves or marks used by itself. `tick()` records Amir's approve / change / drop;
`mark_used()` exists for the agent to write his words down and nothing calls it from
a route. An approval is bound to the SHA-256 it was given; when the file changes the
item falls back to needs-you with a note. A new version is a new item with
`supersedes`; the old one becomes superseded and its file stays where it is.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

from release_manager import storage
from release_manager.paths import repo_root

REVIEW_VERSION = 1

KINDS = ("render", "cover", "caption", "post-draft", "canvas")
FILE_KINDS = ("render", "cover", "canvas")
TEXT_KINDS = ("caption", "post-draft")
VIDEO_KINDS = ("render", "canvas")

STATES = ("draft", "needs-you", "approved", "change", "dropped", "superseded", "used")
OPEN_STATES = ("draft", "needs-you", "change", "approved")
DONE_STATES = ("used", "dropped", "superseded")

# What may follow what. Amir's three ticks go out of needs-you (and out of approved,
# in case he changes his mind before using it). The code moves draft to needs-you
# after the checks, approved back to needs-you when the file changed, and anything
# open to superseded when a new version arrives.
# A phone tick never touches `state`: it only fills item["proposed"]; the real step
# to approved / change / dropped happens locally (the RM page keystroke, or the CLI
# confirm the System chat runs on Amir's words) and records by "amir".
TRANSITIONS = {
    "draft": ("needs-you", "dropped", "superseded"),
    "needs-you": ("approved", "change", "dropped", "superseded"),
    "change": ("needs-you", "dropped", "superseded"),
    "approved": ("used", "change", "dropped", "needs-you", "superseded"),
    "used": (),
    "dropped": (),
    "superseded": (),
}

TICK_ACTIONS = {"approve": "approved", "change": "change", "drop": "dropped"}

AREAS = ("release", "socials", "booking", "income", "studio", "system")
AREA_EMOJI = {"release": "\U0001F3B5", "socials": "\U0001F3AC", "booking": "\U0001F3A7",
              "income": "\U0001F4B6", "studio": "\U0001F3B8", "system": "⚙️"}

# Meta safe zone for 9:16 (docs/brand/frame.md): nothing readable in these strips.
SAFE_TOP, SAFE_BOTTOM, SAFE_SIDE = 270, 672, 65

# Handles that never need a lookup (docs/brand, memory "handles and credits").
OWN_HANDLES = {"inch_of_shadow", "shirzilber.art", "ambertone.studios"}

CHECK_NAMES = ("hash", "format", "duration", "audio", "safe-zone", "no-text-over-face",
               "first-3s", "copy", "handles")
MANUAL_CHECKS = ("no-text-over-face", "first-3s")

HANDLE_RE = re.compile(r"(?:(?<=\s)|^|(?<=[(\[]))@([A-Za-z0-9_.]{2,30})")
EM_DASH_RE = re.compile("[—―]")


class ReviewError(Exception):
    """A refused change: wrong state, unknown item, hash mismatch, forbidden action."""


# ---------------------------------------------------------------------------
# Time, ids, hashing
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_review(rel: dict) -> dict:
    """rel["review"] with version and items present. Mutates rel."""
    block = rel.get("review")
    if not isinstance(block, dict):
        block = {}
    block.setdefault("version", REVIEW_VERSION)
    if not isinstance(block.get("items"), dict):
        block["items"] = {}
    block.setdefault("updated_at", "")
    rel["review"] = block
    return block


def next_id(block: dict) -> str:
    nums = []
    for key in block.get("items", {}):
        m = re.fullmatch(r"r-(\d+)", key)
        if m:
            nums.append(int(m.group(1)))
    return "r-%03d" % (max(nums) + 1 if nums else 1)


def resolve_path(path: str, root: Path | None = None) -> Path:
    """A relative path is read against the repo root resolved once at import (storage.BASE_DIR,
    the same repo_root() value), so a page render never shells out to git per item."""
    p = Path(path)
    return p if p.is_absolute() else (root or storage.BASE_DIR) / p


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def new_item(kind: str, label: str, *, path: str = "", text: str | None = None,
             area: str = "socials", destination: list | None = None,
             made_by: str = "claude", supersedes: str | None = None,
             text_boxes: list | None = None, root: Path | None = None,
             at: str | None = None) -> dict:
    """One review item in state draft. Hash and size come from the file when it exists."""
    if kind not in KINDS:
        raise ReviewError("unknown kind %r (one of %s)" % (kind, ", ".join(KINDS)))
    if area not in AREAS:
        raise ReviewError("unknown area %r (one of %s)" % (area, ", ".join(AREAS)))
    if kind in FILE_KINDS and not path:
        raise ReviewError("a %s needs a path" % kind)
    if kind in TEXT_KINDS and text is None:
        raise ReviewError("a %s needs its text" % kind)
    at = at or now_iso()
    item = {
        "id": "",
        "kind": kind,
        "label": label,
        "area": area,
        "destination": list(destination or []),
        "path": path,
        "sha256": "",
        "bytes": 0,
        "created": at,
        "made_by": made_by,
        "text": text,
        "text_boxes": list(text_boxes or []),
        "version": 1,
        "supersedes": supersedes,
        "superseded_by": None,
        "state": "draft",
        "note": "",
        "checks": [],
        "approved": None,
        "used": None,
        "history": [{"state": "draft", "by": made_by, "at": at, "via": "chat", "note": ""}],
    }
    if path:
        p = resolve_path(path, root)
        if p.is_file():
            item["sha256"] = sha256_of(p)
            item["bytes"] = p.stat().st_size
    elif text is not None:
        item["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        item["bytes"] = len(text.encode("utf-8"))
    return item


def add_item(rel: dict, item: dict) -> dict:
    """Put an item into the release. When it supersedes another, that one becomes
    superseded (its file stays). Mutates rel; returns the item with its id."""
    block = ensure_review(rel)
    item = dict(item)
    if not item.get("id"):
        item["id"] = next_id(block)
    if item["id"] in block["items"]:
        raise ReviewError("item %s exists" % item["id"])
    old_id = item.get("supersedes")
    if old_id:
        old = block["items"].get(old_id)
        if old is None:
            raise ReviewError("supersedes unknown item %s" % old_id)
        if old["state"] in DONE_STATES and old["state"] != "used":
            raise ReviewError("item %s is %s, nothing to supersede" % (old_id, old["state"]))
        item["version"] = int(old.get("version", 1)) + 1
        if old["state"] != "used":
            _move(old, "superseded", by=item.get("made_by", "claude"), via="chat",
                  note="replaced by %s" % item["id"])
        old["superseded_by"] = item["id"]
    block["items"][item["id"]] = item
    block["updated_at"] = now_iso()
    return item


def get_item(rel: dict, item_id: str) -> dict:
    item = ensure_review(rel)["items"].get(item_id)
    if item is None:
        raise ReviewError("unknown item %s" % item_id)
    return item


def _move(item: dict, state: str, *, by: str, via: str, note: str = "") -> dict:
    """The one place a state changes. Refuses a step TRANSITIONS does not list."""
    if state not in STATES:
        raise ReviewError("unknown state %r" % state)
    current = item.get("state", "draft")
    if state not in TRANSITIONS.get(current, ()):
        raise ReviewError("%s cannot go from %s to %s" % (item.get("id", "?"), current, state))
    at = now_iso()
    item["state"] = state
    if note:
        item["note"] = note
    item.setdefault("history", []).append({"state": state, "by": by, "at": at, "via": via, "note": note})
    return item


def tick(rel: dict, item_id: str, action: str, *, by: str = "amir", via: str = "rm",
         note: str = "", sha256: str = "", root: Path | None = None) -> dict:
    """Amir's LOCAL tick (RM page or the CLI confirm): approve / change / drop.
    Anything else is refused, and so is via="phone" (phone ticks only propose).

    approve needs the sha256 the reviewer saw. It must equal the hash recorded when
    the item was submitted AND the hash on disk now; otherwise the tick is refused
    ("file changed after approval" when the disk differs, "hash mismatch" when the
    tick names another hash) and the item carries the note. A held item (any failing
    chip) cannot be approved: the check is fixed first, by a new version.
    The approval records the hash it was given; the bound hash is never rewritten.
    """
    if action not in TICK_ACTIONS:
        raise ReviewError("action %r is not one of approve, change, drop" % action)
    if via == "phone":
        raise ReviewError("a phone tick cannot decide; import_ticks records it as a proposal")
    item = get_item(rel, item_id)
    if item["state"] in DONE_STATES:
        raise ReviewError("%s is %s, no ticks on it" % (item_id, item["state"]))
    note = (note or "").strip()
    if not note and item.get("proposed") and item["proposed"].get("action") == action:
        note = item["proposed"].get("note", "")      # confirming the phone proposal keeps its note
    if action == "approve":
        bound = item.get("sha256") or ""
        if not bound:
            raise ReviewError("%s has no recorded hash, run the checks first" % item_id)
        current = current_hash(item, root)
        if current is None:
            raise ReviewError("file missing: %s" % item.get("path"))
        if current != bound:
            _flag_changed(item, current, by="code", via=via)
            ensure_review(rel)["updated_at"] = now_iso()
            raise ReviewError("file changed after approval")
        if gate(item) == "held":
            failing = [c["name"] for c in item.get("checks") or [] if c.get("pass") is False]
            raise ReviewError("held: %s failing, a new version is needed" % ", ".join(failing))
        if (sha256 or "").strip().lower() != bound:
            raise ReviewError("hash mismatch: the tick names %s, the item is %s" % ((sha256 or "none")[:12], bound[:12]))
        _move(item, "approved", by=by, via=via, note=note)
        item["approved"] = {"by": by, "at": item["history"][-1]["at"], "sha256": bound}
    elif action == "change":
        if not note:
            raise ReviewError("change needs a note: what should be different")
        _move(item, "change", by=by, via=via, note=note)
        item["approved"] = None
    else:
        _move(item, "dropped", by=by, via=via, note=note)
        item["approved"] = None
    item["ticks"] = {"by": by, "at": item["history"][-1]["at"], "via": via, "note": note}
    item["proposed"] = None
    ensure_review(rel)["updated_at"] = now_iso()
    return item


def mark_used(rel: dict, item_id: str, *, where: str, ref: str = "", by: str = "amir") -> dict:
    """Record that it went out. Only from Amir's words; no route calls this."""
    item = get_item(rel, item_id)
    if item["state"] != "approved":
        raise ReviewError("%s is %s, only an approved item can be used" % (item_id, item["state"]))
    _move(item, "used", by=by, via="chat", note="used on %s" % where)
    item["used"] = {"where": where, "at": item["history"][-1]["at"], "by": by, "ref": ref}
    ensure_review(rel)["updated_at"] = now_iso()
    return item


def submit(rel: dict, item_id: str, *, root: Path | None = None, by: str = "claude") -> dict:
    """Run the checks on a draft and hand it to Amir (draft -> needs-you)."""
    item = get_item(rel, item_id)
    run_checks(item, root)
    if item["state"] in ("draft", "change"):
        _move(item, "needs-you", by=by, via="chat", note="")
    ensure_review(rel)["updated_at"] = now_iso()
    return item


# ---------------------------------------------------------------------------
# Hash binding
# ---------------------------------------------------------------------------

def current_hash(item: dict, root: Path | None = None) -> str | None:
    """The SHA-256 of what is on disk now (or of the text). None when the file is gone."""
    if item.get("path"):
        p = resolve_path(item["path"], root)
        if not p.is_file():
            return None
        return sha256_of(p)
    text = item.get("text")
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _flag_changed(item: dict, current: str, *, by: str = "code", via: str = "rm") -> None:
    """The file on disk differs from the bound hash: record what was seen, drop any
    approval, send an approved item back to needs-you. item["sha256"] stays."""
    note = "file changed after approval" if item.get("approved") else "file changed since review"
    if item["state"] == "approved":
        _move(item, "needs-you", by=by, via=via, note=note)
    else:
        item["note"] = note
    item["approved"] = None
    item["proposed"] = None
    item["observed_sha256"] = current
    set_check(item, "hash", False, "%s (disk %s, bound %s)" % (note, current[:12], (item.get("sha256") or "")[:12]))


def refresh(rel: dict, root: Path | None = None) -> list:
    """Re-hash every open item against its bound hash. An approved item whose file
    changed falls back to needs-you with the note; a needs-you item gets a failing
    hash chip. Returns the ids that changed. Mutates rel; the caller saves."""
    changed = []
    for item in ensure_review(rel)["items"].values():
        if item["state"] not in ("approved", "needs-you"):
            continue
        current = current_hash(item, root)
        if current is None:
            if set_check(item, "hash", False, "file missing: %s" % item.get("path")):
                changed.append(item["id"])
            continue
        bound = item.get("sha256") or ""
        if not bound:
            item["sha256"] = current
            changed.append(item["id"])
        elif current != bound:
            if item.get("observed_sha256") != current or item["state"] == "approved":
                _flag_changed(item, current, by="code", via="rm")
                changed.append(item["id"])
        elif item.get("observed_sha256") not in (None, "", current):
            item["observed_sha256"] = current
            if set_check(item, "hash", True, current[:12]):
                changed.append(item["id"])
    if changed:
        rel["review"]["updated_at"] = now_iso()
    return changed


# ---------------------------------------------------------------------------
# Checks (chips)
# ---------------------------------------------------------------------------

def set_check(item: dict, name: str, passed, reason: str = "") -> bool:
    """Write one chip (pass True / False / None for na or manual). True when it changed."""
    checks = item.setdefault("checks", [])
    entry = {"name": name, "pass": passed, "reason": reason}
    for i, c in enumerate(checks):
        if c.get("name") == name:
            if c == entry:
                return False
            checks[i] = entry
            return True
    checks.append(entry)
    return True


def gate(item: dict) -> str:
    """held when any chip fails, pending when none ran, passed otherwise."""
    checks = item.get("checks") or []
    if not checks:
        return "pending"
    if any(c.get("pass") is False for c in checks):
        return "held"
    return "passed"


def _video_presets() -> dict:
    try:
        import video_resizer
    except (ImportError, SystemExit):
        return {}
    out = {}
    for e in video_resizer.VIDEO_EXPORTS:
        key, w, h, platform, _slug, max_s, min_s, audio, fps, desc = e
        out[key] = {"w": w, "h": h, "platform": platform, "max_s": max_s, "min_s": min_s,
                    "audio": audio, "fps": fps, "desc": desc}
    return out


def _image_presets() -> dict:
    try:
        import artwork_resizer
    except (ImportError, SystemExit):
        return {}
    return {e[0]: {"w": e[1], "h": e[2], "platform": e[3]} for e in artwork_resizer.EXPORTS}


def probe_video(path: Path) -> dict | None:
    """Duration, size, fps, codec and audio via the bundled imageio-ffmpeg (video_resizer)."""
    try:
        import video_resizer
        return video_resizer.probe_video(path)
    except (ImportError, SystemExit, OSError, subprocess.SubprocessError):
        return None


def probe_image(path: Path) -> dict | None:
    try:
        from PIL import Image
        with Image.open(path) as im:
            return {"width": im.width, "height": im.height, "format": im.format or ""}
    except Exception:
        return None


def _ratio(w: int, h: int) -> str:
    from math import gcd
    g = gcd(w, h) or 1
    return "%d:%d" % (w // g, h // g)


def check_format(item: dict, probe: dict | None) -> list:
    """format / duration / audio chips per destination preset."""
    chips = []
    kind = item["kind"]
    dests = item.get("destination") or []
    if kind in TEXT_KINDS:
        return [("format", None, "no file"), ("duration", None, "no file"), ("audio", None, "no file")]
    if probe is None:
        return [("format", False, "could not probe the file"),
                ("duration", False, "could not probe the file"), ("audio", False, "could not probe the file")]
    w, h = int(probe.get("width", 0)), int(probe.get("height", 0))
    if kind in VIDEO_KINDS:
        presets = _video_presets()
    else:
        presets = _image_presets()
    if not dests:
        chips.append(("format", None, "%dx%d, no destination named" % (w, h)))
    else:
        bad, good = [], []
        for d in dests:
            p = presets.get(d)
            if p is None:
                bad.append("%s unknown preset" % d)
            elif (w, h) != (p["w"], p["h"]):
                bad.append("%s wants %dx%d, file is %dx%d" % (d, p["w"], p["h"], w, h))
            else:
                good.append(d)
        if bad:
            chips.append(("format", False, "; ".join(bad)))
        else:
            chips.append(("format", True, "%dx%d %s for %s" % (w, h, _ratio(w, h), ", ".join(good))))
    if kind not in VIDEO_KINDS:
        chips.append(("duration", None, "image"))
        chips.append(("audio", None, "image"))
        return chips
    dur = float(probe.get("duration") or 0.0)
    has_audio = bool(probe.get("has_audio"))
    dur_bad, audio_bad, audio_want = [], [], None
    for d in dests:
        p = presets.get(d)
        if p is None:
            continue
        if p["max_s"] and dur > p["max_s"] + 0.05:
            dur_bad.append("%s max %ds, file is %.1fs" % (d, p["max_s"], dur))
        if p["min_s"] and dur < p["min_s"] - 0.05:
            dur_bad.append("%s min %ds, file is %.1fs" % (d, p["min_s"], dur))
        if p["audio"] and not has_audio:
            audio_bad.append("%s needs an audio stream, none found" % d)
        if not p["audio"] and has_audio:
            audio_bad.append("%s must be silent, file has audio" % d)
        audio_want = p["audio"] if audio_want is None else audio_want
    if dur <= 0:
        chips.append(("duration", False, "no duration read"))
    elif dur_bad:
        chips.append(("duration", False, "; ".join(dur_bad)))
    else:
        chips.append(("duration", True, "%.1fs" % dur))
    if audio_bad:
        chips.append(("audio", False, "; ".join(audio_bad)))
    elif has_audio:
        chips.append(("audio", True, probe.get("audio_codec") or "stream present"))
    else:
        chips.append(("audio", True if audio_want is False else None, "silent"))
    return chips


def check_safe_zone(item: dict, probe: dict | None) -> tuple:
    """Meta safe zone 270 / 672 / 65 on a 9:16 frame. Needs the type boxes
    ([x, y, w, h] in frame pixels) the renderer wrote; without them it is manual."""
    if item["kind"] in TEXT_KINDS:
        return ("safe-zone", None, "no frame")
    if probe is None:
        return ("safe-zone", None, "could not probe the file")
    w, h = int(probe.get("width", 0)), int(probe.get("height", 0))
    if not (w and h) or abs(w / h - 9 / 16) > 0.01:
        return ("safe-zone", None, "not 9:16")
    boxes = item.get("text_boxes") or []
    if not boxes:
        return ("safe-zone", None, "manual: no type boxes recorded")
    scale = h / 1920.0
    top, bottom, side = SAFE_TOP * scale, h - SAFE_BOTTOM * scale, SAFE_SIDE * scale
    hits = []
    for b in boxes:
        try:
            x, y, bw, bh = [float(v) for v in b]
        except (TypeError, ValueError):
            return ("safe-zone", False, "type box not [x, y, w, h]: %r" % (b,))
        if y < top:
            hits.append("type at y=%d inside the top %d" % (y, SAFE_TOP))
        if y + bh > bottom:
            hits.append("type to y=%d inside the bottom %d" % (y + bh, SAFE_BOTTOM))
        if x < side or x + bw > w - side:
            hits.append("type at x=%d inside the %d side strip" % (x, SAFE_SIDE))
    if hits:
        return ("safe-zone", False, "; ".join(hits))
    return ("safe-zone", True, "%d type box(es) clear of 270 / 672 / 65" % len(boxes))


def check_copy(item: dict) -> tuple:
    """Copy rules: caption_check.py when present, em-dashes always."""
    text = item.get("text")
    if text is None:
        return ("copy", None, "no text")
    problems = []
    if EM_DASH_RE.search(text):
        problems.append("em-dash in the text")
    try:
        import caption_check
    except ImportError:
        caption_check = None
    if caption_check is not None:
        try:
            rep = caption_check.check(text)
        except Exception as e:
            rep = {"verdict": "FAIL", "results": [{"status": "FAIL", "check": "caption_check", "note": str(e)}]}
        for r in rep.get("results", []):
            if r.get("status") == "FAIL":
                problems.append("%s: %s" % (r.get("check", "").lower(), r.get("note", "")))
        if problems:
            return ("copy", False, "; ".join(problems))
        warns = [r for r in rep.get("results", []) if r.get("status") == "WARN"]
        return ("copy", True, ("%d warning(s) in caption_check" % len(warns)) if warns else "caption_check pass")
    if problems:
        return ("copy", False, "; ".join(problems))
    return ("copy", True, "no em-dashes (caption_check not present)")


def known_handles(root: Path | None = None) -> set:
    """Handles we can vouch for: our own plus anything the IG tracker and target
    list name. Read defensively; a missing file just adds nothing."""
    root = root or repo_root()
    found = set(OWN_HANDLES)
    for rel in ("scene_intelligence/ig_follow_tracker.json", "scene_intelligence/ig_target_list.json"):
        p = root / rel
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        _collect_handles(data, found, depth=0)
    return found


def _collect_handles(node, found: set, depth: int) -> None:
    if depth > 4:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("username", "handle", "ig_handle", "instagram") and isinstance(v, str):
                found.add(v.strip().lstrip("@").lower())
            elif isinstance(v, (dict, list)):
                _collect_handles(v, found, depth + 1)
            elif isinstance(k, str) and depth <= 2 and re.fullmatch(r"[a-z0-9_.]{2,30}", k) and k != "_meta":
                found.add(k.lower())
    elif isinstance(node, list):
        for v in node:
            _collect_handles(v, found, depth + 1)


def check_handles(item: dict, known: set | None = None) -> tuple:
    """Every @handle in the text must be one we verified; unknown ones are flagged
    with a question mark and the chip never passes on them."""
    text = item.get("text")
    if text is None:
        return ("handles", None, "no text")
    handles = [h.rstrip(".") for h in HANDLE_RE.findall(text)]
    if not handles:
        return ("handles", None, "no handles")
    known = known if known is not None else known_handles()
    unknown = sorted({h for h in handles if h.lower() not in known})
    if unknown:
        return ("handles", None, "? unverified: " + ", ".join("@" + h for h in unknown))
    return ("handles", True, ", ".join("@" + h for h in sorted(set(handles))))


def run_checks(item: dict, root: Path | None = None, known: set | None = None) -> list:
    """Run every chip on one item. Manual chips stay manual unless already ticked.
    Mutates item["checks"]; returns the list."""
    existing = {c["name"]: c for c in item.get("checks") or [] if isinstance(c, dict)}
    item["checks"] = []
    kind = item["kind"]
    probe = None
    current = current_hash(item, root)
    if current is None:
        set_check(item, "hash", False, "file missing: %s" % (item.get("path") or "no text"))
    elif not item.get("sha256"):
        item["sha256"] = current          # the bound hash, written once
        item["observed_sha256"] = current
        set_check(item, "hash", True, current[:12])
    elif current == item["sha256"]:
        item["observed_sha256"] = current
        set_check(item, "hash", True, current[:12])
    else:
        item["observed_sha256"] = current
        set_check(item, "hash", False, "file changed since review (disk %s, bound %s)" % (current[:12], item["sha256"][:12]))
    if kind in FILE_KINDS and current is not None:
        p = resolve_path(item["path"], root)
        probe = probe_video(p) if kind in VIDEO_KINDS else probe_image(p)
        if probe is not None:
            item["probe"] = {k: probe.get(k) for k in ("width", "height", "duration", "fps", "codec",
                                                       "has_audio", "audio_codec", "format") if k in probe}
    for name, passed, reason in check_format(item, probe):
        set_check(item, name, passed, reason)
    set_check(item, *check_safe_zone(item, probe))
    for name in MANUAL_CHECKS:
        old = existing.get(name)
        if kind in TEXT_KINDS:
            set_check(item, name, None, "no frame")
        elif old and old.get("pass") is not None:
            set_check(item, name, old["pass"], old.get("reason", ""))
        else:
            set_check(item, name, None, "manual")
    set_check(item, *check_copy(item))
    set_check(item, *check_handles(item, known))
    return item["checks"]


def set_manual_check(item: dict, name: str, passed: bool, by: str = "amir", reason: str = "") -> dict:
    """Amir's word on a manual chip (no text over the face, first 3 s)."""
    if name not in MANUAL_CHECKS:
        raise ReviewError("%s is not a manual check" % name)
    set_check(item, name, bool(passed), reason or ("checked by %s" % by))
    return item


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def backup_release_file(slug: str) -> Path | None:
    """One safety copy per day before the review block first changes a release file."""
    src = storage.release_path(slug)
    if not src.exists():
        return None
    dst = src.with_name("%s.bak.%s_review.json" % (slug, datetime.now().strftime("%Y%m%d")))
    if not dst.exists():
        shutil.copy2(src, dst)
    return dst


def save_release_review(rel: dict) -> Path:
    """Save a release whose review block was edited in place (backup first)."""
    backup_release_file(rel["slug"])
    ensure_review(rel)
    return storage.save_release(rel)


def release_title(rel: dict) -> str:
    meta = rel.get("metadata") or {}
    return meta.get("title") or rel.get("title") or rel.get("slug", "")


def load_all(root: Path | None = None) -> list:
    """Every release with a review block, as (rel, items) with the hash check refreshed
    in memory. Nothing is written here; the page saves when refresh() changed a state."""
    out = []
    for rel in storage.list_releases():
        block = rel.get("review")
        if not isinstance(block, dict) or not block.get("items"):
            continue
        out.append(rel)
    return out


# ---------------------------------------------------------------------------
# Page view
# ---------------------------------------------------------------------------

STATE_ORDER = {"needs-you": 0, "change": 1, "draft": 2, "approved": 3, "used": 4, "dropped": 5, "superseded": 6}


def item_view(rel: dict, item: dict) -> dict:
    """What the template needs for one row."""
    g = gate(item)
    chips = []
    for c in item.get("checks") or []:
        if c.get("pass") is True:
            tone = "pass"
        elif c.get("pass") is False:
            tone = "fail"
        elif c.get("name") in MANUAL_CHECKS and c.get("reason", "").startswith("manual"):
            tone = "manual"
        elif (c.get("reason") or "").startswith("?"):
            tone = "ask"
        else:
            tone = "na"
        chips.append({"name": c.get("name", ""), "tone": tone, "reason": c.get("reason", "")})
    text = item.get("text")
    return {
        "id": item["id"],
        "slug": rel["slug"],
        "release": release_title(rel),
        "kind": item.get("kind", ""),
        "label": item.get("label", ""),
        "area": item.get("area", ""),
        "area_emoji": AREA_EMOJI.get(item.get("area", ""), ""),
        "destination": item.get("destination") or [],
        "path": item.get("path", ""),
        "name": Path(item["path"]).name if item.get("path") else "",
        "sha": (item.get("sha256") or "")[:12],
        "sha256": item.get("sha256") or "",
        "bytes": item.get("bytes", 0),
        "size": _human_size(item.get("bytes", 0)),
        "created": item.get("created", ""),
        "made_by": item.get("made_by", ""),
        "version": item.get("version", 1),
        "supersedes": item.get("supersedes"),
        "superseded_by": item.get("superseded_by"),
        "state": item.get("state", "draft"),
        "gate": g,
        "held": g == "held",
        "note": item.get("note", ""),
        "chips": chips,
        "text": text,
        "text_short": (text or "")[:220] + ("..." if text and len(text) > 220 else ""),
        "approved": item.get("approved"),
        "used": item.get("used"),
        "proposed": item.get("proposed"),
        "open": item.get("state") in OPEN_STATES,
        "probe": item.get("probe") or {},
        "history": item.get("history") or [],
        "is_video": item.get("kind") in VIDEO_KINDS,
        "is_image": item.get("kind") == "cover",
    }


def _human_size(n) -> str:
    try:
        n = float(n)
    except (TypeError, ValueError):
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0
    return ""


def sort_key(v: dict) -> tuple:
    """needs-you first with held on top, then by state order, newest first."""
    return (STATE_ORDER.get(v["state"], 9), 0 if v["held"] else 1, v["created"])


def build_view(releases: list, *, release: str = "", area: str = "") -> dict:
    """Groups by release (newest item first inside each), filters, counts."""
    groups = []
    counts = {"needs-you": 0, "held": 0, "proposed": 0, "approved": 0, "change": 0, "done": 0}
    areas, slugs = set(), []
    for rel in releases:
        block = rel.get("review") or {}
        views = [item_view(rel, it) for it in (block.get("items") or {}).values()]
        slugs.append({"slug": rel["slug"], "title": release_title(rel), "n": len(views)})
        for v in views:
            areas.add(v["area"])
        if release and rel["slug"] != release:
            continue
        if area:
            views = [v for v in views if v["area"] == area]
        if not views:
            continue
        views.sort(key=lambda v: v["created"], reverse=True)
        views.sort(key=lambda v: (STATE_ORDER.get(v["state"], 9), 0 if v["held"] else 1, 0 if v["proposed"] else 1))
        for v in views:
            if v["state"] == "needs-you":
                counts["needs-you"] += 1
                if v["held"]:
                    counts["held"] += 1
            elif v["state"] in counts:
                counts[v["state"]] += 1
            if v["proposed"]:
                counts["proposed"] += 1
            if v["state"] in DONE_STATES:
                counts["done"] += 1
        groups.append({
            "slug": rel["slug"],
            "title": release_title(rel),
            "updated": block.get("updated_at", ""),
            "open": [v for v in views if v["open"]],
            "done": [v for v in views if not v["open"]],
        })
    groups.sort(key=lambda g: max([v["created"] for v in g["open"] + g["done"]] or [""]), reverse=True)
    return {
        "groups": groups,
        "counts": counts,
        "areas": sorted(areas),
        "releases": slugs,
        "filter_release": release,
        "filter_area": area,
        "area_emoji": AREA_EMOJI,
    }


# ---------------------------------------------------------------------------
# Phone export (plans/review-export-<slug>.json)
# ---------------------------------------------------------------------------

def thumbnail_data_uri(item: dict, root: Path | None = None, size: int = 360) -> str:
    """thumbnail_jpeg as a data URI, or an empty string."""
    data = thumbnail_jpeg(item, root, size)
    return ("data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")) if data else ""


def thumbnail_jpeg(item: dict, root: Path | None = None, size: int = 360) -> bytes:
    """A small JPEG (cover: PIL; render: one frame at 1 s through imageio-ffmpeg).
    Empty bytes when it cannot be made; never raises."""
    if not item.get("path"):
        return b""
    p = resolve_path(item["path"], root)
    if not p.is_file():
        return b""
    try:
        from PIL import Image
        if item["kind"] in VIDEO_KINDS:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            out = subprocess.run([ffmpeg, "-v", "error", "-ss", "1", "-i", str(p), "-frames:v", "1",
                                  "-f", "image2pipe", "-vcodec", "png", "-"],
                                 capture_output=True, timeout=30)
            if out.returncode != 0 or not out.stdout:
                return b""
            im = Image.open(BytesIO(out.stdout))
        else:
            im = Image.open(p)
        im = im.convert("RGB")
        im.thumbnail((size, size))
        buf = BytesIO()
        im.save(buf, "JPEG", quality=72)
        return buf.getvalue()
    except Exception:
        return b""


def export_phone(rel: dict, out_path: Path | None = None, *, root: Path | None = None,
                 thumbnails: bool = True) -> dict:
    """The JSON the phone page reads: open items with chips, text, a thumbnail and the
    item's sha256. Nothing in it is a secret (the page is readable), so nothing in it
    grants anything: a phone tick only proposes (see import_ticks). The System chat
    publishes the file with the outreach-page pattern (plans/outreach-page/gen.py);
    ticks come back through ArtifactData."""
    root = root or repo_root()
    block = ensure_review(rel)
    items = []
    for item in block["items"].values():
        if item["state"] not in OPEN_STATES:
            continue
        v = item_view(rel, item)
        items.append({
            "id": v["id"], "label": v["label"], "kind": v["kind"], "area": v["area"],
            "state": v["state"], "gate": v["gate"], "version": v["version"],
            "supersedes": v["supersedes"], "note": v["note"], "made_by": v["made_by"],
            "created": v["created"], "sha256": item.get("sha256", ""), "name": v["name"],
            "chips": v["chips"], "text": v["text"], "proposed": item.get("proposed"),
            "thumbnail": thumbnail_data_uri(item, root) if thumbnails else "",
        })
    items.sort(key=lambda x: (STATE_ORDER.get(x["state"], 9), 0 if x["gate"] == "held" else 1, x["created"]))
    data = {
        "slug": rel["slug"],
        "title": release_title(rel),
        "generated": now_iso(),
        "actions": ["approve", "change", "drop"],
        "note": "Ticks save to the page db collection ticks as {tick_id, id, action, note, sha256, at}. "
                "The agent reads them back with import_ticks: a tick becomes a PROPOSAL on the item (its state "
                "does not move); nothing is approved, changed or dropped until Amir confirms locally "
                "(RM /review or the CLI confirm). A tick with another sha256 than the item's is refused; "
                "a tick_id already imported is ignored; a later valid tick replaces the earlier proposal. "
                "The page never posts, moves or deletes.",
        "items": items,
    }
    out_path = out_path or (root / "plans" / ("review-export-%s.json" % rel["slug"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def import_ticks(rel: dict, ticks: list, *, root: Path | None = None) -> list:
    """Phone ticks read back with ArtifactData: [{tick_id, id, action, note, sha256, at}].

    A phone tick never changes `state`. A valid one (known open item, sha256 equal to
    the bound hash AND to the file on disk, change with a note) fills item["proposed"]
    = {action, note, by: "phone", at, tick_id, ticked_at}; a later valid tick replaces an
    earlier proposal. The real step happens only locally through tick() / confirm()
    and records by "amir". Every tick_id goes into the block's consumed list (refused
    ones too), so a replayed tick is ignored. Returns [(tick_id, item_id, ok, message)]."""
    block = ensure_review(rel)
    consumed = block.setdefault("consumed_ticks", [])
    out = []
    for t in ticks:
        tick_id = str(t.get("tick_id", "") or "").strip()
        item_id = str(t.get("id", "") or "")
        action = str(t.get("action", "") or "")
        if not tick_id:
            out.append(("", item_id, False, "refused: tick without a tick_id"))
            continue
        if tick_id in consumed:
            out.append((tick_id, item_id, False, "ignored: already imported"))
            continue
        consumed.append(tick_id)                      # consumed even when refused: one look per tick
        if action not in TICK_ACTIONS:
            out.append((tick_id, item_id, False, "refused: action %r is not approve, change or drop" % action))
            continue
        try:
            item = get_item(rel, item_id)
        except ReviewError as e:
            out.append((tick_id, item_id, False, "refused: %s" % e))
            continue
        if item["state"] not in OPEN_STATES:
            out.append((tick_id, item_id, False, "refused: %s is %s" % (item_id, item["state"])))
            continue
        tick_hash = str(t.get("sha256", "") or "").strip().lower()
        bound = item.get("sha256") or ""
        if not tick_hash or tick_hash != bound:
            out.append((tick_id, item_id, False, "refused: tick hash %s does not match item %s"
                        % (tick_hash[:12] or "none", bound[:12])))
            continue
        current = current_hash(item, root)
        if current != bound:
            if current is not None:
                _flag_changed(item, current, by="code", via="phone")
            out.append((tick_id, item_id, False, "refused: file changed since review" if current else "refused: file missing"))
            continue
        note = str(t.get("note", "") or "").strip()
        if action == "change" and not note:
            out.append((tick_id, item_id, False, "refused: change needs a note"))
            continue
        item["proposed"] = {"action": action, "note": note, "by": "phone", "at": now_iso(),
                            "tick_id": tick_id, "ticked_at": str(t.get("at", "") or "")}
        out.append((tick_id, item_id, True, "proposed %s, confirm locally" % action))
    block["updated_at"] = now_iso()
    return out


def confirm(rel: dict, item_id: str, *, action: str = "", note: str = "", by: str = "amir",
            root: Path | None = None) -> dict:
    """The local step after a phone proposal (System chat, on Amir's words): a tick()
    with the item's bound hash. Without --action the proposed action is taken."""
    item = get_item(rel, item_id)
    proposed = item.get("proposed") or {}
    action = action or proposed.get("action", "")
    if not action:
        raise ReviewError("%s has no proposal and no action was named" % item_id)
    return tick(rel, item_id, action, by=by, via="chat", note=note or proposed.get("note", ""),
                sha256=item.get("sha256", ""), root=root)


# ---------------------------------------------------------------------------
# Demo release (page screenshot, never a real release)
# ---------------------------------------------------------------------------

DEMO_SLUG = "review-demo-single"


def _ffmpeg_exe() -> str | None:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def demo_release(media_dir: Path, *, with_media: bool = True) -> dict:
    """A throwaway release with one of each kind, its media written into media_dir
    (a 2 s silent clip, a 3 s clip with tone, a 4000 px cover). Paths are absolute so
    nothing in releases/ is touched. Returns the release dict (not saved)."""
    from release_manager.models import new_release_dict, new_track_dict
    media_dir = Path(media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    rel = new_release_dict("Review Demo", "Single", "2026-12-18", genre_primary="Post-punk")
    rel["slug"] = DEMO_SLUG
    rel["tracks"] = [new_track_dict(1, "Review Demo", bpm=112, duration="3:40")]
    reel_a = media_dir / "reel-v1.mp4"
    reel_b = media_dir / "reel-v2.mp4"
    canvas = media_dir / "canvas.mp4"
    cover = media_dir / "cover.png"
    if with_media:
        ff = _ffmpeg_exe()
        if ff:
            base = [ff, "-v", "error", "-y"]
            subprocess.run(base + ["-f", "lavfi", "-i", "color=c=0x0F0D0C:s=1080x1920:r=30:d=3",
                                   "-f", "lavfi", "-i", "sine=frequency=220:duration=3",
                                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(reel_a)],
                           capture_output=True, timeout=120)
            subprocess.run(base + ["-f", "lavfi", "-i", "color=c=0x1a1a1a:s=1080x1920:r=30:d=3",
                                   "-f", "lavfi", "-i", "sine=frequency=330:duration=3",
                                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(reel_b)],
                           capture_output=True, timeout=120)
            subprocess.run(base + ["-f", "lavfi", "-i", "color=c=0x0F0D0C:s=1080x1920:r=30:d=2",
                                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(canvas)],
                           capture_output=True, timeout=120)
        try:
            from PIL import Image
            Image.new("RGB", (4000, 4000), (15, 13, 12)).save(cover)
        except Exception:
            pass
    at = now_iso()
    r1 = add_item(rel, new_item("render", "reel, 9:16, cut 1", path=str(reel_a), area="socials",
                                destination=["reel_instagram", "shorts_youtube"], at=at,
                                text_boxes=[[200, 100, 600, 120]]))
    submit(rel, r1["id"])
    r2 = add_item(rel, new_item("render", "reel, 9:16, cut 2 (title moved down)", path=str(reel_b),
                                area="socials", destination=["reel_instagram", "shorts_youtube"],
                                supersedes=r1["id"], at=at, text_boxes=[[200, 900, 600, 120]]))
    submit(rel, r2["id"])
    c1 = add_item(rel, new_item("canvas", "Spotify Canvas loop", path=str(canvas), area="release",
                                destination=["canvas_vertical_spotify"], at=at))
    submit(rel, c1["id"])
    cv = add_item(rel, new_item("cover", "cover, 4000 px", path=str(cover), area="release",
                                destination=["release_spotify"], at=at))
    submit(rel, cv["id"])
    cap = add_item(rel, new_item("caption", "IG caption, release day",
                                 text="Hi all, Review Demo is out today. Mixed and mastered at @ambertone.studios. Hope you will like it.\n\n#postpunk #newwave #darkwave",
                                 area="socials", at=at))
    submit(rel, cap["id"])
    bad = add_item(rel, new_item("post-draft", "story text with an em-dash and a stranger",
                                 text="Out now — thanks @someone_unknown for the shot", area="socials", at=at))
    submit(rel, bad["id"])
    tick(rel, cv["id"], "approve", note="", sha256=cv["sha256"])
    tick(rel, c1["id"], "change", note="loop point jumps, make it 4 s")
    import_ticks(rel, [{"tick_id": "demo-phone-1", "id": cap["id"], "action": "approve",
                        "sha256": cap["sha256"], "at": at}])
    return rel


# ---------------------------------------------------------------------------
# CLI (the agent's side; nothing here posts or moves a file)
# ---------------------------------------------------------------------------

def _cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Review flow: add, check, tick, export (no file moves).")
    ap.add_argument("--demo", action="store_true", help="build a throwaway demo release in a temp dir and print its path")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="add one draft item and run its checks")
    a.add_argument("slug")
    a.add_argument("--kind", required=True, choices=KINDS)
    a.add_argument("--label", required=True)
    a.add_argument("--path", default="")
    a.add_argument("--text", default=None)
    a.add_argument("--area", default="socials", choices=AREAS)
    a.add_argument("--dest", action="append", default=[], help="preset key, repeatable")
    a.add_argument("--supersedes", default=None)
    a.add_argument("--made-by", default="claude")
    c = sub.add_parser("check", help="re-run the checks on every open item (or one)")
    c.add_argument("slug")
    c.add_argument("item", nargs="?")
    e = sub.add_parser("export", help="write plans/review-export-<slug>.json for the phone page")
    e.add_argument("slug")
    e.add_argument("--no-thumbs", action="store_true")
    u = sub.add_parser("used", help="record Amir's words that an approved item went out")
    u.add_argument("slug")
    u.add_argument("item")
    u.add_argument("--where", required=True)
    u.add_argument("--ref", default="")
    cf = sub.add_parser("confirm", help="Amir's words on a phone proposal: the local tick (approve / change / drop)")
    cf.add_argument("slug")
    cf.add_argument("item")
    cf.add_argument("--action", default="", choices=("", "approve", "change", "drop"))
    cf.add_argument("--note", default="")
    ls = sub.add_parser("list", help="print the items of one release")
    ls.add_argument("slug")
    args = ap.parse_args(argv)

    if args.demo:
        d = Path(tempfile.mkdtemp(prefix="review-demo-"))
        rel = demo_release(d / "media")
        out = d / (DEMO_SLUG + ".json")
        out.write_text(json.dumps(rel, indent=2, ensure_ascii=False))
        print("demo release written to %s (media in %s); open /review?demo=1 for the in-memory version" % (out, d / "media"))
        return 0
    if not args.cmd:
        ap.print_help()
        return 1
    rel = storage.load_release(args.slug)
    if rel is None:
        print("no release %s" % args.slug, file=sys.stderr)
        return 2
    try:
        if args.cmd == "add":
            item = add_item(rel, new_item(args.kind, args.label, path=args.path, text=args.text, area=args.area,
                                          destination=args.dest, supersedes=args.supersedes, made_by=args.made_by))
            submit(rel, item["id"])
            save_release_review(rel)
            print("%s %s %s gate=%s" % (item["id"], item["state"], item["label"], gate(item)))
            for ch in item["checks"]:
                print("  %-18s %-5s %s" % (ch["name"], {True: "pass", False: "FAIL", None: "na"}[ch["pass"]], ch["reason"]))
        elif args.cmd == "check":
            ids = [args.item] if args.item else [i for i, it in ensure_review(rel)["items"].items() if it["state"] in OPEN_STATES]
            for item_id in ids:
                item = get_item(rel, item_id)
                run_checks(item)
                print("%s %s gate=%s" % (item_id, item["state"], gate(item)))
            refresh(rel)
            save_release_review(rel)
        elif args.cmd == "export":
            data = export_phone(rel, thumbnails=not args.no_thumbs)
            print("plans/review-export-%s.json: %d open item(s)" % (rel["slug"], len(data["items"])))
        elif args.cmd == "confirm":
            item = confirm(rel, args.item, action=args.action, note=args.note)
            save_release_review(rel)
            print("%s %s (by amir, via chat)" % (args.item, item["state"]))
        elif args.cmd == "used":
            mark_used(rel, args.item, where=args.where, ref=args.ref)
            save_release_review(rel)
            print("%s used on %s" % (args.item, args.where))
        elif args.cmd == "list":
            for item in ensure_review(rel)["items"].values():
                print("%s  %-10s %-10s v%d  %s  %s" % (item["id"], item["state"], item["kind"], item.get("version", 1),
                                                     gate(item), item["label"]))
    except ReviewError as e:
        print("refused: %s" % e, file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
