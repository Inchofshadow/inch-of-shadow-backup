#!/usr/bin/env python3
"""A Letter for Listeners: set Amir's text as a carousel (board ticket Formats-06).

    letter_slides.py letter.txt --title "Record Name" --mood M2
    letter_slides.py letter.txt --texture artwork/cover.jpg      # the record's own art
    letter_slides.py --budget                                    # how much text fits

The Letter is a piece of poetry reflecting the period of life a record comes from, for an
EP or an album, never a single. It is NOT a thank-you and NOT a making-of. Amir writes the
words; this only sets them. The rule he gave: it takes something from the record's own cover
art, so it speaks the same visual language.

The text file is plain UTF-8. A BLANK LINE starts a new slide. Line breaks inside a slide
are kept exactly as written, because line breaks are part of a poem.

Type and colour come from docs/brand/frame.md, so this follows the brand with nothing
retyped. Every size below survives the render-and-shrink check at Instagram's feed width;
run `--budget` to see the numbers.
"""
from __future__ import annotations

import sys
import textwrap
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import image_generator as ig  # noqa: E402  (brand_font, brand_tokens)

W, H = 1080, 1440              # 3:4, the carousel shape that fills the grid tile
SIDES = 96                     # wider than a reel's 65: a page wants a margin
TOP, BOTTOM = 150, 150
BODY_PX = 40                   # 14.4pt on a 390px phone feed, checked
TITLE_PX = 86
SMALL_PX = 32                  # 11.6pt: labels only, never the poem
LINE = 1.62                    # line height, loose enough to read a poem
OUT = ROOT / "generated_images" / "letter"


def moods() -> dict:
    return ig.brand_tokens()["moods"]


def ink_ground(mood: str) -> tuple:
    m = moods()[mood]
    return _hex(m["light"]), _hex(m["dark"]), m["name"]


def _hex(s: str) -> tuple:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def slides_from(text: str) -> list:
    """Blank line starts a new slide; line breaks inside a slide are kept."""
    out, cur = [], []
    for raw in text.splitlines():
        if raw.strip():
            cur.append(raw.rstrip())
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def wrap(lines: list, font, max_w: int) -> list:
    """Wrap only the lines that are too wide. A poem's own breaks come first."""
    out = []
    for line in lines:
        if font.getlength(line) <= max_w or not line.strip():
            out.append(line)
            continue
        words, cur = line.split(), ""
        for word in words:
            trial = f"{cur} {word}".strip()
            if font.getlength(trial) <= max_w or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = word
        if cur:
            out.append(cur)
    return out


def ground(dark: tuple, texture: Path | None) -> Image.Image:
    """The page. With --texture, the record's own art is dimmed and blurred underneath it,
    which is Amir's rule: the Letter borrows from the cover, it does not repeat it."""
    img = Image.new("RGB", (W, H), dark)
    if not texture:
        return img
    art = ImageOps.exif_transpose(Image.open(texture)).convert("RGB")
    art = ImageOps.fit(art, (W, H), Image.LANCZOS)
    art = art.filter(ImageFilter.GaussianBlur(30))
    # a dark cover would vanish under the page, so lift it first, then dim it on purpose
    art = ImageOps.autocontrast(art, cutoff=1)
    art = ImageEnhance.Color(art).enhance(0.6)
    art = ImageEnhance.Brightness(art).enhance(0.5)
    page = Image.blend(img, art, 0.75)
    # a soft scrim so the words never fight the picture
    scrim = Image.new("RGB", (W, H), dark)
    return Image.blend(page, scrim, 0.35)


def line_width(line, font, tracking):
    return sum(font.getlength(c) for c in line) + font.size * tracking * max(0, len(line) - 1)


def draw_block(img, lines, font, fill, top, tracking=0.0, align="centre"):
    """align="centre" centres every line, for the title page.

    align="poem" sets the lines FLUSH LEFT and centres the block as a whole. A poem is
    written to a left edge: its line breaks are the writing. Centring every line makes the
    wrap remainders float and turns it into a greeting card, which is the opposite of the
    Cohen booklet and the Ovid title page this is drawn from."""
    d = ImageDraw.Draw(img)
    step = round(font.size * LINE)
    left = None
    if align == "poem":
        widest = max((line_width(l, font, tracking) for l in lines), default=0)
        left = max(SIDES, (W - widest) / 2)
    y = top
    for line in lines:
        x = left if left is not None else (W - line_width(line, font, tracking)) / 2
        for c in line:
            d.text((x, y), c, font=font, fill=fill)
            x += font.getlength(c) + font.size * tracking
        y += step
    return y


def title_slide(title: str, mood: str, texture=None) -> Image.Image:
    """Set like a book title page, not a sleeve: the Ovid reference (Castellar with Diotima
    Italic). Small label, the record's name, a rule, then the words A Letter for Listeners."""
    ink, dark, _ = ink_ground(mood)
    img = ground(dark, texture)
    f_small = ig.brand_font(SMALL_PX, "INCH OF SHADOW")
    f_title = ig.brand_font(TITLE_PX, title)
    draw_block(img, ["INCH OF SHADOW"], f_small, ink, 330, tracking=0.24)
    y = draw_block(img, wrap([title], f_title, W - 2 * SIDES), f_title, ink, 470)
    d = ImageDraw.Draw(img)
    d.line([(W / 2 - 110, y + 46), (W / 2 + 110, y + 46)], fill=ink, width=2)
    f_lab = ig.brand_font(SMALL_PX + 6, "A Letter for Listeners")
    draw_block(img, ["A Letter for Listeners"], f_lab, ink, y + 96, tracking=0.12)
    return img


def text_slide(lines: list, mood: str, texture=None) -> Image.Image:
    ink, dark, _ = ink_ground(mood)
    img = ground(dark, texture)
    font = ig.brand_font(BODY_PX, " ".join(lines))
    wrapped = wrap(lines, font, W - 2 * SIDES)
    block_h = round(font.size * LINE) * len(wrapped)
    draw_block(img, wrapped, font, ink, max(TOP, (H - block_h) // 2), align="poem")
    return img, len(wrapped)


ALPHABET = "abcdefghijklmnopqrstuvwxyz "
POEM_CHARS = "abc,'-?."           # the punctuation a poem cannot do without


def budget() -> None:
    """How much text fits on one slide, measured, not guessed.

    Measured for EVERY face on disk, because a poem carries commas and apostrophes and the
    Ogg trial file has none: `brand_font` then falls back to Marcellus for the whole string.
    Until the Ogg licence is bought, plan the Letter on the Marcellus numbers."""
    usable_w, usable_h = W - 2 * SIDES, H - TOP - BOTTOM
    phone_pt, small_pt = BODY_PX * 390 / W, SMALL_PX * 390 / W
    print(f"canvas {W}x{H}, margins {SIDES} sides / {TOP} top / {BOTTOM} bottom")
    print(f"body {BODY_PX}px = {phone_pt:.1f}pt on a 390px phone feed"
          f"   {'OK' if phone_pt >= 11 else 'TOO SMALL'} (minimum 11pt)")
    print(f"labels {SMALL_PX}px = {small_pt:.1f}pt"
          f"   {'OK' if small_pt >= 11 else 'TOO SMALL'}\n")
    for family, path in ig.brand_faces():
        from PIL import ImageFont
        font = ImageFont.truetype(str(path), BODY_PX)
        step = round(font.size * LINE)
        max_lines = usable_h // step
        chars = int(usable_w / (font.getlength(ALPHABET) / len(ALPHABET)))
        words = max(1, int(chars / 5.6))
        note = "" if ig._draws_all(font, POEM_CHARS) else \
            "   <- this file cannot draw , ' - ? so a poem falls back to the next face"
        print(f"{family}:{note}")
        print(f"  {max_lines} lines a slide, about {chars} characters or {words} words a line")
        print(f"  => about {max_lines * words} words a slide, "
              f"{19 * max_lines * words} for a whole 20-slide carousel\n")


def main() -> None:
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="?", type=Path, help="the Letter, plain UTF-8, blank line = new slide")
    ap.add_argument("--title", help="the record's name, sets the title page")
    ap.add_argument("--mood", default="M2", help="a mood from frame.md (default M2)")
    ap.add_argument("--texture", type=Path, help="the record's cover art, dimmed under the page")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--budget", action="store_true", help="how much text fits, then stop")
    a = ap.parse_args()

    if a.budget or not a.text:
        budget()
        return
    if a.mood not in moods():
        sys.exit(f"Unknown mood {a.mood}. Moods: {', '.join(moods())}")

    a.out.mkdir(parents=True, exist_ok=True)
    blocks = slides_from(a.text.read_text(encoding="utf-8"))
    if not blocks:
        sys.exit(f"{a.text} has no text.")

    n = 0
    if a.title:
        title_slide(a.title, a.mood, a.texture).save(a.out / "01_title.png")
        n = 1
        print(f"01_title.png  {a.title}")
    over = []
    for i, block in enumerate(blocks, start=n + 1):
        img, lines = text_slide(block, a.mood, a.texture)
        img.save(a.out / f"{i:02d}_slide.png")
        fits = (H - TOP - BOTTOM) // round(ig.brand_font(BODY_PX).size * LINE)
        flag = ""
        if lines > fits:
            over.append(i)
            flag = f"   OVER by {lines - fits} lines, split this one"
        print(f"{i:02d}_slide.png  {lines} lines{flag}")
    print(f"\n{len(blocks) + n} slides in {a.out}")
    if over:
        print(f"TOO LONG: slides {', '.join(map(str, over))}. Put a blank line in to split them.")
    if len(blocks) + n > 20:
        print(f"Instagram takes 20 slides; this is {len(blocks) + n}.")


if __name__ == "__main__":
    main()
