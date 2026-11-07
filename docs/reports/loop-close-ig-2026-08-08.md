# IG loop 2026-08-08 — closed automatically

**Score: 2/10**

Deductions:
- -2 skip ratio 26/35 (stale/junk queue)
- -3 severe shortfall: ig_follow 0/10
- -3 severe shortfall: ig_like 1/25

Actions: ig_like: 1, ig_skip: 26, ig_unfollow: 8

**POOL LOW: 18 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 35 click events in ig_session_2026-08-08.jsonl
  {'ig_like': 1, 'ig_skip': 26, 'ig_unfollow': 8}
  Unique handles touched: 35

[OK] Merged 35 events into engagement_log.json
[OK] Tracker synced: {'follows_added': 0, 'follows_skipped_dup': 0, 'follows_skipped_history': 0, 'unfollows_moved': 8, 'unfollows_not_found': 0, 'reciprocators_visual_guard_caught': 0}
[OK] Archived session log to ig_session_2026-08-08.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 18 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

**NEEDS AMIR — IG autonomy paused: 2 consecutive IG scores <= 5: [4, 2]**
Run `close_loops.py --resume --platform ig` after review.
