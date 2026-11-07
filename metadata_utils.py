"""
metadata_utils.py
-----------------
Shared metadata embedding utilities for artwork and video resizers.

Provides opt-in metadata embedding -- when metadata=None, nothing is called
and existing resizer behavior (strip all metadata) is unchanged.

No GPS, camera, lens, or device metadata is ever written.
"""

from __future__ import annotations

import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Metadata dict structure
# ---------------------------------------------------------------------------
# {
#     "title":       str,   # track / release title
#     "artist":      str,   # artist name
#     "copyright":   str,   # e.g. "2026 Inch of Shadow"
#     "description": str,   # freeform description
#     "genre":       str,   # e.g. "Dark Disco / Acid"
#     "date":        str,   # YYYY-MM-DD or ""
#     "album":       str,   # release title (used as album tag in video)
# }

SOFTWARE_TAG = "Inch of Shadow Resizer"


# ---------------------------------------------------------------------------
# Build metadata dict from release JSON
# ---------------------------------------------------------------------------

def metadata_from_release(slug: str) -> dict[str, str] | None:
    """Load a release JSON and return a metadata dict.

    Returns None if the release cannot be found.
    """
    try:
        from release_manager.storage import load_release
    except ImportError:
        print(
            "  Warning: release_manager not available -- cannot load release metadata.",
            file=sys.stderr,
        )
        return None

    rel = load_release(slug)
    if not rel:
        return None

    meta = rel.get("metadata", {})
    genre_parts = [
        meta.get("genre_primary", ""),
        meta.get("genre_secondary", ""),
    ]
    return {
        "title":       meta.get("title", ""),
        "artist":      meta.get("artist", ""),
        "copyright":   meta.get("copyright", ""),
        "description": meta.get("description", ""),
        "genre":       " / ".join(p for p in genre_parts if p),
        "date":        rel.get("release_date", ""),
        "album":       meta.get("title", ""),
    }


# ---------------------------------------------------------------------------
# Build metadata dict from manual flags
# ---------------------------------------------------------------------------

def metadata_from_flags(
    title: str = "",
    artist: str = "",
    copyright_text: str = "",
    description: str = "",
    genre: str = "",
    date: str = "",
) -> dict[str, str]:
    """Build a metadata dict from individual CLI flag values."""
    return {
        "title":       title,
        "artist":      artist,
        "copyright":   copyright_text,
        "description": description,
        "genre":       genre,
        "date":        date,
        "album":       title,
    }


# ---------------------------------------------------------------------------
# JPEG: embed EXIF via piexif
# ---------------------------------------------------------------------------

def embed_jpeg_metadata(file_path: Path, metadata: dict[str, str]) -> None:
    """Write EXIF metadata into an existing JPEG file using piexif.

    Uses piexif.insert() which modifies the file in-place and preserves
    the ICC colour profile embedded by Pillow.

    Only writes fields that have non-empty values. GPS IFD is left empty.
    """
    import piexif
    import piexif.helper

    exif_dict: dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

    if metadata.get("title"):
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = (
            metadata["title"].encode("utf-8")
        )
    if metadata.get("artist"):
        exif_dict["0th"][piexif.ImageIFD.Artist] = (
            metadata["artist"].encode("utf-8")
        )
    if metadata.get("copyright"):
        exif_dict["0th"][piexif.ImageIFD.Copyright] = (
            metadata["copyright"].encode("utf-8")
        )
    if metadata.get("date"):
        # EXIF DateTime: "YYYY:MM:DD HH:MM:SS"
        date_str = metadata["date"].replace("-", ":")
        if len(date_str) == 10:
            date_str += " 00:00:00"
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode("utf-8")

    exif_dict["0th"][piexif.ImageIFD.Software] = SOFTWARE_TAG.encode("utf-8")

    # Combine genre + description into UserComment (4 KB limit is safe here)
    comment_parts = []
    if metadata.get("genre"):
        comment_parts.append(f"Genre: {metadata['genre']}")
    if metadata.get("description"):
        comment_parts.append(metadata["description"][:2000])
    if comment_parts:
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = (
            piexif.helper.UserComment.dump(" | ".join(comment_parts), encoding="unicode")
        )

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, str(file_path))


# ---------------------------------------------------------------------------
# PNG: build PngInfo text chunks
# ---------------------------------------------------------------------------

def build_png_metadata(metadata: dict[str, str]):
    """Build a Pillow PngInfo object with tEXt/iTXt text chunks.

    Pass the returned object to result.save(..., pnginfo=build_png_metadata(metadata)).
    """
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()

    if metadata.get("title"):
        info.add_text("Title", metadata["title"])
    if metadata.get("artist"):
        info.add_text("Author", metadata["artist"])
    if metadata.get("copyright"):
        info.add_text("Copyright", metadata["copyright"])
    if metadata.get("genre"):
        info.add_text("Comment", f"Genre: {metadata['genre']}")
    if metadata.get("description"):
        info.add_text("Description", metadata["description"][:2000])
    if metadata.get("date"):
        info.add_text("Creation Time", metadata["date"])

    info.add_text("Software", SOFTWARE_TAG)

    return info


# ---------------------------------------------------------------------------
# Video: build ffmpeg -metadata flags
# ---------------------------------------------------------------------------

def build_ffmpeg_metadata_flags(metadata: dict[str, str]) -> list[str]:
    """Return a flat list of ffmpeg -metadata flags for the given metadata dict.

    Example: ["-metadata", "title=My Track", "-metadata", "artist=Inch of Shadow", ...]
    Only includes keys with non-empty values.
    """
    mapping = [
        ("title",       "title"),
        ("artist",      "artist"),
        ("album",       "album"),
        ("genre",       "genre"),
        ("copyright",   "copyright"),
        ("date",        "date"),
        ("description", "description"),
    ]
    flags: list[str] = []
    for key, ffmpeg_key in mapping:
        value = metadata.get(key, "")
        if value:
            flags.extend(["-metadata", f"{ffmpeg_key}={value}"])
    return flags
