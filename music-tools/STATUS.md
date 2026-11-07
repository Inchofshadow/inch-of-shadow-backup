# Sample Library — Final State

Updated 11 Sep 2026. Project closed by Amir on this date. Everything below is verified on disk.

---

## DONE

### Ableton racks — 41, all samples resolve, all confirmed loading in Live

Location: `~/Music/Ableton/User Library/User - Drum Racks/`
Samples stay in `~/Desktop/SAMPLES MAC/<set>/renamed/`; racks point there by relative + absolute path.
Last full check 11 Sep: 41 racks, 2,989 sample references, 0 missing, 0 pads named `Misc`.

| Set | Racks | Notes |
|---|---|---|
| Drum Machines | 26 | one per machine, max 32 pads. `Real Snares Terminator` and `Sequential Circuits Tom` renamed 11 Sep |
| Eitan Kicks | 6 | by note: E 18 · F 34 · F# 31 · G 28 · G# 22 · Other 27 |
| Splice | 9 | Bells · Foley & Lasers · Hand Perc · Impacts Booms Downlifters · Rides · Risers & Sweeps · Shakers · Tambourines · Wood & Clicks |
| CC Snares | 2 | built 22 Oct, UNTESTED until Amir loads them. 1 = 11 CC snares + 21 closest, 2 = next 32 (`drumrack/snare_pitch/cc_racks_built.csv`). Pads `<body note> <name>`, sorted low to high. Copies in `SAMPLES MAC/CC Snares/` (racks point there) + `Digitakt/CC Snares/`; undo `snare_pitch/undo_cc_racks.sh` |
| Snares by Key | 12 | built 22 Oct, UNTESTED until Amir loads them. `Snares [C]`…`[B]`, 256 snares with a clear body note (prominence >= 24 dB) out of 621 unique; leaning/no-note snares left out on purpose. Copies in `SAMPLES MAC/Snares by Key/<note>/` + `Digitakt/Snares by Key/<note>/`; list `snare_pitch/key_racks_built.csv`, undo `snare_pitch/undo_key_racks.sh` |

Pad naming: `Type [Note] NN Machine`, e.g. `Conga [C#] 02 LM1`. No bracket = no pitch found. All pads start at C1.

**Misc fix (10–11 Sep):** 112 pads across 21 machine racks were named `Misc NN` because the tool did not know names like
`CLHAT1`, `Snaredrum-01`, `UNIVOXsd`, `cabasa`. Every one was traced to its original pack file by waveform (match ≥ 0.9999),
renamed to its real instrument, and the racks rewritten. Map: `SAMPLES MAC/Drum Machine Tune/MISC_SOURCES.csv`.
7 Splice files with pack-prefix names fixed the same way (`Ride Bell`, `Ride 21/22`, `Bell [C#] 07`, `Shaker 16`).
Only unknown left: `Perc 03 RolandR8` (original name `v`, short tonal 1.4 kHz hit).

### Ableton User Library root
`User - Drum Racks`, `User - MIX` (4 mastering chains), then `DRUM -` x6, `FX -` x3, `GTR -` x1, `MAX -` x5.
Dash prefix = Amir's, no dash = Ableton's. Full rename list is in the 11 Sep session record.

### Digitakt set — ready, NOT yet transferred

`~/Desktop/SAMPLES MAC/Digitakt/` — **810 samples, 157 MB**, all mono / 48 kHz / 16-bit, durations match originals.
Bells 16 · Crash 21 · FX 75 · Hand Perc 20 · Rides 20 · Shakers 16 · Tambourines 17 · Wood & Clicks 18 · Vocals 95 ·
Kicks Eitan 160 (folders E/F/F#/G/G#/Other) · Machines 183 (Claps 8 · Cymbals 17 · HiHats 18 · Kicks 23 · OpenHats 7 · Percs 59 · Snares 30 · Toms 21) ·
Witch House 168 (Cymbals · HiHats · Kicks · Kicks Picked · OpenHats · Percs · Snares).
11 Sep: 22 wrong names fixed ("Rim" inside Grimes/Crimewave), Misc folder dissolved into type folders, 9 duplicates moved
to `SAMPLES MAC/_removed from Digitakt 2026-09-11` (Amir to trash). 5 wide-stereo tambourines converted from the stronger
channel instead of a downmix (a plain downmix lost 4–5.5 dB). Vocal loops kept whole; Amir slices on the MPC.

### Serum presets (state 2026-10-20)

Serum 2 reads `/Library/Audio/Presets/Xfer Records/Serum 2 Presets/` (prefs file). Serum 1 reads `.../Serum Presets/`.
Amir still uses both. Serum 2 shows Serum 1's tree a second time as `S1 Presets`.
- **Serum 1 `User/`** holds every `.fxp` preset in 14 theme/pack folders (Track Remakes 47 · Witch House 60 · Hip-Hop & Trap 36 ·
  Crystal Castles 25 · NODE Dark Crystal 72 · Chiptune 11 · Real Instruments 10 · Cyberpunk 9 · Angel Core 8 · Ambient 6 ·
  Film & TV 5 · Presetshare 5 · EBM 4 · Rock 3). Files named vibe-first: `LD Carti - Long Time.fxp`. Serum 1 lists by filename.
- **Serum 2 `User/`** holds the Serum-2-only packs (Tonepusher 850 · Gesaffelstones 50 · Kraftones 50 · 2Hollis 47 · AoKor 36)
  plus 17 `.serumpreset` that load on 2.0.16. The 229 `.fxp` that were in both trees were removed from the Serum 2 side
  (Trash `Serum 2 doubled fxp 2026-10-20`, PUT_BACK.sh inside) so each preset is listed once.
- **207 `.serumpreset` saved with Serum 2.0.17–2.1.5** (incl. all 82 NODE v2.0) do not open on 2.0.16. Parked in
  `SAMPLES MAC/_Serum 2 presets waiting for update (need 2.1.5)/` with `PUT_BACK.sh`. Update Serum 2, run it, Rescan.
- Plan + naming rule: `SERUM_PLAN.md`. Scripts, name map, backups, undo scripts: `drumrack/serum_sort/`.
- **Incident 10-20:** rewriting the data block inside `.fxp` files (to change the name Serum shows) crashed Serum 1 in Live.
  All 298 restored byte-for-byte. Rule: never modify an `.fxp` chunk; rename the FILE instead (Serum 1 shows filenames).
  `.serumpreset` header-text renames (17 files) are in place, unverified by a load.
- Open: tags/author/description for the older packs (needs the one-tag test in Serum 2 to see where tags are stored);
  the parked 207 after the update.

### Library cleaned

| Pack | Before | After |
|---|---|---|
| Cluster New Wave | 2.1 GB | 61 MB |
| Witch House Samples | 1.0 GB | 484 MB, sorted by type |
| Industrial EBM | 810 MB | 610 MB |
| Trigger 2 library | 3.7 GB | 2.8 GB |
| Snaers pack | 3.3 GB | deleted (0 project references) |
| .asd cache | 4,158 | 0 (Live regenerates them when it browses a folder) |

SAMPLES MAC sample library ≈ 7 GB (was 14 GB). Every delete was checked against all project files first.

### Tool — `drumrack/drumrack_tool_v2.py`

Type detection fixed 11 Sep (see `drumrack/CHANGELOG.md`): real words beat pack-prefix codes, leftmost word wins,
11 new percussion types. Proven by `drumrack/tests/test_detect_type.py` (53 real names, 0 wrong) and a regression over
805 renamed files on disk (0 mismatches). Misc-tracing scripts live in `drumrack/misc_fix/`.

---

## OPEN — on request only

1. **Witch House racks** — agreed plan: 3 drum racks (Kick & Snare 32 · Hats & Cymbals 30 · Percs & FX 32) + 57 melodic
   samples as Simpler instruments with root notes. Vocals stay as loops. Not started.
2. **Transfer the Digitakt folder** (Amir), then trash `_removed from Digitakt 2026-09-11`.
3. **Rescan presets in Serum 2** (Amir) so AoKor Hyperpop, AoKor Witchouse and NODE Dark Crystal appear.
4. 23 drum machines never racked · kick-by-note rack across machines · MPC Live 2 `.xpm` programs (planning stalled at
   "too many programs") · Elektron Sound Pack (`.afsnd`/`.arsnd`, never opened).

## RULES IN FORCE

- Originals are never renamed or moved without Amir's word for that specific action. The tool copies.
- Max 32 pads per rack. One-shots only in racks.
- Pitch marker `[C#]` in brackets, real sharp sign, no octave; only at 80%+ confidence. Type first, machine last.
- "Valid XML" is not verification. A rack is verified when Amir loads it and the pads play. Live shows 16 pads per page.
- Every delete is verified against all projects, counted in songs not files, before it happens.
