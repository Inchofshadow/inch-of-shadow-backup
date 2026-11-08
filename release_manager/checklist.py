"""
release_manager/checklist.py
------------------------------
Default checklist template and management functions.

Items can be checked off in any order — no enforced sequence.
"""

from __future__ import annotations

from datetime import datetime


# ---------------------------------------------------------------------------
# Default checklist template
# ---------------------------------------------------------------------------

DEFAULT_CHECKLIST: list[dict] = [
    # Metadata
    {"id": "genre_tags",           "label": "Genre tags decided",                     "category": "metadata"},
    {"id": "credits_confirmed",    "label": "All credits confirmed",                  "category": "metadata"},
    {"id": "isrc_codes",           "label": "ISRC codes (from distributor)",           "category": "metadata"},
    {"id": "upc_code",             "label": "UPC (from distributor)",                  "category": "metadata"},

    # Distribution
    {"id": "account_opened",       "label": "Distributor account opened",             "category": "distribution"},
    {"id": "release_submitted",    "label": "Release submitted to Symphonic",         "category": "distribution"},
    {"id": "distributor_approved", "label": "Distributor approved",                    "category": "distribution"},
    {"id": "bandcamp_setup",       "label": "Bandcamp upload + pre-order live",        "category": "distribution"},

    # Promotion
    {"id": "spotify_pitch",        "label": "Spotify editorial pitch submitted",       "category": "promotion"},
    {"id": "presave_links",        "label": "Pre-save links live",                    "category": "promotion"},
    {"id": "promo_assets",         "label": "Promo assets prepared",                  "category": "promotion"},
    {"id": "blog_premiere_pitch",  "label": "Blog premiere pitches sent",              "category": "promotion"},
    {"id": "early_links",          "label": "Early links sent to personal contacts",   "category": "promotion"},
    {"id": "premiere_live",        "label": "Blog premiere goes live",                 "category": "promotion"},

    # Post-release
    {"id": "dj_promos_sent",       "label": "DJ promos sent (bulk)",                  "category": "post_release"},
    {"id": "platform_links",       "label": "All platform links collected",           "category": "post_release"},
    {"id": "spotify_check",        "label": "Spotify saves / retention check",         "category": "post_release"},
    {"id": "dj_followup",          "label": "DJ promo follow-up",                      "category": "post_release"},
    {"id": "charts_check",         "label": "Charts check (Beatport / Traxsource)",    "category": "post_release"},
    {"id": "artist_pick_rotate",   "label": "Rotate Spotify Artist Pick",              "category": "post_release"},
    {"id": "stats_review",         "label": "Stats review + update SI scores",         "category": "post_release"},
]


# ---------------------------------------------------------------------------
# The fixed format set per single (board ticket Formats-01, Amir 2026-09-20)
# Spec for every object: docs/brand/formats.md; sizes and rules: docs/brand/frame.md.
#   lane "light" = electronic drops. lane "full" = songs: the light set plus the rest.
# A release without a lane (everything made before 2026-09-20) gets none of these.
# ---------------------------------------------------------------------------

FORMAT_CHECKLIST: list[dict] = [
    {"id": "fmt_cover",              "label": "Cover 4000x4000, final before first submission", "category": "formats", "lane": "light"},
    {"id": "fmt_canvas",             "label": "Spotify Canvas, vertical 3-8s loop",             "category": "formats", "lane": "light"},
    {"id": "fmt_process_reel",       "label": "Process reel (about T-4 days)",                  "category": "formats", "lane": "light"},
    {"id": "fmt_release_reel_hooks", "label": "Release reel with 2-3 tested hooks",             "category": "formats", "lane": "light"},
    {"id": "fmt_shorts",             "label": "Both reels posted as YouTube Shorts",            "category": "formats", "lane": "light"},
    {"id": "fmt_story_set",          "label": "Release-day story set (3 frames + link)",        "category": "formats", "lane": "light"},
    {"id": "fmt_reveal_carousel",    "label": "Reveal carousel 1080x1440, face on slide 3",     "category": "formats", "lane": "full"},
    {"id": "fmt_face_reel",          "label": "Face or performance reel",                       "category": "formats", "lane": "full"},
    {"id": "fmt_lyric_reel",         "label": "Lyric reel (release +2 days)",                   "category": "formats", "lane": "full"},
    {"id": "fmt_youtube_visualizer", "label": "YouTube visualizer 4K + plain cover thumbnail",    "category": "formats", "lane": "full"},
    {"id": "fmt_presave_asset",      "label": "Pre-save image (T-14 days)",                     "category": "formats", "lane": "full"},
]

# ---------------------------------------------------------------------------
# The YouTube steps of a release (board ticket Machine-03, 2026-09-21).
# Same ids and order as youtube/tools/yt_release.py, which prints who does each step.
# Rules and reasons: youtube/PLAYBOOK.md sections 5 and 6. Both lanes get all of them.
# ---------------------------------------------------------------------------

YOUTUBE_CHECKLIST: list[dict] = [
    {"id": "yt_render",      "label": "YouTube: main video rendered in 4K",                 "category": "youtube", "lane": "light"},
    {"id": "yt_uploaded",    "label": "YouTube: file dragged into Studio (Amir)",            "category": "youtube", "lane": "light"},
    {"id": "yt_metadata",    "label": "YouTube: title, description, tags, playlists applied", "category": "youtube", "lane": "light"},
    {"id": "yt_thumbnail",   "label": "YouTube: plain cover thumbnail uploaded",             "category": "youtube", "lane": "light"},
    {"id": "yt_premiere",    "label": "YouTube: scheduled + Set as Premiere (Amir)",         "category": "youtube", "lane": "light"},
    {"id": "yt_end_screen",  "label": "YouTube: end screen imported (Amir)",                 "category": "youtube", "lane": "light"},
    {"id": "yt_channel_day", "label": "YouTube: release day on the channel (Amir)",          "category": "youtube", "lane": "light"},
    {"id": "yt_shorts_link", "label": "YouTube: each Short links to the full track (Amir)",  "category": "youtube", "lane": "light"},
]

# ---------------------------------------------------------------------------
# Bandcamp links (ticket BC-04, Amir 2026-10-21). Lane-tagged so only releases
# made from Pinocchio on carry it, not the finished Farewell / The Deceiver.
# ---------------------------------------------------------------------------

BANDCAMP_CHECKLIST: list[dict] = [
    {"id": "bandcamp_campaign_links", "label": "Bandcamp linked with campaign links (SC buy link, YouTube, smart link, Linktree)",
     "category": "post_release", "lane": "light"},
]

LANES = ("light", "full")


def template_for(lane: str | None) -> list[dict]:
    """Checklist template for a lane. No lane = the classic template only."""
    if lane not in LANES:
        return list(DEFAULT_CHECKLIST)
    wanted = ("light",) if lane == "light" else LANES
    extra = FORMAT_CHECKLIST + YOUTUBE_CHECKLIST + BANDCAMP_CHECKLIST
    return list(DEFAULT_CHECKLIST) + [f for f in extra if f["lane"] in wanted]


def expected_ids(lane: str | None) -> set[str]:
    """Ids a release of this lane should carry (used by the web app's auto-migration)."""
    return {item["id"] for item in template_for(lane)}


# ---------------------------------------------------------------------------
# Checklist tooltips (shown on hover in the web UI)
# ---------------------------------------------------------------------------

CHECKLIST_TOOLTIPS: dict[str, str] = {
    "genre_tags":           "Decide primary and secondary genres for each platform (Beatport, Spotify, Traxsource, Bandcamp).",
    "credits_confirmed":    "Verify all credits: producer, mixer, mastering, writer. Legal name for writer (royalty matching).",
    "isrc_codes":           "International Standard Recording Code — assigned automatically by your distributor.",
    "upc_code":             "Universal Product Code — assigned by your distributor for the release.",
    "account_opened":       "Open your distributor account (e.g. Symphonic Starter $19.99/yr).",
    "release_submitted":    "Upload final audio, artwork, and metadata to Symphonic. Ideal 8 weeks, minimum 6 weeks before release.",
    "distributor_approved": "Distributor reviews and approves — usually 5 business days. DSP delivery 1-10 days after.",
    "bandcamp_setup":       "Upload to Bandcamp, set pre-order, enable 1 track preview. Aim for W-3 before release.",
    "spotify_pitch":        "Submit editorial pitch via Spotify for Artists. Best 4 weeks before release. Max 500 chars.",
    "presave_links":        "Generate pre-save links for fans. Distribute via socials and email.",
    "promo_assets":         "Prepare social media posts, teaser clips, press materials.",
    "blog_premiere_pitch":  "Pitch blogs/YouTube channels for exclusive premiere. Aim for W-4.",
    "early_links":          "Send private links to personal contacts / close DJs before public release.",
    "premiere_live":        "Blog/channel premiere goes live (typically day before release).",
    "dj_promos_sent":       "Send promo links to DJs after release to boost streaming. Use Promo Engine press list.",
    "platform_links":       "Collect all store/streaming links once the release goes live on each platform.",
    "spotify_check":        "Check Spotify saves and retention in first 72 hours — critical for algorithmic push.",
    "dj_followup":          "Follow up with DJs who haven't responded to promos after 1 week.",
    "charts_check":         "Check if tracks appear in Beatport or Traxsource charts.",
    "artist_pick_rotate":   "Update your Spotify Artist Pick to feature the new release, then rotate after 2 weeks.",
    "stats_review":         "Review per-platform stats. Update SI contact scores based on who engaged.",
    "fmt_cover":              "Build at 4000x4000 (Apple asks for it). artwork_resizer.py makes every platform size and never upscales. Artwork is final before the first submission.",
    "fmt_canvas":             "Spotify Canvas is vertical 9:16 only, 3 to 8 seconds, no audio. A seamless loop. video_resizer.py --only spotify.",
    "fmt_process_reel":       "Studio or making-of, no announcement. The process reel out-reached the release reel on The Deceiver (455 vs 341).",
    "fmt_release_reel_hooks": "One build, the first 2 seconds swapped as a variable, 2-3 versions run as trial reels, the winner goes out. About 65% of viewers left by 0:02 on The Deceiver.",
    "fmt_shorts":             "Same 1080x1920 files, passed through without re-encoding. Starts our Shorts data.",
    "fmt_story_set":          "Three story frames with the link sticker. The base clicks from stories.",
    "fmt_reveal_carousel":    "Follower depth, not discovery (98% followers, high comments). 3:4 fills the grid tile. Photo carousels cannot carry original audio.",
    "fmt_face_reel":          "Singing or playing, no talking. His portrait out-liked the statues on the reveal carousel.",
    "fmt_lyric_reel":         "The lyrics are the edge. The lyric look is decided on the first one (frame.md, known gaps).",
    "yt_render":      "Drop: the cover video from youtube/tools/render.py (3840x2160, blurred cover behind, lossless sound). Song: the HyperFrames visualizer. Check the artwork against the store cover first.",
    "yt_uploaded":    "Amir drags the file into YouTube Studio. No metadata, do not publish. Never through the API: uploads from an unaudited project get locked private.",
    "yt_metadata":    "python3 youtube/tools/yt_release.py <slug> --draft writes the metadata file; Claude fills the line about the music; then yt_apply.py, dry run first. PREMIERE: yes in the file keeps the script away from the schedule.",
    "yt_thumbnail":   "The plain cover, like the whole channel (Amir, 2026-09-21). Frame grab into thumbnails/covers/, then yt_thumbnails.py --dir thumbnails/covers, dry run first.",
    "yt_premiere":    "Studio: Visibility > Schedule > date, 18:00 > tick Set as Premiere. The API cannot do this. Try the 4K file first; if Studio refuses it, stop and decide: 1080p with a Premiere, or 4K without. No hosted live chat.",
    "yt_end_screen":  "Studio: End screen > Import from video > Save. Drops import from The Cure; songs import from the first song video once there is one.",
    "yt_channel_day": "YouTube's own release-day list: set the video as the channel's featured video, put the release playlist row on top, write a community post with the streaming link, update the banner.",
    "yt_shorts_link": "In each Short's details set Related video = the full track. From release day on, try the official sound from the Shorts audio picker and note what happened.",
    "fmt_youtube_visualizer": "Full song, 16:9, rendered 4K from HyperFrames at delivery quality. Thumbnail: the plain cover, like the rest of the channel (Amir, 2026-09-21). Goes live as a Premiere (Amir ticks 'Set as Premiere' in Studio, metadata file carries PREMIERE: yes). No cards.",
    "fmt_presave_asset":      "Story and post image for the pre-save, two weeks out. Farewell had none.",
    "bandcamp_campaign_links": "Once the Bandcamp page is live: python3 bandcamp_links.py --write, then SC buy link (sc-buy, scene_intelligence/sc_buy_links.py), YouTube description (yt-desc), Hypeddit Bandcamp row 2nd after Spotify (smartlink), Linktree Bandcamp row under Instagram (ig-bio). Instagram stays above Bandcamp.",
}


# ---------------------------------------------------------------------------
# Checklist ID → timeline ID mapping (for auto-linking due dates)
# ---------------------------------------------------------------------------

_CHECKLIST_TO_TIMELINE: dict[str, str] = {
    "genre_tags":           "metadata_filled",
    "credits_confirmed":    "metadata_filled",
    "release_submitted":    "distributor_submit",
    "distributor_approved": "distributor_approved",
    "bandcamp_setup":       "bandcamp_setup",
    "spotify_pitch":        "spotify_pitch",
    "blog_premiere_pitch":  "blog_premiere_pitch",
    "presave_links":        "presave_promo",
    "early_links":          "early_links",
    "premiere_live":        "premiere_live",
    "dj_promos_sent":       "dj_promos_sent",
    "platform_links":       "platform_links",
    "spotify_check":        "spotify_check",
    "dj_followup":          "dj_followup",
    "charts_check":         "charts_check",
    "artist_pick_rotate":   "artist_pick_rotate",
    "stats_review":         "stats_review",
}


# ---------------------------------------------------------------------------
# Generate checklist for a release
# ---------------------------------------------------------------------------

def generate_checklist(
    timeline: list[dict],
    template: list[dict] | None = None,
    lane: str | None = None,
) -> list[dict]:
    """Create checklist items, linking due_date from timeline where IDs match.

    lane "light" or "full" adds the fixed format set (FORMAT_CHECKLIST).
    """
    tmpl = template or template_for(lane)
    # Build timeline lookup
    tl_dates: dict[str, str] = {m["id"]: m["date"] for m in timeline}

    items = []
    for task in tmpl:
        timeline_id = _CHECKLIST_TO_TIMELINE.get(task["id"], "")
        due_date = tl_dates.get(timeline_id, "")
        items.append({
            "id":        task["id"],
            "label":     task["label"],
            "category":  task["category"],
            "done":      False,
            "done_date": "",
            "due_date":  due_date,
            "notes":     "",
        })
    return items


# ---------------------------------------------------------------------------
# Management
# ---------------------------------------------------------------------------

def migrate_checklist(
    existing: list[dict],
    timeline: list[dict],
    lane: str | None = None,
) -> list[dict]:
    """Migrate an old checklist to the new template, preserving done states.

    New items get added with their due dates.  Items no longer in the
    template are dropped only when they carry nothing: an item that is done
    or has notes is kept at the end, so history is never lost (gate review
    2026-11-07: this runs on every release page open and deleted done items).
    """
    done_map: dict[str, dict] = {}
    for item in existing:
        done_map[item["id"]] = {
            "done": item.get("done", False),
            "done_date": item.get("done_date", ""),
            "notes": item.get("notes", ""),
        }

    fresh = generate_checklist(timeline, lane=lane)
    for item in fresh:
        if item["id"] in done_map:
            item["done"] = done_map[item["id"]]["done"]
            item["done_date"] = done_map[item["id"]]["done_date"]
            item["notes"] = done_map[item["id"]]["notes"]
    fresh_ids = {item["id"] for item in fresh}
    for item in existing:
        if item["id"] not in fresh_ids and (item.get("done") or item.get("notes")):
            fresh.append(item)
            fresh_ids.add(item["id"])
    return fresh


def mark_done(checklist: list[dict], task_id: str) -> bool:
    """Mark a checklist item as done. Returns True if found."""
    for item in checklist:
        if item["id"] == task_id:
            item["done"] = True
            item["done_date"] = datetime.now().strftime("%Y-%m-%d")
            return True
    return False


def mark_undone(checklist: list[dict], task_id: str) -> bool:
    """Mark a checklist item as not done. Returns True if found."""
    for item in checklist:
        if item["id"] == task_id:
            item["done"] = False
            item["done_date"] = ""
            return True
    return False


def checklist_progress(checklist: list[dict]) -> tuple[int, int]:
    """Returns (done_count, total_count)."""
    done = sum(1 for item in checklist if item["done"])
    return done, len(checklist)


def overdue_items(
    checklist: list[dict],
    today: str | None = None,
) -> list[dict]:
    """Return checklist items past their due_date that are not done."""
    today_str = today or datetime.now().strftime("%Y-%m-%d")
    return [
        item for item in checklist
        if not item["done"] and item["due_date"] and item["due_date"] < today_str
    ]
