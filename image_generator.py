#!/usr/bin/env python3
"""
Image Generator for Inch of Shadow.

Local-first AI image tool using OpenAI's image model with your own API key.
Three modes:

  art      Text to image. A background or cover in the Inch of Shadow visual
           voice. No text baked in (image models render text poorly).
  restyle  Take one of your own photos or frames and restyle it.
  card     Generate art, then draw a crisp title and wordmark on top with
           Pillow, so the typography is always sharp and on brand.

Technique note: the AI generates the imagery only; all text is drawn in code.
This is the reliable way to get clean titles, since image models garble text.

Key handling mirrors the rest of this repo: OPENAI_API_KEY lives in .env only.
ChatGPT Pro does not include API access; this needs a paid OpenAI Platform
key with its own pay as you go billing (platform.openai.com).

Usage:
  python3 image_generator.py art "a slow figure in fog, neon bleed" --size square
  python3 image_generator.py restyle photo.jpg "grainy 1980s film, cold blue"
  python3 image_generator.py card "rain on a black window" --title "FAREWELL"
  python3 image_generator.py art "a figure on a sidewalk" --light L9 --medium bw-flash-film
  python3 image_generator.py art "..." --motif moon --motif flowers-roses --print-prompt
  python3 image_generator.py options        # list every option per kind

Output goes to generated_images/ (auto created).
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# gpt-image-1.5 shuts down 2026-12-01 and gpt-image-1 on 2026-10-23 (OpenAI deprecations page,
# checked 2026-09-27). Flare is OpenAI's fast 2.5 model; pass --model gpt-image-2.5-sunburst for finals.
DEFAULT_MODEL = "gpt-image-2.5-flare"

OUTPUT_DIR = Path(__file__).resolve().parent / "generated_images"

# Size presets. The model supports square, landscape, and portrait.
SIZE_PRESETS = {
    "square": "1024x1024",
    "landscape": "1536x1024",
    "portrait": "1024x1536",
}

# The Inch of Shadow visual identity is THREE layers (Look-04, 2026-09-14):
#  1. CORE (inch_of_shadow_style.txt) - only what is true for every image: love and
#     shadow, the mood, everything completes as one, one clear light idea, faces kept.
#  2. OPTIONS (options/<kind>/<name>.txt) - chosen per image: light, medium, texture,
#     faces, concept, symbols, setting, motif. Nothing here is forced on every image.
#  3. PALETTE (palettes/<name>.txt) - optional colour per release. Default = none.
STYLE_FILE = Path(__file__).resolve().parent / "inch_of_shadow_style.txt"
PALETTES_DIR = Path(__file__).resolve().parent / "palettes"
DEFAULT_PALETTE = "none"
OPTIONS_DIR = Path(__file__).resolve().parent / "options"
SINGLE_OPTION_KINDS = ("light", "medium", "texture", "faces", "concept", "symbols", "setting")
MULTI_OPTION_KINDS = ("motif",)

# Suggested home for reference images Amir provides to guide the look.
REFERENCES_DIR = Path(__file__).resolve().parent / "references"

# Fallbacks if the files are missing, so the tool stays usable.
_CORE_FALLBACK = (
    "An image in the visual world of Inch of Shadow, a Berlin artist. Love and shadow, light "
    "and dark. Mood: romantic, melancholic, mysterious, refined. Everything in the image "
    "completes as one whole. The light always has one clear idea, never flat, even, commercial "
    "light. Do not add people unless the subject asks for them. When a person is in the image, "
    "their attitude is distant and self-possessed, supremely confident, out of reach, sexy in a "
    "tasteful way, never explicit. If a real person is in the image, keep their face exactly as "
    "it is. No logos, no watermarks, no text or letters anywhere in the image."
)


def load_core() -> str:
    """Return the constant Inch of Shadow visual core (palette-agnostic)."""
    if STYLE_FILE.is_file():
        text = STYLE_FILE.read_text(encoding="utf-8").strip()
        if text:
            return text
    print(f"Note: {STYLE_FILE.name} missing; using built-in core fallback.")
    return _CORE_FALLBACK


def load_palette(name: str) -> str:
    """Resolve a palette. "none" adds no colour line; a name matching palettes/<name>.txt
    loads that file; an inline description (multi-word) is used verbatim for a one-off
    release palette; any other name stops with the list of available palettes."""
    name = (name or DEFAULT_PALETTE).strip()
    if name.lower() == "none":
        return ""
    f = PALETTES_DIR / f"{name}.txt"
    if f.is_file():
        text = f.read_text(encoding="utf-8").strip()
        if text:
            return text
    # Not a known palette file: treat a real description as an inline one-off.
    if " " in name or len(name) > 25:
        return name if name.lower().startswith("palette") else f"Palette: {name}."
    available = sorted(p.stem for p in PALETTES_DIR.glob("*.txt"))
    sys.exit(f"Unknown palette '{name}'. Available: none, {', '.join(available)}, or inline text.")


def available_options(kind: str) -> list[str]:
    """Option names for one kind, from options/<kind>/*.txt."""
    return sorted(p.stem for p in (OPTIONS_DIR / kind).glob("*.txt"))


def load_option(kind: str, name: str) -> str:
    """Resolve one option. Matches the file name exactly or by its id prefix
    (--light L9 finds l9-direct-flash-night); multi-word text is used inline."""
    wanted = name.strip().lower()
    for stem in available_options(kind):
        if stem == wanted or stem.startswith(wanted + "-"):
            return (OPTIONS_DIR / kind / f"{stem}.txt").read_text(encoding="utf-8").strip()
    if " " in wanted:
        return f"{kind.capitalize()}: {name.strip()}."
    sys.exit(
        f"Unknown {kind} option '{name}'. Available: {', '.join(available_options(kind))}, "
        "or inline text in quotes."
    )


def options_text(options: dict | None) -> str:
    """Join the chosen per-image options into prompt sentences, in a stable order."""
    if not options:
        return ""
    parts = []
    for kind in SINGLE_OPTION_KINDS:
        if options.get(kind):
            parts.append(load_option(kind, options[kind]))
    for kind in MULTI_OPTION_KINDS:
        for name in options.get(kind) or []:
            parts.append(load_option(kind, name))
    return " ".join(parts)


def style_prompt(
    subject: str, palette: str = DEFAULT_PALETTE, options: dict | None = None
) -> str:
    """Compose the full prompt: core + optional palette + chosen options + subject."""
    head = " ".join(t for t in (load_core(), load_palette(palette), options_text(options)) if t)
    return f"{head} Subject: {subject.strip()}."


def get_client():
    """Build the OpenAI client, raising a clear error if the key is missing."""
    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        sys.exit(
            "The openai package is not installed. Run: pip install openai "
            "(it is already listed in requirements.txt)."
        )

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        sys.exit(
            "OPENAI_API_KEY not set in .env. Create a key at platform.openai.com "
            "(developer platform, separate from ChatGPT Pro), add billing, then put "
            "OPENAI_API_KEY=sk-... in .env."
        )
    return OpenAI(api_key=api_key)


def image_bytes_from_response(response) -> bytes:
    """Extract raw image bytes whether the API returns b64_json or a url."""
    item = response.data[0]
    b64 = getattr(item, "b64_json", None)
    if b64:
        return base64.b64decode(b64)
    url = getattr(item, "url", None)
    if url:
        return requests.get(url, timeout=60).content
    raise RuntimeError("Image response contained neither b64_json nor url.")


def save_bytes(data: bytes, label: str, project: str | None = None) -> Path:
    """Write image bytes to the output folder with a timestamped name.

    If a project is given, the image is filed under generated_images/<project>/
    so each release or purpose stays in its own subfolder.
    """
    folder = OUTPUT_DIR
    if project:
        safe_project = "".join(
            c if c.isalnum() else "-" for c in project.lower()
        ).strip("-")
        folder = OUTPUT_DIR / (safe_project or "untitled")
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() else "-" for c in label.lower()).strip("-")[:40]
    path = folder / f"{safe or 'image'}-{stamp}.png"
    path.write_bytes(data)
    return path


def art_prompt(
    subject: str, palette: str = DEFAULT_PALETTE, options: dict | None = None,
    references: list | None = None,
) -> str:
    """The exact prompt art mode sends, with or without reference images."""
    prompt = style_prompt(subject, palette, options)
    if references:
        prompt += (
            " Match the visual style, color grade, texture and mood of the provided "
            "reference image(s)."
        )
    return prompt


def generate_art(
    client, subject: str, model: str, size: str, references: list | None = None,
    palette: str = DEFAULT_PALETTE, options: dict | None = None,
) -> bytes:
    """Mode: art. Text to image in the artist voice (core + palette + chosen options).

    If reference images are given, the output is guided to match their look
    (color grade, texture, mood) via the image-to-image edit endpoint.
    """
    prompt = art_prompt(subject, palette, options, references)
    if references:
        paths = [Path(r) for r in references]
        missing = [str(p) for p in paths if not p.is_file()]
        if missing:
            sys.exit("Reference image(s) not found: " + ", ".join(missing))
        handles = [p.open("rb") for p in paths]
        try:
            image_arg = handles if len(handles) > 1 else handles[0]
            response = client.images.edit(
                model=model, image=image_arg, prompt=prompt, size=size, n=1
            )
        finally:
            for h in handles:
                h.close()
        return image_bytes_from_response(response)

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality="high",
        n=1,
    )
    return image_bytes_from_response(response)


def restyle_prompt(
    instruction: str, palette: str = DEFAULT_PALETTE, options: dict | None = None
) -> str:
    """The exact prompt restyle mode sends."""
    head = " ".join(t for t in (load_core(), load_palette(palette), options_text(options)) if t)
    return (
        f"{head} Keep the underlying composition and subject of the provided photograph, "
        f"but restyle it: {instruction.strip()}."
    )


def restyle_photo(
    client, photo: Path, instruction: str, model: str, size: str,
    palette: str = DEFAULT_PALETTE, options: dict | None = None,
) -> bytes:
    """Mode: restyle. Send one of your own images and restyle it.

    Privacy: this uploads the source photo to OpenAI's servers.
    """
    if not photo.is_file():
        sys.exit(f"Photo not found: {photo}")
    prompt = restyle_prompt(instruction, palette, options)
    with photo.open("rb") as fh:
        response = client.images.edit(
            model=model,
            image=fh,
            prompt=prompt,
            size=size,
            n=1,
        )
    return image_bytes_from_response(response)


BRAND_DIR = Path(__file__).resolve().parent / "docs" / "brand"


def brand_tokens() -> dict:
    """The exact brand values (moods, type) from the YAML block of docs/brand/frame.md.
    frame.md is the single source of truth; nothing about type or colour is typed here."""
    import yaml

    text = (BRAND_DIR / "frame.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def brand_faces() -> list:
    """[(family, path), ...] from frame.md: the brand face first, then its fallback. A face
    whose file is not on disk (trial files are not under version control) is skipped."""
    face = brand_tokens().get("face") or {"family": "Marcellus", "file": "fonts/Marcellus-Regular.ttf"}
    found = []
    for f in (face, face.get("fallback") or {}):
        if f.get("file") and (BRAND_DIR / f["file"]).is_file():
            found.append((f["family"], BRAND_DIR / f["file"]))
    if not found:
        raise FileNotFoundError("No brand font file found. Check the face block in docs/brand/frame.md.")
    return found


def _draws_all(font: ImageFont.FreeTypeFont, text: str) -> bool:
    def bmp(ch):
        im = Image.new("L", (font.size * 2, font.size * 2), 0)
        ImageDraw.Draw(im).text((font.size // 4, font.size // 4), ch, font=font, fill=255)
        return im.tobytes()
    missing = bmp("\uE123")
    return all(c.isspace() or bmp(c) != missing for c in set(text))


def brand_font(size: int, text: str = "") -> ImageFont.FreeTypeFont:
    """The brand face from frame.md. No silent fallback to a system sans: an off-brand card
    is worse than an error. If the face cannot draw every character of `text` (trial files
    often lack punctuation), the fallback face sets the whole string."""
    faces = brand_faces()
    for _family, path in faces:
        f = ImageFont.truetype(str(path), size)
        if not text or _draws_all(f, text):
            return f
    return ImageFont.truetype(str(faces[-1][1]), size)


def card_lines(title: str, name: str) -> tuple[str, str]:
    """Mixed case is the default (Look-01): the text is drawn as written, never forced
    to capitals. Write it in capitals yourself when the context asks for it."""
    return title.strip(), name.strip()


def _draw_tracked(draw, xy, text, font, fill, tracking_em):
    x, y = xy
    gap = font.size * tracking_em
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + gap


def _tracked_width(text, font, tracking_em) -> float:
    return sum(font.getlength(c) for c in text) + font.size * tracking_em * (len(text) - 1)


def _hex(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def draw_card(art: bytes, title: str, wordmark: str = "Inch of Shadow", mood: str = "M2") -> bytes:
    """Composite the title and the artist name over generated art.

    Text is drawn in code so it stays crisp and on brand, never AI rendered. Type, sizes
    and colours come from docs/brand/frame.md: the brand face, the title over the artist name,
    the light colour of the chosen mood on a soft band of its dark colour.
    """
    tokens = brand_tokens()
    if mood not in tokens["moods"]:
        raise ValueError(f"Unknown mood '{mood}'. Moods: {', '.join(tokens['moods'])}")
    ink, ground = _hex(tokens["moods"][mood]["light"]), _hex(tokens["moods"][mood]["dark"])
    typo = tokens["typography"]

    base = Image.open(_bytes_io(art)).convert("RGB")
    w, h = base.size

    # Soft dark band from the bottom (frame.md: only when there is no calm area; a card
    # cannot know the picture, so the band is always there, in the mood's dark colour).
    scrim = Image.new("L", (1, h), 0)
    for y in range(h):
        t = max(0.0, (y / h - 0.45) / 0.55)
        scrim.putpixel((0, y), int(200 * t))
    scrim = scrim.resize((w, h))
    base = Image.composite(Image.new("RGB", (w, h), ground), base, scrim)

    draw = ImageDraw.Draw(base)
    title, name = card_lines(title, wordmark)

    # Sizes approved on a 1080px-wide post (title 96, name 56), scaled to this canvas.
    k = w / 1080
    title_font = brand_font(max(28, round(typo["post-title"]["px"] * k)), title)
    name_font = brand_font(max(16, round(typo["post-name"]["px"] * k)), name)
    t_track = float(str(typo["post-title"]["tracking"]).replace("em", ""))
    n_track = float(str(typo["post-name"]["tracking"]).replace("em", ""))

    ty = h * 0.72
    _draw_tracked(draw, ((w - _tracked_width(title, title_font, t_track)) / 2, ty),
                  title, title_font, ink, t_track)
    ny = ty + title_font.size * 1.1 + round(40 * k)      # name 40px under the title (frame.md)
    _draw_tracked(draw, ((w - _tracked_width(name, name_font, n_track)) / 2, ny),
                  name, name_font, ink, n_track)

    out = _bytes_io()
    base.save(out, format="PNG")
    return out.getvalue()


def _bytes_io(data: bytes | None = None):
    """Small helper to avoid importing io at call sites."""
    import io

    return io.BytesIO(data) if data is not None else io.BytesIO()


# Inch of Shadow palette ramp for local grading (luminance -> colour).
# Control points sampled from the brand deck: warm, dark, earthy.
_PALETTE_STOPS = [
    (0, (12, 10, 9)),        # near-black, warm
    (60, (58, 30, 24)),      # dark oxblood brown
    (120, (128, 62, 47)),    # oxblood / rust (signature)
    (190, (167, 153, 134)),  # clay / tan
    (255, (228, 218, 201)),  # cream / bone
]


def _palette_luts():
    """Build per-channel 256-entry lookup tables from the palette stops."""
    lut_r, lut_g, lut_b = [], [], []
    stops = _PALETTE_STOPS
    for i in range(256):
        for j in range(len(stops) - 1):
            x0, c0 = stops[j]
            x1, c1 = stops[j + 1]
            if x0 <= i <= x1:
                t = (i - x0) / (x1 - x0) if x1 > x0 else 0
                lut_r.append(round(c0[0] + (c1[0] - c0[0]) * t))
                lut_g.append(round(c0[1] + (c1[1] - c0[1]) * t))
                lut_b.append(round(c0[2] + (c1[2] - c0[2]) * t))
                break
    return lut_r, lut_g, lut_b


def grade_photo(photo: Path, strength: float = 0.9) -> bytes:
    """Local, NO-AI Inch of Shadow grade. Maps the photo's luminance to the brand
    palette, then adds grain and contrast. Faces and composition are untouched
    (this is a tonal remap, not feature editing). Strength 0..1 blends between
    the original and the full grade.
    """
    if not photo.is_file():
        sys.exit(f"Photo not found: {photo}")
    from PIL import ImageChops, ImageEnhance

    base = Image.open(photo).convert("RGB")
    gray = base.convert("L")
    lut_r, lut_g, lut_b = _palette_luts()
    graded = Image.merge(
        "RGB", (gray.point(lut_r), gray.point(lut_g), gray.point(lut_b))
    )
    graded = ImageEnhance.Contrast(graded).enhance(1.08)
    graded = ImageEnhance.Brightness(graded).enhance(0.96)
    # subtle analog film grain
    noise = Image.effect_noise(base.size, 18).convert("RGB")
    graded = Image.blend(graded, ImageChops.overlay(graded, noise), 0.12)
    # honour strength (blend back toward the untouched original)
    strength = max(0.0, min(1.0, strength))
    out = Image.blend(base, graded, strength)
    buf = _bytes_io()
    out.save(buf, format="PNG")
    return buf.getvalue()


def cutout_subject(photo: Path):
    """Remove the background from a photo LOCALLY with rembg. Returns an RGBA image
    with the subject preserved and the background transparent. This is segmentation
    only - the subject's pixels (face, body) are never altered or AI-redrawn."""
    if not photo.is_file():
        sys.exit(f"Photo not found: {photo}")
    try:
        from rembg import remove
    except ModuleNotFoundError:
        sys.exit("rembg not installed. Run: python3 -m pip install rembg")
    src = Image.open(photo).convert("RGBA")
    print("Removing background locally (rembg). First run downloads a model (~170MB); the photo stays on your machine.")
    return remove(src).convert("RGBA")


def _add_grain(img: Image.Image, amount: float = 0.05) -> Image.Image:
    """Overlay subtle film grain to unify a composite. Texture only, no color change."""
    from PIL import ImageChops

    noise = Image.effect_noise(img.size, 18).convert("RGB")
    return Image.blend(img, ImageChops.overlay(img, noise), max(0.0, min(1.0, amount)))


def _grade_rgba(rgba: Image.Image, strength: float) -> Image.Image:
    """Optional LIGHT palette grade on a cut-out for compositing cohesion. Recolors
    toward the brand palette but preserves facial structure (tonal remap, not feature
    editing). Strength 0..1; alpha preserved."""
    rgb = rgba.convert("RGB")
    gray = rgb.convert("L")
    lut_r, lut_g, lut_b = _palette_luts()
    graded = Image.merge("RGB", (gray.point(lut_r), gray.point(lut_g), gray.point(lut_b)))
    blended = Image.blend(rgb, graded, max(0.0, min(1.0, strength)))
    blended.putalpha(rgba.getchannel("A"))
    return blended


def composite_scene(
    client, photo: Path, background: str, model: str, size: str,
    palette: str = DEFAULT_PALETTE, scale: float = 0.78, blend: float = 0.0,
    options: dict | None = None,
) -> bytes:
    """Mode: composite. Put a real photo's cut-out subject onto a generated Inch of
    Shadow background. Face and body are REAL pixels (rembg, local); only the
    background is generated. The photo never goes to OpenAI."""
    subj = cutout_subject(photo)  # RGBA, untouched subject
    bg_bytes = generate_art(client, background, model, size, None, palette, options)
    bg = Image.open(_bytes_io(bg_bytes)).convert("RGB")
    bw, bh = bg.size
    target_h = max(1, int(bh * scale))
    ratio = target_h / subj.height
    subj = subj.resize((max(1, int(subj.width * ratio)), target_h), Image.LANCZOS)
    if blend and blend > 0:
        subj = _grade_rgba(subj, blend)
    x = (bw - subj.width) // 2
    y = bh - subj.height
    comp = bg.copy()
    comp.paste(subj.convert("RGB"), (x, y), subj.getchannel("A"))
    comp = _add_grain(comp, 0.05)
    out = _bytes_io()
    comp.save(out, format="PNG")
    return out.getvalue()


def parse_args():
    parser = ArgumentParser(description="Generate or restyle images for Inch of Shadow.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_art = sub.add_parser("art", help="Text to image in the artist voice.")
    p_art.add_argument("subject", help="What the image shows.")

    p_re = sub.add_parser("restyle", help="Restyle one of your own photos.")
    p_re.add_argument("photo", type=Path, help="Path to your source image.")
    p_re.add_argument("instruction", help="How to restyle it.")

    p_card = sub.add_parser("card", help="Art plus a drawn title and wordmark.")
    p_card.add_argument("subject", help="What the background shows.")
    p_card.add_argument("--title", required=True, help="Title text to draw.")
    p_card.add_argument("--wordmark", default="Inch of Shadow", help="Artist name line, drawn as written.")
    p_card.add_argument("--mood", default="M2",
                        help="Colour mood from docs/brand/frame.md (M2 default, A, C, E, F, M3, M4, M6).")

    p_grade = sub.add_parser(
        "grade",
        help="Local Inch of Shadow colour grade on your own photo (no AI, face untouched).",
    )
    p_grade.add_argument("photo", type=Path, help="Path to your photo.")
    p_grade.add_argument(
        "--strength", type=float, default=0.9, help="Grade intensity 0..1 (default 0.9)."
    )
    p_grade.add_argument(
        "--project", metavar="NAME", help="File under generated_images/NAME/."
    )
    p_grade.add_argument(
        "--no-open", action="store_true", help="Do not open Finder when done."
    )

    p_comp = sub.add_parser(
        "composite",
        help="Put your real cut-out photo on a generated IoS background (face untouched, local).",
    )
    p_comp.add_argument("photo", type=Path, help="Your photo (clear subject).")
    p_comp.add_argument(
        "background",
        help="The background scene to generate, no figure (e.g. 'an empty concrete room, shaft of light').",
    )
    p_comp.add_argument(
        "--scale", type=float, default=0.78,
        help="Subject height as a fraction of the background (default 0.78).",
    )
    p_comp.add_argument(
        "--blend", type=float, default=0.0,
        help="0..1 light palette grade on your cut-out for cohesion (default 0 = keep your real colors).",
    )

    for p in (p_art, p_re, p_card, p_comp):
        p.add_argument(
            "--size",
            choices=list(SIZE_PRESETS),
            default="square",
            help="Aspect preset (default square).",
        )
        p.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI image model id.")
        p.add_argument(
            "--project",
            metavar="NAME",
            help="File the image under generated_images/NAME/ (e.g. a release name).",
        )
        p.add_argument(
            "--no-open",
            action="store_true",
            help="Do not open the output folder in Finder when done.",
        )

    # References guide the generated look; relevant to art and card (which
    # generates art). Repeatable. Drop your files in references/.
    for p in (p_art, p_card):
        p.add_argument(
            "--reference",
            metavar="PATH",
            action="append",
            help="Reference image to match the look (repeatable).",
        )

    # Per-release palette (core stays constant). A name in palettes/ or inline text.
    for p in (p_art, p_re, p_card, p_comp):
        p.add_argument(
            "--palette",
            metavar="NAME",
            default=DEFAULT_PALETTE,
            help=f"Per-release palette: a name in palettes/ or inline text (default {DEFAULT_PALETTE}).",
        )
        # Per-image options from options/<kind>/. Id prefix, full name, or inline text.
        for kind in SINGLE_OPTION_KINDS:
            p.add_argument(f"--{kind}", metavar="NAME", help=f"A {kind} option from options/{kind}/.")
        p.add_argument(
            "--motif", metavar="NAME", action="append", help="A motif from options/motif/ (repeatable)."
        )
        p.add_argument(
            "--print-prompt",
            action="store_true",
            help="Print the prompt that would be sent and stop (no API call, no cost).",
        )

    sub.add_parser("options", help="List every option name per kind.")

    return parser.parse_args()


def chosen_options(args) -> dict:
    """Collect the per-image option flags from parsed args."""
    chosen = {kind: getattr(args, kind) for kind in SINGLE_OPTION_KINDS}
    chosen["motif"] = args.motif or []
    return chosen


def main():
    args = parse_args()

    if args.mode == "options":
        for kind in SINGLE_OPTION_KINDS + MULTI_OPTION_KINDS:
            print(f"{kind}: {', '.join(available_options(kind))}")
        return

    if args.mode != "grade":
        options = chosen_options(args)
        if args.print_prompt:
            if args.mode in ("art", "card"):
                print(art_prompt(args.subject, args.palette, options, args.reference))
            elif args.mode == "restyle":
                print(restyle_prompt(args.instruction, args.palette, options))
            else:
                print(art_prompt(args.background, args.palette, options))
            return

    if args.mode == "grade":
        # Local, no API, no key needed. Face and composition untouched.
        data = grade_photo(args.photo, args.strength)
        path = save_bytes(data, f"grade-{args.photo.stem}", args.project)

    else:
        size = SIZE_PRESETS[args.size]
        client = get_client()

        if args.mode == "art":
            data = generate_art(client, args.subject, args.model, size, args.reference, args.palette, options)
            path = save_bytes(data, args.subject, args.project)

        elif args.mode == "restyle":
            print("Note: restyle uploads your source photo to OpenAI's servers.")
            data = restyle_photo(client, args.photo, args.instruction, args.model, size, args.palette, options)
            path = save_bytes(data, f"restyle-{args.photo.stem}", args.project)

        elif args.mode == "card":
            art = generate_art(client, args.subject, args.model, size, args.reference, args.palette, options)
            data = draw_card(art, args.title, args.wordmark, args.mood)
            path = save_bytes(data, f"card-{args.title}", args.project)

        elif args.mode == "composite":
            print("Note: only the BACKGROUND is generated by OpenAI; your photo stays local (rembg).")
            data = composite_scene(
                client, args.photo, args.background, args.model, size,
                args.palette, args.scale, args.blend, options,
            )
            path = save_bytes(data, f"composite-{args.photo.stem}", args.project)

        else:  # pragma: no cover
            sys.exit(f"Unknown mode: {args.mode}")

    print(f"Saved: {path}")

    # Pop the output folder in Finder, matching the resizer's behavior.
    if not args.no_open:
        subprocess.run(["open", str(path.parent)], check=False)


if __name__ == "__main__":
    main()
