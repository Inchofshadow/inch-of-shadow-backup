"""
stats/collectors.py
--------------------
API collectors for each platform. Each collector returns a dict of stats, or
{"skipped": "<reason>"} when it could not read (M11, 2026-11-06: a skipped reason, never
a None or a 0, so every reader can say "skipped, because"). All are safe to call.

Spotify artist ID and SoundCloud user ID are auto-detected from .env / token.
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

TIMEOUT = 15
_SECRET_PARAM = re.compile(r"((?:access_token|key|client_secret|client_id|refresh_token)=)[^&\s'\"]+", re.I)


def skipped(reason: str) -> dict:
    """The block a collector returns when it could not read: the reason, never a 0."""
    return {"skipped": str(reason)[:200]}


def reason_of(exc: BaseException) -> str:
    """'ConnectionError: ...' with any token or key in a URL redacted; never prints a secret."""
    text = _SECRET_PARAM.sub(r"\1<redacted>", str(exc))
    for secret in (META_IG_ACCESS_TOKEN, SPOTIFY_CLIENT_SECRET, YOUTUBE_API_KEY, SC_CLIENT_SECRET):
        if secret:
            text = text.replace(secret, "<redacted>")
    return ("%s: %s" % (type(exc).__name__, text)).strip(": ")[:200]

# ---------------------------------------------------------------------------
# Spotify (Client Credentials)
# ---------------------------------------------------------------------------

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_ARTIST_ID = "5k4SyH7JRPMJe1RHYMI2CT"  # Inch of Shadow

_sp_token_cache: dict = {"access_token": "", "expires_at": 0.0}


def _spotify_token() -> str:
    if _sp_token_cache["access_token"] and time.time() < _sp_token_cache["expires_at"]:
        return _sp_token_cache["access_token"]
    creds = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {creds}"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            data = r.json()
            _sp_token_cache["access_token"] = data["access_token"]
            _sp_token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
            return data["access_token"]
    except Exception:
        pass
    return ""


def collect_spotify() -> dict | None:
    """Collect the Spotify catalogue: albums with their tracks, plus top tracks when the app may read them.

    Followers and popularity are no longer requested (System 68, 2026-11-05): the artist-profile
    call answered null for both on every snapshot since 2026-10-01 (Development Mode strips them,
    and genres came back empty), so that call is gone. Followers come from the Monday Spotify for
    Artists read (stats/spotify_s4a.py); the snapshot says so in followers_source.
    """
    token = _spotify_token()
    if not token:
        return skipped("no Spotify token (client credentials call failed or keys missing)")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Top tracks (may return 403 in Dev Mode)
        r2 = requests.get(
            f"https://api.spotify.com/v1/artists/{SPOTIFY_ARTIST_ID}/top-tracks",
            headers=headers, params={"market": "DE"}, timeout=TIMEOUT,
        )
        top_tracks = []
        if r2.status_code == 200:
            for t in r2.json().get("tracks", [])[:10]:
                top_tracks.append({
                    "name": t["name"],
                    "popularity": t.get("popularity", 0),
                    "album": t.get("album", {}).get("name", ""),
                    "duration_ms": t.get("duration_ms", 0),
                    "id": t.get("id", ""),
                })

        # Albums / singles / appearances (Dev Mode caps limit at 10). This is the read that
        # must answer: without the catalogue there is nothing worth a snapshot entry.
        r3 = requests.get(
            f"https://api.spotify.com/v1/artists/{SPOTIFY_ARTIST_ID}/albums",
            headers=headers,
            params={"limit": 10},
            timeout=TIMEOUT,
        )
        if r3.status_code != 200:
            return skipped("Spotify albums call answered HTTP %s" % r3.status_code)
        albums = []
        for a in r3.json().get("items", []):
            album_group = a.get("album_group", a.get("album_type", ""))
            album_id = a.get("id", "")
            album_entry = {
                "name": a.get("name", ""),
                "type": a.get("album_type", ""),
                "group": album_group,
                "release_date": a.get("release_date", ""),
                "total_tracks": a.get("total_tracks", 0),
                "markets": len(a.get("available_markets", [])),
                "id": album_id,
                "tracks": [],
            }

            # Fetch tracks for each album
            if album_id:
                r_tracks = requests.get(
                    f"https://api.spotify.com/v1/albums/{album_id}/tracks",
                    headers=headers,
                    params={"limit": 50},
                    timeout=TIMEOUT,
                )
                if r_tracks.status_code == 200:
                    for t in r_tracks.json().get("items", []):
                        dur_s = t.get("duration_ms", 0) // 1000
                        mins = dur_s // 60
                        secs = dur_s % 60
                        album_entry["tracks"].append({
                            "number": t.get("track_number", 0),
                            "name": t.get("name", ""),
                            "duration": f"{mins}:{secs:02d}",
                            "id": t.get("id", ""),
                            "artists": ", ".join(
                                ar.get("name", "") for ar in t.get("artists", [])
                            ),
                        })

            albums.append(album_entry)

        return {
            "followers_source": "spotify_for_artists",
            "note": "followers and popularity are not requested: the public API answers null for this app, "
                    "the Monday Spotify for Artists read (stats/spotify_s4a.py) is the followers source",
            "top_tracks": top_tracks,
            "albums": albums,
            "catalog_size": len(albums),
        }
    except Exception as e:
        return skipped(reason_of(e))


# ---------------------------------------------------------------------------
# SoundCloud (OAuth user token)
# ---------------------------------------------------------------------------

SC_TOKEN_FILE = BASE_DIR / ".sc_user_token.json"
SC_CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID", "")
SC_CLIENT_SECRET = os.getenv("SOUNDCLOUD_CLIENT_SECRET", "")


def _sc_token() -> str:
    if not SC_TOKEN_FILE.exists():
        return ""
    try:
        with open(SC_TOKEN_FILE) as f:
            data = json.load(f)
        return data.get("access_token", "")
    except Exception:
        return ""


def _sc_refresh_token() -> str:
    """Refresh the SoundCloud OAuth token if possible."""
    if not SC_TOKEN_FILE.exists():
        return ""
    try:
        with open(SC_TOKEN_FILE) as f:
            data = json.load(f)
        refresh = data.get("refresh_token", "")
        if not refresh:
            return ""
        r = requests.post(
            "https://api.soundcloud.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh,
                "client_id": SC_CLIENT_ID,
                "client_secret": SC_CLIENT_SECRET,
            },
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            new_data = r.json()
            with open(SC_TOKEN_FILE, "w") as f:
                json.dump(new_data, f, indent=2)
            return new_data.get("access_token", "")
    except Exception:
        pass
    return ""


def _sc_get(url, headers, params=None):
    """SoundCloud GET with auto token refresh on 401."""
    r = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    if r.status_code == 401:
        token = _sc_refresh_token()
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    return r, headers


def collect_soundcloud(geo: bool = False) -> dict | None:
    """Collect SoundCloud stats with per-track details.

    `geo=True` adds a follower-geography sample (one more /me/followers read, up to 200
    followers -> follower_countries / follower_cities). Off by default since 2026-11-05
    (System 68): it was fetched every day and nothing in the repo read it, and SoundCloud
    allows about 100 reads an hour that the morning discovery refresh already uses.
    """
    token = _sc_token()
    if not token:
        return skipped("no SoundCloud user token (.sc_user_token.json missing or unreadable)")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Get own profile
        r, headers = _sc_get("https://api.soundcloud.com/me", headers)
        if r.status_code != 200:
            return skipped("SoundCloud /me answered HTTP %s" % r.status_code)
        me = r.json()

        # Get tracks with full engagement data
        r2, headers = _sc_get(
            "https://api.soundcloud.com/me/tracks", headers, {"limit": 50},
        )
        tracks = []
        total_plays = 0
        total_likes = 0
        total_reposts = 0
        total_comments = 0
        total_downloads = 0
        if r2.status_code == 200:
            for t in r2.json():
                plays = t.get("playback_count", 0)
                likes = t.get("likes_count", t.get("favoritings_count", 0))
                reposts = t.get("reposts_count", 0)
                comments = t.get("comment_count", 0)
                downloads = t.get("download_count", 0)
                total_plays += plays
                total_likes += likes
                total_reposts += reposts
                total_comments += comments
                total_downloads += downloads
                tracks.append({
                    "title": t.get("title", ""),
                    "plays": plays,
                    "likes": likes,
                    "reposts": reposts,
                    "comments": comments,
                    "downloads": downloads,
                    "genre": t.get("genre", ""),
                    "created": t.get("created_at", "")[:10],
                    "duration_ms": t.get("duration", 0),
                    "artwork_url": t.get("artwork_url") or "",   # weekly panel thumbnails (G-06)
                })

        out = {
            "followers": me.get("followers_count", 0),
            "following": me.get("followings_count", 0),
            "track_count": me.get("track_count", 0),
            "playlist_count": me.get("playlist_count", 0),
            "total_plays": total_plays,
            "total_likes": total_likes,
            "total_reposts": total_reposts,
            "total_comments": total_comments,
            "total_downloads": total_downloads,
            "tracks": sorted(tracks, key=lambda x: x["plays"], reverse=True),
        }

        if geo:
            # Follower geography (sample up to 200 followers), opt-in only
            follower_countries = {}
            follower_cities = {}
            r3, _ = _sc_get(
                "https://api.soundcloud.com/me/followers", headers, {"limit": 200},
            )
            if r3.status_code == 200:
                followers_data = r3.json()
                if isinstance(followers_data, dict):
                    followers_data = followers_data.get("collection", [])
                for f in followers_data:
                    country = f.get("country_code") or f.get("country", "")
                    city = f.get("city", "")
                    if country:
                        follower_countries[country] = follower_countries.get(country, 0) + 1
                    if city:
                        follower_cities[city] = follower_cities.get(city, 0) + 1
            out["follower_countries"] = dict(sorted(follower_countries.items(), key=lambda x: -x[1])[:15])
            out["follower_cities"] = dict(sorted(follower_cities.items(), key=lambda x: -x[1])[:15])

        return out
    except Exception as e:
        return skipped(reason_of(e))


# ---------------------------------------------------------------------------
# YouTube (Data API v3)
# ---------------------------------------------------------------------------

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = ""  # Will auto-detect


def _find_youtube_channel_id() -> str:
    """Find the Inch of Shadow YouTube channel ID."""
    global YOUTUBE_CHANNEL_ID
    if YOUTUBE_CHANNEL_ID:
        return YOUTUBE_CHANNEL_ID
    if not YOUTUBE_API_KEY:
        return ""
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "key": YOUTUBE_API_KEY,
                "forHandle": "InchofShadow",
                "part": "id,statistics,snippet,contentDetails",
            },
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            items = r.json().get("items", [])
            if items:
                YOUTUBE_CHANNEL_ID = items[0]["id"]
                return YOUTUBE_CHANNEL_ID
        # Fallback: search
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "key": YOUTUBE_API_KEY,
                "q": "Inch of Shadow",
                "type": "channel",
                "maxResults": 1,
            },
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            items = r.json().get("items", [])
            if items:
                YOUTUBE_CHANNEL_ID = items[0]["id"]["channelId"]
                return YOUTUBE_CHANNEL_ID
    except Exception:
        pass
    return ""


def collect_youtube() -> dict | None:
    """Collect YouTube stats with per-video engagement rates and comments."""
    channel_id = _find_youtube_channel_id()
    if not channel_id:
        return skipped("YouTube channel id not found (YOUTUBE_API_KEY missing or the lookup failed)")
    try:
        # Channel stats + uploads playlist ID
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "key": YOUTUBE_API_KEY,
                "id": channel_id,
                "part": "statistics,snippet,contentDetails",
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return skipped("YouTube channels call answered HTTP %s" % r.status_code)
        items = r.json().get("items", [])
        if not items:
            return skipped("YouTube channels call returned no channel")
        channel = items[0]
        stats = channel.get("statistics", {})
        uploads_playlist = channel.get("contentDetails", {}).get(
            "relatedPlaylists", {}
        ).get("uploads", "")

        # Get videos via uploads playlist (1 quota unit vs 100 for search)
        video_ids = []
        videos = []
        if uploads_playlist:
            r2 = requests.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "key": YOUTUBE_API_KEY,
                    "playlistId": uploads_playlist,
                    "part": "snippet",
                    "maxResults": 20,
                },
                timeout=TIMEOUT,
            )
            if r2.status_code == 200:
                for item in r2.json().get("items", []):
                    vid_id = item["snippet"]["resourceId"]["videoId"]
                    video_ids.append(vid_id)
                    videos.append({
                        "id": vid_id,
                        "title": item["snippet"]["title"],
                        "published": item["snippet"]["publishedAt"][:10],
                        "thumb": ((item["snippet"].get("thumbnails") or {}).get("medium") or {}).get("url", ""),
                    })

        # Get detailed stats for each video (batch up to 50)
        if video_ids:
            r3 = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "key": YOUTUBE_API_KEY,
                    "id": ",".join(video_ids),
                    "part": "statistics,contentDetails",
                },
                timeout=TIMEOUT,
            )
            if r3.status_code == 200:
                vid_data = {v["id"]: v for v in r3.json().get("items", [])}
                for v in videos:
                    vd = vid_data.get(v["id"], {})
                    s = vd.get("statistics", {})
                    views = int(s.get("viewCount", 0))
                    likes = int(s.get("likeCount", 0))
                    comments = int(s.get("commentCount", 0))
                    v["views"] = views
                    v["likes"] = likes
                    v["comments"] = comments
                    v["engagement_rate"] = round(
                        (likes + comments) / views * 100, 1
                    ) if views > 0 else 0
                    # Parse duration
                    duration = vd.get("contentDetails", {}).get("duration", "")
                    v["duration"] = duration

        total_likes = sum(v.get("likes", 0) for v in videos)
        total_comments = sum(v.get("comments", 0) for v in videos)
        avg_engagement = 0
        vids_with_views = [v for v in videos if v.get("views", 0) > 0]
        if vids_with_views:
            avg_engagement = round(
                sum(v["engagement_rate"] for v in vids_with_views) / len(vids_with_views), 1
            )

        return {
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_engagement_rate": avg_engagement,
            "videos": videos,
        }
    except Exception as e:
        return skipped(reason_of(e))


# ---------------------------------------------------------------------------
# Instagram (Meta Graph API v21.0)
# ---------------------------------------------------------------------------

META_IG_ACCESS_TOKEN = os.getenv("META_IG_ACCESS_TOKEN", "")
# Daily sample source. Default "hikerapi" since 2026-11-05 (System 68): one provider call,
# claimed in the IG daily ledger as kind="provider" like every other HikerAPI read. Direct
# Instagram reads are off since 2026-09-14. "graph" (own-account Graph API, kind="api",
# 2 calls) stays available by setting IG_DAILY_SOURCE=graph in .env.
IG_DAILY_SOURCE = os.getenv("IG_DAILY_SOURCE", "hikerapi")
IG_USERNAME = "inch_of_shadow"


def collect_instagram() -> dict | None:
    """Collect Instagram stats with insights, demographics, and per-post metrics."""
    if not META_IG_ACCESS_TOKEN:
        return None
    try:
        # 1. Account profile
        r = requests.get(
            "https://graph.instagram.com/v21.0/me",
            params={
                "fields": "id,username,account_type,media_count,followers_count,follows_count",
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return None
        me = r.json()

        # 2. Daily insights (30 days): reach, follower_count, follows_and_unfollows
        now = int(time.time())
        since = now - (30 * 86400)
        daily_reach = []
        daily_followers = []

        r2 = requests.get(
            "https://graph.instagram.com/v21.0/me/insights",
            params={
                "metric": "reach,follower_count,follows_and_unfollows,profile_views",
                "period": "day",
                "since": since,
                "until": now,
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        daily_data = {}
        if r2.status_code == 200:
            for item in r2.json().get("data", []):
                name = item["name"]
                values = item.get("values", [])
                daily_data[name] = [
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in values
                ]

        # 3. Demographics: gender/age
        gender_age = {}
        r3 = requests.get(
            "https://graph.instagram.com/v21.0/me/insights",
            params={
                "metric": "follower_demographics",
                "period": "lifetime",
                "metric_type": "total_value",
                "breakdown": "age,gender",
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        if r3.status_code == 200:
            data = r3.json().get("data", [])
            if data:
                breakdowns = data[0].get("total_value", {}).get("breakdowns", [])
                if breakdowns:
                    for item in breakdowns[0].get("results", []):
                        dims = item["dimension_values"]
                        key = f"{dims[1]}.{dims[0]}"  # "M.25-34"
                        gender_age[key] = item["value"]

        # 4. Demographics: countries
        countries = {}
        r4 = requests.get(
            "https://graph.instagram.com/v21.0/me/insights",
            params={
                "metric": "follower_demographics",
                "period": "lifetime",
                "metric_type": "total_value",
                "breakdown": "country",
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        if r4.status_code == 200:
            data = r4.json().get("data", [])
            if data:
                breakdowns = data[0].get("total_value", {}).get("breakdowns", [])
                if breakdowns:
                    for item in sorted(breakdowns[0].get("results", []),
                                       key=lambda x: -x["value"])[:15]:
                        countries[item["dimension_values"][0]] = item["value"]

        # 5. Demographics: cities
        cities = {}
        r5 = requests.get(
            "https://graph.instagram.com/v21.0/me/insights",
            params={
                "metric": "follower_demographics",
                "period": "lifetime",
                "metric_type": "total_value",
                "breakdown": "city",
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        if r5.status_code == 200:
            data = r5.json().get("data", [])
            if data:
                breakdowns = data[0].get("total_value", {}).get("breakdowns", [])
                if breakdowns:
                    for item in sorted(breakdowns[0].get("results", []),
                                       key=lambda x: -x["value"])[:15]:
                        cities[item["dimension_values"][0]] = item["value"]

        # 6. Recent media with per-post insights
        r6 = requests.get(
            "https://graph.instagram.com/v21.0/me/media",
            params={
                "fields": "id,caption,media_type,media_product_type,timestamp,like_count,comments_count",
                "limit": 20,
                "access_token": META_IG_ACCESS_TOKEN,
            },
            timeout=TIMEOUT,
        )
        posts = []
        total_likes = 0
        total_comments = 0
        total_reach = 0
        total_saves = 0
        total_shares = 0
        if r6.status_code == 200:
            for p in r6.json().get("data", []):
                mid = p["id"]
                likes = p.get("like_count", 0)
                comments = p.get("comments_count", 0)
                total_likes += likes
                total_comments += comments
                caption = p.get("caption", "")
                media_type = p.get("media_product_type", p.get("media_type", ""))

                post_data = {
                    "id": mid,
                    "type": media_type,
                    "date": p.get("timestamp", "")[:10],
                    "likes": likes,
                    "comments": comments,
                    "caption": caption[:80] if caption else "",
                }

                # Fetch per-post insights
                metrics = "reach,total_interactions,saved,shares,likes,comments"
                r_post = requests.get(
                    f"https://graph.instagram.com/v21.0/{mid}/insights",
                    params={"metric": metrics, "access_token": META_IG_ACCESS_TOKEN},
                    timeout=TIMEOUT,
                )
                if r_post.status_code == 200:
                    for item in r_post.json().get("data", []):
                        vals = item.get("values", [{}])
                        val = vals[0].get("value", 0) if vals else 0
                        post_data[item["name"]] = val
                    total_reach += post_data.get("reach", 0)
                    total_saves += post_data.get("saved", 0)
                    total_shares += post_data.get("shares", 0)

                posts.append(post_data)

        # Compute gender summary
        male_total = sum(v for k, v in gender_age.items() if k.startswith("M."))
        female_total = sum(v for k, v in gender_age.items() if k.startswith("F."))
        unknown_total = sum(v for k, v in gender_age.items() if k.startswith("U."))
        gender_total = male_total + female_total + unknown_total
        gender_summary = {}
        if gender_total > 0:
            gender_summary = {
                "male": round(male_total / gender_total * 100, 1),
                "female": round(female_total / gender_total * 100, 1),
                "unknown": round(unknown_total / gender_total * 100, 1),
            }

        return {
            "followers": me.get("followers_count", 0),
            "following": me.get("follows_count", 0),
            "media_count": me.get("media_count", 0),
            "recent_likes": total_likes,
            "recent_comments": total_comments,
            "recent_reach": total_reach,
            "recent_saves": total_saves,
            "recent_shares": total_shares,
            "recent_posts": posts[:10],
            "daily_insights": daily_data,
            "demographics": {
                "gender_age": gender_age,
                "gender_summary": gender_summary,
                "countries": countries,
                "cities": cities,
            },
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Instagram daily sample (light: 1 HikerAPI call by default, or 2 Graph calls) + HikerAPI balance
# ---------------------------------------------------------------------------

def _claim(**kw):
    """Ledger claim before any Instagram read (raises LedgerRefused, a SystemExit, if refused)."""
    from scene_intelligence.ig_daily_ledger import check_and_claim
    return check_and_claim(**kw)


def _provider():
    from scene_intelligence.ig_data_provider import Provider
    return Provider()


def _ig_daily_hikerapi() -> dict | None:
    _claim(script="stats_daily_sync", kind="provider", est_calls=1, endpoint="user_by_username")
    p = _provider().profile(IG_USERNAME)
    if not p:
        return skipped("HikerAPI profile read returned nothing (provider error or empty answer)")
    return {
        "followers": p.get("follower_count"),
        "following": p.get("following_count"),
        "media_count": p.get("media_count"),
        "reach_30d": None,
        "source": "hikerapi",
    }


def _ig_daily_graph() -> dict | None:
    if not META_IG_ACCESS_TOKEN:
        return skipped("no META_IG_ACCESS_TOKEN in .env for the Graph variant")
    try:
        _claim(script="stats_daily_sync", kind="api", est_calls=2, endpoint="graph_insights")
    except KeyboardInterrupt:
        raise
    except SystemExit:
        # OpsGate (09:00-21:00 rule) and LedgerRefused (one API job per day) are
        # SystemExit subclasses. Provider claims have no hours rule, so the
        # 08:45 sync still gets its reading from HikerAPI.
        return _ig_daily_hikerapi()
    try:
        r = requests.get(
            "https://graph.instagram.com/v21.0/me",
            params={"fields": "id,username,media_count,followers_count,follows_count",
                    "access_token": META_IG_ACCESS_TOKEN},
            timeout=TIMEOUT,
        )
        ok = r.status_code == 200
    except requests.RequestException:
        ok = False
    if not ok:
        return _ig_daily_hikerapi()
    prof = r.json()
    reach = None
    try:
        ri = requests.get(
            "https://graph.instagram.com/v21.0/me/insights",
            params={"metric": "reach", "period": "days_28", "metric_type": "total_value",
                    "access_token": META_IG_ACCESS_TOKEN},
            timeout=TIMEOUT,
        )
        if ri.status_code == 200:
            reach = ri.json()["data"][0]["total_value"]["value"]
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        reach = None
    return {
        "followers": prof.get("followers_count"),
        "following": prof.get("follows_count"),
        "media_count": prof.get("media_count"),
        "reach_30d": reach,
        "source": "graph",
    }


def collect_instagram_daily() -> dict | None:
    """Light daily Instagram sample, every read ledger-claimed. Skipped (with the reason) on refusal or failure."""
    try:
        if IG_DAILY_SOURCE == "hikerapi":
            return _ig_daily_hikerapi()
        return _ig_daily_graph()
    except KeyboardInterrupt:
        raise
    except SystemExit as e:  # LedgerRefused and the OpsGate are SystemExit subclasses
        return skipped("ledger refused the Instagram read: %s" % (e.code if e.code is not None else e))
    except Exception as e:
        return skipped(reason_of(e))


def collect_hikerapi_balance() -> dict | None:
    """HikerAPI request balance (not an Instagram read, so no ledger claim)."""
    try:
        bal = _provider().balance()
        if not bal:
            return skipped("HikerAPI balance call returned nothing")
        return {"requests": bal.get("requests"), "balance": bal}
    except Exception as e:
        return skipped(reason_of(e))


# ---------------------------------------------------------------------------
# Collect all platforms
# ---------------------------------------------------------------------------

def collect_all(skip: tuple = ()) -> dict:
    """Run all collectors and return combined results. `skip` leaves platforms out (Instagram
    is a light, ledger-claimed daily sample).

    A platform that could not be read sits in `platforms` as {"skipped": reason} (so the
    snapshot says why), its name is in `errors` and its reason in `skipped`."""
    results = {}
    errors = []
    skips = {}

    for name, fn in [
        ("spotify", collect_spotify),
        ("soundcloud", collect_soundcloud),
        ("youtube", collect_youtube),
        ("instagram", collect_instagram_daily),
        ("hikerapi", collect_hikerapi_balance),
    ]:
        if name in skip:
            continue
        try:
            data = fn()
        except Exception as e:
            data = skipped(reason_of(e))
        if data is None:
            data = skipped("collector returned nothing")
        if isinstance(data, dict) and "skipped" in data:
            errors.append(name)
            skips[name] = data["skipped"]
        results[name] = data

    return {"platforms": results, "errors": errors, "skipped": skips}
