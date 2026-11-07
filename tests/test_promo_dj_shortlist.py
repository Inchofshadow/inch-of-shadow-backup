import scene_intelligence.promo_dj_shortlist as ps


def test_genre_match_same_scene_true():
    # EBM/acid release vs an electro DJ - adjacent in the dark-electronic family
    assert ps.genre_match("EBM / Acid", "Electro") is True
    assert ps.genre_match("Dark Disco", "Techno") is True


def test_genre_match_out_of_scene_false():
    assert ps.genre_match("EBM / Acid", "Pop") is False
    assert ps.genre_match("EBM / Acid", "") is False
    assert ps.genre_match("", "Electro") is False


def _dj(name, genre="Electro", followers=500, score=5, category="dj"):
    return {"name": name, "genre_main": genre, "soundcloud_followers": followers,
            "relevance_score": score, "category": category}


def test_shortlist_filters_and_sorts():
    djs = [
        _dj("InPool", score=9),                       # excluded: already in pool
        _dj("LowReach", followers=50),                # excluded: below min_sc_followers
        _dj("OffGenre", genre="Pop"),                 # excluded: out of scene
        _dj("NotADj", category="label"),              # excluded: not a dj
        _dj("Good1", followers=800, score=7),
        _dj("Good2", followers=300, score=9),
    ]
    out = ps.shortlist(djs, existing_names=["inpool"], release_genre="EBM / Acid",
                       min_sc_followers=200)
    names = [c["name"] for c in out]
    assert names == ["Good2", "Good1"]               # sorted by score desc


def test_shortlist_handles_string_numbers():
    djs = [{"name": "StrNums", "genre_main": "Techno",
            "soundcloud_followers": "640", "relevance_score": "8", "category": "dj"}]
    out = ps.shortlist(djs, existing_names=[], release_genre="Techno", min_sc_followers=200)
    assert [c["name"] for c in out] == ["StrNums"]
