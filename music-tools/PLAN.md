# Sample Library Plan — Inch of Shadow

**Owner:** Amir · **Started:** 2 Sep 2026
**Scope:** `~/Desktop/SAMPLES MAC` (14 GB, ~15,000 audio files)
**Targets:** Ableton Live 12.3 · Elektron Digitakt (mk1) · Akai MPC Live 2

---

## 1. Goal

Turn a 14 GB pile of samples into a library that is:
1. Sorted by source and by sound type
2. Pitch-labelled where pitch actually exists
3. Loadable as Ableton Drum Racks
4. Loadable on Digitakt and MPC Live 2

**Hard rule: existing Ableton projects must never break.** See §5.

---

## 2. What is actually in the library (scanned 2 Sep 2026)

| Folder | Audio files | Size | Single source? |
|---|---|---|---|
| Snaers pack | 6,336 | 5.4 G | No — construction kits |
| Cluster New Wave | 1,760 | 2.1 G | No — 163 subfolders |
| Tape Drum Machines Vol.2 | 1,837 | 124 M | **Yes — 10 machines** |
| Tape Drum Machines Vol.1 | 1,209 | 97 M | **Yes — 11 machines** |
| Eitan Rieter | 1,070 | 4.7 G | No |
| Studio Real Drum Machines | 863 | 67 M | **Yes — 28 machines** |
| Industrial Strength Dark EBM | 365 | 815 M | No |
| Witch House Samples | 281 | 478 M | No (cleaned 1 Sep) |
| TRNSNT2 Primal Kicks | 160 | 21 M | Partly |
| Travis Scott MIDI Kit | 88 | 111 M | No |

### The 49 single-source machines — start here
- **Studio Real Drum Machines (28):** Linn 9000, LinnDrum LM2, Oberheim DMX, Alesis SR-16, Roland R8 / TR-606 / TR-727 / CR-8000, Yamaha RX11 / RX-21 / RY-30 / MR10, Kawai R-50e + R-100, Akai XR-10, Sequential Drumtraks / Tom / Studio 440, Simmons SDS-5, Boss DR-55, Pearl Syncussion SY1, Univox Micro-Rhythmer, Visco SpaceDrum, Sakata DPM-48, SoundMaster SR-88, S900 kits, Acoustic Drums 80s
- **Tape Vol.1 (11):** LM-1, DR-110, MR-10, TR-505, Drumulator, Rom808, MPC-TheKit, MRX-185, Tom, 4InTheFloor
- **Tape Vol.2 (10):** LinnDrum, CR-78, DDR-30, RX-5, DR-55, SynsonicsPro, RPM-40, KPR-77, TR-626, Bohm

### Notes from the scan
- `Studio Real Drum Machines/Ableton Drum Racks/` already holds a Live Pack (`.alp`) of racks. **Open it before rebuilding those 28.**
- Filenames carry **no note information** anywhere. All pitch must be measured.
- `CR78_BD_C2A_R1.wav` style names are already clean. The `C2A` / `T1A` suffixes are **tape-deck variants, not notes.**
- ~~4,158 `.asd` files (70 MB)~~ **deleted 2 Sep** (§6). Ableton rebuilds them on demand.
- `SAMPLES MAC/files/` and `SAMPLES MAC/files 2/` are **identical duplicates** of the tool docs.

---

## 3. What can be pitch-detected — honest tiers

| Tier | Sounds | What we get |
|---|---|---|
| **Reliable note** | Kicks, toms, bass one-shots, cowbell, clave, conga, bongo, single sustained vox or synth stabs | A real note + cents (e.g. `G0 +4c`) |
| **Root guess only** | Pads, chords, anything playing more than one note | The lowest/strongest note. Often the chord root, sometimes wrong. Label as *root*, never as *the* note. |
| **Key, not note** | Melodic loops, vocal phrases, basslines that move | Needs *key detection* — a different algorithm from what the tool does today |
| **No pitch, by physics** | Snares, claps, hats, cymbals, most FX, risers, impacts, noise | Nothing. Not a limitation, these have no fundamental. |

### 3.1 Confidence gate (decided 2 Sep)
Every detected note carries a confidence score. **Below the threshold the tool prints no note at all** instead of guessing. A blank is honest; a wrong note is worse than none. Threshold starts at 80% and is tunable with `--min-confidence`. Applies to every tier, not just vocals.

### Answers to specific questions
- **Vocals** — a held single note detects fine. A sung *phrase* moves in pitch, so it needs key detection, not note detection. **Decision (Amir, 2 Sep): only show a vocal note when confidence is high (~80%+); otherwise show nothing rather than a wrong note.** See §3.1.
- **Pads** — usually chords. Expect a root guess, not a chord name. Proper chord naming is a separate feature.
- **FX** — no. Risers, sweeps, impacts and noise have no stable fundamental. Tonal drones are the exception.
- **Snares** — no, and this is permanent. Only the 808 snare has a usable tonal component.
- **Bass** — the *best* case for detection, but the tool currently has **no bass rule at all**. Must be added.

---

## 4. Naming scheme

```
MACHINE_TYPE_PITCH_NN.wav
```
Examples: `RX5_BD_G0_01.wav` · `SR16_SD_03.wav` · `DMX_TOM_C1_02.wav`

- **Type codes:** BD SD RS CP CH OH RD CR CY LT MT HT TM CB CL CG BG SH TB MA PC FX (+ **BS** for bass, to be added)
- **Pitch tag only on tonal hits.** Snares and hats get no note — that is correct, not missing data.
- **Octave labels follow Ableton** (C3 = 60), matching Live's display. 50 Hz reads `G0`. Tuner convention (`G1`) available via a flag.

---

## 5. Why existing projects cannot break

**The tool copies. It never renames or moves an original.** Your projects point at the old files, which stay exactly where they are under their old names. There is nothing to relink.

Rules:
1. **Never use `--in-place`.** It is the only flag that touches originals.
2. Ableton locates missing samples **by filename**. Rename an original and Live's auto-search fails, leaving you to locate every sample by hand.
3. **Before any bulk work: File → Collect All and Save** on active projects. That copies samples into each project folder and makes those projects immune to anything done afterwards.
4. Originals in `SAMPLES MAC` stay as the raw archive. The renamed copies become the working library.

---

## 6. The .asd question

`.asd` files are Ableton's analysis cache — waveform drawing, and warp markers if any were set.

- **Ableton recreates them automatically** the next time it touches the sample.
- For **unwarped one-shots** (all of these) they hold nothing of value.
- The only real loss would be **manually set warp markers or warp mode** on a specific file. Drum one-shots are not warped.

**Verdict: safe to delete.** 4,158 files, 70 MB, and they slow down every scan.

---

## 7. Hardware targets

### Digitakt mk1
- **Required format: 48 kHz, 16-bit, MONO WAV.** The tool's `--convert` already does exactly this.
- Storage is small. This is a **curated subset**, not a library dump — pick the best handful per machine.
- Transfer with the Elektron Transfer app over USB.
- Keep filenames short.

### MPC Live 2 — what to choose
- **Takes your WAVs as they are.** Stereo fine, 44.1 or 48 kHz fine, 16 or 24-bit fine. **No conversion needed.**
- So: same renamed files as Ableton, copied to the internal SSD or an SD card.
- **It cannot read `.adg`.** To get pads pre-mapped you need an **`.xpm` drum program**, which the tool does not build yet. Same technique as the `.adg` builder — a feature to add.
- Without `.xpm` you load samples onto pads by hand.

**Summary:** MPC gets the full-quality renamed copies. Digitakt gets a small mono 48k/16-bit subset.

---

## 8. Tool bugs to fix before the first real run

Reviewed 2 Sep 2026. Nothing has been run on the real library yet.

**Blocking**
1. **Picks only ever grow.** `load_picks` unions every `*.picks.json` it finds. Re-audition and keep fewer, the dropped samples come back. Must take the newest file per machine.
2. **Output folder gets re-scanned.** `_DrumRackTool` lives inside the library, so the next `scan` treats it as a machine and reprocesses the renamed copies. Must exclude the out dir.

**Important**
3. **No XML escaping on paths.** An `&` in any folder name produces a broken `.adg` Live will not open.
4. **Pad notes can pass MIDI 127.** More than 92 kept samples in one machine writes invalid notes. Needs a guard + split.
5. **`--all` does not ignore picks** when picks exist, contradicting both READMEs.
6. **`--tune-root` is a no-op** — accepted by the CLI, never used.
7. **Add a `BS` bass type**, tonal, so bass one-shots get notes.
8. **Add a confidence score + `--min-confidence` gate** (default 80%). No note shown below threshold.

**Minor**
9. `--map-start` typo silently falls back to C1 instead of erroring.
10. `sanitize()` collisions silently overwrite (`RX-5` and `RX 5` both become `RX5`).
11. `--flat` is not recursive while normal mode is.
12. CSVs written without `encoding="utf-8"`; the library contains `✧` filenames.
13. Unreadable files are silently dropped with no count.

**Not a bug after all:** the predicted CR-78 → "Crash" misclassification does **not** fire. Files are named `CR78_BD_…` with no hyphen, so the kick rule catches them correctly.

---

## 9. Work order

| # | Step | Risk |
|---|---|---|
| 1 | Fix blocking + important bugs, add bass type | none — copy of the script |
| 2 | ~~Delete 4,158 `.asd` files~~ **DONE 2 Sep — 4,158 removed, 70 MB, 13,969 audio files intact** | none |
| 3 | Open the existing `.alp` and see which of the 28 machines already have racks | none |
| 4 | Test run on **one** machine, drag rack into Live, confirm | none |
| 5 | Run the 49 single-source machines | none — copies only |
| 6 | Curate + convert the Digitakt subset | none |
| 7 | Build `.xpm` export for MPC Live 2 | new feature |
| 8 | Tackle the multi-source packs (Snaers, Cluster, Eitan) — needs a different approach | later |

---

## 9.1 Where the library lives (decided 2 Sep)

Everything stays on the Desktop. Nothing moves into the Ableton User Library.

```
~/Desktop/SAMPLES MAC/
  Drum Machine Tune/          <- clean renamed copies, one folder per machine
    CR-78/  LinnDrum/  RX11/ ...
  <original packs>        <- untouched raw archive
```

**One thing to watch:** `SAMPLES MAC` is already in Ableton's Places. Once the renamed copies live inside it, every sample appears **twice** in browser search, once raw and once renamed. Fix by pointing Places at `SAMPLES MAC/Drum Machine Tune` instead of the whole folder, so the browser shows only the clean library while the raw archive stays on disk.

## 10. Open decisions

- Which machines matter most? 49 is a lot; pick the 8–10 you actually use.
- Where should the finished library live — inside the Ableton User Library, or stay on the Desktop and be added to Places?
- Digitakt: how many samples per machine, and which machines?
- Do the multi-source packs get key detection, or are they left alone?

---

## 11. Stale info in HANDOVER.md

`HANDOVER.md` §5 and §6 describe the Ableton User Library **before** the 1–2 Sep cleanup:
- Racks are now named `DRUM - Alesis HR16`, `DRUM - Yamaha RX11`, `DRUM - Roland RX5`, `DRUM - Crash`, `DRUM - Kick Witch House`, `DRUM - Snare Witch House`, plus four `FX - ` racks.
- `Drum Rack.adg` no longer exists — it was a byte-identical duplicate of `Crash Rack.adg` and was removed.
- §6 step 4 recommends foldering the User Library root. **Amir decided the opposite:** everything stays at the root so it is visible in Live's browser.
- The `Icon` file is 64 KB, not 0 bytes, and is intentionally kept.
- M1 / Pro-G VST presets are confirmed exact triplicates but are **intentionally kept** — VST presets are off-limits.
