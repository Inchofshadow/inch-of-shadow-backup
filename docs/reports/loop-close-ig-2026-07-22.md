# IG loop 2026-07-22 — closed automatically

**Score: 5/10**

Deductions:
- -3 cap violation: ig_like 40 > 25
- -1 shortfall: ig_follow 7/10
- -1 shortfall: ig_unfollow 4/8

Actions: ig_correction: 1, ig_follow: 7, ig_like: 40, ig_skip: 59, ig_unfollow: 4, session_pause: 1

**POOL LOW: 28 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 112 click events in ig_session_2026-07-22.jsonl
  {'ig_correction': 1, 'ig_follow': 7, 'ig_like': 40, 'ig_skip': 59, 'ig_unfollow': 4, 'session_pause': 1}
  Unique handles touched: 100

[OK] Merged 111 events into engagement_log.json
[OK] Tracker synced: {'follows_added': 7, 'follows_skipped_dup': 0, 'follows_skipped_history': 0, 'unfollows_moved': 4, 'unfollows_not_found': 0, 'reciprocators_visual_guard_caught': 0}
  [!] Unrecognized reach skip reason (entry left pending): 'follow_button_unavailable' @auguste_nuncino
  [!] Unrecognized reach skip reason (entry left pending): 'queue_batch_skip' @lvsauvage
  [!] Unrecognized reach skip reason (entry left pending): 'queue_batch_skip' @the.olaf.hund
  [!] Unrecognized reach skip reason (entry left pending): 'queue_batch_skip' @francedegriessen
  [!] Unrecognized reach skip reason (entry left pending): 'queue_batch_skip' @zak_de_danube
[OK] Queue synced: {'queue_followed': 1, 'queue_skipped_stale': 4, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 5}
[OK] Archived session log to ig_session_2026-07-22.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 28 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  [!] last_builder_run is 19 days old -- the queue may need a fresh ig_queue_builder.py pass for NEW candidates
```

**NEEDS AMIR — autonomy paused: cap violation: ig_like 40 > 25**
Run `close_loops.py --resume` after review.
