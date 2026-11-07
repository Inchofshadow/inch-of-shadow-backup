# Release Sync Layer — Implementation Plan
# Last updated: 2026-03-17

## What We're Building

A release context layer that connects all tools around a single release.
When you set a genre in RM, Scene Intelligence re-ranks automatically.
When you set a release date, the full platform deadline calendar generates.
When you mark a checklist item done, downstream alerts fire.

No new app. Everything integrates into the existing Flask RM.

---

## Current State (what already exists)

| What | File | Status |
|---|---|---|
| Release schema with genre_primary / genre_secondary | models.py | Done |
| Timeline with 9 milestones | timeline.py | Done |
| Checklist with 15 items | checklist.py | Done |
| SEO copy generator reads genre | seo_copy_generator.py | Done |
| Promotion Engine UI shell | templates/promotion.html | Shell only — no backend contact logic |
| Engagement page | templates/engagement.html | Done (separate system) |
| Scene Intelligence contacts | scene_intelligence/enriched_contacts.json | 920 contacts, genre_sub field |

Key gap: **nothing connects genre_primary → SI contacts → Promotion Engine.**
The Promotion Engine page exists but shows zero contacts — no backend logic yet.

---

## What We're Adding: 3 Modules

---

### Module 1 — Contact Bridge
**File:** `release_manager/contact_bridge.py`
**Purpose:** Given a release's genre, return filtered + ranked contacts from SI.

#### Logic
1. Load `scene_intelligence/enriched_contacts.json`
2. Map release genre to SI genre keywords:
   - EBM → matches genre_sub containing "EBM", "Industrial", "Cold Wave"
   - Acid → matches "Acid", "Techno", "Minimal"
   - Dark Disco → matches "Dark Disco", "Darkwave", "Disco", "Nu-Disco"
   - Electro → matches "Electro", "Electro-Industrial"
   - Techno → matches "Techno", "Minimal Techno"
   - (expandable — stored as a JSON config file)
3. For each contact: calculate `release_match_score` (0-10) based on:
   - Base: existing `match_score` (1-5) from SI
   - Bonus: genre_sub contains one of the mapped keywords (+3)
   - Bonus: contact is in Rekordbox library (+2)
   - Bonus: contact location = Berlin/DE/EU (+1)
   - Penalty: discogs_last_year < 2023 or soundcloud no tracks (-2)
4. Return contacts sorted by release_match_score, grouped by category:
   - DJs (top targets for promos)
   - Labels (top targets for demos)
   - Media (blogs, channels, radio — premieres)
   - Promoters / Venues

#### New API route
`GET /api/release/<slug>/contacts?category=dj&limit=20`
Returns JSON list of top contacts for that release + category.

#### Integration point
Promotion Engine page — when you select a release from the dropdown,
JavaScript calls this API and renders the contact list.
No page reload needed.

---

### Module 2 — Content Calendar
**File:** `release_manager/content_calendar.py`
**Template:** `release_manager/templates/calendar.html`
**Route:** `/release/<slug>/calendar`

#### What it generates
Given release_date, it produces a week-by-week + post-by-post schedule:

| Date | Platform | Content Type | Optimal Time | Notes |
|---|---|---|---|---|
| release_date - 42 days | — | Submit to Symphonic | — | Critical path start |
| release_date - 42 days | Instagram | Studio/process teaser | Story, any time | Week -6 |
| release_date - 35 days | — | Send DJ promos | — | Score 4-5 DJs only |
| release_date - 28 days | — | Pitch blog premieres | — | 3-4 weeks out |
| release_date - 28 days | Spotify | Editorial pitch window opens | — | After Symphonic delivers |
| release_date - 21 days | Instagram | Artwork reveal | Thu 9am feed post | |
| release_date - 21 days | Instagram | Pre-save link live | Story with link sticker | |
| release_date - 21 days | SoundCloud | Upload teaser clip | — | Free preview |
| release_date - 14 days | Instagram | Audio snippet reel | Wed 6pm | 15-30 sec |
| release_date - 14 days | Instagram | Countdown sticker Story | Evening | |
| release_date - 14 days | — | Confirm premiere with blog | — | Deadline |
| release_date - 7 days | Instagram | Behind the scenes | Story series | |
| release_date - 7 days | Instagram | "Dropping Friday" post | Thu 9am | |
| release_date - 1 day | Instagram | Premiere live — tag blog | Story + Feed | |
| release_date (Friday) | ALL | Release day | 9am local | Spotify, Bandcamp, etc |
| release_date (Friday) | Instagram | Release post | Thu 11pm or Fri 9am | |
| release_date (Friday) | Instagram | Platform links Story | Morning | |
| release_date + 7 days | Instagram | Engagement / thank you | Story | |
| release_date + 14 days | — | Charts check | — | Beatport, Traxsource |
| release_date + 28 days | — | Stats review + score update | — | Update SI contact scores |

#### Bandcamp Friday flag
If release_date is within 7 days of a Bandcamp Friday → show banner:
"Consider shifting to [date] — it's a Bandcamp Friday (zero commission)."

#### Output format
- Rendered as a grid in the browser (calendar view by week)
- Exportable as a simple text/markdown checklist
- Each item has a "done" checkbox (stored in release JSON under `content_calendar`)

---

### Module 3 — Enhanced Timeline + Checklist
**Files:** `timeline.py`, `checklist.py` (additions only, no breaking changes)

#### New timeline milestones (added to DEFAULT_TIMELINE)
| id | label | weeks_before |
|---|---|---|
| symphonic_submit | Submit to Symphonic | 6 |
| dj_promos_send | Send DJ promos (score 4-5) | 6 |
| beatport_confirm | Beatport/Traxsource confirmed live | 3 |
| blog_premiere_pitch | Pitch blog/channel premiere | 4 |
| presave_campaign | Pre-save campaign + Instagram tease | 3 |
| bandcamp_live | Bandcamp live (D2F window) | 1 |

#### New checklist items
| id | label | category |
|---|---|---|
| symphonic_submitted | Submitted to Symphonic | distribution |
| dj_promos_sent | DJ promo copies sent (score 4-5) | promotion |
| blog_pitched | Blog/channel premiere pitched | promotion |
| presave_live | Pre-save link live on all socials | promotion |
| beatport_live | Beatport/Traxsource confirmed live | distribution |
| bandcamp_published | Bandcamp page published | distribution |

#### Smart alerts (in release_detail route)
When checklist item is marked done, check:
- `symphonic_submitted` done → show: "Spotify pitch window opens in ~7-10 days. Come back to pitch."
- `distributor_approved` done → show: "Pitch Spotify NOW — you're in the window. Go to Spotify for Artists."
- `release_date` is a Friday? → green. Not a Friday? → yellow warning.
- Release date < 6 weeks away AND symphonic_submitted not done? → red alert.

---

## What Stays the Same

- All existing routes and data structures unchanged
- No database — still JSON files
- Release JSON schema gets 2 new optional fields:
  - `content_calendar: []` — stores done states for calendar items
  - `promo_log: []` — stores contact outreach history (moved from promotion_log.json to per-release)

---

## File Changes Summary

| File | Change |
|---|---|
| `release_manager/contact_bridge.py` | NEW — genre → SI contact filtering |
| `release_manager/content_calendar.py` | NEW — release date → post schedule |
| `release_manager/templates/calendar.html` | NEW — calendar view |
| `release_manager/timeline.py` | ADD 6 new milestones |
| `release_manager/checklist.py` | ADD 6 new items + smart alert logic |
| `release_manager/webapp.py` | ADD /api/release/<slug>/contacts route, /release/<slug>/calendar route, smart alert rendering |
| `release_manager/templates/promotion.html` | UPDATE — wire contact list from API |
| `release_manager/templates/release_detail.html` | UPDATE — smart alerts panel |

---

## Build Order

1. `contact_bridge.py` — the core of the sync layer, most valuable
2. Timeline + checklist additions — small changes, immediate value
3. Smart alerts in release_detail — wires checklist → warnings
4. Content calendar — most visible, needs content_calendar.py + template
5. Promotion Engine contact list — wires contact_bridge into UI

---

## Out of Scope for This Phase

- Scheduled SI refresh (separate Cowork scheduled task — simple to add after)
- Email sending (Tool 4 — separate project)
- Stats dashboard (Tool 5 — needs live release data first)
- Rekordbox → scoring boost (nice to have, add to contact_bridge v2)
