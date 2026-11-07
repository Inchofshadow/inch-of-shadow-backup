# IG loop 2026-08-10 — closed automatically

**Score: 4/10**

Deductions:
- -3 severe shortfall: ig_follow 0/10
- -3 severe shortfall: ig_like 3/25

Actions: ig_like: 3, ig_skip: 9, ig_unfollow: 9

**POOL LOW: 15 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 21 click events in ig_session_2026-08-10.jsonl
  {'ig_like': 3, 'ig_skip': 9, 'ig_unfollow': 9}
  Unique handles touched: 21

[OK] Merged 21 events into engagement_log.json
[OK] Tracker synced: {'follows_added': 0, 'follows_skipped_dup': 0, 'follows_skipped_history': 0, 'unfollows_moved': 9, 'unfollows_not_found': 0, 'reciprocators_visual_guard_caught': 0}
  [!] Unrecognized reach skip reason (entry left pending): 'button_missing_after_reload' @auguste_nuncino
[OK] Queue synced: {'queue_followed': 0, 'queue_skipped_stale': 2, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 1}
[OK] Archived session log to ig_session_2026-08-10.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 15 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

**NEEDS AMIR — IG autonomy paused: 2 consecutive IG scores <= 5: [2, 4]**
Run `close_loops.py --resume --platform ig` after review.
