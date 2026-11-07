from __future__ import annotations

from pathlib import Path
import pytest
from stats.ig_followback import cohorts, since_may_pct, followers_from_export

TRACKER = {"active_follows": [{"username": "A", "followed_at": "2026-09-03T10:00"}, {"username": "b", "followed_at": "2026-09-10"}],
           "unfollowed_history": [{"username": "c", "followed_date": "2026-08-02"}, {"username": "nodate"}, {"username": "d", "followed_date": "2026-11-20"}]}


def test_cohorts_count_tracker_follows_by_month_against_the_export():
    c = cohorts(TRACKER, {"a", "c"}, export_date="2026-10-10")
    assert c["2026-09"] == {"followed": 2, "back": 1, "pct": 50.0}
    assert c["2026-08"] == {"followed": 1, "back": 1, "pct": 100.0}
    assert c["2026-11"]["pct"] is None                       # cohort after the export, review focus 4
    assert "nodate" not in str(c)
    assert since_may_pct(c) == pytest.approx(66.7, abs=0.1)   # 2 back of 3 dated follows at or before the export


ROOT = Path(__file__).resolve().parent.parent
EXPORTS_1010 = sorted(d for d in (ROOT / "data").glob("instagram-inch_of_shadow-2026-10-10-*") if d.is_dir())


def test_export_month_cohort_is_partial_with_no_pct():
    c = cohorts(TRACKER, {"a"}, export_date="2026-09-30")
    assert c["2026-09"] == {"followed": 2, "back": 1, "pct": None, "partial": True}
    assert since_may_pct(c) == 0.0          # only the completed August cohort counts


@pytest.mark.skipif(not EXPORTS_1010, reason="10-10 export not on this machine")
def test_reproduces_the_2026_10_10_analysis():
    import json
    d = EXPORTS_1010[0]                    # resolved explicitly, not the newest export
    tracker = json.loads((ROOT / "scene_intelligence" / "ig_follow_tracker.json").read_text())
    c = cohorts(tracker, followers_from_export(d), export_date="2026-10-10")
    assert (c["2026-05"]["followed"], c["2026-05"]["back"]) == (54, 14)
    assert (c["2026-06"]["followed"], c["2026-06"]["back"]) == (91, 16)
    assert (c["2026-07"]["followed"], c["2026-07"]["back"]) == (81, 18)
    assert (c["2026-08"]["followed"], c["2026-08"]["back"]) == (35, 7)
    assert (c["2026-09"]["followed"], c["2026-09"]["back"]) == (58, 17)
    assert round(since_may_pct(c)) == 23
