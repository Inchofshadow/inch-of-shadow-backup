# Gate round 2: the Release Manager work of 11-08 to 11-13 that no second model had read (2026-11-15, Fable, on Amir's "Yes, gate round 2")

Opus and its side chats built all of it. Read: the source diffs of the keep migration and Export, the any-release change, the ratio graph module, the date tags and the render size option. Measured on the running app: contrast on 16 pages, sideways overflow at 375 px on 15 pages, old ticket ids on the tickets pages. Suite: 1,500 passed.

## Verdicts

| Work | Verdict |
|---|---|
| Keep numbers + Export + picks page (⚙️ System 97, 423bbac) | approve, 1 should-fix |
| Layout for any release (⚙️ System 92, 1ca390f) | approve |
| Finish stages (⚙️ System 93, 1c0fcf2, e40b42d) | approve, read lightly (page script; proof below) |
| Moonrise palette (⚙️ System 101, f0ec978) | approve with 3 small fixes; one claim overstated |
| First RM check: 6 fixes + option C (⚙️ System 89, 90) | approve, 1 small fix |
| Ratio graphs (⚙️ System 98) | approve |
| Sidebar button (99), phone fit (100) | approve |
| Date tags (⚙️ System 103, 95fcc63) | approve, 1 small fix |
| Render size option (⚙️ System 96, 792e92f) | approve |

## What I proved myself
- **Half the Night's keeps, repeated by me, not taken from the Layout chat:** 50 keeps before and 50 now, same order, every field identical, ids 1 to 50 in list order, no field added. The six other playground data files are byte-identical to the 11-10 backup. All 156 snapshot pictures from before the migration are still on disk with the same content.
- **Paths:** the base picture of a release must sit inside `artwork/` and exist; the Export saves under a time stamp and never overwrites; the cover resizer is started with a fixed argument list on a file checked to be inside `artwork/`.
- **Ratio graphs match the data:** SoundCloud 502 / 419 = 1.198 and Instagram 997 / 1,046 = 0.953 on the newest snapshot (11-14), the same numbers the page shows. Targets are written values with their source; a missing one shows "not set".
- **Contrast, measured on 16 pages at 1,440 px** (Home, Stats, tickets, board, two release pages, Fonts, Effects, Archive, Review, Shoot, Words, Outreach, Video, Artwork Resizer, Imagine): about 8,300 pieces of text, 4 below the AA line.
- **Phone width:** no sideways scroll on 15 pages at 375 px, the cover Layout page included; the Menu button sits inside the screen.

## Fixes
1. **Should-fix, keeps file (System 97):** the keeps file is written in place, and an unreadable file is read as "no keeps". A crash in the middle of a write, then one Keep click, would save a file with a single keep. Write through a temp file and refuse to write when the existing file cannot be read. (The old code had the same weakness; git and the 11-10 backup hold copies.)
2. **Small, palette:** on the Artwork Resizer the line "Pick or drop a picture" has a contrast of 1.5:1 (near invisible). The "blocked" pill on the tickets pages is 4.2:1 (needs 4.5).
3. **Small, palette:** 19 pieces of text on Imagine and 1 on Fonts are under the 13 px floor.
4. **Claim to correct, palette:** "every colour now comes from the first :root block" is not exact. 174 fixed hex colours and 289 rgb() values still sit outside it in `style.css` (many are fallbacks or fixed ink on gold). The next colour job is not ":root edits only".
5. **Small, first RM check:** three old ticket ids still show on the tickets pages (M-09 twice, R-07 once). They sit inside hand-written "waits on" text in `tickets.json`, not in the page code. Reword those three lines with area labels.
6. **Small, date tags:** a waiting ticket whose date has passed shows the old date as if it were a plan ("📅 20 Sep" on 🎬 Socials 2, "📅 1 Oct" on 🎬 Socials 5). A past date should read as overdue.

## Not covered
- The cover studio pages (Layout, wall, colours) were not contrast-measured: they keep the dark ground on purpose and mix page colours with picture colours.
- 164 pieces of text on Stats sit on gradients or drawn graphics, where this measurement cannot read the background.
- The finish stages were not re-rendered by me. The Layout chat's proof (keep #50 identical with old and new code in one browser session) stands, next to my data proof above.

## For Opus (the other model reads what Fable wrote today)
- `release_manager/storage.py` backup filter (2148cbc), the backup's final secret check (331339a), the drawer's untagged chip (ca0bc79), `stats/evening_reports.py` + its LaunchAgent and the two changed task prompts (d85b528), the memory index repair.
