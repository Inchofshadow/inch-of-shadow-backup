"""Imagine (Machine-17): the prompt is built in fixed sections from the four layers, words-only
references never leave the Mac, every render is logged with its real cost. No real API calls."""
import base64
import io
import json
from types import SimpleNamespace

import pytest
from PIL import Image

from release_manager import imagine as im

MOODS = {"M2": {"name": "platinum + warm black", "light": "#D6D1C8", "dark": "#0F0D0C"}}


def png_b64():
    b = io.BytesIO(); Image.new("RGB", (8, 8), (20, 20, 20)).save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


class FakeClient:
    def __init__(self):
        self.calls = []
        self.images = SimpleNamespace(generate=self._gen, edit=self._edit)

    def _resp(self, n):
        return SimpleNamespace(data=[SimpleNamespace(b64_json=png_b64()) for _ in range(n)],
                               usage={"input_tokens": 400, "output_tokens": 392,
                                      "input_tokens_details": {"text_tokens": 300, "image_tokens": 100}})

    def _gen(self, **kw):
        self.calls.append(("generate", kw)); return self._resp(kw["n"])

    def _edit(self, **kw):
        self.calls.append(("edit", kw)); return self._resp(kw["n"])


def test_prompt_sections_in_order_with_core_verbatim_and_never_list():
    rel = {"image_brief": {"mood": "M2", "motifs": ["moon"], "concept": "a wooden boy who wants to be real", "never": "No puppets strings."}}
    p = im.build_prompt("cover", "A small wooden figure on a windowsill.", {"light": "l2-window-light"}, rel, MOODS, "top")
    order = [p.index(s) for s in ("USE:", "SUBJECT:", "DETAILS:", "COMPOSITION:", "BRAND:", "CONSTRAINTS:")]
    assert order == sorted(order)
    assert im.core() in p and "#D6D1C8" in p and "No puppets strings." in p
    assert "religious architecture" in p and "Keep the top 30% quiet" in p


def test_words_only_references_are_described_not_sent(tmp_path, monkeypatch):
    monkeypatch.setattr(im, "REFS", tmp_path / "refs"); monkeypatch.setattr(im, "OUT", tmp_path / "out")
    b = io.BytesIO(); Image.new("RGB", (8, 8)).save(b, "PNG")
    mine = im.add_ref("brand", "anchor.png", b.getvalue(), "palette", "our Farewell cover", True, "mine")
    other = im.add_ref("brand", "someone.png", b.getvalue(), "light", "hard side light, deep shadow", True, "other")
    assert mine["send"] and not other["send"]                         # other artists' work never goes as an image
    items = im.refs("brand")
    p = im.build_prompt("cover", "A rose.", {}, None, MOODS, "none", ref_items=items)
    assert "Image 1: palette reference" in p and "Described reference (light): hard side light" in p
    fake = FakeClient()
    recs = im.generate(p, "gpt-image-2.5-flare", "low", "1024x1024", 2, items, {"release": "test", "choice": {}}, client=fake)
    kind, kw = fake.calls[0]
    assert kind == "edit" and len(kw["image"]) == 1                    # only the approved one was sent
    assert len(recs) == 2 and (tmp_path / "out" / recs[0]["file"]).is_file()
    assert recs[0]["cost_usd"] == pytest.approx((392 * 30 + 100 * 8 + 300 * 5) / 1e6 / 2)


def test_decisions_spend_estimate_and_option_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(im, "OUT", tmp_path / "out")
    fake = FakeClient()
    recs = im.generate("x", "gpt-image-2.5-flare", "low", "1024x1024", 1, [], {"release": "r", "choice": {"light": "l2-window-light"}}, client=fake)
    assert fake.calls[0][0] == "generate"
    im.set_decision(recs[0]["id"], "keep")
    assert im.option_stats()[0] == {"kind": "light", "name": "l2-window-light", "kept": 1, "rejected": 0}
    assert im.month_spend()["images"] == 1
    assert im.estimate("gpt-image-2.5-flare", "low", "1024x1024", 3)["basis"].startswith("average of 1")
    assert im.estimate("gpt-image-2.5-sunburst", "high", "2048x2048", 1)["each"] == pytest.approx(0.211 * 4)
    with pytest.raises(ValueError):
        im.set_decision("../x", "keep")


def test_bad_inputs_are_refused():
    with pytest.raises(ValueError):
        im.build_prompt("cover", "  ", {}, None, MOODS)
    with pytest.raises(ValueError):
        im.build_prompt("cover", "x", {"light": "../../etc"}, None, MOODS)
    with pytest.raises(ValueError):
        im.generate("x", "dall-e-3", "low", "1024x1024", 1, [], {}, client=FakeClient())


def test_composite_is_local_and_keeps_only_the_photo_name(tmp_path, monkeypatch):
    import json
    from PIL import Image
    monkeypatch.setattr(im, "OUT", tmp_path)
    Image.new("RGB", (400, 400), (20, 20, 20)).save(tmp_path / "rel_1.png")
    (tmp_path / "rel_1.json").write_text(json.dumps({"id": "rel_1", "file": "rel_1.png", "kind": "background",
                                                     "release": "rel", "prompt": "USE: plate", "cost_usd": 0.01}))
    photo = tmp_path / "out-152.jpg"
    Image.new("RGB", (200, 300), (200, 180, 160)).save(photo)

    def fake_cut(img):                                   # a centred opaque block stands in for him
        a = Image.new("L", img.size, 0)
        a.paste(255, (50, 50, 150, 250))
        img.putalpha(a)
        return img
    rec = im.composite("rel_1", photo, 0.5, "left", cutout=fake_cut)
    assert rec["model"] == "local composite" and rec["cost_usd"] == 0 and rec["photo"] == "out-152.jpg"
    out = Image.open(tmp_path / rec["file"])
    assert out.size == (400, 400)
    r, g, b = out.getpixel((60, 390))                   # his block stands on the bottom edge, left side
    assert r > 120 and out.getpixel((380, 20))[0] < 60
    assert im.record(rec["id"])["plate"] == "rel_1"
    import pytest
    with pytest.raises(ValueError):
        im.composite("nope", photo, cutout=fake_cut)
    with pytest.raises(ValueError):
        im.composite("rel_1", photo, position="top", cutout=fake_cut)


def test_test_runs_group_by_run_newest_first(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(im, "OUT", tmp_path)
    for i, (run, key) in enumerate([("20260901-1", "b"), ("20260901-1", "a"), ("20260930-1", "a")]):
        (tmp_path / f"t{i}.json").write_text(json.dumps({"id": f"t{i}", "file": f"t{i}.png", "made": "2026-09-30T10:00:00",
                                                         "model": "m", "quality": "low", "test_run": run, "test_key": key}))
        (tmp_path / f"t{i}.png").write_bytes(b"x")
    runs = im.test_runs()
    assert [r["run"] for r in runs] == ["20260930-1", "20260901-1"]
    assert [x["test_key"] for x in runs[1]["images"]] == ["a", "b"]
    assert len(im.test_set()) == 5


def test_element_kind_sends_only_the_drawing_block():
    p = im.build_prompt("element", "One black swan in ink.", {}, None, MOODS, title_area="none")
    assert "USE: One illustrated element" in p and "BRAND:\n" + im.core("element") in p
    assert "film grain" not in p and "No crowds." not in p and "thumbnail" not in p
    assert "- No text, letters, numbers, logos or watermarks." in p
    assert im.core("free") != im.core("element")


def test_redraw_role_keeps_our_own_draft():
    item = {"send": True, "role": "redraw", "note": "the swan", "file": "x.png", "scope": "s", "path": "x.png"}
    p = im.build_prompt("element", "A swan.", {}, None, MOODS, title_area="none", ref_items=[item])
    assert "Image 1: our own earlier draft: the swan. Redraw it at full quality: keep its subject, shapes and layout." in p


def test_illustration_kind_uses_the_drawing_block_for_a_whole_cover():
    p = im.build_prompt("illustration", "A cover in ink.", {}, None, MOODS, title_area="bottom")
    assert p.startswith("USE: Square album cover artwork, drawn by hand on paper.")
    assert im.core("element") in p and "film grain" not in p and "thumbnail" in p
