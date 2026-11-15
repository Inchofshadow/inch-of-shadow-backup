# IG ratio plan to Dec 31 (1.2:1), 2026-11-12

Asked by ⚙️ System (Amir "Yes, send it", 11-12). Read-only so far; nothing changed.

## Facts (from disk)

- Now (11-11 snapshot): 992 followers / 1,016 following = 0.98:1.
- Followers grew 966 -> 992 from 11-02 to 11-11: about +2.9 a day. Following grew 951 -> 1,016 (+65) in the same days.
- 28 IG sessions left to Dec 31 (Mon/Wed/Fri/Sat from 11-13). Caps: 16 follows, 8 unfollows, 12 likes.
- Unfollows per session since 11-06: 2, 0, 0, 0. Planner today: 0 eligible (26 verified non-followers blocked by the 21-day window rule, 58 unverified).
- Why unfollows stalled: the 11-10 follower-list fetch returned 979 rows but only 876 unique names (103 duplicates, about 116 real followers missing). The follow-back check needs the list within 2% of 992, so it rightly refused it. Last trusted check: 11-03. No new "does not follow back" checks = no unfollows.
- Side effect: si_follow_flags.py checked coverage with the row count (979), not unique names, so it applied the 11-10 list and set "follows you" to False on 8 SI contacts (e.g. sofiaxrb, glue.berlin). Some may be real unfollows, some list gaps.
- From the 11-10 list: 474 accounts Amir follows are not in the follower list (an over-count, since the list missed ~116 followers). 83 of them are engine follows; 391 are older follows the engine does not track.

## Projection (hypothesis, from the last 9 days' pace)

- Followers on Dec 31: about 1,135 if the pace holds.
- 1.2:1 at 1,135 followers needs following at about 945 or fewer: about 70 fewer than today.

## Options

A. Fix the follower-list fetch (dedupe, refetch until within 2%), refresh lists twice a week, raise unfollows 8 -> 16. Engine follows only. Following stays about flat, so the ratio lands near 1.1:1. Misses 1.2.
B. A, plus a sweep of the older follows that don't follow back (the 391, minus protected and personal), about 8 extra per session from a clean list. Following goes down about 150-200, so 1.2:1 is reachable. Needs Amir's yes: the engine only unfollows its own follows today.
C. A, plus follows 16 -> 8. Following drops, but follower growth slows too (follows drive follow-backs). Uncertain, may still miss.

Recommended: fix the fetch first (needed in every option), then B.

## Status 2026-11-14 (Amir chose B on 11-12)

| | Followers | Following | Ratio |
|---|---|---|---|
| 11-11 | 992 | 1,016 | 0.98 |
| 11-14 | 997 | 1,046 | 0.95 |
| After the sweep (est.) | ~1,000 | ~865 | ~1.16 |
| Dec 31 target | ~1,135 | ≤ ~945 | 1.2 |

- Picks page (plans/ig-sweep-page, https://claude.ai/artifact/8W74pNWcQcfxa4ZnGdyQuu): 321 old non-followers. 11-14: ~181 going, ~122 staying, ~18 open (his taps + suggestions). Contacts of all 321 saved first (plans/ig-follow-contacts-2026-11.md). HTN send list, DM/booking contacts and Shadow Archive accounts are tagged.
- Likes stopped for the 17 going accounts that were like targets (SI ig_blocked, Amir 11-14).
- Following still grows ~+14 a session (16 follows, engine unfollows stalled on the unreliable follower list), so the sweep alone lands near 1.16. Reaching 1.2 also needs the engine's own unfollows working again (option A part: a follower list that passes the 2% check; HikerAPI paging repeats pages) or fewer follows per session.
- Not built yet: the run that executes his picks (untracked unfollows in a session, about 8 extra a session). Needs Amir's final go and an engine change (his yes).
- Follow pool refill: 11-14 builder (9 new), Sun 11-15 09:00 builder on 12 seeds + checks, Mon 09:30 dispatcher checks.
