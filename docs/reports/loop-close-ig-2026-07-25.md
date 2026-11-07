# IG loop 2026-07-25 — closed automatically

**Score: 4/10**

Deductions:
- -3 cap violation: ig_like 26 > 25
- -3 cap violation: ig_unfollow 9 > 8

Actions: ig_follow: 10, ig_like: 36, ig_unfollow: 9

**POOL LOW: 10 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 55 click events in ig_session_2026-07-25.jsonl
  {'ig_follow': 10, 'ig_like': 36, 'ig_unfollow': 9}
  Unique handles touched: 45

[OK] Merged 55 events into engagement_log.json
[OK] Tracker synced: {'follows_added': 10, 'follows_skipped_dup': 0, 'follows_skipped_history': 0, 'unfollows_moved': 9, 'unfollows_not_found': 0, 'reciprocators_visual_guard_caught': 0}
[OK] Queue synced: {'queue_followed': 10, 'queue_skipped_stale': 0, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 0}
[OK] Archived session log to ig_session_2026-07-25.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 10 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  [!] last_builder_run is 22 days old -- the queue may need a fresh ig_queue_builder.py pass for NEW candidates
```

**NEEDS AMIR — IG autonomy paused: cap violation: ig_like 26 > 25**
Run `close_loops.py --resume --platform ig` after review.
