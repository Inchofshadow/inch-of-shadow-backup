"""
video_resizer.py
-----------------
Takes one master video and exports correctly sized/trimmed versions
for every music-artist platform.

Requires: pip install imageio-ffmpeg

Supported platforms:
    Instagram   — Reel (9:16), Story (9:16), Post square (1:1), Post portrait (4:5)
    YouTube     — Regular (16:9), Shorts (9:16)
    Spotify     — Canvas square (1:1), Canvas vertical (9:16)
    TikTok      — Video (9:16)

Usage:
    python3 video_resizer.py videos/promo.mp4
    python3 video_resizer.py videos/promo.mp4 --focal top
    python3 video_resizer.py videos/promo.mp4 --only spotify --trim 2 8
    python3 video_resizer.py videos/promo.mp4 --only instagram --focal top
    python3 video_resizer.py --list
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

# ---------------------------------------------------------------------------
# ffmpeg binary (bundled by imageio-ffmpeg)
# ---------------------------------------------------------------------------

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    print("Error: imageio-ffmpeg not installed. Run: pip install imageio-ffmpeg")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Export specifications
# (template, width, height, category, platform, duration_max, duration_min, audio, fps, notes)
#   fps: target frame rate (None = keep source fps)
# Sizes and caps checked against the platforms' own pages on 2026-09-20
# (board ticket Machine-07): an Instagram story clip can be 60s; feed video has no 60s
# cap any more (reels are recommended to new audiences up to 3 min); Spotify Canvas is
# vertical 9:16 only; YouTube accepts 1440p and 4K and recommends higher bitrates there.
# ---------------------------------------------------------------------------

VIDEO_EXPORTS = [
    # Instagram
    ("reel_instagram",          1080, 1920, "Instagram",      "instagram", 180, None, True,  30, "H.264, 9:16, 30fps, max 180s"),
    ("story_instagram",         1080, 1920, "Instagram",      "instagram",  60, None, True,  30, "H.264, 9:16, 30fps, max 60s per clip"),
    ("post_square_instagram",   1080, 1080, "Instagram",      "instagram", 180, None, True,  30, "H.264, 1:1, 30fps, max 180s"),
    ("post_portrait_instagram", 1080, 1350, "Instagram",      "instagram", 180, None, True,  30, "H.264, 4:5, 30fps, max 180s"),

    # YouTube
    ("video_youtube",           1920, 1080, "YouTube",        "youtube",  None, None, True,  None, "H.264, 16:9, source fps"),
    ("video_youtube_1440",      2560, 1440, "YouTube",        "youtube",  None, None, True,  None, "H.264, 16:9, 1440p, source fps, only from a source that large"),
    ("video_youtube_4k",        3840, 2160, "YouTube",        "youtube",  None, None, True,  None, "H.264, 16:9, 4K, source fps, only from a source that large"),
    ("shorts_youtube",          1080, 1920, "YouTube",        "youtube",   180, None, True,  30, "H.264, 9:16, 30fps, max 180s"),

    # Spotify Canvas
    ("canvas_vertical_spotify", 1080, 1920, "Spotify Canvas", "spotify",     8,    3, False, 30, "H.264, 9:16, 30fps, 3-8s loop, no audio, <10MB"),

    # TikTok
    ("video_tiktok",            1080, 1920, "TikTok",         "tiktok",   180, None, True,  30, "H.264, 9:16, 30fps, max 180s"),
]

ALL_VIDEO_PLATFORMS = sorted({e[4] for e in VIDEO_EXPORTS})
REEL_SET = ("reel_instagram", "shorts_youtube", "video_tiktok")   # --reel: one piece, three platforms

# Presets that are only written when the source is at least that large. Upscaling adds
# nothing; a 1080p master gets the 1080p file only.
NO_UPSCALE = {"video_youtube_1440", "video_youtube_4k"}

DEFAULT_CRF = 18

FOCAL_CHOICES = [
    "center",
    "top", "bottom", "left", "right",
    "top-left", "top-right", "bottom-left", "bottom-right",
]

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

CANVAS_MAX_MB = 10.0


# ---------------------------------------------------------------------------
# Video probing
# ---------------------------------------------------------------------------

def probe_video(input_path: Path) -> dict:
    """Extract video metadata using ffmpeg -i (stderr parsing)."""
    cmd = [FFMPEG_BIN, "-i", str(input_path), "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    stderr = result.stderr

    info = {
        "width": 0, "height": 0, "duration": 0.0,
        "has_audio": False, "fps": 0.0, "codec": "",
        "pix_fmt": "", "audio_codec": "",
    }

    # Parse duration: Duration: HH:MM:SS.mm
    dur_match = re.search(r"Duration:\s+(\d+):(\d+):(\d+)\.(\d+)", stderr)
    if dur_match:
        h, m, s, cs = dur_match.groups()
        info["duration"] = int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 100

    # Parse video stream: Video: codec, ..., WxH
    vid_match = re.search(r"Video:\s+(\w+).*?,\s+(\d{2,5})x(\d{2,5})", stderr)
    if vid_match:
        info["codec"] = vid_match.group(1)
        info["width"] = int(vid_match.group(2))
        info["height"] = int(vid_match.group(3))
    pix_match = re.search(r"Video:\s+\w+[^\n]*?,\s+(yuvj?\d{3}p\d*\w*|rgb\w*|gbr\w*|nv\d+)", stderr)
    if pix_match:
        info["pix_fmt"] = pix_match.group(1)

    # Parse fps
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s+fps", stderr)
    if fps_match:
        info["fps"] = float(fps_match.group(1))

    # Check for audio stream
    aud_match = re.search(r"Audio:\s+(\w+)", stderr)
    if aud_match:
        info["has_audio"] = True
        info["audio_codec"] = aud_match.group(1)

    return info


# ---------------------------------------------------------------------------
# Encode helpers
# ---------------------------------------------------------------------------

def h264_level(width: int, height: int, fps: float | None) -> str:
    """Smallest H.264 level that carries this frame size and rate."""
    pixels = width * height
    rate = fps or 30
    if pixels <= 1920 * 1080 * 1.05:
        return "4.2"
    if pixels <= 2560 * 1440 * 1.05:
        return "5.0" if rate <= 30 else "5.1"
    return "5.1" if rate <= 30 else "5.2"


def can_passthrough(
    src: dict,
    target_w: int, target_h: int,
    fps: int | None,
    trim_start: float | None,
    trim_end: float | None,
    dur_max: float | None,
) -> bool:
    """True when the source already IS the platform file: same size, H.264, yuv420p,
    same frame rate, nothing to trim or cut. Then the picture is copied, not re-encoded,
    because every extra encode loses quality."""
    if (src["width"], src["height"]) != (target_w, target_h):
        return False
    if src.get("codec") != "h264" or src.get("pix_fmt") != "yuv420p":
        return False
    if fps is not None and abs(src["fps"] - fps) > 0.01:
        return False
    if trim_start or trim_end:
        return False
    if dur_max and src["duration"] > dur_max + 0.05:
        return False
    return True


def build_passthrough_cmd(
    input_path: Path,
    output_path: Path,
    src: dict,
    include_audio: bool,
    metadata: dict | None = None,
) -> list[str]:
    """Copy the video stream untouched; still strip source metadata and add faststart."""
    cmd = [FFMPEG_BIN, "-i", str(input_path), "-map", "0:v:0", "-c:v", "copy"]
    if include_audio and src["has_audio"]:
        cmd += ["-map", "0:a:0"]
        if src.get("audio_codec") == "aac":
            cmd += ["-c:a", "copy"]
        else:
            cmd += ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", "-map_metadata", "-1", "-map_chapters", "-1"]
    if metadata:
        from metadata_utils import build_ffmpeg_metadata_flags
        cmd += build_ffmpeg_metadata_flags(metadata)
    cmd += ["-y", str(output_path)]
    return cmd


def latest_render(project_dir: Path) -> Path:
    """Newest MP4 in a HyperFrames project's renders/ folder."""
    renders = Path(project_dir) / "renders"
    files = sorted(renders.glob("*.mp4"), key=lambda f: f.stat().st_mtime) if renders.is_dir() else []
    if not files:
        raise FileNotFoundError(f"No MP4 found in {renders}")
    return files[-1]


# ---------------------------------------------------------------------------
# Focal point crop computation (same logic as artwork_resizer.py)
# ---------------------------------------------------------------------------

def shape_of(w: int, h: int) -> str:
    """The aspect as the page names it: 1080x1920 -> '9:16'."""
    from math import gcd
    g = gcd(w, h)
    return f"{w // g}:{h // g}"


def picked_frame(frame: dict | None) -> dict | None:
    """A frame Amir dragged on the page, checked: centre cx, cy as fractions of the source,
    zoom z from 1 (the largest box of that shape) down to 0.25."""
    if not isinstance(frame, dict):
        return None
    try:
        cx, cy, z = (float(frame.get(k, d)) for k, d in (("cx", 0.5), ("cy", 0.5), ("z", 1.0)))
    except (TypeError, ValueError):
        return None
    clip = lambda v, lo, hi: max(lo, min(v, hi))
    return {"cx": clip(cx, 0.0, 1.0), "cy": clip(cy, 0.0, 1.0), "z": clip(z, 0.25, 1.0)}


def compute_crop_box(
    src_w: int, src_h: int,
    target_w: int, target_h: int,
    focal,
) -> tuple[tuple[int, int, int, int], int, int]:
    """Compute crop box matching target aspect ratio, honoring focal point.
    `focal` is a named point, or a picked frame {cx, cy, z} (see picked_frame).
    Returns (box, crop_w, crop_h) where box = (left, top, right, bottom).
    """
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    frame = picked_frame(focal) if isinstance(focal, dict) else None
    if frame:
        if src_ratio > target_ratio:
            base_w, base_h = src_h * target_ratio, src_h
        elif src_ratio < target_ratio:
            base_w, base_h = src_w, src_w / target_ratio
        else:
            base_w, base_h = src_w, src_h
        crop_w, crop_h = max(2, int(base_w * frame["z"])), max(2, int(base_h * frame["z"]))
        left = min(max(0, round(frame["cx"] * src_w - crop_w / 2)), src_w - crop_w)
        top = min(max(0, round(frame["cy"] * src_h - crop_h / 2)), src_h - crop_h)
        return (left, top, left + crop_w, top + crop_h), crop_w, crop_h
    if isinstance(focal, dict):
        focal = "center"

    if src_ratio > target_ratio:
        crop_w = int(src_h * target_ratio)
        crop_h = src_h
        if "left" in focal:
            left = 0
        elif "right" in focal:
            left = src_w - crop_w
        else:
            left = (src_w - crop_w) // 2
        box = (left, 0, left + crop_w, src_h)

    elif src_ratio < target_ratio:
        crop_w = src_w
        crop_h = int(src_w / target_ratio)
        if "top" in focal:
            top = 0
        elif "bottom" in focal:
            top = src_h - crop_h
        else:
            top = (src_h - crop_h) // 2
        box = (0, top, src_w, top + crop_h)

    else:
        crop_w, crop_h = src_w, src_h
        box = (0, 0, src_w, src_h)

    return box, crop_w, crop_h


# ---------------------------------------------------------------------------
# ffmpeg command builder
# ---------------------------------------------------------------------------

def build_ffmpeg_cmd(
    input_path: Path,
    output_path: Path,
    src_w: int, src_h: int,
    target_w: int, target_h: int,
    focal: str,
    trim_start: float | None,
    trim_end: float | None,
    include_audio: bool,
    crf: int = DEFAULT_CRF,
    fps: int | None = None,
    metadata: dict | None = None,
    src_fps: float | None = None,
) -> list[str]:
    """Build the ffmpeg command for one export."""
    box, crop_w, crop_h = compute_crop_box(src_w, src_h, target_w, target_h, focal)
    left, top = box[0], box[1]

    # Make crop dimensions even (H.264 requires even dimensions)
    crop_w = crop_w - (crop_w % 2)
    crop_h = crop_h - (crop_h % 2)

    vf = f"crop={crop_w}:{crop_h}:{left}:{top},scale={target_w}:{target_h}:flags=lanczos"

    cmd = [FFMPEG_BIN]

    # Trim (input-level seeking for speed)
    if trim_start is not None:
        cmd += ["-ss", str(trim_start)]
    if trim_end is not None:
        cmd += ["-to", str(trim_end)]

    cmd += ["-i", str(input_path)]

    # Video filters and codec
    cmd += [
        "-vf", vf,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level:v", h264_level(target_w, target_h, fps or src_fps),
        "-pix_fmt", "yuv420p",
        "-crf", str(crf),
        "-preset", "medium",
    ]

    # Frame rate (None = keep source fps)
    if fps is not None:
        cmd += ["-r", str(fps)]

    # Audio (48kHz sample rate for platform compatibility)
    if include_audio:
        cmd += ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    else:
        cmd += ["-an"]

    # Strip source metadata, then optionally add custom tags
    cmd += [
        "-movflags", "+faststart",
        "-map_metadata", "-1",   # strip GPS, camera, device tags from source
    ]
    if metadata:
        from metadata_utils import build_ffmpeg_metadata_flags
        cmd += build_ffmpeg_metadata_flags(metadata)
    cmd += [
        "-y",
        str(output_path),
    ]

    return cmd


# ---------------------------------------------------------------------------
# Single export
# ---------------------------------------------------------------------------

def export_video(
    input_path: Path,
    output_path: Path,
    src_info: dict,
    target_w: int, target_h: int,
    focal: str,
    trim_start: float | None,
    trim_end: float | None,
    include_audio: bool,
    crf: int = DEFAULT_CRF,
    fps: int | None = None,
    metadata: dict | None = None,
) -> tuple[float, list[str]]:
    """Export one video. Returns (size_kb, warnings_list)."""
    warnings = []

    cmd = build_ffmpeg_cmd(
        input_path, output_path,
        src_info["width"], src_info["height"],
        target_w, target_h, focal,
        trim_start, trim_end,
        include_audio and src_info["has_audio"],
        crf, fps,
        metadata=metadata,
        src_fps=src_info.get("fps"),
    )

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-300:]}")

    # Verify output is a valid video (catch silent corruption)
    verify = subprocess.run(
        [FFMPEG_BIN, "-v", "error", "-i", str(output_path), "-f", "null", "-"],
        capture_output=True, text=True, timeout=120,
    )
    if verify.stderr.strip():
        error_count = len(verify.stderr.strip().split("\n"))
        warnings.append(f"Output has {error_count} decode error(s) — may not play correctly")

    size_kb = output_path.stat().st_size / 1024
    return size_kb, warnings


def export_passthrough(
    input_path: Path,
    output_path: Path,
    src_info: dict,
    include_audio: bool,
    metadata: dict | None = None,
) -> tuple[float, list[str]]:
    """Write the platform file without re-encoding the picture."""
    cmd = build_passthrough_cmd(input_path, output_path, src_info, include_audio, metadata=metadata)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-300:]}")
    return output_path.stat().st_size / 1024, ["passthrough: source already fits, picture not re-encoded"]


# ---------------------------------------------------------------------------
# Spotify Canvas special handler (<5MB, CRF escalation)
# ---------------------------------------------------------------------------

def export_canvas(
    input_path: Path,
    output_path: Path,
    src_info: dict,
    target_w: int, target_h: int,
    focal: str,
    trim_start: float | None,
    trim_end: float | None,
    fps: int | None = 30,
    metadata: dict | None = None,
) -> tuple[float, list[str]]:
    """Export Spotify Canvas with file size constraint (<10MB)."""
    warnings = []
    crf = 23

    while crf <= 35:
        cmd = build_ffmpeg_cmd(
            input_path, output_path,
            src_info["width"], src_info["height"],
            target_w, target_h, focal,
            trim_start, trim_end,
            include_audio=False,
            crf=crf, fps=fps,
            metadata=metadata,
        )

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr[-300:]}")

        size_mb = output_path.stat().st_size / (1024 * 1024)

        if size_mb <= CANVAS_MAX_MB:
            if crf > 23:
                warnings.append(f"CRF raised to {crf} to fit under 10MB")
            return output_path.stat().st_size / 1024, warnings

        crf += 2

    warnings.append(f"File is {size_mb:.1f}MB — exceeds 10MB limit even at CRF {crf}")
    return output_path.stat().st_size / 1024, warnings


# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------

def process_video(
    input_path: Path,
    output_dir: Path,
    active_exports: list,
    focal: str,
    trim_start: float | None,
    trim_end: float | None,
    dry_run: bool = False,
    metadata: dict | None = None,
    crf: int = DEFAULT_CRF,
    frames: dict | None = None,
) -> list:
    """Process one video into all requested platform exports.
    `frames` maps a shape ('9:16') to the frame Amir picked for it; other shapes use `focal`.

    Returns list of tuples:
        [(filename, width, height, size_kb, duration_s, category, warnings), ...]
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Probe source
    src = probe_video(input_path)
    if src["width"] == 0:
        raise RuntimeError(f"Could not read video: {input_path}")
    if src["duration"] < 0.1:
        raise RuntimeError(f"Not a video file (no duration detected): {input_path.name}")

    stem = input_path.stem
    src_dur = src["duration"]

    print(f"\nSource: {input_path.name}")
    print(f"  Resolution: {src['width']}x{src['height']}")
    print(f"  Duration:   {src_dur:.1f}s")
    print(f"  FPS:        {src['fps']}")
    print(f"  Audio:      {'yes' if src['has_audio'] else 'no'}")
    print(f"  Focal:      {focal}")
    if metadata:
        meta_fields = [f for f in ("title", "artist", "copyright", "genre") if metadata.get(f)]
        print(f"  Metadata:   embedding {', '.join(meta_fields)}")
    print()

    results = []

    for export in active_exports:
        template, tw, th, category, platform, dur_max, dur_min, audio, fps, notes = export
        filename = f"{template}_{stem}.mp4"
        out_path = output_dir / filename
        frame = picked_frame((frames or {}).get(shape_of(tw, th)))
        where = frame or focal

        # Compute effective trim for this export
        eff_start = trim_start or 0.0
        eff_end = trim_end or src_dur

        # Clip to max duration
        segment_dur = eff_end - eff_start
        if dur_max and segment_dur > dur_max:
            eff_end = eff_start + dur_max

        actual_dur = eff_end - eff_start

        # Check minimum duration
        warnings = []
        if dur_min and actual_dur < dur_min:
            warnings.append(f"Source too short ({actual_dur:.1f}s < {dur_min}s min)")
            if not dry_run:
                print(f"  SKIP {filename} — {warnings[0]}")
                continue

        # Large YouTube presets only from a source that large (never upscale)
        if template in NO_UPSCALE and (src["width"] < tw or src["height"] < th):
            print(f"  SKIP {filename} -- source {src['width']}x{src['height']} is smaller than {tw}x{th}")
            continue

        # A forced frame rate that differs from the source duplicates or drops frames
        if fps is not None and src["fps"] and abs(src["fps"] - fps) > 0.5:
            warnings.append(
                f"source {src['fps']:g} fps converted to {fps} fps, motion may stutter; "
                f"render or shoot at {fps} fps"
            )

        passthrough = can_passthrough(src, tw, th, fps, trim_start, trim_end, dur_max)
        if frame and frame["z"] < 0.999:
            passthrough = False                                   # zoomed in: the picture changes

        if dry_run:
            if passthrough:
                notes = notes + "  [passthrough, no re-encode]"
            print(f"  [dry-run] {filename}  {tw}x{th}  {actual_dur:.1f}s  {notes}")
            results.append((filename, tw, th, 0, actual_dur, category, warnings))
            continue

        # Export
        print(f"  Exporting {filename} ({tw}x{th}, {actual_dur:.1f}s)...", end="", flush=True)

        is_canvas = "canvas" in template
        if is_canvas and passthrough and input_path.stat().st_size > CANVAS_MAX_MB * 1024 * 1024:
            passthrough = False  # too heavy for Canvas as is, let the size loop re-encode it

        if passthrough:
            size_kb, export_warnings = export_passthrough(
                input_path, out_path, src, audio, metadata=metadata,
            )
        elif is_canvas:
            size_kb, export_warnings = export_canvas(
                input_path, out_path, src, tw, th,
                where, eff_start, eff_end, fps,
                metadata=metadata,
            )
        else:
            size_kb, export_warnings = export_video(
                input_path, out_path, src, tw, th,
                where, eff_start, eff_end, audio, crf=crf, fps=fps,
                metadata=metadata,
            )

        warnings.extend(export_warnings)
        warn_str = f"  [{', '.join(warnings)}]" if warnings else ""
        size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        print(f" {size_str}{warn_str}")

        results.append((filename, tw, th, round(size_kb), actual_dur, category, warnings))

    return results


# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------

def print_summary(results: list, dry_run: bool = False):
    """Print a formatted summary table."""
    if not results:
        print("\nNo exports generated.")
        return

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Summary — {len(results)} export(s)")
    print("-" * 72)
    print(f"  {'File':<42} {'Resolution':>12} {'Duration':>10} {'Size':>10}")
    print("-" * 72)

    for r in results:
        fname, w, h, size_kb, dur, cat, warns = r
        size_str = f"{size_kb} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        if dry_run:
            size_str = "—"
        print(f"  {fname:<42} {w}x{h:>4}  {dur:>8.1f}s  {size_str:>10}")
        if warns:
            for w_msg in warns:
                label = "NOTE" if w_msg.startswith("passthrough") else "WARNING"
                print(f"    {label}: {w_msg}")

    print("-" * 72)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = ArgumentParser(
        description="Export video resized for all music platforms.",
        epilog=(
            f"Platforms: {', '.join(ALL_VIDEO_PLATFORMS)}\n"
            f"Focal points: {', '.join(FOCAL_CHOICES)}"
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("video", nargs="?", type=Path,
                        help="Path to source video (MP4, MOV, etc.)")
    parser.add_argument("--focal", choices=FOCAL_CHOICES, default="center",
                        metavar="POINT", help="Crop focal point (default: center)")
    parser.add_argument("--reel", action="store_true",
                        help="The source is a finished vertical piece for Reels, Shorts and TikTok: "
                             "export only those three (no square, 4:5, story or landscape crops). "
                             "One piece, three platforms (Formats-04).")
    parser.add_argument("--only", nargs="+", choices=ALL_VIDEO_PLATFORMS,
                        metavar="PLATFORM", help="Export only selected platforms")
    parser.add_argument("--trim", nargs=2, type=float, metavar=("START", "END"),
                        help="Trim window in seconds (e.g. --trim 5 13)")
    parser.add_argument("--list", action="store_true",
                        help="List all video export specs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be exported")
    parser.add_argument("--crf", type=int, default=DEFAULT_CRF, metavar="N",
                        help=f"H.264 quality for re-encoded files, lower is better "
                             f"(default {DEFAULT_CRF}; 14-16 for masters). Ignored for "
                             f"passthrough files and for Spotify Canvas.")
    parser.add_argument("--from-hyperframes", type=Path, metavar="DIR", dest="from_hyperframes",
                        help="Use the newest MP4 in DIR/renders as the source "
                             "(render it first with: npx hyperframes render . -q delivery).")
    parser.add_argument("--open", action="store_true",
                        help="Open output folder when done")
    # --- Metadata embedding (opt-in) ---
    parser.add_argument("--release", metavar="SLUG",
                        help="Embed metadata from a release JSON (e.g. --release fsd-single).")
    parser.add_argument("--title", metavar="TEXT", help="Embed title metadata.")
    parser.add_argument("--artist", metavar="TEXT", help="Embed artist metadata.")
    parser.add_argument("--copyright", metavar="TEXT", dest="copyright_text",
                        help="Embed copyright metadata.")
    parser.add_argument("--description", metavar="TEXT", help="Embed description metadata.")
    parser.add_argument("--genre", metavar="TEXT", help="Embed genre metadata.")
    return parser.parse_args()


def list_exports():
    """Print all export specifications."""
    print(f"\nVideo Resizer — {len(VIDEO_EXPORTS)} export specs\n")
    print(f"  {'Template':<30} {'Resolution':>12} {'FPS':>5} {'Max Dur':>10} {'Audio':>7} {'Platform':>10}")
    print("-" * 80)
    for e in VIDEO_EXPORTS:
        template, w, h, cat, plat, dur_max, dur_min, audio, fps, notes = e
        dur_str = f"{dur_max}s" if dur_max else "—"
        if dur_min:
            dur_str = f"{dur_min}-{dur_max}s"
        audio_str = "yes" if audio else "no"
        fps_str = str(fps) if fps else "src"
        print(f"  {template:<30} {w:>5}x{h:<5} {fps_str:>5} {dur_str:>10} {audio_str:>7} {plat:>10}")
    print()


def main():
    args = parse_args()

    if args.list:
        list_exports()
        return

    if args.from_hyperframes:
        try:
            args.video = latest_render(args.from_hyperframes)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
        print(f"  HyperFrames render: {args.video}")

    if not args.video:
        print("Error: provide a video path, --from-hyperframes DIR, or use --list")
        sys.exit(1)

    if not args.video.exists():
        print(f"Error: file not found: {args.video}")
        sys.exit(1)

    if args.video.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"Error: unsupported format: {args.video.suffix}")
        sys.exit(1)

    output_dir = Path("resized_video")
    active_exports = VIDEO_EXPORTS
    if args.reel:
        active_exports = [e for e in VIDEO_EXPORTS if e[0] in REEL_SET]
    if args.only:
        active_exports = [e for e in active_exports if e[4] in args.only]

    trim_start = args.trim[0] if args.trim else None
    trim_end = args.trim[1] if args.trim else None

    # Build metadata dict (opt-in -- None means strip all, existing behavior)
    metadata = None
    if args.release:
        from metadata_utils import metadata_from_release
        metadata = metadata_from_release(args.release)
        if metadata is None:
            print(f"Error: release '{args.release}' not found in releases/.")
            sys.exit(1)
        print(f"  Metadata source: release '{args.release}'")
    elif any(getattr(args, f, None) for f in ("title", "artist", "copyright_text", "description", "genre")):
        from metadata_utils import metadata_from_flags
        metadata = metadata_from_flags(
            title=args.title or "",
            artist=args.artist or "",
            copyright_text=args.copyright_text or "",
            description=args.description or "",
            genre=args.genre or "",
        )
        print("  Metadata source: CLI flags")

    results = process_video(
        args.video, output_dir, active_exports,
        args.focal, trim_start, trim_end, args.dry_run,
        metadata=metadata, crf=args.crf,
    )

    print_summary(results, args.dry_run)

    if args.open and not args.dry_run:
        subprocess.run(["open", str(output_dir)])


if __name__ == "__main__":
    main()
