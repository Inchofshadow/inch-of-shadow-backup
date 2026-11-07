# drumrack_tool

Audition → cherry-pick → rename → rack. Turn folders of drum-machine one-shots
into clean Ableton Drum Racks, keeping only the samples you actually like.
Same renamed files drop straight into Digitakt.

## Your existing projects are safe
By default the tool **never renames or moves your originals** — it makes renamed
*copies* in a separate `_DrumRackTool/` folder and leaves every original exactly
where it is. So any Ableton project pointing at those originals keeps working.
The only flag that touches originals is `--in-place`; just don't use it and you're
fully protected. (If you ever want to retire the originals, open each project and
do **File → Collect All and Save** first, then you can delete them safely.)

## Install
```
pip install numpy soundfile scipy
```

## Step 1 — SCAN (audition & pick)
```
python drumrack_tool.py scan "/path/to/SAMPLES MAC"
```
For one machine folder directly, add `--flat`.

This analyzes everything and writes one **audition web page per machine** to
`_DrumRackTool/audition/<Machine>.html`. Nothing is copied or renamed yet.

Open a page in any browser. For each sample you get a **play button** (audio is
embedded, so it works offline) and a **keep checkbox**, plus its detected type,
note and length. Untick what you don't want — e.g. keep 3 of 10 kicks — then click
**⬇ Download picks**. That saves `<Machine>.picks.json` (goes to your Downloads).
Helpers: Keep all / Drop all / Only kicks / Invert.

## Step 2 — BUILD (from your picks)
```
python drumrack_tool.py build "/path/to/SAMPLES MAC"
python drumrack_tool.py build "/path/to/SAMPLES MAC" --convert
```
It finds your `*.picks.json` files (looks in Downloads and `_DrumRackTool/picks/`),
and for each machine builds **only the samples you kept**:
```
_DrumRackTool/
  renamed/<Machine>/    clean-named copies   (e.g. TR808_BD_G0_02.wav)
  digitakt/<Machine>/   48k/16-bit mono      (only with --convert)
  racks/<Machine>.adg   drag into Live (pads from C1 up, kicks first)
  build_report.csv
```
Each .adg pad points straight at its renamed file, so it opens in Live with no
relinking.

If you'd rather just build everything without auditioning, pass `--all`.

## Build options
| flag | what it does |
|---|---|
| `--all` | build every sample, ignore picks |
| `--convert` | also write Digitakt 48 kHz / 16-bit mono copies |
| `--name-order {machine,type}` | `TR808_BD_01` (default) vs `BD_TR808_01` |
| `--in-place` | rename the originals instead of copying (destructive — avoid) |
| `--no-pitch-tag` | leave detected notes out of filenames |
| `--map-start C1` | MIDI note of the first pad (default C1 = 36) |
| `--octave {ableton,scientific}` | note labels. **ableton** (default) matches Live's display (C3 = 60), so 50 Hz reads `G0`. **scientific** reads it as `G1` (matches most tuners). |

## Honest notes
- **Pitch is only tagged for tonal hits** (kicks, toms, cowbells…). Snares, hats,
  claps, cymbals are noise-based and get no note — by design.
- **Kicks are read at the settled tail**, not the attack. Tested accurate to a few
  cents on clean tones; treat it as a strong reference, trust your ears for the
  final call.
- **Type detection reads the filename first.** Spelled-out words beat 2-letter codes,
  and the leftmost word wins, so `TS_SD_crash_ride_smash` is a crash. Anything still
  unrecognised gets `XX`; check it on the audition page (it shows each detected type).
  Real cases live in `tests/test_detect_type.py` — add a line there when a name goes wrong.
- The `.adg` template came from a real Live 12.3 rack. On an older Live, if a rack
  won't open, tell me your version and I'll regenerate it.

## Suggested first run
```
python drumrack_tool.py scan "/path/to/one machine folder" --flat
```
Open the HTML, pick a few, download, then:
```
python drumrack_tool.py build "/path/to/one machine folder" --flat --convert
```
Open the .adg in Live. Happy? Run it on the whole library.
