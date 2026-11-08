from scene_intelligence import contact_index as ci


def test_ig_handle_normalises():
    assert ci.ig_handle("@Foo.Bar") == "foo.bar"
    assert ci.ig_handle("https://www.instagram.com/dark_disco/?hl=en") == "dark_disco"
    assert ci.ig_handle("instagram.com/x_y/") == "x_y"
    assert ci.ig_handle("facebook.com/foo") == ""
    assert ci.ig_handle(None) == ""


def test_sc_slug():
    assert ci.sc_slug("https://soundcloud.com/mmdiscos?utm_medium=api") == "mmdiscos"
    assert ci.sc_slug("https://example.com/mmdiscos") == ""


def test_name_keys_drop_parenthetical():
    assert ci.name_keys("Iptamenos Discos (Local Suicide)") == ["iptamenosdiscoslocalsuicide", "iptamenosdiscos"]
    assert ci.name_keys("") == []


def _build(si=(), booking=(), outreach=(), igt=None, sct=None, fol=(), fwg=()):
    return ci.build(list(si), list(booking), list(outreach), igt or {}, sct or {}, set(fol), set(fwg))


def test_join_by_handle_then_name_and_new_rows():
    si = [{"name": "Iptamenos Discos", "ig": "iptamenosdiscos", "sc": "", "category": "label", "city": "Athens", "score": "4"}]
    booking = [{"name": "Renate", "ig": "renate.berlin", "sc": "", "type": "venue", "city": "Berlin", "status": "", "in_si_flag": False}]
    outreach = [
        {"name": "Iptamenos Discos (Local Suicide)", "ig": "iptamenosdiscos", "sc": "", "batch": "batch-2", "status": "proposed", "channel": "instagram"},
        {"name": "Renate", "ig": "", "sc": "", "batch": "batch-1", "status": "drafted", "channel": "email"},
    ]
    rows = _build(si, booking, outreach, fol={"iptamenosdiscos"}, fwg={"renate.berlin"})
    assert len(rows) == 2
    ipt = next(r for r in rows if r["ig"] == "iptamenosdiscos")
    assert ipt["in"] == ["si", "outreach"] and ipt["follows_amir"] and ipt["outreach"][0]["status"] == "proposed"
    ren = next(r for r in rows if r["name"] == "Renate")
    assert ren["in"] == ["booking", "outreach"] and ren["amir_follows"]
    s = ci.summary(rows)
    assert s["booking_not_in_si"] == 1 and s["outreach_not_in_si"] == 1 and s["warm_outreach"] == 2


def test_si_duplicates_are_counted_not_merged_away():
    si = [{"name": "Local Suicide", "ig": "localsuicide", "sc": "", "category": "dj", "city": "", "score": ""},
          {"name": "Local Suicide", "ig": "", "sc": "", "category": "dj", "city": "", "score": ""}]
    rows = _build(si)
    assert len(rows) == 1 and rows[0]["si_duplicates"] == 2 and len(rows[0]["si"]) == 2


def test_tracker_states():
    igt = ci.ig_tracker_map({"active_follows": [{"username": "a", "followed_back": True}, {"username": "b"}],
                             "unfollowed_history": [{"username": "c"}]})
    assert igt == {"a": "followed_back", "b": "active", "c": "unfollowed"}
    sct = ci.sc_tracker_map({"follows": [{"url": "https://soundcloud.com/x?u=1", "no_longer_following": True},
                                         {"url": "https://soundcloud.com/y", "followed_back": True}]})
    assert sct == {"x": "unfollowed", "y": "followed_back"}


def test_main_writes_only_the_index(tmp_path, monkeypatch):
    for name in ("SI", "BOOKING", "OUTREACH", "IG_TRACKER", "SC_TRACKER"):
        monkeypatch.setattr(ci, name, tmp_path / f"missing_{name}.json")
    monkeypatch.setattr(ci, "OWN_LISTS_GLOBS", [str(tmp_path / "none-*.json")])
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    monkeypatch.setattr(ci, "OUT", tmp_path / "contact_index.json")
    monkeypatch.setattr("sys.argv", ["contact_index.py"])
    assert ci.main() == 0
    assert [p.name for p in tmp_path.iterdir()] == ["contact_index.json"]


def test_newest_own_lists_reads_both_folders_by_name_date(tmp_path):
    a = tmp_path / "a"; b = tmp_path / "b"; a.mkdir(); b.mkdir()
    (b / "dj07-own-lists-2026-11-03.json").write_text("{}")
    (a / "own-lists-2026-11-10.json").write_text("{}")
    got = ci.newest_own_lists([str(a / "own-lists-*.json"), str(b / "dj07-own-lists-*.json")])
    assert got.endswith("own-lists-2026-11-10.json")
    assert ci.newest_own_lists([str(tmp_path / "none-*.json")]) is None
