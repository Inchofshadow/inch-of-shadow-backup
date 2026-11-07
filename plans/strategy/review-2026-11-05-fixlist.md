# Strategy review: fix list for stale lines (2026-11-05)

Applied 2026-11-05 by ⚙️ System 69, commit 27ae612 (Status column: done = edited, proposed = line in the socials handover, banner = History banner on the old doc, C = not applied; row 19 and 20 edited on disk, file gitignored). Truth used: `review-2026-11-05-facts.md`
sections 1, 6 and 7, `docs/brand/positioning.md`, `plans/handovers/release/half-the-night-ep.md`.

- Songs are the main line since 2026-09-13, not public yet. Electronic lane continues, same name.
- Next release: Half the Night EP (Half the Night + Pinocchio), slug `pinocchio-single`. Not out
  on 2026-11-06. Date open, early Dec at best, after the Symphonic submit.
- No "3 EPs in 2026". No Beatport for new releases. No label demo waves for electronic tracks.
  Web3 lane dead since 07-11.
- Area emojis: 🎵 Release, 🎬 Socials, 🎧 Booking, 💶 Income, 🎸 Studio, ⚙️ System.

Line numbers are from 2026-11-05. Re-check each line before editing.

## Fix list

| # | File:line | Says now (quote, max 15 words) | Proposed new text (short) | Priority | Status |
|---|---|---|---|---|---|
| 1 | docs/ig-agent-context.md:23 | "Songs (guitars and voice) become the main line from 2027" | Songs (guitars and voice) are the main line since 2026-09-13, not public yet. | A | proposed |
| 2 | docs/ig-agent-context.md:34 | "Next: Pinocchio single (2026-11-06)." | Next: Half the Night EP (Half the Night + Pinocchio). Date open, early Dec at best. | A | proposed |
| 3 | docs/ig-agent-context.md:46 | "release_context.json (currently: Pinocchio, single, 2026-11-06)" | (currently: Half the Night EP, date open). Release framing flexes per release, not per EP. | A | proposed |
| 4 | docs/ig-agent-context.md:29 | "790 -> 1,200-1,500 followers in 6 months (April 2026 -> October 2026)" | Goal: the Nov-Dec rungs in `plans/targets.json` (996 by 30 Nov, 1026 by 31 Dec). | A | proposed |
| 5 | docs/ig-agent-context.md:52 | "Followers \| 790 \| 1,200-1,500" | Mark as April 2026 baseline; point the target column to `plans/targets.json`. | A | proposed |
| 6 | docs/ig-agent-context.md:1009 | "(790 followers, target 1,200-1,500 in 6mo)" | (targets: `plans/targets.json`) | A | proposed |
| 7 | docs/ig-agent-context.md:454-455 | "Techno Trance EP uses set ... Downtempo / Exotic EP uses" | Remove both lines. These EPs are no longer planned. | A | proposed |
| 8 | docs/ig-agent-context.md:604 | "promotion_log.json -- currently farewell-single" | No active campaign now. Check `promotion_log.json`; Farewell is finished. | A | proposed |
| 9 | docs/ig-agent-context.md:12-13 | "plans/strategy/inch-of-shadow-marketing-guide.md (broader marketing context)" | Add: electronic-era docs; Beatport and label-demo parts no longer apply. | A | proposed |
| 10 | docs/ig-engagement-sop.md:17 | "790 -> 1,200-1,500 followers in 6 months ... currently Phase 1 (10 follows" | Goal = `plans/targets.json` rungs. Caps per config (12/16/8 since 11-04). Add the songs lane. | A | proposed |
| 11 | docs/sc-agent-context.md:29-31 | "The 2026 release plan. Three EPs across different styles." | Release plan: songs are the main line (not public). Next electronic release: Half the Night EP, date open. | A | proposed |
| 12 | docs/sc-agent-context.md:33-39 | "EP \| Genre \| Targeting flavor ... flexes with the EP" | Rename to "Genre framings for targeting"; framing flexes per release, not per EP. | A | proposed |
| 13 | docs/sc-agent-context.md:41 | "as of 2026-08-27 the most recent release is The Deceiver" | Add: next is Half the Night EP (Half the Night + Pinocchio), date open, early Dec at best. | A | proposed |
| 14 | docs/sc-agent-context.md:138 | "Currently: farewell-single." | Currently: none active (check the file). | A | proposed |
| 15 | docs/sc-agent-context.md:139 | "Currently: Farewell, EBM/Acid, May 15." | Read the file; next release is the Half the Night EP, date open. | A | proposed |
| 16 | docs/sc-agent-context.md:147 | "Currently active campaign: farewell-single -- targets being pre-warmed include" | Remove the line, or: no active campaign; verify in `promotion_log.json`. | A | proposed |
| 17 | CLAUDE.md:14 | "Stats Dashboard \| Not started" | Stats Dashboard \| Partial \| RM `/stats` + score board (11-01) | A | done |
| 18 | CLAUDE.md:26 | "plans/ — master plan ... (read plans/master-plan.md for full project vision)" | Long-run aim: `docs/brand/positioning.md`. `master-plan.md` is electronic-era history. | A | done |
| 19 | .claude/skills/release-prep/SKILL.md:9 | "Inch of Shadow (dark disco, acid, electro, EBM -- Berlin underground)." | Two lanes: songs (main line, not public yet) and the electronic lane (dark disco, acid, electro, EBM). | A | done |
| 20 | .claude/skills/release-prep/SKILL.md:56-57 | "Beatport (if applicable) ... DJ-focused: groove, texture, energy" | Remove, or: Beatport is not used for new releases; skip unless Amir adds it back. | A | done |
| 21 | .claude/skills/release-prep/SKILL.md:85 | "\"beatport\": { \"description\": \"...\" }" | Drop the beatport key from the example JSON. | C | C, not applied |
| 22 | .claude/skills/promo/SKILL.md:12 | "Labels - demo-safe target curation + per-label hooks (Amir sends via Tool 4)." | Labels: no demo waves for electronic tracks. Song-era label list only, on Amir's call. | A | done |
| 23 | docs/brand/formats.md:10 | "LIGHT = electronic drops (Pinocchio, 2026-11-06)." | LIGHT = electronic drops (Half the Night EP, date open). | A | done |
| 24 | docs/brand/formats.md:152 | "4K to be tried on Pinocchio" | 4K to be tried on the Half the Night EP | C | C, not applied |
| 25 | docs/brand/frame.md:356 | "Pinocchio (2026-11-06) is never shown as released before that date." | The Half the Night EP is never shown as released before its date (open). | A | done |
| 26 | docs/brand/proof.md:105 | "Pinocchio, single, PAUSED (Amir 2026-11-02, was planned 2026-11-06, no new date)" | Half the Night EP (Half the Night + Pinocchio), not out, date open, early Dec at best. | A | done |
| 27 | docs/brand/proof.md:117 | "Spotify, Apple Music, Bandcamp, Beatport, SoundCloud, YouTube, Audius, Catalog." | Check first if Audius and Catalog still carry the catalogue (Web3 lane dead 07-11); drop them if not. | C | C, not applied |
| 28 | docs/brand/kit/references/cover.md:4-5 (twin: ../.claude/skills/brand/references/cover.md) | "Beatport is write-once on the Starter plan: artwork and metadata are 100% final" | Beatport is not used for new releases. The write-once rule applies only if it is added back. | A | done |
| 29 | docs/brand/kit/references/cover.md:25 (same twin) | "plus Beatport 3000, SoundCloud, profile images and thumbnails" | plus SoundCloud, profile images and thumbnails (Beatport 3000 only if it comes back). | C | C, not applied |
| 30 | docs/brand/frame.md:287 | "Bandcamp needs 1400 or more, Beatport prefers 3000" | Bandcamp needs 1400 or more (drop Beatport) | C | C, not applied |
| 31 | plans/curator-pitch-template.md:31 | "(Farewell now; The Deceiver at its release); a one-line tease of the upcoming" | Lead with the newest live track. Never tease the Half the Night EP before its date is set. | A | done |
| 32 | plans/AREAS.md:22 | "📱 Socials, 🎧 Booking, 💰 Income, 🎛️ Studio" | 🎬 Socials, 🎧 Booking, 💶 Income, 🎸 Studio | B | done |
| 33 | plans/bc06-nov6-half-the-night.md:1 | "BC-06: Nov 6 Bandcamp Friday + Listening Party (Half the Night / Pinocchio)" | BC-06: Bandcamp Friday + Listening Party (Half the Night EP, date open) | B | done |
| 34 | plans/bc06-nov6-half-the-night.md:3 | "ICR-003, 2026-11-06, may slide to 2026-11-13" | Not out on 11-06; date open, early Dec at best. Next Bandcamp Friday 2026-12-04. | B | done |
| 35 | plans/bc06-nov6-half-the-night.md:18-19 | "Fri Nov 6, about 09:30 Berlin ... Fri Nov 6, 19:00 Berlin" | Release day or a Bandcamp Friday after it (date open). | B | done |
| 36 | plans/bc06-nov6-half-the-night.md:25 | "Follower message, Fri Nov 6 (draft)" | Follower message, release day (draft) | B | done |
| 37 | plans/bandcamp-traffic-plan-2026-10-21.md:69 | "Nov 6 (Pinocchio day) and Dec 4 follower messages" | Release day of the Half the Night EP (date open) and Dec 4 follower messages | B | done |
| 38 | plans/master-plan.md:1 | (no status line; header "Last updated: 2026-03-24") | Add banner: Electronic-era plan (March). Superseded by bridge plan v2 (09-13) and positioning.md. | B | banner |
| 39 | plans/master-plan.md:112 | "3 EPs planned for 2026." | Delete, or: 2 singles out in 2026; Half the Night EP next, date open. | B | banner |
| 40 | plans/master-plan.md:159, 164 | "Release 3 EPs in 2026." / "3 EPs released on all platforms via Symphonic" | Covered by the banner in #38; or strike through. | B | banner |
| 41 | plans/master-plan.md:209 | "Demo submissions sent to 15-20 aligned labels (filtered from SI by score 4-5)" | No electronic demo waves. Song-era label list is proposed only. | B | banner |
| 42 | plans/master-plan.md:277 | "2026 releases: 3 EPs planned (Dark Disco Acid, Techno Trance, Downtempo/Exotic)" | 2026 releases: Farewell, The Deceiver; Half the Night EP next, date open. | B | banner |
| 43 | plans/project-brief.md:14 | "2026 plan: 3 EPs (Dark Disco Acid, Techno Trance, Downtempo/Exotic)" | Songs are the main line (not public). Electronic: Half the Night EP next, date open. | B | banner |
| 44 | plans/project-brief.md:54, 57 | "Build a professional catalog (3 EPs in 2026)" / "Get label releases" | Add banner: electronic-era brief (March); see positioning.md for current aims. | B | banner |
| 45 | plans/seo-strategy.md:21 | "Beatport \| DJ market, chart potential in niche genres" | Mark: back catalogue only; not used for new releases. | B | done |
| 46 | plans/seo-strategy.md:195 | "## 6. Beatport Strategy" | Add one line under it: not used for new releases (since bridge plan v2). | B | done |
| 47 | plans/seo-strategy.md:245 | "Set Beatport genre/subgenre through Symphonic" | Remove the checklist item. | B | done |
| 48 | plans/release-day-playbook.md:74 | "Web3 uploads -- Nina, Audius." | Remove. Web3 lane dead since 2026-07-11. | B | done |
| 49 | plans/release-day-playbook.md:83 | "T+12-14: Beatport/Traxsource charts check" | T+12-14: rotate Spotify Artist Pick. (no Beatport for new releases) | B | done |
| 50 | plans/release-platform-deadlines.md:31 | "Charts check (Beatport, Traxsource)" | Remove the row. | B | done |
| 51 | plans/release-platform-deadlines.md:63 | "### Beatport" | Add: not used for new releases; kept as reference. | B | done |
| 52 | plans/release-platform-deadlines.md:111-112 | "Label Demo Submissions ... not release-dependent, ongoing" | No demo waves for electronic tracks. Song-era labels only, on Amir's call. | B | done |
| 53 | plans/marketing-campaign-template.md:46 | "Beatport genre/subgenre set: ___" | Remove the checklist item. | B | done |
| 54 | plans/marketing-campaign-template.md:109, 159 | "Beatport: [link]" | Remove from the link blocks for new releases. | B | done |
| 55 | plans/marketing-campaign-template.md:189 | "## Beatport Genre Mapping" | Add one line: reference only, Beatport is not used for new releases. | B | done |
| 56 | plans/ig-engagement-strategy.md:5 | "Grow @inch_of_shadow from 790 -> 1,200+ followers in 6 months" | Mark expired (Oct 2026, unmet). Current goal: `plans/targets.json`. | B | proposed |
| 57 | plans/sync-licensing-plan.md:200 | "EP3 (Downtempo/Exotic) tracks get sync deliverables at release" | Half the Night EP tracks get sync deliverables at release. | B | done |
| 58 | plans/festival-targets-2026-27.md:13 | "Deadlines that are close: TMW on 26 Oct 2026, CTM Vorspiel on 6 Nov" | TMW (26 Oct) and CTM Vorspiel (6 Nov) passed. Open: 48 Stunden Neukölln, 16 Nov to 10 Jan. | C | C, not applied |
| 59 | plans/engagement-log-design-lessons.md:4 | "Catalog, Audius, or whatever replaces Nina in the web3 strategy" | Any new engagement platform (the Web3 lane is dead since 2026-07-11). | C | C, not applied |
| 60 | plans/sync-layer-plan.md:100, 122, 134 | "Charts check ... Beatport, Traxsource" / "beatport_confirm" / "beatport_live" | Note at top: Beatport steps apply to the back catalogue only. | C | C, not applied |
| 61 | plans/release-manager.md:55, 84 | "Beatport (release + profile)" / "7 platforms: ... Beatport ..." | Mark Beatport as back catalogue only. | C | C, not applied |
| 62 | plans/release-day-playbook.md:7 | "When starting the next release, read Parts A-C." | Add: Beatport, Nina and Audius parts no longer apply. | C | C, not applied |
| 63 | plans/seo-strategy.md:4 | "Sound: Dark disco, acid, electro, EBM, techno, slowmo, cinematic" | Add: songs are the main line (not public); this file covers the electronic lane. | C | C, not applied |

Not a doc, so not in the table, but the same stale fact lives there: the data file
`scene_intelligence/release_context.json` (agents read it; facts section 7 also names the
release file's own `release_date`).

## History, leave as is

- `plans/2026-04-23-vs-code-handoff.md`, `plans/2026-04-24-cowork-resume-prompt.md`, `plans/vs-code-session-2026-04-24.md`
- `plans/the-deceiver-*.md` (6 files), `plans/farewell-curator-outreach-tracker.md`
- Marked retired or superseded: `plans/booking-wave1-drafts.md`, `plans/ig-content-craft-reference.md`,
  `plans/sc-automation-session-prompt.md`, `plans/sc-engagement-automation.md`,
  `docs/brand/VIDEO-BRAND-SESSION-KIT.md`, `docs/brand/CONTROL-PANEL-SETUP-ROADMAP.md`
- Logs and trackers: `plans/release-lessons.md`, `plans/ig-content-performance-log.md`, `plans/weekly-stats.md`,
  `docs/ig-session-scorecard.md`, `plans/sc-follow-contacts-2026-11-03.md`, `plans/sc-seed-candidates-2026-08-05-harvest.md`,
  `plans/release-backups-dryrun-2026-11-04.md`, `plans/outreach-prior-contact-audit.md`
- Dated research snapshots: `plans/platform-algorithm-research-2026-06.md`, `plans/platform-algorithm-research-tiktok.md`,
  `plans/groover-submithub-research-2026-06.md`, `plans/api-providers-research-2026-10-15.md`,
  `plans/bandcamp-discovery-research-2026-10-21.md`, `plans/berlin-promoters-2026-10.md`, `plans/fetish-scene-berlin-2026-10.md`,
  `plans/sisyphos-booking-2026-10.md`, `plans/paid-gigs-berlin-2026.md`, `plans/mix-series-research-2026-09-25.md`,
  `plans/mix-series-active-2026-10.md`, `plans/magazine-socials-targets-2026-10.md`, `plans/festival-status-2026-10-21.md`,
  `plans/symphonic-genre-list-2026-11-03.md`, `plans/claude-skills-analysis.md` (03-22 snapshot)
- Session notes: `plans/half-the-night-cover-*.md`, `plans/genre-cover-board-2026-11-03.md`
- `docs/superpowers/**` (dated specs and plans), `docs/boost_reports/**`, `docs/brand/research/**`

## Counts

- Status (commit 27ae612): done 28, proposed 17, banner 7, C not applied 11.

- A (an agent or skill reads it): 26
- B (active plan): 26
- C (minor): 11
- Total: 63
