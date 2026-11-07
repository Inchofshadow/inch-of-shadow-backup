"""GR-10 profile quality check: no network, no Claude."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gap_radar"))
import profile_check as pc  # noqa: E402


def prof(**sources):
    return {"name": "t", "question": "q", "sources": sources}


def test_generic_keywords_flagged_specific_kept():
    p = prof(reddit={"subs": ["x"], "phrases": ['"best app"', '"is there a tool"']},
             hn_queries=["is there a tool", "spreadsheet"],
             youtube_queries=["best app", "wedding photographer culling workflow"])
    # inside a named subreddit intent phrases are fine; site-wide they are noise
    assert pc.generic_keywords(p) == ["is there a tool", "best app"]


def test_source_problems_uses_and_fills_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "CACHE", tmp_path / "c.json")
    seen = []

    def fake(name):
        seen.append(name)
        return {"real": "ok", "fake": "missing", "slow": "unknown"}[name]

    p = prof(reddit={"subs": ["real", "fake", "slow"], "phrases": []})
    out = pc.source_problems(p, check=fake)
    assert out == {"missing": ["r/fake"], "unknown": ["r/slow"]}
    cache = json.loads((tmp_path / "c.json").read_text())
    assert cache == {"r/fake": "missing", "r/real": "ok"}      # unknown is never cached
    seen.clear()
    pc.source_problems(p, check=fake)
    assert seen == ["slow"]                                     # cached ones are not re-checked


def test_pre_check_line(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "CACHE", tmp_path / "c.json")
    p = prof(reddit={"subs": ["real"], "phrases": ['"by hand"']}, youtube_queries=["best app"])
    line = pc.pre_check(p, check=lambda n: "ok")
    assert line == "Check t: Keywords: 1 of 2 specific, generic: best app | sources: all real"


def test_keyword_yield(tmp_path):
    items = [{"title": "", "text": "I do this by hand every week"},
             {"title": "By hand again", "text": ""},
             {"title": "", "text": "my spreadsheet broke"},
             {"title": "", "text": "nothing related"}]
    p = prof(reddit={"subs": ["x"], "phrases": ['"by hand"', '"spreadsheet"', '"takes me hours"']})
    y = pc.keyword_yield(p, items, [{"evidence_ids": [0, 1]}])
    assert y == {'"by hand"': "strong", '"spreadsheet"': "weak", '"takes me hours"': "dead"}
    (tmp_path / "raw.json").write_text(json.dumps(items))
    (tmp_path / "rep.json").write_text(json.dumps([{"evidence_ids": [0, 1]}]))
    line = pc.yield_line(p, tmp_path / "rep.json", tmp_path / "raw.json")
    assert line.startswith("Keyword yield t: 1 of 3 strong | weak/dead:")


def test_review_writes_file_and_line(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "REVIEWS", tmp_path)
    import claude_api

    class Msg:
        pass

    reply = {"verdict": "Mostly specific.", "generic": ["best app"],
             "better_keywords": ["culling", "Lightroom catalog"], "better_sources": []}
    monkeypatch.setattr(claude_api, "ask", lambda *a, **k: Msg())
    monkeypatch.setattr(claude_api, "text_of", lambda m: json.dumps(reply))
    p = {"name": "t", "question": "q", "sources": {}}
    line = pc.review(p, client=object())
    assert line == "Review t: Mostly specific. | generic: best app | try: culling, Lightroom catalog"
    assert json.loads((tmp_path / "t.json").read_text()) == reply
