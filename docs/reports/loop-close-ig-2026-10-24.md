# IG loop 2026-10-24 — closed automatically

**Score: 6/10** (execution vs plan)
**Growth: 0 / 11 follows** — short by 11; supply, not execution, when the score is high


Deductions:
- -3 severe shortfall: ig_follow 0/1
- -1 shortfall: ig_like 3/6

Actions: ig_like: 3, ig_skip: 3, ig_vet: 2

**POOL LOW: 0 vetted targets (<= 30) — schedule a queue refresh.**

## Merge output
```
Found 8 click events in ig_session_2026-10-24.jsonl
  {'ig_like': 3, 'ig_skip': 3, 'ig_vet': 2}
  Unique handles touched: 6

[OK] Merged 6 events into engagement_log.json
  [!] Unrecognized reach skip reason (entry left pending): 'profile_not_found' @aametzz_
  [!] ig_vet @leonardo.bartolozzi unusable (missing followers/posts/private) -- left unvetted
  [!] ig_vet @duxevy unusable (missing followers/posts/private) -- left unvetted
[OK] Queue synced: {'queue_followed': 0, 'queue_skipped_stale': 0, 'queue_not_in_queue': 0, 'queue_skip_unrecognized': 1, 'queue_vet_pass': 0, 'queue_vet_fail': 0, 'queue_vet_unusable': 2, 'queue_vet_revived': 0, 'queue_already_following': 0}
[OK] Archived session log to ig_session_2026-10-24.jsonl.bak

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
**Reach pool is down to 0 vetted candidates -- needs an audit before it runs out.**
(threshold 30; refill: audit 60-80 from the un-audited pending tail on a silent-skip day)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  [!] last_builder_run is 55 days old -- the queue may need a fresh ig_queue_builder.py pass for NEW candidates
```
