# 🎬 Socials: Bandcamp side chat

Written 2026-11-05 by the Bandcamp side chat (under 🎬 Socials). Ranks below Instagram in priority.

## Hard rule

Bandcamp's Acceptable Use Policy bans bots, scripts, scrapers and any automated reading. So: no engine on Bandcamp, no scripted stats reads, no scraping other artists' buyers. Only official tools (Tools page exports, campaign tracking, follower messages, listening parties, discount codes) and `?campaign=` links from `bandcamp_links.py`. Every Bandcamp setting: Amir changes it, or gives a go per change with the old value recorded first. Messages: drafts shown first, Amir sends.

## Where things stand

- Account baseline (read by hand 2026-10-21): 51 followers, 16 mailing-list addresses; all time since 2024-11-16: 2,333 plays, 595 visits, EUR 62.50 from 31 sales. Last 30 days: 49 plays, 20 visits, EUR 2.50. Discover sent 5 visits ever: sales drive placement, outside traffic carries him.
- Done in October: campaign links (BC-07), SC buy links on 9 tracks + Meltscape set (BC-02), YouTube description lines on 6 videos (BC-03), checklist rule (BC-04), stats card from official exports (BC-01), page redesign live (BC-11), Meltscape EP now EUR 4.
- **Half the Night is NOT out on Fri 11-06.** Per the Release handover (11-05): cover not final, nothing submitted on Symphonic, release date open (about 3-4 weeks out). So no pre-order page, and no listening party tomorrow. The 10-21 plan for Nov 6 (`plans/bc06-nov6-half-the-night.md`) assumed release day; it needs a new shape.
- Next 3-monthly export routine: about 2027-01-21 (raw data report + mailing list; Claude files and parses).

## Open decisions (Amir)

1. **Bandcamp Friday Nov 6 (tomorrow, 09:00 Fri to 08:59 Sat Berlin):** send a short catalogue message to followers anyway (no new release), or skip and save the follower message for Dec 4. Claude drafts, Amir sends.
2. **Discography bundle (🎬 Socials 17):** turning it on notifies ALL followers. Was planned for Nov 6 so it would include Half the Night. Options: turn it on tomorrow with the current catalogue (the notice lands on Bandcamp Friday), or wait until Half the Night is public.
3. **Listening party:** moves to Half the Night release day, or Dec 4 if the release lands near it. Needs the pre-order public first.
4. **Supporter names (🎬 Socials 18):** waiting for Amir's hand-read names from 3-5 similar releases.

## Key files

- Plans: `plans/bandcamp-traffic-plan-2026-10-21.md`, `plans/bandcamp-discovery-research-2026-10-21.md`, `plans/bc06-nov6-half-the-night.md` (Nov 6 draft, now out of date on the release), `plans/bc04-hand-changes.md` (reference only, not to be raised again).
- Code: `bandcamp_links.py` (campaign links, CLI `--write`), `stats/bandcamp_import.py`, `scene_intelligence/bandcamp_supporter_match.py`, `release_manager/checklist.py` (BANDCAMP_CHECKLIST).
- Data (main checkout, gitignored): `data/bandcamp/` (exports, mailing list, design/link-order/prices records). Supporter intake `data/bandcamp/supporter-notes.md`, output `supporter-candidates.json`.
- Release: `releases/pinocchio-single.json` (Half the Night EP, slug `pinocchio-single`); Release handover `plans/handovers/release/half-the-night-ep.md`.
- Design: `artwork/edits/bandcamp-page-bc11/` (live header, undo files).

## Linked tickets

| Ticket | Old id | Status | Who acts |
|---|---|---|---|
| 🎬 Socials 14 · Bandcamp Friday messages + listening party | BC-06 | in-progress | Amir decides Nov 6 shape; Claude drafts; Amir sends |
| 🎬 Socials 17 · Pricing and bundles (discography bundle left) | BC-09 | in-progress | Amir (bundle switch) |
| 🎬 Socials 18 · Supporter names matched to IG/SC | BC-10 | in-progress | Amir reads names; Claude matches |
| 🎬 Socials 13 · Page basics (location, featured track, tags) | BC-05 | proposed | Claude checklist; Amir applies |
| 🎬 Socials 16 · Bandcamp labels/curators in outreach | BC-08 | proposed | Claude, via /outreach |

Done (reference): 🎬 Socials 9 stats exports (BC-01), 10 SC buy links (BC-02), 11 YT descriptions (BC-03), 12 link order + checklist (BC-04), 15 campaign links (BC-07), 19 page redesign (BC-11).

## Ticket updates (for the System chat to merge)

- 🎬 Socials 14 (BC-06): note "2026-11-05: Half the Night not released on 11-06 (cover not final, Symphonic not submitted). Nov 6 = Bandcamp Friday without a release; party moves to release day. blocked_on stays."
- 🎬 Socials 17 (BC-09): note "2026-11-05: bundle timing open again, Half the Night will not be public on 11-06."
