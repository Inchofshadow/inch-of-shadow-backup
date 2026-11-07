"""Shadow Archive (Machine-18): the index validates, the filters and the markdown renderer
behave, paths never leave the archive folder, and the pages answer."""
from pathlib import Path

import pytest

from release_manager import archive

ROOT = Path(__file__).resolve().parent.parent


def _data():
    return {
        "allowed": {"kind": ["reel", "creator"], "topics": ["type", "hooks"], "lane": ["songs", "electronic", "both"],
                    "weight": ["test", "mentor"], "read_level": ["read"]},
        "references": [
            {"id": "R-001", "title": "A reel", "source": "@a", "kind": "reel", "topics": ["type"], "lane": "both",
             "weight": "test", "amir_reason": "test", "added": "2026-10-01", "read_level": "read", "notes": "refs/R-001.md",
             "releases": [], "summary": "fonts on covers"},
            {"id": "R-002", "title": "A mentor", "source": "@b", "kind": "creator", "topics": ["hooks", "type"], "lane": "songs",
             "weight": "mentor", "amir_reason": "learn", "added": "2026-10-11", "read_level": "read", "notes": "refs/R-002.md",
             "releases": ["pinocchio-single"], "summary": "hooks and shoots"},
        ],
    }


def test_the_real_index_is_valid_and_complete():
    data = archive.load_index(ROOT)
    base = archive.archive_dir(ROOT)
    assert data["references"], "the archive has entries"
    for r in data["references"]:
        assert (base / r["notes"]).is_file(), r["id"]
        assert (base / r["thumb"]).is_file(), r["id"]
        for c in r.get("children") or []:
            assert (base / c["path"]).exists(), (r["id"], c["path"])


def test_validate_catches_bad_values():
    d = _data()
    d["references"][0]["kind"] = "poem"
    d["references"][1]["topics"] = []
    d["references"].append(dict(d["references"][0], id="R-001"))
    errs = archive.validate(d)
    assert any("kind 'poem'" in e for e in errs)
    assert any("topics must be" in e for e in errs)
    assert any("duplicate id" in e for e in errs)


def test_filters_and_sort():
    refs = _data()["references"]
    assert [r["id"] for r in archive.filter_refs(refs, {"topic": "hooks"})] == ["R-002"]
    assert [r["id"] for r in archive.filter_refs(refs, {"lane": "electronic"})] == ["R-001"]   # 'both' counts for every lane
    assert [r["id"] for r in archive.filter_refs(refs, {"release": "pinocchio-single"})] == ["R-002"]
    assert [r["id"] for r in archive.filter_refs(refs, {"q": "COVERS"})] == ["R-001"]
    assert [r["id"] for r in archive.sort_refs(refs, "added")] == ["R-002", "R-001"]
    assert [r["id"] for r in archive.sort_refs(refs, "id")] == ["R-001", "R-002"]


def test_facets_count_over_the_full_set():
    d = _data()
    f = archive.facets(d, d["references"])
    assert {x["value"]: x["count"] for x in f["topics"]} == {"type": 2, "hooks": 1}
    assert f["releases"] == ["pinocchio-single"]


def test_for_release():
    d = _data()
    assert [r["id"] for r in archive.for_release(d, "pinocchio-single")] == ["R-002"]
    assert archive.for_release(d, "nothing") == []


def test_safe_path_never_leaves_the_archive(tmp_path):
    assert archive.safe_path(ROOT, "../../.env") is None
    assert archive.safe_path(ROOT, "/etc/passwd") is None
    assert archive.safe_path(ROOT, "") is None
    p = archive.safe_path(ROOT, "refs/R-001.md")
    assert p is not None and p.name == "R-001.md"


def test_markdown_renders_headings_lists_tables_links():
    md = "# Title (One)\n\nText **bold** and `code` and [in](#x) and [rel](../a.md) and [ext](https://e.com).\n\n" \
         "- a\n  - nested\n- b\n\n1. one\n2. two\n\n| H1 | H2 |\n|---|---|\n| c1 | c2 |\n\n---\n"
    h = archive.render_markdown(md, link_base="/archive/file/refs/")
    assert '<h1 id="title-one">Title (One)</h1>' in h
    assert "<strong>bold</strong>" in h and "<code>code</code>" in h
    assert 'href="#x"' in h and 'href="/archive/file/refs/../a.md"' in h and 'href="https://e.com"' in h
    assert "<ul>" in h and "<li>a<ul>" in h.replace("\n", "") and "<ol>" in h
    assert "<table>" in h and "<th>H1</th>" in h and "<td>c2</td>" in h
    assert "<hr>" in h


def test_markdown_escapes_html():
    h = archive.render_markdown("<script>alert(1)</script> & co")
    assert "<script>" not in h and "&lt;script&gt;" in h and "&amp; co" in h


def test_readme_render_lists_every_reference():
    d = _data()
    text = archive.render_readme(d)
    assert "### R-001" in text and "### R-002" in text and "pinocchio-single" in text


@pytest.fixture
def client():
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_pages_answer(client):
    assert client.get("/archive").status_code == 200
    assert client.get("/archive?topic=colour+and+grade&q=gothic").status_code == 200
    data = archive.load_index(ROOT)
    first = data["references"][0]["id"]
    assert client.get(f"/archive/{first}").status_code == 200
    assert client.get(f"/archive/thumb/{first}").status_code == 200
    assert client.get("/archive/R-999").status_code == 404
    assert client.get("/archive/file/refs/R-001.md").status_code == 200
    assert client.get("/archive/file/rapville/videos/").status_code == 200
    assert client.get("/archive/file/../../.env").status_code == 404
    assert client.get("/archive/file/index.json").status_code == 404      # only markdown is rendered


def test_our_ideas_need_execution_and_filter_apart():
    """Machine-28: our own ideas sit next to the references, need an execution line, no weight."""
    d = _data()
    d["allowed"]["kind"].append("idea")
    ours = {"id": "R-003", "title": "Swan", "source": "Inch of Shadow (ours)", "kind": "idea", "topics": ["type"],
            "lane": "both", "origin": "ours", "execution": "ink, engraving undecided", "amir_reason": "keep it",
            "added": "2026-10-21", "read_level": "read", "notes": "refs/R-003.md", "releases": []}
    d["references"].append(ours)
    assert archive.validate(d) == []
    ours["execution"] = ""
    assert any("execution" in e for e in archive.validate(d))
    ours["execution"] = "ink"
    assert [r["id"] for r in archive.filter_refs(d["references"], {"origin": "ours"})] == ["R-003"]
    assert [r["id"] for r in archive.filter_refs(d["references"], {"origin": "reference"})] == ["R-001", "R-002"]
    assert [r["id"] for r in archive.filter_refs(d["references"], {"q": "engraving"})] == []
    assert {f["value"]: f["count"] for f in archive.facets(d, d["references"])["origin"]} == {"reference": 2, "ours": 1}
    assert "## Our own ideas" in archive.render_readme(d)


def test_archive_detail_shows_example_pictures():
    from release_manager.webapp import app
    c = app.test_client()
    html = c.get("/archive/R-002").get_data(as_text=True)
    assert 'class="archive-examples"' in html and "/effects/" in html
    ours = c.get("/archive/R-014").get_data(as_text=True)
    assert "/imagine/img/" in ours
