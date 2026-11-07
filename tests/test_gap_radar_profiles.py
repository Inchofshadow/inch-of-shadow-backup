"""GR-03: profile-driven Gap Radar. All HTTP and Claude calls mocked; ledgers in tmp."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from release_manager import claude_api

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gap_radar"))
sys.path.insert(0, str(ROOT / "scene_intelligence"))


@pytest.fixture(autouse=True)
def _one_claude_api(monkeypatch):
    monkeypatch.setitem(sys.modules, "claude_api", claude_api)


import gap_radar as gr  # noqa: E402
import ig_daily_ledger as L  # noqa: E402
import sources_extra as sx  # noqa: E402

IOS = ["producer-tools", "song-ideas", "brand-marketing", "ig-hooks", "music-seo", "scene-outreach"]
SOURCE_KEYS = {"reddit", "hn_queries", "stackexchange", "youtube_queries", "github_queries",
               "appstore", "hikerapi"}


def test_all_profiles_load_with_the_fixed_format():
    names = sorted(p.stem for p in gr.PROFILES_DIR.glob("*.json"))
    assert set(IOS + ["income-gaps"]) <= set(names)
    for n in IOS + ["income-gaps"]:
        p = gr.load_profile(n)
        assert set(gr.PROFILE_KEYS) <= set(p) and set(p["sources"]) == SOURCE_KEYS
        assert p["sources"]["hikerapi"]["max_calls"] == 0          # HikerAPI off by default
        assert p["question"].strip() and p["output_dir"]
    assert [n for n in IOS if gr.load_profile(n)["crowding"]] == ["producer-tools"]
    assert gr.load_profile("income-gaps")["crowding"] is True
    assert "never" in gr.load_profile("song-ideas")["system_extra"].lower()   # no lyrics rule
    assert "lyrics" in gr.load_profile("song-ideas")["system_extra"]


def test_income_gaps_keeps_the_old_core():
    # GR-10 (2026-11-05) tuned the profile after its quality review: generic subs and
    # site-wide queries were swapped for specific ones; the original buy-intent phrases stay.
    s = gr.load_profile("income-gaps")["sources"]
    assert set(gr.PHRASES) <= set(s["reddit"]["phrases"])
    assert {"SaaS", "smallbusiness", "freelance"} <= set(s["reddit"]["subs"])
    assert s["appstore"]["genres"] == list(gr.APPSTORE_GENRES)
    assert s["stackexchange"] == {"sites": sx.SE_SITES, "queries": sx.SE_PHRASES}


@pytest.mark.parametrize("bad", ["../x", "Upper", "a/b", ""])
def test_bad_profile_names_refused(bad):
    with pytest.raises(SystemExit):
        gr.load_profile(bad)


def profile(tmp_path, **over):
    p = {"name": "t", "question": "Q?", "system_extra": "EXTRA", "output_dir": str(tmp_path / "out"),
         "crowding": False, "sources": {}}
    p.update(over)
    return p


def test_collect_runs_only_given_sources_into_profile_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(gr, "HERE", tmp_path)
    monkeypatch.setattr(gr.time, "sleep", lambda s: None)
    calls = []

    def fake_get(url, headers=None, timeout=None, params=None):
        calls.append(url)
        return NS(status_code=200, raise_for_status=lambda: None, json=lambda: {"hits": [
            {"objectID": "1", "title": "Need a sampler", "comment_text": "would pay", "created_at": "2026-11-01"}]})
    monkeypatch.setattr(gr.requests, "get", fake_get)
    p = profile(tmp_path, sources={"hn_queries": ["x"], "reddit": {"subs": ["a"], "phrases": []},
                                   "youtube_queries": [], "hikerapi": {"hashtags": ["t"], "max_calls": 0}})
    path = gr.collect(p)
    assert all("algolia" in u for u in calls) and len(calls) == 1
    assert path.parent == tmp_path / "raw" / "t"
    assert json.loads(path.read_text())[0]["title"] == "Need a sampler"


def test_bad_subreddit_name_is_never_put_in_a_url(monkeypatch):
    monkeypatch.setattr(gr.requests, "get", lambda *a, **k: pytest.fail("no request expected"))
    assert gr.reddit(["../../x", "a b"], ['"p"']) == []


class FakeClaude:
    def __init__(self, payload):
        self.payload, self.calls = payload, []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return NS(content=[NS(type="text", text=json.dumps(self.payload))], stop_reason="end_turn",
                  usage=NS(input_tokens=1000, output_tokens=100))


def test_insight_profile_report(tmp_path, monkeypatch):
    raw = tmp_path / "2026-11-05.json"
    raw.write_text(json.dumps([{"src": "reddit r/darkwave", "title": "t", "text": "x", "url": "https://r/1"},
                               {"src": "youtube 'q'", "title": "t", "text": "y", "url": "https://y/2"}]))
    fake = FakeClaude({"findings": [{"name": "Night drives", "insight": "many describe", "examples": ["empty roads"],
                                     "evidence_ids": [0, 1, 9], "use": "a song angle", "strength": 4}]})
    monkeypatch.setattr(claude_api, "client", lambda *a, **k: fake)
    p = profile(tmp_path)
    md = gr.analyze(raw, profile=p)
    assert md == tmp_path / "out" / "2026-11-05.md"
    text = md.read_text()
    assert "## 1. Night drives  (strength 4/5" in text and "Examples: empty roads" in text
    assert "https://r/1" in text and "Question: Q?" in text
    sent = fake.calls[0]
    assert "Q?" in sent["system"] and sent["system"].rstrip().endswith("EXTRA")
    assert "never song lyrics" in sent["system"]
    assert sent["output_config"]["format"]["schema"] is gr.INSIGHT_SCHEMA
    assert claude_api.month_spend()["calls"] == 1                  # costed into the (tmp) ledger
    with pytest.raises(SystemExit):
        gr.check_report(p)                                          # insight: no crowding check


def test_product_profile_uses_gap_schema(tmp_path, monkeypatch):
    raw = tmp_path / "r.json"
    raw.write_text(json.dumps([{"src": "hackernews", "title": "t", "text": "x", "url": "https://h/1"}]))
    gap = {"name": "G", "pain": "p", "who_pays": "w", "evidence_ids": [0], "pay_signal": "s",
           "product_idea": "i", "build_weeks": 2, "fit_for_us": 4, "known_competitors": "A", "check_next": "c"}
    fake = FakeClaude({"gaps": [gap]})
    monkeypatch.setattr(claude_api, "client", lambda *a, **k: fake)
    md = gr.analyze(raw, profile=profile(tmp_path, crowding=True, name="producer-tools"))
    assert "# Gap Radar: producer-tools - r" in md.read_text()
    assert fake.calls[0]["output_config"]["format"]["schema"] is gr.SCHEMA
    assert claude_api.month_spend()["usd"] > 0


def test_relative_output_dir_is_repo_relative():
    assert gr.report_dir({"output_dir": "gap_radar/reports/x"}) == gr.HERE.parent / "gap_radar/reports/x"
    assert gr.report_dir({"output_dir": "/abs/dir"}) == Path("/abs/dir")


def test_github_free_queries():
    seen = []

    def fake_get(url, pause, params=None):
        seen.append(params["q"])
        return NS(json=lambda: {"items": []})
    orig = sx._get
    sx._get = fake_get
    try:
        sx.github(queries=["repo:a/b reactions:>=5", "repo:c/d"], min_reactions=30)
    finally:
        sx._get = orig
    assert seen[0].count("reactions:") == 1 and "reactions:>=5" in seen[0]
    assert "repo:c/d reactions:>=30" in seen[1]


# --- HikerAPI -------------------------------------------------------------------------------

class FakeProvider:
    def __init__(self):
        self.calls = []

    def _get(self, path, **params):
        self.calls.append((path, params))
        if "hashtag" in path:
            return [[{"pk": "11", "code": "AB", "caption_text": "new set tonight", "comment_count": 5,
                      "taken_at": 1762300000},
                     {"pk": "12", "code": "CD", "caption_text": "", "comment_count": 0}], "next"]
        if "comments" in path:
            return {"comments": [{"text": "what synth is that bassline from?", "created_at_utc": 1762300000},
                                 {"text": "fire"}]}
        return None


def ledger_with(tmp_path, used, day="2026-11-05"):
    path = tmp_path / "ig_daily_ledger.json"
    path.write_text(json.dumps({"runs": [{"date": day, "script": "ig_audit_queue_freshness",
                                          "kind": "provider", "est_calls": used}]}))
    return path


@pytest.fixture
def cap300(monkeypatch):
    monkeypatch.setattr(L, "provider_cap", lambda: 350)          # config may say more; radar stays at 300


def test_hikerapi_off_when_max_calls_zero(tmp_path, cap300):
    prov = FakeProvider()
    assert gr.hikerapi({"hashtags": ["ebm"], "max_calls": 0}, "t", provider=prov,
                       ledger_path=ledger_with(tmp_path, 0), today="2026-11-05") == []
    assert prov.calls == []


def test_hikerapi_uses_only_the_leftover_and_claims_it(tmp_path, cap300):
    path, prov = ledger_with(tmp_path, 298), FakeProvider()
    items = gr.hikerapi({"hashtags": ["ebm", "coldwave", "darkwave"], "max_calls": 50}, "ig-hooks",
                        provider=prov, ledger_path=path, today="2026-11-05")
    assert len(prov.calls) == 2                                   # 300 - 298 = 2 left
    claim = [r for r in json.loads(path.read_text())["runs"] if r["script"] == "gap_radar_ig-hooks"]
    assert claim[0]["kind"] == "provider" and claim[0]["est_calls"] == 2
    assert {it["title"] for it in items} == {"caption"}           # no budget left for comments


def test_hikerapi_items_and_nothing_when_cap_used(tmp_path, cap300):
    prov = FakeProvider()
    items = gr.hikerapi({"hashtags": ["#ebm"], "max_calls": 5}, "t", provider=prov,
                        ledger_path=ledger_with(tmp_path, 0), today="2026-11-05")
    assert [c[0] for c in prov.calls] == ["/v1/hashtag/medias/top/chunk", "/v1/media/comments/chunk"]
    assert prov.calls[0][1] == {"name": "ebm"}
    texts = {it["text"]: it for it in items}
    assert "fire" not in texts and texts["what synth is that bassline from?"]["src"] == "instagram #ebm"
    assert texts["new set tonight"]["url"] == "https://www.instagram.com/p/AB/"
    prov2 = FakeProvider()
    assert gr.hikerapi({"hashtags": ["ebm"], "max_calls": 5}, "t2", provider=prov2,
                       ledger_path=ledger_with(tmp_path, 300), today="2026-11-05") == []
    assert prov2.calls == []


def test_load_profile_from_a_file_path(tmp_path):
    src = gr.PROFILES_DIR / "song-ideas.json"
    f = tmp_path / "song-ideas.json"
    f.write_text(src.read_text())
    assert gr.load_profile(str(f))["name"] == "song-ideas"
    with pytest.raises(SystemExit):
        gr.load_profile(str(tmp_path / "missing.json"))
