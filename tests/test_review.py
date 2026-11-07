"""Review flow (System 82, card M10): state transitions, hash binding, supersedes, the
check chips, the phone export and its ticks, and the /review page + API that refuses
used, delete and anything destructive. Uses a fixture release only, never a real file."""
import json
import subprocess
from pathlib import Path

import pytest

from release_manager import review, storage
from release_manager.models import new_release_dict, new_track_dict

SLUG = "review-test-single"


def fixture_release() -> dict:
    rel = new_release_dict("Review Test", "Single", "2026-12-18", genre_primary="Post-punk")
    rel["slug"] = SLUG
    rel["tracks"] = [new_track_dict(1, "Night Walk", bpm=118, duration="3:40")]
    rel["notes"] = "keep me"
    return rel


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    """One 9:16 clip with audio, one silent 2 s clip, one 4000 px cover (made once)."""
    d = tmp_path_factory.mktemp("review-media")
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    base = [ff, "-v", "error", "-y"]
    subprocess.run(base + ["-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=3",
                           "-f", "lavfi", "-i", "sine=frequency=220:duration=3",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(d / "reel.mp4")],
                   check=True, capture_output=True, timeout=120)
    subprocess.run(base + ["-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30:d=2",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(d / "canvas.mp4")],
                   check=True, capture_output=True, timeout=120)
    from PIL import Image
    Image.new("RGB", (4000, 4000), (15, 13, 12)).save(d / "cover.png")
    Image.new("RGB", (1080, 1080), (15, 13, 12)).save(d / "small.png")
    return d


def text_item(label="caption", text="Hi all, out today. Hope you will like it.", **kw):
    return review.new_item("caption", label, text=text, **kw)


def file_item(path, kind="render", dest=("reel_instagram",), **kw):
    return review.new_item(kind, Path(path).name, path=str(path), destination=list(dest), **kw)


# --- model and states ---------------------------------------------------------------------

def test_new_item_hashes_the_file_and_the_text(media):
    it = file_item(media / "cover.png", kind="cover", dest=["release_spotify"])
    assert it["sha256"] == review.sha256_of(media / "cover.png")
    assert it["bytes"] == (media / "cover.png").stat().st_size
    assert it["state"] == "draft" and it["history"][0]["state"] == "draft"
    t = text_item()
    assert len(t["sha256"]) == 64 and t["path"] == ""
    with pytest.raises(review.ReviewError):
        review.new_item("render", "no path")
    with pytest.raises(review.ReviewError):
        review.new_item("caption", "no text")
    with pytest.raises(review.ReviewError):
        review.new_item("poster", "unknown kind", path="x")


def test_ids_count_up_and_add_refuses_duplicates():
    rel = fixture_release()
    a = review.add_item(rel, text_item())
    b = review.add_item(rel, text_item("second"))
    assert (a["id"], b["id"]) == ("r-001", "r-002")
    with pytest.raises(review.ReviewError):
        review.add_item(rel, dict(text_item(), id="r-001"))


def test_transitions_follow_the_table():
    rel = fixture_release()
    it = review.add_item(rel, text_item())
    with pytest.raises(review.ReviewError):           # draft cannot be approved
        review.tick(rel, it["id"], "approve", sha256=it["sha256"])
    review.submit(rel, it["id"])
    assert it["state"] == "needs-you"
    review.tick(rel, it["id"], "change", note="shorter")
    assert it["state"] == "change" and it["note"] == "shorter"
    with pytest.raises(review.ReviewError):           # change -> approved is not a step
        review.tick(rel, it["id"], "approve", sha256=it["sha256"])
    review.submit(rel, it["id"])                      # the agent re-submits
    review.tick(rel, it["id"], "approve", sha256=it["sha256"])
    assert it["state"] == "approved" and it["approved"]["sha256"] == it["sha256"]
    review.mark_used(rel, it["id"], where="instagram", ref="https://instagram.com/p/x")
    assert it["state"] == "used" and it["used"]["where"] == "instagram"
    for action in ("approve", "change", "drop"):
        with pytest.raises(review.ReviewError):
            review.tick(rel, it["id"], action, note="x", sha256=it["sha256"])
    assert [h["state"] for h in it["history"]] == ["draft", "needs-you", "change", "needs-you", "approved", "used"]


def test_tick_refuses_unknown_actions_and_change_without_a_note():
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, text_item())["id"])
    for action in ("used", "delete", "move", "post", ""):
        with pytest.raises(review.ReviewError):
            review.tick(rel, it["id"], action)
    with pytest.raises(review.ReviewError):
        review.tick(rel, it["id"], "change", note="   ")
    assert it["state"] == "needs-you"


def test_mark_used_only_from_approved():
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, text_item())["id"])
    with pytest.raises(review.ReviewError):
        review.mark_used(rel, it["id"], where="instagram")


# --- hash binding -------------------------------------------------------------------------

def test_approve_needs_the_hash_the_reviewer_saw(media, tmp_path):
    f = tmp_path / "reel.mp4"
    f.write_bytes((media / "reel.mp4").read_bytes())
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(f))["id"])
    bound = it["sha256"]
    with pytest.raises(review.ReviewError, match="hash mismatch"):
        review.tick(rel, it["id"], "approve", sha256="")
    with pytest.raises(review.ReviewError, match="hash mismatch"):
        review.tick(rel, it["id"], "approve", sha256="0" * 64)
    assert it["state"] == "needs-you" and it["approved"] is None
    review.tick(rel, it["id"], "approve", sha256=bound.upper())
    assert it["approved"]["sha256"] == bound


def test_changed_file_after_approval_goes_back_to_needs_you(media, tmp_path):
    f = tmp_path / "reel.mp4"
    f.write_bytes((media / "reel.mp4").read_bytes())
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(f))["id"])
    bound = it["sha256"]
    review.tick(rel, it["id"], "approve", sha256=bound)
    assert review.refresh(rel) == []                  # nothing changed, nothing written
    f.write_bytes(f.read_bytes() + b"\x00")           # the file changes on disk
    assert review.refresh(rel) == [it["id"]]
    assert it["state"] == "needs-you"
    assert it["note"] == "file changed after approval"
    assert it["approved"] is None
    assert it["sha256"] == bound                      # the bound hash is never rewritten
    assert it["observed_sha256"] == review.sha256_of(f)
    chip = [c for c in it["checks"] if c["name"] == "hash"][0]
    assert chip["pass"] is False and "file changed after approval" in chip["reason"]
    assert it["history"][-1]["by"] == "code"
    with pytest.raises(review.ReviewError, match="file changed after approval"):
        review.tick(rel, it["id"], "approve", sha256=bound)
    assert review.refresh(rel) == []                  # already flagged, same observed hash


def test_approve_refuses_when_the_disk_changed_before_the_tick(media, tmp_path):
    f = tmp_path / "cover.png"
    f.write_bytes((media / "cover.png").read_bytes())
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(f, kind="cover", dest=["release_spotify"]))["id"])
    bound = it["sha256"]
    f.write_bytes(f.read_bytes() + b"\x00")
    with pytest.raises(review.ReviewError, match="file changed after approval"):
        review.tick(rel, it["id"], "approve", sha256=bound)
    assert it["state"] == "needs-you" and it["note"] == "file changed since review"
    assert it["sha256"] == bound and it["observed_sha256"] != bound


def test_run_checks_never_overwrites_the_bound_hash(media, tmp_path):
    f = tmp_path / "cover.png"
    f.write_bytes((media / "cover.png").read_bytes())
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(f, kind="cover", dest=["release_spotify"]))["id"])
    bound = it["sha256"]
    f.write_bytes(f.read_bytes() + b"\x00")
    review.run_checks(it)
    assert it["sha256"] == bound
    assert it["observed_sha256"] == review.sha256_of(f)
    assert review.gate(it) == "held"


def test_held_item_cannot_be_approved():
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, text_item(text="Out now — tonight"))["id"])
    assert review.gate(it) == "held"
    with pytest.raises(review.ReviewError, match="held: copy failing"):
        review.tick(rel, it["id"], "approve", sha256=it["sha256"])
    assert it["state"] == "needs-you" and it["approved"] is None
    review.tick(rel, it["id"], "drop")                # drop and change still work on a held item
    assert it["state"] == "dropped"


# --- supersedes -----------------------------------------------------------------------------

def test_new_version_supersedes_the_old_and_carries_no_approval():
    rel = fixture_release()
    v1 = review.submit(rel, review.add_item(rel, text_item("v1"))["id"])
    review.tick(rel, v1["id"], "approve", sha256=v1["sha256"])
    v2 = review.add_item(rel, text_item("v2", text="Hi all, a new cut.", supersedes=v1["id"]))
    assert v2["version"] == 2 and v2["state"] == "draft" and v2["approved"] is None
    assert v1["state"] == "superseded" and v1["superseded_by"] == v2["id"]
    assert v1["history"][-1]["note"] == "replaced by r-002"
    with pytest.raises(review.ReviewError):           # nothing supersedes a superseded item
        review.add_item(rel, text_item("v3", supersedes=v1["id"]))
    with pytest.raises(review.ReviewError):
        review.add_item(rel, text_item("v3", supersedes="r-999"))


def test_superseding_a_used_item_keeps_it_used():
    rel = fixture_release()
    v1 = review.submit(rel, review.add_item(rel, text_item("v1"))["id"])
    review.tick(rel, v1["id"], "approve", sha256=v1["sha256"])
    review.mark_used(rel, v1["id"], where="instagram")
    v2 = review.add_item(rel, text_item("v2", supersedes=v1["id"]))
    assert v1["state"] == "used" and v1["superseded_by"] == v2["id"] and v2["version"] == 2


# --- checks (chips) -----------------------------------------------------------------------

def chips(item):
    return {c["name"]: (c["pass"], c["reason"]) for c in item["checks"]}


def test_video_checks_format_duration_audio_and_safe_zone(media):
    rel = fixture_release()
    ok = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", dest=["reel_instagram", "shorts_youtube"],
                                                            text_boxes=[[200, 900, 600, 120]]))["id"])
    c = chips(ok)
    assert c["hash"][0] is True
    assert c["format"][0] is True and "1080x1920" in c["format"][1]
    assert c["duration"][0] is True
    assert c["audio"][0] is True
    assert c["safe-zone"][0] is True
    assert c["no-text-over-face"] == (None, "manual") and c["first-3s"] == (None, "manual")
    assert c["copy"][0] is None and c["handles"][0] is None
    assert review.gate(ok) == "passed"
    assert ok["probe"]["width"] == 1080 and ok["probe"]["has_audio"] is True

    low = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", text_boxes=[[200, 100, 600, 120]]))["id"])
    assert chips(low)["safe-zone"][0] is False and "top 270" in chips(low)["safe-zone"][1]
    assert review.gate(low) == "held"

    wrong = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", dest=["video_youtube"]))["id"])
    assert chips(wrong)["format"][0] is False and "1920x1080" in chips(wrong)["format"][1]

    unknown = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", dest=["nope"]))["id"])
    assert chips(unknown)["format"][0] is False and "unknown preset" in chips(unknown)["format"][1]

    none = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", dest=[]))["id"])
    assert chips(none)["format"][0] is None and chips(none)["safe-zone"] == (None, "manual: no type boxes recorded")


def test_canvas_must_be_silent_and_three_to_eight_seconds(media):
    rel = fixture_release()
    short = review.submit(rel, review.add_item(rel, file_item(media / "canvas.mp4", kind="canvas",
                                                               dest=["canvas_vertical_spotify"]))["id"])
    c = chips(short)
    assert c["duration"][0] is False and "min 3s" in c["duration"][1]
    assert c["audio"] == (True, "silent")
    loud = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4", kind="canvas",
                                                              dest=["canvas_vertical_spotify"]))["id"])
    assert chips(loud)["audio"][0] is False and "silent" in chips(loud)["audio"][1]
    assert chips(loud)["duration"][0] is True


def test_cover_checks_size_per_artwork_preset(media):
    rel = fixture_release()
    big = review.submit(rel, review.add_item(rel, file_item(media / "cover.png", kind="cover", dest=["release_spotify"]))["id"])
    c = chips(big)
    assert c["format"][0] is True and c["duration"] == (None, "image") and c["safe-zone"] == (None, "not 9:16")
    small = review.submit(rel, review.add_item(rel, file_item(media / "small.png", kind="cover", dest=["release_spotify"]))["id"])
    assert chips(small)["format"][0] is False and "4000x4000" in chips(small)["format"][1]


def test_missing_file_fails_the_hash_chip(tmp_path):
    rel = fixture_release()
    it = review.add_item(rel, review.new_item("render", "gone", path=str(tmp_path / "gone.mp4")))
    assert it["sha256"] == ""
    review.submit(rel, it["id"])
    assert chips(it)["hash"][0] is False and chips(it)["format"][0] is False
    with pytest.raises(review.ReviewError):
        review.tick(rel, it["id"], "approve", sha256="")


def test_copy_chip_em_dash_and_caption_check():
    rel = fixture_release()
    good = review.submit(rel, review.add_item(rel, text_item(text="Hi all, Night Walk is out today. Hope you will like it."))["id"])
    assert chips(good)["copy"][0] is True
    bad = review.submit(rel, review.add_item(rel, text_item(text="Out now — go listen"))["id"])
    assert chips(bad)["copy"][0] is False and "em-dash" in chips(bad)["copy"][1]
    assert chips(bad)["format"] == (None, "no file") and chips(bad)["no-text-over-face"] == (None, "no frame")


def test_handles_chip_never_passes_an_unknown_handle():
    rel = fixture_release()
    known = {"inch_of_shadow", "ambertone.studios"}
    own = review.add_item(rel, text_item(text="Mixed at @ambertone.studios, by @inch_of_shadow."))
    review.run_checks(own, known=known)
    assert chips(own)["handles"] == (True, "@ambertone.studios, @inch_of_shadow")
    stranger = review.add_item(rel, text_item(text="Shot by @someone_new and @ambertone.studios"))
    review.run_checks(stranger, known=known)
    assert chips(stranger)["handles"][0] is None
    assert chips(stranger)["handles"][1] == "? unverified: @someone_new"
    assert review.gate(stranger) == "passed"          # unverified is a question, not a fail
    none = review.add_item(rel, text_item(text="No handles here."))
    review.run_checks(none, known=known)
    assert chips(none)["handles"] == (None, "no handles")
    assert review.OWN_HANDLES <= review.known_handles()


def test_manual_chips_keep_amirs_word_across_reruns(media):
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(media / "reel.mp4"))["id"])
    review.set_manual_check(it, "no-text-over-face", True)
    review.set_manual_check(it, "first-3s", False, reason="sting at 0:01")
    review.run_checks(it)
    assert chips(it)["no-text-over-face"] == (True, "checked by amir")
    assert chips(it)["first-3s"] == (False, "sting at 0:01")
    assert review.gate(it) == "held"
    with pytest.raises(review.ReviewError):
        review.set_manual_check(it, "hash", True)


def test_item_view_tones_and_gate():
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, text_item(text="Hi all, out today @nobody_known. Hope you will like it."))["id"])
    review.run_checks(it, known=set(review.OWN_HANDLES))
    v = review.item_view(rel, it)
    tones = {c["name"]: c["tone"] for c in v["chips"]}
    assert tones["hash"] == "pass" and tones["handles"] == "ask" and tones["format"] == "na"
    assert v["gate"] == "passed" and v["open"] is True and v["sha256"] == it["sha256"]


# --- load / save, backup, view --------------------------------------------------------------

@pytest.fixture
def releases_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "RELEASES_DIR", tmp_path)
    rel = fixture_release()
    (tmp_path / (SLUG + ".json")).write_text(json.dumps(rel, indent=2))
    return tmp_path


def _stored(releases_dir):
    return json.loads((releases_dir / (SLUG + ".json")).read_text())


def test_save_keeps_the_rest_of_the_file_and_backs_it_up(releases_dir, media):
    before = _stored(releases_dir)
    rel = storage.load_release(SLUG)
    it = review.submit(rel, review.add_item(rel, file_item(media / "cover.png", kind="cover", dest=["release_spotify"]))["id"])
    review.save_release_review(rel)
    after = _stored(releases_dir)
    assert after["review"]["items"][it["id"]]["state"] == "needs-you"
    assert after["review"]["version"] == review.REVIEW_VERSION
    for key in before:
        if key not in ("review", "updated_at"):
            assert after[key] == before[key], key
    backups = list(releases_dir.glob(SLUG + ".bak.*_review.json"))
    assert len(backups) == 1 and "review" not in json.loads(backups[0].read_text())
    assert [p.name for p in storage.iter_release_paths()] == [SLUG + ".json"]
    assert [r["slug"] for r in review.load_all()] == [SLUG]


def test_build_view_groups_by_release_needs_you_first_held_on_top(media):
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("ok caption", at="2026-11-06T10:00:00"))["id"])
    b = review.submit(rel, review.add_item(rel, text_item("held caption", text="x — y", at="2026-11-06T11:00:00"))["id"])
    c = review.submit(rel, review.add_item(rel, text_item("approved one", at="2026-11-06T12:00:00"))["id"])
    review.tick(rel, c["id"], "approve", sha256=c["sha256"])
    d = review.submit(rel, review.add_item(rel, text_item("dropped one", at="2026-11-06T13:00:00"))["id"])
    review.tick(rel, d["id"], "drop")
    view = review.build_view([rel])
    g = view["groups"][0]
    assert g["slug"] == SLUG
    assert [v["id"] for v in g["open"]] == [b["id"], a["id"], c["id"]]
    assert [v["id"] for v in g["done"]] == [d["id"]]
    assert view["counts"] == {"needs-you": 2, "held": 1, "proposed": 0, "approved": 1, "change": 0, "done": 1}
    assert review.build_view([rel], area="release")["groups"] == []
    assert review.build_view([rel], release="other")["groups"] == []
    assert [v["id"] for v in review.build_view([rel], area="socials")["groups"][0]["open"]] == [b["id"], a["id"], c["id"]]


# --- phone export and ticks -----------------------------------------------------------------

def test_export_carries_hashes_and_open_items_only_and_no_secret(tmp_path):
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("open"))["id"])
    d = review.submit(rel, review.add_item(rel, text_item("dropped"))["id"])
    review.tick(rel, d["id"], "drop")
    out = tmp_path / "plans" / "review-export.json"
    data = review.export_phone(rel, out, root=tmp_path, thumbnails=False)
    on_disk = json.loads(out.read_text())
    assert on_disk == data
    assert [i["id"] for i in data["items"]] == [a["id"]]
    assert data["items"][0]["sha256"] == a["sha256"]
    assert "token" not in data and "export" not in rel["review"]
    assert "PROPOSAL" in data["note"]


def test_phone_tick_only_proposes_until_the_local_confirm():
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("a"))["id"])
    res = review.import_ticks(rel, [{"tick_id": "t1", "id": a["id"], "action": "approve", "sha256": a["sha256"], "at": "2026-11-06T20:00:00Z"}])
    assert res == [("t1", a["id"], True, "proposed approve, confirm locally")]
    assert a["state"] == "needs-you" and a["approved"] is None          # the state never moves
    assert a["proposed"]["action"] == "approve" and a["proposed"]["by"] == "phone" and a["proposed"]["tick_id"] == "t1"
    assert [h["state"] for h in a["history"]] == ["draft", "needs-you"]  # no history entry, nothing happened
    assert rel["review"]["consumed_ticks"] == ["t1"]
    # a proposal is still open and still waits for him
    view = review.build_view([rel])
    assert view["counts"]["proposed"] == 1 and view["counts"]["approved"] == 0 and view["counts"]["needs-you"] == 1
    assert view["groups"][0]["open"][0]["proposed"]["action"] == "approve"
    # the local confirm is the real step and records amir
    it = review.confirm(rel, a["id"])
    assert it["state"] == "approved" and it["approved"]["by"] == "amir" and it["proposed"] is None
    assert it["history"][-1]["by"] == "amir" and it["history"][-1]["via"] == "chat"


def test_local_tick_may_overrule_a_phone_proposal():
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("a"))["id"])
    review.import_ticks(rel, [{"tick_id": "t1", "id": a["id"], "action": "drop", "sha256": a["sha256"]}])
    assert a["state"] == "needs-you" and a["proposed"]["action"] == "drop"
    review.tick(rel, a["id"], "approve", sha256=a["sha256"])           # RM page keystroke
    assert a["state"] == "approved" and a["proposed"] is None
    b = review.submit(rel, review.add_item(rel, text_item("b"))["id"])
    review.import_ticks(rel, [{"tick_id": "t2", "id": b["id"], "action": "change", "sha256": b["sha256"], "note": "shorter"}])
    assert b["state"] == "needs-you" and b["proposed"]["action"] == "change"
    review.confirm(rel, b["id"])                                        # keeps the phone note
    assert b["state"] == "change" and b["note"] == "shorter"
    with pytest.raises(review.ReviewError):                             # tick() itself never takes a phone via
        review.tick(rel, a["id"], "drop", via="phone")


def test_phone_tick_refused_on_wrong_hash_missing_id_bad_action_or_closed_item():
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("a"))["id"])
    d = review.submit(rel, review.add_item(rel, text_item("d"))["id"])
    review.tick(rel, d["id"], "drop")
    res = review.import_ticks(rel, [
        {"tick_id": "t1", "id": a["id"], "action": "approve", "sha256": "0" * 64},      # wrong hash
        {"tick_id": "t2", "id": a["id"], "action": "approve"},                           # no hash
        {"id": a["id"], "action": "approve", "sha256": a["sha256"]},                     # no tick_id
        {"tick_id": "t3", "id": a["id"], "action": "used", "sha256": a["sha256"]},       # not an action
        {"tick_id": "t4", "id": "r-999", "action": "approve", "sha256": a["sha256"]},    # unknown item
        {"tick_id": "t5", "id": d["id"], "action": "approve", "sha256": d["sha256"]},    # dropped item
        {"tick_id": "t6", "id": a["id"], "action": "change", "sha256": a["sha256"]},     # change without a note
    ])
    assert [r[2] for r in res] == [False] * 7
    assert "does not match" in res[0][3] and "does not match" in res[1][3]
    assert "tick_id" in res[2][3] and "not approve" in res[3][3] and "unknown item" in res[4][3]
    assert "is dropped" in res[5][3] and "needs a note" in res[6][3]
    assert a["state"] == "needs-you" and a.get("proposed") is None
    assert rel["review"]["consumed_ticks"] == ["t1", "t2", "t3", "t4", "t5", "t6"]


def test_phone_tick_never_moves_an_approved_item_and_a_later_tick_replaces_the_proposal():
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("a"))["id"])
    review.tick(rel, a["id"], "approve", sha256=a["sha256"])
    res = review.import_ticks(rel, [{"tick_id": "t1", "id": a["id"], "action": "drop", "sha256": a["sha256"]}])
    assert res[0][2] is True
    assert a["state"] == "approved" and a["approved"]["by"] == "amir"      # untouched
    assert a["proposed"]["action"] == "drop" and a["proposed"]["tick_id"] == "t1"
    res = review.import_ticks(rel, [{"tick_id": "t2", "id": a["id"], "action": "change", "sha256": a["sha256"], "note": "later"}])
    assert res[0][2] is True
    assert a["state"] == "approved"
    assert a["proposed"]["action"] == "change" and a["proposed"]["tick_id"] == "t2" and a["proposed"]["note"] == "later"
    assert rel["review"]["consumed_ticks"] == ["t1", "t2"]
    assert "proposed-" not in str(review.STATES) and "proposed-" not in str(review.TRANSITIONS)
    review.confirm(rel, a["id"])                                            # his local word takes the last proposal
    assert a["state"] == "change" and a["note"] == "later" and a["history"][-1]["by"] == "amir"


def test_replayed_phone_tick_is_ignored():
    rel = fixture_release()
    a = review.submit(rel, review.add_item(rel, text_item("a"))["id"])
    t = {"tick_id": "t1", "id": a["id"], "action": "drop", "sha256": a["sha256"]}
    first = review.import_ticks(rel, [t])
    assert first[0][2] is True and a["state"] == "needs-you" and a["proposed"]["tick_id"] == "t1"
    review.tick(rel, a["id"], "approve", sha256=a["sha256"])            # he decided otherwise locally
    again = review.import_ticks(rel, [t, dict(t, tick_id="t1")])
    assert again == [("t1", a["id"], False, "ignored: already imported")] * 2
    assert a["state"] == "approved"
    assert rel["review"]["consumed_ticks"] == ["t1"]


def test_phone_tick_on_a_changed_file_is_refused_and_flags_the_item(media, tmp_path):
    f = tmp_path / "cover.png"
    f.write_bytes((media / "cover.png").read_bytes())
    rel = fixture_release()
    it = review.submit(rel, review.add_item(rel, file_item(f, kind="cover", dest=["release_spotify"]))["id"])
    f.write_bytes(f.read_bytes() + b"\x00")
    res = review.import_ticks(rel, [{"tick_id": "t1", "id": it["id"], "action": "approve", "sha256": it["sha256"]}])
    assert res[0][2] is False and "file changed" in res[0][3]
    assert it["state"] == "needs-you" and it["note"] == "file changed since review"
    # and a proposal already made falls with the file
    g = tmp_path / "cover2.png"
    g.write_bytes((media / "cover.png").read_bytes())
    it2 = review.submit(rel, review.add_item(rel, file_item(g, kind="cover", dest=["release_spotify"]))["id"])
    review.import_ticks(rel, [{"tick_id": "t2", "id": it2["id"], "action": "approve", "sha256": it2["sha256"]}])
    assert it2["state"] == "needs-you" and it2["proposed"]["action"] == "approve"
    g.write_bytes(g.read_bytes() + b"\x00")
    assert review.refresh(rel) == [it2["id"]]
    assert it2["state"] == "needs-you" and it2["proposed"] is None
    with pytest.raises(review.ReviewError):
        review.confirm(rel, it2["id"])                                  # nothing proposed any more


def test_thumbnail_for_cover_and_render(media):
    cover = file_item(media / "cover.png", kind="cover")
    assert review.thumbnail_data_uri(cover).startswith("data:image/jpeg;base64,")
    reel = file_item(media / "reel.mp4")
    assert review.thumbnail_jpeg(reel)[:3] == b"\xff\xd8\xff"
    assert review.thumbnail_jpeg(text_item()) == b""
    assert review.thumbnail_jpeg(review.new_item("render", "gone", path=str(media / "gone.mp4"))) == b""


# --- the page and the API -------------------------------------------------------------------

@pytest.fixture
def seeded(releases_dir, media):
    rel = storage.load_release(SLUG)
    ok = review.submit(rel, review.add_item(rel, file_item(media / "cover.png", kind="cover", dest=["release_spotify"]))["id"])
    held = review.submit(rel, review.add_item(rel, text_item("held", text="x — y"))["id"])
    cap = review.submit(rel, review.add_item(rel, text_item("caption", text="Hi all, out today. Hope you will like it."))["id"])
    review.save_release_review(rel)
    return {"ok": ok["id"], "held": held["id"], "cap": cap["id"], "sha": ok["sha256"], "cap_sha": cap["sha256"]}


@pytest.fixture
def client(releases_dir):
    from release_manager.webapp import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def test_review_page_renders_groups_chips_and_keys(client, seeded):
    html = client.get("/review").get_data(as_text=True)
    assert "Review Test" in html
    assert 'data-id="%s"' % seeded["ok"] in html
    assert 'data-sha="%s"' % seeded["sha"] in html
    assert "rv-chip pass" in html and "rv-chip fail" in html and "rv-chip manual" in html
    assert "em-dash in the text" in html
    assert ">held<" in html
    assert "<kbd>a</kbd>" in html and "<kbd>c</kbd>" in html and "<kbd>d</kbd>" in html
    assert "/api/review/" in html
    for word in ("delete", "rename", "move file", "Post now"):
        assert word not in html.replace("moves, deletes or posts", "")
    assert client.get("/review?release=other").status_code == 200
    assert "Nothing to review" in client.get("/review?release=other").get_data(as_text=True)


def test_review_page_without_review_blocks(client):
    html = client.get("/review").get_data(as_text=True)
    assert "Nothing to review" in html


def test_review_page_demo_renders_in_memory(client, releases_dir):
    html = client.get("/review?demo=1").get_data(as_text=True)
    assert "Review Demo" in html and "Demo release, in memory only" in html
    assert not list(releases_dir.glob("review-demo*"))
    assert client.get("/review/thumb/review-demo-single/r-002?demo=1").status_code == 200


def test_thumb_route_serves_recorded_files_only(client, seeded):
    r = client.get("/review/thumb/%s/%s" % (SLUG, seeded["ok"]))
    assert r.status_code == 200 and r.mimetype == "image/jpeg"
    assert client.get("/review/thumb/%s/%s" % (SLUG, seeded["cap"])).status_code == 404
    assert client.get("/review/thumb/%s/r-999" % SLUG).status_code == 404
    assert client.get("/review/thumb/no-such/r-001").status_code == 404


def test_api_approve_with_the_hash_writes_the_file(client, seeded, releases_dir):
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": "approve", "sha256": seeded["sha"]})
    assert r.status_code == 200 and r.get_json()["item"]["state"] == "approved"
    stored = _stored(releases_dir)["review"]["items"][seeded["ok"]]
    assert stored["state"] == "approved" and stored["approved"] == {
        "by": "amir", "at": stored["history"][-1]["at"], "sha256": seeded["sha"]}
    assert stored["history"][-1]["via"] == "rm"


def test_api_refuses_wrong_hash_held_and_used_or_delete(client, seeded, releases_dir):
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": "approve", "sha256": "0" * 64})
    assert r.status_code == 409 and "hash mismatch" in r.get_json()["error"]
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": "approve"})
    assert r.status_code == 409
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["held"]), json={"action": "approve", "sha256": "x"})
    assert r.status_code == 409 and r.get_json()["error"].startswith("held")
    for action in ("used", "delete", "move", "post", "rename"):
        r = client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": action, "sha256": seeded["sha"]})
        assert r.status_code == 400, action
    assert client.post("/api/review/%s/r-999" % SLUG, json={"action": "drop"}).status_code == 404
    assert client.post("/api/review/no-such/r-001", json={"action": "drop"}).status_code == 404
    stored = _stored(releases_dir)["review"]["items"]
    assert len(stored) == 3 and stored[seeded["ok"]]["state"] == "needs-you"


def test_api_change_writes_the_note_and_drop_keeps_the_file(client, seeded, releases_dir, media):
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["cap"]), json={"action": "change"})
    assert r.status_code == 409 and "note" in r.get_json()["error"]
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["cap"]), json={"action": "change", "note": "shorter opener"})
    assert r.status_code == 200
    stored = _stored(releases_dir)["review"]["items"][seeded["cap"]]
    assert stored["state"] == "change" and stored["note"] == "shorter opener"
    assert stored["ticks"] == {"by": "amir", "at": stored["history"][-1]["at"], "via": "rm", "note": "shorter opener"}
    r = client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": "drop", "note": "not this one"})
    assert r.status_code == 200
    stored = _stored(releases_dir)["review"]["items"]
    assert stored[seeded["ok"]]["state"] == "dropped" and len(stored) == 3
    assert (media / "cover.png").is_file()            # nothing deleted, nothing moved
    assert client.post("/api/review/%s/%s" % (SLUG, seeded["ok"]), json={"action": "approve", "sha256": seeded["sha"]}).status_code == 409


def test_page_get_demotes_an_approved_item_whose_file_changed(client, releases_dir, tmp_path, media):
    f = tmp_path / "cover.png"
    f.write_bytes((media / "cover.png").read_bytes())
    rel = storage.load_release(SLUG)
    it = review.submit(rel, review.add_item(rel, file_item(f, kind="cover", dest=["release_spotify"]))["id"])
    review.tick(rel, it["id"], "approve", sha256=it["sha256"])
    review.save_release_review(rel)
    f.write_bytes(f.read_bytes() + b"\x00")
    html = client.get("/review").get_data(as_text=True)
    assert "file changed after approval" in html
    stored = _stored(releases_dir)["review"]["items"][it["id"]]
    assert stored["state"] == "needs-you" and stored["approved"] is None and stored["sha256"] == it["sha256"]


def test_demo_cli_writes_a_temp_release_only(releases_dir, capsys):
    assert review._cli(["--demo"]) == 0
    out = capsys.readouterr().out
    assert "demo release written to" in out
    assert not list(releases_dir.glob("*.json"))[1:]   # only the fixture file lives in releases/
    path = Path(out.split("written to ")[1].split(" (media")[0])
    data = json.loads(path.read_text())
    assert data["slug"] == review.DEMO_SLUG and len(data["review"]["items"]) == 6


def test_relative_paths_resolve_without_a_git_call(monkeypatch):
    """A page render resolves item paths against the repo root found at import, never per item."""
    def no_shell(*a, **k):
        raise AssertionError("resolve_path shelled out")
    monkeypatch.setattr(subprocess, "run", no_shell)
    assert review.resolve_path("artwork/x.png") == storage.BASE_DIR / "artwork" / "x.png"
    assert review.resolve_path("/tmp/x.png") == Path("/tmp/x.png")
