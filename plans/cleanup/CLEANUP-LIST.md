# Cleanup list (dry run) - 2026-11-05

Nothing has been moved or deleted. Tick the rows you want gone; ticked rows go to the macOS Trash (not permanent), with an undo script.
Scan: whole `Inch of Shadow` folder (19 GB), exact-duplicate check by content hash on every file over 1 MB (144 groups, `dupes.json`).

## A. Safe to remove

| # | Tick | What | Size | Reason |
|---|---|---|---|---|
| A1 | [ ] | `ChatGPT/fa7142d8...0d5480c9.zip` | 985 MB | ChatGPT export zip; the unzipped folder next to it holds the same 1,438 files |
| A2 | [ ] | 89 `.DS_Store`, all `__pycache__`, `.pytest_cache` | ~1 MB | macOS/Python junk, recreated automatically |
| A3 | [ ] | `Inchofshadowcode/artwork/Farewell Single/untitled folder/` (3 copies) + `Reel Build/SKIP/duplicate_original.png` | ~25 MB | byte-identical copies of the Farewell cover and reel frames that live in `Reel Build/USE/` |
| A4 | [ ] | `Releases/Eastern Star/Music for insta/Music for Instagram videos 2/` | ~23 MB | same 5 WAVs as `Music for Instagram videos/` |

**A total: ~1.03 GB**

## B. REVIEW - duplicates that may be on purpose

| # | Tick | What | Size | Why unsure |
|---|---|---|---|---|
| B1 | [ ] | `youtube/assets/audio/` The Tour, The Deceiver, Farewell WAVs | 262 MB | identical to the masters in `Releases/`, but the YouTube tools may read them from here |
| B2 | [ ] | `Inchofshadowcode/videos/ the tour the code dj.mov` | 38 MB | same file in `Releases/The Tour/` |
| B3 | [ ] | `Inchofshadowcode/EPK/Inch Of Shadow EPK March 26 copy.pdf` | 9 MB | same as `Press & EPK/... HQ.pdf` |
| B4 | [ ] | `presetshare_report*.md/.csv` (6 files, Desktop folder root) | 1 MB | 3 report versions from 10-20, contents differ; `SERUM_PLAN.md` mentions presetshare |
| B5 | [ ] | `youtube/thumbnails/_work/chrome/` | 16 MB | throwaway Chrome profile from thumbnail rendering; may be reused by the tool |

## C. Keep (checked, not candidates)

- Old IG exports in `Inchofshadowcode/data/` (Feb/Apr/Jun/Aug): code still reads them (`extract_contacts.py`, `ig_follow_tracker.json`, tests).
- `STUDIO/photos/CHOOSEN/` and `Portraits/Chosen`: copies of photos, but they are your picks.
- Serum backups in `music-tools/drumrack/serum_sort/backups/`: the restore source after the 10-20 crash.
- Artwork copies inside `Inchofshadowcode/artwork/` and `youtube/assets/art/`: tools use these paths.
- RAW photo folders, release masters, `Personal/`.
- `A Liar New 1.8.4 ii.wav`, `Half The Night Master 2.wav`, the two signed Ambertone PDFs in the Desktop folder root: current files; tidying them into folders = a move, ask separately.
