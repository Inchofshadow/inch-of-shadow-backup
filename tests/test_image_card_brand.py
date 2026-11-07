"""image_generator.py card mode reads the brand from docs/brand/frame.md (Machine-02).

Before 2026-09-20 the card drew Helvetica capitals in white and blue-grey. Now: Marcellus,
mixed case, the title over the artist name, colours from the chosen mood.
"""
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import image_generator as ig  # noqa: E402


def art(w=1080, h=1350, colour=(120, 110, 100)):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), colour).save(buf, format="PNG")
    return buf.getvalue()


def test_brand_tokens_come_from_frame_md():
    t = ig.brand_tokens()
    assert t["moods"]["M2"]["light"].upper() == "#D6D1C8"
    assert t["moods"]["M2"]["dark"].upper() == "#0F0D0C"
    assert t["typography"]["title"]["fontFamily"] == t["face"]["family"]
    assert t["face"]["fallback"]["family"] == "Marcellus"


def test_brand_font_comes_from_the_face_block():
    # the trial file of the face is not under version control, so either may lead
    families = [fam for fam, _ in ig.brand_faces()]
    assert families[-1] == "Marcellus"
    assert ig.brand_font(60).getname()[0].split()[0] in {f.split()[0] for f in families}


def test_text_the_face_cannot_draw_falls_back_whole():
    # Marcellus draws the handle; a trial face without @ and _ must not be used for it
    f = ig.brand_font(60, "@inch_of_shadow")
    assert ig._draws_all(f, "@inch_of_shadow")


def test_card_keeps_size_and_uses_the_mood_ink():
    out = Image.open(io.BytesIO(ig.draw_card(art(), "The Deceiver", mood="M3"))).convert("RGB")
    assert out.size == (1080, 1350)
    ink = tuple(int(ig.brand_tokens()["moods"]["M3"]["light"][i:i + 2], 16) for i in (1, 3, 5))
    colours = {c for _, c in out.getcolors(maxcolors=1 << 24)}
    assert ink in colours, "the title is not drawn in the mood's light colour"
    assert (255, 255, 255) not in colours, "pure white type is the old off-brand card"


def test_unknown_mood_is_refused():
    with pytest.raises(ValueError):
        ig.draw_card(art(), "X", mood="ZZ")


def test_title_is_not_forced_to_capitals():
    assert ig.card_lines("The Deceiver", "Inch of Shadow") == ("The Deceiver", "Inch of Shadow")
