# Inch of Shadow — Project Instructions

## What This Is
Personal music platform for Inch of Shadow, a Berlin artist. Two lanes under one name: songs (the main line since 2026-09, not public yet) and the electronic lane (dark disco, acid, electro, EBM, the released catalogue). Brand source: `docs/brand/README.md`. Five tools automating releases, research, promotion, and stats. All Python, all local-first.

## Tools

| # | Tool | Status | Location |
|---|------|--------|----------|
| 1 | Scene Intelligence Engine | Partial | `scene_intelligence/` |
| 2 | Release Manager | Done | `release_manager/`, `artwork_resizer.py`, `video_resizer.py`, `metadata_utils.py` |
| 3 | Promotion Engine | Not started | — |
| 4 | Email Outreach Manager | Not started | — |
| 5 | Stats Dashboard | Partial | RM `/stats` + score board (11-01) |

## Key Directories
- `artwork/` — source artwork files
- `resized/` — artwork exports (24 platform specs, 22 files; release cover 4000px, never upscaled)
- `videos/` — source video files
- `resized_video/` — video exports (10 platform presets; passthrough when the source already fits; 1440p/4K for YouTube only from a source that large)
- `releases/` — one JSON per release
- `release_manager/` — Flask web UI (webapp.py, 8 templates, static/)
- `release_manager/seo_platform_specs.json` — platform SEO specs (character limits, fields, best practices)
- `plans/` — plans and strategy docs. Long-run aim: `docs/brand/positioning.md`; `plans/master-plan.md` is electronic-era history (March 2026)
- `scene_intelligence/` — ZIP extract → enrich → Google Sheets pipeline
- `data/` — raw ZIP exports (Instagram, YouTube, ChatGPT)

## Architecture
- **Web UI:** Flask app at `release_manager/webapp.py`, run with `python -m release_manager.webapp`
- **CLI tools:** `artwork_resizer.py`, `video_resizer.py` (also integrated into web UI)
- **Video encoding:** Uses `imageio-ffmpeg` bundled ffmpeg binary (no system ffmpeg needed)
- **Storage:** JSON files in `releases/`, no database
- **Sheets integration:** `gspread` + `google-auth` for Scene Intelligence

## Scope Discipline (Amir, 2026-09-29, super important for the ticket system)
- Do exactly what was asked, nothing more: no extra features, files, installs, PRs or side fixes.
- If a request or ticket turns out bigger than it sounded, stop, list 2-3 options in a few lines, and ask first.
- Anything noticed outside the scope is one line in the reply or a proposed ticket, never done silently.
- Bulk file jobs (rename, move, delete): dry run first. Write a list of old path, new path and reason, with unsure items on a REVIEW list. Wait for Amir's yes, then run it, check it, and leave an undo script. Only the folder he named.

## Temporary Files Rule (Amir, 2026-10-24)
Research, cloning and reference work leave NO raw downloads behind.
- Save text only: extract what the job needs (contacts, facts, notes) into our own files (JSON/MD). Never store raw web pages (.html) with their scripts; use a text extractor (firecrawl `--only-main-content`, or strip every `<script>`/`<iframe>` before saving).
- Scratch folders (`scratch-*`, downloads, cloned repos, other artists' files fetched for reference) are temporary: at the END of the run, once the results are saved in our own data, move them to the Trash (never `rm`) and say so in the reply.
- What stays: our own extracted results and anything Amir chose to keep on purpose (e.g. Shadow Archive references).
- Tool: fetch pages with `python3 fetch_text.py URL [--links] [-o notes.md]`. It strips scripts/iframes, keeps text + links + emails, refuses non-public addresses, and never writes HTML.
- Unknown or new sites are opened only as text (fetch_text, WebFetch) or in the separate built-in browser pane. Amir's Chrome profiles (logged into SoundCloud, Instagram, Gmail) are for those accounts and sites we already know, never for browsing unknown pages.
- Check: `python3 hygiene_check.py` (read-only) lists leftover scratch folders, saved pages with scripts (WARN) and remote-code loaders (RED). It runs in the 1st/15th maintenance.
- Why: 2026-10-21 outreach research left 143 raw pages in `plans/outreach-page/research-organisers/scratch-*`; two (inverted-audio.com) carried a hacked remote-code script. Removed 2026-10-24.

## Non-Negotiable Rules
- ALL API keys in `.env` only — never hardcoded
- `.env` always in `.gitignore`
- Output folders auto-created if missing

## Security
- Code must be secure: no command injection, no XSS, no SQL injection, no OWASP top 10 vulnerabilities
- Sanitize all user input at system boundaries
- Never expose API keys, credentials, or internal paths to the client

## Privacy and Third-Party Services
- Privacy first: no data sent to third-party services without explicit approval
- No external APIs that log or store user data
- Prefer local/self-controlled solutions over hosted services
- **Important:** When a tool could be upgraded using an external service or API, always inform the user first. Explain what the service does, what data it would send, what it costs, and any privacy implications. Let the user decide.

## API Keys (in .env)
SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, DISCOGS_TOKEN, GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEETS_ID, ANTHROPIC_API_KEY, YOUTUBE_API_KEY, SOUNDCLOUD_CLIENT_ID, SOUNDCLOUD_CLIENT_SECRET

## Coding Conventions
- Python 3.9+ (system Python on macOS)
- No emojis in code or output unless user requests
- Flag mediocre search/data quality issues before proceeding
- Confirm working directory before creating files

## Dependencies (requirements.txt)
Pillow, piexif, pdfminer.six, gspread, google-auth, python-dotenv, requests, imageio-ffmpeg, anthropic, Flask, beautifulsoup4

## Repo Publication Rule (2026-08-31, Amir)
This repository is LOCAL-ONLY and must never be given a remote or pushed
anywhere without a full git-history scrub first: the history contains
personal data (an IP address, redacted from the working tree on 2026-08-31
but still present in past commits; private-contact notes; profile emails).
No session may add a remote or push on its own judgment.
Exception (Amir, 2026-11-06/07): the no-history backup snapshot in
`~/Backups/inch-of-shadow-github` (built by `plans/cleanup/backup_snapshot.py`:
contacts encrypted, no secrets, no DMs) is pushed to the private repo
Inchofshadow/inch-of-shadow-backup with its deploy key, weekly by the
`github-backup-weekly` task. That snapshot only, never this repo.
