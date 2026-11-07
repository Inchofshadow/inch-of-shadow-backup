"""Shared IG daily ledger (audit P1-7, finding 8).

One IG API-calling script per day across the whole toolchain. Claims are
written before the first API call; a second script the same day is refused
with exit code 4 unless overridden; unreadable ledgers fail closed.
"""
import json

import pytest

import scene_intelligence.ig_daily_ledger as dl
from datetime import datetime

# Fixed daytime clock (2026-08-31): the 2.0 hours gate (09:00-21:00)
# made these tests time-dependent -- green by day, red after 21:00,
# which the nightly watchdog test run would flag every night.
DAY_NOON = datetime(2026, 7, 19, 12, 0)


def _runs(path):
    return json.loads(path.read_text())["runs"]


def test_first_claim_writes_entry(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19", now=DAY_NOON)
    runs = _runs(p)
    assert len(runs) == 1
    assert runs[0]["script"] == "ig_queue_builder"
    assert runs[0]["date"] == "2026-07-19"
    assert runs[0]["override"] is False


def test_second_claim_same_day_refused_with_exit_4(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_followback_checker", path=p, today="2026-07-19", now=DAY_NOON)
    with pytest.raises(SystemExit) as exc:
        dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)
    assert exc.value.code == dl.EXIT_REFUSED
    # refused run must NOT be recorded
    assert len(_runs(p)) == 1


def test_override_allows_and_marks_entry(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_followback_checker", path=p, today="2026-07-19", now=DAY_NOON)
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-19",
                       override=True, reason="test", now=DAY_NOON)
    runs = _runs(p)
    assert len(runs) == 2
    assert runs[1]["script"] == "ig_engagement"
    assert runs[1]["override"] is True


def test_new_day_claims_freely(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-20", now=DAY_NOON)
    assert len(_runs(p)) == 2


def test_override_without_prior_run_not_marked(tmp_path):
    # --override-ledger passed defensively on the day's first run
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-19",
                       override=True, now=DAY_NOON)
    assert _runs(p)[0]["override"] is False


def test_unreadable_ledger_fails_closed(tmp_path):
    p = tmp_path / "ledger.json"
    p.write_text("{not json")
    with pytest.raises(SystemExit) as exc:
        dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)
    assert exc.value.code == dl.EXIT_REFUSED


def test_wrong_shape_fails_closed(tmp_path):
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps({"runs": "nope"}))
    with pytest.raises(SystemExit):
        dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)


def test_old_entries_pruned(tmp_path):
    p = tmp_path / "ledger.json"
    old = {"runs": [{"date": "2026-01-01", "script": "x", "ts": "t"}]}
    p.write_text(json.dumps(old))
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)
    dates = [r["date"] for r in _runs(p)]
    assert "2026-01-01" not in dates
    assert "2026-07-19" in dates


def test_runs_on_reads_only(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_engagement", path=p, today="2026-07-19", now=DAY_NOON)
    assert dl.runs_on("2026-07-19", path=p)[0]["script"] == "ig_engagement"
    assert dl.runs_on("2026-07-18", path=p) == []


# --- 2026-09-03 amendment: the override is NOT a rerun button ------------
# Background: 2026-09-01 the builder ran twice in one day via --override-ledger
# and IG answered with a 429 the next morning -> 48h cooldown, two sessions
# lost. Rule: no override re-runs the SAME script, and no override runs a
# second BULK crawl on a bulk day. Overrides also require a logged reason.

def test_override_cannot_rerun_same_script_same_day(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19", now=DAY_NOON)
    with pytest.raises(SystemExit) as exc:
        dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19",
                           override=True, reason="Amir: go", now=DAY_NOON)
    assert exc.value.code == dl.EXIT_REFUSED
    assert len(_runs(p)) == 1


def test_override_cannot_stack_two_bulk_jobs(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19", now=DAY_NOON)
    with pytest.raises(SystemExit) as exc:
        dl.check_and_claim("ig_audit_queue_freshness", path=p, today="2026-07-19",
                           override=True, reason="Amir: go", now=DAY_NOON)
    assert exc.value.code == dl.EXIT_REFUSED
    assert len(_runs(p)) == 1


def test_override_requires_reason(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19", now=DAY_NOON)
    with pytest.raises(SystemExit) as exc:
        dl.check_and_claim("ig_followback_checker", path=p, today="2026-07-19",
                           override=True, now=DAY_NOON)
    assert exc.value.code == dl.EXIT_REFUSED
    assert len(_runs(p)) == 1


def test_override_with_reason_allows_non_bulk_after_bulk_and_logs_it(tmp_path):
    p = tmp_path / "ledger.json"
    dl.check_and_claim("ig_queue_builder", path=p, today="2026-07-19", now=DAY_NOON)
    dl.check_and_claim("ig_followback_checker", path=p, today="2026-07-19",
                       override=True, reason="Amir: go 14:30 (planned combo)",
                       now=DAY_NOON)
    runs = _runs(p)
    assert len(runs) == 2
    assert runs[1]["override"] is True
    assert runs[1]["override_reason"] == "Amir: go 14:30 (planned combo)"
