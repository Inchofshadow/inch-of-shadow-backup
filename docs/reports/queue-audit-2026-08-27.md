# Queue Freshness Audit — Thursday 2026-08-27

**Planned:** audit ~60 unaudited pending candidates + re-check 12 borderline SI contacts.
**Actual:** two runs; re-check deferred. ~68 IG API calls total for the day.

## Run 1 (~12:57) — died on auth
`--count 60`: HTTP 401 at candidate 7/60 — `.env` session cookies had expired
(browser login itself was fine). Nothing persisted; ~7 calls spent. Amir
refreshed `sessionid`/`csrftoken` via DevTools (~13:15); session verified with
one `--whoami` probe (@inch_of_shadow).

## Run 2 (~13:25, `--count 50 --override-ledger`) — completed
- **Fresh (vetted, audit_date=2026-08-27): 20** — incl. re-confirmed
  @rafael_sebastian__, @andrewredhand, and @transgression_music
  (reminder: needs `keep_following` once followed, per standing note).
- **Stale (marked skipped_stale): 6** — @pleasureofsin_xo (79 followers),
  @artem.egorov (14.1K), @barbicastelvi (3.9K), @electra.collective (0 posts),
  @onav_onav_ (3.5K), @tigerweeds_ath (last post 43d).
- **Fetch errors: 24** — positions 29–34 are the six documented perma-400
  accounts; then **16 consecutive 400/404 through candidate 50**, including
  known-active accounts (@cultivated_electronics, @irakli.wav,
  @distantgaze_records).

## The error streak — suspected soft throttle (unconfirmed)
Two hypotheses: (a) IG soft-throttled `web_profile_info` mid-run after the
perma-400 cluster; (b) a contiguous ancient dead tail batch. No CAPTCHA, no
401/429, no account warning. Recorded in `detection_events.json`.
**Action: all further IG API calls stopped for the day; the 12-contact
borderline re-check is deferred** (those labels remain excluded by
LABEL_CEILING_STALE_GUARD, so no exposure).

## State after
- Vetted Reach pool: **20** (threshold 30) — below target but sufficient for
  Friday (9 follows) and Saturday.
- Pending: 752. Ledger: audit claimed 12:57; run 2 as override continuation;
  `ig_borderline_recheck` NOT run.
- Queue backup: `backups/ig_target_list.json.bak.20260827_pre_audit`.

## Friday 2026-08-28 plan
Session proceeds (browser clicks, different surface). The morning follow-back
checker doubles as the API health probe: cascading 400s again = confirmed
throttle → no sweep (the 1-day staleness gate blocks it anyway), record, and
likes/follows continue in-browser.

## Script gaps observed (fix candidates)
1. The audit has **no consecutive-400 circuit breaker** — it burned 16 calls
   into the error streak (§4.3 says cascading 400s = stop immediately).
2. The six perma-400 accounts are re-fetched every audit run — they should be
   marked `skipped_stale:perma_error` after N failed audits instead of
   burning 6 calls per run.
