# 💶 Income: +500 EUR/month + Gap Radar (handover, 2026-11-05)

Chat: "💶 Income +500 EUR (main)"; continued by the 💶 Income +500 side chat from 2026-11-05 (💶 Income 8 stays with the 💶 Income parent). Goal: +500 EUR/month from something Amir owns, run from here,
passive or few decisions, no client work (music only with proven income). Then grow it.

## Where it stands
- **RESTARTED by Amir 2026-11-06: "move forward and find 500 income as fast as we can".** income-niches tuned
  (new niches + insider words + do-not-repeat list of the 40 checked ideas), run right after the 11-06 radar run.
- (old) PAUSED by Amir (2026-11-05, side chat): income search on hold. No runs, no checks until he restarts it.
  Restart options when he does: tuned income-niches run (~$7, keywords from profile_reviews/income-niches.json),
  or 💶 Income 14 (music income with proof).
- **CORRECTION (side chat, 2026-11-05): the open decisions below were stale.** Both were already done today
  (see `plans/income-500-options-2026-11-05.md`): run 4 = income-niches alone, 492 items, 1 open
  (venue blog generator for wedding photographers, rated B-, Offer 13); landlord deadline calendar deep
  check ($1.13) = weak, dropped. Profile keywords were NOT tuned yet (yield 4 of 21 strong; review in
  `gap_radar/profile_reviews/income-niches.json`).
- **Venue blog idea checked (side chat): dropped.** Vowrio sells the same tool at $29/month (WordPress/Showit
  publish, alt text, vendor credits) and still has no proof that anyone pays for it. The radar's crowding check missed Vowrio.
  **0 vetted income ideas again.**
- **Owned-leverage check (💶 Income 13) done, $0 API:** Telegram alerts rated C (no paid demand found outside
  trading signals, Berlin flats already covered by MietAlert at EUR 4.99); Discogs dropped (ToS bans commercial use
  of Restricted Data, free alerts exist). Details at the end of `plans/income-500-options-2026-11-05.md`.
- **No vetted income idea yet.** 4 radar runs, 40 ideas checked: 0 open, 37 crowded, 3 unclear.
  Broad consumer gaps are always crowded; narrow professional niches are the current bet.
- **Gap Radar built** (`gap_radar/`): collect (Reddit RSS, HN, App Store, Stack Exchange,
  YouTube, GitHub, optional HikerAPI) -> Claude analysis -> crowding check -> report.
  Profile-driven (`gap_radar/profiles/*.json`, or any .json path). Quality check
  (`profile_check.py`, `lint` command). 83 tests pass.
- Profiles: income-gaps, income-niches; Inch of Shadow x6 (producer-tools, song-ideas,
  brand-marketing, ig-hooks, music-seo, scene-outreach); Gero x3 (closed, on demand only);
  Life x7 in apartmentcode (not merged, see below).
- Claude spend Nov: ~$36.1 USD of the $200 credit (ledger 2026-11-05 06:33; Anthropic bills in USD) (build days; Amir OK with it).

## 💶 Income 5: weekly radar (side chat, 2026-11-05, commits 052b6ba + 5282305)
- Built, NOT activated. `gap_radar/schedule.py` (+ `schedule.json`, status "default, Amir confirms"):
  weekly = 6 Inch of Shadow profiles + money-back; monthly = 4 Life profiles + crowding checks (first
  week of the month only); income profiles paused; Gero + trip-prep/doctors on demand. Life paths are
  skipped while their files are missing.
- Spend guard: refuses to run while `radar_cap_usd_month` or `ios_reserve_usd_month` is null. Skips a
  profile whose estimate would cross the radar cap, or would push the month total into the Inch of Shadow
  reserve (limit is LIMIT_USD = $150 in claude_api.py). HikerAPI already only gets the leftover of 300/day; all profiles have max_calls 0.
- Measured (ledger + reports, $0): analysis $0.30-1.04/run, crowding $5.6-7.2/run (~$0.65/idea);
  crowding = $32.7 of the $36.1 November spend. Value so far: 5 product runs, 0 vetted ideas; 5 of the 6
  Inch of Shadow profiles have never run, so their value is unknown.
- Default plan cost (my estimate, conservative $1.10/analysis): first week ~$20, other weeks ~$7.70
  = ~$43/month. Amir picks both caps.
- launchd: `gap_radar/launchd/com.inchofshadow.gap-radar.plist.draft` (Sun 05:00), install steps inside.
- Expansion ideas: `plans/radar-expansion-ideas-2026-11-05.md` (8 ideas, none built).
- RM pages: Amir 11-05 "no pages need for now", then "Remove /radar": removed in 5282305
  No Income page in RM. Reports stay as .md files in gap_radar/reports/.
- Caps SET by Amir 2026-11-05/06: radar_cap_usd_month 70 (5ef51ed), ios_reserve_usd_month 80 (329767e).
  With the $150 limit, the radar stops at whichever comes first: $70 radar spend, or a month total of $70.
  Dry run 11-06: every profile in the plan passes (radar $36.12 spent this month). Plist still NOT installed.
- LIVE since 2026-11-06: installed + loaded by the 💶 Income parent on Amir's yes
  (~/Library/LaunchAgents/com.inchofshadow.gap-radar.plist, Sun 05:00, python3.9, log docs/reports/gap-radar-launchd.log).
- Correction to the "~$20 first-week run on 8 Nov": 8 Nov is day 8, so it is a WEEKLY run (7 profiles, no
  competitor checks, ~$7.70 estimate). The first monthly run (+4 Life profiles + producer-tools competitor
  check, ~$20) is Sun 6 Dec. November gets no monthly run.
- 2026-11-06 evening, Amir: "make first calls tonight ... then delay the sunday one". Guard added (6347541):
  gap_radar/schedule_state.json records the last run; the job waits while it is < 5 days old (--force overrides).
  Manual run started 11-06 (counts as November's monthly run, est. ~$20); Sunday 8 Nov will skip; next run Sun 15 Nov.
- 2026-11-06 ~03:00 first real test (Amir via the 💶 Income parent: more tonight, several categories, up to the $70 cap):
  - Two monthly runs overlapped by mistake: the parent's (02:50, log gap-radar-manual-2026-11-06.log) and mine
    (03:07, log gap-radar-launchd.log). I stopped mine. Waste: about $8-10 (a second producer-tools analysis and
    competitor check, plus a few insight analyses; reports with T0350/T03xx stamps are the duplicates).
  - New profile income-trades (8a339ce): trades + regulated professions, do-not-repeat list. income-gaps stays paused.
  - Chain (log docs/reports/gap-radar-income-2026-11-06.log): after the parent's run ends -> income-niches -> income-trades,
    each only if it fits the cap (estimate $9.10 each incl. competitor check). A run past $70 waits for Amir's yes.
  - Morning: open ideas get my own manual competitor check; only those that pass are shown to Amir.
- RESULT of the 11-06 night test: 0 vetted ideas; 1 candidate (set bridge for live sets, B-, feasibility test next);
  overlap cost $9.43; income-trades waits for a cap raise (~$9.10). Details: end of income-500-options-2026-11-05.md.
- Set bridge feasibility (11-06): desk check done; 5-minute hands-on test for Amir in plans/set-bridge/FEASIBILITY.md
  (does a second app keep playing through a Live set load on the Fireface?). Decides B- vs C.
- Set bridge DROPPED by Amir (11-06, "nah sounds bad"). No test, no prototype. Files in plans/set-bridge/ kept as notes.
- Idea 3 (scene finds into outreach): scene-outreach runs on 8 Nov anyway, so option A needs no extra run.
  Still open for Amir: what happens with the names (candidates file reviewed in chat, or handed to Booking).
- Open for Amir: weekly list still marked "default, Amir confirms" in schedule.json.

## Decisions made (Amir, 2026-11-05)
- Show only vetted ideas; failed checks go to the notes file, never pitched.
- HikerAPI: IG agent automation first; radar only uses the leftover of 300/day.
- Gero lane closed: profiles on demand only. Focus: Inch of Shadow radar + +500 EUR.
- Claude credit OK for our own product (Credit Terms ban only reselling credits).
- Heavy spend fine during build days; before weekly runs: measure, then spend rules with him.
- Life lane searches German + English with synonyms; reports in English.
- No stop-words list; vinyl is not his world (removed from brand profile).
- Autopilot: chain radar tickets myself; still ask for ideas, spend rules, schedules.
- Ticket summaries: What / Why / Serves / Result / Next, short with emojis.

## Open decisions (Amir)
1. Next income step: deeper check on "landlord deadline calendar" (unclear, ~$1 USD) or
   re-run income-niches alone with tuned keywords (~$7 USD; first run got only 262 posts).
2. Merge Life lane: add one line (`radar/reports/`) to apartmentcode `.gitignore`
   (his uncommitted flat-bot edits are in that file) and merge the rest?
3. Spend rules + weekly coverage (💶 Income 5) after measuring.

## Side chats: what is merged
| Chat | Work | Merged here? |
|---|---|---|
| GR-02 crowding (deleted) | `crowding.py` | yes (ff180a5) |
| GR-04 sources (deleted by Amir) | `sources_extra.py` | yes (ff180a5) |
| GR-03 Inch of Shadow (deleted) | profile engine + 6 profiles | yes (8a7b57e) |
| GR-07 Gero (deleted) | 3 profiles; note in `/Users/amir/Desktop/Gero/gap-radar-reports/` | yes (aa2fc16) |
| **Radar · Life (GR-08)**, live | 7 profiles + README + test | **NO**: only on `refs/heads/claude/radar-life-02d979` in apartmentcode (e07515c) |

Leftover merged branches in this repo (safe to delete): `claude/gap-radar-profiles-ffbe27`,
`claude/gap-radar-gero-fcc8d8`.

## Key files
- `plans/income-500-options-2026-11-05.md`: every offer checked, dropped ideas, owned leverage, credit terms
- `plans/income-500-new-chat-prompt.md`: brief for a fresh chat
- `gap_radar/USES.md`: radar uses per lane
- `gap_radar/reports/` (income runs), `gap_radar/reports/income-niches/`, `gap_radar/profile_reviews/`
- `stats_snapshots/claude_spend.json`: spend ledger (by tool)

## Tickets touched
💶 Income 1 done · 2 done · 3 done · 4 done · 5 approved (P1) · 6 proposed · 7 done (lane closed)
· 8 waiting (merge) · 9 proposed · 10 done

## Proposed new +500 tickets (none exist yet)
- 💶 Income 11: re-run income-niches alone (no Reddit clash), tuned keywords. P1.
- 💶 Income 12: deep check of the "unclear" ideas (landlord deadline calendar; German version?). P2.
- 💶 Income 13: owned-leverage check: Telegram alert engine + Stars subscriptions, Discogs price
  data. Evidence of paid demand first. P2.
- 💶 Income 14: music income with proof: Symphonic label account for other artists, only with
  real income examples. P3.

## Ticket updates (for the System chat to merge)
- 💶 Income 5: status done; note "weekly radar live 2026-11-06 (launchd Sun 05:00, caps 70 radar / 80 Inch of Shadow reserve; schedule 052b6ba, caps 5ef51ed + 329767e). RM /radar page dropped on Amir's word (removed 5282305). First run 8 Nov (weekly), first monthly run 6 Dec."
- 💶 Income 11 + 14: status parked, note "income search paused by Amir 2026-11-05".
- (superseded) income profiles are out of the weekly run by default while the search is paused (schedule.json "paused").
- 💶 Income 13: done (Telegram C, Discogs dropped; notes in income-500-options-2026-11-05.md).
- 💶 Income 12: done (deep check landlord calendar, $1.13, weak, dropped; deepcheck-landlord-calendar.json).
- 💶 Income 11: run alone done (run 4, 2026-11-05T0619, 492 items, 1 open = venue blog). Keyword tuning not done; keep open only if Amir wants a tuned run.
- 💶 Income 11-14: already present in tickets.json as proposed (checked 2026-11-05), nothing to add.
- GR-08 / 💶 Income 8: status `waiting`, blocked_on "merge into apartmentcode: .gitignore clash
  with Amir's uncommitted edits". Note: done in e07515c on refs/heads/claude/radar-life-02d979;
  engine loads profiles by path (Inchofshadowcode 0a17f9c). (Already written to tickets.json
  before this housekeeping message.)
- GR-10 / 💶 Income 10: add note "stop-words list built and removed on Amir's 'no'; vinyl removed
  from brand-marketing (b82ef3e)".
- GR-09 / 💶 Income 9: consider moving to 🎧 Booking (DJ gig + festival calls).
- Add 💶 Income 11-14 above as proposed.

### Priority fields (💶 Income parent chat, 2026-11-05, per AREAS.md "Priority")
Open tickets only (12 + 13 are done above; 8 is done, see `radar-life.md`). 1 now, cap 3.
- 💶 Income 5: bucket now · who claude · label "Radar weekly run" · next_step "measure cost + value per profile from the build-day runs, then spend rules for Amir's yes" · chrome false
- 💶 Income 11: bucket next · who amir · label "Radar niche re-run" · next_step "Amir: tuned-keyword re-run (~$7) yes or close" · chrome false
- 💶 Income 14: bucket parked · who claude · label "Symphonic label income" · next_step "find real income examples before anything else" · chrome false
- 💶 Income 9: bucket parked · who amir · label "Festival calls radar" · next_step "Amir: move to 🎧 Booking or keep" · chrome false
- 💶 Income 6: bucket parked · who amir · label "Reddit API access" · next_step "Amir files the request only if the radar needs Reddit comments" · chrome true

### 💶 Income GR-10 "Gap radar fix" (2026-11-06, ticket from ⚙️ System)
- Old plist header, recorded before the change (~/Library/LaunchAgents/com.inchofshadow.gap-radar.plist, lines 3-8):
  "DRAFT, NOT INSTALLED (Income 5, 2026-11-05). Weekly Gap Radar, Sunday 05:00 (no IG session that day).
   Install only on Amir's yes to the spend rules: 1. set radar_cap_usd_month + ios_reserve_usd_month in
   gap_radar/schedule.json 2. cp this file to ~/Library/LaunchAgents/... 3. launchctl load ...
   Remove: launchctl unload that file, then delete it."
- Done 2026-11-06:
  - plist header now says INSTALLED 2026-11-05, with the caps and the stop command (plutil OK; comment only, no reload).
  - gap_radar.py Reddit: back-off on 429 is 60s, then 180s, then the sub is skipped with a reason.
    Two subs in a row still 429 = the rest of Reddit is skipped for that run, with the list and the reason (GR-06).
    Error lines are short now (no long URLs).
  - Tested offline with mocked requests ($0, no network). schedule.py --dry-run OK: 0 calls, radar $63.77 of $70.
  - Backup of the old gap_radar.py was in the scratchpad (wiped on reboot); the old code is in git history.
- Ticket update for ⚙️ System: 💶 Income GR-10 = done.

## Perplexity as a cheaper crowding check (2026-11-06): PARKED, future option
- Idea: run the crowding check (about 90% of radar spend, about $0.65-0.80 per idea) through Perplexity's Agent API (POST https://api.perplexity.ai/v1/agent, web_search tool). Hypothesis: a few cents per idea, so 10-30x more ideas per cap. Their docs show no fixed per-search price; one example shows $0.0025 per search.
- No connector exists in the directory; it needs an API key (console.perplexity.ai/project/keys, pay-as-you-go).
- Test kit ready, not run: gap_radar/perplexity_test.py (same rules + URL vetting as crowding.py, stops at $1). Test set = producer-tools/2026-11-06T0320.json (10 ideas, Claude check cost $8.19). Run: add PERPLEXITY_API_KEY to .env, then python3 gap_radar/perplexity_test.py.
- Amir: "skip for now, an option for the future". Do not raise it again unless he asks.
- 2026-11-06: Premiere versioning panel DROPPED after own check (details in plans/income-500-options-2026-11-05.md). Night-test list closed; only set bridge (B-) stays.
