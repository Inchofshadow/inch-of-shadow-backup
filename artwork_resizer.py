"""
artwork_resizer.py
------------------
Takes one master artwork image and exports correctly sized versions
for every platform needed as a music artist.

Upgrades in this version:
  - Apple Music release + profile exports
  - Source image name embedded in every output filename
  - Auto effect detection: analyzes the image and appends effect name to filename
  - Focal point crop: choose where the subject is (center, top, left, etc.)
  - Platform selector: export only the platforms you need (--only)
  - Preview grid: generates a thumbnail sheet of all exports
  - Auto-open: opens resized/ in Finder when done
  - EXIF/GPS/metadata stripped from all outputs
  - ICC color profile preserved end-to-end
  - JPEG saved with subsampling=0 (4:4:4) and quality=97
  - PNG output option (--format png) for lossless exports
  - Unsharp mask applied after downscaling to restore crispness
  - Upscaling detection warns when master image is too small
  - Quality report: warns if any export has suspiciously small file size (D)
  - --list: print all platform names and pixel sizes, then exit (E)
  - Batch report: summary line after processing multiple images (F)
  - --format png: lossless PNG output option (G)
  - --dry-run: show what would be exported without writing anything (H)

Usage:
    python3 artwork_resizer.py artwork/IMG_6455.jpeg
    python3 artwork_resizer.py artwork/IMG_6455.jpeg --focal top
    python3 artwork_resizer.py artwork/IMG_6455.jpeg --only spotify applemusic
    python3 artwork_resizer.py artwork/IMG_6455.jpeg --format png
    python3 artwork_resizer.py artwork/IMG_6455.jpeg --dry-run
    python3 artwork_resizer.py --list
"""

from __future__ import annotations

import io
import math
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageStat

# Guard against decompression bomb attacks (maliciously crafted images that
# decompress to gigabytes of RAM). 250MP ≈ 16000x16000px — well above any
# real artwork you'd use. Pillow raises DecompressionBombError beyond this.
Image.MAX_IMAGE_PIXELS = 250_000_000


# ---------------------------------------------------------------------------
# Platform export definitions
# (output_template, target_w, target_h, category_label, platform_tag)
# The output filename will be:  {template}_{image_stem}.{ext}
#
# Sizes checked against the platforms' own pages on 2026-09-20 (board ticket Machine-07):
# Apple asks for covers of at least 4000x4000 (Spotify takes up to 10000, Bandcamp 1400+,
# Symphonic JPEG 1000-10000); Beatport prefers 3000x3000; YouTube recommends 3840x2160
# thumbnails (2160x3840 for Shorts, 50 MB from a computer, 2 MB from a phone); Instagram
# keeps photo quality from 1.91:1 to 3:4 and its profile grid shows 3:4 tiles.
# Not stated officially anywhere: Bandcamp header height (975 wide is official) and
# Bandcamp avatar size.
# ---------------------------------------------------------------------------
COVER_MASTER_PX   = 4000   # release cover, when the master image is large enough
COVER_FALLBACK_PX = 3000   # otherwise: never upscale a cover

EXPORTS = [
    # --- Release Artwork ---
    ("release_spotify",           4000, 4000, "Release Artwork",      "spotify"),
    ("release_applemusic",        4000, 4000, "Release Artwork",      "applemusic"),
    ("release_bandcamp",          4000, 4000, "Release Artwork",      "bandcamp"),
    ("release_beatport",          3000, 3000, "Release Artwork",      "beatport"),
    ("profile_beatport",           590,  404, "Beatport Profile",     "beatport"),
    ("release_soundcloud",         800,  800, "Release Artwork",      "soundcloud"),
    ("release_web_thumb",           500,  500, "Release Artwork",      "spotify"),

    # --- Spotify Artist Profile ---
    ("profile_spotify_avatar",     750,  750, "Spotify Profile",      "spotify"),
    ("profile_spotify_banner",    2660, 1140, "Spotify Profile",      "spotify"),

    # --- Apple Music Profile ---
    ("profile_applemusic",        3000, 3000, "Apple Music Profile",  "applemusic"),

    # --- YouTube ---
    ("profile_youtube_banner",    2560, 1440, "YouTube",              "youtube"),
    ("profile_youtube_avatar",     800,  800, "YouTube",              "youtube"),
    ("thumb_youtube",             1280,  720, "YouTube",              "youtube"),
    ("thumb_youtube_4k",          3840, 2160, "YouTube",              "youtube"),
    ("thumb_youtube_shorts",      2160, 3840, "YouTube",              "youtube"),

    # --- Bandcamp Profile ---
    ("profile_bandcamp_avatar",   1440, 1440, "Bandcamp Profile",     "bandcamp"),
    ("profile_bandcamp_header",    975,  180, "Bandcamp Profile",     "bandcamp"),

    # --- SoundCloud Profile ---
    ("profile_soundcloud_banner", 2480,  520, "SoundCloud Profile",   "soundcloud"),
    ("profile_soundcloud_avatar", 1000, 1000, "SoundCloud Profile",   "soundcloud"),

    # --- Instagram ---
    ("social_instagram_post",     1080, 1080, "Instagram",            "instagram"),
    ("social_instagram_story",    1080, 1920, "Instagram",            "instagram"),
    ("social_instagram_portrait", 1080, 1350, "Instagram",            "instagram"),
    ("social_instagram_grid",     1080, 1440, "Instagram",            "instagram"),
    ("social_instagram_reel_cover", 420, 654, "Instagram",            "instagram"),
]

# Release covers that want the 4000px master and fall back without upscaling
COVER_MASTER_TEMPLATES = {"release_spotify", "release_applemusic", "release_bandcamp"}

# All unique platform tags derived from EXPORTS (used for --only validation)
ALL_PLATFORMS = sorted({e[4] for e in EXPORTS})

# ---------------------------------------------------------------------------
# Sharpening — subtle unsharp mask applied after Lanczos resize.
# Skipped for outputs where the shortest side is below SHARPEN_MIN_PX.
# ---------------------------------------------------------------------------
SHARPEN_RADIUS    = 0.6   # small radius — tightens edges without halos
SHARPEN_PERCENT   = 130   # moderate strength
SHARPEN_THRESHOLD = 3     # ignore noise below this tone difference
SHARPEN_MIN_PX    = 400   # skip sharpening on very small outputs

# Valid focal point values
FOCAL_CHOICES = [
    "center",
    "top", "bottom", "left", "right",
    "top-left", "top-right", "bottom-left", "bottom-right",
]


# ---------------------------------------------------------------------------
# Descriptive filename helpers
# ---------------------------------------------------------------------------

# Display name for each platform tag (no spaces — used in filenames)
PLATFORM_DISPLAY = {
    "spotify": "Spotify",
    "applemusic": "AppleMusic",
    "bandcamp": "Bandcamp",
    "beatport": "Beatport",
    "soundcloud": "SoundCloud",
    "youtube": "YouTube",
    "instagram": "Instagram",
}

# Purpose label per template (used in filenames)
TEMPLATE_PURPOSE = {
    "release_spotify": "Release",
    "release_applemusic": "Release",
    "release_bandcamp": "Release",
    "release_beatport": "Release",
    "profile_beatport": "Profile",
    "release_soundcloud": "Release",
    "release_web_thumb": "Thumbnail",
    "profile_spotify_avatar": "Avatar",
    "profile_spotify_banner": "Banner",
    "profile_applemusic": "Profile",
    "profile_youtube_banner": "Banner",
    "profile_youtube_avatar": "Avatar",
    "thumb_youtube": "Thumbnail",
    "thumb_youtube_4k": "Thumbnail4K",
    "thumb_youtube_shorts": "ShortsThumbnail",
    "profile_bandcamp_avatar": "Avatar",
    "profile_bandcamp_header": "Header",
    "profile_soundcloud_banner": "Banner",
    "profile_soundcloud_avatar": "Avatar",
    "social_instagram_post": "Post",
    "social_instagram_story": "Story",
    "social_instagram_portrait": "Post4x5",
    "social_instagram_grid": "Post3x4",
    "social_instagram_reel_cover": "ReelCover",
}

# Override display platform for templates where EXPORTS platform tag is misleading
TEMPLATE_PLATFORM_OVERRIDE = {
    "release_web_thumb": "Web",
}


def clean_stem(stem: str) -> str:
    """Remove pixel dimension patterns (e.g. _3000x3000, -1080x1920) from filename stem."""
    cleaned = re.sub(r'[_\- ]?\d{3,5}\s*[xX]\s*\d{3,5}[_\- ]?', '', stem)
    cleaned = cleaned.strip('_- ')
    return cleaned if cleaned else stem


def apply_cover_fallback(active_exports: list, src_w: int, src_h: int) -> tuple[list, str | None]:
    """Release covers are 4000px when the master allows it, else 3000px. Never upscaled.

    Returns the adjusted export list and a note for the user (None when nothing changed).
    """
    square = min(src_w, src_h)
    if square >= COVER_MASTER_PX:
        return active_exports, None
    adjusted = [
        (t, COVER_FALLBACK_PX, COVER_FALLBACK_PX, cat, plat) if t in COVER_MASTER_TEMPLATES else (t, w, h, cat, plat)
        for (t, w, h, cat, plat) in active_exports
    ]
    if adjusted == list(active_exports):
        return active_exports, None
    note = (
        f"  NOTE  master is {src_w}x{src_h}px: release cover exported at "
        f"{COVER_FALLBACK_PX}x{COVER_FALLBACK_PX}, not upscaled. Apple Music asks for at "
        f"least {COVER_MASTER_PX}x{COVER_MASTER_PX}; build the cover at {COVER_MASTER_PX}px or larger."
    )
    return adjusted, note


def merge_exports(active_exports: list) -> list[dict]:
    """Merge exports with identical (width, height, category) to produce one file instead of duplicates."""
    merged: dict[tuple, dict] = {}
    order: list[tuple] = []
    for template, w, h, category, platform in active_exports:
        key = (w, h, category)
        display = TEMPLATE_PLATFORM_OVERRIDE.get(
            template, PLATFORM_DISPLAY.get(platform, platform.title())
        )
        if key not in merged:
            merged[key] = {
                "width": w, "height": h, "category": category,
                "templates": [template], "platforms": [platform],
                "display_platforms": [display],
            }
            order.append(key)
        else:
            merged[key]["templates"].append(template)
            if platform not in merged[key]["platforms"]:
                merged[key]["platforms"].append(platform)
            if display not in merged[key]["display_platforms"]:
                merged[key]["display_platforms"].append(display)
    return [merged[k] for k in order]


def build_export_filename(entry: dict, stem: str, fmt: str) -> str:
    """Build descriptive filename: Platforms_WxH_Purpose_source.ext"""
    purpose = TEMPLATE_PURPOSE.get(entry["templates"][0], "Export")
    platforms_str = "_".join(entry["display_platforms"])
    w, h = entry["width"], entry["height"]
    return f"{platforms_str}_{w}x{h}_{purpose}_{stem}.{fmt}"


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = ArgumentParser(
        description="Export artwork sized for all music platforms.",
        epilog=(
            f"Available platforms for --only: {', '.join(ALL_PLATFORMS)}\n"
            f"Available focal points: {', '.join(FOCAL_CHOICES)}"
        ),
    )
    parser.add_argument(
        "image",
        nargs="?",          # optional — not needed for --delete / --list / auto-scan
        help="Path to the master artwork image (JPG, PNG, HEIC, etc.)",
    )
    parser.add_argument(
        "--focal",
        choices=FOCAL_CHOICES,
        default="center",
        metavar="POINT",
        help=(
            "Focal point for cropping. Use this when your subject isn't centered. "
            f"Choices: {', '.join(FOCAL_CHOICES)}  (default: center)"
        ),
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=ALL_PLATFORMS,
        metavar="PLATFORM",
        help=(
            "Export only the specified platform(s). "
            f"Choices: {', '.join(ALL_PLATFORMS)}"
        ),
    )
    parser.add_argument(
        "--delete",
        metavar="NAME",
        help=(
            "Delete all exports in resized/ that belong to the given image name. "
            "Example: --delete IMG_6455_haze"
        ),
    )
    parser.add_argument(
        "--flip",
        choices=["h", "v"],
        metavar="AXIS",
        help="Flip the image before exporting. h = horizontal (mirror), v = vertical.",
    )
    parser.add_argument(
        "--rotate",
        choices=["90", "180", "270"],
        metavar="DEG",
        help="Rotate the image clockwise before exporting. Choices: 90, 180, 270.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the resized/ folder in Finder automatically when done.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all platform export names and pixel sizes, then exit.",
    )
    parser.add_argument(
        "--format",
        choices=["jpg", "png"],
        default="jpg",
        metavar="FMT",
        help="Output format: jpg (default, near-lossless JPEG) or png (lossless, larger files).",
    )
    parser.add_argument(
        "--cover",
        action="store_true",
        help=(
            "The image is a RELEASE COVER. Skips every profile picture and banner, and for "
            "sizes that are not square (YouTube thumbnails, story, 4:5, 3:4) keeps the WHOLE "
            "cover: it sits centred on a blurred, darkened copy of itself, the same picture as "
            "the YouTube cover videos, instead of being cropped."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be exported without writing any files.",
    )
    # --- Metadata embedding (opt-in) ---
    parser.add_argument(
        "--release",
        metavar="SLUG",
        help="Embed metadata from a release JSON (e.g. --release fsd-single).",
    )
    parser.add_argument("--title", metavar="TEXT", help="Embed title metadata.")
    parser.add_argument("--artist", metavar="TEXT", help="Embed artist metadata.")
    parser.add_argument(
        "--copyright", metavar="TEXT", dest="copyright_text",
        help="Embed copyright metadata (e.g. '2026 Inch of Shadow').",
    )
    parser.add_argument("--description", metavar="TEXT", help="Embed description metadata.")
    parser.add_argument("--genre", metavar="TEXT", help="Embed genre metadata.")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Color management
# ---------------------------------------------------------------------------

def extract_icc_profile(image: Image.Image) -> bytes | None:
    """Return the raw ICC profile bytes from the image, or None if absent."""
    return image.info.get("icc_profile", None)


def ensure_rgb_with_profile(
    image: Image.Image,
    icc_bytes: bytes | None,
) -> tuple[Image.Image, bytes]:
    """
    Convert the image to RGB using a color-managed transform when possible.

    iPhone photos (and many professional images) use Display P3 or other
    wide-gamut profiles. Without this step, colors get desaturated when
    viewers interpret the pixels as sRGB. We convert to sRGB properly and
    embed a canonical sRGB tag in every output.
    """
    srgb_profile = ImageCms.createProfile("sRGB")
    srgb_bytes   = ImageCms.ImageCmsProfile(srgb_profile).tobytes()

    if image.mode == "RGB":
        if icc_bytes:
            try:
                src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
                transform = ImageCms.buildTransform(
                    src_profile, srgb_profile,
                    inMode="RGB", outMode="RGB",
                    renderingIntent=ImageCms.Intent.PERCEPTUAL,
                )
                image = ImageCms.applyTransform(image, transform)
                return image, srgb_bytes
            except Exception:
                pass  # corrupt or unsupported profile — fall through
        return image, srgb_bytes

    # CMYK source with embedded profile (common in Photoshop exports)
    if image.mode == "CMYK" and icc_bytes:
        try:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
            transform = ImageCms.buildTransform(
                src_profile, srgb_profile,
                inMode="CMYK", outMode="RGB",
                renderingIntent=ImageCms.Intent.PERCEPTUAL,
            )
            image = ImageCms.applyTransform(image, transform)
            return image, srgb_bytes
        except Exception:
            pass

    # Generic fallback (palette, LAB, RGBA, etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image, srgb_bytes


# ---------------------------------------------------------------------------
# Crop and resize
# ---------------------------------------------------------------------------

def compute_crop_box(
    src_w: int, src_h: int,
    target_w: int, target_h: int,
    focal: str,
) -> tuple[tuple[int, int, int, int], int, int]:
    """
    Compute the crop box that matches the target aspect ratio,
    honoring the focal point.

    Returns (box, crop_w, crop_h).
    """
    target_ratio = target_w / target_h
    src_ratio    = src_w / src_h

    if src_ratio > target_ratio:
        # Source is wider — trim left and/or right
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
        # Source is taller — trim top and/or bottom
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
        # Aspect ratios already match — no crop needed
        crop_w, crop_h = src_w, src_h
        box = (0, 0, src_w, src_h)

    return box, crop_w, crop_h


COVER_MODE = False   # set by --cover: a square release cover is never cropped


def compose_cover(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """The whole square cover, centred on a blurred, darkened blow-up of itself.

    Same picture as youtube/tools/render.py makes for the cover videos (blur 60 px on a
    3840 canvas, darker, a little less colour), so a thumbnail made here matches the channel.
    """
    from PIL import ImageFilter
    side = max(target_w, target_h)
    bg = image.resize((side, side), Image.LANCZOS)
    left, top = (side - target_w) // 2, (side - target_h) // 2
    bg = bg.crop((left, top, left + target_w, top + target_h))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=side / 64))
    # ffmpeg's eq works on luma and chroma, not on RGB: brightness=-0.2 takes a fifth of the
    # range off the luma only, saturation=0.8 pulls the chroma toward grey. Same here.
    y, cb, cr = bg.convert("YCbCr").split()
    y = y.point(lambda v: max(0, v - 44))
    cb, cr = (c.point(lambda v: round(128 + (v - 128) * 0.8)) for c in (cb, cr))
    bg = Image.merge("YCbCr", (y, cb, cr)).convert("RGB")
    small = min(target_w, target_h)
    bg.paste(image.resize((small, small), Image.LANCZOS), ((target_w - small) // 2, (target_h - small) // 2))
    return bg


def crop_and_resize(
    image: Image.Image,
    target_w: int,
    target_h: int,
    focal: str,
    filename: str,
) -> tuple[Image.Image, bool]:
    """Crop to target aspect ratio (respecting focal point) then resize."""
    src_w, src_h = image.size
    if COVER_MODE and abs(src_w - src_h) <= 2 and target_w != target_h:
        return compose_cover(image, target_w, target_h), min(target_w, target_h) > src_w
    box, crop_w, crop_h = compute_crop_box(src_w, src_h, target_w, target_h, focal)

    # Warn if the crop region is smaller than the target (upscaling required)
    upscaling = (target_w > crop_w) or (target_h > crop_h)
    if upscaling:
        print(
            f"  WARNING  {filename}: upscaling detected "
            f"(crop {crop_w}x{crop_h} -> target {target_w}x{target_h}) "
            f"-- consider a larger master image",
            file=sys.stderr,
        )

    if box != (0, 0, src_w, src_h):
        image = image.crop(box)

    image = image.resize((target_w, target_h), Image.LANCZOS)
    return image, upscaling


def apply_sharpening(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Subtle unsharp mask to recover crispness after Lanczos downscaling.
    Skipped on very small outputs where it would introduce ringing.
    """
    if min(target_w, target_h) < SHARPEN_MIN_PX:
        return image
    return image.filter(
        ImageFilter.UnsharpMask(
            radius=SHARPEN_RADIUS,
            percent=SHARPEN_PERCENT,
            threshold=SHARPEN_THRESHOLD,
        )
    )


# ---------------------------------------------------------------------------
# Single image export
# ---------------------------------------------------------------------------

def export_image(
    source: Image.Image,
    srgb_profile_bytes: bytes,
    output_path: Path,
    target_w: int,
    target_h: int,
    focal: str,
    fmt: str = "jpg",
    metadata: dict | None = None,
) -> tuple[int, bool]:
    """
    Crop, resize, sharpen, and save one output image.

    EXIF / GPS / camera metadata is intentionally NOT written to the output
    (Pillow omits it unless explicitly passed). This protects your privacy.

    Pass metadata= to opt-in to embedding title/artist/copyright/genre.
    No GPS or camera data is ever written regardless of this flag.

    JPEG quality settings:
      quality=97      near-lossless JPEG
      subsampling=0   4:4:4 chroma — no color-detail loss (vs default 4:2:0)
      optimize=True   Huffman table optimisation (smaller file, same quality)
      icc_profile     canonical sRGB tag embedded for correct color rendering

    PNG: lossless, no chroma subsampling, significantly larger files.
    """
    result, was_upscaled = crop_and_resize(
        source, target_w, target_h, focal, output_path.name
    )
    result = apply_sharpening(result, target_w, target_h)

    if fmt == "png":
        save_kwargs: dict = {
            "format": "PNG",
            "icc_profile": srgb_profile_bytes,
            # exif is intentionally omitted
        }
        if metadata:
            from metadata_utils import build_png_metadata
            save_kwargs["pnginfo"] = build_png_metadata(metadata)
        result.save(output_path, **save_kwargs)
    else:
        result.save(
            output_path,
            format="JPEG",
            quality=97,
            subsampling=0,
            optimize=True,
            icc_profile=srgb_profile_bytes,
            # exif is intentionally omitted — strips GPS and camera metadata
        )
        if metadata:
            from metadata_utils import embed_jpeg_metadata
            embed_jpeg_metadata(output_path, metadata)

    return output_path.stat().st_size // 1024, was_upscaled


# ---------------------------------------------------------------------------
# Preview grid
# ---------------------------------------------------------------------------

def generate_preview_grid(
    results: list[tuple],
    output_dir: Path,
    stem: str,
    ext: str = "jpg",
) -> Path:
    """
    Generate a thumbnail contact sheet showing all exported crops.
    Each cell shows the image preview, the template name, and dimensions.
    Saved as _preview_{stem}.jpg inside resized/.
    """
    THUMB_MAX  = 220       # max dimension per thumbnail
    PADDING    = 14        # padding around each cell
    LABEL_H    = 38        # height reserved for text labels below thumbnail
    COLS       = 4         # number of columns in the grid
    BG         = (18, 18, 18)
    CELL_BG    = (32, 32, 32)
    TEXT_COLOR = (215, 215, 215)
    DIM_COLOR  = (120, 120, 120)

    cell_w = THUMB_MAX + PADDING * 2
    cell_h = THUMB_MAX + LABEL_H + PADDING * 2
    rows   = math.ceil(len(results) / COLS)
    grid_w = COLS * cell_w + PADDING
    grid_h = rows * cell_h + PADDING

    grid = Image.new("RGB", (grid_w, grid_h), BG)
    draw = ImageDraw.Draw(grid)

    for i, (filename, w, h, kb, category, upscaled) in enumerate(results):
        col = i % COLS
        row = i // COLS
        cx  = col * cell_w + PADDING
        cy  = row * cell_h + PADDING

        # Cell background
        draw.rectangle(
            [cx, cy, cx + cell_w - PADDING, cy + cell_h - PADDING],
            fill=CELL_BG,
        )

        # Thumbnail (loaded from the already-saved export)
        thumb = Image.open(output_dir / filename)
        thumb.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        tx = cx + (THUMB_MAX - thumb.width)  // 2
        ty = cy + (THUMB_MAX - thumb.height) // 2
        grid.paste(thumb, (tx, ty))

        # Labels — show the template name (strip the stem suffix for brevity)
        template_label = filename.replace(f"_{stem}.{ext}", "")
        if len(template_label) > 26:
            template_label = template_label[:24] + ".."
        draw.text((cx + 5, cy + THUMB_MAX + 6),  template_label, fill=TEXT_COLOR)
        draw.text((cx + 5, cy + THUMB_MAX + 22), f"{w}x{h}px",   fill=DIM_COLOR)

    grid_path = output_dir / f"_preview_{stem}.jpg"
    grid.save(grid_path, "JPEG", quality=90, optimize=True)
    return grid_path


# ---------------------------------------------------------------------------
# Summary output
# ---------------------------------------------------------------------------

def print_summary(results: list[tuple], dry_run: bool = False) -> None:
    col_file = 42
    col_dims = 14
    col_size = 10

    header  = f"{'File':<{col_file}} {'Dimensions':<{col_dims}} {'Size':>{col_size}}"
    divider = "-" * len(header)

    label = "DRY RUN -- no files written" if dry_run else "Export Summary"
    print()
    print(f"  Artwork Resizer -- {label}")
    print(f"  {divider}")
    print(f"  {header}")
    print(f"  {divider}")

    current_category = None
    upscale_warnings = []
    quality_warnings = []

    for filename, w, h, kb, category, upscaled in results:
        if category != current_category:
            print(f"\n  [{category}]")
            current_category = category

        dims    = f"{w}x{h}px"
        min_kb  = max(20, (w * h) // 100_000)
        quality_low = not dry_run and 0 < kb < min_kb
        flag    = " [upscaled]" if upscaled else ""
        if quality_low:
            flag += " [quality?]"
        size_str = f"{kb} KB" if not dry_run else "-- KB"
        print(f"  {filename:<{col_file}} {dims:<{col_dims}} {size_str:>{col_size}}{flag}")

        if upscaled:
            upscale_warnings.append(filename)
        if quality_low:
            quality_warnings.append((filename, w, h, kb, min_kb))

    print(f"\n  {divider}")
    if dry_run:
        print(f"  {len(results)} files would be exported to resized/ (dry run -- nothing written)")
    else:
        print(f"  {len(results)} files exported to resized/")
        print("  EXIF / GPS / metadata stripped from all outputs")

    if upscale_warnings:
        print()
        print("  WARNING: the following exports required upscaling.")
        print("  Use a larger master image for best quality:")
        for name in upscale_warnings:
            print(f"    - {name}")

    if quality_warnings:
        print()
        print("  WARNING: the following exports have unexpectedly small file sizes.")
        print("  This may indicate a corrupt or blank source image:")
        for name, w, h, kb, min_kb in quality_warnings:
            print(f"    - {name}  ({kb} KB, expected >{min_kb} KB)")

    print()


# ---------------------------------------------------------------------------
# Effect detection
# ---------------------------------------------------------------------------

def detect_effects(image: Image.Image) -> str:
    """
    Analyze pixel statistics on a small sample of the image to detect
    common visual effects. Returns a short label (e.g. 'bw', 'warm_faded')
    that is appended to the output stem, or an empty string if no clear
    effect is detected.

    Detected effects:
      bw           — black and white / grayscale
      sepia        — warm brownish monochrome tone
      warm         — orange/red color grade
      cool         — blue color grade
      desaturated  — colors muted / washed out
      vivid        — oversaturated / punchy colors
      bright       — overexposed / very bright
      dark         — dark / moody / underexposed
      faded        — low contrast, flat/matte look
      hc           — high contrast
      blur         — soft focus / blur effect
    """
    # Analyze a small temporary copy — the original image is never modified.
    sample = image.copy()
    sample.thumbnail((120, 120), Image.LANCZOS)

    stat       = ImageStat.Stat(sample)
    r_mean     = stat.mean[0]
    g_mean     = stat.mean[1]
    b_mean     = stat.mean[2]
    r_std      = stat.stddev[0]
    g_std      = stat.stddev[1]
    b_std      = stat.stddev[2]
    brightness = (r_mean + g_mean + b_mean) / 3
    contrast   = (r_std + g_std + b_std) / 3

    # Max difference between any two channel means — low = grayscale
    max_ch_diff = max(
        abs(r_mean - g_mean),
        abs(g_mean - b_mean),
        abs(r_mean - b_mean),
    )

    # Per-pixel saturation: (max_channel - min_channel) / max_channel
    pixels = list(sample.getdata())
    sat_values = []
    for r, g, b in pixels:
        mx = max(r, g, b)
        mn = min(r, g, b)
        sat_values.append((mx - mn) / mx if mx > 0 else 0.0)
    avg_sat = sum(sat_values) / len(sat_values)

    effects = []

    # --- Black & White: channels must be very close — clearly intentional ---
    if max_ch_diff < 6:
        effects.append("bw")

    else:
        # --- Sepia: warm R > G > B with very low saturation ---
        is_sepia = (
            r_mean > g_mean > b_mean
            and 18 < (r_mean - g_mean) < 55
            and  8 < (g_mean - b_mean) < 35
            and avg_sat < 0.20
        )
        if is_sepia:
            effects.append("sepia")
        else:
            # --- Color temperature: only flag strong, obvious grades ---
            if r_mean - b_mean > 45:
                effects.append("warm")
            elif b_mean - r_mean > 45:
                effects.append("cool")

            # --- Saturation: only flag extreme ends ---
            if avg_sat < 0.08:
                effects.append("desaturated")
            elif avg_sat > 0.68:
                effects.append("vivid")

    # --- Exposure: only flag clearly over/underexposed images ---
    if brightness > 218:
        effects.append("bright")
    elif brightness < 40:
        effects.append("dark")

    # --- Contrast: only flag clearly flat or crushed images ---
    if contrast < 18:
        effects.append("faded")
    elif contrast > 90:
        effects.append("hc")

    # --- Blur: only flag when edges are nearly absent ---
    gray      = sample.convert("L")
    edges     = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    if edge_mean < 3.0:
        effects.append("blur")

    return "_".join(effects)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def delete_exports(stem: str) -> None:
    """
    Find and delete all files in resized/ whose name ends with _{stem}.jpg
    or _{stem}.png, plus the preview grid _preview_{stem}.jpg.

    Shows the full list first and asks for confirmation before deleting.
    """
    output_dir = Path("resized")
    if not output_dir.exists():
        print(f"\n  resized/ folder not found — nothing to delete.\n")
        return

    # Collect matching files (both jpg and png)
    targets = sorted(
        list(output_dir.glob(f"*_{stem}.jpg")) +
        list(output_dir.glob(f"*_{stem}.png"))
    )

    if not targets:
        print(f"\n  No exports found for '{stem}' in resized/.\n")
        return

    print(f"\n  The following files will be deleted:\n")
    for f in targets:
        size_kb = f.stat().st_size // 1024
        print(f"    {f.name:<50} {size_kb} KB")

    print(f"\n  Total: {len(targets)} files")
    answer = input("\n  Confirm delete? [y/N] ").strip().lower()

    if answer != "y":
        print("  Cancelled — nothing deleted.\n")
        return

    deleted = 0
    for f in targets:
        try:
            f.unlink()
            deleted += 1
        except Exception as exc:
            print(f"  x  Could not delete {f.name}: {exc}")

    print(f"\n  Done — {deleted} file(s) deleted.\n")


# ---------------------------------------------------------------------------
# Single-image processing (shared by both manual and auto-scan modes)
# ---------------------------------------------------------------------------

def process_image(
    input_path: Path,
    output_dir: Path,
    active_exports: list,
    focal: str,
    flip: str | None,
    rotate: str | None,
    fmt: str = "jpg",
    dry_run: bool = False,
    metadata: dict | None = None,
) -> list:
    """Load, transform, detect effects, export, and summarize one image.

    Returns the results list for batch reporting.
    Pass metadata= to embed title/artist/copyright/genre in exports.
    """

    print(f"\nLoading: {input_path.name}")
    try:
        source = Image.open(input_path)
        source.load()
    except Exception as exc:
        print(f"  Error opening image: {exc}")
        return []

    raw_stem = Path(input_path.stem).name  # strip any accidental path separators
    stem = clean_stem(raw_stem)

    # Color management
    icc_bytes = extract_icc_profile(source)
    if icc_bytes:
        print(f"  ICC profile found ({len(icc_bytes)} bytes) -- color management enabled")
    else:
        print("  No ICC profile found -- assuming sRGB")

    source, srgb_profile_bytes = ensure_rgb_with_profile(source, icc_bytes)

    # Apply flip transformation if requested
    if flip == "h":
        source = source.transpose(Image.FLIP_LEFT_RIGHT)
        print("  Transform: flipped horizontal (mirrored)")
    elif flip == "v":
        source = source.transpose(Image.FLIP_TOP_BOTTOM)
        print("  Transform: flipped vertical")

    # Apply rotation if requested (Pillow rotates counter-clockwise, so invert)
    if rotate == "90":
        source = source.transpose(Image.ROTATE_270)
        print("  Transform: rotated 90° clockwise")
    elif rotate == "180":
        source = source.transpose(Image.ROTATE_180)
        print("  Transform: rotated 180°")
    elif rotate == "270":
        source = source.transpose(Image.ROTATE_90)
        print("  Transform: rotated 270° clockwise")

    # Detect visual effects and append to the stem used in output filenames
    effect = detect_effects(source)
    if effect:
        stem = f"{stem}_{effect}"
        print(f"  Effect detected: {effect}")
    else:
        print(f"  Effect detected: none (looks unmodified)")

    src_w, src_h = source.size
    fmt_label = fmt.upper()
    print(f"  Master: {src_w}x{src_h}px  |  Mode: {source.mode}  |  Focal: {focal}  |  Format: {fmt_label}")

    if metadata:
        meta_fields = [f for f in ("title", "artist", "copyright", "genre") if metadata.get(f)]
        print(f"  Metadata: embedding {', '.join(meta_fields)}")

    # Release cover: 4000px from a large enough master, else 3000px, never upscaled
    active_exports, cover_note = apply_cover_fallback(active_exports, src_w, src_h)
    if cover_note:
        print(cover_note)

    # Merge exports with identical dimensions + category (e.g. Spotify + Apple Music + Bandcamp)
    merged = merge_exports(active_exports)
    results = []

    if dry_run:
        print(f"\n  Would export {len(merged)} files (dry run):\n")
        for entry in merged:
            filename = build_export_filename(entry, stem, fmt)
            print(f"  -  {filename}")
            results.append((filename, entry["width"], entry["height"], 0, entry["category"], False))
    else:
        print(f"\n  Exporting {len(merged)} files...\n")
        for entry in merged:
            filename    = build_export_filename(entry, stem, fmt)
            output_path = output_dir / filename
            try:
                size_kb, upscaled = export_image(
                    source, srgb_profile_bytes,
                    output_path, entry["width"], entry["height"], focal, fmt,
                    metadata=metadata,
                )
                results.append((filename, entry["width"], entry["height"], size_kb, entry["category"], upscaled))
                status = "!" if upscaled else "v"
                print(f"  {status}  {filename}")
            except Exception as exc:
                print(f"  x  {filename}  -- ERROR: {exc}")

        # Generate preview grid
        print(f"\n  Generating preview grid...")
        try:
            grid_path = generate_preview_grid(results, output_dir, stem, fmt)
            print(f"  v  {grid_path.name}")
        except Exception as exc:
            print(f"  x  Preview grid failed: {exc}")

    print_summary(results, dry_run=dry_run)
    return results


def is_already_exported(stem: str, output_dir: Path) -> bool:
    """Return True if resized/ already contains exports for this image stem."""
    cleaned = clean_stem(stem)
    for s in {stem, cleaned}:
        if (any(output_dir.glob(f"*_{s}.jpg")) or
            any(output_dir.glob(f"*_{s}.png")) or
            any(output_dir.glob(f"*_{s}_*.jpg")) or
            any(output_dir.glob(f"*_{s}_*.png"))):
            return True
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # --list mode: print all platforms and sizes, then exit
    if args.list:
        col_t = 34
        print()
        print(f"  {'Export template':<{col_t}} {'Size':<14} Platform")
        print("  " + "-" * 62)
        current_cat = None
        for template, w, h, category, platform in EXPORTS:
            if category != current_cat:
                print(f"\n  [{category}]")
                current_cat = category
            print(f"  {template:<{col_t}} {w}x{h}px")
        print()
        sys.exit(0)

    # --delete mode: remove all exports for a given image name and exit
    if args.delete:
        if not re.match(r'^[\w\-. ]+$', args.delete):
            print("Error: --delete name contains invalid characters.")
            sys.exit(1)
        delete_exports(args.delete)
        sys.exit(0)

    output_dir = Path("resized")
    if not args.dry_run:
        output_dir.mkdir(exist_ok=True)

    # Build the active exports list (filtered by --only if given)
    active_exports = EXPORTS
    if args.cover:
        global COVER_MODE
        COVER_MODE = True
        EXPORTS_NO_PROFILE = [e for e in EXPORTS if not e[0].startswith("profile_")]
        active_exports = EXPORTS_NO_PROFILE
    if args.only:
        active_exports = [e for e in active_exports if e[4] in args.only]
        if not active_exports:
            print(f"No exports match the given platforms: {args.only}")
            sys.exit(1)

    fmt = args.format

    if args.dry_run:
        print("  [DRY RUN] No files will be written.\n")

    # --- Build metadata dict (opt-in -- None means strip all, existing behavior) ---
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

    # --- Auto-scan mode: no image argument given ---
    # Scan artwork/ folder and export only images not yet in resized/
    if not args.image:
        artwork_dir = Path("artwork")
        if not artwork_dir.exists():
            print("Error: artwork/ folder not found. Create it and drop your images in.")
            sys.exit(1)

        image_exts  = {".jpg", ".jpeg", ".png", ".heic", ".tiff", ".bmp", ".webp"}
        all_images  = [f for f in sorted(artwork_dir.iterdir())
                       if f.suffix.lower() in image_exts]

        if not all_images:
            print("No images found in artwork/ folder.")
            sys.exit(0)

        # Split into new (not exported) and already done
        new_images  = [f for f in all_images
                       if not is_already_exported(f.stem, output_dir)]
        done_images = [f for f in all_images if f not in new_images]

        if done_images:
            print(f"\n  Already exported ({len(done_images)} skipped):")
            for f in done_images:
                print(f"    - {f.name}")

        if not new_images:
            print("\n  All images in artwork/ have already been exported.")
            print("  Drop a new image into artwork/ and run again.\n")
            sys.exit(0)

        print(f"\n  New images to export: {len(new_images)}")
        total_files = 0
        total_kb    = 0
        for f in new_images:
            results = process_image(
                f, output_dir, active_exports, args.focal, args.flip, args.rotate,
                fmt=fmt, dry_run=args.dry_run, metadata=metadata,
            )
            total_files += len(results)
            total_kb    += sum(r[3] for r in results)

        # Batch summary (only meaningful when more than one image was processed)
        if len(new_images) > 1:
            total_mb = total_kb / 1024
            verb = "would be exported" if args.dry_run else "exported"
            print(
                f"  Batch complete: {len(new_images)} images processed, "
                f"{total_files} files {verb}, {total_mb:.1f} MB written.\n"
            )

    # --- Manual mode: image path given explicitly ---
    else:
        input_path = Path(args.image)
        if not input_path.is_file():
            print(f"Error: File not found -- {input_path}")
            sys.exit(1)
        process_image(
            input_path, output_dir, active_exports, args.focal, args.flip, args.rotate,
            fmt=fmt, dry_run=args.dry_run, metadata=metadata,
        )

    if not args.dry_run:
        # Open resized/ in Finder when done
        subprocess.run(["open", str(output_dir)], check=False)
    print()


if __name__ == "__main__":
    main()
