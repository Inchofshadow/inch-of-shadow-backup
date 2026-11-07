"""The Imagine page: free prompt preview, Generate refused without confirmation, decisions and the
release brief saved, generated images openable in the photo editor. No real API calls."""
import release_manager.views.imagine as w   # the Imagine routes read their globals here (RM 2.0 slice 6)
from release_manager import imagine as im
from release_manager.webapp import app


def client_no_csrf():
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def test_page_renders_and_prompt_preview_is_free(monkeypatch):
    called = []
    monkeypatch.setattr(im, "generate", lambda *a, **k: called.append(1) or [])
    c = client_no_csrf()
    try:
        assert c.get("/imagine").status_code == 200
        j = c.post("/imagine/prompt", json={"kind": "cover", "subject": "A rose on stone.", "choice": {"light": "l2-window-light"}}).get_json()
        assert j["ok"] and j["prompt"].startswith("USE:") and j["model"] == "gpt-image-2.5-flare" and "estimate" in j
        assert c.post("/imagine/generate", json={"kind": "cover", "subject": "x"}).status_code == 400   # no confirmation
        assert not called
    finally:
        app.config["WTF_CSRF_ENABLED"] = True


def test_generate_after_confirmation_and_anchor_sets_the_brief(tmp_path, monkeypatch):
    monkeypatch.setattr(im, "OUT", tmp_path)
    from PIL import Image
    Image.new("RGB", (16, 16)).save(tmp_path / "rel_1.png")
    rec = {"id": "rel_1", "file": "rel_1.png", "made": "2026-09-27T16:00:00", "model": "gpt-image-2.5-flare", "quality": "low",
           "size": "1024x1024", "prompt": "USE: x", "cost_usd": 0.007, "release": "rel", "decision": None}
    monkeypatch.setattr(im, "generate", lambda *a, **k: [rec])
    import json; (tmp_path / "rel_1.json").write_text(json.dumps(rec))
    saved = {}
    monkeypatch.setattr(w, "load_release", lambda slug: {"slug": "rel", "metadata": {"title": "Rel"}} if slug == "rel" else None)
    monkeypatch.setattr(w, "save_release", lambda r: saved.update(r))
    c = client_no_csrf()
    try:
        j = c.post("/imagine/generate", json={"release": "rel", "kind": "cover", "subject": "A rose.", "confirmed": True}).get_json()
        assert j["ok"] and j["images"][0]["url"].endswith("/imagine/img/rel_1.png")
        assert c.post("/imagine/decision", json={"id": "rel_1", "decision": "anchor"}).get_json()["decision"] == "anchor"
        assert saved["image_brief"]["anchor"] == "rel_1.png"
        assert c.get("/edit", query_string={"src": "imagine:rel_1.png"}).status_code == 200
        assert c.get("/imagine/img/../x").status_code == 404
    finally:
        app.config["WTF_CSRF_ENABLED"] = True


def test_test_set_needs_confirmation_then_runs_every_prompt_once(monkeypatch):
    calls = []
    monkeypatch.setattr(im, "generate", lambda prompt, model, quality, size, n, refs, meta: calls.append((model, quality, n, meta)) or [])
    c = client_no_csrf()
    try:
        assert c.post("/imagine/test-set", json={}).status_code == 400 and not calls
        j = c.post("/imagine/test-set", json={"confirmed": True, "preset": "draft"}).get_json()
        assert j["ok"] and len(calls) == len(im.test_set()) == 5
        assert all(m == "gpt-image-2.5-flare" and q == "low" and n == 1 and meta["test_run"] == j["run"] for m, q, n, meta in calls)
        assert sorted(meta["test_key"] for *_, meta in calls) == sorted(t["key"] for t in im.test_set())
    finally:
        app.config["WTF_CSRF_ENABLED"] = True


def test_composite_route_uses_her_edit_and_never_calls_openai(tmp_path, monkeypatch):
    got = {}
    monkeypatch.setattr(im, "generate", lambda *a, **k: (_ for _ in ()).throw(AssertionError("paid call")))
    monkeypatch.setattr(w, "_shoot_photos", lambda: ({}, [{"id": "out-152", "edit": "Edits/out-152.jpg"}]))

    class SC:
        DRIVE = tmp_path / "drive"
    monkeypatch.setattr(w, "_shoot_tools", lambda: (SC, None))
    monkeypatch.setattr(w, "SHOOT_EDIT_PREVIEWS", tmp_path / "prev")
    (tmp_path / "prev").mkdir()
    (tmp_path / "prev" / "out-152.jpg").write_bytes(b"x")
    rec = {"id": "rel_2_composite", "file": "rel_2_composite.png", "model": "local composite", "prompt": "", "kind": "composite", "photo": "out-152.jpg"}
    monkeypatch.setattr(im, "composite", lambda pid, photo, scale, pos: got.update(pid=pid, photo=photo, scale=scale, pos=pos) or rec)
    c = client_no_csrf()
    try:
        assert c.post("/imagine/composite", json={"id": "rel_1", "photo": "out-999"}).status_code == 404
        j = c.post("/imagine/composite", json={"id": "rel_1", "photo": "out-152", "scale": "0.6", "position": "right"}).get_json()
        assert j["ok"] and got["photo"] == tmp_path / "prev" / "out-152.jpg" and got["scale"] == 0.6 and got["pos"] == "right"
        assert "drive" not in j["image"]["photo"]
    finally:
        app.config["WTF_CSRF_ENABLED"] = True
