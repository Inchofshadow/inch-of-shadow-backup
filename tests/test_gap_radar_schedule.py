"""Income 5: Gap Radar weekly schedule (spend gate, plan, ledger). No network, no Claude."""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gap_radar"))
import schedule as sch  # noqa: E402


# --- schedule ---------------------------------------------------------------------------

S = {"weekly": [], "monthly": [], "estimate_usd": {"analysis": 1.1, "crowding": 8.0},
     "radar_cap_usd_month": 30, "ios_reserve_usd_month": 60}


def test_gate_blocks_until_caps_set():
    assert "caps not set" in sch.gate(dict(S, radar_cap_usd_month=None), 0, 0, 150, 1)
    assert "caps not set" in sch.gate(dict(S, ios_reserve_usd_month=None), 0, 0, 150, 1)


def test_gate_radar_cap_and_ios_reserve():
    assert sch.gate(S, 10, 50, 150, 5) == ""
    assert "radar cap" in sch.gate(S, 28, 50, 150, 5)
    assert "Inch of Shadow reserve" in sch.gate(S, 10, 88, 150, 5)    # 88+5 > 150-60


def test_monthly_only_first_week_and_crowding_estimate():
    s = dict(S, weekly=["a"], monthly=["b"])
    assert sch.plan(s, date(2026, 11, 3)) == (["a", "b"], True)
    assert sch.plan(s, date(2026, 11, 12)) == (["a"], False)
    assert sch.plan(s, date(2026, 11, 12), force_monthly=True) == (["a", "b"], True)
    assert sch.estimate({"crowding": True}, S["estimate_usd"], True) == pytest.approx(9.1)
    assert sch.estimate({"crowding": True}, S["estimate_usd"], False) == pytest.approx(1.1)


def test_radar_spend_reads_ledger():
    led = {"months": {"2026-11": {"usd": 40, "by": {"gap_radar_x": {"usd": 3}, "copy": {"usd": 1}}}}}
    assert sch.radar_spend(led, "2026-11") == 3 and sch.total_spend(led, "2026-11") == 40
    assert sch.radar_spend({}, "2026-11") == 0


def test_real_schedule_file_has_amirs_caps():
    s = sch.load_schedule()
    assert isinstance(s["radar_cap_usd_month"], (int, float)) and isinstance(s["ios_reserve_usd_month"], (int, float))
    assert s["min_days_between_runs"] >= 1
    assert not set(s["paused"]) & set(s["weekly"])


def test_too_soon_waits_after_a_recent_run():
    st = {"last_run": "2026-11-06"}
    assert "2 day(s) ago" in sch.too_soon(st, date(2026, 11, 8), 5)      # Sunday after a Friday run
    assert sch.too_soon(st, date(2026, 11, 15), 5) == ""
    assert sch.too_soon({}, date(2026, 11, 8), 5) == ""
    assert sch.too_soon(st, date(2026, 11, 8), 0) == ""
