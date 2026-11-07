"""iter_release_paths must skip stats-capture backups that end in .json.

The 2026-07-15 release-health report listed Farewell twice and The Deceiver
three times because releases/ holds backups like
the-deceiver-single.bak.20260711_215347_sc_stats.json, which a bare *.json
glob picks up as releases.
"""
from scene_intelligence.release_weekly_health import iter_release_paths


def _touch(d, name):
    p = d / name
    p.write_text("{}")
    return p


def test_backups_excluded(tmp_path):
    real = _touch(tmp_path, "the-deceiver-single.json")
    _touch(tmp_path, "the-deceiver-single.bak.20260711_215347_sc_stats.json")
    _touch(tmp_path, "the-deceiver-single.bak.20260713_ig_weekly_stats.json")
    _touch(tmp_path, "farewell-single.bak.20260719_015152_sc_stats.json")
    assert iter_release_paths(tmp_path) == [real]


def test_json_bak_suffix_never_globbed(tmp_path):
    # these don't end in .json, but guard the pattern anyway
    real = _touch(tmp_path, "farewell-single.json")
    (tmp_path / "farewell-single.json.bak.20260711_igstats").write_text("{}")
    assert iter_release_paths(tmp_path) == [real]


def test_sorted_and_complete(tmp_path):
    b = _touch(tmp_path, "b-single.json")
    a = _touch(tmp_path, "a-single.json")
    assert iter_release_paths(tmp_path) == [a, b]
