"""Gate fix 1 (Amir 2026-11-15, "Dispatcher smaller"): on the six IG sweep days
the provider audit takes 60 fewer names and the SI contact re-check is skipped,
so ~85 calls stay free for the 16:00 sweep fetch. Every other day is unchanged."""
from datetime import date

import pytest

import scene_intelligence.ig_dispatcher as D


@pytest.fixture
def jobs(monkeypatch):
    ran = []
    monkeypatch.setattr(D, "_run_job", lambda cmd, label, dry_run: ran.append((label, cmd)) or "ok")
    monkeypatch.setattr(D, "_log", lambda *a, **k: None)
    monkeypatch.setattr(D, "_local_hygiene", lambda today, dry_run: None)
    monkeypatch.setattr(D, "_seed_yield_report", lambda today: None)
    monkeypatch.setattr(D, "provider_budget_left", lambda today: 300)
    monkeypatch.setattr(D, "follow_lists_age_days", lambda today: 1)
    monkeypatch.setattr(D, "stale_contacts_count", lambda today: 500)
    monkeypatch.setattr(D, "vetted_pool_depth", lambda: 5)
    monkeypatch.setattr(D, "unvetted_pending", lambda: 1000)
    monkeypatch.setattr(D, "provider_requests_left", lambda: None)
    monkeypatch.setattr(D, "provider_plan", lambda *a: {"audit": 100, "builder": []})
    return ran


def _audit_count(ran):
    cmd = next(c for label, c in ran if label == "freshness audit")
    return int(cmd[cmd.index("--count") + 1])


def test_sweep_days_are_exactly_the_six_run_dates():
    import scene_intelligence.ig_sweep as S
    assert list(D.SWEEP_DAYS) == S.RUN_DATES
    assert D.is_sweep_day(date(2026, 11, 17)) and not D.is_sweep_day(date(2026, 11, 18))
    assert not D.is_sweep_day(date(2026, 12, 1))


@pytest.mark.parametrize("day", D.SWEEP_DAYS)
def test_sweep_day_cuts_audit_and_skips_reenrich(jobs, day):
    D._provider_day(date.fromisoformat(day), dry_run=True)
    assert _audit_count(jobs) == 40
    assert "contact re-enrichment" not in [label for label, _c in jobs]


@pytest.mark.parametrize("day", ["2026-11-16", "2026-11-18", "2026-11-30"])
def test_other_days_unchanged(jobs, day):
    D._provider_day(date.fromisoformat(day), dry_run=True)
    assert _audit_count(jobs) == 100
    assert "contact re-enrichment" in [label for label, _c in jobs]


def test_audit_cut_never_negative():
    assert D.sweep_day_audit(date(2026, 11, 17), 30) == 0
    assert D.sweep_day_audit(date(2026, 11, 18), 30) == 30
