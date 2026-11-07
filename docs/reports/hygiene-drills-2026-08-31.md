# Watchdog, restore drill, tier-drift analysis — 2026-08-31 evening

## Watchdog (new, live)
`ig_heartbeat.py` + launchd agent `com.inchofshadow.ig-heartbeat` (nightly
22:30, independent of the dispatcher it watches). Checks: dispatcher logged
within 30h; an IG session processed within 4d (unless paused); test suite
green. Alerts via macOS notification + dispatch-log line; logs one heartbeat
line when all green. First run immediately caught a real defect: the ledger
tests failed after 21:00 (the 2.0 hours gate made the suite time-dependent —
it would have false-alarmed every night). Tests now inject a fixed daytime
clock; suite green day and night (348).

## Backup restore drill — ALL PASS
1. Newest tracker backup parses, schema valid, restorable copy written.
2. archive_pre_2026-08-31.tar.gz extracts; members parse.
3. Git-history restore (HEAD~8 tracker) parses.
4. Newest engagement_log backup parses.
5. Newest queue backup parses (>1000 entries).
Backups are real backups, not hopes.

## Tier-budget drift (decision for Amir)
Budgets were sized to May pools (8/16/110/31). Today:

| Tier | Budget | Pool now | Pool share |
|---|---|---|---|
| T1 core DJs 4-5 | 40% | 11 | 7% |
| T2 labels 4-5 | 35% | 13 | 8% |
| T3 DJs 2-3 | 15% | 110 | 70% |
| T4 labels 2-3 | 10% | 24 | 15% |

75% of every session's likes chase 24 accounts (15% of the eligible pool)
on 25-45d cooldowns — this is WHY sessions kept landing on contacts with
nothing new to like (six dead slots on 08-26). The no-new-content cooldown
treats the symptom; the split is the cause.
Proposed rebalance for Amir: T1 25% / T2 20% / T3 40% / T4 15% — keeps the
DJs-over-labels emphasis (T3 IS DJs, just score 2-3) while pointing likes
where supply exists. NOT applied — awaiting his call.
