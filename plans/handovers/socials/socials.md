# 🎬 Socials: parent chat

Written 2026-11-05 by the 🎬 Socials parent chat. Covers Instagram, SoundCloud, YouTube, Bandcamp.

## How Socials works (Amir, 2026-11-05)

- Side chats, one per platform: 🎬 Instagram, 🎬 SoundCloud (main folder, live data), 🎬 YouTube, 🎬 Bandcamp (own worktrees). Handovers: `ig-agent.md`, `sc-agent.md`, `youtube.md`, `bandcamp.md`.
- Every ticket is named with its platform and topic, e.g. "🎬 Socials 29 · SoundCloud inbox replies", never a bare number.
- **Max 3 tickets in 🔥 Now for all of Socials.** Side chats bring up only their Now ticket, plus one line "+N parked". ⏭️ Next waits for a free Now slot. 🅿️ Parked comes back only when Amir asks. 🔁 Routine is run by automation or the calendar and is never listed.
- Every open ticket is flagged: **🙋 Amir decides** (the work waits on him) or **🎃 Claude goes** (Claude works on it until the named blocker, then asks).
- **🌐 = the work happens in Amir's Chrome** (Claude in Chrome, inch_of_shadow profile, or Amir clicking himself). Chrome is one shared browser: only one 🌐 job at a time, never during the automation windows below, and Chrome must be open and on screen. Tickets without 🌐 run on files and APIs (HikerAPI, SoundCloud API) and can run in parallel.
- **Chrome busy windows (automation, Berlin time):** SC session 10:00 (about 1 h), SC retry 13:00 (only if 10:00 did nothing), IG session 15:00 Mon/Wed/Fri/Sat (about 1 h), SC sweep 16:15 (until Fri 11-06), Spotify for Artists read Mon 08:00. Plan 🌐 tasks outside these.
- **Every evening, when the digest arrives, the parent chat draws the SoundCloud ratio graph under it** (Amir 11-06): followers / following per day from `stats_snapshots/snapshot_*.json` (soundcloud), since 2026-09-26, with the 1:1 floor (dashed) and the targets as FUTURE points, not a band over the past (Amir 11-06): x-axis runs to Dec 31, a dotted path from today's ratio to the Dec 31 target 1.2; the Aug 2027 target 1.4-1.6 shows as a card. The digest ends with the cue line "📈 SC ratio graph below".
- **Start pings** (Amir 11-06): the IG session, SC session, SC retry (only when it runs) tasks each post "▶️ <run> started HH:MM" into this chat right after their gates pass (START PING line in their SKILL.md; backups SKILL.md.bak-20261106). At the end they post "🏁 <run> finished HH:MM" plus their short report (FINISH REPORT line, Amir 11-06). New IG/SC session tasks get the same lines; SC sweeps get no ping (Amir 11-06).
- Daily digest at about 20:00 posts into the parent chat (`stats/socials_digest.py`, task `socials-daily-digest`). Format A, blank lines between lines, YouTube/Bandcamp only when something ran there, one goals line, one Now line.

## Priority list (Amir approved 2026-11-05)

| | Ticket | Who | 🌐 | Next step / blocker |
|---|---|---|---|---|
| 🔥 | 🎬 Socials 14 · Bandcamp Friday | 🙋 Amir |  | Claude drafts the catalogue message now; Amir decides send (Nov 6) or skip to Dec 4, and sends it himself |
| 🔥 | 🎬 Socials 29 · SoundCloud inbox replies | 🎃 Claude | 🌐 | Claude re-reads the 9 threads and writes fresh drafts; blocker: Amir picks which to send |
| 🔥 | 🎬 Socials 27 · Instagram like list refresh | 🎃 Claude |  | Claude checks the scene like targets and proposes a fresh list; blocker: Amir OKs the list before it goes into the engagement data |
| ⏭️ | 🎬 Socials 23 · Instagram scene-fit score | 🎃 Claude |  | Already approved; build it inside the 300/day HikerAPI cap; blocker: first scored batch shown to Amir |
| ⏭️ | 🎬 Socials 21 · Instagram profile checks 15 → 6 | 🎃 Claude |  | Already approved, the pool is 39 (30+ condition met); blocker: none, report the change |
| ⏭️ | 🎬 Socials 2 · YouTube login renewal | 🙋 Amir | 🌐 | Amir runs the login and clicks Allow, around Nov 13 before the stats snapshot |
| ⏭️ | 🎬 Socials 17 · Bandcamp discography bundle | 🙋 Amir | 🌐 | Amir decides when to switch it on (it notifies all followers); waits for the Half the Night date |
| 🅿️ | 🎬 Socials 1 · Instagram reciprocator review | 🙋 Amir |  | Decide whether the sweep keeps skipping reciprocators |
| 🅿️ | 🎬 Socials 4 · Instagram data export | 🙋 Amir | 🌐 | Amir pulls the All-time export |
| 🅿️ | 🎬 Socials 13 · Bandcamp page basics | 🎃 Claude | 🌐 | Claude writes the checklist; blocker: Amir applies it on Bandcamp |
| 🅿️ | 🎬 Socials 16 · Bandcamp outreach | 🎃 Claude |  | Claude researches labels/curators; blocker: Amir reviews the batch |
| 🅿️ | 🎬 Socials 18 · Bandcamp supporter names | 🙋 Amir | 🌐 | Amir reads names from 3-5 similar releases |
| 🅿️ | 🎬 Socials 28 · SoundCloud SOP rule | 🙋 Amir |  | Amir OKs the wording in `sc-agent.md` |
| 🔁 | 🎬 Socials 5 · SoundCloud maintenance | 🤖 auto |  | 1st/15th maintenance run |
| 🔁 | 🎬 Socials 6 · Instagram data refresh (120d) | 🤖 auto |  | Calendar |
| 🔁 | 🎬 Socials 7 · Instagram estate sweep | 🤖 auto |  | Quarterly |
| ✅ | 🎬 Socials 26 · Instagram unfollow checks | — |  | Closed 11-06 (Amir) |

## Ticket updates (for the System chat to merge)

Add two fields to every open 🎬 Socials ticket in `plans/tickets.json`, from the table above:
- `bucket`: `now` | `next` | `parked` | `routine`
- `who`: `amir` | `claude` | `auto`
- `next_step`: the "Next step / blocker" text
- `label`: the short platform + topic name from the Ticket column, without the number (e.g. "Bandcamp Friday", "SoundCloud inbox replies"); the digest and side chats show it

Values:
- 14 now/amir · 29 now/claude · 27 now/claude
- 23 next/claude · 21 next/claude · 2 next/amir · 17 next/amir
- 1 parked/amir · 4 parked/amir · 13 parked/claude · 16 parked/claude · 18 parked/amir · 28 parked/amir
- 5 routine/auto · 6 routine/auto · 7 routine/auto
- 26: **done** (Amir 2026-11-06 "Yes, close it"): IG part done 11-04 (7/7, visual check passed); SC part done 11-06 sweep 3/3, all 47 picks unfollowed + 8 regular. Set status done.

- `chrome`: `true` when the ticket's work happens in Amir's Chrome (the 🌐 column): 29, 2, 17, 4, 13, 18 are `true`; all others `false`

Also add `bucket`, `who`, `next_step`, `label`, `chrome` to the `fields` list, and the rule "max 3 `now` per area" to `area_rule` if the System chat agrees.
