# Score board: growth metrics against targets (design)

Date: 2026-11-01. Status: DRAFT, waiting for Amir's approval. Nothing built.

## Intent

Amir wants one place in the Release Manager where he sees the growth of Inch of
Shadow on the socials against written targets, the way the Gero control panel's
Score page does it: big numbers, a light per metric, a monthly ladder, and a
chart of reality against the plan. The last six weeks (HikerAPI empty, direct
Instagram reads off) count as a pause; the system starts fresh on 2026-11-01
with HikerAPI back on the Standard rate.

He does not want to think about numbers. Baselines and targets are derived from
the data by a stated rule ("computer"), he approves or rejects them.

## Goals

- Six gate metrics with lights, a monthly ladder, and "% of the way from
  baseline to target", on the existing `/stats` page.
- Targets written once per period into a file, never edited mid-period.
- Every number traces to a file. A metric with no reading says "collecting",
  never a fake zero.
- Daily, automatic, including Instagram follower count again.

## Non-goals

- Not a second Gero. No digests, no per-page site checks, no manual-sample
  overdue list beyond the health row below.
- No per-session activity numbers (likes, follows, session count) on the board.
  Those stay in the session reports.
- No light mode, no chart library, no CDN. The Release Manager is dark only,
  local fonts, server-rendered inline SVG.

## Anti-goals (would make it a failure even if it worked)

- A target that moves because the month went badly.
- A number on the board that nobody can trace to a file and a date.
- Extra Instagram reads from Amir's own account. The only new Instagram read
  is one HikerAPI call per day, through the provider ledger.
- A reminder habit heavier than: Monday screenshot, monthly export.

## The six gate metrics

| # | Metric | Source of the daily or periodic sample | Cadence |
|---|---|---|---|
| 1 | IG followers | HikerAPI `user/by/username` for `inch_of_shadow` (followers, following, media_count), stored in the daily snapshot under `platforms.instagram` | daily, 08:45 sync |
| 2 | IG follow-back % by monthly cohort | cohort = the automation's follows by month, from `scene_intelligence/ig_follow_tracker.json` (active_follows.followed_at and unfollowed_history.followed_date, read-only); "back" = the handle appears in `followers_1.json` of the newest All-time export. This is the 2026-10-10 method (May 54/14, Jun 91/16, Jul 81/18, Aug 35/7, Sep 58/17). Not `following.json`, which only holds keepers after the 7-day unfollow. | monthly, when Amir drops the export |
| 3 | IG reach, last 30 days | Instagram Insights "Accounts reached" screenshot from Amir, number stored as a manual entry (`instagram`, `reach_30d`) | weekly, Monday, with the Spotify read |
| 4 | SoundCloud followers | daily snapshot, `platforms.soundcloud.followers` (exists) | daily |
| 5 | Spotify monthly active listeners | `stats_snapshots/spotify_s4a.json` `weeks[<end>].monthly_active` (exists, Monday read) | weekly |
| 6 | TikTok followers | none yet. Card shows "collecting" until a collector exists (ticket Measure-01) | n/a |

Decided by Amir: 2 is monthly, 3 is weekly by screenshot, 3 was briefly out and is
back in.

OPEN (Amir): metrics 1 and 3 could instead come from the official Meta Graph API
(`scene_intelligence/ig_fetch_insights.py`, own-account token, graph.instagram.com),
which the ledger already budgets as a safe surface (`graph_insights: 40`) and
which last worked on 2026-10-04. Graph gives the follower count and the 30-day
"accounts reached" in one daily call, so no screenshot habit and no HikerAPI
spend for the own profile. The private-client reads that got fingerprinted are a
different surface. If Amir says Graph: 1 and 3 become automatic, HikerAPI stays
as the fallback for the follower count. If he says no Graph: HikerAPI for 1,
screenshot for 3, as written. See "Data changes".

### Health row (pass/fail dots, no targets)

IG ratio followers:following >= 1.0; last IG session score >= 8; vetted IG pool
>= 30; HikerAPI balance > $10; detection signals in the last 7 days = 0; newest
snapshot <= 2 days old; newest All-time export <= 40 days old; newest Spotify
read <= 10 days old. Each dot links to where the number comes from.

### Trend-only cards (no target)

YouTube subscribers, Spotify followers (S4A), Bandcamp followers (manual entry,
baseline 51 on 2026-10-21), SoundCloud follow-back %.

## Targets: the rule and the first period

First period: 2026-11-01 to 2026-12-31 (two months). Then calendar quarters.
Targets are derived once at the start of a period and written to
`plans/targets.json`. Amir approves the file; after that nobody edits it until
the next period.

The rule ("computer"):

- Baseline = the first reading of the period from the board's own source
  (for Instagram the first daily profile reading on 2026-11-02, about 950; the
  export's 955 counts differently). The rungs are computed from that reading
  once, the file is written that day, and nothing in it changes until the next
  period.
- Monthly rung = baseline + N months x the average monthly rate over the last
  six months of pre-pause data (Instagram: 2026-04-03 to 2026-09-26, 777 to
  948, 29.4 per month). Rates rounded to 5.
- Period target = the last rung.
- For a rate metric (follow-back %): no ladder. Floor = mean of the monthly
  cohorts since May minus 3 points, rounded down to 5.
- For a flat or noisy series (Spotify monthly active): Nov rung = 12-week
  mean, Dec rung = best 4-week mean of the last six months, rounded to 5.
- A metric with fewer than 4 readings gets no target; the card says
  "collecting" and the ladder starts next period.
- Where Amir already confirmed a ladder (SoundCloud, SC-07, 2026-09-01), that
  ladder is used unchanged.

Lights: green when today's reading >= the ladder value for today (linear
between rungs) minus 5%; amber when within 15% below; red beyond. Rate metrics:
green at or above the floor, amber within 5 points, red below. "No data" is a
fourth state, grey.

### First-period numbers (derived 2026-11-01, Amir to approve)

| Metric | Baseline (date) | Rate used | Nov 30 rung | Dec 31 rung |
|---|---|---|---|---|
| IG followers | first profile reading on 2026-11-02 (about 950) | 30/month (Apr 3 to Sep 26 average, 29.4) | base + 30 (about 980) | base + 60 (about 1,010) |
| IG follow-back % | 23% (export 2026-10-10, cohorts May 26, Jun 18, Jul 22, Aug 21, Sep 29) | floor rule | floor 20% | floor 20% |
| IG reach 30d | none | collecting | - | - |
| SoundCloud followers | 447 (2026-10-31) | SC-07 ladder | 510 | 600 |
| Spotify monthly active | 96 (week to 2026-10-30) | 12-week mean 91.75 (Aug 10 to Oct 30), best 4-week mean 109 (Oct 5 to 30) | 90 | 110 |
| TikTok followers | none | collecting | - | - |

Sanity notes: the Instagram rate is the pre-pause pace with the automation
at 6 to 12 follows per session; the queue is refilling from 2026-11-02, so 30
is a floor, not a stretch.

Derive versus record: `targets.json` holds the APPROVED numbers. A one-off
script (`stats/propose_targets.py`) applies the rule to the data and prints a
proposal; Amir approves; the file is written. `stats/targets.py` only reads the
file, validates it, interpolates the ladder for today and computes the lights.
Tests cover the interpolation and the lights, not the proposal numbers. When
the rule and an approved number disagree, the file wins. The SoundCloud ladder was already beaten in
October (447 vs 420), kept as is because it is Amir's confirmed ladder.
Spotify is flat since July; the Pinocchio single (2026-11-06) is the first thing
that could move it.

## How it looks

Top of `/stats`, replacing the current trend-only score block:

- Score line: "ON PACE, 4/6 GREEN, 1 DRIFTING, 1 COLLECTING", from the lights.
  "On pace" when green >= half of the metrics with data.
- Six cards in a 3x2 grid, same `.st-card` style. Each: name, source key in
  mono (for example `hikerapi.ig.followers`), the big number (Marcellus), unit,
  the light, the current rung line ("NOV 30 1,010, +12 PAST RUNG" or "-9 TO
  RUNG"), a progress bar "% of the way from baseline to target", and a footer
  "955 BASE, NOV 30 1,010 RUNG, 1,045 TARGET, as of 2026-11-01". Sparkline
  120x32 on the right, last 90 days.
- Below the cards: the health row (dots, "7/8 pass"), then the ladder charts,
  one per gate metric with a ladder: the real line, the dashed staircase
  through baseline and rungs, "today" marker, dotted baseline, period on the
  x axis.
- Below that: the existing "This week" panel, then the trend-only cards, then
  the existing per-track grid (SC plays, likes, reposts, YT views, and so on),
  all kept as they are. Nothing on the page is removed, only the score block at
  the top is replaced.

Style: existing tokens (`--bg-secondary`, `--text-accent` platinum, status
greens/ambers/reds), Marcellus for the numbers, Inter for the rest, no new
colours except the TikTok brand `#25F4EE` already used elsewhere.

## Data changes

1. **IG daily sample.** Two variants, Amir picks (see OPEN above).
   (a) Graph: the `instagram` collector keeps its Graph call (own-account
   token, `ig_fetch_insights.py` path), writes followers, following,
   media_count and 30-day accounts reached; one ledger claim
   (`kind="api"`, endpoint `graph_insights`); HikerAPI profile call only as
   the fallback when Graph fails.
   (b) HikerAPI: the collector calls
   `scene_intelligence.ig_data_provider.Provider().profile("inch_of_shadow")`
   after a ledger claim (`check_and_claim(script="stats_daily_sync",
   kind="provider", est_calls=1)`), writes followers, following, media_count;
   reach comes from the Monday screenshot.
   In both: the launchd plist drops `--skip instagram`; the ledger refusal
   (`LedgerRefused` is a SystemExit) is caught so the "Sync now" button and a
   second run in a day do not crash the sync; on failure the snapshot carries
   the error and the card shows the last good reading with its date. The
   private-client reads stay off.
2. **Follow-back script.** New `stats/ig_followback.py`: reads the tracker
   (read-only) for the cohorts and the newest All-time export's
   `followers_1.json` for who is back, writes
   `stats_snapshots/ig_followback.json` with `{export_date, cohorts{YYYY-MM:{followed, back, pct}}, since_may_pct}`.
   Must reproduce the 2026-10-10 numbers above from the 10-10 export (that is
   the test). It never writes the tracker. Run by hand when an export lands,
   and by the daily sync when it sees a newer export than the file records.
3. **Manual entries.** The existing manual-entry store gains
   `instagram_insights / reach_30d` (its own platform key, so it does not
   collide with the API `instagram` key in `get_overview`), `tiktok /
   followers`, `bandcamp / followers` (hand-dated backfill: 51 on 2026-10-21).
   Entry path for a screenshot number: a small CLI,
   `python3 stats/manual_entry.py instagram_insights reach_30d <n> --date
   <d>`, which Claude runs when Amir sends the screenshot in any chat. No
   web form, no watched folder.
4. **Targets file.** `plans/targets.json`: period, per metric baseline (value,
   date), rungs (date: value), target, rule used, approved_by, approved_on.
5. **Monday habit (variant b only).** The `spotify-s4a-weekly-read` task's
   closing report adds one line asking Amir for the Instagram Insights
   screenshot; he sends it in chat, Claude stores it with the CLI. The
   unattended task itself cannot wait for him.
6. **HikerAPI balance** is read once per daily sync (`Provider().balance()`,
   the same call the dispatcher makes) and stored in the snapshot for the
   health dot.

## Constraints

- Hands off the engagement automation code and state. The only touch points
  are the provider client (read) and the ledger (claim), both already shared.
- The Release Manager server is not restarted by Claude.
- Tests for the ladder maths, the light rules, the follow-back script (against
  the 10-10 export numbers) and the page build, in `tests/`.
- No em-dashes in copy on the page.

## Left to the builder

- Exact JSON shape of `targets.json` and where the ladder maths lives (a
  `stats/targets.py` next to `stats_tracks.py` is the obvious spot).
- How the ladder chart SVG is drawn (server-side, like the sparklines).
- Grid behaviour below 900px.
- Whether the follow-back script also refreshes the tracker's `follow_backs`
  count (nice to have; must not write engagement state without a separate go).

## Calls made after the builder check (Claude's, not Amir's)

- Follow-back cohort = tracker follows by month, matched to the export
  (the 10-10 method).
- Targets file records approved numbers; a proposal script applies the rule;
  the file wins.
- Instagram baseline = first board reading on 2026-11-02; rungs fixed from it
  that day. Rate 30/month from the six-month pre-pause average.
- Spotify Nov rung 90 (true 12-week mean), Dec 110.
- Nothing is removed from `/stats`; the per-track grid stays below.
- Screenshot numbers enter through a CLI, not a form or a folder.
- Balance read once per sync for the health dot.

## Open question for Amir

Graph API (variant a: automatic followers + reach, no screenshot) or HikerAPI
plus screenshot (variant b)?
