

def test_bios_latest_release_is_the_newest_one_actually_out():
    from release_manager.views.words import latest_out_release
    rels = [
        {"slug": "farewell", "release_date": "2026-05-15", "distribution": {"status": "approved"}},
        {"slug": "deceiver", "release_date": "2026-07-10", "distribution": {"status": "approved"}},
        {"slug": "pinocchio", "release_date": "2026-11-06", "distribution": {"status": "draft"}},
        {"slug": "future", "release_date": "2027-01-01", "distribution": {"status": "approved"}},
    ]
    assert latest_out_release(rels, today="2026-11-08")["slug"] == "deceiver"
    assert latest_out_release([], today="2026-11-08") is None
