"""Shared JSON state I/O (audit P2-10): atomic writes, loud corrupt failures.

A state file that exists but cannot be parsed must be a hard stop, never an
empty default — the old fallbacks let a corrupt tracker load as empty state
and the next save clobbered the recoverable file.
"""
import json

import pytest

from scene_intelligence.json_io import (
    EXIT_CORRUPT, atomic_write_json, load_json_checked,
)


def test_missing_file_returns_default(tmp_path):
    assert load_json_checked(tmp_path / "gone.json", {"a": 1}) == {"a": 1}


def test_valid_file_loads(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text(json.dumps({"follows": [1, 2]}))
    assert load_json_checked(p, {}) == {"follows": [1, 2]}


def test_corrupt_existing_file_is_hard_stop(tmp_path):
    p = tmp_path / "tracker.json"
    p.write_text("{truncated")
    with pytest.raises(SystemExit) as exc:
        load_json_checked(p, {}, what="follow tracker")
    assert exc.value.code == EXIT_CORRUPT


def test_atomic_write_roundtrip(tmp_path):
    p = tmp_path / "out.json"
    atomic_write_json(p, {"x": "ü"})
    assert json.loads(p.read_text(encoding="utf-8")) == {"x": "ü"}
    # no temp file left behind
    assert list(tmp_path.iterdir()) == [p]


def test_atomic_write_failure_preserves_original(tmp_path):
    p = tmp_path / "out.json"
    p.write_text(json.dumps({"keep": True}))
    with pytest.raises(TypeError):
        atomic_write_json(p, {"bad": object()})  # not JSON-serializable
    # original untouched, temp cleaned up
    assert json.loads(p.read_text()) == {"keep": True}
    assert list(tmp_path.iterdir()) == [p]


def test_sc_tracker_load_dies_on_corrupt(monkeypatch, tmp_path):
    import scene_intelligence.sc_engagement as sc
    bad = tmp_path / "sc_follow_tracker.json"
    bad.write_text("{nope")
    monkeypatch.setattr(sc, "FOLLOW_TRACKER", bad)
    with pytest.raises(SystemExit):
        sc.load_follow_tracker()


def test_ig_load_json_dies_on_corrupt(tmp_path):
    import scene_intelligence.ig_engagement as ig
    bad = tmp_path / "state.json"
    bad.write_text("{nope")
    with pytest.raises(SystemExit):
        ig._load_json(bad, {})
    # missing file still returns default (first-run bootstrap)
    assert ig._load_json(tmp_path / "gone.json", {"d": 1}) == {"d": 1}
