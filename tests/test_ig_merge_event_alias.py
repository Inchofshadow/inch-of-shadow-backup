"""Tests for the action-key aliasing in _normalize_event.

Cowork has twice renamed the per-event action key in session JSONL files:
"type" (2026-07-01 session) and "event" (2026-07-08 session), both instead of
"action". Each slip crashed event_to_log_entry on ev["action"]. The
normalizer must accept any of the three, then map short action names through
_ACTION_ALIASES ("like" -> "ig_like"), so a format slip never crashes the
merge or silently drops an event.
"""
import scene_intelligence.ig_merge_session_log as m


def test_action_key_passes_through():
    ev = m._normalize_event({"action": "ig_follow", "handle": "x"})
    assert ev["action"] == "ig_follow"


def test_type_key_aliased_to_action():
    # 2026-07-01 session format slip; short name then canonicalized
    ev = m._normalize_event({"type": "like", "handle": "x"})
    assert ev["action"] == "ig_like"


def test_event_key_aliased_to_action():
    # 2026-07-08 session format slip
    ev = m._normalize_event({"event": "follow", "handle": "x"})
    assert ev["action"] == "ig_follow"


def test_action_wins_over_alternates():
    ev = m._normalize_event({"action": "ig_follow", "type": "like"})
    assert ev["action"] == "ig_follow"


def test_no_action_key_at_all_left_untouched():
    # nothing to alias; downstream handles the missing key explicitly
    ev = m._normalize_event({"handle": "x"})
    assert "action" not in ev
