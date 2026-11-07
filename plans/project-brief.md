# Inch of Shadow -- Project Brief

> **History (2026-11-05).** Electronic-era document from March 2026, kept as background: songs are the main line since 2026-09-13, no 3 EPs, no Beatport for new releases, next release Half the Night EP (date open).
> Current truth: `plans/strategy/refresh-page/` and `plans/strategy/review-2026-11-05-facts.md`.

**For use in any Claude session (web, mobile, API) -- copy-paste or upload this file.**
**Last updated:** 2026-03-16

---

## Who

**Amir / Inch of Shadow** -- Berlin-based electronic music producer. Dark disco, acid, electro, EBM, techno, slowmo, cinematic, melancholic. Producer, mixer, mastering engineer, writer (all self). Both DJ sets and live performance.

**Distributor:** Symphonic Starter ($19.99/yr) -- active since March 2026
**Labels:** MM Discos, Stereo Society, NaNa Disc
**2026 plan:** 3 EPs (Dark Disco Acid, Techno Trance, Downtempo/Exotic)

## Platforms

Instagram, Spotify, Apple Music, Bandcamp, Beatport, YouTube, SoundCloud, Resident Advisor, Traxsource, Audius, Catalog

## The Project

Personal music platform -- Python tools automating the full release lifecycle from research to stats. Local-first, privacy-first, no database (JSON + Google Sheets), Flask web UI. All code lives at `/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode`.

**The big goal:** Accelerate Inch of Shadow's career from local Berlin presence to a recognized name in the underground electronic scene. More releases, more followers, more gigs, more income, more opportunities -- faster than doing it all manually. The tools eliminate friction between finishing a track and getting it heard, bought, and played.

## Tools (current state)

| # | Tool | Status |
|---|------|--------|
| 1 | **Scene Intelligence** -- 920 contacts, 6 data sources, 4 enrichment APIs (Discogs, SoundCloud, Spotify, YouTube), Google Sheets output | Partial |
| 2 | **Release Manager** -- artwork resizer (17 exports), video resizer (9 exports), SEO copy generator (Claude API, 7 platforms), dark-themed Flask UI | Done |
| 3 | **Promotion Engine** -- playlist pitching, press kit generation | Not started |
| 4 | **Email Outreach** -- templates, tracking, SMTP, contact list from SI | Not started |
| 5 | **Stats Dashboard** -- Spotify/Bandcamp/SoundCloud stats aggregation | Not started |

## Key Decisions

- **Google Sheets is the central database** for all contact/industry data across tools
- **Privacy first:** no data sent to third-party services without explicit approval. Always inform before using external APIs.
- **Security:** no OWASP top 10 vulnerabilities, all API keys in `.env` only
- **Python 3.9+**, Flask, JSON storage, imageio-ffmpeg for video
- **No emojis** in code or output unless requested

## What Amir Prefers

- Concise communication, no fluff
- Flag data quality issues before proceeding
- Privacy and security are critical -- always explain external services before using them
- Prefers working through Claude, not terminal directly

## Career Goals (priority order)

0. **Grow audience and revenue** -- followers, streams, sales across all platforms. The metric that unlocks everything else
1. Build a professional catalog (3 EPs in 2026)
2. Get DJ support from score 4-5 contacts in SI
3. Secure media coverage and premieres
4. Get label releases (1-2 signed, rest self-released)
5. Sign with management
6. Secure booking agency and regular gigs
7. Play festivals (summer 2027 target)

## For Detailed Context

These files in the project have full details:
- `CLAUDE.md` -- project instructions, architecture, rules
- `plans/master-plan.md` -- vision, career goals, technical phases
- `plans/scene-intelligence.md` -- SI pipeline, contacts, scripts, enrichment stats
- `plans/release-manager.md` -- RM architecture, sub-tools, UI/UX
- `plans/seo-strategy.md` -- platform SEO strategy
- `plans/marketing-campaign-template.md` -- release campaign template
