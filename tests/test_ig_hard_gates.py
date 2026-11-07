"""Tests for the IG hard gates added 2026-07-05 (audit P1-4, findings 2+3).

Before this fix: 'never 2 IG scripts same day' had zero enforcement
(stats.last_session was written but never read), the PAUSE_AFTER_*
cooldown config was dead (referenced by no code), and --no-preflight
bypassed every gate on live runs.
"""
from datetime import date, datetime, timedelta, timezone

import scene_intelligence.ig_engagement as ig

TODAY = date(2026, 7, 5)
NOW = datetime(2026, 7, 5, 10, 0, tzinfo=timezone.utc)


class FakeCfg:
    PAUSE_AFTER_SOFT_BLOCK = 48
    PAUSE_AFTER_HARD_BLOCK = 72
    PAUSE_AFTER_CAPTCHA = 72
    PAUSE_AFTER_VERIFICATION = 0


def _tracker(last_session):
    return {"stats": {"last_session": last_session}}


# --- same_day_guard ---

def test_blocks_when_tracker_last_session_is_today():
    blocked, why = ig.same_day_guard(_tracker("2026-07-05T09:12:00+00:00"), [], TODAY)
    assert blocked and "last_session" in why


def test_allows_when_last_session_was_yesterday():
    blocked, _ = ig.same_day_guard(_tracker("2026-07-04T11:00:00+00:00"), [], TODAY)
    assert not blocked


def test_blocks_when_live_report_started_today():
    reports = [{"started_at": "2026-07-05T08:00:00Z", "dry_run": False}]
    blocked, why = ig.same_day_guard(_tracker(None), reports, TODAY)
    assert blocked and "session_reports" in why


def test_dry_run_report_today_does_not_block():
    reports = [{"started_at": "2026-07-05T08:00:00Z", "dry_run": True}]
    blocked, _ = ig.same_day_guard(_tracker(None), reports, TODAY)
    assert not blocked


def test_unparseable_last_session_does_not_crash():
    blocked, _ = ig.same_day_guard(_tracker("not-a-date"), [], TODAY)
    assert not blocked


# --- detection_cooldown_guard: REMOVED 2026-09-01 (T-015). The live
# detection gate is ig_ops_guards.active_detection_cooldown, covered by
# test_ops_guards_and_ledger.py. same_day_guard tests above still apply
# to the preflight tracker-source check.
