"""Machine-25: Try the fix. One more draft from a review's prompt fix, three closeness stops."""

import json

import pytest
from PIL import Image

from release_manager import imagine as im
from tests.test_imagine import FakeClient


@pytest.fixture
def out(tmp_path, monkeypatch):
    monkeypatch.setattr(im, "OUT", tmp_path)
    return tmp_path


PROMPT = ("USE: Square album cover artwork.\n\nSUBJECT: A pale rose on wet stone.\n\nDETAILS:\n- soft light\n\n"
          "COMPOSITION: One focal point.\n\nREFERENCES:\n- Image 1: style reference. Take only its style.\n\n"
          "BRAND:\ncore text\n\nCONSTRAINTS:\n- No text.")


def make(out, image_id, **extra):
    Image.new("RGB", (64, 64), (30, 20, 10)).save(out / f"{image_id}.png")
    rec = {"id": image_id, "file": f"{image_id}.png", "made": "2026-10-20T10:00:00", "model": "gpt-image-2.5-flare",
           "quality": "low", "size": "1024x1024", "kind": "cover", "prompt": PROMPT, "release": "test-song",
           "subject": "A pale rose on wet stone.", "choice": {"light": "l1"}, "title_area": "top", "decision": None, **extra}
    (out / f"{image_id}.json").write_text(json.dumps(rec))
    return rec


def test_keep_sends_the_draft_and_changes_only_the_fix(out):
    make(out, "d_1")
    nxt = im.next_round("d_1", "no lettering in the corners", "keep")
    assert nxt["refs"][0]["role"] == "redraw" and nxt["refs"][0]["send"] and nxt["refs"][0]["path"].endswith("d_1.png")
    p = nxt["prompt"]
    assert "Image 1: our own earlier draft" in p and "style reference" not in p        # the old references are baked in
    assert p.endswith("THIS ROUND: Redraw Image 1 with exactly one change: no lettering in the corners. Keep everything else "
                      "as it is in Image 1: the same subject, layout, light, palette and texture.")
    assert p.startswith("USE: Square album cover artwork.\n\nSUBJECT: A pale rose on wet stone.")
    assert nxt["meta"] == {"release": "test-song", "kind": "cover", "subject": "A pale rose on wet stone.",
                           "choice": {"light": "l1"}, "title_area": "top", "step": 2, "parent": "d_1",
                           "closeness": "keep", "fix": "no lettering in the corners."}


def test_mostly_keeps_subject_and_layout_only(out):
    make(out, "d_2")
    p = im.next_round("d_2", "Warmer light.", "mostly")["prompt"]
    assert "Image 1: our own earlier draft" in p
    assert "THIS ROUND: Redraw Image 1 and apply this change: Warmer light. Keep its subject and layout; you may change" in p


def test_free_sends_no_image_and_no_references(out):
    make(out, "d_3", step=2)
    nxt = im.next_round("d_3", "Warmer light", "free")
    assert nxt["refs"] == [] and "REFERENCES" not in nxt["prompt"] and "Image 1" not in nxt["prompt"]
    assert nxt["prompt"].endswith("THIS ROUND: Apply this change to the image described above: Warmer light. "
                                  "Everything else follows the sections above.")
    assert nxt["meta"]["step"] == 3


@pytest.mark.parametrize("bad", [("nope", "fix", "keep"), ("d_4", "", "keep"), ("d_4", "fix", "halfway")])
def test_bad_inputs_raise(out, bad):
    make(out, "d_4")
    with pytest.raises(ValueError):
        im.next_round(*bad)


def test_composites_are_never_redrawn(out):
    make(out, "c_1", kind="composite", plate="d_1")
    with pytest.raises(ValueError):
        im.next_round("c_1", "fix", "free")


def test_round_record_keeps_the_chain(out):
    make(out, "d_5")
    nxt = im.next_round("d_5", "Darker sky.", "keep")
    fake = FakeClient()
    recs = im.generate(nxt["prompt"], "gpt-image-2.5-flare", "low", nxt["size"], 1, nxt["refs"], nxt["meta"], client=fake)
    assert fake.calls[0][0] == "edit"                                   # the parent draft was sent
    r = json.loads((out / f"{recs[0]['id']}.json").read_text())
    assert r["step"] == 2 and r["parent"] == "d_5" and r["closeness"] == "keep" and r["fix"] == "Darker sky."
    assert r["references"] == [{"file": "d_5.png", "scope": "round", "role": "redraw", "sent": True}]


def test_route_estimates_free_then_renders_on_confirm(out, monkeypatch):
    from release_manager import webapp
    make(out, "d_6")
    fake = FakeClient()
    monkeypatch.setattr(im, "_client", lambda: fake)
    app = webapp.app
    app.config["WTF_CSRF_ENABLED"] = False
    c = app.test_client()
    j = c.post("/imagine/round", json={"id": "d_6", "fix": "Darker sky", "closeness": "mostly"}).get_json()
    assert j["ok"] and "THIS ROUND" in j["prompt"] and j["model"] == "gpt-image-2.5-flare" and j["quality"] == "low"
    assert j["sent_refs"] == 1 and j["estimate"]["total"] > 0 and fake.calls == []
    j = c.post("/imagine/round", json={"id": "d_6", "fix": "Darker sky", "closeness": "mostly", "confirmed": True}).get_json()
    assert j["ok"] and j["images"][0]["step"] == 2 and j["images"][0]["parent"] == "d_6" and len(fake.calls) == 1
    r = c.post("/imagine/round", json={"id": "d_6", "fix": "", "closeness": "keep"})
    assert r.status_code == 400


def test_old_single_newline_prompts_keep_their_sections_whole(out):
    old = ("USE: test.\nSCENE: A ledge.\nSUBJECT: A rose.\nBRAND: core line one.\n\nCore line two.\n"
           "CONSTRAINTS: No text.")
    make(out, "d_7", prompt=old)
    p = im.next_round("d_7", 'Replace the SCENE line with: "SCENE: fog only."', "keep")["prompt"]
    secs = p.split("\n\n")
    assert secs[3].startswith("REFERENCES:") and secs[4] == "BRAND: core line one.\n\nCore line two." or \
        "BRAND: core line one.\n\nCore line two." in p
    assert p.index("REFERENCES:") < p.index("BRAND:") < p.index("CONSTRAINTS:") < p.index("THIS ROUND:")
    assert 'fog only.".' not in p                       # no double full stop after a quoted fix
