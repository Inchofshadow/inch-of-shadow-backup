# Handover — Drum Sample Library & Drum Rack Tool

**Owner:** Amir · **Date:** 1 Sep 2026 · **Built with:** Claude Fable 5.1
**Status:** Tool built, tested, verified. Not yet run on the real library.

---

## 1. Goal

Organize a large collection of drum-machine one-shot samples so they can be:
1. Auditioned and cherry-picked (not every sample is wanted).
2. Renamed on a consistent scheme.
3. Loaded into **Ableton Live** as Drum Racks.
4. Loaded into an **Elektron Digitakt**.

Hard constraint: **existing Ableton projects must not break.** Samples currently in use must never be renamed or moved.

---

## 2. Key findings on drum-machine pitch

- Only **analog** machines have a real "designed" kick pitch:
  - TR-808 kick ≈ 50 Hz real (spec 56 Hz) → ~G (Ableton labels this G0; scientific G1)
  - TR-909 kick ≈ 47 Hz settled → ~F#
- Everything **sample-based** (RX5, RX11, RX-21, RY-30, DMX, LinnDrum, Linn 9000, Alesis HR-16/SR-16, Kawai R-50e/R-100, Akai XR-10, TR-707, etc.) has **no spec pitch** — the pitch is whatever the recording is. Must be measured per sample.
- **Snares are atonal** (noise-based). No clean note. Only the 808 snare has a usable tonal component.
- Boss DR-55 is analog (real fundamental, no published spec). SH-101 is a synth, not a drum machine.

---

## 3. What was built

### `drumrack_tool.py` (single self-contained Python script)

Two-step workflow:

**Step 1 — `scan`**
```
python drumrack_tool.py scan "/path/to/SAMPLES MAC"
```
- Each sub-folder = one machine.
- Analyzes every sample: type (kick/snare/hat…), length, and **settled pitch** for tonal hits.
- Writes one **audition web page per machine** → `_DrumRackTool/audition/<Machine>.html`.
  - Audio is embedded in the page (plays offline, no path issues).
  - Play button + keep-checkbox per sample. Helpers: Keep all / Drop all / Only kicks / Invert.
  - "⬇ Download picks" saves `<Machine>.picks.json` to Downloads.
- Nothing is copied or renamed in this step.

**Step 2 — `build`**
```
python drumrack_tool.py build "/path/to/SAMPLES MAC"
python drumrack_tool.py build "/path/to/SAMPLES MAC" --convert
```
- Reads `*.picks.json` (from Downloads and `_DrumRackTool/picks/`).
- Builds **only the kept samples**:
  ```
  _DrumRackTool/
    renamed/<Machine>/    clean-named copies  (e.g. TR808_BD_G0_01.wav)
    digitakt/<Machine>/   48 kHz / 16-bit / mono   (only with --convert)
    racks/<Machine>.adg   Ableton Drum Rack, drag into Live
    build_report.csv
  ```
- Each `.adg` pad points at its renamed file by absolute path → opens in Live with no relinking.
- Pads fill from C1 upward, kicks first.

Use `--flat` on either command to point at a single machine folder directly.

### Naming scheme (decided)
`MACHINE_TYPE_PITCH_NN.wav` — machine-first, e.g. `TR808_BD_G0_02.wav`
- Type codes: BD SD RS CP CH OH RD CR CY LT MT HT TM CB CL CG BG SH TB MA PC FX
- Pitch tag only on tonal hits (kicks, toms, cowbells). Snares/hats get none.
- Octave labels default to **Ableton convention** (C3 = 60), matching Live's display. `--octave scientific` switches to tuner-style labels (same pitch, +1 octave number).

### Safety model (critical)
- **Default = copy.** Originals are never renamed or moved. Existing projects keep working.
- **`--in-place` renames originals. DO NOT USE** on samples any project depends on.
- To retire originals later: open each project → **File → Collect All and Save** first.

### Build flags
| flag | effect |
|---|---|
| `--all` | build everything, ignore picks |
| `--convert` | add Digitakt 48k/16-bit mono copies |
| `--name-order type` | `BD_TR808_01` instead of machine-first |
| `--no-pitch-tag` | omit note from filenames |
| `--map-start C1` | first pad note |
| `--octave ableton\|scientific` | note label convention |
| `--in-place` | destructive rename — avoid |

---

## 4. Verification done

Tested on synthetic samples with known pitches:
- Pitch detection: 50.0→50.1 Hz, 41.2→41.3 Hz, 61.7→61.8 Hz (within a few cents).
- Curation: picked 1 of 3 → rack contained exactly 1 pad, nothing else.
- Generated `.adg` parsed as valid Live 12.3 XML, correct notes/paths/durations.
- Digitakt output confirmed 48000 Hz / PCM_16 / 1 ch.
- Originals confirmed untouched after every run.
- Re-verified from the delivered file on 1 Sep 2026.

---

## 5. Amir's environment

- **Mac mini**, user `amir`. Ableton Live **12.3**.
- Raw sample library: `~/Desktop/SAMPLES MAC/` (e.g. `Tape Drum Machines Vol.2/Samples/RX-5/`).
- Ableton User Library: `~/Music/Ableton/User Library/`
  - Root is cluttered with ~20 loose `.adg` / `.vstpreset` / `.amxd` files.
  - Existing drum racks: `Roland Rx5.adg`, `YAMAHA RX11.adg`, `Alessis H16.adg`, `Drum Rack.adg`, `Crash Rack.adg`, `Kick Witch House DRUM RACK.adg`, `SNR Witch House DRUM RACK.adg`.
  - `Samples/` = 1.9 GB: `Imported/` 1.0 G, `Recorded/` 818 M, `Splice/` 112 M, `Processed/` 19 M. 225 files. **Projects reference this — do not move/rename.**
- Machines in collection: Yamaha RX-21/RX11/RX5/RX7/RY-30, Akai XR-10, Alesis SR-16/HR-16A/HR-16B, Boss DR-55, Kawai R-50e/R-100, Linn 9000, LinnDrum LM-2, Oberheim DMX, Roland TR-707/CR-78, TR-808/909 samples, SH-101 SFX, plus one unidentified "KB-800".

---

## 6. Recommended next steps

1. **First run on one folder** (low risk):
   ```
   python drumrack_tool.py scan "~/Desktop/SAMPLES MAC/.../RX-5" --flat
   ```
   Open the HTML, pick a few, download, then
   ```
   python drumrack_tool.py build "~/Desktop/SAMPLES MAC/.../RX-5" --flat --convert
   ```
   Drag the `.adg` into Live and check.
2. If good, run `scan` on the whole `SAMPLES MAC` folder.
3. Move `_DrumRackTool/renamed/` and `racks/` into the Ableton User Library so they appear in Live's browser permanently.
4. Tidy the User Library root: group loose files into `Presets/Drum Racks`, `Mastering`, `Vocal`, `VST Presets`, `Max`. (`.adg` files are safe to move — they store absolute sample paths.) Delete the 0-byte `Icon?` file; check M1/Pro-G triplicates.
5. Keep `~/Desktop/SAMPLES MAC` as the raw archive; use the tool's output as the working library.

## 7. Open ideas (not built)
- Type-override dropdown on the audition page (filename-based type guessing can misfire on messy names).
- Audio-based fallback classifier.
- Hat choke groups (open/closed cut each other).
- `--tune-root` that writes a real transpose into each pad so a machine snaps to one key.
- Regenerate the `.adg` template if an older Live version won't open the racks.

## 8. Install
```
pip install numpy soundfile scipy
```
Python 3.9+. Files: `drumrack_tool.py`, `README.md`, this `HANDOVER.md`.
