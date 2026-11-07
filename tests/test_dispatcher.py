"""Dispatcher decision table (T-003). Every branch is a logged decision."""
import json
from datetime import datetime

import scene_intelligence.ig_dispatcher as disp


# 2026-09-14: the real repo has HIKERAPI_KEY in .env, which flips the dispatcher
# into provider mode and would also make provider_requests_left() hit the
# network. Tests of the IG-law path must see "no provider" unless they opt in.
import pytest as _pytest
import scene_intelligence.ig_data_provider as _dp
import scene_intelligence.ig_dispatcher as _disp


@_pytest.fixture(autouse=True)
def _no_provider_by_default(monkeypatch):
    monkeypatch.setattr(_dp, "available", lambda: False)
    monkeypatch.setattr(_disp, "provider_requests_left", lambda: None)
    # SI upkeep (2026-11-04) reads the real SI file and ledger; off unless opted in.
    monkeypatch.setattr(_disp, "follow_lists_age_days", lambda d: 0)
    monkeypatch.setattr(_disp, "stale_contacts_count", lambda d: 0)



def _setup(monkeypatch, tmp_path, *, pause=None, cooldown=None,
           pool=50, builder_age=5, export_age=3, stale_contacts=0):
    monkeypatch.setattr(disp, "LOG_PATH", tmp_path / "dispatch-log.md")
    monkeypatch.setattr(disp, "_notify", lambda *a: None)
    monkeypatch.setattr(disp, "vetted_pool_depth", lambda: pool)
    monkeypatch.setattr(disp, "builder_age_days", lambda d: builder_age)
    monkeypatch.setattr(disp, "newest_export_age_days", lambda d: export_age)
    monkeypatch.setattr(disp, "stale_contacts_count", lambda d: stale_contacts)
    monkeypatch.setattr(disp, "bulk_job_yesterday", lambda d: None)
    monkeypatch.setattr(disp, "_local_hygiene", lambda *a, **k: None)
    # Isolate the REAL queue file: the T-013 cursor branch reads/writes
    # QUEUE_PATH, and on 2026-09-01 the suite (dry_run=False + stubbed
    # _run_job) advanced the production cursor to 28 from inside pytest.
    qf = tmp_path / "queue.json"
    qf.write_text('{"_meta": {"builder_seed_cursor": 0}, "queue": []}',
                  encoding="utf-8")
    monkeypatch.setattr(disp, "QUEUE_PATH", qf)

    import scene_intelligence.ig_ops_guards as guards
    monkeypatch.setattr(guards, "get_pause", lambda p="ig", **k: pause)
    monkeypatch.setattr(guards, "active_detection_cooldown",
                        lambda now=None, **k: cooldown)
    ran = []
    monkeypatch.setattr(disp, "_run_job",
                        lambda cmd, label, dry: ran.append(label) or "ok")
    return ran


def _logtext(tmp_path):
    return (tmp_path / "dispatch-log.md").read_text(encoding="utf-8")


TUE_10 = datetime(2026, 9, 1, 10, 0)     # quiet day
MON_10 = datetime(2026, 8, 31, 10, 0)    # session day
SUN_10 = datetime(2026, 8, 30, 10, 0)
TUE_23 = datetime(2026, 9, 1, 23, 0)


def test_pause_skips_everything(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pause={"paused_by": "amir", "at": "x"})
    disp.decide_and_run(TUE_10)
    assert not ran and "paused" in _logtext(tmp_path)


def test_cooldown_skips(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path,
                 cooldown=({"date": "2026-08-31", "type": "t"},
                           datetime(2026, 9, 2, 0, 0)))
    disp.decide_and_run(TUE_10)
    assert not ran and "cooldown" in _logtext(tmp_path)


def test_night_skips(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path)
    disp.decide_and_run(TUE_23)
    assert not ran and "daytime" in _logtext(tmp_path)


def test_sunday_off(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path)
    disp.decide_and_run(SUN_10)
    assert not ran and "Sunday" in _logtext(tmp_path)


def test_session_day_reserved_no_api(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pool=0)  # even with a starving pool
    disp.decide_and_run(MON_10)
    assert not ran and "session day" in _logtext(tmp_path)


def test_quiet_day_low_pool_runs_audit(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pool=10)
    disp.decide_and_run(TUE_10)
    assert ran == ["freshness audit"]
    assert "vetted pool 10 < 30" in _logtext(tmp_path)


def test_builder_outranks_audit_when_both_fire(monkeypatch, tmp_path):
    """2026-08-31 priority fix: with pool low AND builder overdue, the builder
    runs first so the next audit vets FRESH candidates, not the stale tail
    (the 09-01 situation: pool 19, builder 16d, six new seeds uncrawled)."""
    ran = _setup(monkeypatch, tmp_path, pool=10, builder_age=20)
    disp.decide_and_run(TUE_10)
    assert ran == ["queue builder"]


def test_quiet_day_stale_contacts_run_reenrichment(monkeypatch, tmp_path):
    """Registry Part 4: with supply healthy, the quiet day goes to contact
    re-enrichment batches until the stale estate is refreshed."""
    ran = _setup(monkeypatch, tmp_path, pool=50, builder_age=5,
                 stale_contacts=473)
    disp.decide_and_run(TUE_10)
    assert ran == ["contact re-enrichment"]
    assert "473 contacts" in _logtext(tmp_path)


def test_quiet_day_old_builder_runs_builder(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pool=50, builder_age=20)
    disp.decide_and_run(TUE_10)
    assert ran == ["queue builder"]


def test_quiet_day_nothing_needed_is_logged(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pool=50, builder_age=5)
    disp.decide_and_run(TUE_10)
    assert not ran and "nothing needed" in _logtext(tmp_path)


def test_stale_export_notifies_but_does_not_block(monkeypatch, tmp_path):
    ran = _setup(monkeypatch, tmp_path, pool=10, export_age=45)
    disp.decide_and_run(TUE_10)
    txt = _logtext(tmp_path)
    assert "notify-amir" in txt and "45 days old" in txt
    assert ran == ["freshness audit"]  # the day's job still runs


def test_export_age_parses_real_folder_names(tmp_path, monkeypatch):
    monkeypatch.setattr(disp, "DATA_DIR", tmp_path)
    (tmp_path / "instagram-inch_of_shadow-2026-08-30-NsEqnjWQ").mkdir()
    from datetime import date
    assert disp.newest_export_age_days(date(2026, 9, 10)) == 11


def test_rest_day_after_builder(monkeypatch, tmp_path):
    """2026-09-02 'more calculated': the day after a builder crawl is an API
    rest day even when triggers fire (every throttle followed bulk enumeration)."""
    ran = _setup(monkeypatch, tmp_path, pool=10, builder_age=20)
    monkeypatch.setattr(disp, "bulk_job_yesterday", lambda d: "ig_queue_builder")
    disp.decide_and_run(TUE_10)
    assert not ran and "rest day" in _logtext(tmp_path)


def test_run_job_keeps_stderr_on_failure(monkeypatch, tmp_path):
    """2026-09-05: the audit's exit reason (stderr) was lost behind stdout."""
    import subprocess
    import scene_intelligence.ig_dispatcher as d

    def fake_run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 1, stdout="[1/30] checking @x...",
                                          stderr="[AUDIT] Session expired (HTTP 401).")
    monkeypatch.setattr(d.subprocess, "run", fake_run)
    monkeypatch.setattr(d, "_notify", lambda *a, **k: None)
    out = d._run_job(["python3", "x.py"], "freshness audit", dry_run=False)
    assert "HTTP 401" in out and "checking @x" in out


# --- provider mode (2026-09-14) ------------------------------------------------

def test_provider_plan_backlog_audit_and_no_builder():
    import scene_intelligence.ig_dispatcher as d
    plan = d.provider_plan(pool=12, unvetted=749, seeds_ranked=[("a", 50, 5)], all_seeds=["a", "b"])
    assert plan["audit"] == 100 and plan["builder"] == []


def test_provider_plan_steady_audit_and_builder_when_low():
    import scene_intelligence.ig_dispatcher as d
    ranked = [("good", 40, 8), ("meh", 40, 1)]
    plan = d.provider_plan(pool=12, unvetted=150, seeds_ranked=ranked, all_seeds=["meh", "good", "new1", "new2"])
    assert plan["audit"] == 60
    assert plan["builder"][:3] == ["good", "new1", "meh"]  # best yield first, a fresh seed interleaved


def test_provider_plan_nothing_when_healthy():
    import scene_intelligence.ig_dispatcher as d
    plan = d.provider_plan(pool=45, unvetted=500, seeds_ranked=[], all_seeds=["a"])
    assert plan == {"audit": 0, "builder": []}


def test_provider_day_runs_on_a_session_day_despite_ig_cooldown(monkeypatch, tmp_path):
    import scene_intelligence.ig_dispatcher as d
    import scene_intelligence.ig_data_provider as dp
    q = tmp_path / "q.json"
    q.write_text(json.dumps({"_meta": {}, "queue": [{"username": "u%d" % i, "status": "pending"} for i in range(400)]}))
    monkeypatch.setattr(d, "QUEUE_PATH", q)
    monkeypatch.setattr(d, "vetted_pool_depth", lambda: 12)
    monkeypatch.setattr(d, "get_pause", lambda p: None, raising=False)
    monkeypatch.setattr(dp, "available", lambda: True)
    monkeypatch.setattr(d, "_local_hygiene", lambda t, dr: None)
    monkeypatch.setattr(d, "_seed_yield_report", lambda t: None)
    logged = []
    monkeypatch.setattr(d, "_log", lambda dec, why, outcome="": logged.append((dec, why, outcome)))
    jobs = []
    monkeypatch.setattr(d, "_run_job", lambda cmd, label, dr: jobs.append((label, cmd)) or "exit 0")
    from datetime import datetime
    rc = d.decide_and_run(datetime(2026, 9, 14, 9, 30), dry_run=False)  # Monday, inside the 429 cooldown
    assert rc == 0
    assert [j[0] for j in jobs] == ["freshness audit"]
    assert "--count" in jobs[0][1] and jobs[0][1][-1] == "100"
    assert any("provider" in l[0] for l in logged)


def test_provider_day_shrinks_to_balance(monkeypatch, tmp_path):
    import scene_intelligence.ig_dispatcher as d
    import scene_intelligence.ig_data_provider as dp
    q = tmp_path / "q.json"
    q.write_text(json.dumps({"_meta": {}, "queue": [{"username": "u%d" % i, "status": "pending"} for i in range(400)]}))
    monkeypatch.setattr(d, "QUEUE_PATH", q)
    monkeypatch.setattr(d, "vetted_pool_depth", lambda: 12)
    monkeypatch.setattr(dp, "available", lambda: True)
    monkeypatch.setattr(d, "provider_requests_left", lambda: 90)
    monkeypatch.setattr(d, "_local_hygiene", lambda t, dr: None)
    monkeypatch.setattr(d, "_notify", lambda *a: None)
    logged = []; jobs = []
    monkeypatch.setattr(d, "_log", lambda dec, why, outcome="": logged.append((dec, why)))
    monkeypatch.setattr(d, "_run_job", lambda cmd, label, dr: jobs.append(cmd) or "exit 0")
    from datetime import datetime
    d.decide_and_run(datetime(2026, 9, 15, 9, 30), dry_run=False)
    assert jobs and jobs[0][-1] == "45"                      # 90 requests -> 45 candidates
    assert any("balance low" in why for _d, why in logged)  # Amir is told to top up


# --- SI upkeep on provider days (2026-11-04, SI-01/SI-02) ----------------------

def _upkeep(monkeypatch, left, stale, lists_age):
    import scene_intelligence.ig_dispatcher as d
    monkeypatch.setattr(d, "provider_budget_left", lambda t: left)
    monkeypatch.setattr(d, "stale_contacts_count", lambda t: stale)
    monkeypatch.setattr(d, "follow_lists_age_days", lambda t: lists_age)
    logged, jobs = [], []
    monkeypatch.setattr(d, "_log", lambda dec, why, outcome="": logged.append((dec, why)))
    monkeypatch.setattr(d, "_run_job", lambda cmd, label, dr: jobs.append((label, cmd)) or "exit 0")
    return d, logged, jobs


def test_upkeep_reenrich_uses_full_batch_when_room(monkeypatch):
    from datetime import date
    d, logged, jobs = _upkeep(monkeypatch, left=300, stale=533, lists_age=1)
    assert d._provider_si_upkeep(date(2026, 11, 4), False, None) is True
    assert [j[0] for j in jobs] == ["contact re-enrichment"] and jobs[0][1][-1] == "40"


def test_upkeep_never_exceeds_cap_or_balance(monkeypatch):
    from datetime import date
    d, logged, jobs = _upkeep(monkeypatch, left=300, stale=533, lists_age=1)
    d._provider_si_upkeep(date(2026, 11, 4), False, 12)          # balance 12 < cap
    assert jobs[0][1][-1] == "12"
    d, logged, jobs = _upkeep(monkeypatch, left=3, stale=533, lists_age=1)
    assert d._provider_si_upkeep(date(2026, 11, 4), False, None) is False
    assert not jobs and any("re-check waits" in w for _d, w in logged)


def test_upkeep_monthly_follow_flags_first_then_smaller_batch(monkeypatch):
    from datetime import date
    d, logged, jobs = _upkeep(monkeypatch, left=100, stale=533, lists_age=31)
    d._provider_si_upkeep(date(2026, 11, 4), False, None)
    assert [j[0] for j in jobs] == ["SI follow flags", "follow-back verification", "contact re-enrichment"]
    assert "--apply" in jobs[0][1] and jobs[2][1][-1] == "15"   # 100 - 85


def test_upkeep_skips_follow_flags_without_room(monkeypatch):
    from datetime import date
    d, logged, jobs = _upkeep(monkeypatch, left=40, stale=0, lists_age=None)
    assert d._provider_si_upkeep(date(2026, 11, 4), False, None) is False
    assert not jobs
