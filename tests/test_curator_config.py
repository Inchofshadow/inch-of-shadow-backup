from scene_intelligence.curator_config import (
    GENRE_KEYWORDS,
    match_genres,
    is_editorial_owner,
    SPOTIFY_MIN_PLAYLIST_FOLLOWERS,
    SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS,
)


def test_genre_keywords_non_empty():
    assert len(GENRE_KEYWORDS) >= 8
    assert "dark disco" in GENRE_KEYWORDS
    assert "acid techno" in GENRE_KEYWORDS
    assert "ebm" in GENRE_KEYWORDS


def test_match_genres_finds_keyword_in_title():
    matches = match_genres("Dark Disco 2026 - Best Tracks")
    assert "dark disco" in matches


def test_match_genres_is_case_insensitive():
    matches = match_genres("ACID TECHNO VIBES")
    assert "acid techno" in matches or "acid" in matches


def test_match_genres_scans_description():
    matches = match_genres(
        title="Generic Title",
        description="A playlist of dark disco, EBM, and cosmic disco music."
    )
    assert "dark disco" in matches
    assert "ebm" in matches
    assert "cosmic disco" in matches


def test_match_genres_empty_on_no_match():
    assert match_genres("Top 40 Pop Hits") == []


def test_is_editorial_owner_detects_spotify():
    assert is_editorial_owner("Spotify", "spotify") is True
    assert is_editorial_owner("spotify", "") is True


def test_is_editorial_owner_allows_user():
    assert is_editorial_owner("Berlin DJ", "berlindj123") is False


def test_thresholds_are_sane():
    assert SPOTIFY_MIN_PLAYLIST_FOLLOWERS >= 100
    assert SOUNDCLOUD_MIN_PLAYLIST_FOLLOWERS >= 50
