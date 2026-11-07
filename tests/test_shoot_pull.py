"""shoot_pull: where a crop lands, tested without the drive."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shoot_pull as sp  # noqa: E402

PORTRAIT, LANDSCAPE = (5504, 8256), (8256, 5504)


def inside(box, size, subject):
    x, y = subject[0] * size[0], subject[1] * size[1]
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def test_every_format_has_the_right_shape_and_stays_in_the_frame():
    for size in (PORTRAIT, LANDSCAPE):
        for f, (tw, th, _) in sp.FORMATS.items():
            l, t, r, b = sp.crop_box(size, f, (0.5, 0.3, "head"))
            assert 0 <= l < r <= size[0] and 0 <= t < b <= size[1]
            assert abs((r - l) / (b - t) - tw / th) < 0.01


def test_the_head_is_inside_the_crop_even_at_the_edges_of_the_frame():
    for subject in ((0.08, 0.1, "h"), (0.92, 0.9, "h"), (0.5, 0.7, "h"), (0.78, 0.68, "h")):
        for size in (PORTRAIT, LANDSCAPE):
            for f in sp.FORMATS:
                assert inside(sp.crop_box(size, f, subject), size, subject), (f, size, subject)


def test_a_portrait_crop_follows_him_sideways_in_a_landscape_frame():
    left = sp.crop_box(LANDSCAPE, "reel", (0.25, 0.3, "h"))
    right = sp.crop_box(LANDSCAPE, "reel", (0.75, 0.3, "h"))
    assert left[0] < right[0]


def test_rotated_finds_map_back_to_the_upright_frame():
    # a point at the top-left of the frame, seen after one counter-clockwise quarter turn
    w, h = 400, 300
    assert sp._rot_point(0, 0, w, h, 0) == (0, 0)
    x, y = sp._rot_point(10, 389, h, w, 1)          # rot90 of a 400x300 frame is 300 wide, 400 tall
    assert (x, y) == (10, 10)
