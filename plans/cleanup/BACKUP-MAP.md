# Backup map - Inchofshadowcode (2026-11-05, read-only scan)

The whole folder is 2.55 GB. Git tracks only 38 MB of it (code, docs, plans, SI data).
The other 2.5 GB is media and exports that git already ignores.
Nothing below changes the Mac copy. GitHub = an extra copy only.

## 1. Up to GitHub, readable (code + text without people data)

| Folder | Tracked | Notes |
|---|---|---|
| scene_intelligence (74 .py + configs/reports) | part of 11.3 MB | SI code: enrich, discovery, push_to_sheets, IG/SC engines |
| release_manager | 1.5 MB | Flask app (1 file with an email, goes to 2) |
| plans/control-panel | 4.5 MB | board, no people data |
| plans (other), docs | ~9 MB | text minus the files listed in 2 |
| stats_snapshots, tests, gap_radar, root scripts | ~2.5 MB | tests: 10 files with emails, goes to 2 |

## 2. Up to GitHub, LOCKED (encrypted, only this Mac can read)

Files with other people's emails, phones or handle lists. About 160 tracked files.

| Folder | Files with emails/phones | Biggest |
|---|---|---|
| scene_intelligence (SI data) | 14 + people lists | enriched_contacts 2.5 MB, engagement_log 1.7 MB, ig_target_list 1.2 MB, contact_index, sc/ig_follow_tracker, ig_enriched_contacts, raw_contacts, promotion_log, booking_targets, ig_follower_roster, label_tiers |
| scene_intelligence/backups (97 tracked) | 34 | old sweep copies |
| plans/outreach-page | 55 | outreach research + batches |
| plans (root) | 23 | sc-follow-contacts, sc-sweep, outreach-batches |
| docs | 18 | reports naming contacts |
| tests, releases, release_manager, root | 16 | fixtures, release JSONs |

The SI master Google Sheet (invite-only) already holds a second copy of the main SI contacts.

## 3. NOT on GitHub - too big / media (needs Dropbox, iCloud or a drive)

| Folder | Size | What |
|---|---|---|
| data | 929 MB | IG/YouTube/SC exports, incl. private DMs |
| artwork | 711 MB | cover sources and builds |
| generated_images | 235 MB | AI renders + prompts (local-only by rule) |
| music-tools | 224 MB | incl. Serum backups (restore source) |
| docs (media part) | 227 MB | images/video inside docs |
| references | 58 MB | Shadow Archive images |
| scene_intelligence/backups (archives) | 46 MB | 18 dated SI archives (.tar.gz) |
| scene_intelligence (session plans etc.) | 18 MB | per-session files, regenerated |
| videos, EPK, brand, styled | 58 MB | media |

## 4. NEVER on GitHub

### 4a. Secrets (never leave the Mac)
`.env`, `credentials.json`, `youtube_token.json`, `.sc_user_token.json`, `.sc_browser_state.json` (SoundCloud login cookies), `.flask_secret`. All already ignored by git.
Scan 11-05: no other real keys in the working tree. Hits were image data (outreach-page/images.json) and code/docs that only name the `oauth_token` cookie.

### 4a+. Private DM messages - NEVER (Amir 2026-11-05: "just dont upload personal dm msgs there, only info")
- `data/instagram-*/your_instagram_activity/messages/` in all 4 exports that have one (Feb, Apr, Jun, Aug; 219 MB). The rest of each export (followers, following, likes, info) goes up, locked.
- `plans/voice-study/my-english-dm-lines.json` (raw DM lines).
- `plans/voice-study/amir-dm-voice.md` is INFO (his DM style rules) and goes up, locked.

### 4b. NOT never - these go to GitHub too (Amir 2026-11-05: "all can go", they do not need to be on the never list)
N2 and N3 hold private DMs, so they go LOCKED. The rest plain. No file in them is over 50 MB, so GitHub's 100 MB file limit is fine; together they add ~1.4 GB.
| # | What | Size | First reason given for "never" (overruled) |
|---|---|---|---|
| N1 | `docs/brand/fonts/trials/` (8 foundry trial / personal-use packs) | 208 MB | licences forbid passing them on; already git-ignored |
| N2 | `plans/voice-study/amir-dm-voice.md` (tracked) + `my-english-dm-lines.json` | 0.4 MB | his own private DM lines and voice study |
| N3 | `data/` IG exports (DMs inside `messages/inbox`) | 929 MB | private conversations; drive backup only, no cloud |
| N4 | `generated_images/` | 235 MB | AI prompts + release concepts, local-only by earlier rule |
| N5 | 36 `scene_intelligence/session_plan_*.json`, `.playwright-mcp`, `.superpowers`, `__pycache__` | ~25 MB | regenerated or cache, no value in a backup |
| N6 | `scene_intelligence/backups/sweep-20260831/` (97 tracked) | 1.7 MB | old copies from the 08-31 sweep; the current files and the 18 tar archives already hold this |

## Notes

- The `_worktree_removal_backup_20260609` folder no longer holds an `.env` copy (checked); the .gitignore comment about it is outdated.
- SI engagement files have uncommitted changes from the live runs; a snapshot takes them as they are and does not commit or touch the engagement code.
- Old git history (DM lines, March contact backups, the IP) does not go up in any option.
