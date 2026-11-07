"""print_looks.py: the style library as a tool (board ticket Look-11).

Synthetic photo only. Each look must keep the input size, give the same print for the
same photo, really change the picture, and the rejected look must stay out.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import print_looks as pl  # noqa: E402


@pytest.fixture(scope="module")
def photo():
    # a dark portrait-like gradient with a bright side, like the shoot photos
    y, x = np.mgrid[0:600, 0:400].astype(np.float32)
    lum = np.clip((x / 400) * 0.9 * np.exp(-((y - 250) / 260) ** 2), 0, 1)
    rgb = np.stack([lum * 255, lum * 200, lum * 160], -1).astype(np.uint8)
    return Image.fromarray(rgb)


def test_library_is_the_looks_amir_picked():
    # S1-S7 picked 2026-09-20; S8-S10 (dither family) picked 2026-10-13 on his photo
    assert list(pl.LOOKS) == ["xerox", "halftone", "riso", "engraving",
                              "cyanotype", "solarisation", "pictorialism",
                              "dither", "scanlines", "pixel",
                              "halation", "window", "crt", "softclub", "emboss",
                              "ascii", "vhs", "anaglyph", "thermal", "nightvision",
                              "pixelsort", "blowout", "monotint", "monotintnight",
                              "nightflash", "camcorder"]
    assert "screenprint" not in pl.LOOKS          # rejected: breaks a face into blotches
    codes = [f"S{i}" for i in range(1, 26)]
    codes.insert(23, "S23b")                      # the night setting of S23 Monotint
    assert [v[0] for v in pl.LOOKS.values()] == codes


def test_mosaic_blocks_only_the_box(photo):
    out = pl.mosaic(photo, (100, 200, 120, 120))
    a, b = np.asarray(photo, np.int16), np.asarray(out, np.int16)
    assert (a[:200] == b[:200]).all() and (a[:, :100] == b[:, :100]).all()
    assert np.abs(a[200:320, 100:220] - b[200:320, 100:220]).sum() > 0


@pytest.mark.parametrize("look", list(pl.LOOKS))
def test_each_look_keeps_size_and_changes_the_picture(photo, look):
    out = pl.apply_look(photo, look)
    assert out.size == photo.size and out.mode == "RGB"
    if look == "pixel":
        # pixelation barely moves a smooth gradient; what it must do is cut the palette
        assert len(out.getcolors(maxcolors=4096) or []) <= 12, "pixel kept too many colours"
    else:
        diff = np.abs(np.asarray(out, np.int16) - np.asarray(photo, np.int16)).mean()
        assert diff > 4, f"{look} barely changed the picture"
    assert np.asarray(out).std() > 8, f"{look} produced a flat image"


@pytest.mark.parametrize("look", list(pl.LOOKS))
def test_same_photo_gives_the_same_print(photo, look):
    a = np.asarray(pl.apply_look(photo, look))
    b = np.asarray(pl.apply_look(photo, look))
    assert (a == b).all()


def test_looks_scale_with_the_photo(photo):
    big = photo.resize((1600, 2400))
    out = pl.apply_look(big, "halftone")
    assert out.size == (1600, 2400)


def test_unknown_look_is_refused(photo):
    with pytest.raises(ValueError):
        pl.apply_look(photo, "screenprint")


def test_sheet_is_written(tmp_path, photo):
    out = pl.sheet(photo, tmp_path / "sheet.jpg")
    assert out.is_file() and Image.open(out).size[0] > 1000
