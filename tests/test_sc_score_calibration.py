"""Tests for SC session-score calibration (added 2026-08-12).

Three defects made the SC score measure things other than session quality:

1. HARDCODED 24-LIKE TARGET. The rubric wanted 12 PASS A + 12 PASS C maintenance
   likes. But PASS C draws on reciprocators gated by a 30-day cooldown: 33
   reciprocators / 30 days is ~1.1 eligible per day, not 12. Measured
   2026-08-08, actual eligible was 0. So 12 was the real ceiling, which is
   exactly 50% of 24, so every flawless session took an automatic -1 and could
   never score 10.

2. SKIPS NOT CREDITED. When every visible track on a candidate is already liked,
   skipping is correct behaviour (SOP D.4). Those skips counted as zero, so the
   2026-08-06 session turned 12 real actions into "2/24" and a -3 severe
   shortfall, scoring 7. close_loops already credits the equivalent case on IG
   (`ig_unfollow_skip`); SC had no counterpart.

3. EXTERNAL TRUNCATION READ AS FAILURE. Sessions cut short by the operator's
   token budget (2026-08-07: 3 follows) were scored as protocol shortfalls and
   counted toward the two-consecutive-low-scores autonomy pause. A session that
   was interrupted from outside is not a session CC ran badly.

The point is not a higher number. A rubric that punishes impossible targets is
useless as an escalation signal, and can pause autonomy for no real reason.
"""
import scene_intelligence.close_loops as cl


def _tracker(*follows):
    return {"follows": list(follows)}


def _recip(uid, last_engaged, **kw):
    d = {"user_id": uid, "followed_back": True, "last_engaged": last_engaged}
    d.update(kw)
    return d


# --- 1. dynamic PASS C target ------------------------------------------------

def test_pass_c_available_counts_only_reciprocators_past_cooldown():
    t = _tracker(
        _recip("1", "2026-06-01"),           # 72 days, eligible
        _recip("2", "2026-08-01"),           # 11 days, in cooldown
        {"user_id": "3", "followed_back": False, "last_engaged": "2026-06-01"},
    )
    assert cl._sc_pass_c_available(t, "2026-08-12") == 1


def test_pass_c_available_excludes_swept_and_do_not_engage():
    t = _tracker(
        _recip("1", "2026-06-01", no_longer_following=True),
        _recip("2", "2026-06-01", no_longer_engage=True),
        _recip("3", "2026-06-01"),
    )
    assert cl._sc_pass_c_available(t, "2026-08-12") == 1


def test_pass_c_available_treats_never_engaged_as_eligible():
    t = _tracker(_recip("1", None), _recip("2", ""))
    assert cl._sc_pass_c_available(t, "2026-08-12") == 2


def test_like_target_is_pass_a_only_pass_c_is_a_bonus():
    """2026-09-24: the PASS C pool counts accounts outside the like cooldown,
    not accounts with a track to like (9-10 of 10 had none), so adding it to
    the target docked a point from flawless sessions. PASS C likes still count
    toward the day; they are never a debt."""
    t = _tracker(_recip("1", "2026-06-01"), _recip("2", "2026-06-01"))
    assert cl._sc_like_target(t, "2026-08-12") == cl.SC_PASS_A_LIKES


def test_like_target_floors_at_pass_a_when_pool_is_empty():
    """The 2026-08-08 reality: zero reciprocators outside cooldown."""
    t = _tracker(_recip("1", "2026-08-10"))
    assert cl._sc_like_target(t, "2026-08-12") == cl.SC_PASS_A_LIKES


def test_like_target_ignores_a_large_pass_c_pool():
    t = _tracker(*[_recip(str(i), "2026-01-01") for i in range(40)])
    assert cl._sc_like_target(t, "2026-08-12") == cl.SC_PASS_A_LIKES


def test_perfect_session_against_empty_pass_c_pool_scores_10():
    """The core regression: 12 likes + 12 follows was capped at 9."""
    t = _tracker(_recip("1", "2026-08-10"))               # pool empty
    score, ded, imm = cl.score_sc_day(
        {"sc_like": cl.SC_PASS_A_LIKES, "sc_follow": cl.SC_FOLLOW_TARGET},
        "", tracker=t, day="2026-08-12")
    assert score == 10, ded
    assert ded == []


# --- 2. skip crediting -------------------------------------------------------

def test_already_liked_skips_count_toward_the_like_target():
    t = _tracker(_recip("1", "2026-08-10"))
    score, ded, _ = cl.score_sc_day(
        {"sc_like": 2, "sc_like_skip": cl.SC_PASS_A_LIKES - 2,
         "sc_follow": cl.SC_FOLLOW_TARGET}, "",
        tracker=t, day="2026-08-12")
    assert score == 10, ded


def test_skips_alone_do_not_mask_a_real_shortfall():
    t = _tracker(_recip("1", "2026-08-10"))
    score, ded, _ = cl.score_sc_day(
        {"sc_like": 1, "sc_like_skip": 1, "sc_follow": 2}, "",
        tracker=t, day="2026-08-12")
    assert score < 10
    assert any("sc_follow" in d for d in ded)


# --- 3. external truncation --------------------------------------------------

def test_token_truncation_is_not_scored_as_a_protocol_shortfall():
    t = _tracker(_recip("1", "2026-08-10"))
    report = "Session ended early: ran out of tokens mid-run."
    score, ded, imm = cl.score_sc_day(
        {"sc_like": 3, "sc_follow": 3}, report, tracker=t, day="2026-08-12")
    assert not any("shortfall" in d for d in ded), ded
    assert score >= 8
    assert imm is None


def test_truncated_session_still_flags_a_detection_signal():
    """Truncation must not become a way to hide a CAPTCHA."""
    t = _tracker(_recip("1", "2026-08-10"))
    report = "ran out of tokens. Also hit a captcha on follow 4."
    score, ded, imm = cl.score_sc_day(
        {"sc_like": 3, "sc_follow": 3}, report, tracker=t, day="2026-08-12")
    assert imm is not None
    assert any("detection" in d for d in ded)


def test_truncated_session_still_flags_cap_violations():
    t = _tracker(_recip("1", "2026-08-10"))
    report = "session incomplete, token limit reached"
    score, ded, _ = cl.score_sc_day(
        {"sc_like": 3, "sc_follow": 99}, report, tracker=t, day="2026-08-12")
    assert any("cap violation" in d for d in ded)


def test_normal_report_text_is_not_mistaken_for_truncation():
    t = _tracker(_recip("1", "2026-08-10"))
    score, ded, _ = cl.score_sc_day(
        {"sc_like": 3, "sc_follow": 3}, "All passes completed normally.",
        tracker=t, day="2026-08-12")
    assert any("shortfall" in d for d in ded)


# --- backwards compatibility -------------------------------------------------

def test_score_sc_day_still_works_without_tracker():
    """Callers that pass no tracker fall back to the PASS-A-only target."""
    score, ded, _ = cl.score_sc_day(
        {"sc_like": cl.SC_PASS_A_LIKES, "sc_follow": cl.SC_FOLLOW_TARGET}, "")
    assert score == 10, ded
