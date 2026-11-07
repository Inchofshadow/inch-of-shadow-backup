"""shoot_catalogue: the parts that decide a link, tested without the drive."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shoot_catalogue as sc  # noqa: E402

RAWS = {
    "Outdoor/A/Raw/DSC_1.NEF": {"captured": "2026-08-26T21:27:11.060"},
    "Outdoor/A/Raw/DSC_2.NEF": {"captured": "2026-08-26T21:27:11.840"},
    "Outdoor/A/Raw/DSC_3.NEF": {"captured": "2026-08-26T21:27:30.000"},
    "Outdoor/A/Raw/DSC_4.NEF": {"captured": None},
}


def test_candidates_keep_only_raws_within_the_window():
    got = sc.candidates(datetime(2026, 8, 26, 21, 27, 11, 60000), RAWS)
    assert got == ["Outdoor/A/Raw/DSC_1.NEF", "Outdoor/A/Raw/DSC_2.NEF"]


def test_candidates_come_nearest_first():
    got = sc.candidates(datetime(2026, 8, 26, 21, 27, 11, 800000), RAWS)
    assert got[0].endswith("DSC_2.NEF")


def test_a_raw_without_a_capture_time_is_never_a_candidate():
    assert not any(c.endswith("DSC_4.NEF") for c in sc.candidates(datetime(2026, 8, 26, 21, 27, 11), RAWS))


def test_classify_clear_winner_is_verified():
    assert sc.classify(120, 13) == "verified"


def test_classify_a_burst_is_ambiguous_not_verified():
    # out-204 on 2026-09-21: 646 against 634 inliers, the image cannot choose
    assert sc.classify(646, 634) == "ambiguous"


def test_classify_weak_match_is_only_likely():
    assert sc.classify(15, 3) == "likely"


def test_classify_nothing_is_unmatched():
    assert sc.classify(4, 0) == "unmatched"


def test_cache_name_is_flat_and_reversible_enough():
    p = sc.cache_path("Outdoor/Outdoor Shoot 4/Raw/DSC_6813.NEF")
    assert p.name == "Outdoor__Outdoor Shoot 4__Raw__DSC_6813.NEF.jpg"


def test_upright_rotates_only_flagged_orientations():
    from PIL import Image
    im = Image.new("RGB", (40, 20))
    assert sc.upright(im, 1).size == (40, 20)
    assert sc.upright(im, 8).size == (20, 40)
    assert sc.upright(im, 6).size == (20, 40)
    assert sc.upright(im, 3).size == (40, 20)


# ---- by-image (Look-13): edits without a capture time

def test_by_image_edges_settle_a_burst():
    # indoor -12 on 2026-10-14: the true frame 0.96, its burst neighbours 0.24 and below
    got = sc.classify_by_image([("A", 734, 0.96), ("B", 401, 0.22), ("C", 315, 0.13)])
    assert got[0] == "verified" and got[1][0] == "A"


def test_by_image_edges_beat_the_inlier_count():
    got = sc.classify_by_image([("B", 400, 0.30), ("A", 380, 0.95)])
    assert got[0] == "verified" and got[1][0] == "A"


def test_by_image_near_tie_is_ambiguous():
    # outdoor -112: the wrong frame led by 0.011
    assert sc.classify_by_image([("A", 483, 0.524), ("B", 470, 0.513)])[0] == "ambiguous"


def test_by_image_dark_frame_with_few_features_is_only_likely():
    assert sc.classify_by_image([("A", 13, 0.80)])[0] == "likely"


def test_by_image_nothing_shared_is_unmatched():
    assert sc.classify_by_image([])[0] == "unmatched"
    assert sc.classify_by_image([("A", 5, 0.9)])[0] == "unmatched"
