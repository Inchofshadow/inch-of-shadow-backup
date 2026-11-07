"""plans/decisions_writeback.py: decisions file -> targets, tickets, handovers (temp copies only)."""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("decisions_writeback", ROOT / "plans" / "decisions_writeback.py")
wb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wb)


@pytest.fixture
def repo(tmp_path):
    """A temp root with copies of the real targets file, both boards and one handover."""
    for rel in ("plans/targets.json", "plans/tickets.json", "plans/control-panel/tickets.json",
                "plans/handovers/system/system.md"):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    # The tests assume the state of 2026-11-05: rungs still proposed, no decisions section yet.
    # Amir confirmed the rungs on 2026-11-06, so the copies are reset here instead of the live files.
    tp = tmp_path / "plans" / "targets.json"
    t = json.loads(tp.read_text(encoding="utf-8"))
    for key in ("spotify_followers", "email_list"):
        t["metrics"][key]["confirmed"] = False
    tp.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = tmp_path / "plans" / "handovers" / "system" / "system.md"
    text = md.read_text(encoding="utf-8")
    cut = text.find("\n## Decisions ")
    if cut != -1:
        md.write_text(text[:cut + 1], encoding="utf-8")
    return tmp_path


def decisions_file(root, *decisions, day="2026-11-09"):
    p = root / "plans" / ("decisions-%s.json" % day)
    p.write_text(json.dumps(list(decisions), ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def D(did, writes, question="q?", answer="yes", day="2026-11-09"):
    return {"id": did, "question": question, "answer": answer, "answered_at": day, "writes": writes}


def W(file, key, value=None):
    return {"file": file, "key_or_section": key, "value": value}


def test_dry_run_prints_plan_and_writes_nothing(repo, capsys):
    f = decisions_file(repo, D("D1", [W("plans/targets.json", "metrics.spotify_followers.confirmed", True),
                                     W("plans/tickets.json", "G-20.bucket", "now")]))
    before = {p: (repo / p).read_bytes() for p in ("plans/targets.json", "plans/tickets.json")}
    assert wb.main([str(f), "--dry-run", "--root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "[dry run]" in out and "2 write(s)" in out
    assert "metrics.spotify_followers.confirmed: False -> True" in out
    assert "G-20.bucket: 'next' -> 'now'" in out
    for p, raw in before.items():
        assert (repo / p).read_bytes() == raw
    assert not list((repo / "plans").glob(".*.bak-*"))


def test_targets_confirmed_and_rung_written_with_backup(repo):
    f = decisions_file(repo, D("D1", [
        W("plans/targets.json", "metrics.spotify_followers.confirmed", True),
        W("plans/targets.json", "metrics.spotify_followers.rungs.2026-11-30", 85),
        W("plans/targets.json", "metrics.email_list.target", 60),
    ]))
    res = wb.run(f, root=repo)
    assert res["applied"] == 3
    t = json.loads((repo / "plans" / "targets.json").read_text(encoding="utf-8"))
    assert t["metrics"]["spotify_followers"]["confirmed"] is True
    assert t["metrics"]["spotify_followers"]["rungs"]["2026-11-30"] == 85
    assert t["metrics"]["spotify_followers"]["rungs"]["2026-12-31"] == 90     # untouched rung stays
    assert t["metrics"]["email_list"]["target"] == 60
    bak = repo / "plans" / ".targets.json.bak-2026-11-09-decisions"
    assert bak.exists() and res["backups"] == [bak]
    assert json.loads(bak.read_text(encoding="utf-8"))["metrics"]["spotify_followers"]["confirmed"] is False
    from stats.targets import load_targets
    load_targets(repo / "plans" / "targets.json")        # still a valid targets file


def test_ticket_fields_written_on_both_boards_and_updated_set(repo):
    f = decisions_file(repo, D("D2", [
        W("plans/tickets.json", "G-15.bucket", "now"),
        W("plans/tickets.json", "G-15.who", "claude"),
        W("plans/tickets.json", "R-10.status", "approved"),
        W("plans/control-panel/tickets.json", "Formats-04.bucket", "next"),
    ]))
    wb.run(f, root=repo)
    main = json.loads((repo / "plans" / "tickets.json").read_text(encoding="utf-8"))
    g15 = next(t for t in main["tickets"] if t["id"] == "G-15")
    assert g15["bucket"] == "now" and g15["who"] == "claude" and g15["updated"] == "2026-11-09"
    r10 = next(t for t in main["tickets"] if t["id"] == "R-10")
    assert r10["status"] == "approved" and r10["updated"] == "2026-11-09"
    assert main["updated"] == "2026-11-09"
    cp = json.loads((repo / "plans" / "control-panel" / "tickets.json").read_text(encoding="utf-8"))
    f04 = next(t for t in cp["tickets"] if t["id"] == "Formats-04")
    assert f04["bucket"] == "next" and f04["updated"] == "2026-11-09"
    assert (repo / "plans" / ".tickets.json.bak-2026-11-09-decisions").exists()
    assert (repo / "plans" / "control-panel" / ".tickets.json.bak-2026-11-09-decisions").exists()
    from release_manager.tickets import load_tickets
    from release_manager.board import load_board
    load_tickets(repo / "plans" / "tickets.json")
    load_board(repo / "plans" / "control-panel" / "tickets.json")


def test_handover_gets_decisions_section_once_and_lines_appended(repo):
    md = repo / "plans" / "handovers" / "system" / "system.md"
    f = decisions_file(repo,
                       D("D3", [W("plans/handovers/system/system.md", "beatport", "cancel the add-on")],
                         question="Keep Beatport?", answer="no"),
                       D("D4", [W("plans/handovers/system/system.md", "-")], question="Rungs ok?", answer="yes"))
    wb.run(f, root=repo)
    text = md.read_text(encoding="utf-8")
    assert text.count("## Decisions 2026-11-09") == 1
    assert "- D3 [beatport] Keep Beatport? -> no (cancel the add-on)" in text
    assert "- D4 Rungs ok? -> yes" in text
    assert text.index("- D3 ") < text.index("- D4 ")
    assert (md.parent / ".system.md.bak-2026-11-09-decisions").exists()
    # a second run on a later day opens a new section; same day appends into the existing one
    wb.run(decisions_file(repo, D("D5", [W("plans/handovers/system/system.md", "-")], question="More?", answer="later")), root=repo)
    text = md.read_text(encoding="utf-8")
    assert text.count("## Decisions 2026-11-09") == 1 and "- D5 More? -> later" in text


def test_appends_inside_an_existing_section_not_after_later_sections(repo):
    md = repo / "plans" / "handovers" / "system" / "system.md"
    md.write_text("# H\n\n## Decisions 2026-11-09\n- D0 old\n\n## Later\ntext\n", encoding="utf-8")
    wb.run(decisions_file(repo, D("D1", [W("plans/handovers/system/system.md", "-")], question="Q", answer="A")), root=repo)
    text = md.read_text(encoding="utf-8")
    assert text.index("- D0 old") < text.index("- D1 Q -> A") < text.index("## Later")


@pytest.mark.parametrize("write", [
    W("plans/targets.json", "metrics.nope.confirmed", True),
    W("plans/targets.json", "metrics.spotify_followers.confirmed", "yes"),
    W("plans/targets.json", "metrics.spotify_followers.rungs.Nov30", 85),
    W("plans/targets.json", "period.end", "2027-01-01"),
    W("plans/tickets.json", "ZZ-99.bucket", "now"),
    W("plans/tickets.json", "G-20.bucket", "soon"),
    W("plans/tickets.json", "G-20.who", "fable"),
    W("plans/tickets.json", "G-20.status", "maybe"),
    W("plans/tickets.json", "G-20.title", "x"),
    W("plans/tickets.json", "G-20.due", "next week"),
    W("plans/tickets.json", "G-20.metric", "none"),
    W("stats/spend.py", "x", 1),
    W("../outside.md", "-"),
])
def test_bad_writes_are_refused_before_anything_changes(repo, write):
    f = decisions_file(repo, D("D1", [W("plans/targets.json", "metrics.spotify_followers.confirmed", True), write]))
    before = (repo / "plans" / "targets.json").read_bytes()
    with pytest.raises(wb.WritebackError):
        wb.run(f, root=repo)
    assert (repo / "plans" / "targets.json").read_bytes() == before
    assert not list((repo / "plans").glob(".*.bak-*"))


def test_cli_picks_file_by_date_and_reports_errors(repo, capsys):
    assert wb.main(["2026-11-09", "--root", str(repo)]) == 2      # no such decisions file
    assert "error:" in capsys.readouterr().err
    decisions_file(repo, D("D1", [W("plans/targets.json", "metrics.email_list.confirmed", True)]))
    assert wb.main(["2026-11-09", "--root", str(repo)]) == 0
    assert "applied 1 write(s)" in capsys.readouterr().out
