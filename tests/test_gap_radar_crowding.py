"""Gap Radar crowding check (GR-02): web search tool passed, URLs vetted, report rewritten."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from release_manager import claude_api

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gap_radar"))


@pytest.fixture(autouse=True)
def _one_claude_api(monkeypatch):
    """gap_radar imports claude_api by bare name: point it at the module conftest already patched."""
    monkeypatch.setitem(sys.modules, "claude_api", claude_api)


import crowding  # noqa: E402
import gap_radar  # noqa: E402


def verdict_text(verdict="open", url="https://a.com/pricing", verified=True):
    return ("Searched.\n```json\n" + json.dumps({
        "verdict": verdict, "reason": "few weak tools",
        "competitors": [{"name": "A", "price": "$5/mo", "url": url, "verified": verified},
                        {"name": "Ghost", "price": "$9", "url": "https://made-up.example", "verified": True}],
        "pay_proof": [{"claim": "A charges $5/mo", "url": url, "verified": verified}]}) + "\n```")


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        stop, text = self.replies.pop(0)
        content = [NS(type="server_tool_use", name="web_search"),
                   NS(type="web_search_tool_result", content=[NS(type="web_search_result", url="https://www.a.com/pricing/")]),
                   NS(type="text", text=text, citations=None)]
        return NS(content=content, stop_reason=stop,
                  usage=NS(input_tokens=1000, output_tokens=100, server_tool_use=NS(web_search_requests=2)))


GAP = {"name": "Gap", "pain": "p", "who_pays": "w", "evidence_ids": [0], "pay_signal": "s",
       "product_idea": "i", "build_weeks": 2, "fit_for_us": 4, "known_competitors": "A", "check_next": "c"}


def test_ask_passes_tools_only_when_given():
    c = Fake([("end_turn", "x"), ("end_turn", "x")])
    claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="low")
    claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="low", tools=[crowding.SEARCH_TOOL])
    assert "tools" not in c.calls[0]
    assert c.calls[1]["tools"] == [crowding.SEARCH_TOOL]


def test_web_searches_are_costed_into_the_ledger():
    c = Fake([("end_turn", "x")])
    u = claude_api.usage_of(claude_api.ask(c, max_tokens=10, system="s", messages=[], effort="low"))
    assert u["web_searches"] == 2
    assert u["cost_usd"] == pytest.approx(1000 * 4e-6 + 100 * 20e-6 + 2 * 0.01)
    assert claude_api.month_spend()["usd"] == pytest.approx(u["cost_usd"], abs=1e-4)


def test_check_vets_urls_against_search_results():
    c = Fake([("end_turn", verdict_text())])
    out = crowding.check([GAP], client=c)
    v = out[0]["crowding"]
    assert c.calls[0]["tools"][0]["type"] == "web_search_20260209"
    assert v["verdict"] == "open" and v["web_searches"] == 2
    comp = {x["name"]: x["verified"] for x in v["competitors"]}
    assert comp == {"A": True, "Ghost": False}          # never returned by the search
    assert v["pay_proof"][0]["verified"] is True


def test_open_without_verified_pay_proof_becomes_unclear():
    c = Fake([("end_turn", verdict_text(url="https://not-searched.com"))])
    v = crowding.check([GAP], client=c)[0]["crowding"]
    assert v["verdict"] == "unclear" and "no verified pay proof" in v["reason"]


def test_pause_turn_is_resumed_and_bad_reply_is_unclear():
    c = Fake([("pause_turn", "still searching"), ("end_turn", verdict_text("crowded"))])
    v = crowding.check([GAP], client=c)[0]["crowding"]
    assert len(c.calls) == 2 and c.calls[1]["messages"][-1]["role"] == "assistant"
    assert v["verdict"] == "crowded"
    v2 = crowding.check([GAP], client=Fake([("end_turn", "no json here")]))[0]["crowding"]
    assert v2["verdict"] == "unclear" and v2["reason"].startswith("check failed")


def test_report_lists_open_first_and_drops_crowded(tmp_path, monkeypatch):
    monkeypatch.setattr(gap_radar, "HERE", tmp_path)
    (tmp_path / "raw").mkdir()
    (tmp_path / "reports").mkdir()
    raw = tmp_path / "raw" / "2026-01-01.json"
    raw.write_text(json.dumps([{"src": "hackernews", "title": "t", "text": "x", "url": "https://hn/1"}]))
    (tmp_path / "reports" / "2026-01-01.md").write_text("x Claude cost $1.02. y")
    mk = lambda name, verdict: {**GAP, "name": name, "crowding": {
        "verdict": verdict, "reason": f"r-{name}", "cost_usd": 0.5, "web_searches": 1,
        "competitors": [{"name": "Big", "price": "$1", "url": "https://big", "verified": False}],
        "pay_proof": []}}
    gaps = [mk("Crowd", "crowded"), mk("Maybe", "unclear"), mk("Win", "open")]
    md = gap_radar.analyze(raw, gaps=gaps).read_text()
    assert md.index("[OPEN] Win") < md.index("[UNCLEAR] Maybe") < md.index("## Dropped (crowded)")
    assert "- Crowd: r-Crowd (Big)" in md and "## 3." not in md
    assert "$1.02 (analysis) + $1.50 (crowding" in md and "(unverified)" in md
    saved = json.loads((tmp_path / "reports" / "2026-01-01.json").read_text())
    assert [g["crowding"]["verdict"] for g in saved] == ["crowded", "unclear", "open"]
