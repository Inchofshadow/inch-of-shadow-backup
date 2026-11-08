"""
release_manager/clips.py
-------------------------
The clip pack per song (System 79, card S10, 2026-11-06).

A release file carries a "clips" block: per track the TikTok 60 s window, the reel
hook bar (the fixed audio section), the Spotify Canvas loop, the YouTube Shorts
Preview window and a used_in log. Everything is a timecode in seconds; the masters
are exported silent and the song is attached in each app, so no audio files live here.

Spec and sources: plans/clip-pack-schema.md
(research: plans/strategy/research-clip-pack-2026-11-06.md).

Shape, inside releases/<slug>.json:

    "clips": {
        "version": 1,
        "tracks": [
            {
                "number": 1,
                "tiktok": {"start": 72.0},
                "hook_bar": {"start": 72.0, "length": 3.5},
                "canvas": {"length": 5.0, "source": "", "height_px": null, "confirmed": false},
                "shorts_preview": {"start": null, "duration": null, "start_date": ""},
                "used_in": [
                    {"platform": "instagram", "post": "https://...", "date": "2026-11-20",
                     "cut": "A1", "kind": "post"}
                ]
            }
        ]
    }
"""

from __future__ import annotations

import copy
import re
import shutil
from datetime import datetime
from pathlib import Path

from release_manager import storage

CLIPS_VERSION = 1

TIKTOK_WINDOW_S = 60.0            # Symphonic delivers one 60 s clip; start in HH:MM:SS
HOOK_MIN_S, HOOK_MAX_S = 0.5, 60.0
CANVAS_MIN_S, CANVAS_MAX_S = 3.0, 8.0           # Spotify Canvas guidelines
CANVAS_MIN_PX, CANVAS_MAX_PX = 720, 1080        # height, 9:16
PREVIEW_MIN_S, PREVIEW_MAX_S = 30.0, 60.0       # DDEX ERN 3.6 Shorts Preview duration

PLATFORMS = ("tiktok", "instagram", "youtube")
KINDS = ("post", "trial", "repost", "replace_audio")
UPLOAD_KINDS = ("post", "trial")                # a fresh upload of a cut; repost / replace_audio reuse one

CANVAS_RULES = ("silent, 9:16, 720 to 1080 px tall, no talking or singing, "
                "no links, no handle, no other brands, no sting")


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def default_track_clips(number: int) -> dict:
    return {
        "number": int(number),
        "tiktok": {"start": None},
        "hook_bar": {"start": None, "length": None},
        "canvas": {"length": None, "source": "", "height_px": None, "confirmed": False},
        "shorts_preview": {"start": None, "duration": None, "start_date": ""},
        "used_in": [],
    }


def _fill(block: dict, number: int) -> dict:
    """A track block with every key present (missing keys get defaults, nothing removed)."""
    out = default_track_clips(number)
    for key in ("tiktok", "hook_bar", "canvas", "shorts_preview"):
        sub = block.get(key)
        if isinstance(sub, dict):
            out[key].update(sub)
    used = block.get("used_in")
    out["used_in"] = [dict(u) for u in used] if isinstance(used, list) else []
    for key, val in block.items():
        if key not in out:
            out[key] = val
    return out


def ensure_clips(rel: dict) -> dict:
    """Make sure rel["clips"] exists with one block per track, in track order. Mutates rel."""
    clips = rel.get("clips")
    if not isinstance(clips, dict):
        clips = {}
    clips.setdefault("version", CLIPS_VERSION)
    existing = {}
    for b in clips.get("tracks") or []:
        if isinstance(b, dict) and "number" in b:
            existing[int(b["number"])] = b
    blocks = []
    for t in rel.get("tracks") or []:
        n = int(t.get("number", 0))
        blocks.append(_fill(existing.get(n, {}), n))
    clips["tracks"] = blocks
    rel["clips"] = clips
    return clips


def renumber_clips(rel: dict, mapping: dict) -> None:
    """Move clip blocks with their tracks after a renumber. `mapping` is old track
    number -> new number; a block whose track is gone is dropped. Mutates rel.
    Gate review 2026-11-07: track_delete renumbered tracks only, so clip data moved
    to the wrong track and the last block was lost."""
    clips = rel.get("clips")
    if not isinstance(clips, dict):
        return
    out = []
    for b in clips.get("tracks") or []:
        if not isinstance(b, dict) or "number" not in b:
            continue
        new = mapping.get(int(b["number"]))
        if new is not None:
            out.append(dict(b, number=new))
    clips["tracks"] = sorted(out, key=lambda b: b["number"])


def track_clips(rel: dict, number: int) -> dict | None:
    """The clip block of one track (None when the track does not exist)."""
    for b in ensure_clips(rel)["tracks"]:
        if b["number"] == int(number):
            return b
    return None


# ---------------------------------------------------------------------------
# Parsing (seconds, never frames)
# ---------------------------------------------------------------------------

_TC = re.compile(r"^(?:(\d{1,3}):)?(\d{1,2}(?:\.\d+)?)$")


def parse_seconds(text) -> float | None:
    """'72', '72.5', '1:12', '1:12.5' -> seconds. Empty -> None. Bad -> ValueError."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    s = str(text).strip()
    if not s:
        return None
    m = _TC.match(s)
    if not m:
        raise ValueError(f"not a time: {s!r} (use seconds like 72.5 or m:ss like 1:12.5)")
    minutes = int(m.group(1)) if m.group(1) else 0
    secs = float(m.group(2))
    if m.group(1) and secs >= 60:
        raise ValueError(f"not a time: {s!r} (seconds part must be under 60)")
    return minutes * 60 + secs


def fmt_seconds(value) -> str:
    """72.5 -> '1:12.5'; None -> ''."""
    if value is None or value == "":
        return ""
    v = float(value)
    m = int(v // 60)
    s = v - m * 60
    txt = f"{s:04.1f}" if m else f"{s:.1f}"
    return f"{m}:{txt}" if m else txt


def _hms(value) -> str:
    """Seconds -> HH:MM:SS (the Symphonic Clip Start Time format, whole seconds)."""
    if value is None:
        return ""
    v = int(float(value))
    return f"{v // 3600:02d}:{(v % 3600) // 60:02d}:{v % 60:02d}"


def track_duration_seconds(track: dict | None) -> float | None:
    """The track's 'duration' field (M:SS) as seconds, None when unset or odd."""
    if not track:
        return None
    try:
        return parse_seconds(track.get("duration", ""))
    except ValueError:
        return None


def _date_ok(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _num(value, what: str, errors: list, lo=None, hi=None, allow_none=True):
    if value is None or value == "":
        if not allow_none:
            errors.append(f"{what}: missing")
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        errors.append(f"{what}: not a number ({value!r})")
        return None
    if lo is not None and v < lo:
        errors.append(f"{what}: {fmt_seconds(v)} is below {fmt_seconds(lo)}")
    if hi is not None and v > hi:
        errors.append(f"{what}: {fmt_seconds(v)} is above {fmt_seconds(hi)}")
    return v


def validate_used_in(entries: list, new: dict | None = None) -> list[str]:
    """Errors in a used_in list; with `new`, also whether adding it would break the never-twice rule."""
    errors: list[str] = []
    rows = list(entries or [])
    if new is not None:
        rows.append(new)
    seen: set[tuple[str, str]] = set()
    for i, u in enumerate(rows, 1):
        tag = "new row" if (new is not None and i == len(rows)) else f"used_in row {i}"
        if not isinstance(u, dict):
            errors.append(f"{tag}: not a record")
            continue
        platform = str(u.get("platform", "")).strip().lower()
        kind = str(u.get("kind", "post") or "post").strip().lower()
        cut = str(u.get("cut", "")).strip()
        date = str(u.get("date", "")).strip()
        post = str(u.get("post", "")).strip()
        if platform not in PLATFORMS:
            errors.append(f"{tag}: platform must be one of {', '.join(PLATFORMS)} (got {platform!r})")
        if kind not in KINDS:
            errors.append(f"{tag}: kind must be one of {', '.join(KINDS)} (got {kind!r})")
        if not cut:
            errors.append(f"{tag}: cut label or hash is missing (a different first frame is a different cut)")
        if not date or not _date_ok(date):
            errors.append(f"{tag}: date must be YYYY-MM-DD (got {date!r})")
        if not post:
            errors.append(f"{tag}: post id or URL is missing")
        if platform in PLATFORMS and cut and kind in UPLOAD_KINDS:
            key = (platform, cut)
            if key in seen:
                errors.append(f"{tag}: cut {cut!r} was already uploaded to {platform} "
                              "(never twice on one platform; make a new cut with a different first frame, "
                              "or log a repost / replace_audio)")
            seen.add(key)
    return errors


def validate_track_clips(block: dict, track: dict | None = None, release_date: str = "") -> list[str]:
    """Every rule of the spec for one track block. Empty list = valid."""
    errors: list[str] = []
    b = _fill(block, block.get("number", 0))
    dur = track_duration_seconds(track)

    tt = _num(b["tiktok"].get("start"), "TikTok start", errors, lo=0)
    if tt is not None and dur is not None and tt >= dur:
        errors.append(f"TikTok start: {fmt_seconds(tt)} is past the track end ({fmt_seconds(dur)})")

    hs = _num(b["hook_bar"].get("start"), "hook bar start", errors, lo=0)
    hl = _num(b["hook_bar"].get("length"), "hook bar length", errors, lo=HOOK_MIN_S, hi=HOOK_MAX_S)
    if hs is not None and hl is None:
        errors.append("hook bar length: missing")
    if hs is None and hl is not None:
        errors.append("hook bar start: missing")
    if hs is not None and hl is not None:
        if tt is not None and (hs < tt or hs + hl > tt + TIKTOK_WINDOW_S):
            errors.append(f"hook bar {fmt_seconds(hs)} + {hl:g} s must sit inside the TikTok window "
                          f"{fmt_seconds(tt)} to {fmt_seconds(tt + TIKTOK_WINDOW_S)}")
        if dur is not None and hs + hl > dur:
            errors.append(f"hook bar ends after the track end ({fmt_seconds(dur)})")

    cv = b["canvas"]
    _num(cv.get("length"), "Canvas length", errors, lo=CANVAS_MIN_S, hi=CANVAS_MAX_S)
    h = cv.get("height_px")
    if h not in (None, ""):
        try:
            hv = int(h)
            if hv < CANVAS_MIN_PX or hv > CANVAS_MAX_PX:
                errors.append(f"Canvas height: {hv} px is outside {CANVAS_MIN_PX} to {CANVAS_MAX_PX}")
        except (TypeError, ValueError):
            errors.append(f"Canvas height: not a whole number ({h!r})")

    sp = b["shorts_preview"]
    ps = _num(sp.get("start"), "Shorts Preview start", errors, lo=0)
    pd = _num(sp.get("duration"), "Shorts Preview duration", errors, lo=PREVIEW_MIN_S, hi=PREVIEW_MAX_S)
    if ps is not None and pd is None:
        errors.append("Shorts Preview duration: missing")
    if ps is None and pd is not None:
        errors.append("Shorts Preview start: missing")
    if ps is not None and pd is not None and dur is not None and ps + pd > dur:
        errors.append(f"Shorts Preview ends after the track end ({fmt_seconds(dur)})")
    sd = str(sp.get("start_date") or "").strip()
    if sd:
        if not _date_ok(sd):
            errors.append(f"Shorts Preview start date: must be YYYY-MM-DD (got {sd!r})")
        elif release_date and _date_ok(release_date) and sd >= release_date:
            errors.append(f"Shorts Preview start date {sd} must be before the release date {release_date}")

    errors.extend(validate_used_in(b["used_in"]))
    return errors


def validate_clips(rel: dict) -> list[str]:
    """All tracks; each message is prefixed with the track number."""
    out: list[str] = []
    tracks = {int(t.get("number", 0)): t for t in rel.get("tracks") or []}
    clips = rel.get("clips") or {}
    for b in clips.get("tracks") or []:
        n = int(b.get("number", 0))
        for e in validate_track_clips(b, tracks.get(n), rel.get("release_date", "")):
            out.append(f"track {n}: {e}")
    return out


# ---------------------------------------------------------------------------
# Form handling (the release page edit form; values in seconds)
# ---------------------------------------------------------------------------

FORM_FIELDS = ("tiktok_start", "hook_start", "hook_length", "canvas_length", "canvas_source",
               "canvas_height", "canvas_confirmed", "preview_start", "preview_duration",
               "preview_start_date")


def block_to_form(block: dict) -> dict:
    """Stored block -> the strings the edit form shows."""
    b = _fill(block, block.get("number", 0))
    return {
        "tiktok_start": fmt_seconds(b["tiktok"].get("start")),
        "hook_start": fmt_seconds(b["hook_bar"].get("start")),
        "hook_length": "" if b["hook_bar"].get("length") is None else f"{float(b['hook_bar']['length']):g}",
        "canvas_length": "" if b["canvas"].get("length") is None else f"{float(b['canvas']['length']):g}",
        "canvas_source": b["canvas"].get("source") or "",
        "canvas_height": "" if b["canvas"].get("height_px") in (None, "") else str(b["canvas"]["height_px"]),
        "canvas_confirmed": bool(b["canvas"].get("confirmed")),
        "preview_start": fmt_seconds(b["shorts_preview"].get("start")),
        "preview_duration": ("" if b["shorts_preview"].get("duration") is None
                             else f"{float(b['shorts_preview']['duration']):g}"),
        "preview_start_date": b["shorts_preview"].get("start_date") or "",
    }


def form_to_block(form: dict, current: dict) -> tuple[dict, list[str]]:
    """Form strings -> a candidate block (used_in kept from `current`). Returns (block, parse errors)."""
    errors: list[str] = []
    b = copy.deepcopy(_fill(current, current.get("number", 0)))

    def sec(name, what):
        try:
            return parse_seconds(form.get(name, ""))
        except ValueError as e:
            errors.append(f"{what}: {e}")
            return None

    b["tiktok"]["start"] = sec("tiktok_start", "TikTok start")
    b["hook_bar"]["start"] = sec("hook_start", "hook bar start")
    b["hook_bar"]["length"] = sec("hook_length", "hook bar length")
    b["canvas"]["length"] = sec("canvas_length", "Canvas length")
    b["canvas"]["source"] = str(form.get("canvas_source", "")).strip()
    h = str(form.get("canvas_height", "")).strip()
    if h:
        try:
            b["canvas"]["height_px"] = int(h)
        except ValueError:
            errors.append(f"Canvas height: not a whole number ({h!r})")
            b["canvas"]["height_px"] = None
    else:
        b["canvas"]["height_px"] = None
    b["canvas"]["confirmed"] = str(form.get("canvas_confirmed", "")).strip().lower() in ("1", "on", "true", "yes")
    b["shorts_preview"]["start"] = sec("preview_start", "Shorts Preview start")
    b["shorts_preview"]["duration"] = sec("preview_duration", "Shorts Preview duration")
    b["shorts_preview"]["start_date"] = str(form.get("preview_start_date", "")).strip()
    return b, errors


def update_track_clips(rel: dict, number: int, form: dict) -> list[str]:
    """Apply the edit form to one track. Returns errors; the release is only changed when empty."""
    current = track_clips(rel, number)
    if current is None:
        return [f"track {number}: no such track"]
    track = next((t for t in rel.get("tracks") or [] if int(t.get("number", 0)) == int(number)), None)
    block, errors = form_to_block(form, current)
    if errors:
        return errors
    errors = validate_track_clips(block, track, rel.get("release_date", ""))
    if errors:
        return errors
    current.update(block)
    return []


def used_in_entry(form: dict) -> dict:
    return {
        "platform": str(form.get("platform", "")).strip().lower(),
        "post": str(form.get("post", "")).strip(),
        "date": str(form.get("date", "")).strip(),
        "cut": str(form.get("cut", "")).strip(),
        "kind": str(form.get("kind", "post") or "post").strip().lower(),
    }


def add_used_in(rel: dict, number: int, entry: dict) -> list[str]:
    """Append one used_in row. Refuses a second upload of the same cut on the same platform."""
    current = track_clips(rel, number)
    if current is None:
        return [f"track {number}: no such track"]
    new = used_in_entry(entry)
    errors = validate_used_in(current["used_in"], new)
    if errors:
        return errors
    current["used_in"].append(new)
    return []


def remove_used_in(rel: dict, number: int, index: int) -> list[str]:
    """Drop one used_in row by its 0-based index."""
    current = track_clips(rel, number)
    if current is None:
        return [f"track {number}: no such track"]
    rows = current["used_in"]
    if not (0 <= index < len(rows)):
        return [f"track {number}: no used_in row {index + 1}"]
    rows.pop(index)
    return []


# ---------------------------------------------------------------------------
# View model for the release page
# ---------------------------------------------------------------------------

def summary(block: dict, track: dict | None = None) -> dict:
    """Readable lines for the current values of one track."""
    b = _fill(block, block.get("number", 0))
    tt = b["tiktok"].get("start")
    hs, hl = b["hook_bar"].get("start"), b["hook_bar"].get("length")
    cv, sp = b["canvas"], b["shorts_preview"]
    tiktok = (f"{fmt_seconds(tt)} to {fmt_seconds(float(tt) + TIKTOK_WINDOW_S)} "
              f"(Symphonic Clip Start Time {_hms(tt)})") if tt is not None else "not set"
    hook = (f"{fmt_seconds(hs)} for {float(hl):g} s (to {fmt_seconds(float(hs) + float(hl))})"
            if hs is not None and hl is not None else "not set")
    canvas = "not set"
    if cv.get("length") is not None:
        canvas = f"{float(cv['length']):g} s loop"
        if cv.get("height_px"):
            canvas += f", {cv['height_px']} px tall"
        if cv.get("source"):
            canvas += f", from {cv['source']}"
        canvas += ", rules confirmed" if cv.get("confirmed") else ", rules not confirmed yet"
    preview = "not set (only if Symphonic delivers it)"
    if sp.get("start") is not None and sp.get("duration") is not None:
        preview = f"{fmt_seconds(sp['start'])} for {float(sp['duration']):g} s"
        if sp.get("start_date"):
            preview += f", live from {sp['start_date']}"
    return {"tiktok": tiktok, "hook_bar": hook, "canvas": canvas, "shorts_preview": preview,
            "title": (track or {}).get("title", ""), "number": b["number"]}


def page_rows(rel: dict) -> list[dict]:
    """One row per track for the Clip pack block: block, form strings, summary, used_in."""
    tracks = {int(t.get("number", 0)): t for t in rel.get("tracks") or []}
    rows = []
    for b in ensure_clips(rel)["tracks"]:
        t = tracks.get(b["number"])
        rows.append({"number": b["number"], "title": (t or {}).get("title", f"Track {b['number']}"),
                     "block": b, "form": block_to_form(b), "summary": summary(b, t),
                     "used_in": list(b["used_in"])})
    return rows


# ---------------------------------------------------------------------------
# Load / save (every other key of the release file stays as it is)
# ---------------------------------------------------------------------------

def load_clips(slug: str) -> dict | None:
    """The clips block of a release, with defaults filled; None when the release is missing."""
    rel = storage.load_release(slug)
    if rel is None:
        return None
    return ensure_clips(rel)


def backup_release_file(slug: str) -> Path | None:
    """One safety copy per day before the clips block first changes a release file."""
    src = storage.release_path(slug)
    if not src.exists():
        return None
    dst = src.with_name(f"{slug}.bak.{datetime.now().strftime('%Y%m%d')}_clips.json")
    if not dst.exists():
        shutil.copy2(src, dst)
    return dst


def save_clips(slug: str, clips: dict) -> Path | None:
    """Write a clips block into a release file, re-reading the file so nothing else is lost."""
    rel = storage.load_release(slug)
    if rel is None:
        return None
    backup_release_file(slug)
    rel["clips"] = copy.deepcopy(clips)
    ensure_clips(rel)
    return storage.save_release(rel)


def save_release_clips(rel: dict) -> Path:
    """Save a release dict whose clips block was edited in place (backup first)."""
    backup_release_file(rel["slug"])
    ensure_clips(rel)
    return storage.save_release(rel)
