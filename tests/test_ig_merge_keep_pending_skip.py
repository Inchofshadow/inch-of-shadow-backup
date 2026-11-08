"""Socials 37 (2026-11-08): a reach skip with a keep-pending reason
("button_missing...", the Follow button did not render) must be counted and
leave the queue entry pending. The counter was never initialised, so the
merge raised KeyError on the first such skip."""
import json

import scene_intelligence.ig_merge_session_log as m


def test_button_missing_skip_counts_and_keeps_pending(tmp_path, monkeypatch):
    q = tmp_path / "ig_target_list.json"
    q.write_text(json.dumps({"_meta": {}, "queue": [
        {"username": "someone", "status": "pending"}]}), encoding="utf-8")
    monkeypatch.setattr(m, "QUEUE_FILE", q)
    ev = {"action": "ig_skip", "handle": "someone", "track": "reach",
          "reason": "button_missing_after_reload", "ts": "2026-11-08T15:10:00"}
    counts = m.update_queue_from_events([ev], "2026-11-08", dry_run=True)
    assert counts["queue_skip_render_bug_kept_pending"] == 1
    assert json.loads(q.read_text())["queue"][0]["status"] == "pending"
