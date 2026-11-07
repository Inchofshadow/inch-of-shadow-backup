"""Tests for the default-slug discovery guard (added 2026-07-10).

Discovery emits candidates whose permalink is a SoundCloud DEFAULT slug
(user-31224680, or a custom-looking name with a long trailing id like
james-payne-849040223). These are accounts that never set a real handle: low
signal, low reciprocity. The SOP told CC to skip them by eye; the engine never
enforced it, so 7 sat in discovery_candidates_20260710.json relying on CC's
click-time judgment.

_is_default_slug centralizes the rule so discovery filters them at the source.
"""
import scene_intelligence.sc_engagement as sc


def test_bare_user_id_slug_is_default():
    assert sc._is_default_slug("user-31224680")
    assert sc._is_default_slug("user-190308300")
    assert sc._is_default_slug("user-1")


def test_name_with_long_trailing_id_is_default():
    # SC appends the numeric id when a chosen handle collides.
    assert sc._is_default_slug("james-payne-849040223")
    assert sc._is_default_slug("lisa-asil-207228568")
    assert sc._is_default_slug("dare-dare-motus-734005289")


def test_real_handles_are_not_default():
    for good in ["dreambabydreambar", "terrorclashmexico", "records_zaman",
                 "hedrome", "flip_the_lid", "24-7", "cleo-25a7", "b12"]:
        assert not sc._is_default_slug(good), good


def test_short_trailing_number_is_not_default():
    # A trailing number that is not a real SC user id (short) is a stylistic
    # handle, not a collision suffix. cleo-25a7 / 24-7 must survive.
    assert not sc._is_default_slug("cleo-25a7")
    assert not sc._is_default_slug("model-500")


def test_empty_and_none_are_not_default():
    assert not sc._is_default_slug("")
    assert not sc._is_default_slug(None)


def test_accepts_full_url_or_bare_slug():
    assert sc._is_default_slug("https://soundcloud.com/user-31224680")
    assert not sc._is_default_slug("https://soundcloud.com/dreambabydreambar")
