"""Pure-logic tests for discover_curators. API calls are covered by manual smoke tests."""

from scene_intelligence.discover_curators import (
    aggregate_playlists_by_owner,
    build_candidate_row,
    filter_existing,
)


def _pl(playlist_id, name, followers, owner_id, owner_name, genres, url=""):
    return {
        "id": playlist_id,
        "name": name,
        "followers": followers,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "matched_genres": genres,
        "url": url or f"https://open.spotify.com/playlist/{playlist_id}",
    }


def test_aggregate_groups_playlists_by_owner_id():
    playlists = [
        _pl("p1", "Dark Disco", 2000, "user1", "DJ One", ["dark disco"]),
        _pl("p2", "Acid Cuts",   800, "user1", "DJ One", ["acid"]),
        _pl("p3", "EBM Nights", 1500, "user2", "DJ Two", ["ebm"]),
    ]
    owners = aggregate_playlists_by_owner(playlists)

    assert len(owners) == 2
    u1 = owners["user1"]
    assert u1["playlist_count"] == 2
    assert u1["playlist_total_followers"] == 2800
    assert u1["top_playlist_followers"] == 2000
    assert u1["top_playlist_name"] == "Dark Disco"
    assert set(u1["playlist_genres"]) == {"dark disco", "acid"}


def test_aggregate_sorts_top_playlist_by_follower_count():
    playlists = [
        _pl("p1", "Small",  100, "user1", "DJ One", ["dark disco"]),
        _pl("p2", "Big",   5000, "user1", "DJ One", ["dark disco"]),
    ]
    owners = aggregate_playlists_by_owner(playlists)
    assert owners["user1"]["top_playlist_name"] == "Big"


def test_build_candidate_row_for_spotify():
    owner = {
        "owner_id": "user42",
        "owner_name": "Berlin Curator",
        "playlist_count": 3,
        "playlist_total_followers": 4200,
        "top_playlist_name": "Dark Disco 2026",
        "top_playlist_followers": 3000,
        "top_playlist_url": "https://open.spotify.com/playlist/xyz",
        "playlist_genres": ["dark disco", "acid"],
        "playlist_urls": ["https://open.spotify.com/playlist/xyz"],
        "discovered_via": ["search:dark disco"],
    }
    row = build_candidate_row(owner, platform="spotify")

    assert row["name"] == "Berlin Curator"
    assert row["category"] == "curator"
    assert row["sub_type"] == "spotify"
    assert row["source"] == "curator_discovery"
    assert row["spotify_id"] == "user42"
    assert row["spotify_url"] == "https://open.spotify.com/user/user42"
    assert row["match_score"] == "3"
    assert row["playlist_count"] == 3
    assert row["playlist_total_followers"] == 4200
    assert row["top_playlist_name"] == "Dark Disco 2026"
    assert row["playlist_genres"] == "dark disco, acid"


def test_build_candidate_row_for_soundcloud():
    owner = {
        "owner_id": "sc_user_99",
        "owner_name": "SC Curator",
        "owner_permalink_url": "https://soundcloud.com/sc-curator",
        "owner_followers": 1800,
        "playlist_count": 2,
        "playlist_total_followers": 600,
        "top_playlist_name": "Acid Set",
        "top_playlist_followers": 400,
        "top_playlist_url": "https://soundcloud.com/sc-curator/sets/acid-set",
        "playlist_genres": ["acid"],
        "playlist_urls": ["https://soundcloud.com/sc-curator/sets/acid-set"],
        "discovered_via": ["search:acid"],
    }
    row = build_candidate_row(owner, platform="soundcloud")

    assert row["sub_type"] == "soundcloud"
    assert row["soundcloud_user_id"] == "sc_user_99"
    assert row["soundcloud_url"] == "https://soundcloud.com/sc-curator"
    assert row["soundcloud_followers"] == "1800"


def test_filter_existing_drops_duplicates_by_name():
    candidates = [
        {"name": "Berlin Curator", "spotify_id": "new1"},
        {"name": "Someone Else", "spotify_id": "new2"},
    ]
    existing = {
        "names": {"berlincurator"},
        "spotify_ids": set(),
        "soundcloud_user_ids": set(),
    }
    fresh = filter_existing(candidates, existing)
    assert len(fresh) == 1
    assert fresh[0]["name"] == "Someone Else"


def test_filter_existing_drops_duplicates_by_platform_id():
    candidates = [
        {"name": "Unique Name A", "spotify_id": "taken_id"},
        {"name": "Unique Name B", "soundcloud_user_id": "taken_sc"},
    ]
    existing = {
        "names": set(),
        "spotify_ids": {"taken_id"},
        "soundcloud_user_ids": {"taken_sc"},
    }
    assert filter_existing(candidates, existing) == []
