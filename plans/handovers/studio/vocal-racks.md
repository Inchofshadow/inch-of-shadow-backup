# 🎸 Studio: vocal racks handover

Chat: vocal racks (side chat started from the 🎸 Studio vocal chain research). Written 2026-11-12.
Ask: build the vocal-direction chains as Live Audio Effect Racks, built and saved by Live itself (screen control), named like his `FX - Vocal Travis.adg`.
Sources: [vocal-chain-research.md](vocal-chain-research.md), [vocal-chains.md](../../../music-tools/research/vocal-chains.md), picker page source `music-tools/research/vocal-style-picker.html` (direction 5).

## Where it stands

- ✅ Built in Live 12.3 and saved by Live: `~/Music/Ableton/User Library/FX - Vocal Tuned New Wave.adg` (23.6 KB, 23:27).
- 11-12 later: all 4 renamed after singers on Amir's "y" (done in the research chat; checked on disk, sizes unchanged): Tuned New Wave → `FX - Vocal Crystal Castles.adg`, Close and Dark → `FX - Vocal Lana Del Rey.adg`, Far and Haunted → `FX - Vocal Robert Smith.adg`, Modern and Treated → `FX - Vocal The Weeknd.adg`. The old names below are the build names.
  - Saved by dragging the rack onto User Library (Live wrote `Audio Effect Rack.adg`), then renamed in Live's browser (Cmd+R). Nothing else in the User Library was touched.
  - File check (read-only): same format as `FX - Vocal Travis Autotune.adg` (Creator "Ableton Live 12.3", `Vst3Preset` entries), 6 plug-in states stored, Chorus-Ensemble (`Chorus2`), 2 racks.
- ❓ Unproven: only Amir loading it on a fresh track proves the plug-ins come up with their settings.
- Built on a new audio track "38 Audio" in his open Untitled set (his template). The set was not saved by me; the track can be deleted or kept.
- ⏸ Directions 1, 2, 4 wait for his OK on this one (3 is parked).

## Rack: FX - Vocal Crystal Castles (built as Tuned New Wave, direction 5)

Chain (one chain in the outer rack):
1. Auto-Tune Artist (VST3): **Key A, Scale Minor** (Amir's pick), **Retune Speed 0** (Amir's pick; source: billyxo Crystal Castles tutorial). Rest default: Input Type Soprano, Humanize 0, Flex-Tune 0, Natural Vibrato 0, Classic off, Transpose 0, Detune 440, Tracking 50.
2. Waves DeEsser Stereo: default. Frequency default is 5506 Hz, which matches Seth Firkins' 5.5 kHz (SOS 2017). Threshold 0 = no de-essing until set by ear ("hitting about once every 10 words").
3. FabFilter Pro-Q 3: flat default. The research says "dynamic cut where your voice gets hard": set by ear on his voice.
4. Softube Tube-Tech CL 1B (native, not UAD-2): attack/release select = **Fix** (verified in the plug-in's readout). Threshold, ratio, gain at default; the research's 3-5 dB gain reduction needs his signal.
5. Inner rack "Parallel Grit", two chains:
   - Dry: empty, 0 dB.
   - Parallel Grit: Soundtoys Little Radiator > UADx 1176LN Rev E (native UADx, no Apollo needed), both default; chain volume **-12 dB** (Claude's number for "blended low", not from a source). Illangelo "slammed" the 1176: input/ratio by ear.
6. Live Chorus-Ensemble: default (Classic, Rate 0.90 Hz, Amount 50%, Dry/Wet 50%).

Not in the rack (by design): delays and reverbs go on Returns.

Noted: Live showed 7824 samples (177 ms) latency for the track with the rack while I worked; heavy for tracking. Likely from one plug-in's lookahead/linear mode (unchecked which).

## Racks 1, 2, 4 (built 11-12 at 23:43-23:47, on Amir's "contniue do all 4" relayed from the research chat, without waiting for the load test)

Same method: new audio tracks 39, 40, 41 in the same Untitled set, saved by dragging the rack onto User Library, then renamed in Live's browser. Delays, reverbs and "on a Return" steps are left out of every rack. File check: all Live 12.3, one plug-in state per plug-in, -12 dB parallel chain where there is one.

**FX - Vocal Lana Del Rey.adg** (built as Close and Dark, direction 1, 7.2 KB)
1. UADx Neve 1073 Preamp and EQ: default.
2. Softube Tube-Tech CL 1B: attack/release select **Fix** (its default was Man; verified in the readout). Rest default ("3-5 dB" needs his signal).
3. Waves DeEsser Stereo: default (5506 Hz, threshold 0).
4. Pro-Q 3: flat ("cut only", by ear).
5. Parallel Grit: Dry 0 dB | UADx 1176 Rev A at **-12 dB** (Claude's number for "blended low"). "Pushed hard" = input by ear.
- Left out: Magma Springs (a Return, low).

**FX - Vocal Robert Smith.adg** (built as Far and Haunted, direction 2, 3.3 KB)
1. Pro-Q 3: flat. The research's dynamic notch "about 3 kHz" is Robert Smith's voice, so set it on his.
2. Softube Tube-Tech CL 1B: default ("gentle").
- Left out (Returns): Echo/EchoBoy two times, MetaFlanger or Chorus-Ensemble, ValhallaVintageVerb long with pre-delay. His set already has Returns D/E/F delays and G Chorus.

**FX - Vocal The Weeknd.adg** (built as Modern and Treated, direction 4, 26.2 KB)
1. Auto-Tune Artist: default ("subtle": Retune 20, Key C, Chromatic, Soprano). No key was asked for this one.
2. Waves DeEsser Stereo: default.
3. Pro-Q 3: flat (low and top roll-off for verses, by ear).
4. Waves API-560 Stereo: default.
5. FabFilter Pro-MB: default.
6. Parallel Grit: Dry 0 dB | Little Radiator > UADx 1176LN Rev E at **-12 dB** ("slammed" = input by ear).
7. Waves Doubler2 Stereo: default.
8. Soundtoys MicroShift: default.
- Left out: Reel ADT (choruses only), Timeless 3 delays, ducked reverb (Returns).
- During the build, a mis-click briefly grouped Auto-Tune alone; ungrouped (Cmd+Shift+G) and regrouped. A click also moved MicroShift's unmapped XY dot in Live's device panel; moved back, no parameter is mapped to it.

## Next

- Amir loads each of the 4 racks on a fresh audio track and checks the plug-ins open with the settings above. All 4 stay unproven until then.
- Tracks 38-41 in the Untitled set are build scratch; the set was not saved.

## Ticket updates (for ⚙️ System to merge)

- 🎸 Studio 11 (new, ST- prefix; next free number per the handovers, ⚙️ confirms):
  - `bucket`: 🔥 now
  - `who`: 🙋 amir (load test), then 🎃
  - `label`: Vocals · vocal FX racks in Live (5 directions)
  - `next_step`: Amir loads the 4 FX - Vocal racks (Crystal Castles, Lana Del Rey, Robert Smith, The Weeknd) on fresh tracks and confirms the settings came up
  - `chrome`: false
  - note: all 4 racks saved by Live 2026-11-12, unproven; handover `plans/handovers/studio/vocal-racks.md`

## 11-13: send chains inside the racks (Amir: "in each rack create a send")

Layout agreed with Amir: the effect sends are extra chains inside each rack's parallel rack, next to Dry and the grit chain. Each effect is 100% wet; its chain volume = the send level (Amir picked -15 dB as the start).

- ✅ **FX - Vocal Lana Del Rey.adg** saved 02:05 from Live with Amir's own tweaks: Parallel Grit (1176 Rev A, input/output raised by him) at -20 dB | Dry 0 dB | Spring (Magma Springs Stereo, Mix 100) at -15 dB. CL 1B on fixed. DeEsser threshold still 0 (inactive). Old file moved to the Trash (Amir: "Replace (old to Trash)"). Live saved it as "-1" and it was renamed in Live's browser.
- 🔨 Built, NOT saved yet (waiting for Amir's tweaks, then save the same way):
  - **The Weeknd** (track 39): Parallel Grit -12 | Dry 0 | Delay (Timeless 3, Wet mode, Wet Level 0 dB) -15 | Verb (ValhallaRoom default, Mix 100%) -15. Ducking the reverb by the dry vocal is NOT built (no sidechain inside a rack chain).
  - **Robert Smith** (track 40): had no parallel rack, so a new inner rack "Sends" after the CL 1B: Echo (Live Echo default 1/8 dotted, Dry/Wet 100) -15 | Dry 0 | Flanger (MetaFlanger Stereo, Mix 100) -15 | Verb (ValhallaVintageVerb default: Concert Hall, 4 s, pre-delay 20 ms, Mix 100) -15. Research's "two different times" on the delay is not set (both sides 1/8 dotted).
  - **Crystal Castles** (track 41): Parallel Grit -12 | Dry 0 | Echo (Dry/Wet 100) -15 | Spring (Magma, Mix 100) -15 | Verb (ValhallaRoom, Mix 100) -15. Chorus-Ensemble stays after the parallel rack, so it also colours the sends. Reverb ducking not built.
- Slips (fixed): a Delete removed the whole Lana rack, restored with Cmd+Z; a click on a rack's save icon made Live write `Presets/Audio Effects/Audio Effect Rack/Audio Effect Rack.adg` (02:08), moved to the Trash; a click moved the CL 1B panel's unmapped XY dot, moved back.
- 11-13 later (Amir: "make it like the research"): Crystal Castles' Chorus-Ensemble moved from an insert after Parallel Grit into its own chain "Chorus" inside Parallel Grit, Dry/Wet 100%, -15 dB (research: chorus on a Return). The dry vocal and the other sends are no longer chorused. Still not saved.
- Known open: The Weeknd's Timeless 3 still passes the dry signal (Wet mode, dry level 0 dB); it needs Mix mode at 100% (Amir spotted it; left to him while he edits).

## 11-13 ~02:40: "Apply all fixes" (Amir)

Applied in Live on tracks 38-41 (racks NOT re-saved yet):
- All 4 Pro-Q 3: Linear Phase -> **Zero Latency** (Lana's change is on track 38 only; the saved Lana .adg still has Linear Phase until re-saved).
- The Weeknd: Timeless 3 -> Mix mode 100%, tempo-synced, L 1/4 note, R 151% (two times); Pro-MB: one compress band ~200-500 Hz (default threshold, set by ear), global Lookahead Off; 1176LN Input -6.1 dB / Output -14.8 dB (copied from Amir's Lana 1176); ValhallaRoom pre-delay 70 ms, decay 1.8 s, Hi Cut 6 kHz (🎃 numbers); Doubler2 > MicroShift moved into a "Width" chain in Parallel Grit, Doubler2 Direct (dry) Off, MicroShift Mix full wet, -15 dB.
- Robert Smith: VintageVerb pre-delay 80 ms (Amir's LowCut 360 Hz kept); Amir's EchoBoy Mix set fully wet (his Dual Echo 1/8 + 1/4 kept).
- Crystal Castles: Amir's 1176 left as he set it (Input -5.3, 20:1); EchoBoy (default) -> Mix fully wet, Dual Echo, Echo 2 = 1/4 note.
- Not changed: Lana DeEsser threshold (taste, needs his voice).

## 11-13 02:40-02:41: all 4 re-saved (Amir: "Save all 4")

Saved from Live (drag onto User Library -> "-1" files), the previous 4 files moved to the Trash via Finder, new files renamed to the clean names. Travis racks untouched.
- FX - Vocal Lana Del Rey.adg (8.3 KB): 6 plug-ins; chains Parallel Grit / Dry / Spring; Pro-Q 3 Zero Latency. DeEsser threshold still 0.
- FX - Vocal The Weeknd.adg (28.5 KB): 11 plug-ins; chains Parallel Grit / Dry / Delay / Verb / Width.
- FX - Vocal Robert Smith.adg (9.9 KB): 5 plug-ins; Sends rack: EchoBoy (Amir's, Dual 1/8 + 1/4, full wet) / Dry / Flanger / Verb.
- FX - Vocal Crystal Castles.adg (29.2 KB): 9 plug-ins + Chorus-Ensemble; chains Parallel Grit / Dry / EchoBoy / Spring / Verb / Chorus.
- Still unproven: only Amir loading each on a fresh track proves the plug-ins come back with these settings.
- Scratch tracks 38-41 in the Untitled set remain; the set was not saved by Claude.

## 11-13 ~03:00: two more racks (Amir: "do it")

Built on new tracks 41/42 (Untitled set), saved from Live (drag onto User Library -> "Audio Effect Rack.adg", renamed). Same layout as the others: inserts, then a "Sends" rack (Dry 0 dB + wet chains at -15 dB). All Pro-Q 3 on Zero Latency, CL 1B on Fix.

- **FX - Vocal Nick Cave.adg** (9.9 KB, 8 plug-ins). Source: Nick Launay, *Push The Sky Away*, AudioTechnology 2013 (engineer says).
  UADx Neve 1073 (default; stand-in for his Neve 1081) > CL 1B (Fix) > Waves DeEsser Stereo (default) > Pro-Q 3 (flat) > Sends: Grit (Devil-Loc, default) | Dry | Spring (Magma Springs, Mix 100) | Plate (UADx Pure Plate, Wet Solo on; stand-in for EMT plate) | Slap (UADx Galaxy Tape Echo, Wet Solo on, head 1 only, feedback 0, stand-in for RE-301).
  Devil-Loc placement (parallel) is Claude's choice; Launay doesn't say insert or parallel.
- **FX - Vocal Deftones.adg** (9.7 KB, 6 plug-ins). ⚠️ UNVERIFIED: source is only a search snippet (Terry Date, AudioTechnology, *Ohms* 2021: RAT distortion + Strymon Volante slap). Compressor, EQ and the reverb are Claude's picks.
  CL 1B (Fix) > DeEsser > Pro-Q 3 > Sends: Grit (bx_blackdist2, default; RAT stand-in) | Dry | Slap (EchoBoy, Mix wet, Single Echo, 1/16 note, Studio Tape) | Space (ValhallaSupermassive, Mix 100, rest default).
- Both unproven until Amir loads them on a fresh track.
- 11-13 03:16 (Amir: "i prefer valhalla plate"): Nick Cave Plate chain now ValhallaPlate (default: Chrome, 3.0 s, Mix 100%) instead of UADx Pure Plate. Re-saved from Live; previous file to the Trash. (The chain's "BrowserContentPath" still names Pure Plate: that is only Live's note of how the chain was first made, the device is ValhallaPlate per its plug-in UID.)
