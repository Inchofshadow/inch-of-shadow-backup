"""The last pass over generated copy (release_manager/copy_pass.py). No network."""
import release_manager.copy_pass as cp


def test_finalise_copy_cleans_fields_and_checks_instagram():
    result = {
        "spotify_pitch": "Farewell — an EBM track…",
        "youtube_titles": ["Farewell – Inch of Shadow", "Farewell (EBM)"],
        "instagram_caption": "Farewell. Out now — acid melody, brooding atmosphere \U0001F5A4",
        "instagram_hashtags": ["darkdisco", "ebm", "acidtechno", "berlinunderground", "electronicmusic"],
        "_usage": {"input_tokens": 1, "output_tokens": 1},
    }
    out = cp.finalise_copy(result, {"metadata": {"genre_primary": "EBM"}})
    assert out["spotify_pitch"] == "Farewell, an EBM track..."
    assert out["youtube_titles"][0] == "Farewell, Inch of Shadow"
    assert out["instagram_caption"].startswith("Farewell. Out now, acid melody")
    assert out["_clean"]["changes"] == 4
    chk = out["_check"]["instagram"]
    assert chk["verdict"] == "PASS"
    assert chk["hashtags"] == ["#darkdisco", "#ebm", "#acidtechno", "#berlinunderground", "#electronicmusic"]
    assert "WHAT THE FEED SHOWS" in chk["text"]
    assert any(r["check"] == "KEYWORD" and r["status"] == "PASS" for r in chk["results"])
    assert out["_usage"] == {"input_tokens": 1, "output_tokens": 1}


def test_finalise_copy_flags_a_bad_caption():
    result = {"instagram_caption": "Let me know what you think!",
              "instagram_hashtags": ["music", "a", "b", "c", "d", "e"]}
    out = cp.finalise_copy(result)
    chk = out["_check"]["instagram"]
    assert chk["verdict"] == "FAIL"
    names = {r["check"]: r["status"] for r in chk["results"] if r["status"] == "FAIL"}
    assert names.get("ASKS") == "FAIL" and names.get("HASHTAGS") == "FAIL"


def test_finalise_copy_without_instagram_has_no_check():
    out = cp.finalise_copy({"beatport_description": "clean already"})
    assert out["_clean"]["changes"] == 0 and "_check" not in out


def test_assemble_instagram_accepts_string_tags():
    text = cp.assemble_instagram({"instagram_caption": "Out now.", "instagram_hashtags": "#ebm, darkdisco"})
    assert text == "Out now.\n\n#ebm #darkdisco"


def test_finalise_bios_cleans_only():
    out = cp.finalise_bios({"instagram": "Dark disco · Berlin — producer", "spotify": "ok"})
    assert out["instagram"] == "Dark disco · Berlin, producer"
    assert out["_clean"]["changes"] == 1 and "_check" not in out
