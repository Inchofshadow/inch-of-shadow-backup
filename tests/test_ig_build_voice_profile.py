import json
import scene_intelligence.ig_build_voice_profile as vp


def test_fix_ig_text_decodes_mojibake():
    # IG exports store UTF-8 bytes re-read as latin-1. Build that mojibake reliably.
    original = "\U0001f5a4"  # black-heart emoji
    mojibake = original.encode("utf-8").decode("latin-1")
    assert vp.fix_ig_text(mojibake) == original


def test_fix_ig_text_passes_plain_text():
    assert vp.fix_ig_text("hello world") == "hello world"
    assert vp.fix_ig_text("") == ""


def test_collect_titles_walks_nested_shapes():
    data = {"ig_reels_media": [{"media": [{"title": "reel caption @friend"}]}]}
    out = []
    vp.collect_titles(data, out)
    assert "reel caption @friend" in out


def test_collect_titles_skips_empty():
    out = []
    vp.collect_titles({"title": "   ", "media": [{"title": "real"}]}, out)
    assert out == ["real"]


def _write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def test_load_captions_merges_all_media_files(tmp_path):
    base = tmp_path / "data" / "instagram-test" / "your_instagram_activity"
    _write(base / "media" / "posts_1.json",
           [{"title": "post one @alpha #darkdisco", "media": [{"title": ""}]}])
    _write(base / "media" / "reels.json",
           {"ig_reels_media": [{"media": [{"title": "reel one @beta"}]}]})
    _write(base / "media" / "stories.json",
           {"ig_stories": [{"title": "story one"}]})
    glob_path = str(tmp_path / "data" / "instagram-*" / "your_instagram_activity")
    caps = vp.load_captions(glob_path)
    assert "post one @alpha #darkdisco" in caps
    assert "reel one @beta" in caps
    assert "story one" in caps


def test_load_comment_owners(tmp_path):
    base = tmp_path / "data" / "instagram-test" / "your_instagram_activity"
    _write(base / "comments" / "post_comments_1.json",
           [{"string_map_data": {"Comment": {"value": "fire"},
                                 "Media Owner": {"value": "jonnyknueppel"}}}])
    glob_path = str(tmp_path / "data" / "instagram-*" / "your_instagram_activity")
    owners = vp.load_comment_owners(glob_path)
    assert owners == ["jonnyknueppel"]


def test_build_profile_counts_mentions_hashtags():
    caps = ["hi @alpha @alpha #darkdisco \U0001f5a4", "yo @beta #darkdisco"]
    profile = vp.build_voice_profile(caps)
    assert profile["caption_count"] == 2
    assert profile["top_hashtags"][0][0] == "darkdisco"
    assert profile["emoji_caption_ratio"] > 0
    assert isinstance(profile["captions"], list)


def test_build_collaborators_ranks_mentions_and_owners():
    caps = ["@alpha @alpha @beta"]
    owners = ["alpha", "gamma"]
    collab = vp.build_collaborators(caps, owners)
    handles = [c["handle"] for c in collab["accounts"]]
    assert handles[0] == "alpha"   # most frequent overall
    assert "gamma" in handles


def test_build_collaborators_excludes_own_handle():
    caps = ["@inch_of_shadow @inch_of_shadow @beta"]
    collab = vp.build_collaborators(caps, [])
    handles = [c["handle"] for c in collab["accounts"]]
    assert "inch_of_shadow" not in handles
    assert "beta" in handles
