# Tool 2 -- Release Manager

**Location:** `release_manager/` + `artwork_resizer.py` + `video_resizer.py` + `metadata_utils.py`
**Status:** Done
**Last updated:** 2026-03-16
**Purpose:** Central hub for the full release lifecycle. Tracks releases, resizes artwork + video, generates SEO copy, manages timelines/checklists/platform links.

---

## Architecture

**Backend:** 7 Python modules (cli.py, models.py, storage.py, timeline.py, checklist.py, display.py, __init__.py)
**Web UI:** Flask app at localhost:5001 (webapp.py + 8 templates + style.css + app.js)
**Storage:** JSON files in `releases/` (one per release, schema_version 1)
**Run:** `python -m release_manager.webapp`

---

## Pages

- **Dashboard:** release grid with artwork, progress bars, overdue alerts, social links
- **Release detail:** metadata, tracks table, 15-item checklist, 9-milestone timeline, platform links
- **Forms:** create/edit release, add/edit track, platform links
- **Artwork Resizer** (`/artwork-resizer`)
- **Video Resizer** (`/video-resizer`)
- **SEO Copy Generator** (`/seo-copy`)
- **Color Palette** (`/palette`)

---

## Timeline Milestones (weeks before release)

| Week | Milestone |
|------|-----------|
| 8 | Production complete |
| 7 | Artwork ready |
| 6 | Metadata finalized |
| 5 | Distributor submit |
| 4 | Approved |
| 3 | Spotify pitch |
| 2 | Pre-save live |
| 1 | Premieres |
| 0 | Release day |

---

## Artwork Resizer (integrated)

**File:** `artwork_resizer.py`

Converts one master image to 17 platform-optimized exports:
- Spotify (release + profile + banner)
- Apple Music
- Bandcamp (release + avatar)
- Beatport (release + profile)
- SoundCloud (release + banner)
- YouTube (banner + avatar + thumbnail)
- Instagram (post + story)
- Web thumbnail

Features: P3->sRGB color management, focal point cropping (9 points), Lanczos + unsharp mask, EXIF strip, PNG option, metadata embedding (piexif/PngInfo). CLI + web UI.

---

## Video Resizer (integrated)

**File:** `video_resizer.py`

Converts one master video to 9 platform-optimized exports:
- Instagram (reel, story, square post, portrait post)
- YouTube (video, shorts)
- Spotify Canvas (square, vertical)
- TikTok

Features: ffmpeg via imageio-ffmpeg (no system ffmpeg), focal point cropping, trimming, FPS normalization, audio strip for Canvas, metadata embedding. CLI + web UI.

---

## SEO Copy Generator (integrated)

**Files:** `release_manager/seo_copy_generator.py`, `release_manager/seo_platform_specs.json` (858 lines), `plans/seo-strategy.md`

Claude API (claude-haiku-4-5) generates platform-specific SEO copy:
- 7 platforms: Spotify, Apple Music, YouTube, Instagram, Beatport, Bandcamp, SoundCloud
- 3 tones: Authentic / Professional / Hype
- Character counters, one-click copy, token usage display

Metadata embedding via `metadata_utils.py` (piexif JPEG, PngInfo PNG, ffmpeg video). Web UI at `/seo-copy`.

---

## UI/UX Design (integrated)

Berlin underground club aesthetic with polished interactions:
- **Typography:** Space Grotesk headings + Inter body (variable woff2, locally hosted, ~70KB)
- **Effects:** Film grain overlay (8% opacity), vignette, 3 animated ambient light blobs (20-28s drift), glassmorphism nav/sections/modals
- **Cards:** Artwork-dominant with hover glow (8px lift, 6% zoom), gold focus rings, gradient buttons
- **Animations:** CSS counter step numbers on resizer pages, IntersectionObserver scroll reveals, checkbox pop animations
- **Colors:** #080808 bg, #f0f0f0 text, #d4a94e gold accent
- **Responsive:** 768px hamburger nav
- **Accessibility:** `prefers-reduced-motion` disables all animations
- **Palette editor** at `/palette`

---

## Content Calendar (PLANNED -- Extension of RM)

**Purpose:** Plan platform content around release windows. Week-grid view, items linked to releases.

**Platforms:** Spotify, Bandcamp, SoundCloud (core). Others optional.

### Release Timing Guide

| Week | Platform | Action |
|------|----------|--------|
| W-6 | Bandcamp | Upload, set pre-order, enable 1 track preview |
| W-5 | Spotify | Submit editorial pitch (31-40 day window) |
| W-3 | Bandcamp | Send fan update |
| W-2 | Spotify | Pre-save link ready |
| W-1 | SoundCloud | Full track early access (optional) |
| Release day | All | Spotify live, Bandcamp converts, SoundCloud upload |
| W+1 | Spotify | Check saves/retention (first 72h critical) |
| W+2 | Spotify | Rotate Artist Pick |
| Bandcamp Friday | Bandcamp | First Friday of month = zero commission day |

### Planned Features

- Week-grid view (8 weeks, Mon-Sun columns)
- Items: platform, content type, title, release link, status (planned/posted)
- AJAX "Mark posted" toggle
- Auto-suggest calendar items from release date
- Storage: `release_manager/content_calendar.json`
- Routes integrated into Release Manager Flask app

---

## Key Directories

```
release_manager/
  webapp.py              -- Flask app, all routes, port 5001
  seo_copy_generator.py  -- Claude API logic
  seo_platform_specs.json -- platform specs (858 lines)
  models.py              -- release data model
  storage.py             -- JSON file operations
  timeline.py            -- 9-milestone timeline logic
  checklist.py           -- 15-item checklist logic
  cli.py                 -- CLI interface
  display.py             -- terminal display helpers
  __init__.py            -- package init
  templates/             -- 8 Jinja2 templates
  static/
    style.css            -- Berlin club aesthetic
    app.js               -- frontend interactions
    fonts/               -- Space Grotesk + Inter (woff2)
artwork_resizer.py       -- 17 platform artwork exports
video_resizer.py         -- 9 platform video exports
metadata_utils.py        -- shared metadata embedding
releases/                -- one JSON per release
artwork/                 -- source artwork files
resized/                 -- artwork exports
videos/                  -- source video files
resized_video/           -- video exports
```
