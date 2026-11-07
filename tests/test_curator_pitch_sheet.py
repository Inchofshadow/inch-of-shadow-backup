import scene_intelligence.curator_pitch_sheet as ps


def test_rank_orders_fit_then_crosslist_then_saves():
    curators = [
        {"name": "A", "fit": "good", "cross_list_count": 3, "saves": 100},
        {"name": "B", "fit": "top",  "cross_list_count": 1, "saves": 50},
        {"name": "C", "fit": "top",  "cross_list_count": 2, "saves": 10},  # cross-list beats saves
    ]
    ranked = [c["name"] for c in ps.rank(curators)]
    assert ranked == ["C", "B", "A"]   # top before good; within top, higher cross-list first


def test_rank_flags_suspect_high_saves_zero_crosslist():
    curators = [{"name": "Farm", "fit": "top", "cross_list_count": 0, "saves": 20000}]
    out = ps.rank(curators)
    assert out[0]["suspect"] is True


def test_rank_not_suspect_when_crosslisted():
    out = ps.rank([{"name": "Real", "fit": "top", "cross_list_count": 2, "saves": 20000}])
    assert out[0]["suspect"] is False
