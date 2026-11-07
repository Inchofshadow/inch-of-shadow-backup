"""Machine-22: Claude draft review on the Imagine page (fake client, nothing sent)."""

import json
from types import SimpleNamespace

import pytest
from PIL import Image

from release_manager import imagine as im
from release_manager import imagine_review as rv


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(im, "OUT", tmp_path)
    return tmp_path


def make(out, image_id, **extra):
    Image.new("RGB", (2048, 1024), (40, 30, 20)).save(out / f"{image_id}.png")
    rec = {"id": image_id, "file": f"{image_id}.png", "made": "2026-10-20T10:00:00", "model": "gpt-image-2.5-flare",
           "quality": "low", "size": "2048x1024", "kind": "cover", "prompt": "USE: cover\n\nSUBJECT: a lamp",
           "decision": None, **extra}
    (out / f"{image_id}.json").write_text(json.dumps(rec))
    return rec


class FakeClient:
    def __init__(self, reply, stop="end_turn"):
        self.calls = []
        self.reply, self.stop = reply, stop
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(
            content=[SimpleNamespace(type="thinking", thinking=""),
                     SimpleNamespace(type="text", text=json.dumps(self.reply))],
            stop_reason=self.stop, usage=SimpleNamespace(input_tokens=2000, output_tokens=500))


FIX = {"verdict": "fix", "summary": "Small letters in the corner.",
       "issues": [{"area": "text", "note": "letters bottom left"}, {"area": "made-up", "note": "dropped"}],
       "prompt_fix": "Add: no lettering anywhere, including the corners."}


def test_review_saves_into_record_and_sends_prompt_and_downscaled_image(out):
    make(out, "x_1")
    c = FakeClient(FIX)
    rec = rv.review("x_1", client=c)
    kw = c.calls[0]
    assert kw["model"] == "claude-opus-5-5"
    assert kw["output_config"]["effort"] == "medium"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["extra_body"] == {"fallbacks": "default"}
    blocks = kw["messages"][0]["content"]
    assert blocks[0]["type"] == "image" and "SUBJECT: a lamp" in blocks[1]["text"]
    import base64, io
    w, h = Image.open(io.BytesIO(base64.b64decode(blocks[0]["source"]["data"]))).size
    assert max(w, h) <= rv.MAX_EDGE
    saved = json.loads((out / "x_1.json").read_text())["review"]
    assert saved == rec["review"]
    assert saved["verdict"] == "fix" and [i["area"] for i in saved["issues"]] == ["text"]
    assert saved["cost_usd"] == pytest.approx(2000 * 4e-6 + 500 * 20e-6)


def test_pass_clears_the_prompt_fix(out):
    make(out, "x_2")
    rec = rv.review("x_2", client=FakeClient({"verdict": "pass", "summary": "Good.", "issues": [], "prompt_fix": "x"}))
    assert rec["review"]["prompt_fix"] == ""


def test_review_keeps_a_decision_saved_meanwhile(out):
    make(out, "x_3")

    class Racing(FakeClient):
        def create(self, **kw):
            im.set_decision("x_3", "keep")
            return super().create(**kw)

    rec = rv.review("x_3", client=Racing(FIX))
    assert rec["decision"] == "keep" and rec["review"]["verdict"] == "fix"


@pytest.mark.parametrize("extra", [{"kind": "composite"}, {"photo": "out-152.jpg"}, {"plate": "x_1"},
                                   {"model": "local composite", "quality": "-"}, {"model": ""}])
def test_composites_and_his_photo_are_never_sent(out, extra):
    make(out, "c_1", **extra)
    c = FakeClient(FIX)
    with pytest.raises(rv.ReviewError):
        rv.review("c_1", client=c)
    assert c.calls == []


def test_unknown_image_and_refusal(out):
    with pytest.raises(rv.ReviewError):
        rv.review("nope", client=FakeClient(FIX))
    make(out, "x_4")
    with pytest.raises(rv.ReviewError):
        rv.review("x_4", client=FakeClient(FIX, stop="refusal"))
    assert "review" not in json.loads((out / "x_4.json").read_text())


def test_route_returns_review_and_errors(out, monkeypatch):
    from release_manager import webapp
    make(out, "x_5")
    monkeypatch.setattr(rv, "_client", lambda: FakeClient(FIX))
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    c = app.test_client()
    r = c.post("/imagine/review", json={"id": "x_5"})
    assert r.status_code == 200 and r.get_json()["review"]["verdict"] == "fix"
    make(out, "c_2", kind="composite")
    r = c.post("/imagine/review", json={"id": "c_2"})
    assert r.status_code == 400 and not r.get_json()["ok"]


def test_current_never_list_is_sent_even_when_the_prompt_predates_it(out, monkeypatch):
    make(out, "x_6")
    monkeypatch.setattr(im, "never_global", lambda: ["No churches, domes, crosses."])
    c = FakeClient(FIX)
    rv.review("x_6", client=c)
    text = c.calls[0]["messages"][0]["content"][1]["text"]
    assert "CURRENT RULES" in text and "No churches, domes, crosses." in text and "Brand core:" in text


def test_route_shows_the_claude_api_reason_not_a_generic_message(out, monkeypatch):
    import anthropic, httpx
    from release_manager import webapp
    make(out, "x_7")

    class Broke:
        messages = None

        def __init__(self):
            self.messages = self

        def create(self, **kw):
            resp = httpx.Response(400, request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"))
            raise anthropic.BadRequestError("Your credit balance is too low to access the Anthropic API.", response=resp, body=None)

    monkeypatch.setattr(rv, "_client", lambda: Broke())
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    r = app.test_client().post("/imagine/review", json={"id": "x_7"})
    j = r.get_json()
    assert r.status_code == 502 and not j["ok"]
    assert "400" in j["error"] and "credit balance" in j["error"]
    assert "ANTHROPIC_API_KEY" not in j["error"] and "/Users/" not in j["error"]


def test_a_draft_from_a_renamed_model_is_still_reviewable(out):
    make(out, "x_8", model="gpt-image-3-newname")
    c = FakeClient(FIX)
    assert rv.review("x_8", client=c)["review"]["verdict"] == "fix" and len(c.calls) == 1


def test_route_carries_the_limit_note_for_the_pop_up(out, monkeypatch):
    from release_manager import claude_api, webapp
    make(out, "x_9")
    monkeypatch.setattr(rv, "_client", lambda: FakeClient(FIX))
    monkeypatch.setattr(claude_api, "LIMIT_USD", 0.01)
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    c = app.test_client()
    first = c.post("/imagine/review", json={"id": "x_9"}).get_json()       # crosses the limit: note on success
    assert first["ok"] and first["limit_note"].startswith("Monthly Claude API limit reached")
    second = c.post("/imagine/review", json={"id": "x_9"})
    j = second.get_json()
    assert second.status_code == 400 and not j["ok"] and j["limit_note"] and "limit" in j["error"]



class FakeOpenAI:
    """Stands in for openai.OpenAI: records the Responses API request, answers with JSON."""
    def __init__(self, reply, status="completed"):
        self.calls, self.reply, self.status = [], reply, status
        self.responses = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(status=self.status, output_text=json.dumps(self.reply),
                               usage=SimpleNamespace(input_tokens=3000, output_tokens=400))


PASS = {"verdict": "pass", "summary": "Fine.", "issues": [], "prompt_fix": "ignored"}


def test_openai_review_sends_same_input_and_saves_next_to_claude(out):
    make(out, "o_1")
    rv.review("o_1", client=FakeClient(FIX))
    o = FakeOpenAI(PASS)
    rec = rv.review_openai("o_1", client=o)
    kw = o.calls[0]
    assert kw["model"] == "gpt-6.1-sol" and kw["reasoning"] == {"effort": "medium"}
    assert kw["text"]["format"]["type"] == "json_schema" and kw["text"]["format"]["strict"] is True
    assert kw["instructions"] == rv.SYSTEM
    parts = kw["input"][0]["content"]
    assert parts[0]["type"] == "input_image" and parts[0]["image_url"].startswith("data:image/png;base64,")
    assert "SUBJECT: a lamp" in parts[1]["text"] and "CURRENT RULES" in parts[1]["text"]
    assert rec["review"]["verdict"] == "fix" and rec["review_openai"]["verdict"] == "pass"
    assert rec["review_openai"]["prompt_fix"] == "" and rec["review_openai"]["model"] == "gpt-6.1-sol"
    assert rec["review_openai"]["cost_usd"] == pytest.approx(3000 * 2e-6 + 400 * 10e-6)
    from release_manager import openai_api
    assert openai_api.month_spend()["calls"] == 1


def test_openai_review_refuses_composites_before_any_call(out):
    make(out, "o_2", kind="composite")
    o = FakeOpenAI(PASS)
    with pytest.raises(rv.ReviewError):
        rv.review_openai("o_2", client=o)
    assert o.calls == []


def test_openai_review_unfinished_reply_raises_and_saves_nothing(out):
    make(out, "o_3")
    with pytest.raises(rv.ReviewError):
        rv.review_openai("o_3", client=FakeOpenAI(PASS, status="incomplete"))
    assert "review_openai" not in json.loads((out / "o_3.json").read_text())


def test_route_who_openai(out, monkeypatch):
    from release_manager import openai_api, webapp
    make(out, "o_4")
    monkeypatch.setattr(openai_api, "client", lambda env_file=None: FakeOpenAI(FIX))
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    r = app.test_client().post("/imagine/review", json={"id": "o_4", "who": "openai"})
    j = r.get_json()
    assert r.status_code == 200 and j["ok"] and j["review"]["model"] == "gpt-6.1-sol"
