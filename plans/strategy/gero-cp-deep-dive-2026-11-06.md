# Gero control panel, deep dive: metrics, dashboard, review flow (2026-11-06)

Read-only study, second pass. Nothing edited, moved, built or called in either repo. No secret
values here. The first pass (`gero-transfer-2026-11-06.md`) covered skills, SEO, video, X and
LinkedIn; this one goes into the data, the Score page and the review flow.

Where the code was read: the metrics core lives only on Gero's `origin/main` (`src/lib/pm`,
`docs/pm`, `src/components/console`, `src/app/pm`); the local checkout sits on a docs branch
without it, so those trees were exported with `git archive` into the scratchpad and read there.
The Video Desk build was read from the `video-desk` worktree. Gero memory files were read for the
known drift. IoS side: `release_manager/score_board.py`, `templates/stats.html`, `stats/*`,
`plans/targets.json`, the 11-01 score board spec, `stats_snapshots/`, `docs/brand/`,
`plans/outreach-page/`, `releases/*.json`, `plans/AREAS.md`.

Short verdict: Gero's numbers are "super accurate" because of six habits, not because of
Postgres or Cloud Run. IoS already copied the shape of the Score page on 11-01; what is missing
is the discipline underneath it (one registry, provenance per sample, skip reasons, a freshness
rule, frozen gates, parity tests). All of that fits in JSON files on one Mac.

---

## A. Metrics methodology and data accuracy

### A1. Where each number comes from

| Metric family (ids) | Source and field | Collector, cadence | Window and maths |
|---|---|---|---|
| `gsc.gero.*`, `gsc.nexus.*` (clicks, impressions, positions, CTR per page, keyword clusters) | Search Console API, domain property `sc-domain:gerowallet.io`; query rows (limit 1000) + page rows (limit 500) + page x date rows (limit 25,000) | `cron:pm-gsc`, daily ~04:10 UTC | Trailing 28 days ending 3 days back (GSC lag). The range is inclusive, so 29 days arrive; totals are multiplied by 30/29 to a "per month" figure. Non-brand = total minus brand-regex clicks, floored at 0. Positions and CTR are unnormalised. |
| `ga4.gero.users`, `users_filtered`, `organic_sessions`, `ga4.nexus.users`, `trial_form_starts` | GA4 Data API, both properties, bot and internal-IP filters (`docs/pm/ga4-filters.md`) | `cron:pm-ga4`, daily | Same 29-day window as GSC. Raw users shown next to filtered users on purpose (about 1/3 bots). |
| `ga4.gero.store_clickouts`, `download_page_conversion`, `pm.traffic.unmapped_share` | GA4 per day, per channel, written to `pm_traffic_daily` | `cron:pm-traffic`, daily, D-2 and D-1 | conversion = clickouts / sessions that viewed /download/; skipped (never 0) when the page had no sessions; can exceed 100 % and the note says why. |
| `site.gero.*`, `site.nexus.*` (sitemap URL count, non-200, multi-h1, missing meta, titles over 60, www redirect, Contentful status, llms-full status, status page live) | Live HTTP crawl of the sitemap URLs | `cron:pm-site-health`, nightly ~03:10 UTC | A sitemap shrinking more than 10 % between nights writes a `pm_alert` row. |
| `wallet.sync_sessions` (+ platform split), `wallet.sync_addresses` | gero-sync admin API (live websocket gauge) | `cron:pm-wallet`, hourly | One sample row per UTC day holding the latest reading (`upsertDailySample`), plus min/max/sum/count per day in `pm_gauge_daily`. |
| `wallet.chrome_weekly_users` | The public Chrome Web Store listing page ("9,000 users"), scraped | same hourly run | Google rounds to hundreds or thousands; when the listing shows no count the collector skips and logs instead of writing 0 (a 0 would mean "delisted" on a gate metric). |
| `social.youtube_subscribers` | YouTube Data API `channels.list(statistics, mine)` | `cron:pm-youtube`, daily 03:50 UTC | Hidden or unreadable count = skip, never 0. Broken refresh token = `error` so the run returns 502 and the scheduler retries. |
| `x.gero.followers`, `x.*.impressions_30d` | X API, two calls per account; stored first in `x_stat_snapshot` (account, metric, day), bridged into the registry | `cron:x-stats`, daily | X has no history endpoint, so the trend is accrued one row a day. Delta on the tiles is week-on-week although the window is 30 days (a 30-day delta would need 60 days of history). |
| `help.*` (12 counters) | gero-backend Help analytics, anonymous daily aggregates | `cron:pm-help`, daily | Re-reads the last 3 days every run because the newest day is still filling; each day is upserted under its own day (`upsertSampleForDay`), so a re-run moves a value, never adds a row. |
| `pm.tickets.open`, `closed_this_sprint`, `tickets_with_valid_metric` | GitHub API across three repos, mirrored into `pm_ticket` | `cron:pm-tickets`, hourly | Compliance = share of OPEN tickets whose body contains a backticked registered metric id. |
| `pm.dashboard_freshness_hours` | Computed from `max(captured_at)` over auto metrics | `cron:weekly-monitoring`, weekly | Written as a by-product after the digest is stored. |
| `nexus.trials.started`, `clients.paying`, `mrr` | "the #56 endpoint" | none (on pause) | Never collected; the digest lists them as a known gap, not a fault. |
| 9 manual metrics (`comp.*` Semrush, `ads.*`, `discord.members`, `wallet.testflight_testers`, `comp.gero.aio_presence`) | A human reads a UI, types the number on `/pm/manual` | weekly / monthly / quarterly by metric | Stored as a sample with `source_run = 'manual:admin'`. `docs/pm/manual-metrics.md` says the exact screen, settings and date range per metric so two people get the same number. "If you cannot reach the source, leave it blank": a blank and a 0 are different facts. |

How the jobs run: every collector is an HTTP POST route under `src/app/api/cron/` on Cloud Run.
Google Cloud Scheduler calls it with an OIDC token; `src/lib/cron-auth.ts` checks the token's
email, `email_verified`, issuer and audience path before anything runs. Only Adam has GCP access,
so a new job or a secret is a handover item. `docker-compose.yml` is only a local Postgres for
development; `k8s/` is a template from the website repo and is not what runs. The Mac launchd
jobs are video renders, not metrics (and they hit the same Full Disk Access block IoS solved on
09-03).

### A2. How a number is stored

Two tables carry everything (migration `007_pm_metrics.sql`):

- `pm_metric`: id, name, unit, source, collection (auto | manual), direction (up | down |
  bool), baseline, baseline_at, target, target_at, is_gate, manual_frequency, notes.
- `pm_metric_sample`: metric_id, value (numeric), captured_at, source_run, UNIQUE (metric_id,
  captured_at). Samples accrete; nothing is ever overwritten by a normal collector run.

Around them: `pm_alert` (regression alerts with an acknowledged_at), `pm_gauge_daily`
(min/max/sum/samples per metric per day for hourly gauges), `pm_gate_snapshot` + `pm_gate_note`
(the frozen gate reviews), `pm_digest` (one row per weekly run), `pm_traffic_daily` and
`pm_gsc_page_daily` (page-grain evidence), `x_stat_snapshot` and `x_post_metric` (X history,
primary key on day).

`source_run` is the provenance stamp on every row: `cron:pm-gsc`, `cron:pm-wallet`,
`manual:admin`, `cron:weekly-monitoring`. Readers filter on it: a manual metric only counts as
"entered" when the newest row is `manual:%`; a backfill or a later collector cannot reset the
staleness clock.

### A3. Duplicates, gaps, late data, failures

- **Duplicates.** Readers never `LIMIT 1` in a loop; `latestByMetric()` is one `DISTINCT ON
  (metric_id)` query. Daily series take the latest row per UTC calendar day of `captured_at`,
  and the writer uses the same day definition, so one stored day can never split in two in a
  non-UTC session. The day-upserts are single SQL statements (CTE update-then-insert) because the
  pool hands out a connection per call and a hand-rolled transaction would not be one.
- **Timezones.** `toDateOnly()` formats a `date` column from local components (pg parses it at
  local midnight; `toISOString()` would land on the previous day east of UTC). `addUtcDays()` is
  the only day arithmetic, in `Date.UTC`, so a 23-hour DST day is a non-event. Gate dates are UTC
  calendar days on purpose.
- **Late data.** GSC is read 3 days back and the page-grain rows re-read 3 days each night
  because a "final" day is still revised. Help counters re-read 3 days. The gate freeze reads
  "what was known before the cutoff" (`latestByMetricAsOf`), so re-freezing the 1st on the 3rd
  reproduces the 1st.
- **Failures.** Every collector returns `{ recorded, skipped: [{ id, reason }], error? }`. A
  per-metric problem is a named skip and the run still answers 200; a whole-run failure sets
  `error` and the route answers 502 so Cloud Scheduler retries. The rule repeated in every file:
  a failed call records nothing, because a 0 would read as a collapse. "No data" is a word on the
  page, never a blank cell and never 0.
- **Known-gap vs fault.** The digest maps each registry `source` string to the cron that feeds
  it and prints the exact curl to re-run it; a source with no cron (Nexus endpoint) is reported as
  a known gap, not as a stale collector.

### A4. One definition, reused (the registry)

`src/lib/pm/registry-data.ts` is the single source: 80 metric definitions (9 manual, 6 gates).
From it: `npm run pm:seed` upserts `pm_metric` (idempotent, and since PR #100 retires rows the
registry no longer names); `scripts/pm/gen-metrics-doc.ts` renders `docs/pm/metrics.md`; every
Q4 ticket must cite a registered id in backticks (`pm-tickets` grades that hourly). The
`registry-parity.test.ts` pins:

- the committed doc equals the renderer output byte for byte (a hand-edited baseline fails CI);
- the count is exactly 80 and the gate set is exactly these six ids;
- every set-point ladder names a registry metric, ends exactly on that metric's target and
  target date, and sits on a direction-up metric (the light maths only reads correctly for up);
- `GATE_METRIC_IDS` in `gates.ts` equals the registry's `isGate` set;
- the freshness red line constant equals the registry target of `pm.dashboard_freshness_hours`;
- the gate metrics knowingly left without a ladder are named, so the list shrinks on purpose.

### A5. Targets and pace

- `SET_POINTS` in `gates.ts`: a monthly ladder per laddered metric, keyed by gate date
  (10-01, 11-01, 12-01, 12-31). `activeSetPoint()` = the first rung on or after today; after the
  last gate, the final rung stays active.
- `gateLight()`: latest / active rung >= 0.9 green, >= 0.6 amber, else red; no ladder or no
  sample = no light.
- `pctToTarget()`: % of the way from baseline to target, clamped at 0; a "hold the line" metric
  whose baseline equals its target reads 100 only while it is still at or above it.
- `gateCategory()` precedence: no sample beats everything; a stale or never-entered manual value
  beats its own number; then the light; then baseline comparison, direction-aware (a position
  going DOWN is improvement, not drift); else "tracking".
- `verdictLine()`: any red = OFF PACE, else any amber = WATCH, else any green = ON PACE, else
  NO READINGS YET, then `2/6 GREEN · 1 DRIFTING · 3 NO DATA`.
- Rung wording respects the print resolution: a gap that rounds to 0 is worded "UNDER 1 TO
  RUNG", never "+0"; only a raw zero may say "AT RUNG".
- Freshness: `DATA 14H` in the global strip, red above 24 h; a digest marks an auto metric stale
  above 48 h (weekly-written metrics get 8 days). Manual values grey out above 2x their expected
  frequency and appear in the overdue list.
- Gate freeze: at 06:00 UTC on the 1st and 2nd of each month, one row per registry metric is
  frozen (value, rung, the classifier word, when sampled, when frozen). A metric with no sample
  is a row with value NULL and status `no-data`, so "nothing was known" is recorded. The verdict
  is typed next to the frozen numbers (`pm_gate_note`).

### A6. What makes a number trustworthy there

1. Baselines are frozen with a date (`baseline_at`), most from the 2026-08-28 audit, five on
   their own date; the doc sentence and the seed both say which.
2. A scope difference is written on the metric, not fixed by editing the baseline (the four
   page-hygiene metrics: audit crawl was wider than the nightly sitemap crawl).
3. Provenance per sample (`source_run`) and an as-of per reading on every card.
4. The page reads Postgres only; no external API at render time, so the Score page answers on a
   morning when Google is down, and opening it costs no quota.
5. Pure rule modules with `now` as a parameter (`gates.ts`, `verdict.ts`, `scoreboard.ts`,
   `digest.ts`, `format.ts`), 32 test files under `src/lib/pm/__tests__/`; reader tests assert the
   SQL shape (`DISTINCT ON`, the UTC cast, the `manual:%` filter) and the pg-to-number coercion
   (numeric arrives as a string; a target compared to a string is the bug they test against).
6. A number policy module (`fmtConsole`): counts print as integers, one decimal only for
   positions and percentages, NaN and Infinity print as "no data" rather than "NaN".

### A7. What is NOT accurate (from code comments, docs and memory)

- `wallet.chrome_weekly_users` is Google-rounded; the listing flipped 9,000 to 10,000 for six
  days in September and back. Memory says: do not claim 10k. Rungs are in round hundreds for the
  same reason.
- GA4 users carry about 1/3 bot traffic; Nexus GA4 included the team until the Israel filter;
  the Nexus baseline of 14 predates the filter.
- GSC `.total` metrics are truncated sums if the 1000/500 row limits saturate (warned, not
  silently trusted). Page rows trail GA4 by about 3 days, so a page and its channel are never at
  the same freshness on one screen.
- The four site-hygiene baselines are not comparable to the nightly samples (scope note above).
- `nexus.*` never collected (#56 on pause); `gsc.gero.midnight_cluster_clicks` skipped until its
  cluster list exists; `ga4.nexus.trial_form_starts` skipped until an env var is set.
- `pm-tickets` stopped 2026-10-01 to 10-10 (expired GitHub token); `pm-youtube` had never
  written until 10-10 (first sample 805 subscribers). `CURRENT_SPRINT` is hard-coded in
  `collectors/tickets.ts` and must be bumped by hand.
- The weekly freshness metric reported a false STALE every week until PR #100 gave
  weekly-written metrics an 8-day allowance.
- Two ghost ids (`x.*.impressions_7d`) sat in `pm_metric` after a rename until the seed learned
  to retire rows.
- The 2026-09-17 sitemap alert (80 to 48) was a transient Contentful failure, not a real drop;
  the alert stayed open until acknowledged on 09-27.
- X delta on the tiles is weekly while the number is a 30-day window (documented, deliberate).
- `/seo-dashboard` reads GSC and GA4 live with a 1-hour cache through a second code path
  (`src/lib/seo/*`), so the same source is read two ways; only the registry path is tested.
- Production can be behind main; the PM code exists only on `origin/main` and feature branches
  lack `scripts/pm/`, which has bitten memory twice.
- Manual metrics: Semrush is a borrowed login, TestFlight needs a key nobody holds, Google Ads
  may not exist; those rows are blank by design.

### What IoS takes (A)

- **S. A `source_run` style stamp per reading.** Each snapshot platform block already says
  `"source": "hikerapi"`; add `source` to every manual entry (`manual:amir`, `cli:s4a-read`,
  `import:bandcamp-csv`) and to the follow-back file. Readers show it as the tooltip on the card.
- **S. Skipped reasons, not `None`.** `stats/collectors.py` returns `None` on failure and the
  snapshot carries `errors: []`. Make each collector return `{recorded, skipped: [{metric,
  reason}]}` like Gero's contract, write it into the snapshot, and show "IG: skipped, HikerAPI
  429" as a word on the page. `test_stats_collect_skip.py` already exists; extend it.
- **S. The freshness rule as one constant.** Today the page says "synced N days ago" (stale
  above 14) and a health dot says "newest snapshot <= 2 days". One rule, one place
  (`stats/targets.py` or a new `stats/rules.py`): red above 48 h for the daily sync, 10 days for
  the Monday Spotify read, 40 days for the IG export, with the word DATA 14H in the header.
- **S. Manual staleness = 2x the expected frequency.** `plans/targets.json` metrics of kind
  `collecting` and the manual platforms get a `frequency` (weekly | monthly | quarterly); older
  than 2x = greyed and listed under "overdue". Never-entered stays a different word from 0.
- **M. One registry file.** Today a metric is defined in three places: `plans/targets.json` (the
  6 gates), the `TRENDS` tuple in `score_board.py`, and `s.tracks` built elsewhere for the
  per-platform grid. Fold them into one `plans/metrics.json` with id, label, unit, source string,
  direction, kind, baseline + date, frequency, notes, area (one of the six). `targets.json` keeps
  only the period, rungs and the approval stamp. A test pins the doc (a generated
  `docs/metrics.md`) to the registry, like `registry-parity.test.ts`.
- **M. Direction-aware drift.** `_card()` has no `direction`; a follow-back floor or a
  followers:following ratio moving the wrong way should say "drifting", not sit on "collecting".
  Copy `gateCategory()` precedence: no data > stale manual > light > drift (direction) > tracking.
- **M. Gate freeze.** On the 1st of the month the daily sync writes
  `stats_snapshots/gate_YYYY-MM-01.json`: every registry metric, value as of the cutoff, rung,
  classifier word, sampled date. `/stats` gets a small "Gates" section (Nov 30, Dec 31) that
  reads these files, plus one text box per gate for Amir's verdict, stored in the same file.
  Re-freezing must reproduce the same numbers (read snapshots dated before the cutoff only).
- **M. Rounding honesty in the rung line.** `_rung_line()` prints `+0 ahead` when the gap is
  under one; adopt the under-one wording.
- **L. Reader tests on the readers.** `get_time_series()` dedupes newest-per-day by walking all
  snapshots; add tests for the two-snapshots-one-day case, the manual-entry-fills-a-gap case and
  the malformed-timestamp case, so a future change cannot split a day or lose a manual value.

### What IoS does not take (A)

- Postgres, Cloud Run, Cloud Scheduler, OIDC cron auth: IoS runs one launchd job on one Mac,
  by design (privacy first, no server). JSON files with atomic writes already do the job at 77
  snapshots; the one risk (reading all files per series) is far from mattering.
- The 28-day-to-30-day normalisation: IoS metrics are counts at a point in time (followers,
  listeners), not windowed sums, so there is nothing to normalise. Only an IG reach-30d would
  need it, and the screenshot already is a 30-day number.
- Keyword clusters, brand/non-brand split, page-grain evidence tables: there is no site.
- The hourly gauge table: nothing at IoS moves within a day.
- The ticket-cites-a-metric rule as a graded metric: nice idea, but `plans/tickets.json` is
  not GitHub and the areas already carry the link; a `metric` field on a ticket is enough, no
  compliance score.
- Alerts with acknowledgement: the health row with eight dots covers the same ground for one
  person; an alert table would be a second inbox for Amir, which the "no waiting-item
  reminders" rule forbids.

---

## B. The dashboard

### B1. What Gero shows, in order

Shell on every page: a left rail (SCORE, GATES, SHIP, SEO, X, LINKEDIN, YOUTUBE, ENTER, ADMIN,
longest-match active state) and a global status strip (`UTC clock · DATA 14H · ALERTS 0 ·
SHIP: X 3/5`). The strip has five honest states: loading, live, SESSION EXPIRED, DATABASE
UNAVAILABLE (a 503 from the status route when Postgres refuses), STATUS UNAVAILABLE.

`/pm` Score, top to bottom (`src/app/pm/page.tsx`):

1. Header: "Score" and the computed verdict line in mono (`ON PACE, 2/6 GREEN · 1 DRIFTING`; Gero itself joins the two halves with a dash).
2. PageIntro: two plain-English sentences saying what the page measures and when it updates.
3. Digest line: week ending, all-clear or N issues, link to `/pm/digest`. Worded in every
   state, including "none yet" and "not migrated", so a stopped cron is visible.
4. Alerts strip: only rendered when an alert is open, each with an Ack button.
5. Gate grid: the six gate metrics as 3x2 Cells (11 px caps label, 34 px mono numeral with
   unit, a delta line like `NOV 400 · −9 TO RUNG` or `BASE 26 · DRIFTING −4`, a 90-day
   sparkline, a `manual · entered 2026-10-03 · stale` tag where relevant).
6. Site LED strip: `SITE 11/13` and one 14 px square LED per check; failing checks list their
   condition and ticket ref; the full table sits in a collapsed `<details>`.
7. Ladder panel: two SVG charts, samples against the dashed rungs, baseline dash, active rung.
8. Wallet chart: hourly band (min/max) with the ledger of actions marked, window toggle.
9. Help Center panel in its own Suspense boundary (it reads the backend live; it may be slow
   and must not hold the score).
10. Track panels: Gero B2C, Midnight, Nexus B2B, metrics-only console tables (name, value,
    from-baseline). No tickets here; tickets live on `/delivery`.
11. Ticker: one mono line (`SHIP ON PLAN · 12 OPEN TICKETS · 83.3% CITE A METRIC · LIFT 0
    COMPUTED · WINDOWS FILLING`) and links to SHIP and GATES.

`/pm/gates`: one column per gate date, frozen rows, the typed verdict. `/pm/manual` (ENTER):
form table with last entry date and freshness word. `/pm/metric/[id]`: drill-down with trend,
drivers, evidence. `/x`: segmented account switch, four stat Cells with sparks read from the
DB (never from X), the queue, composer, mix dial. `/youtube`: Shorts queue with the channel
status (still on the interim light "bridge" styling). `/seo-dashboard`: 1,061-line client page
with scheduler, queue, keywords, drafts, analytics (live GSC/GA4, 1-hour cache), logs.
`/linkedin-dashboard` and `/admin`: forms.

### B2. Visual language

- One committed dark theme, no toggle. Tokens in `globals.css`: bg `#0D1418`, surface
  `#151D22`, line `#26363E`, text hi `#E6F1F3` / body `#B8C4C8` / dim `#7C8B90`, accent teal
  `#33CFE8`, good `#3ADC9B`, warn `#F5B94D`, bad `#FF6B5E`, each with a dark wash.
- IBM Plex Sans for UI, IBM Plex Mono for every numeral, id, timestamp and status word, with
  tabular figures. Scale 11 / 12.5 / 13.5 / 15 / 22 / 34 px; nothing below 11.
- Borders, never shadows. Chips carry the word, the wash only reinforces it. LEDs carry a
  title and a screen-reader word. State is never colour alone. WCAG AA checked per token.
- No chart library. Sparklines and ladders are hand-rolled SVG rendered on the server
  (`charts.tsx`, no `use client`), tested as pure geometry. Fewer than two plottable points draws
  nothing and the card says "collecting"; a flat series runs through the middle of the box so
  "steady" does not read as "bottomed out"; a NaN is filtered so one bad row cannot blank a chart.
- Copy policy: counts as integers, verdicts as words (ON PACE / DRIFTING / NO DATA), empty
  states say what happens next, never a file path or an npm command.

Live vs mocked: no mocks in the pm tree. Everything on Score is real Postgres data; the holes
are named on the page (NO DATA, never entered, not migrated). The Video Desk is built but not
deployed (PR open, shared DB, "never approve films before the deploy"). The seo-dashboard,
youtube and admin pages still carry the pre-console light styling inside the dark shell.

### B3. IoS today, honestly

`/stats` (`score_board.py` + `stats.html`) already mirrors the Score page: score line, six
cards with lights, rung line, progress bar and spark; health row (8 dots, each linking to its
source file); ladder charts; "This week" tiles with deltas; "What moved" with release art;
trend-only cards; per-platform tracks; manual-entry forms; Bandcamp sales card. Data:
`stats_snapshots/snapshot_*.json` (77 files, daily 08:45 launchd), `manual_entries.json`,
`spotify_s4a.json` (Monday read), `ig_followback.json` (monthly export). Targets in
`plans/targets.json` with the derivation rule and `approved_by / approved_on` written in. Fonts:
Marcellus (headings) + Inter (body), warm black `#080808` / platinum `#D6D1C8`.

**What Gero does better in data handling**

- One registry with tests pinning the doc, the gate set and the ladders to it. IoS defines
  metrics in three places (see A).
- Provenance and skip reasons per reading. IoS snapshots have `errors: []` and collectors
  return `None`.
- Freshness as a stated rule with a red line in the header. IoS has "synced N days ago" (stale
  above 14) and a 2-day health dot; two rules, both loose.
- Direction-aware classification and rounding-honest wording.
- The gate freeze and the typed verdict per gate. IoS has nothing frozen; a review re-reads a
  moving number.
- The verdict rule: any red = OFF PACE. IoS `_score()` says ON PACE when green >= half of the
  metrics with data, which can print ON PACE with a red card.
- Light thresholds stated against a rung with a published ladder date; IoS lights are 95/85 %
  of an interpolated plan line, which is finer but hides which rung is being graded.
- Manual values grey out by frequency; IoS shows "entered <date>" with no rule.
- Reader tests on SQL shape and coercion; IoS has 13 score-board tests and 6 target tests,
  none on `get_time_series()`.

**What IoS already does better**

- The targets file carries the rule that derived each number and the approval stamp; Gero's
  ladders are a constant in `gates.ts` with the reason in a comment.
- Baseline date per metric from day one (Gero added `baselineAt` as a fix after a wrong claim).
- Health dots link to the file and the date; Gero's LEDs link to a drill-down page.
- "What moved" per release with art: Gero has no per-item movers on the Score.
- Zero infrastructure: no DB, no scheduler service, no secrets on a cloud; a snapshot is a
  readable file Amir can open.
- The whole board never raises on a missing file (`score_board.py` docstring); Gero's page
  deliberately throws to an error boundary for metric reads.
- Brand fonts and a dark page that is already his, not IBM Plex.

### B4. Design brief: the IoS dashboard

Goal: one glance says where we stand, every number traces to a file and a date, and the page
looks like Inch of Shadow, not like a console.

**Frame.** Warm black `#0F0D0C` ground, platinum `#D6D1C8` ink (frame.md M2); surface one step
lighter (`#141211`), hairline `#2A2624`. Marcellus for the big numerals and section titles
(Albertus Nova stays Canva-only; no file). Jost 300/400 for labels, deltas and body (the
light electronic-lane face from Look-01; Inter is the current stand-in and can stay until Jost
is wired in). Numerals tabular. Status: the existing greens/ambers/reds, each with a dark wash;
the word always beside the colour. No shadows, no gradients, no teal.

**Information order** (top to bottom, nothing above the verdict):

1. Verdict line in Marcellus caps: `ON PACE · 4/6 GREEN · 1 DRIFTING · 1 COLLECTING`. Rule:
   any red = BEHIND, any amber = WATCH, else ON PACE; COLLECTING only when nothing has data.
2. Freshness and provenance strip in small Jost: `DATA 6H · IG hikerapi 11-05 · SC api 11-05 ·
   Spotify S4A read 11-03 · IG export 10-10 (26 d)`. Red word when a rule is broken. One line
   that says where every number on the page comes from.
3. The six gate cards (3x2, 2x3 on a phone): name, big numeral, unit, light word, rung line
   (`NOV 30 996 · +3 PAST RUNG`), progress bar baseline to target, 90-day spark, `as of` only when
   older than 3 days, `manual` tag when hand-typed. Who-emoji in the corner: 🤖 collected by
   itself, 🎃 Claude reads it (S4A, export), 🙋 Amir types it (reach screenshot, TikTok).
4. Health row: 8 dots, all-good collapses to `HEALTH 8/8`; a failing dot shows its label,
   reading, limit and a link to the file.
5. Ladders: one SVG per laddered metric (IG, SC, Spotify), the staircase through baseline and
   rungs, the real line, the now dot. Same as today, restyled.
6. This week: tiles and "What moved" with art. Keep.
7. By area, collapsed: 🎬 Socials (SC plays, likes, reposts, YT views), 🎵 Release (per-release
   SC stats, Bandcamp sales), 💶 Income (Bandcamp net, spend files), ⚙️ System (HikerAPI
   balance, Claude and OpenAI spend from `*_spend.json`). Areas with nothing to show are not
   drawn.
8. Gates: the frozen columns (Nov 30, Dec 31) with Amir's typed verdict. Empty until the first
   freeze; the line says "first gate freezes 2026-12-01".

**The 6-8 numbers that matter** (the cards and the strip): IG followers, IG follow-back %, IG
reach 30d, SoundCloud followers, Spotify monthly listeners, TikTok followers (collecting), plus
two trend numbers in the strip: followers:following ratio (floor 1:1, the ratio-comparison rule)
and YouTube subscribers. Nothing else above the fold.

**How pace shows.** The light is a word and a colour on the card; the rung line says the gap to
the next published rung in the metric's own unit; the progress bar says the share of the way
from baseline to target; the ladder chart shows the same three things as a picture. One rule
set, used by the card, the chart and the gate freeze, so they can never disagree.

**How freshness shows.** Strip at the top (one line), `as of` on any card older than 3 days,
`manual · entered <date> · stale` when older than 2x its frequency, a health dot for the sync
age. A collector that skipped shows the reason as a word on the card ("skipped: HikerAPI 429").

**What never goes on it.** Per-session activity (likes, follows, session scores beyond the one
health dot); outreach contacts or DJ names; anything from Amir's private network; release
captions or copy; ticket lists (they live on /tickets); engagement automation state (hands
off); a number without a source and a date; a 0 that means "not collected"; a target that moved
mid-period; an em-dash.

**Phone.** Cards stack one per row under 600 px; the strip wraps; sparks keep their height. The
existing claude.ai page pattern could carry a read-only copy, but /stats on the Mac is the
source; no second data path.

### What IoS takes (B)

- **S. Verdict rule and threshold fix.** Any red = BEHIND; the GREEN count out of all cards;
  lights graded against the active rung (90/60) with the rung date in the line.
- **S. Freshness strip** under the verdict, one line, from the one rule.
- **S. Who-emoji per card** (🤖🎃🙋) from the registry `source` string.
- **S. Collapse areas with nothing to show**; health row collapses to `8/8`.
- **M. Restyle in brand**: Marcellus numerals, Jost labels, M2 colours, hairlines, no shadows;
  check every size by the render-and-shrink rule on a phone.
- **M. Gates section** reading the freeze files, with the verdict box (depends on A's freeze).
- **M. Area grouping** of the per-platform grid using `plans/AREAS.md` labels.
- **L. Reader-layer tests + the registry file** (shared with A).

### What IoS does not take (B)

- IBM Plex, teal, the console look: the brand is Marcellus, platinum, warm black.
- The left rail and global strip across the whole RM: RM already has its own nav; one page is
  the dashboard, the rest are tools.
- The digest page and weekly digest row: `plans/weekly-stats.md` already is the Monday digest,
  and chat gets the Monday read; a second surface would be noise.
- Drill-down pages per metric with drivers and lift engine: no traffic to attribute; the
  release-level "What moved" already says what carried.
- Track panels for business lines (B2C, Midnight, B2B): the six areas are the IoS axis.
- The `/delivery` ship-vs-plan ticker: the "no posting reminders" rule rules it out.

---

## C. The review flow

### C1. What Gero built (Video Desk, spec 10-19, revision 11-04, built 11-05, not live)

One record per film in `x_film` (worktree migration): identity (title, account, family, tier,
series, episode, kind), variants (`square / vertical / landscape`, each with duration, size,
width, height probed on ingest), provenance (source `launchd | youtube-sync | upload`, edition
JSON, render path, YouTube id), history (`x_history posted | never | unknown`, posted date, post
id), gate (`gate_status pending | passed | held`, `gate_report` JSON with one row per check,
`gate_ran_at`), copy (tweet, reply, YouTube title/description/tags, `copy_edited`), plan
(`slot_at`, destinations, `plan_status`, approved_by, approved_at).

States (`plan_status`): `unplanned, proposed, needs-review, approved, posting, posted, skipped,
failed, dismissed`. The card shows one of six words: held, needs-you, approved, posted,
skipped, failed; "held" wins over any plan status.

The gate: five checks, each `pass | fail | na` with a one-line reason, rendered as five chips on
the card and the review panel. Numbers agree with the edition JSON and re-derive within 0.5
points; banned words across tweet, reply, YouTube text and on-screen text; visual sanity (six
key frames to Claude, fixed JSON answer: cut-off text, typos, wrong logo, black frames, wrong
palette); series rules (episode number, slot day, account, layout); format per destination
(variant exists, length, size, codec). Any fail = held, top of the queue with the reason, never
auto-fires, re-runnable. The gate runs on ingest and again before firing (checks 1 and 5).

Approve is one call: `validateApprove()` refuses if already posted, gate not passed, no slot or
slot in the past, no family, empty or too-long tweet, missing variant for a destination, banned
word in the final copy, series rule broken. It writes the copy edits, sets `approved`, creates
the bridge `x_post` (a unique index on the film id makes a double Approve impossible), queues a
private YouTube Short where asked. Hold adds a `manual` fail chip with "held by <who>: <reason>"
and pauses the bridged post. Editing an approved film's slot, copy, destinations, family or tier
sends it back to needs-review. A film whose slot passes unapproved becomes `skipped`, "missed,
not approved", never posted late. Keyboard: a approve, h hold, j/k next.

Gero's old way (`videos/_REVIEW/` and `_APPROVED/` with `-APPROVED` and `-superseded` names and
a Finder tag) is the thing Amir does not want. Gero's own memory records why: the `_APPROVED`
Midnight files turned out to be silent earlier cuts while the real finals sat in `_REVIEW/`;
the rule became "never trust the suffix, ffprobe every candidate". The parked registry design
(09-01) already concluded: film with versions underneath, identity by content hash plus the
source commit, human names are notes, never identity. The desk is that design, built.

### C2. Proposal for IoS: a Review page, no file moves

**Principle.** A file is identified by its path and its SHA-256, never by its folder or its
name. Approval is a field in the release JSON. The agent writes files and records; Amir decides;
nothing moves, nothing posts, nothing is deleted.

**Where it lives.** `releases/<slug>.json` gets a `review` block. Two surfaces read it: an RM
page `/review` (desktop, local) and a private claude.ai page (phone), built like
`plans/outreach-page/gen.py` from the same JSON with thumbnails embedded. Ticks from the phone
land in the page db collections `ticks` and `approvals` (the existing pattern) and are read back
with ArtifactData into the release JSON by the agent, same as `plans/outreach-batches.json`
today. RM `/review` writes the JSON directly. The JSON is the truth; the page db is a mailbox.

**Data model** (`releases/<slug>.json`, key `review`):

```
"review": {
  "items": {
    "r-023": {
      "kind": "render" | "cover" | "caption" | "post" | "story" | "thumbnail",
      "label": "Half the Night reel, 9:16, cut 3",
      "area": "socials",                       # one of the six areas
      "destination": ["ig-reel", "yt-short"],  # where it would go, for the format check
      "path": "videos/half-the-night/renders/reel-v3.mp4",   # never changes
      "sha256": "…", "bytes": 48213340,
      "probe": {"duration_s": 14.9, "w": 1080, "h": 1920, "audio": "aac", "fps": 30},
      "made_by": "claude" | "amir" | "auto", "made_at": "2026-11-06T13:10:00",
      "source": {"project": "videos/half-the-night", "commit": "abc1234", "prompt_id": null},
      "version": 3, "supersedes": "r-019",
      "text": null,                            # captions and posts carry their text here
      "checks": [ {"id": "safe-zone", "verdict": "pass", "reason": ""},
                  {"id": "no-text-over-face", "verdict": "fail", "reason": "title crosses the face at 0:04"},
                  {"id": "em-dash", "verdict": "na", "reason": "no text layer"} ],
      "gate": "held" | "passed" | "pending",   # any fail = held
      "state": "draft" | "needs-you" | "approved" | "change" | "dropped" | "superseded" | "used",
      "ticks": {"by": "amir", "at": "2026-11-06T18:02:00", "via": "phone" | "rm" | "chat", "note": "move the title down"},
      "approved": {"by": "amir", "at": "…", "sha256": "…"},   # the hash that was approved
      "used": {"where": "instagram", "at": "…", "by": "amir", "ref": "post url"}
    }
  },
  "updated_at": "…"
}
```

Rules in the model: `approved.sha256` must equal the file's current hash, or the item falls back
to `needs-you` with a chip "file changed after approval". A new version of the same thing is a
new item with `supersedes`; the old one becomes `superseded`, its file stays where it is.
`used` is written by Amir or by the agent only from his words ("posted it"), never from a
posting action, because the agent never posts.

**States and what happens**

| State | Meaning | Agent does | Amir does |
|---|---|---|---|
| `draft` | made, checks not run yet | runs the checks, computes hash and probe, sets `gate`, moves to `needs-you` (or stays `held` inside needs-you) | nothing |
| `needs-you` | waiting for him; chips visible | nothing; it may propose one fix in chat if asked | ticks approve / change / drop on phone or RM |
| `change` | he wants a change; note attached | makes the new version as a NEW item with `supersedes`; never overwrites the file he looked at | reviews the new item |
| `approved` | he said yes to this hash | records `approved`, prepares the post text and the publish checklist (location, tags, audio name) in chat; never posts | posts it himself, says "posted" |
| `used` | it went out | records `used` with his reference, starts the stats log for it | nothing |
| `dropped` | not this one | records it; the file stays; nothing is deleted | nothing |
| `superseded` | replaced by a newer item | records the link; file stays | nothing |

A `held` gate inside `needs-you` means at least one check failed; the item sits at the top with
the reason. Amir can still approve a held item (it is his call, the chip stays as a record), the
way Gero's hold needs a human to clear it but the human may override.

**The chips** (checks run by the agent, each pass / fail / na with a reason; all local):

- `format`: size, ratio, duration, codec, audio stream present, per destination
  (`video_resizer.py` and `artwork_resizer.py` limits, Machine-07).
- `safe-zone`: Meta safe zone 270 / 672 / 65 and the 11 pt minimum by render-and-shrink.
- `no-text-over-face`: subject position per shot vs type placement (frame checks already
  described in memory; verified on rendered frames, never assumed).
- `first-3s`: no branding in the first three seconds; sting, handle and credit rules
  (videos/PLAYBOOK).
- `brand`: face family, mood pair from frame.md, one face per piece, no bold hierarchy.
- `copy`: no em-dashes, no meta lines, no feedback asks, handle spelled `inch_of_shadow`,
  credits per the handles rule, "Hi all / Hope you will like it" kept.
- `handles`: every tagged handle verified against export, tracker, SI or a real profile; unknown
  ones flagged ❓, never passed.
- `hash`: current SHA-256 equals the recorded one.
- `imagine-review`: for AI images, the existing `imagine_review.py` verdict (pass / fix, issue
  areas) becomes this chip; it already refuses anything holding his face.

Chips are words with a colour wash; a failing chip carries its one-line reason; `na` is grey.

**The pages.**

- RM `/review`: one list, newest first, grouped by state (needs-you first, held on top of it),
  filter by release and area. A row = thumbnail or text preview, label, kind, area emoji, who
  made it, version, chips, three buttons (Approve / Change + note / Drop). Keyboard a / c / d,
  j / k. Approved and used items collapse under "Done". Nothing on the page can move, rename,
  delete or post.
- Phone page: the outreach card pattern with the same three ticks; ticks save to the page db;
  the agent reads them back on the next turn and writes the JSON. The page says "not saving" when
  opened signed out, as the outreach page does.

**What the agent does on each turn that touches review:** read the page db, write any new ticks
into the JSON (with `via: phone`), run checks on new drafts, update chips, regenerate the phone
page if items changed, and tell Amir in short bullets what is waiting and what changed. It
proposes; it does not decide.

**What it must never do**

- Post, schedule, upload, send, or create a draft on any platform from an approval. Approval
  means "this file may be used"; the use is his.
- Move, rename, delete or overwrite a reviewed file. A change is a new file and a new item.
- Approve on his behalf, infer approval from silence, or carry an approval from one item to its
  next version (the hash rule enforces this).
- Mark `used` without his words.
- Edit the engagement automation, the release checklist or stats from the review page.
- Send his face to any AI review (the imagine-review refusal stands).
- Re-list what waits on him outside the page (the "no waiting-item reminders" rule).

### What IoS takes (C)

- **S. The `review` block** in the release JSON with items, states, hash and `supersedes`; the
  agent writes it for every render, cover, caption and post draft from now on.
- **S. Hash-bound approval** (`approved.sha256` must match) and the superseded link.
- **S. Phone page** generated from the JSON with the outreach `gen.py` pattern and the same
  `ticks` / `approvals` collections.
- **M. The check runner** producing chips: format probe (ffprobe), safe-zone and text-over-face
  frame checks, copy rules, handle verification, hash; imagine-review wired in as a chip.
- **M. RM `/review`** page with keyboard, grouped by state, no destructive actions.
- **L. A pre-use re-check**: when Amir says "posting this now", re-run format, hash and copy
  on that item and answer in one line before he posts; same idea as Gero's pre-fire gate, with
  Amir as the firing mechanism.

### What IoS does not take (C)

- `_REVIEW` / `_APPROVED` folders, `-APPROVED` suffixes, Finder tags: identity by folder is
  the failure Gero's own memory records.
- The slot table, planner rules, urgent mode, Sunday proposer, the posting tick: IoS never
  posts, and the "no posting reminders" rule stands; a slot would be a reminder in disguise.
- The bridge to `x_posts` and YouTube upload from the panel: no automated publishing surface
  exists at IoS by design.
- Keyframes sent to a model as a default check: his face is in most frames; the imagine-review
  refusal rule applies, so the visual checks stay local (frame position, safe zone, text
  placement) unless an image is model-made and face-free.
- A GCS upload door and signed URLs: files are already on the Mac; the page carries thumbnails
  only.
- Family and tier taxonomy: the six areas plus the release slug already say what an item is.

---

## Notes outside scope, one line each

- Gero's Chrome listing lesson applies to IoS Spotify numbers: a weekly S4A read is a sample,
  not a trend, until there are several; the sparkline rule "under two points draws nothing" is
  already in `stats_tracks.sparkline` and should stay.
- `stats/storage.get_time_series()` opens every snapshot file per call; at 77 files it is fine,
  at 1,000 it will be slow. A small daily index file would fix it when needed, not now.
- The Gero memory index keeps one-line entries; the IoS index is over its size limit and
  truncates (also noted in the first pass).
