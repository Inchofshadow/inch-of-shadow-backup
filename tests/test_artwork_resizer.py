"""artwork_resizer.py: preset table, 4000px cover master with no upscaling, privacy, colour.

Synthetic images only. Spec basis: platform pages checked 2026-09-20 (ticket Machine-07):
Apple asks for covers of at least 4000x4000, YouTube recommends 3840x2160 thumbnails
(2160x3840 for Shorts), Instagram's grid shows 3:4 tiles, Beatport prefers 3000x3000.
"""
import sys
from pathlib import Path

import piexif
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import artwork_resizer as ar  # noqa: E402


def make_image(path: Path, w: int, h: int, gps: bool = False) -> Path:
    im = Image.new("RGB", (w, h), (40, 20, 30))
    for x in range(0, w, max(1, w // 20)):
        for y in range(0, h, max(1, h // 20)):
            im.putpixel((x, y), (214, 209, 200))
    kw = {}
    if gps:
        kw["exif"] = piexif.dump({
            "0th": {piexif.ImageIFD.Make: b"TESTCAM"},
            "GPS": {piexif.GPSIFD.GPSLatitudeRef: b"N",
                    piexif.GPSIFD.GPSLatitude: ((52, 1), (28, 1), (0, 1))},
        })
    im.save(path, quality=95, **kw)
    return path


def sizes(name):
    return next((e[1], e[2]) for e in ar.EXPORTS if e[0] == name)


def run(src, out, only=None):
    out.mkdir(parents=True, exist_ok=True)
    exports = [e for e in ar.EXPORTS if (only is None or e[0] in only)]
    return ar.process_image(src, out, exports, "center", None, None)


# --- preset table ---------------------------------------------------------

def test_release_cover_master_is_4000():
    for name in ("release_spotify", "release_applemusic", "release_bandcamp"):
        assert sizes(name) == (4000, 4000), name


def test_beatport_release_is_3000():
    assert sizes("release_beatport") == (3000, 3000)


def test_youtube_thumbnails_include_4k_and_shorts():
    assert sizes("thumb_youtube_4k") == (3840, 2160)
    assert sizes("thumb_youtube_shorts") == (2160, 3840)
    assert sizes("thumb_youtube") == (1280, 720)  # kept: phone uploads are capped at 2 MB


def test_instagram_portrait_stills_exist():
    assert sizes("social_instagram_portrait") == (1080, 1350)
    assert sizes("social_instagram_grid") == (1080, 1440)
    assert sizes("social_instagram_reel_cover") == (420, 654)


def test_new_profile_presets_exist():
    assert sizes("profile_soundcloud_avatar") == (1000, 1000)
    assert sizes("profile_bandcamp_header") == (975, 180)


def test_every_template_has_a_purpose_label():
    for e in ar.EXPORTS:
        assert e[0] in ar.TEMPLATE_PURPOSE, e[0]


def test_filenames_are_unique():
    merged = ar.merge_exports(ar.EXPORTS)
    names = [ar.build_export_filename(m, "x", "jpg") for m in merged]
    assert len(names) == len(set(names))


# --- cover master: 4000 when the source allows, never upscaled -------------

def test_4000_master_gives_4000_cover(tmp_path):
    src = make_image(tmp_path / "art.jpg", 4200, 4200)
    results = run(src, tmp_path / "out", only={"release_spotify", "release_applemusic", "release_bandcamp"})
    assert len(results) == 1
    filename, w, h, kb, category, upscaled = results[0]
    assert (w, h) == (4000, 4000) and upscaled is False
    assert Image.open(tmp_path / "out" / filename).size == (4000, 4000)


def test_3000_master_falls_back_to_3000_not_upscaled(tmp_path, capsys):
    src = make_image(tmp_path / "art.jpg", 3000, 3000)
    results = run(src, tmp_path / "out", only={"release_spotify", "release_applemusic", "release_bandcamp"})
    filename, w, h, kb, category, upscaled = results[0]
    assert (w, h) == (3000, 3000) and upscaled is False
    assert Image.open(tmp_path / "out" / filename).size == (3000, 3000)
    text = capsys.readouterr()
    assert "4000" in (text.out + text.err)  # says what Apple asks for


# --- privacy and colour stay intact ---------------------------------------

def test_outputs_strip_gps_and_embed_srgb(tmp_path):
    src = make_image(tmp_path / "art.jpg", 4200, 4200, gps=True)
    results = run(src, tmp_path / "out", only={"release_spotify", "social_instagram_grid", "thumb_youtube_4k"})
    assert len(results) == 3
    for filename, *_ in results:
        im = Image.open(tmp_path / "out" / filename)
        assert im.mode == "RGB"
        assert im.info.get("icc_profile")
        ex = im.info.get("exif")
        if ex:
            loaded = piexif.load(ex)
            assert not loaded.get("GPS")
            assert piexif.ImageIFD.Make not in loaded.get("0th", {})


def test_webapp_labels_cover_every_template():
    text = (ROOT / "release_manager" / "views" / "release.py").read_text(encoding="utf-8")   # _build_artwork_export_groups labels, since RM 2.0 slice 7
    for e in ar.EXPORTS:
        assert f'"{e[0]}"' in text, f"webapp label missing for {e[0]}"


def test_cover_mode_keeps_the_whole_cover_and_skips_profile_sizes():
    """--cover (Machine-09 rehearsal, 2026-09-21): a square release cover is never cropped.

    A plain 16:9 crop cut the artist name off The Deceiver's cover, and a cover run also made
    avatars and banners nobody wants from a cover.
    """
    import artwork_resizer as ar
    from PIL import Image
    cover = Image.new("RGB", (600, 600), (200, 30, 30))
    for x in range(600):                                   # a top and a bottom band, the parts a crop loses
        for y in list(range(0, 40)) + list(range(560, 600)):
            cover.putpixel((x, y), (255, 255, 255))
    out = ar.compose_cover(cover, 1280, 720)
    assert out.size == (1280, 720)
    assert out.getpixel((640, 10))[0] > 240 and out.getpixel((640, 710))[0] > 240   # both bands survive
    assert out.getpixel((640, 360)) == (200, 30, 30)                                # the cover itself is untouched
    assert sum(out.getpixel((40, 360))) < sum((200, 30, 30))                        # the sides are the darkened blur
    tall = ar.compose_cover(cover, 1080, 1920)
    assert tall.size == (1080, 1920) and tall.getpixel((540, 960)) == (200, 30, 30)
    kept = [e for e in ar.EXPORTS if not e[0].startswith("profile_")]          # what --cover exports
    assert {e[0] for e in kept} >= {"release_spotify", "thumb_youtube", "thumb_youtube_4k", "social_instagram_story"}
    assert not any("avatar" in e[0] or "banner" in e[0] or "header" in e[0] for e in kept)
