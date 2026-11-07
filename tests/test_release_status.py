import datetime
import scene_intelligence.release_status as rs


def test_detect_stage_by_date_offset():
    today = datetime.date(2026, 5, 15)
    def rel(date, **kw):
        return {"release_date": date, **kw}
    assert rs.detect_stage(rel("2026-06-30"), today) == "plan"        # >14d before
    assert rs.detect_stage(rel("2026-05-22"), today) == "prep"        # within 14d before
    assert rs.detect_stage(rel("2026-05-15"), today) == "release_day" # release day
    assert rs.detect_stage(rel("2026-05-05"), today) == "capture"     # 10d after
    assert rs.detect_stage(rel("2026-03-01"), today) == "post_mortem" # >25d after


def test_detect_stage_explicit_override_wins():
    today = datetime.date(2026, 5, 15)
    r = {"release_date": "2026-05-15", "stage": "post_mortem"}
    assert rs.detect_stage(r, today) == "post_mortem"


def test_detect_stage_no_date_defaults_plan():
    assert rs.detect_stage({}, datetime.date(2026, 5, 15)) == "plan"


def test_match_ig_media_date_window():
    media = [
        {"permalink": "a", "timestamp": "2026-05-15T17:13:17+0000"},  # release day -> in
        {"permalink": "b", "timestamp": "2026-05-30T10:00:00+0000"},  # +15d -> in
        {"permalink": "c", "timestamp": "2026-01-29T10:00:00+0000"},  # months before -> out
        {"permalink": "d", "timestamp": "2026-07-01T10:00:00+0000"},  # +47d -> out
    ]
    got = [m["permalink"] for m in rs.match_ig_media(media, "2026-05-15")]
    assert got == ["a", "b"]


def test_promotion_funnel_counts_statuses():
    campaign = {"targets": [
        {"status": "sent"}, {"status": "sent"}, {"status": "replied"},
        {"status": "rejected"}, {"status": "bounced"},
    ]}
    f = rs.promotion_funnel(campaign)
    assert f["total"] == 5
    assert f["by_status"]["sent"] == 2
    assert f["by_status"]["replied"] == 1


def test_promotion_funnel_empty():
    assert rs.promotion_funnel({})["total"] == 0
