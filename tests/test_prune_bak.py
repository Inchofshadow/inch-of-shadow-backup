"""tools/prune_bak.py: only the SC weekly-health backups are pruned (gate review 2026-11-08)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import prune_bak  # noqa: E402


def _old(path, days, now):
    path.write_text("x")
    os.utime(path, (now - days * 86400, now - days * 86400))


def test_only_old_sc_tracker_backups_are_candidates(tmp_path):
    now = 2_000_000_000
    _old(tmp_path / "sc_follow_tracker.bak.20261001_120000_health.json", 30, now)
    _old(tmp_path / "sc_follow_tracker.bak.20261105_120000_health.json", 3, now)
    _old(tmp_path / "ig_follow_tracker.json.bak.20261104_pre_provider_recip", 30, now)
    _old(tmp_path / "engagement_log.json.bak.20260901", 60, now)
    names = [p.name for p, _, _ in prune_bak.candidates(now=now, folder=tmp_path)]
    assert names == ["sc_follow_tracker.bak.20261001_120000_health.json"]
