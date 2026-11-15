"""2026-11-14: follow-back check combines recent follower lists (HikerAPI pages repeat)."""
from datetime import date

import scene_intelligence.ig_reciprocity_from_lists as r


def test_union_trusted_when_combined_lists_cover_profile():
    lists = [(date(2026, 11, 12), {"a", "b", "c"}, 4), (date(2026, 11, 10), {"c", "d"}, 4)]
    union, trusted, vdate = r.combined_roster(lists)
    assert union == {"a", "b", "c", "d"} and trusted and vdate == "2026-11-12"


def test_union_not_trusted_when_short():
    lists = [(date(2026, 11, 12), {"a", "b"}, 100)]
    _u, trusted, _v = r.combined_roster(lists)
    assert not trusted


def test_absent_marked_only_when_trusted():
    tr = {"active_follows": [{"username": "x"}, {"username": "a"}]}
    r.apply_roster(tr, {"a"}, False, "2026-11-12")
    assert "followback_verified_at" not in tr["active_follows"][0]
    assert tr["active_follows"][1]["followed_back"] is True


def test_recent_lists_reads_all_formats(tmp_path, monkeypatch):
    import json
    si = tmp_path / "si"; (si / "own_lists").mkdir(parents=True)
    (si / "own_lists" / "own-lists-2026-11-10.json").write_text(json.dumps(
        {"fetched": "2026-11-10T09:00", "profile": {"follower_count": 3}, "followers": [{"username": "A"}]}))
    (si / "own_lists" / "probe-g2-followers-2026-11-12.json").write_text(json.dumps(
        {"fetched": "2026-11-12T01", "profile": {"follower_count": 3}, "followers": ["b", "c"]}))
    (si / "own_lists" / "own-lists-2026-10-01.json").write_text(json.dumps(
        {"fetched": "2026-10-01", "profile": {"follower_count": 3}, "followers": [{"username": "old"}]}))
    monkeypatch.setattr(r, "SI_DIR", si); monkeypatch.setattr(r, "REPO", tmp_path)
    lists = r.recent_lists(date(2026, 11, 14))
    assert [d.isoformat() for d, _n, _r in lists] == ["2026-11-12", "2026-11-10"]
    union, trusted, vdate = r.combined_roster(lists)
    assert union == {"a", "b", "c"} and trusted and vdate == "2026-11-12"
