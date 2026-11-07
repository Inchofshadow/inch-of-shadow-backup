"""Detection scanning must not fire on NEGATED mentions (added 2026-08-12).

scan_for_detection did a naive substring match for "captcha", "datadome" etc.
Session reports routinely state the ABSENCE of trouble, so a clean session was
penalised for saying so:

    2026-07-23 report: "## No CAPTCHAs, no DataDome challenges today."
      -> -5 detection signal + IMMEDIATE autonomy pause. Session was clean.
    2026-08-06 report: "None. No CAPTCHA, no 403, no unexpected popups."
      -> same false positive.

CC itself flagged this on 2026-07-23 ("This appears to be from the July 21
session logs, NOT from today... close_loops.py may be reading stale session
events") and it was never acted on. Real incidents must still fire: the
2026-07-24 report ("One DataDome CAPTCHA appeared mid-session") was a genuine
detection and has to keep scoring -5.
"""
import scene_intelligence.close_loops as cl


# --- negated mentions must NOT fire -----------------------------------------

def test_no_captchas_line_does_not_fire():
    assert cl.scan_for_detection("## No CAPTCHAs, no DataDome challenges today.") == []


def test_none_prefix_does_not_fire():
    assert cl.scan_for_detection("- None. No CAPTCHA, no 403, no unexpected popups.") == []


def test_various_negation_phrasings_do_not_fire():
    for line in [
        "No CAPTCHAs, no throttle errors, no login prompts. Session clean throughout.",
        "Zero DataDome challenges.",
        "There was no rate limit today.",
        "Completed without a captcha.",
        "Never hit a captcha during the run.",
        "No 429 responses.",
    ]:
        assert cl.scan_for_detection(line) == [], line


# --- genuine detections must STILL fire -------------------------------------

def test_real_captcha_still_fires():
    txt = ("All three passes completed. One DataDome CAPTCHA appeared mid-session "
           "(during A11 like attempt); Amir solved it manually.")
    hits = cl.scan_for_detection(txt)
    assert "captcha" in hits and "datadome" in hits


def test_real_403_rate_limit_still_fires():
    assert "rate limit" in cl.scan_for_detection(
        "Follow #6 returned HTTP 403, looks like a rate limit.")


def test_mixed_report_fires_only_on_the_real_sentence():
    txt = ("No CAPTCHAs during PASS A. "
           "However a captcha appeared on follow 4 and we stopped.")
    assert "captcha" in cl.scan_for_detection(txt)


def test_negation_does_not_leak_across_sentences():
    """A negation in one sentence must not suppress a later real hit."""
    txt = "No issues in PASS A. DataDome challenge fired in PASS B."
    assert "datadome" in cl.scan_for_detection(txt)


def test_negation_does_not_leak_across_lines():
    txt = "No CAPTCHAs today.\nCAPTCHA appeared at 11:42 on the follow click."
    assert "captcha" in cl.scan_for_detection(txt)


# --- regression: the two real reports ---------------------------------------

def test_20260723_clean_report_scores_clean():
    """Was: 2/10 and an autonomy pause, on a session with zero challenges."""
    txt = "## No CAPTCHAs, no DataDome challenges today."
    score, ded, imm = cl.score_sc_day(
        {"sc_like": cl.SC_PASS_A_LIKES, "sc_follow": cl.SC_FOLLOW_TARGET}, txt)
    assert imm is None, ded
    assert score == 10, ded


def test_20260724_real_incident_still_pauses():
    txt = "One DataDome CAPTCHA appeared mid-session during the A11 like attempt."
    score, ded, imm = cl.score_sc_day(
        {"sc_like": cl.SC_PASS_A_LIKES, "sc_follow": cl.SC_FOLLOW_TARGET}, txt)
    assert imm is not None
    assert score <= 5


def test_empty_and_none_text_are_safe():
    assert cl.scan_for_detection("") == []
    assert cl.scan_for_detection(None) == []


def test_bare_number_needs_http_context():
    """2026-09-07: follower count 429 in an unfollow table paused autonomy."""
    table = "| 2 | Laura Aha | 429 | 2026-07-16 | 9852671 |"
    assert cl.scan_for_detection(table) == []
    assert "429" in cl.scan_for_detection("the follow call returned HTTP 429 with Retry-After")
    assert "429" in cl.scan_for_detection("got a 429 on follow 6")
    assert cl.scan_for_detection("account id 14290 in the queue") == []
