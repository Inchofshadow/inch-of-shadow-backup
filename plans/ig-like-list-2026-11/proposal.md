# 🎬 Socials 27 · Instagram like list refresh: proposal (2026-11-06)

Checked on HikerAPI 2026-11-06, 122 calls, read-only (`check_like_targets.py`, raw results in `like_targets_check.json`). Nothing was written to SI, the engagement log or the config.

## Why likes ran 5/12 on 11-04

- The like budget goes to T1 (score 4-5 DJs/artists) and T2 (score 4-5 labels) only. SI has just **23** contacts in those two tiers.
- 22 of the 23 were on cooldown (25-45 days), so the engine filled all 12 slots from T3 (score 2-3 DJs, budget 0%, "retired"). The dead accounts are in T3.
- SI data for these contacts was enriched in April 2026 (7 months old).

## Check result (63 accounts: all 23 T1/T2 + 40 T3 that are off cooldown)

| Status | T1 | T2 | T3 |
|---|---|---|---|
| active (post within 90 days) | 10 | 11 | 21 |
| inactive (no post in 90+ days) | 1 | 1 | 15 |
| private | 0 | 0 | 2 |
| gone | 0 | 0 | 1 |
| no posts | 0 | 0 | 1 |

Remove from the like rotation (20):
- T1/T2: @dollkraut (138d), @internationalfeelibiza (133d)
- T3 inactive: @microlith_, @halincandenzamusic, @s.loth030, @positivesource, @erhalder, @sync_berlin, @claudiobrioski, @fierobanda, @armonics.wave, @abnormal.load, @autobahnmusik, @tamburineri, @gen.y.official, @volodymyr.gnatenko, @itsmiemusic
- T3 private/gone/empty: @piecinski, @thisisdjkitty, @xmtsk, @gesloten_cirkel

Keep (42 active): T1 10, T2 11, T3 21 (handles in `like_targets_check.json`).
Not checked: 59 T3 accounts still on cooldown.

## Supply math

- 42 active accounts on their cooldowns give about 32 likes a month.
- 4 sessions a week is about 17 sessions a month, so the list supports about **2 likes per session**, while the cap is 12.
- Cleaning the list stops the wasted slots. It does not fill 12.

## Options for the gap (Amir decides)

1. Grow T1/T2: 47 score 4-5 DJs/artists/labels in SI have no IG handle. Find their handles on HikerAPI (about 50-100 calls, one day), show them for a yes, then add them.
2. Lower the likes cap from 12 to what the list supports (about 3) until the pool grows.
3. Both: cap down now, back up as the pool grows.

## How the removal would be written (after the OK)

Not decided yet. The engine already skips contacts with `ig_handle_dead`, `ig_is_private` or a name in the engagement log's `hidden` list. Which field fits the inactive ones (who may post again) gets picked after the OK, and the exact write is shown before it runs.

## Handle search (2026-11-06, Amir "Yes, find more")

45 score 4-5 SI DJs/artists/labels without an IG handle, searched on HikerAPI (109 calls, read-only, `find_handles.py`, raw in `handle_candidates.json`). Every match was compared with SI (city, SoundCloud, bio).

Confirmed, active and in like range (3), proposed to add:
- @mori_ra (Mori-Ra, DJ, Osaka, Japan; 4,247 followers; SoundCloud matches)
- @fane.e.label (Fanée, label by Anetha; 2,024; SI SoundCloud bio matches)
- @alfamatrix (Alfa Matrix, label, Brussels, Belgium; 2,639; "official account" in bio)

Wrong person (5): @__acidalia, @franciscofarfan9, @demidigital, @planeterouge_, @fabrika_records.
Right account but too big for likes (label > 5,000 or > 8,000): aufnahme + wiedergabe 5,266, Sonic Groove 7,194, Radiant 10,418, Avant! 10,401, BITE 12,686, Other People 14,982, Northern Electronics 17,322, Ostgut Ton 100k.
No match 10, inactive 10, private 4, no posts 2.

Result: +3 likeable accounts. The SI score 4-5 list is nearly used up; more like targets need new SI contacts.
