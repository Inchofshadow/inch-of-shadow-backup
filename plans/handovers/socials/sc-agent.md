# 🎬 Socials: SoundCloud agent (SC hub chat)

Written 2026-11-05 06:00 by the SC hub chat. This chat runs all SoundCloud work: the daily automation, discovery supply, sweeps and the SC inbox. The IG agent is the other 🎬 Socials chat.

## Where things stand

**Account (live, end of 11-04):** 469 followers, 457 following, ratio 1.03:1. Floor 1:1, target 1.4-1.6:1. Goals: Nov 30 510 followers, Dec 31 600 at 1.2:1, Aug 2027 1000 at 1.4-1.6:1. The Oct 31 mark of 420 was reached; the 1.1 ratio was missed.

**Daily automation (all running, all local Berlin time):**

| Task | When | What |
|---|---|---|
| SC refresh 1/3, 2/3, 3/3 | 06:30, 07:30, 08:30 | Discovery crawl, about 30 candidates each. SoundCloud allows 100 API reads per hour, so it is split into three runs. Run 3 sends the daily health report and commits data. |
| Sc engagement | 10:00 | Up to 20 unfollows (10-day window), 20 warm-up likes + 20 follows, PASS C maintenance likes, hard stop 60 actions. |
| SC 13:00 retry | 13:00 | Runs only when the 10:00 run logged nothing (`--retry-gate`), closes with `--rescore`. |
| Sc monthly maintenance | 1st + 15th, 12:00 | `sc_maintenance.py` + `hygiene_check.py`. |
| Sc weekly release stats | Fri 18:00 | Release track stats. |

**Manual-follow sweep (in progress, Amir's request 11-03):**
- Amir ticked 47 accounts he followed himself (not automation follows) for unfollow, on a private picks page: https://claude.ai/artifact/TYi8tzqJzpdgYinP3rsGyG (db collection `picks`). Final list: `plans/sc-sweep-picks-2026-11-03.json`.
- Done: 16 on 11-03 at 21:00 (run by hand in this chat), 16 on 11-04 at 16:15 (sweep run 1, plus 12 regular unfollows). Remaining: 15 (file positions 33-47).
- Runs left: **Thu 11-05 16:15** (sweep 2/3: the remaining 15 + regular due batch), **Fri 11-06 16:15** (sweep 3/3: regular due batch + any leftover). One-time tasks `sc-sweep-run-2-1105`, `sc-sweep-run-3-1106`; they disable themselves after running.
- On 11-04..11-06 the config `UNFOLLOW_CATCHUP_DAYS` raises the day caps, so the 10:00 session skips its own unfollow lane and the 16:15 run does those unfollows. After 11-06 everything returns to normal by itself (dated entries).
- Contact info of all 76 non-following own follows (emails, links, booking lines, full bios) was saved BEFORE any unfollow: `plans/sc-follow-contacts-2026-11-03.md` + `.json`.
- The swept accounts go on `permanently_unfollowed` in the tracker, so the automation never re-follows them.

## Decisions made (recent)

- **Follow cap 10/day 11-07..11-16 (Amir "B", 11-06).** Following stayed ~457 because 20 follows/day refilled what unfollows removed. Goal: following ~376 (476/376 = 1.27:1) by ~11-16. Config FOLLOW_CAP_DAYS, was 20; back to 20 on 11-17 by itself. Check the daily following count against the path (~-6 to -10/day).

- **Anyone in the outreach list stays followed** (Amir 11-03, "if we approach someone i dont wanna remove the follow"), any status including passed. 9 such accounts were removed from the sweep. Personal-network accounts and anyone with an SC inbox thread are also never swept.
- **G-03 option A (10-24):** a reciprocator who stops following back becomes a normal unfollow candidate (`FOLLOWBACK_LOST_UNFOLLOW = True`).
- **PASS C re-check pause (11-03):** targets with no track in the last 90 days are marked with `--mark-passc-checked` and stay off the list for 14 days. It worked at once: 8 PASS C likes on 11-04 against 2 the day before.
- **Discovery:** seed rotation (least recently crawled first); techno is fine, numbers matter most (10-07); new seeds Moravie_, Local Suicide, Blank Wave/Shia LaBiff, CURSES; three refresh runs a day because of the 100 reads/hour limit (10-25).
- **13:00 retry** when the 10:00 run did nothing (10-25).
- **Dennis vd Berg: never unfollow** (keep_following).
- **Sweep runs at 16:15** (Amir moved them from 18:30, then 16:00), a few hours after the 10:00 session, so no single sitting goes far past 60 clicks.
- **Temporary Files Rule (10-24):** research saves text only, scratch downloads go to the Trash; `fetch_text.py` + `hygiene_check.py`.
- **Inbox:** drafts are always shown to Amir first; "send yourself" covers only the drafts named in that exchange.

## Open decisions (Amir's call)

1. **SC inbox replies (🎬 Socials 29).** 2026-11-06: all 29 threads read (context in plans/sc-inbox-context-2026-11-06.md), 10 need a reply, drafts below under "Unsent drafts"; Amir picks which to send. Nothing sent.
2. **Dated follow cap of 15 ("soften")** to lift the ratio faster. Offered twice, not taken; not needed once the sweep ends.
3. **The 37 early tracker follows** (7-9 days old, no follow-back) were offered for the sweep and not chosen; nothing pending unless Amir asks.

## Key files

- Code: `scene_intelligence/sc_engagement.py`, `sc_engagement_config.py` (THE LAW for caps), `sc_weekly_health.py` (refresh + health), `close_loops.py` (scorer).
- State: `scene_intelligence/sc_follow_tracker.json` (read `stats.active_follows`, never subtract), `discovery_candidates_<date>.json`, `sc_rejected_candidates.json`, `sc_seed_rotation.json`, `engagement_log.json`, `sc_session_report_<date>.md`.
- Docs: `docs/sc-engagement-sop.md`, `docs/sc-agent-context.md`.
- Sweep: `plans/sc-sweep-picks-2026-11-03.json`, `plans/sc-sweep-2026-11-03.json` (live pull), `plans/sc-follow-contacts-2026-11-03.md`, `plans/sc-sweep-page/index.html`.
- Scheduled task prompts: `~/.claude/scheduled-tasks/<task>/SKILL.md`.
- Commits this stretch (local only): 458a432 PASS C pause, 2a85877 + 359564a sweep allowances, 18f1520 travel notes removed.

## Linked tickets

| Ticket | Status | Note |
|---|---|---|
| 🎬 Socials 1 | waiting | Reciprocator-skip review |
| 🎬 Socials 4 | waiting | IG data export pull (also feeds the SC manual-follows intake) |
| 🎬 Socials 5 | waiting | Oct 1 SC maintenance: archive session_reports.json + nina files |
| 🎬 Socials 8 | done | SC tracker: notice when a reciprocator stops following back (G-03) |
| 🎬 Socials 18 | in progress | Supporter notes by hand, names matched to IG/SC |
| 🎬 Socials 26 | in progress | Unfollow sweep verified from the follower list |

## Not merged anywhere else (lives only in this chat)

- The 10-21 inbox reply drafts are now copied in full below under "Unsent drafts" (they were only in the chat transcript before 11-05).
- The outreach-stays-followed rule is below as a proposed SOP line and in Claude's memory file `sc-manual-follow-sweep-2026-11.md`; `docs/sc-engagement-sop.md` itself is not edited yet.
- Uncommitted SC data (normal; the 08:30 refresh run commits it): tracker, rejected candidates, 11-03/11-04 session reports, loop-close reports.

## SC inbox replies SENT 2026-11-06 ~13:30-13:45 (Amir "Yes, send 1-10")

All 10 below went out word for word, each checked in the thread after sending. Before the "liked" lines: Herzblut played muted 28 s + liked + logged; Stories 021, LEMNISCATE and A Body Without Witness were already liked (checked). Slip: Stories 021 was already liked and my first click UNLIKED it; re-liked at once and verified (54, "Unlike"). Rule since: check the like state before clicking. Next: watch for answers; the EP goes to TheTallMan + Owo Barry when out (promised).

### The sent texts

Full per-thread context: `plans/sc-inbox-context-2026-11-06.md`. Amir 11-06: "u dont need to push links by force", answer like a human; a track only where the thread is a track trade. Amir picks; nothing goes out unasked.

1. Unseen-Kollektiv (needs muted 20-30 s play + like first; he writes very short): "Hey hey :) Stories 021 is so good, very nice selection! Thanks for sharing"
2. TheTallMan (writes "Hello mate !!", signs "Take care,"): "Hello mate !! Thank you so much, really happy you liked it :) Yes, an EP is coming, two new tracks. I'll send it to you as soon as it's out. Take care!"
3. Owo Barry (❓ sound line): "Thank you so much :) The new ones go a bit more to the dancefloor, acid with a darker edge. Will send them when they're out!"
4. Andre Heil (needs muted play + like of Herzblut first; trade thread, track optional: Insomnia set): "Herzblut für die Niederlande is super cool, love the energy and the bass :)"
5. IKALEE (verify the like on "Sequel to Empty Rooms" first; writes cryptic + 🖤; trade thread, track optional: Farewell): "Sequel to Empty Rooms is beautiful, I liked it a lot 🖤"
6. HARUN (like logged 10-26, verify it shows before sending): "Hi, how are you? :) Thank you so much! A Body Without Witness is super cool, I really liked it."
7. DJ Slowbridge: "Hi :) my pleasure! Greetings from Berlin"
8. erhan__music: "Thank you! 🖤"
9. WORSTFØLD: "Welcome back! :)"
10. Noah Wilson: "Hey, how are you? :)"

## Proposed SOP line (not in the SOP yet)

For `docs/sc-engagement-sop.md` §6.3 (unfollows), proposed wording, for Amir's OK before anyone edits the SOP:

> **Outreach contacts stay followed (Amir, 2026-11-03).** Never unfollow an account that appears in `plans/outreach-batches.json`, whatever its status (proposed, drafted, needs rewrite, passed, sent). Match on the SoundCloud URL, an email in the bio, or the contact name. The same holds for the personal network list and anyone with a SoundCloud inbox thread. Before any sweep, re-run this check against the current outreach file and drop every match from the batch.

## Ticket updates (for the System chat to merge)

- M4 state-file rotation (Batch 4): Amir 11-07 "Yes, as you say" = CHANGE: yes to .bak 14 days -> Trash + .gitignore; no to splitting engagement_log.json for now. enrich_soundcloud.py may move to archive/si-discovery/. Sent to System; System does the moves with dry run + undo.

- 🎬 Socials 26 · unfollow sweep (SC part): sweep run 3/3 on 11-06 16:15 finished; all 47 of Amir's picks are now unfollowed (0 left), plus 8 regular unfollows. 16:15 end: 476 followers / 457 following = 1.04:1. Amir 11-06: keep it open.
- RM /sc-automation (System D17): SC chat answered (b) read-only status view, no run button, no test-auth (11-06).

- 🎬 Socials 29 · SoundCloud inbox replies: 2026-11-06 all 29 threads read, who-is-who in plans/sc-inbox-context-2026-11-06.md, 10 replies sent on Amir's go (no forced links, tracks liked before any "liked" line). Done; close.

- 🎬 Socials 26 (M-13): add note "2026-11-03..06: manual-follow sweep of 47 own follows Amir ticked (picks page, live follower pull, outreach/personal/inbox excluded, contacts saved first). 32 done by 11-04, last 15 on 11-05 16:15." Close it after the 11-06 run if Amir agrees.
- New ticket, 🎬 Socials (next free number): "SC SOP: write the 'outreach contacts stay followed' rule into docs/sc-engagement-sop.md §6.3 and the sweep planner" (P3, S).
- New ticket, 🎬 Socials (next free number): "SC inbox: reply drafts for TheTallMan, HARUN, erhan__music, Noah Wilson, DJ Slowbridge, Owo Barry, Andre Heil, WORSTFØLD, Ika Lee" (P2, S, waiting on Amir).

## Proposed fact fixes from ⚙️ System (2026-11-05)

Not applied: `docs/sc-agent-context.md` sits next to the engagement automation, so nobody edits it from the System chat. Source: `plans/strategy/review-2026-11-05-fixlist.md`. Truth: songs are the main line since 2026-09-13 (not public); next electronic release Half the Night EP (Half the Night + Pinocchio), date open, as early as possible; no 3 EPs.

- Row 11, `docs/sc-agent-context.md:29-31`. Now: "The 2026 release plan. Three EPs across different styles." Proposed: Release plan: songs are the main line (not public). Next electronic release: Half the Night EP, date open.
- Row 12, `docs/sc-agent-context.md:33-39`. Now: "EP | Genre | Targeting flavor ... flexes with the EP". Proposed: rename the table to "Genre framings for targeting"; framing flexes per release, not per EP.
- Row 13, `docs/sc-agent-context.md:41`. Now: "as of 2026-08-27 the most recent release is The Deceiver". Proposed: add: next is the Half the Night EP (Half the Night + Pinocchio), date open, as early as possible.
- Row 14, `docs/sc-agent-context.md:138`. Now: "Currently: farewell-single." Proposed: Currently: none active (check the file).
- Row 15, `docs/sc-agent-context.md:139`. Now: "Currently: Farewell, EBM/Acid, May 15." Proposed: read the file; next release is the Half the Night EP, date open.
- Row 16, `docs/sc-agent-context.md:147`. Now: "Currently active campaign: farewell-single -- targets being pre-warmed include". Proposed: remove the line, or: no active campaign; verify in `promotion_log.json`.

## Proposed from ⚙️ System (2026-11-06): platform jobs

Not applied: `docs/sc-agent-context.md` and `docs/sc-engagement-sop.md` sit next to the engagement automation, so nobody edits them from the System chat. Source: `plans/strategy/platform-plan-songs-2026-11-05.md` (approved by Amir 2026-11-06, D5). Exact lines to add, for the SC chat to place:

- `docs/sc-agent-context.md`, in the release plan block (rows 11-13 above touch the same lines), add:
  > **SoundCloud's job (approved 2026-11-06):** home of the electronic lane, and a side door for the songs. Electronic releases run as today (Half the Night EP next, date open). Songs get one follower-only early drop per single (Artist Pro), then public and Amplify inside 14 days, uploaded direct and not via the distributor, so Amplify applies.
- `docs/sc-agent-context.md`, same block, the measures line:
  > **What we measure for this job:** electronic, plays in the first 14 days, Amplify result, likes and reposts; songs, follows gained from the gated drop. Still a guess: whether a gated track becomes Amplify-eligible when made public; test on a non-key track first.
- `docs/sc-engagement-sop.md`, under the goal, one line:
  > Engagement serves SoundCloud's one job, the electronic home: seeds and cadence stay electronic, the songs lane does not change SC cadence. Full plan: `plans/strategy/platform-plan-songs-2026-11-05.md`.


## Proposed from ⚙️ System (2026-11-06): state file rotation (M4, Batch 4)

Not applied; the engagement state is yours. Facts today: `scene_intelligence/engagement_log.json` is 1.7 MB and
grows every session; the SC tracker health refresh writes a 500 KB `.bak` three times a day (55 untracked
`.bak.*` files in `scene_intelligence/` now). Proposal, for your yes and your dry run:
- `engagement_log.json` keeps the current month; older months move to `scene_intelligence/archive/engagement_log-YYYY-MM.json.gz` by a small script you own, run on the 1st; every reader that scans history reads the archive too (list the readers first).
- `.bak.*` files: keep 14 days, then Trash (never rm), and add `scene_intelligence/*.bak.*` to `.gitignore` so they never enter git (the 23 files under `backups/sweep-20260831/` stay as they are).
- Test: one session after the rotation must log, score and report exactly as before.
Reply in your handover's "Ticket updates" with yes / change / no.