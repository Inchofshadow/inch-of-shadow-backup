"""The 2.0 hard gates + ledger law (T-003, Amir-approved 2026-08-30).

Covers review finding L1 (pauses/cooldowns enforced by nothing) and L2/L3
(sessions invisible to the ledger; per-endpoint budgets replace the flat
one-script rule + 150 cap)."""
import json
from datetime import datetime

import pytest

import scene_intelligence.ig_ops_guards as guards
import scene_intelligence.ig_daily_ledger as ledger


# --- pause gate --------------------------------------------------------------

def _write(p, data):
    p.write_text(json.dumps(data), encoding="utf-8")


def test_pause_blocks(tmp_path):
    f = tmp_path / "autonomy_state.json"
    _write(f, {"pauses": {"ig": {"reason": "test rest", "at": "x", "paused_by": "amir"}}})
    with pytest.raises(SystemExit) as e:
        guards.require_not_paused("ig", path=f)
    assert e.value.code == guards.EXIT_PAUSED


def test_no_pause_passes(tmp_path):
    f = tmp_path / "autonomy_state.json"
    _write(f, {"pauses": {"ig": None, "sc": None}})
    guards.require_not_paused("ig", path=f)


def test_legacy_global_paused_key_still_blocks(tmp_path):
    # The 08-29 hole: a caller reading only the dead legacy key passed a real
    # pause. The guard honors BOTH shapes.
    f = tmp_path / "autonomy_state.json"
    _write(f, {"paused": True, "paused_reason": "legacy"})
    with pytest.raises(SystemExit):
        guards.require_not_paused("ig", path=f)


def test_unreadable_pause_file_fails_closed(tmp_path):
    f = tmp_path / "autonomy_state.json"
    f.write_text("{not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        guards.require_not_paused("ig", path=f)


def test_missing_pause_file_passes(tmp_path):
    guards.require_not_paused("ig", path=tmp_path / "absent.json")


# --- detection cooldown gate -------------------------------------------------

NOW = datetime(2026, 8, 31, 12, 0)


def test_recent_event_blocks(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-30", "platform": "instagram",
                           "type": "anything"}]})
    with pytest.raises(SystemExit) as e:
        guards.require_no_cooldown(NOW, path=f)
    assert e.value.code == guards.EXIT_COOLDOWN


def test_old_event_clears(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-01", "platform": "instagram",
                           "type": "anything"}]})
    guards.require_no_cooldown(NOW, path=f)


def test_other_platform_ignored(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-30", "platform": "soundcloud",
                           "type": "datadome_captcha"}]})
    guards.require_no_cooldown(NOW, path=f)


def test_per_type_window_from_config(tmp_path):
    # session_invalidated... has a 48h window in config: end of 08-28 + 48h
    # = 08-31 00:00 -> clear at NOW (12:00); the 72h default would block.
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-28", "platform": "instagram",
                           "type": "session_invalidated_after_roster_enumeration"}]})
    guards.require_no_cooldown(NOW, path=f)
    _write(f, {"events": [{"date": "2026-08-28", "platform": "instagram",
                           "type": "unknown_type_uses_default_72h"}]})
    with pytest.raises(SystemExit):
        guards.require_no_cooldown(NOW, path=f)


# --- daytime law -------------------------------------------------------------

@pytest.mark.parametrize("hour,ok", [(8, False), (9, True), (14, True),
                                     (20, True), (21, False), (2, False)])
def test_daytime_window(hour, ok):
    now = datetime(2026, 8, 31, hour, 30)
    if ok:
        guards.require_daytime(now)
    else:
        with pytest.raises(SystemExit) as e:
            guards.require_daytime(now)
        assert e.value.code == guards.EXIT_NIGHT


def test_daytime_override():
    guards.require_daytime(datetime(2026, 8, 31, 2, 0), override=True)


# --- ledger v2: kinds, budgets, ceiling -------------------------------------

DAY = "2026-08-31"
NOON = datetime(2026, 8, 31, 12, 0)


def claim(path, script="s1", **kw):
    kw.setdefault("path", path)
    kw.setdefault("today", DAY)
    kw.setdefault("now", NOON)
    return ledger.check_and_claim(script, **kw)


def test_api_claim_records_fields(tmp_path):
    p = tmp_path / "ledger.json"
    claim(p, "ig_audit_queue_freshness", est_calls=25, endpoint="profile_reads")
    runs = ledger.runs_on(DAY, p)
    assert runs[0]["kind"] == "api" and runs[0]["est_calls"] == 25
    assert runs[0]["endpoint"] == "profile_reads"


def test_second_api_job_refused_and_override_allows(tmp_path):
    p = tmp_path / "ledger.json"
    claim(p, "a", est_calls=5, endpoint="friendship_checks")
    with pytest.raises(SystemExit) as e:
        claim(p, "b", est_calls=5, endpoint="friendship_checks")
    assert e.value.code == ledger.EXIT_REFUSED
    claim(p, "b", est_calls=5, endpoint="friendship_checks", override=True, reason="test")
    assert len(ledger.runs_on(DAY, p)) == 2


def test_browser_claim_neither_blocks_nor_is_blocked(tmp_path):
    p = tmp_path / "ledger.json"
    claim(p, "ig_session", kind="browser")
    claim(p, "checker", est_calls=10, endpoint="friendship_checks")  # not refused
    claim(p, "ig_session_2", kind="browser")                         # not refused
    total, per = ledger.day_call_totals(DAY, p)
    assert total == 10  # browser entries contribute zero


def test_browser_claim_allowed_at_night(tmp_path):
    p = tmp_path / "ledger.json"
    ledger.check_and_claim("ig_session", kind="browser", path=p, today=DAY,
                           now=datetime(2026, 8, 31, 23, 0))


def test_api_claim_refused_at_night(tmp_path):
    p = tmp_path / "ledger.json"
    with pytest.raises(SystemExit):
        ledger.check_and_claim("x", est_calls=1, path=p, today=DAY,
                               now=datetime(2026, 8, 31, 23, 0))


def test_endpoint_budget_enforced_across_claims(tmp_path):
    p = tmp_path / "ledger.json"
    claim(p, "a", est_calls=20, endpoint="profile_reads")
    with pytest.raises(SystemExit):
        claim(p, "b", est_calls=15, endpoint="profile_reads", override=True, reason="test")
    claim(p, "b", est_calls=10, endpoint="profile_reads", override=True, reason="test")


def test_roster_walk_banned_even_with_override(tmp_path):
    p = tmp_path / "ledger.json"
    with pytest.raises(SystemExit):
        claim(p, "backfill", est_calls=1, endpoint="roster_walk", override=True, reason="test")


def test_hard_ceiling_no_override(tmp_path):
    p = tmp_path / "ledger.json"
    with pytest.raises(SystemExit):
        claim(p, "big", est_calls=151, override=True, reason="test")


def test_soft_target_warns_but_allows(tmp_path, capsys):
    p = tmp_path / "ledger.json"
    claim(p, "a", est_calls=60)
    out = capsys.readouterr().out
    assert "normal-day target" in out
    assert len(ledger.runs_on(DAY, p)) == 1


def test_ledger_file_stays_valid_json(tmp_path):
    p = tmp_path / "ledger.json"
    claim(p, "a", est_calls=1)
    json.loads(p.read_text(encoding="utf-8"))


# --- 2026-09-06: API-surface throttles do not block browser sessions --------
# Three 48h cooldowns (09-02, 09-05, 09-06) never cleared a profile-read 429;
# meanwhile sessions -- which click in Amir's real Chrome and never touch the
# API -- were coupled to it by our own rule. Decoupled on Amir's "Go".

def test_api_throttle_blocks_api_kind_only(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-30", "platform": "instagram",
                           "type": "rate_limited_429_profile_reads"}]})
    with pytest.raises(SystemExit):
        guards.require_no_cooldown(NOW, path=f, kind="api")
    guards.require_no_cooldown(NOW, path=f, kind="session")  # clicks allowed


def test_account_level_event_blocks_sessions_too(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [{"date": "2026-08-30", "platform": "instagram",
                           "type": "datadome_captcha"}]})
    with pytest.raises(SystemExit):
        guards.require_no_cooldown(NOW, path=f, kind="session")
    with pytest.raises(SystemExit):
        guards.require_no_cooldown(NOW, path=f, kind="api")


def test_active_cooldown_session_kind_ignores_api_events(tmp_path):
    f = tmp_path / "detection_events.json"
    _write(f, {"events": [
        {"date": "2026-08-30", "platform": "instagram",
         "type": "rate_limited_429_profile_reads"},
        {"date": "2026-08-01", "platform": "instagram",
         "type": "datadome_captcha"}]})
    assert guards.active_detection_cooldown(NOW, path=f, kind="session") is None
    hit = guards.active_detection_cooldown(NOW, path=f, kind="api")
    assert hit and hit[0]["type"] == "rate_limited_429_profile_reads"


def test_429_cooldown_is_seven_days():
    # 2026-09-06: 48h was a guess and three of them in a row failed.
    assert guards._cooldown_hours_for("rate_limited_429_profile_reads") == 168


# --- SC cooldown law (Amir, 2026-09-09) -------------------------------------
# A SoundCloud challenge Amir clears himself is not a platform block. SC events
# freeze nothing unless he approved an explicit cooldown. IG is unaffected.

def _sc_events(tmp_path, events):
    import json
    f = tmp_path / "detection_events.json"
    f.write_text(json.dumps({"events": events}))
    return f


def test_sc_event_without_approval_imposes_no_freeze(tmp_path):
    from datetime import date
    f = _sc_events(tmp_path, [{"date": date.today().isoformat(),
                               "platform": "soundcloud",
                               "type": "datadome_captcha"}])
    assert guards.active_detection_cooldown(platform="sc", path=f) is None
    guards.require_no_cooldown(platform="sc", path=f)     # must not raise


def test_sc_event_with_amir_approved_hours_does_freeze(tmp_path):
    from datetime import date
    f = _sc_events(tmp_path, [{"date": date.today().isoformat(),
                               "platform": "soundcloud",
                               "type": "action_block",
                               "cooldown_hours": 72,
                               "cooldown_approved_by": "amir"}])
    hit = guards.active_detection_cooldown(platform="sc", path=f)
    assert hit is not None
    with pytest.raises(SystemExit):
        guards.require_no_cooldown(platform="sc", path=f)


def test_sc_hours_without_approver_is_ignored(tmp_path):
    from datetime import date
    f = _sc_events(tmp_path, [{"date": date.today().isoformat(),
                               "platform": "soundcloud", "type": "x",
                               "cooldown_hours": 72}])
    assert guards.active_detection_cooldown(platform="sc", path=f) is None


def test_ig_events_still_auto_freeze(tmp_path):
    from datetime import date
    f = _sc_events(tmp_path, [{"date": date.today().isoformat(),
                               "platform": "instagram",
                               "type": "action_block"}])
    assert guards.active_detection_cooldown(platform="ig", path=f) is not None
