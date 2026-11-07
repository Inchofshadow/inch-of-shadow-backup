"""Guard against ACTION-STRING DRIFT — the bug class that hid for months.

2026-08-17: the skip-cooldown matched `action == "skipped"` while the engine had
been writing `"ig_skip"` since May. No error, no warning — the comparison was
simply always False, so the cooldown never fired and dead accounts were served
every session for six sessions straight.

That failure is invisible to normal tests because synthetic fixtures use
whatever string the test author picked. The only way to catch it is to check the
code's expectations against the REAL log vocabulary.

This test asserts every action value the engine matches on actually occurs in
the live engagement log. If someone renames an action (or a matcher goes stale),
this fails loudly instead of silently disabling a safety rule.
"""
import json
from pathlib import Path

import pytest

import scene_intelligence.ig_engagement as eng

LOG = Path(__file__).parent.parent / "scene_intelligence" / "engagement_log.json"


def _live_actions() -> set[str]:
    if not LOG.exists():
        pytest.skip("no live engagement log available")
    data = json.loads(LOG.read_text(encoding="utf-8")).get("log", {})
    return {
        e.get("action")
        for entries in data.values()
        for e in entries
        if isinstance(e, dict) and e.get("action")
    }


def test_skip_actions_exist_in_the_live_log():
    """At least one value in IG_SKIP_ACTIONS must really be written.

    If this fails, the skip-cooldown is dead code again.
    """
    live = _live_actions()
    matched = eng.IG_SKIP_ACTIONS & live
    assert matched, (
        "IG_SKIP_ACTIONS matches NOTHING in the live log — the skip-cooldown "
        f"is disabled. Expected any of {sorted(eng.IG_SKIP_ACTIONS)}, "
        f"log contains {sorted(live)}"
    )


def test_the_dominant_skip_action_is_covered():
    """The most common skip-ish action in the log must be in the matcher.

    Catches the exact 2026-08-17 shape: matcher covers a rare legacy value
    ("skipped", 40 entries) while missing the dominant one ("ig_skip", 743).
    """
    if not LOG.exists():
        pytest.skip("no live engagement log available")
    data = json.loads(LOG.read_text(encoding="utf-8")).get("log", {})
    counts: dict[str, int] = {}
    for entries in data.values():
        for e in entries:
            if not isinstance(e, dict):
                continue
            a = e.get("action") or ""
            if "skip" in a:
                counts[a] = counts.get(a, 0) + 1
    if not counts:
        pytest.skip("no skip events logged yet")
    dominant = max(counts, key=counts.get)
    assert dominant in eng.IG_SKIP_ACTIONS, (
        f"'{dominant}' is the most-written skip action ({counts[dominant]} entries) "
        f"but is NOT in IG_SKIP_ACTIONS {sorted(eng.IG_SKIP_ACTIONS)}"
    )


def test_core_engagement_actions_are_not_classed_as_skips():
    """Real engagement must never be treated as a skip."""
    for a in ("ig_like", "ig_follow", "ig_unfollow"):
        assert a not in eng.IG_SKIP_ACTIONS
