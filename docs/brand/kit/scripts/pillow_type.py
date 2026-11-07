#!/usr/bin/env python3
"""Brand type for still images made with Pillow.

Pillow has no letter-spacing, and every still needs it (title 0.03em, name 0.05em, small
0.24em), so this draws tracked text once, the same way everywhere.

    from pillow_type import font, draw_tracked, tracked_width
    f = font(450, "The Deceiver")                   # the brand face from frame.md at 450px
    w = tracked_width("The Deceiver", f, 0.03)
    draw_tracked(img, (x, y), "The Deceiver", f, fill="#D6D1C8", tracking_em=0.03,
                 shadow=True)                        # shadow only on photos
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.dont_write_bytecode = True


sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame_tokens import face_files  # noqa: E402


def _has_all_glyphs(f: ImageFont.FreeTypeFont, text: str) -> bool:
    def bmp(ch):
        im = Image.new("L", (f.size * 2, f.size * 2), 0)
        ImageDraw.Draw(im).text((f.size // 4, f.size // 4), ch, font=f, fill=255)
        return im.tobytes()
    missing = bmp("\uE123")                      # a code point no text font draws
    return all(c.isspace() or bmp(c) != missing for c in set(text))


def font(px: int, text: str = "", path: Path = None) -> ImageFont.FreeTypeFont:
    """The brand face from frame.md at this size. Give the text too: a face that cannot
    draw every character of it (trial files often lack punctuation) is skipped and the
    fallback face is used for the whole string, never a mix of two faces in one word."""
    if path:
        return ImageFont.truetype(str(path), px)
    faces = face_files()
    for fam, fpath in faces:
        f = ImageFont.truetype(str(fpath), px)
        if not text or _has_all_glyphs(f, text):
            return f
        print(f"note: {fam} cannot draw every character of {text!r}; using the next face", file=sys.stderr)
    return ImageFont.truetype(str(faces[-1][1]), px)


def tracked_width(text: str, f, tracking_em: float) -> float:
    gap = f.size * tracking_em
    return sum(f.getlength(c) for c in text) + gap * (len(text) - 1)


def draw_tracked(img: Image.Image, xy, text: str, f, fill, tracking_em: float,
                 shadow: bool = False) -> None:
    """Draw text with letter-spacing. shadow=True adds the one approved soft shadow
    (0 2px 24px rgba(15,13,12,0.55) on a 1080px-wide canvas, scaled to this canvas)."""
    x, y = xy
    gap = f.size * tracking_em
    if shadow:
        k = img.size[0] / 1080
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        cx = x
        for c in text:
            d.text((cx, y + 2 * k), c, font=f, fill=(15, 13, 12, 140))
            cx += f.getlength(c) + gap
        layer = layer.filter(ImageFilter.GaussianBlur(12 * k))
        img.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(img)
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += f.getlength(c) + gap
