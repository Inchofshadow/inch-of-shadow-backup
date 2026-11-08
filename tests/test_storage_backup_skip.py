"""release_manager.storage must skip stats-capture backups that end in .json.

The 2026-07-28 RM homepage showed Farewell 4x and The Deceiver 6x because
releases/ holds backups like the-deceiver-single.bak.20260724_180207_sc_stats.json,
which a bare *.json glob picks up as releases. Same bug hit the release-health
report on 2026-07-15 (see test_release_health_backup_skip.py); storage.py never
got the filter. Backups also made find_release() partial matches ambiguous.
"""
import json

import release_manager.storage as storage


def _write(d, name, slug):
    p = d / name
    p.write_text(json.dumps({"slug": slug, "release_date": "2026-07-10"}))
    return p


def test_list_releases_excludes_backups(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RELEASES_DIR", tmp_path)
    _write(tmp_path, "the-deceiver-single.json", "the-deceiver-single")
    _write(tmp_path, "the-deceiver-single.bak.20260724_180207_sc_stats.json", "bak1")
    _write(tmp_path, "the-deceiver-single.bak.20260726_ig_weekly_stats.json", "bak2")
    _write(tmp_path, "farewell-single.json", "farewell-single")
    _write(tmp_path, "farewell-single.bak.20260719_015152_sc_stats.json", "bak3")
    slugs = [r["slug"] for r in storage.list_releases()]
    assert slugs == ["farewell-single", "the-deceiver-single"]


def test_find_release_partial_not_ambiguous_from_backups(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RELEASES_DIR", tmp_path)
    _write(tmp_path, "the-deceiver-single.json", "the-deceiver-single")
    _write(tmp_path, "the-deceiver-single.bak.20260711_215347_sc_stats.json", "bak1")
    _write(tmp_path, "the-deceiver-single.bak.20260713_ig_weekly_stats.json", "bak2")
    found = storage.find_release("deceiver")
    assert found is not None
    assert found["slug"] == "the-deceiver-single"


def test_iter_release_paths_sorted_and_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RELEASES_DIR", tmp_path)
    b = _write(tmp_path, "b-single.json", "b-single")
    a = _write(tmp_path, "a-single.json", "a-single")
    (tmp_path / "a-single.json.bak.20260711_igstats").write_text("{}")
    assert storage.iter_release_paths() == [a, b]


def test_unsafe_release_slugs_never_leave_releases_dir():
    import pytest
    from release_manager import storage
    for bad in ("../x", "..", "a/b", "/etc/passwd", ".hidden", "", "a\\b", "x/../../y", None):
        with pytest.raises(ValueError):
            storage.release_path(bad)
        assert storage.load_release(bad) is None
        assert storage.release_exists(bad) is False
        assert storage.delete_release(bad) is False
    assert storage.release_path("pinocchio-single").name == "pinocchio-single.json"
    assert storage.release_path("farewell-single.bak.20261106_review").parent == storage.RELEASES_DIR
