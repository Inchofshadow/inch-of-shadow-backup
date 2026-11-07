# IG loop 2026-07-24 — closed automatically

**Score: 4/10**

Deductions:
- -3 cap violation: ig_like 27 > 25
- -3 severe shortfall: ig_unfollow 3/8

Actions: ig_follow: 8, ig_like: 27, ig_skip: 3, ig_unfollow: 3, ig_unfollow_skip: 5

**POOL LOW: 20 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 46 click events in ig_session_2026-07-24.jsonl
  {'ig_follow': 8, 'ig_like': 27, 'ig_skip': 3, 'ig_unfollow': 3, 'ig_unfollow_skip': 5}
  Unique handles touched: 38

[OK] Merged 46 events into engagement_log.json
  WARN: ig_unfollow @oliv__paula but not in active_follows -- skipping
  WARN: ig_unfollow @ezeszen but not in active_follows -- skipping
  WARN: ig_unfollow @bplastic.collective but not in active_follows -- skipping
[OK] Tracker synced: {'follows_added': 0, 'follows_skipped_dup': 8, 'follows_skipped_history': 0, 'unfollows_moved': 0, 'unfollows_not_found': 3, 'reciprocators_visual_guard_caught': 0}
[OK] Queue synced: {'queue_followed': 8, 'queue_skipped_stale': 0, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 0}
[OK] Archived session log to ig_session_2026-07-24.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 20 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  [!] last_builder_run is 21 days old -- the queue may need a fresh ig_queue_builder.py pass for NEW candidates
```

**NEEDS AMIR — IG autonomy paused: cap violation: ig_like 27 > 25**
Run `close_loops.py --resume --platform ig` after review.
