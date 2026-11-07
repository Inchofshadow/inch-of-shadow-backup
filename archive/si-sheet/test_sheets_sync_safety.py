"""Sheets sync-back safety (audit P2-12/13).

Stale-overwrite protection: a sheet cell that still shows what WE last
pushed must not revert a newer SI-side edit. Name collisions: ambiguous
display names get no edits and no deletes. Prune guards: no pruning on
partial sheet reads, and a per-run cap.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scene_intelligence"))
import push_to_sheets as p  # noqa: E402


class _WS:
    def __init__(self, rows):
        self._rows = rows

    def get_all_values(self):
        return self._rows


class _Sheet:
    def __init__(self, tabs):
        self._tabs = tabs

    def worksheet(self, name):
        if name not in self._tabs:
            raise p.gspread.WorksheetNotFound(name)
        return _WS(self._tabs[name])


HDR = ["Name", "Category", "Type", "Genre", "Score", "Promo", "Delete"]


def _sheet_with_all_tabs(rows_by_tab):
    """Every _SYNC_TABS tab present (default just a header) so the
    tabs-failed prune guard doesn't trigger unless a test wants it to.
    Header-only tabs count as 'failed' loads, so pad with a dummy row."""
    tabs = {}
    dummy = ["__dummy__", "", "", "", "", "", ""]
    for t in p._SYNC_TABS:
        tabs[t] = rows_by_tab.get(t, [HDR, dummy])
    return _Sheet(tabs)


def _setup(monkeypatch, tmp_path, snapshot=None):
    monkeypatch.setattr(p, "_rate_limit", lambda: None)
    monkeypatch.setattr(p, "SNAPSHOT_FILE", tmp_path / "snap.json")
    monkeypatch.setattr(p, "ENRICHED_FILE", tmp_path / "enriched.json")
    if snapshot is not None:
        import json
        (tmp_path / "snap.json").write_text(json.dumps(snapshot))


def test_stale_sheet_value_does_not_revert_local_edit(monkeypatch, tmp_path):
    # We pushed category "dj"; sheet still says "dj"; local was since
    # changed to "label" -> sync must KEEP "label".
    _setup(monkeypatch, tmp_path,
           snapshot={"Armela": {"category": "dj", "sub_type": "", "genre": "",
                                "score": "", "promo": ""}})
    contacts = [{"name": "Armela", "category": "label"}]
    sheet = _sheet_with_all_tabs(
        {"DJs": [HDR, ["Armela", "dj", "", "", "", "", ""]]})
    p.sync_from_sheet(sheet, contacts)
    assert contacts[0]["category"] == "label"


def test_human_sheet_edit_still_applies(monkeypatch, tmp_path):
    # We pushed "dj" but the sheet now says "venue" -> human edit, apply.
    _setup(monkeypatch, tmp_path,
           snapshot={"Armela": {"category": "dj", "sub_type": "", "genre": "",
                                "score": "", "promo": ""}})
    contacts = [{"name": "Armela", "category": "dj"}]
    sheet = _sheet_with_all_tabs(
        {"DJs": [HDR, ["Armela", "venue", "", "", "", "", ""]]})
    p.sync_from_sheet(sheet, contacts)
    assert contacts[0]["category"] == "venue"


def test_no_snapshot_behaves_like_before(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, snapshot=None)
    contacts = [{"name": "Armela", "category": "dj"}]
    sheet = _sheet_with_all_tabs(
        {"DJs": [HDR, ["Armela", "venue", "", "", "", "", ""]]})
    p.sync_from_sheet(sheet, contacts)
    assert contacts[0]["category"] == "venue"


def test_stale_promo_not_cleared(monkeypatch, tmp_path):
    # We pushed promo "" and Amir since set promo_list=yes in SI; the sheet
    # cell is still empty -> must NOT clear the local yes.
    _setup(monkeypatch, tmp_path,
           snapshot={"Armela": {"category": "dj", "sub_type": "", "genre": "",
                                "score": "", "promo": ""}})
    contacts = [{"name": "Armela", "category": "dj", "promo_list": "yes"}]
    sheet = _sheet_with_all_tabs(
        {"DJs": [HDR, ["Armela", "dj", "", "", "", "", ""]]})
    p.sync_from_sheet(sheet, contacts)
    assert contacts[0]["promo_list"] == "yes"


def test_ambiguous_name_gets_no_edits_or_delete(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    contacts = [
        {"name": "Shadow", "category": "dj"},
        {"name": "Shadow", "category": "label"},
    ]
    sheet = _sheet_with_all_tabs(
        {"DJs": [HDR, ["Shadow", "venue", "", "", "", "", "x"]]})
    changes, deletes = p.sync_from_sheet(sheet, contacts)
    assert deletes == 0
    assert len(contacts) == 2
    assert contacts[0]["category"] == "dj"
    assert contacts[1]["category"] == "label"


def test_prune_skipped_when_tab_fails(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    contacts = [{"name": "Vanished", "category": "dj", "match_score": "5"}]
    tabs = {t: [HDR, ["__dummy__", "", "", "", "", "", ""]]
            for t in p._SYNC_TABS}
    del tabs["Labels"]  # one tab unreadable
    p.sync_from_sheet(_Sheet(tabs), contacts, prune_missing=True)
    assert len(contacts) == 1  # nothing pruned


def test_prune_cap_refuses_mass_delete(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    contacts = [{"name": f"c{i}", "category": "dj", "match_score": "5"}
                for i in range(p.MAX_PRUNE_PER_RUN + 5)]
    sheet = _sheet_with_all_tabs({})  # none of the contacts appear anywhere
    p.sync_from_sheet(sheet, contacts, prune_missing=True)
    assert len(contacts) == p.MAX_PRUNE_PER_RUN + 5  # refused, kept all


def test_prune_under_cap_still_works(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    contacts = [
        {"name": "Vanished", "category": "dj", "match_score": "5"},
        {"name": "__dummy__", "category": "dj", "match_score": "5"},
    ]
    sheet = _sheet_with_all_tabs({})
    p.sync_from_sheet(sheet, contacts, prune_missing=True)
    assert [c["name"] for c in contacts] == ["__dummy__"]


def test_snapshot_roundtrip(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    p.write_push_snapshot([{"name": "Armela", "category": "DJ",
                            "match_score": 7, "promo_list": "yes"}])
    snap = p.load_push_snapshot()
    assert snap["Armela"]["category"] == "dj"
    assert snap["Armela"]["score"] == "7"
    assert snap["Armela"]["promo"] == "yes"
