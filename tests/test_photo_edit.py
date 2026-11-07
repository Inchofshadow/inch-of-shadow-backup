"""The photo editor's maths: identity is a no-op, geometry sizes are right, tone is monotonic."""
import numpy as np
from PIL import Image

from release_manager import photo_edit as pe


def gradient(w=120, h=80):
    x = np.linspace(0, 255, w, dtype=np.uint8)[None, :, None].repeat(h, 0).repeat(3, 2)
    x[..., 1] = np.linspace(0, 255, h, dtype=np.uint8)[:, None]
    return Image.fromarray(x)


def test_identity_changes_nothing():
    im = gradient()
    out = pe.apply(im, {})
    assert out.size == im.size and np.array_equal(np.asarray(out), np.asarray(im))


def test_crop_quarter_turn_and_mirror_sizes():
    im = gradient(120, 80)
    assert pe.apply(im, {"crop": {"x": .25, "y": .25, "w": .5, "h": .5}}).size == (60, 40)
    assert pe.apply(im, {"rot": 1}).size == (80, 120)
    m = np.asarray(pe.apply(im, {"flip": True}))
    assert np.array_equal(m[:, 0], np.asarray(im)[:, -1])


def test_straighten_keeps_the_frame_covered():
    im = Image.new("RGB", (200, 100), (200, 50, 50))
    out = np.asarray(pe.apply(im, {"angle": 12}))
    assert out.shape[:2] == (100, 200) and out.min(axis=(0, 1))[0] > 150      # no empty (black) corners
    assert pe.cover_scale(200, 100, 0) == 1.0 and pe.cover_scale(200, 100, 12) > 1.0


def test_tone_moves_the_right_way_and_clamps():
    base = np.full((1, 3, 3), 0.4, np.float32)
    p = pe.clean_params({"exposure": .5})
    assert pe.tone(base.copy(), p).mean() > .4
    p = pe.clean_params({"saturation": -1})
    col = np.array([[[0.8, 0.2, 0.2]]], np.float32)
    s = pe.tone(col.copy(), p)
    assert np.allclose(s[..., 0], s[..., 1], atol=1e-5)                        # fully desaturated
    assert pe.clean_params({"exposure": 9, "angle": 99, "crop": {"x": -1, "w": 5}})["exposure"] == 1.0
