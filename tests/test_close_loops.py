"""Loop-closer scoring + escalation rules (built 2026-07-19).

Immediate pause: detection signal, reciprocator churn, cap violation.
Trend pause: two consecutive same-platform scores <= 5.
While paused the tool refuses to act until --resume.
"""
import scene_intelligence.close_loops as cl


def _ev(action, handle="x"):
    return {"action": action, "handle": handle}


# --- IG scoring -------------------------------------------------------------

def _phase_targets():
    """Read the LIVE phase targets so these tests survive a phase change.
    Hardcoding Phase 2 volumes broke them when Amir stepped down to 1b after
    the 2026-08-19 detection warning."""
    import scene_intelligence.ig_engagement_config as cfg
    lim = cfg.PHASE_LIMITS[cfg.CURRENT_PHASE]
    return (lim["follows_per_session"], lim["likes_per_session"],
            lim["unfollows_per_session"])


def test_clean_session_at_target_scores_10():
    # a session delivering exactly the CURRENT phase's targets must score 10
    f, l, u = _phase_targets()
    events = ([_ev("ig_follow")] * f + [_ev("ig_like")] * l
              + [_ev("ig_unfollow")] * u + [_ev("ig_skip")] * 4)
    score, ded, imm = cl.score_ig_session(events, set(), "normal log", 0)
    assert score == 10, ded
    assert imm is None


def test_target_shortfall_deducts(monkeypatch):
    # the real 2026-07-20 session: 6/10, 15/25, 4/8 — must NOT be a 10.
    # Pin the due-supply high so the unfollow target stays the phase ceiling
    # (the scorer is supply-bound since 2026-08-15 and otherwise reads the
    # live tracker, which would make this test nondeterministic).
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    # Pin targets/caps to the Phase 2 values this scenario was recorded under,
    # so the test does not break every time Amir changes phase (it broke on the
    # 2026-08-19 step-down to 1b and again when unfollows went to 0).
    _T = {"ig_follow": 10, "ig_like": 25, "ig_unfollow": 8}
    monkeypatch.setattr(cl, "_ig_targets", lambda: dict(_T))
    monkeypatch.setattr(cl, "ig_caps", lambda: {"ig_follow": 11, "ig_like": 28, "ig_unfollow": 9})
    # NOTE: skips are interleaved, not trailing — a session whose LAST 5+ events
    # are skips is a Class C breaker stop and is exempt from volume scoring
    # (see test_breaker_stop_is_not_scored_as_shortfall).
    events = ([_ev("ig_skip")] * 27 + [_ev("ig_follow")] * 6
              + [_ev("ig_like")] * 15 + [_ev("ig_unfollow")] * 4)
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert score == 7, (score, ded)


def test_unfollow_shortfall_is_supply_bound(monkeypatch):
    # 2026-08-15: only 2 due, both processed -> no unfollow deduction, even
    # though the phase target is 8.
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 0)
    _T = {"ig_follow": 10, "ig_like": 25, "ig_unfollow": 8}
    monkeypatch.setattr(cl, "_ig_targets", lambda: dict(_T))
    monkeypatch.setattr(cl, "ig_caps", lambda: {"ig_follow": 11, "ig_like": 28, "ig_unfollow": 9})
    events = ([_ev("ig_follow")] * 10 + [_ev("ig_like")] * 25
              + [_ev("ig_unfollow")] * 2)
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert not any("ig_unfollow" in d for d in ded), ded
    assert score == 10, (score, ded)


def test_severe_shortfall_deducts_more():
    # under half of target on follows
    got = cl._target_shortfall({"ig_follow": 3}, {"ig_follow": 10})
    assert got and got[0].startswith("-3 severe")


def test_shortfall_ignores_zero_targets():
    # Phase 1 has unfollows_per_session = 0; must not divide by zero or deduct
    assert cl._target_shortfall({"ig_unfollow": 0}, {"ig_unfollow": 0}) == []


def test_sc_shortfall_deducts():
    # Recalibrated 2026-08-12. This used to assert 14 likes / 12 follows == 9,
    # which encoded the old hardcoded 24-like target (12 PASS A + 12 PASS C).
    # The 30-day cooldown made 24 unreachable, so that -1 fired on every
    # complete session. With the target now PASS A + the real PASS C pool,
    # 14 likes is over-delivery and correctly costs nothing; a genuine
    # shortfall still deducts.
    score, ded, _ = cl.score_sc_day(
        {"sc_like": cl.SC_PASS_A_LIKES, "sc_follow": cl.SC_FOLLOW_TARGET}, "")
    assert score == 10, (score, ded)

    score, ded, _ = cl.score_sc_day(
        {"sc_like": 5, "sc_follow": cl.SC_FOLLOW_TARGET}, "")
    assert score == 7, (score, ded)          # likes < 50% of target -> -3
    assert any("sc_like" in d for d in ded)


def test_detection_signal_immediate_pause():
    score, ded, imm = cl.score_ig_session(
        [_ev("ig_like")], set(), "saw a CAPTCHA challenge_required", 0)
    assert imm is not None
    assert score <= 5


def test_reciprocator_churn_immediate_pause():
    events = [_ev("ig_unfollow", "gallows"), _ev("ig_like")]
    score, ded, imm = cl.score_ig_session(events, {"gallows"}, "", 0)
    assert imm is not None and "gallows" in imm


def test_unfollow_aborted_is_not_churn():
    events = [_ev("ig_unfollow_aborted", "gallows"), _ev("ig_like")]
    _, _, imm = cl.score_ig_session(events, {"gallows"}, "", 0)
    assert imm is None


def test_cap_violation_immediate_pause():
    events = [_ev("ig_follow")] * (cl.ig_caps()["ig_follow"] + 1)
    _, ded, imm = cl.score_ig_session(events, set(), "", 0)
    assert imm is not None and "cap violation" in imm


def test_hitting_caps_exactly_is_not_a_violation():
    # caps are read live from the phase config; a full-target session must
    # never be flagged (would have paused autonomy on the first clean
    # Phase 2 session — caught 2026-07-20)
    caps = cl.ig_caps()
    events = [_ev(a) for a, n in caps.items() for _ in range(n)]
    _, ded, imm = cl.score_ig_session(events, set(), "", 0)
    assert imm is None, ded
    assert not any("cap violation" in d for d in ded)


def test_caps_track_the_configured_phase():
    # Caps = phase target + the POSITIVE session jitter the config authorizes
    # (+1 like for the prominent slot). A session executing its own jitter-
    # rolled plan must never count as a cap violation (2026-07-25 false pause).
    import scene_intelligence.ig_engagement_config as cfg
    lim = cfg.PHASE_LIMITS[cfg.CURRENT_PHASE]
    jit = cfg.SESSION_JITTER
    caps = cl.ig_caps()
    assert caps["ig_follow"] == lim["follows_per_session"] + max(0, jit["follows_per_session"][1])
    assert caps["ig_like"] == lim["likes_per_session"] + max(0, jit["likes_per_session"][1]) + 1
    assert caps["ig_unfollow"] == lim["unfollows_per_session"] + max(0, jit["unfollows_per_session"][1])


def test_high_skip_ratio_deducts():
    events = [_ev("ig_skip")] * 8 + [_ev("ig_like")] * 2
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert any("skip ratio" in d for d in ded)


# --- SC scoring -------------------------------------------------------------

def test_sc_clean_day():
    score, ded, imm = cl.score_sc_day(
        {"sc_like": 20, "sc_follow": cl.SC_FOLLOW_TARGET, "sc_repost": 1}, "")
    assert score == 10 and imm is None


def test_sc_cap_violation():
    _, _, imm = cl.score_sc_day({"sc_follow": cl.SC_CAPS["sc_follow"] + 3}, "")
    assert imm is not None


def test_sc_detection_in_report():
    _, _, imm = cl.score_sc_day({"sc_like": 5}, "DataDome slider appeared")
    assert imm is not None


# --- escalation state -------------------------------------------------------

def _fresh_state():
    return {"pauses": {"ig": None, "sc": None},
            "recent": [], "processed": {"ig": [], "sc": []}}


def test_immediate_pause_sets_state():
    s = _fresh_state()
    reason = cl.record_score(s, "ig", "2026-07-20", 3, "detection signal")
    assert reason and (s["pauses"]["ig"] or s["pauses"]["sc"])


def test_trend_pause_two_consecutive_low():
    s = _fresh_state()
    assert cl.record_score(s, "ig", "2026-07-20", 5, None) is None
    reason = cl.record_score(s, "ig", "2026-07-22", 4, None)
    assert reason and (s["pauses"]["ig"] or s["pauses"]["sc"])
    assert "consecutive" in reason


def test_no_trend_pause_when_recovered():
    s = _fresh_state()
    cl.record_score(s, "ig", "2026-07-20", 4, None)
    assert cl.record_score(s, "ig", "2026-07-22", 8, None) is None
    assert not s["pauses"]["ig"] and not s["pauses"]["sc"]


def test_trend_is_per_platform():
    s = _fresh_state()
    cl.record_score(s, "ig", "2026-07-20", 4, None)
    assert cl.record_score(s, "sc", "2026-07-21", 4, None) is None
    assert not s["pauses"]["ig"] and not s["pauses"]["sc"]


def test_score_six_does_not_trend_pause():
    s = _fresh_state()
    cl.record_score(s, "ig", "2026-07-20", 6, None)
    assert cl.record_score(s, "ig", "2026-07-22", 6, None) is None
    assert not s["pauses"]["ig"] and not s["pauses"]["sc"]


def test_breaker_stop_is_not_scored_as_shortfall(monkeypatch):
    """2026-08-17: session stopped correctly on 5 trailing skips (Class C) and
    was scored 1/10 with -3/-3/-3 volume shortfalls, arming a false trend pause.
    Obeying the breaker is protocol compliance, not under-delivery."""
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    monkeypatch.setattr(cl, "_ig_targets", lambda: {"ig_follow": 12, "ig_like": 6, "ig_unfollow": 8})  # live follows paused 2026-09-26
    events = ([_ev("ig_follow")] * 4 + [_ev("ig_like")] * 7
              + [_ev("ig_skip")] * 5)          # trailing 5 skips = breaker stop
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert score == 10, (score, ded)
    assert not any("shortfall" in d for d in ded), ded
    assert any("breaker" in d for d in ded), ded


def test_shortfall_still_scored_when_skips_are_not_trailing(monkeypatch):
    """Guard against the exemption being too broad: skips in the MIDDLE of a
    session are ordinary noise, not a breaker stop."""
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    events = ([_ev("ig_skip")] * 5 + [_ev("ig_follow")] * 4
              + [_ev("ig_like")] * 7)          # session continued after the skips
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert any("shortfall" in d for d in ded), ded
    assert score < 10, (score, ded)


def test_safety_halt_is_not_scored_as_shortfall(monkeypatch):
    """T-006 (2026-08-31): the 08-28 session halted DELIBERATELY on a P0
    safety finding and was scored 1/10 on volume shortfalls; 08-26 (Chrome
    renderer death) same class. A session_halt event with reason
    safety|infrastructure exempts volume targets, like a breaker stop."""
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    events = ([_ev("ig_follow")] * 1 + [_ev("ig_like")] * 4
              + [{"action": "session_halt",
                  "reason": "safety: unfollow lane on unmeasured data"}])
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert score == 10, (score, ded)
    assert not any("shortfall" in d for d in ded), ded
    assert any("protocol-compliant" in d for d in ded), ded


def test_infrastructure_halt_exempt_but_detection_still_scores(monkeypatch):
    """A halt can never mask a CAPTCHA: detection deductions still apply."""
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    events = [{"action": "session_halt", "reason": "infrastructure: renderer died"}]
    score, ded, _ = cl.score_ig_session(
        events, set(), "One DataDome CAPTCHA appeared mid-session", 0)
    assert any("detection" in d for d in ded), ded
    assert score <= 5, (score, ded)


def test_halt_with_other_reason_still_scores_volume(monkeypatch):
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: 99)
    events = [{"action": "session_halt", "reason": "felt like stopping"}]
    score, ded, _ = cl.score_ig_session(events, set(), "", 0)
    assert any("shortfall" in d for d in ded), ded


def test_targets_capped_at_plan_file_volumes(monkeypatch, tmp_path):
    """2026-09-07: a session that delivers everything the plan offered must
    not lose points for the config ceiling it was never given supply for."""
    import json
    monkeypatch.setattr(cl, "SI_DIR", tmp_path)
    monkeypatch.setattr(cl, "_ig_targets", lambda: {"ig_follow": 12, "ig_like": 6, "ig_unfollow": 8})
    monkeypatch.setattr(cl, "_overdue_unfollows_remaining", lambda: None)
    (tmp_path / "session_plan_2026-09-07.json").write_text(json.dumps({
        "reach_follows": [{"handle": f"r{i}"} for i in range(7)],
        "scene_likes": [{"handle": f"s{i}"} for i in range(4)],
        "prominent_likes": [{"handle": "p1"}],
        "unfollows": [],
    }))
    events = ([{"ts": "2026-09-07T19:04:00+02:00", "action": "ig_follow", "handle": f"r{i}"} for i in range(7)]
              + [{"ts": "2026-09-07T19:05:00+02:00", "action": "ig_like", "handle": f"s{i}"} for i in range(5)])
    score, deductions, immediate = cl.score_ig_session(events, set(), "", 0)
    assert score == 10, deductions
