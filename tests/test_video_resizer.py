"""video_resizer.py: preset table, passthrough, no-upscale, frame-rate warning, 4K output.

Sources are tiny synthetic clips made with the bundled ffmpeg; no network, no real media.
Spec basis: platform pages checked 2026-09-20 (board ticket Machine-07).
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import video_resizer as vr  # noqa: E402


def make_clip(path: Path, w: int, h: int, fps: int = 30, dur: float = 1.0,
              audio: bool = True, tags: bool = False) -> Path:
    cmd = [vr.FFMPEG_BIN, "-v", "error", "-y",
           "-f", "lavfi", "-i", f"testsrc2=size={w}x{h}:rate={fps}:duration={dur}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={dur}"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "128k"]
    if tags:
        cmd += ["-metadata", "title=SECRET", "-metadata", "comment=camera junk",
                "-metadata", "location=+52.4800+013.4300/"]
    cmd += [str(path)]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


def spec(name):
    return next(e for e in vr.VIDEO_EXPORTS if e[0] == name)


def run(src, out, names, **kw):
    exports = [spec(n) for n in names]
    return vr.process_video(src, out, exports, "center", None, None, **kw)


# --- preset table ---------------------------------------------------------

def test_no_square_spotify_canvas():
    # Spotify Canvas is vertical 9:16 only
    names = [e[0] for e in vr.VIDEO_EXPORTS]
    assert "canvas_square_spotify" not in names
    assert "canvas_vertical_spotify" in names


def test_story_cap_is_60_seconds():
    assert spec("story_instagram")[5] == 60


def test_feed_video_caps_are_not_60_seconds():
    assert spec("post_square_instagram")[5] == 180
    assert spec("post_portrait_instagram")[5] == 180


def test_youtube_has_1440_and_4k():
    assert spec("video_youtube_1440")[1:3] == (2560, 1440)
    assert spec("video_youtube_4k")[1:3] == (3840, 2160)
    assert {"video_youtube_1440", "video_youtube_4k"} <= vr.NO_UPSCALE


def test_all_dimensions_even():
    for e in vr.VIDEO_EXPORTS:
        assert e[1] % 2 == 0 and e[2] % 2 == 0, e[0]


def test_h264_level_fits_resolution():
    assert vr.h264_level(1080, 1920, 30) == "4.2"
    assert vr.h264_level(2560, 1440, 30) == "5.0"
    assert vr.h264_level(3840, 2160, 30) == "5.1"
    assert vr.h264_level(3840, 2160, 60) == "5.2"


# --- passthrough ----------------------------------------------------------

def test_matching_source_is_passed_through_without_reencode(tmp_path):
    src = make_clip(tmp_path / "master.mp4", 1080, 1920, fps=30, tags=True)
    results = run(src, tmp_path / "out", ["reel_instagram"])
    (filename, w, h, size_kb, dur, category, warnings) = results[0]
    assert any("passthrough" in x for x in warnings)
    out = tmp_path / "out" / filename
    info = vr.probe_video(out)
    assert (info["width"], info["height"]) == (1080, 1920)
    assert info["codec"] == "h264"
    # the video stream is bit-identical to the source
    def vhash(p):
        r = subprocess.run([vr.FFMPEG_BIN, "-v", "error", "-i", str(p), "-map", "0:v:0",
                            "-c", "copy", "-f", "md5", "-"], capture_output=True, text=True)
        return r.stdout.strip()
    assert vhash(src) == vhash(out)


def test_passthrough_still_strips_source_metadata(tmp_path):
    src = make_clip(tmp_path / "master.mp4", 1080, 1920, tags=True)
    results = run(src, tmp_path / "out", ["reel_instagram"])
    out = tmp_path / "out" / results[0][0]
    r = subprocess.run([vr.FFMPEG_BIN, "-i", str(out)], capture_output=True, text=True)
    assert "SECRET" not in r.stderr
    assert "camera junk" not in r.stderr
    assert "52.48" not in r.stderr


def test_no_passthrough_when_trimmed_or_too_long(tmp_path):
    src = make_clip(tmp_path / "master.mp4", 1080, 1920, dur=2.0)
    info = vr.probe_video(src)
    assert vr.can_passthrough(info, 1080, 1920, 30, None, None, 180) is True
    assert vr.can_passthrough(info, 1080, 1920, 30, 0.5, None, 180) is False   # trim asked
    assert vr.can_passthrough(info, 1080, 1920, 30, None, None, 1) is False    # longer than cap
    assert vr.can_passthrough(info, 1080, 1350, 30, None, None, 180) is False  # other size


def test_canvas_passthrough_drops_audio(tmp_path):
    src = make_clip(tmp_path / "loop.mp4", 1080, 1920, dur=4.0, audio=True)
    results = run(src, tmp_path / "out", ["canvas_vertical_spotify"])
    out = tmp_path / "out" / results[0][0]
    assert vr.probe_video(out)["has_audio"] is False


# --- no upscaling ---------------------------------------------------------

def test_4k_preset_skipped_for_1080_source(tmp_path):
    src = make_clip(tmp_path / "hd.mp4", 1920, 1080)
    results = run(src, tmp_path / "out", ["video_youtube", "video_youtube_1440", "video_youtube_4k"])
    names = [r[0] for r in results]
    assert any(n.startswith("video_youtube_hd") for n in names)
    assert not any("4k" in n or "1440" in n for n in names)


def test_4k_source_keeps_4k_for_youtube(tmp_path):
    src = make_clip(tmp_path / "uhd.mp4", 3840, 2160, dur=0.5)
    results = run(src, tmp_path / "out", ["video_youtube_4k"])
    out = tmp_path / "out" / results[0][0]
    info = vr.probe_video(out)
    assert (info["width"], info["height"]) == (3840, 2160)


# --- frame rate -----------------------------------------------------------

def test_fps_conversion_is_reported(tmp_path):
    src = make_clip(tmp_path / "cam25.mp4", 1920, 1080, fps=25)
    results = run(src, tmp_path / "out", ["reel_instagram"])
    warnings = results[0][6]
    assert any("25" in x and "30" in x for x in warnings)


# --- HyperFrames hand-off -------------------------------------------------

def test_latest_render_picks_newest_mp4(tmp_path):
    import os
    renders = tmp_path / "proj" / "renders"
    renders.mkdir(parents=True)
    old = renders / "a.mp4"; old.write_bytes(b"x")
    new = renders / "b.mp4"; new.write_bytes(b"x")
    os.utime(old, (1, 1))
    assert vr.latest_render(tmp_path / "proj") == new
    with pytest.raises(FileNotFoundError):
        vr.latest_render(tmp_path / "empty")


def test_a_picked_frame_sets_the_crop_and_zooms_inside_the_shape():
    from video_resizer import compute_crop_box, picked_frame, shape_of
    assert shape_of(1080, 1920) == "9:16" and shape_of(1080, 1350) == "4:5" and shape_of(3840, 2160) == "16:9"
    # 1920x1080 source into 9:16: the full box is 607x1080; centred on the right third
    box, w, h = compute_crop_box(1920, 1080, 1080, 1920, {"cx": 0.8, "cy": 0.5, "z": 1})
    assert (w, h) == (607, 1080) and box[0] == round(0.8 * 1920 - 607 / 2) and box[1] == 0
    # pushed past the edge: clamped inside the picture
    box, w, h = compute_crop_box(1920, 1080, 1080, 1920, {"cx": 1.0, "cy": 0.0, "z": 1})
    assert box[2] == 1920 and box[1] == 0
    # zoom 0.5: half the box, still the same shape, placed where asked
    box, w, h = compute_crop_box(1920, 1080, 1080, 1920, {"cx": 0.5, "cy": 0.25, "z": 0.5})
    assert (w, h) == (303, 540) and box[1] == round(0.25 * 1080 - 270)
    # bad input is checked, not trusted
    assert picked_frame({"cx": "x"}) is None and picked_frame("9:16") is None
    assert picked_frame({"cx": 3, "cy": -1, "z": 0.01}) == {"cx": 1.0, "cy": 0.0, "z": 0.25}


def test_frames_go_to_their_shape_only_and_a_zoom_stops_passthrough(tmp_path, monkeypatch):
    import video_resizer as vr
    src = {"width": 1080, "height": 1920, "duration": 10.0, "fps": 30.0, "has_audio": False,
           "codec": "h264", "pix_fmt": "yuv420p"}
    monkeypatch.setattr(vr, "probe_video", lambda p: src)
    used = []
    monkeypatch.setattr(vr, "export_video", lambda i, o, s, tw, th, where, *a, **k: used.append(("encode", tw, th, where)) or (1.0, []))
    monkeypatch.setattr(vr, "export_passthrough", lambda *a, **k: used.append(("copy",)) or (1.0, []))
    exports = [e for e in vr.VIDEO_EXPORTS if e[0] in ("reel_instagram", "post_square_instagram")]
    f = tmp_path / "a.mp4"; f.write_bytes(b"x")
    vr.process_video(f, tmp_path / "out", exports, "top", None, None, frames={"9:16": {"cx": 0.5, "cy": 0.5, "z": 0.6}})
    assert used[0][:3] == ("encode", 1080, 1920) and used[0][3]["z"] == 0.6     # zoomed: re-encoded, not copied
    assert used[1] == ("encode", 1080, 1080, "top")                               # other shape: the focal point
    used.clear()
    vr.process_video(f, tmp_path / "out", exports[:1], "top", None, None, frames={"9:16": {"cx": 0.3, "cy": 0.5, "z": 1}})
    assert used == [("copy",)]                                                    # same shape, whole frame: untouched copy
