

def test_home_shows_tickets_by_area_label_never_the_stored_id():
    """Amir's rule: tickets are shown as '<emoji> <Area> <number>', never as R-02 / G-14."""
    from release_manager.views.release import _home_tickets
    out = _home_tickets()
    rows = [t for g in out["areas"] for t in g["tickets"]] + out["decisions"]
    assert rows, "expected at least one ticket on the live board"
    for t in rows:
        if t.get("area") and t.get("area_no") not in ("", None):
            assert t["shown"] != t["id"] and str(t["area_no"]) in t["shown"], t["id"]


def test_who_filter_shows_the_area_rule_names():
    from release_manager.core import who_filter
    assert who_filter("amir") == "\U0001F64B Amir"
    assert who_filter("claude") == "\U0001F383 Claude"
    assert who_filter("auto") == "\U0001F916 auto"
    assert who_filter("") == ""
    assert who_filter("someone") == "someone"


def test_home_rows_wrap_and_never_show_the_raw_who(monkeypatch):
    """RM 2.0 check 2026-11-08: the next step ran off the page in a no-wrap monospace span and the
    who column read 'amir'. Rows are now .home-row with the next step below the title."""
    import release_manager.views.release as rel
    fake = {"areas": [{"label": "\U0001F3B5 Release", "tickets": [
                {"id": "R-02", "shown": "\U0001F3B5 Release 2", "title": "Cover final", "who": "amir",
                 "next_step": "Amir picks effects on the wall; then type + 4000 px export."}]}],
            "next": 0, "cp_open": 0, "decisions": [], "tickets_error": None, "cp_error": None}
    monkeypatch.setattr(rel, "_home_tickets", lambda: fake)
    from release_manager.webapp import app
    html = app.test_client().get("/").get_data(as_text=True)
    now = html.split('id="home-now"', 1)[1].split("</section>", 1)[0]
    assert 'class="home-row' in now and "ap-task-due" not in now
    assert "\U0001F64B Amir" in now and ">amir<" not in now
    assert "Amir picks effects on the wall" in now


def test_every_page_has_the_phone_menu_button():
    """RM check 2026-11-08: under 768 px the sidebar is hidden above the page and nothing opened it."""
    from release_manager.webapp import app
    html = app.test_client().get("/").get_data(as_text=True)
    assert 'id="nav-menu-btn"' in html and 'aria-controls="sidebar"' in html
    assert "classList.toggle('mobile-open')" in html
    css = (app.static_folder + "/style.css")
    text = open(css, encoding="utf-8").read()
    assert ".sidebar.mobile-open" in text and ".nav-menu-btn" in text


def test_home_is_in_the_rooms_look():
    """Amir's pick 2026-11-08: look 3 (rooms) in look 1's colours: each now-area is a room, the
    verdict is a pill, colours come from the --ledger tokens on :root."""
    from release_manager.views.release import _home_tickets
    from release_manager.webapp import app
    html = app.test_client().get("/").get_data(as_text=True)
    now = html.split('id="home-now"', 1)[1].split("</section>", 1)[0]
    assert now.count('class="home-room home-room-') == len(_home_tickets()["areas"])
    assert 'class="home-pill' in html
    css = open(app.static_folder + "/style.css", encoding="utf-8").read()
    root = css.split(":root {", 1)[1].split("}", 1)[0]
    for token in ("--ledger-ground", "--ledger-room", "--ledger-line", "--ledger-ink", "--ledger-dim", "--ledger-amir"):
        assert token in root, token


def test_home_rooms_wear_their_area_mood_on_a_warm_black_room():
    """Amir 2026-11-08: option C (each area in its own mood colour), backgrounds changed to look 1's warm black."""
    from release_manager.views.release import _home_tickets
    from release_manager.webapp import app
    html = app.test_client().get("/").get_data(as_text=True)
    for a in _home_tickets()["areas"]:
        key = a["label"].split()[-1].lower()
        assert 'class="home-room home-room-%s"' % key in html, key
    css = open(app.static_folder + "/style.css", encoding="utf-8").read()
    root = css.split(":root {", 1)[1].split("}", 1)[0]
    for area in ("release", "socials", "booking", "income", "studio", "system"):
        assert "--mood-%s:" % area in root and ".home-room-%s" % area in css, area
    room = css.split("\n.home-room { ", 1)[1].split("}", 1)[0]
    assert "background: var(--ledger-room)" in room      # never a tinted background


def test_home_rooms_are_an_aligned_equal_height_grid():
    """Amir 2026-11-09: all room cards line up and share one height (grid rows of 1fr, not CSS columns)."""
    from release_manager.webapp import app
    css = open(app.static_folder + "/style.css", encoding="utf-8").read()
    rooms = css.split("\n.home-rooms {", 1)[1].split("}", 1)[0]
    assert "display: grid" in rooms and "grid-auto-rows: 1fr" in rooms and "columns:" not in rooms.replace("grid-template-columns", "")


def test_home_puts_system_first():
    """Amir 2026-11-09: 'system should be top'."""
    import json
    from release_manager.views import release as rel
    data = {"areas": {"Release": "R", "Socials": "S", "System": "Y"},
            "tickets": [{"id": "a", "area": "Release", "bucket": "now", "status": "approved"},
                        {"id": "b", "area": "System", "bucket": "now", "status": "approved"}]}
    class F:
        def read_text(self, encoding=None):
            return json.dumps(data)
    import release_manager.views.work as work
    orig = work.TICKETS_FILE
    work.TICKETS_FILE = F()
    try:
        out = rel._home_tickets()
    finally:
        work.TICKETS_FILE = orig
    assert [a["label"] for a in out["areas"]] == ["Y", "R"]


def test_sidebar_toggle_on_every_page():
    """System 99 (Amir 2026-11-11: "an option close and open the side bar"): a real button on every
    base page, the choice remembered per browser behind try/catch, phones keep the Menu button."""
    from release_manager.webapp import app
    c = app.test_client()
    for url in ("/", "/stats", "/tickets"):
        html = c.get(url).get_data(as_text=True)
        assert '<button type="button" class="sidebar-toggle" id="sidebar-toggle"' in html, url
        assert 'aria-controls="sidebar"' in html and 'aria-expanded="true"' in html
        assert 'id="nav-menu-btn"' in html                                   # the phone Menu stays
        head = html.split("</head>", 1)[0]
        assert "localStorage.getItem('rm-sidebar')" in head and "try {" in head   # set before first paint
    assert "localStorage.setItem('rm-sidebar'" in html and "catch (e)" in html
    css = open(app.static_folder + "/style.css", encoding="utf-8").read()
    block = css.split("System 99", 1)[1].split("The phone menu button", 1)[0]
    assert "html.sb-closed .sidebar { transform: translateX(-100%); visibility: hidden; }" in block
    assert "html.sb-closed .main-content { margin-left: 0;" in block
    assert "@media (max-width: 768px) { .sidebar-toggle { display: none; } }" in block
    assert block.index("@media (min-width: 769px)") < block.index("html.sb-closed .sidebar {")   # phones untouched
    import os
    lay = open(os.path.join(app.root_path, app.template_folder, "playground_layout.html"), encoding="utf-8").read()
    assert "100vw - var(--sidebar-w, 280px)" in lay                      # the Layout stage grows when closed
