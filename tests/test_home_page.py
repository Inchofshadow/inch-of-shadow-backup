

def test_home_shows_tickets_by_area_label_never_the_stored_id():
    """Amir's rule: tickets are shown as '<emoji> <Area> <number>', never as R-02 / G-14."""
    from release_manager.views.release import _home_tickets
    out = _home_tickets()
    rows = [t for g in out["areas"] for t in g["tickets"]] + out["decisions"]
    assert rows, "expected at least one ticket on the live board"
    for t in rows:
        if t.get("area") and t.get("area_no") not in ("", None):
            assert t["shown"] != t["id"] and str(t["area_no"]) in t["shown"], t["id"]
