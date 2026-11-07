# SC quarterly review, October 2026

Run 2026-10-01 from the maintenance checklist. Read-only analysis; no automation changed.

## 1. Seed review

Per-seed yield cannot be measured: candidates do not record which seed found them,
and the tracker deletes an account when it is unfollowed, so recent periods keep only
the accounts that followed back (the first pass read 59-75% follow-back, which was that
bias). Era totals below are computed from the full follow log instead (every logged
follow up to 2026-09-21, i.e. at least 10 days old).

| seeding era | follows | followed back | rate |
|---|---|---|---|
| A: curated label seeds only (to 07-23) | 454 | 50 | 11% |
| B: reciprocator seeds (07-24 to 09-02) | 142 | 28 | 20% |
| C: 35 reciprocator seeds + labels, genre gate + rejection memory (09-03 to 09-21) | 138 | 36 | 26% |

Reading: seeding from accounts that followed back nearly doubled the rate, and the
09-03 split plus the click-time genre gate lifted it again. Keep the 35/20 split.
"Labels crawled 0x since 07-24" is resolved by that split (label seeds fill the
remaining slots).

Band breakdown for eras B and C is not reliable: most recent follows were logged
without a follower count.

## 2. Law diff

Config SESSION_* = scorer caps = SOP 4.1 = session task: 20 follows, 20 warm-up likes
(32 like cap), up to 20 unfollows, 60-action stop, 10-day window. Two legacy-section
mentions of the 14-day window updated. No conflicts.

## 3. Experiments

- 600-1000 band (pre-committed rule: >=10% keep, <5% revert): era A mature cohort
  10/84 = 12% -> KEEP. Recent eras too thin to judge per band.
- In flight, verdict dates: daily sessions + 10-day window (review 2026-10-06);
  PASS C 90-day track window (since 09-18: 0-3 likes a session, pool still thin).

## 4. Goals

Oct 31: 420 followers / ratio 1.1 (set 09-29). Needs +3.7/day from 309; late
September ran ~4/day. Achievable, no slack for blocked days (09-30 and 10-01
mornings lost to the apartment-bot Chrome).

## Proposed (not done, for Amir's decision)

1. Keep unfollowed accounts in the tracker (flag no_longer_following instead of
   deleting) and log the follower count with every follow, so band and cohort
   analysis work again.
2. Record the seed that found each discovery candidate, so next quarter's seed review
   can rank individual seeds.
