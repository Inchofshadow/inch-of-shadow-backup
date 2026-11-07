# Type detection fix — 11 Sep 2026

Found while tracing 112 `Misc` pads and 7 wrong Splice names back to their packs by waveform
(`misc_fix/`, `Drum Machine Tune/MISC_SOURCES.csv`). Proven by `tests/test_detect_type.py`
(53 real filenames from the library) and a regression over every renamed file on disk.

## Fixed

| # | Was | Now | Example |
|---|---|---|---|
| 1 | A 2-letter pack prefix could win over the spelled-out instrument | Real words (strong) beat the abbreviation codes in `WEAK_TOKENS` (weak) | `SIG_RS_drum_ride_crash…` → Ride, not Rimshot; `FL_HT_Shaker_Closer` → Shaker, not Hi Tom |
| 2 | Rule order decided ties, so `crash_ride` and `ride_crash` could not both be right | Within a tier the **leftmost** word wins (packs name files `<pack>_<instrument>_<descriptors>`) | `TS_SD_crash_ride_smash` → Crash; `SULLIVAN_KING_ride_bell_01` → Ride |
| 3 | No rule for many percussion names, so they became `XX` (renamed to "Misc" downstream) | 11 new codes + glued forms | `CLHAT1` → CH, `Snaredrum-01` → SD, `Linn cabasa hard` → CA, `Hitimb_Oberheim_DMX` → TI |
| 4 | A machine whose name is the instrument (Sequential Circuits **Tom**) lost its type when the machine name was stripped | Retry on the raw name, real words only, so `CR-78` still can't become a crash | `Tom 02 Tom` → Tom; `CR78_01` → XX |

## Added

New codes: `CA` Cabasa, `CS` Castanet, `TI` Timbale (tonal 100–700 Hz), `AG` Agogo (tonal 300–2000 Hz),
`VS` Vibraslap, `TR` Triangle, `CM` Chime, `SP` Snap, `CU` Cuica, `WH` Whistle, `BL` Bell (tonal 200–4000 Hz).
New vocabulary: `clhat`, `ophat`, `snaredrum`, `sidestick`, `fbd/hbd/pbd`, `bong`, `block`, `stick`, `percussion`, `china`, `splash`, `claves`.

## Not fixed here

- The "Grimes → Rim" bug that hit the Digitakt copies was in the one-off Digitakt copy script, not in this tool; this tool always used `\b` word boundaries.
- A bare "stick" is filed as Perc, not Rimshot; only `sidestick` is a rimshot.

# drumrack_tool v2 — 2 Sep 2026

`drumrack_tool_v2.py`. v1 (`drumrack_tool.py`) left untouched next to it.

## Fixed

| # | Was | Now | Proven by |
|---|---|---|---|
| 1 | Picks from every `*.picks.json` were **merged**, so re-auditioning could never drop a sample | Newest file per machine wins, older ones ignored | 4 current + 1 stale pick file → 4 pads, stale one ignored |
| 2 | `_DrumRackTool` sat inside the library, so the next `scan` treated it as a machine | Output folder excluded from the walk | 2nd scan: v1 finds `MachineA` + `DrumRackTool`, v2 finds only `MachineA` |
| 3 | Paths written into the rack unescaped | `&`, `<`, `>`, `"` escaped | `&` in path: v1 rack is **not well-formed XML**, v2 parses clean |
| 4 | Pad notes could pass MIDI 127 | Rack splits into `Machine_2.adg` at the limit | guard in `process_machine` |
| 5 | `--all` still filtered by picks | Picks skipped entirely under `--all` | |
| 6 | `--tune-root` accepted but did nothing | Removed | |
| 7 | Bad `--map-start` silently fell back to C1 | Errors with a clear message; range-checked | |
| 8 | `RX-5` and `RX 5` collided, second silently won | Second becomes `RX52`, prints a warning | |
| 9 | `--flat` non-recursive while normal mode recursed | Both recurse | |
| 10 | CSVs written without an encoding | `encoding="utf-8"` (library has `✧` names) | |
| 11 | Unreadable files vanished silently | Counted, listed in `skipped.txt` | |

## Added

- **Confidence score (0–100) on every detected note.** Combines periodicity (does the wave repeat), stability (do slices of the tail agree, in cents) and tonality (spectral flatness). Below `--min-confidence` (default 80) **no note is written**. Score is always kept in the CSV, so a blank can be investigated.
- **`BS` bass type**, tonal, band 28–400 Hz. `bass drum` still resolves to `BD`, not `BS`.
- **`--peak-db`** normalises copies so peaks sit at a set dBFS (`-6` recommended). Digitakt copies default to −6 dBFS.
- **No octave in filenames.** `RX5_BD_G_01.wav`, not `G0`. Full note + cents still in the report.
- **Type override dropdown** on the audition page; the chosen type is saved into the picks file and used at build.
- Machine name stripped before type detection, so a folder called `CR-78` cannot make everything a Crash.

## Verified on synthetic fixtures

```
Kick   50.0 Hz → G0  98.4%  tagged
Tom   110.0 Hz → A1  99.7%  tagged
Bass   41.2 Hz → E0  99.6%  tagged
Snare  noise   → no note
Hat    noise   → no note
```
Peak normalisation measured at −6.00 dBFS. Digitakt output 48000 Hz / PCM_16 / 1 ch. Originals unchanged after every run.

## Not done yet

- MPC Live 2 `.xpm` export
- Key detection for loops and phrases
- Chord naming for pads
