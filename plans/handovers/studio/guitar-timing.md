# 🎸 Studio · guitar timing follows vocal (2026-11-22)

## Set
- [A Dorian 11bpm Composotion.als](/Users/amir/Desktop/PROJECTS/A%20Dorian%20111%20Bpm%20Composion/A%20Dorian%2011bpm%20Composotion%20Project/A%20Dorian%2011bpm%20Composotion.als), saved 02:02, read 02:05 (read-only, never written)
- 111 BPM, 4/4. 1 beat = 540 ms.
- Track 7 "Mic" = `Mic 0001 [2026-11-22 005542].wav`; track 12 "Gtr/Instert" = `Gtr_Instert 0002 [2026-11-22 005546].wav`.
  Both 245.65 s, 44.1k 24-bit mono, identical warp anchors (0 s -> clip beat 2.2431). Same take.
- Track 12 = one clip 14.1.1 -> 36.1.1, unedited. Track 7 = 7 clips, same span.

## Track 7 edits vs the raw take (track 12)
| # | Vocal clip now | Take audio was at | Move |
|---|---|---|---|
| 1 | 14.1.1 - 17.4.4 | same | 0 |
| 2 | 17.4.4 - 20.3.2.50 | 18.2.2.50 - 21.1.1 | 1.625 beats earlier (take 17.4.4-18.2.2.50 cut out) |
| 3 | 20.4.1.50 - 22.2.3.50 | 21.1.1 - 22.3.3 | 0.875 beats earlier (0.75-beat gap before it) |
| 4 | 22.4.3 - 25.4.1 | 22.3.3 - 25.3.1 | 1 beat later (1.875-beat gap before it) |
| 5 | 25.4.1 - 29.1.1 | 25.3.1 - 28.4.1 | 1 beat later + warp markers at 26.1.1 and 27.2.2: about +1.2 beats at the start, about +0.93 from 27.2.2 |
| 6 | 29.1.1 - 31.2.1 | 28.4.1 - 31.1.1 | 1 beat later |
| 7 | 31.2.1 - 36.1.1 | same | 0 (take 31.1.1-31.2.1 cut out) |
No fades on any clip. Bleed: out of scope.

## Options given
- A (offered, waiting for yes): new file next to the original, track 12's one clip replaced by 7 guitar clips copying track 7's positions, offsets and warp markers exactly. Original untouched. Only Amir opening it in Live proves it.
- B manual: split track 12 at the table points, slide by the moves (1/32 grid), redo the clip-5 warp by hand.

## State
- 02:11 Amir asked me to do it in the set itself. Done: backup `A Dorian 11bpm Composotion [before gtr sync].als` (byte copy of the 02:02 save), then track 12 in the original .als rewritten to 7 guitar clips copying track 7 (positions, offsets, warp markers, fades). Nothing else changed (text splice of track 12's Events only; re-read verified).
- Not verified in Live yet: Amir must reopen the set (Live had the old version open).
- Undo: open the [before gtr sync] file.
- Script: scratchpad mirror.py (temporary).

## Ticket updates
- none
