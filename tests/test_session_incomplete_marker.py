"""Structured incomplete-session marker (added 2026-08-28).

close_loops exempts externally-truncated sessions from volume penalties, but the
detection matched free prose ("ended early", "ran out of tokens", ...). On its
first real test it FAILED: the 2026-08-28 report said "STOPPED EARLY at 5/12"
and "Stopped deliberately", neither of which is in the marker list, so a session
blocked by a browser fault scored 4/10 and counted toward the two-consecutive-
low-scores autonomy pause. That is the exact outcome the exemption exists to
prevent.

Fix: a STRUCTURED marker the report writer emits deliberately —
`SESSION_INCOMPLETE: <reason>` — plus a broadened prose fallback. Detection and
cap violations still apply during truncation, so this can never hide a CAPTCHA.
"""
import scene_intelligence.close_loops as cl


def test_structured_marker_is_detected():
    assert cl.scan_for_truncation("SESSION_INCOMPLETE: clicks stopped reaching SoundCloud")


def test_structured_marker_is_case_insensitive():
    assert cl.scan_for_truncation("session_incomplete: browser fault")


def test_the_actual_20260828_phrasing_now_matches():
    """The regression: this report scored 4/10 because nothing matched."""
    for phrasing in [
        "**Status: STOPPED EARLY at 5/12 follows.**",
        "Stopped deliberately, not crashed.",
        "Session was blocked partway through.",
        "Could not complete the session.",
        "Session halted after 5 follows.",
    ]:
        assert cl.scan_for_truncation(phrasing), phrasing


def test_existing_prose_markers_still_work():
    for phrasing in ["ran out of tokens", "token limit reached",
                     "session incomplete", "ended early", "was interrupted"]:
        assert cl.scan_for_truncation(phrasing), phrasing


def test_normal_complete_report_is_not_truncation():
    for phrasing in [
        "Status: COMPLETE. All passes run, all actions logged.",
        "All 12 follows completed. No anomalies.",
        "PASS C skipped: 0 eligible, which is correct.",
    ]:
        assert not cl.scan_for_truncation(phrasing), phrasing


def test_empty_text_is_safe():
    assert not cl.scan_for_truncation("")
    assert not cl.scan_for_truncation(None)


def test_incomplete_session_is_exempt_from_volume_penalty():
    tracker = {"follows": []}
    counts = {"sc_like": 6, "sc_follow": 5}
    report = "SESSION_INCOMPLETE: clicks stopped reaching SoundCloud after 11 actions."
    score, ded, imm = cl.score_sc_day(counts, report, tracker=tracker, day="2026-08-28")
    assert not any("shortfall" in d for d in ded), ded
    assert score == 10, ded
    assert imm is None


def test_incomplete_session_still_flags_a_real_captcha():
    tracker = {"follows": []}
    report = "SESSION_INCOMPLETE: stopped. A captcha appeared on follow 6."
    score, ded, imm = cl.score_sc_day({"sc_like": 6, "sc_follow": 5}, report,
                                      tracker=tracker, day="2026-08-28")
    assert imm is not None
    assert any("detection" in d for d in ded)


def test_incomplete_session_still_flags_cap_violations():
    tracker = {"follows": []}
    report = "SESSION_INCOMPLETE: stopped early."
    score, ded, _ = cl.score_sc_day({"sc_follow": 99}, report,
                                    tracker=tracker, day="2026-08-28")
    assert any("cap violation" in d for d in ded)
