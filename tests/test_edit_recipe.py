"""edit_recipe: the parts that shape a grade, tested without the drive."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import edit_recipe as er  # noqa: E402


def test_families_from_the_light_tag():
    assert er.family_of("direct flash, black and white") == "bw"      # black and white wins over flash
    assert er.family_of("direct flash, colour (L9)") == "flash"
    assert er.family_of("flash at blue hour (L9 + L5)") == "flash"
    assert er.family_of("blue hour, pink sky (L5)") == "bluehour"
    assert er.family_of("soft dusk, green cast") == "dusk"
    assert er.family_of("L3 golden hour, dappled leaf shadows") == "day"


def test_identity_lut_changes_nothing():
    g = np.linspace(0, 1, er.N)
    lut = np.stack(np.meshgrid(g, g, g, indexing="ij"), axis=-1)
    img = np.random.default_rng(1).integers(0, 256, (8, 8, 3), dtype=np.uint8)
    assert np.abs(er.apply_lut(img, lut).astype(int) - img).max() <= 1


def test_levelling_moves_brightness_to_the_target_and_keeps_order():
    rng = np.random.default_rng(2)
    dark = rng.integers(0, 40, (4000, 3)).astype(np.uint8)            # an underexposed frame
    target = np.array([5, 15, 60, 110, 160, 215, 240], float)
    out = er.level(dark, er.level_curve(er.luma(dark), target))
    assert abs(np.median(er.luma(out)) - 110) < 12                    # the median lands on the target's
    order_before = np.argsort(er.luma(dark)[:200], kind="stable")
    assert np.all(np.diff(er.luma(out)[:200][order_before]) >= -1e-6)  # brighter stays brighter


def test_a_black_frame_does_not_blow_up():
    black = np.zeros((500, 3), np.uint8)
    out = er.level(black, er.level_curve(er.luma(black), np.array([5, 15, 60, 110, 160, 215, 240], float)))
    assert np.isfinite(out).all() and out.max() <= 255


def test_darker_and_brighter_sit_either_side_of_auto():
    W = np.zeros((8, 7)); W[0] = [5, 15, 60, 110, 160, 215, 240]      # a model that always predicts this spread
    lum = np.full(100, 50.0)
    d, a, b = (er.predict_target(lum, W, k) for k in ("darker", "auto", "brighter"))
    assert (d <= a).all() and (a <= b).all() and d[3] < a[3] < b[3]
    assert np.all(np.diff(a) >= 0)


def test_cube_file_is_well_formed(tmp_path):
    g = np.linspace(0, 1, er.N)
    lut = np.stack(np.meshgrid(g, g, g, indexing="ij"), axis=-1)
    f = tmp_path / "x.cube"
    er.write_cube(lut, f, "test")
    lines = f.read_text().splitlines()
    assert lines[1] == f"LUT_3D_SIZE {er.N}"
    rows = [l for l in lines if l and l[0].isdigit()]
    assert len(rows) == er.N ** 3
    assert rows[1].startswith("0.062500 0.000000 0.000000")           # red runs fastest, as .cube requires
