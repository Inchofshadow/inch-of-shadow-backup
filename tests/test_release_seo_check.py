"""release_seo_check.py - offline, pure text (System 102)."""
import hashlib
import json
from pathlib import Path

import pytest

import release_seo_check as rsc

ROOT = Path(__file__).resolve().parent.parent

RELEASE = {
    "slug": "test-ep",
    "release_date": "2026-12-11",
    "metadata": {"title": "Half the Night", "artist": "Inch of Shadow", "release_type": "EP",
                 "catalog_number": "ICR-003", "copyright": "2026 Indigo Children Records",
                 "description": "Half the Night is a restless 303 acid line."},
    "tracks": [{"number": 1, "title": "Half the Night", "bpm": 127.0, "key": "Fm", "isrc": "QZWDE2693303"},
               {"number": 2, "title": "Pinocchio", "bpm": 126.0, "key": "", "isrc": "QZWDE2693308"}],
    "distribution": {"upc": "708208624645", "live_date": ""},
    "platform_tags": {"tag_rules": {"never": ["techno", "trance", "dark electro"],
                                    "description_words_only": ["303", "rolling bass"]}},
    "bandcamp_campaign_links": {"sc-desc": "https://inchofshadow.bandcamp.com/album/half-the-night?campaign=sc-desc"},
}
PROFILE = {"labels": ["Stereo Society", "Indigo Children Records"],
           "links": {"instagram": "https://www.instagram.com/inch_of_shadow/"}}


@pytest.fixture
def env(tmp_path):
    rel_dir = tmp_path / "releases"
    rel_dir.mkdir()
    (rel_dir / "test-ep.json").write_text(json.dumps(RELEASE))
    prof = tmp_path / "artist_profile.json"
    prof.write_text(json.dumps(PROFILE))
    specs = tmp_path / "specs.json"
    specs.write_text(json.dumps({"platforms": {
        "soundcloud": {"text_fields": {"track_title": {"max_chars": 100}}},
        "youtube": {"video_fields": {"tags": {"max_total_chars": 50}}}}}))
    return rel_dir, prof, specs


def run(env, fields, **doc):
    rel_dir, prof, specs = env
    d = {"release": "test-ep", "fields": fields}
    d.update(doc)
    return rsc.run_check(d, releases_dir=rel_dir, profile_path=prof, specs_path=specs)


def checks(rep, i=0):
    return {x["check"] for x in rep["fields"][i]["issues"]}


def text(t, platform="soundcloud", field="description", **kw):
    f = {"platform": platform, "field": field, "text": t}
    f.update(kw)
    return f


def test_clean_copy_passes(env):
    rep = run(env, [text("Half the Night EP, out 11 December 2026 on Indigo Children Records (ICR-003).\n"
                         "Bandcamp: https://inchofshadow.bandcamp.com/album/half-the-night?campaign=sc-desc")])
    assert rep["verdict"] == "PASS", rep["fields"][0]["issues"]


@pytest.mark.parametrize("bad", ["dark — rolling", "dark -- rolling", "dark – rolling", "a―b"])
def test_dashes_fail(env, bad):
    rep = run(env, [text(bad)])
    assert "DASHES" in checks(rep) and rep["verdict"] == "FAIL"


def test_plain_hyphen_and_number_range_are_fine(env):
    assert "DASHES" not in checks(run(env, [text("Inch of Shadow - Half the Night, tracks 1-2")]))


def test_never_tag_and_text_only_word_fail(env):
    rep = run(env, [{"platform": "soundcloud", "field": "tags", "tags": ["electro", "Techno", "#darkelectro", "303"]}])
    bad = [i["quote"] for i in rep["fields"][0]["issues"] if i["check"] == "NEVER TAG"]
    assert bad == ["Techno", "#darkelectro", "303"]


def test_never_words_allowed_in_text(env):
    # the never list is for tags; "trance arp" and "303" are fine in the description
    assert run(env, [text("a dark, rolling trance arp and a 303 line")])["verdict"] == "PASS"


def test_genre_field_is_checked_like_a_tag(env):
    assert "NEVER TAG" in checks(run(env, [text("Techno", field="genre")]))


@pytest.mark.parametrize("bad", ["Written in F minor.", "a Fm groove", "in the key of A", "Camelot 4A mix", "C#m drive"])
def test_key_in_copy_fails(env, bad):
    assert "KEY" in checks(run(env, [text(bad)]))


@pytest.mark.parametrize("ok", ["EBM from Berlin", "send me a DM", "a minor detail", "a minimal groove"])
def test_key_false_friends_pass(env, ok):
    assert "KEY" not in checks(run(env, [text(ok)]))


def test_key_in_tags_fails(env):
    rep = run(env, [{"platform": "soundcloud", "field": "tags", "tags": ["f minor", "Fm", "8A", "acid"]}])
    assert [i["quote"] for i in rep["fields"][0]["issues"] if i["check"] == "KEY"] == ["f minor", "Fm", "8A"]


def test_bpm_in_copy_fails_unless_amir_asked(env):
    assert "BPM" in checks(run(env, [text("driving at 127 BPM")]))
    assert "BPM" not in checks(run(env, [text("driving at 127 BPM")], bpm_in_copy_ok=True))


def test_bpm_tag_is_fine_but_must_match_the_record(env):
    rep = run(env, [{"platform": "soundcloud", "field": "tags", "tags": ["127 bpm", "130 bpm"]}])
    issues = rep["fields"][0]["issues"]
    assert [i["quote"] for i in issues] == ["130 bpm"] and issues[0]["check"] == "FACTS"


def test_facts_must_come_from_the_release_json(env):
    rep = run(env, [text("ISRC QZWDE2693399, UPC 708208624699, ICR-004, out 4 December, "
                         "https://example.com/x")])
    quotes = [i["quote"] for i in rep["fields"][0]["issues"] if i["check"] == "FACTS"]
    assert sorted(quotes) == sorted(["QZWDE2693399", "708208624699", "ICR-004", "4 December",
                                     "https://example.com/x"])


def test_known_facts_pass_in_all_date_formats(env):
    rep = run(env, [text("QZWDE2693303 / 708208624645 / ICR-003 / 2026-12-11 / Dec 11 / December 11, 2026 / "
                         "11 Dec / https://www.instagram.com/inch_of_shadow/")])
    assert "FACTS" not in checks(rep), rep["fields"][0]["issues"]


def test_wrong_year_fails(env):
    assert "FACTS" in checks(run(env, [text("out 11 December 2025")]))


def test_placeholders_fail(env):
    rep = run(env, [text("Stream: [TODO the smart link]\nSpotify: <smart link>")])
    assert [i["check"] for i in rep["fields"][0]["issues"]].count("PLACEHOLDER") == 2


def test_soundcloud_title_stays_plain(env):
    rep = run(env, [text("Inch of Shadow - Half the Night", field="title"),
                    text("Half the Night", field="title"),
                    text("Inch of Shadow - Half the Night (Official Audio)", platform="youtube", field="title")])
    assert [r["status"] for r in rep["fields"]] == ["FAIL", "PASS", "PASS"]


def test_name_in_full(env):
    assert "NAME" in checks(run(env, [text("new IoS release")]))


def test_length_from_specs(env):
    assert "LENGTH" in checks(run(env, [text("x" * 101, field="title")]))
    rep = run(env, [{"platform": "youtube", "field": "tags", "tags": ["a" * 30, "b" * 30]}])
    assert "LENGTH" in checks(rep)


def test_other_label_and_release_type_warn(env, tmp_path):
    rep = run(env, [text("out on Stereo Society")])
    assert rep["fields"][0]["status"] == "WARN" and "LABEL" in checks(rep)
    single = dict(RELEASE, metadata=dict(RELEASE["metadata"], release_type="Single"))
    (env[0] / "test-ep.json").write_text(json.dumps(single))
    assert "RELEASE TYPE" in checks(run(env, [text("Half the Night EP")]))


def test_release_type_passes_when_copy_type_is_ep(env):
    store_single = dict(RELEASE, metadata=dict(RELEASE["metadata"], release_type="Single", copy_release_type="EP"))
    (env[0] / "test-ep.json").write_text(json.dumps(store_single))
    assert "RELEASE TYPE" not in checks(run(env, [text("Half the Night EP")]))
    other = dict(RELEASE, metadata=dict(RELEASE["metadata"], release_type="Single", copy_release_type="Single"))
    (env[0] / "test-ep.json").write_text(json.dumps(other))
    assert "RELEASE TYPE" in checks(run(env, [text("Half the Night EP")]))


def test_fact_sheet_shows_store_and_copy_type(env):
    rel_dir, prof, _ = env
    assert "(store)" not in rsc.render_facts(rsc.facts_sheet("test-ep", rel_dir, prof))
    rel = dict(RELEASE, metadata=dict(RELEASE["metadata"], release_type="Single", copy_release_type="EP"))
    (rel_dir / "test-ep.json").write_text(json.dumps(rel))
    assert "Single  (store)  copy says: EP" in rsc.render_facts(rsc.facts_sheet("test-ep", rel_dir, prof))


def test_youtube_hashtag_count_warns(env):
    assert "HASHTAGS" in checks(run(env, [text("x\n\n#DarkDisco #Electro", platform="youtube")]))
    assert "HASHTAGS" not in checks(run(env, [text("x\n\n#DarkDisco #Electro #Acid", platform="youtube")]))


def test_duplicate_tags_warn(env):
    rep = run(env, [{"platform": "bandcamp", "field": "tags", "tags": ["dark disco", "Dark Disco"]}])
    assert rep["fields"][0]["status"] == "WARN" and "DUPLICATE" in checks(rep)


def test_voice_lines_are_drafts_until_approved(env):
    rep = run(env, [text("Half the Night EP", voice=True),
                    text("Half the Night EP", voice=True, approved="2026-11-10 Amir")])
    assert [r["draft"] for r in rep["fields"]] == [True, False]
    assert len(rep["drafts"]) == 1
    assert "DRAFT (his voice" in rsc.render_report(rep)


def test_top_fixes_worst_first_and_max_three(env):
    rep = run(env, [text("in F minor -- at 127 BPM, ISRC QZWDE2693399, [TODO]")])
    order = [t["check"] for t in rep["top_fixes"]]
    assert order == ["FACTS", "PLACEHOLDER", "KEY"]


def test_missing_rules_warn(env):
    bare = dict(RELEASE, platform_tags={})
    (env[0] / "test-ep.json").write_text(json.dumps(bare))
    rep = run(env, [text("fine")])
    assert rep["release_issues"] and rep["verdict"] == "WARN"


def test_bad_slug_refused(env):
    with pytest.raises(SystemExit):
        rsc.load_release("../secrets", env[0])


def test_out_never_into_releases(tmp_path):
    with pytest.raises(SystemExit):
        rsc._safe_out(rsc.RELEASES / "x.md", None)
    src = tmp_path / "f.json"
    with pytest.raises(SystemExit):
        rsc._safe_out(src, src)
    with pytest.raises(SystemExit):
        rsc._safe_out(tmp_path / "x.html", None)


def test_script_has_no_network_or_live_code():
    src = (ROOT / "release_seo_check.py").read_text()
    for banned in ("import requests", "urllib", "http.client", "socket", "subprocess", "selenium",
                   "playwright", "webbrowser", "smtplib"):
        assert banned not in src, banned


def test_real_release_file_is_never_written(tmp_path, capsys):
    path = ROOT / "releases" / "pinocchio-single.json"
    if not path.is_file():
        pytest.skip("release file not on disk")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    fields = tmp_path / "f.json"
    fields.write_text(json.dumps({"release": "pinocchio-single",
                                  "fields": [text("Half the Night", field="title")]}))
    out = tmp_path / "r.md"
    assert rsc.main(["check", str(fields), "--out", str(out)]) == 0
    assert out.read_text().startswith("RELEASE SEO CHECK")
    assert rsc.main(["facts", "pinocchio-single"]) == 0
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    assert "never in copy or tags" in capsys.readouterr().out


def test_skill_example_audit_file_runs(capsys):
    ex = ROOT / ".claude" / "skills" / "release-prep" / "examples" / "half-the-night-audit-2026-11-16.json"
    if not ex.is_file():
        pytest.skip("example not on disk")
    rsc.main(["check", str(ex)])
    assert "TOP 3 FIXES" in capsys.readouterr().out


def test_top_fixes_group_one_problem_across_fields(env):
    rep = run(env, [text("[TODO a]", platform="youtube", item="A"),
                    text("[TODO b]", platform="youtube", item="B"),
                    text("dark -- night")])
    assert [t["check"] for t in rep["top_fixes"]] == ["PLACEHOLDER", "DASHES"]
    assert len(rep["top_fixes"][0]["where"]) == 2


# ---- Fable gate 2026-11-16: the gaps the first build let through

SECRET = "https://soundcloud.com/inch-of-shadow/sets/half-the-night/s-cqiK2IkEg0T"


def test_secret_and_edit_links_never_pass(env):
    rel = dict(RELEASE, distribution=dict(RELEASE["distribution"], secret_links={"ep": SECRET},
                                          bandcamp_live={"edit_url": "https://x.bandcamp.com/edit_album?id=1"}))
    (env[0] / "test-ep.json").write_text(json.dumps(rel))
    rep = run(env, [text("Listen: " + SECRET), text("https://x.bandcamp.com/edit_album?id=1"),
                    text("https://studio.youtube.com/channel/UC1/editing/profile")])
    assert [r["issues"][0]["check"] for r in rep["fields"]] == ["PRIVATE LINK"] * 3
    assert rep["top_fixes"][0]["check"] == "PRIVATE LINK"


def test_secret_link_in_a_free_text_note_is_not_a_fact(env):
    rel = dict(RELEASE, notes="DJ promo link " + SECRET)
    (env[0] / "test-ep.json").write_text(json.dumps(rel))
    assert "PRIVATE LINK" in checks(run(env, [text(SECRET)]))


def test_never_word_inside_a_longer_tag(env):
    rep = run(env, [{"platform": "soundcloud", "field": "tags",
                     "tags": ["acid techno", "#acidtechno", "warehouse", "electro", "roland 303"]}])
    got = [(i["level"], i["quote"]) for i in rep["fields"][0]["issues"] if i["check"] == "NEVER TAG"]
    assert got == [("FAIL", "acid techno"), ("WARN", "#acidtechno"), ("FAIL", "roland 303")]


def test_never_hashtag_inside_a_description(env):
    rep = run(env, [text("Dark and rolling.\n\n#Techno #DarkDisco #Acid", platform="youtube")])
    assert [i["quote"] for i in rep["fields"][0]["issues"] if i["check"] == "NEVER TAG"] == ["#Techno"]


@pytest.mark.parametrize("bad", ["out 04.12.2026", "out 12/04/2026", "out on the 4th of December",
                                 "out November 2026", "out 11.12.25"])
def test_wrong_dates_in_other_formats_fail(env, bad):
    assert "FACTS" in checks(run(env, [text(bad)]))


@pytest.mark.parametrize("ok", ["out 11.12.2026", "out 12/11/2026", "out on the 11th of December",
                                "out December 2026", "out 11.12.26", "version 1.8.4 of the mix"])
def test_right_dates_in_other_formats_pass(env, ok):
    assert "FACTS" not in checks(run(env, [text(ok)]))


def test_bare_wrong_year_warns(env):
    assert "YEAR" in checks(run(env, [text("Half the Night (Indigo Children Records, 2025)")]))
    assert "YEAR" not in checks(run(env, [text("Half the Night (Indigo Children Records, 2026)")]))


def test_bpm_in_words_and_number_after(env):
    assert "BPM" in checks(run(env, [text("127 beats per minute")]))
    rep = run(env, [text("BPM: 130")], bpm_in_copy_ok=True)
    assert checks(rep) == {"FACTS"}
    assert run(env, [text("BPM: 127")], bpm_in_copy_ok=True)["verdict"] == "PASS"
    assert "BPM" in checks(run(env, [text("BPM: 127")], bpm_in_copy_ok="yes"))  # only a real true lifts it


@pytest.mark.parametrize("bad", ["in F sharp minor", "E-flat major", "written in f minor", "an F-minor line"])
def test_key_spelled_out_or_lower_case_fails(env, bad):
    rep = run(env, [text(bad)])
    assert rep["fields"][0]["status"] == "FAIL" and "KEY" in checks(rep)


def test_song_title_with_am_only_warns(env):
    rep = run(env, [text("I Am the Night", field="title")])
    assert rep["fields"][0]["status"] == "WARN" and "KEY" in checks(rep)


def test_gear_names_are_not_catalog_numbers(env):
    assert run(env, [text("a TB-303 and a TR-808 through an SH-101")])["verdict"] == "PASS"


@pytest.mark.parametrize("bad", ["ICR004", "icr-4", "ICR 012"])
def test_catalog_number_other_spellings_fail(env, bad):
    assert "FACTS" in checks(run(env, [text(bad)]))


def test_catalog_number_same_number_passes(env):
    assert "FACTS" not in checks(run(env, [text("ICR003, ICR-003, ICR 003")]))


def test_isrc_with_hyphens(env):
    assert "FACTS" in checks(run(env, [text("QZ-WDE-26-93399")]))
    assert "FACTS" not in checks(run(env, [text("QZ-WDE-26-93303")]))


def test_mistyped_fields_never_pass_silently(env):
    rep = run(env, [{"platform": "soundcloud", "field": "tags", "tag": ["techno"]},
                    {"platform": "soundcloud", "field": "description", "txt": "x"},
                    {"field": "title", "text": "Half the Night"},
                    {"platform": "instagram", "field": "hashtags", "text": "#techno #acid"},
                    {"platform": "soundcloud", "field": "description", "text": ""}])
    assert [r["status"] for r in rep["fields"]] == ["FAIL", "FAIL", "FAIL", "FAIL", "WARN"]
    assert "NEVER TAG" in checks(rep, 3)


def test_empty_fields_file_is_an_error(env):
    for fields in ([], None, "x"):
        with pytest.raises(SystemExit):
            run(env, fields)


def test_approved_field_must_hold_the_approved_text(env):
    rep = run(env, [text("A different text.", platform="bandcamp", field="about", approved="2026-11-10 Amir"),
                    text("First line.\n\nHalf the Night is a restless  303 acid line.\nmore", platform="bandcamp",
                         field="about", approved="2026-11-10 Amir")])
    assert "APPROVED TEXT" in checks(rep, 0) and "APPROVED TEXT" not in checks(rep, 1)


def test_draft_marks_and_labels_left_in_copy_fail(env):
    for bad in ("Half the Night [CHECK]", "✍️ Half the Night EP", "[HYPOTHESIS: charts]"):
        assert "PLACEHOLDER" in checks(run(env, [text(bad)])), bad


def test_name_casing_warns(env):
    rep = run(env, [text("New from Inch Of Shadow")])
    assert rep["fields"][0]["status"] == "WARN" and "NAME" in checks(rep)
    assert "NAME" not in checks(run(env, [text("New from Inch of Shadow")]))


def test_dashes_inside_a_url_are_not_copy(env):
    rel = dict(RELEASE, platform_links={"bandcamp": "https://x.bandcamp.com/album/half--night"})
    (env[0] / "test-ep.json").write_text(json.dumps(rel))
    assert run(env, [text("Bandcamp: https://x.bandcamp.com/album/half--night")])["verdict"] == "PASS"


def test_out_never_overwrites_a_project_file(tmp_path):
    other = tmp_path / "tickets.json"
    other.write_text('{"tickets": []}')
    with pytest.raises(SystemExit):
        rsc._safe_out(other, None)
    old_report = tmp_path / "report.md"
    old_report.write_text("RELEASE SEO CHECK  x\n")
    assert rsc._safe_out(old_report, None) == old_report.resolve()


def test_main_exit_code_follows_the_verdict(tmp_path, capsys):
    if not (ROOT / "releases" / "pinocchio-single.json").is_file():
        pytest.skip("release file not on disk")
    f = tmp_path / "f.json"
    f.write_text(json.dumps({"release": "pinocchio-single", "fields": [text("dark -- night")]}))
    assert rsc.main(["check", str(f)]) == 1
    capsys.readouterr()


def test_one_tempo_is_reported_once(env):
    rep = run(env, [text("genre, tempo 127.0 BPM, the instruments")])
    assert [i["check"] for i in rep["fields"][0]["issues"]] == ["BPM"]


def test_real_specs_keep_soundcloud_tag_numbers_unverified():
    """System 106: the old '5 tags, 20 chars' was never verified; no number is stated as fact."""
    specs = json.loads((ROOT / "release_manager" / "seo_platform_specs.json").read_text())
    tags = specs["platforms"]["soundcloud"]["tags"]
    assert tags["max_per_track"] is None and tags["max_chars_per_tag"] is None
    assert "NOT VERIFIED" in tags["unverified"]
    quick = specs["cross_platform_summary"]["character_limits_quick_reference"]["soundcloud_tags_max"]
    assert "NOT VERIFIED" in quick and not any(c.isdigit() for c in quick)
    # the guard still reads its real SoundCloud limits from the same file
    assert rsc.spec_limit(specs, "soundcloud", "title") == 100
    assert rsc.spec_limit(specs, "soundcloud", "description") == 4000
