# IG loop 2026-08-07 — closed automatically

**Score: 4/10**

Deductions:
- -3 severe shortfall: ig_follow 4/10
- -3 severe shortfall: ig_like 12/25

Actions: ig_follow: 4, ig_like: 16, ig_skip: 18, ig_unfollow: 9

**POOL LOW: 18 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 47 click events in ig_session_2026-08-07.jsonl
  {'ig_follow': 4, 'ig_like': 16, 'ig_skip': 18, 'ig_unfollow': 9}
  Unique handles touched: 42

[OK] Merged 47 events into engagement_log.json
[OK] Tracker synced: {'follows_added': 4, 'follows_skipped_dup': 0, 'follows_skipped_history': 0, 'unfollows_moved': 9, 'unfollows_not_found': 0, 'reciprocators_visual_guard_caught': 0}
  [!] Unrecognized reach skip reason (entry left pending): 'follow_button_not_rendered' @auguste_nuncino
  [!] Unrecognized reach skip reason (entry left pending): 'grid_load_error_persistent' @werthealiens_label
  [!] Unrecognized reach skip reason (entry left pending): 'followers_out_of_range' @jil_lahr
  [!] Unrecognized reach skip reason (entry left pending): 'followers_out_of_range' @jasonjppeters
  [!] Unrecognized reach skip reason (entry left pending): 'already_following' @alphanova_music
  [!] Unrecognized reach skip reason (entry left pending): 'grid_load_error_persistent' @calystarrmusic
[OK] Queue synced: {'queue_followed': 4, 'queue_skipped_stale': 1, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 6}
[OK] Archived session log to ig_session_2026-08-07.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 18 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

**NEEDS AMIR — IG autonomy paused: 2 consecutive IG scores <= 5: [0, 4]**
Run `close_loops.py --resume --platform ig` after review.
