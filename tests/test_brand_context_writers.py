"""The copy writers read the brand files and keep Pinocchio on the electronic lane (2026-09-27)."""
import json
from pathlib import Path

from release_manager import brand_context
from release_manager.bio_manager import _build_system_prompt as bio_prompt
from release_manager.seo_copy_generator import _build_system_prompt as seo_prompt

ROOT = Path(__file__).resolve().parent.parent


def pinocchio():
    return json.loads((ROOT / "releases" / "pinocchio-single.json").read_text())


def test_pinocchio_is_electronic_and_dance_music_first():
    p = seo_prompt("authentic", pinocchio())
    assert "LANE: ELECTRONIC" in p and "DANCE MUSIC" in p
    m = pinocchio()["metadata"]                               # its own genres lead, whatever they are now
    assert f'{m["genre_primary"]} / {m["genre_secondary"]}' in p   # (Acid / Italo Disco until the 11-03 tag change)
    assert "dark dance wave" in p.lower()
    assert "About Blank" in p                                 # venues only from proof.md
    assert "Tresor" not in p and "Berghain" not in p
    assert "Do NOT mention songs, singing" in p


def test_a_songs_release_is_marked_not_public_while_the_status_block_stands():
    p = seo_prompt("authentic", {"lane": "full", "metadata": {"genre_primary": "Darkwave"}})
    assert "LANE: SONGS" in p
    if not brand_context.songs_public():
        assert "NOT PUBLIC YET" in p


def test_bios_speak_for_the_electronic_lane_and_double_figure_is_past():
    p = bio_prompt()
    assert "LANE: ELECTRONIC" in p and "was one half of the duo Double Figure" in p
    assert "About Blank" in p and "DADA" in p


def test_section_reader():
    assert brand_context.section("## A\none\n## B\ntwo\n", "A") == "one"
    assert brand_context.section("## A\none\n", "Missing") == ""


def test_the_electronic_brief_carries_no_songs_era_identity():
    f = brand_context.facts("electronic")
    assert "sings" not in f and "bio switch" not in f and "producer and DJ" in f
