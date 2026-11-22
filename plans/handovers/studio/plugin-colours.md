# 🎸 Studio: plugin colours handover

Chat: plugin colours (side chat from the 🎸 Studio parent chat). Written 2026-11-21.
Ask (Amir, 11-21): "organise my plugin list colours in Ableton ... scan all my plugins and suggest alternatives. I feel I have too much coloured that I don't use."

## Where it stands

- ✅ Proposal ready, nothing changed in Live: [PROPOSAL.md](../../../../Documents/plugin-colours-2026-11-21/PROPOSAL.md)
- ✅ Record before change: [tags-before-2026-11-21.md](../../../../Documents/plugin-colours-2026-11-21/tags-before-2026-11-21.md) + DB copies in `Documents/plugin-colours-2026-11-21/backup-before/` (copied 15:25 with Live OPEN, incl. -wal/-shm; take a fresh copy with Live closed before applying).
- ⏸ Waiting for Amir: yes/no on the system, Gray = Vocal (A) or Instruments (B), apply method.

## 11-21 19:11: Favorites cleanup done (Amir's list)

- Done in Live by screen control (right-click → Favorites), Live stayed open; checked in Live's database after.
- 🔴 removed: Oxford Inflator (now 🔵), FAN, EchoBoy, Crystallizer (now 🟢), Thermal (now 🔵), Glue Compressor, External Audio Effect (both now no colour).
- 🔴 added: UADx Studio D Chorus (now 🔴🟢).
- Favorites: 33 → 27. Undo: the before list, [tags-before-2026-11-21.md](../../../../Documents/plugin-colours-2026-11-21/tags-before-2026-11-21.md).
- Not changed (Amir kept them): Tekturon, Repeater, soothe2, HG-2MS, SplitEQ, RC-20, ValhallaPlate, VintageVerb, bx_digital V3, Saturn 2, Lexicon 224, Ampex, Shimmer, MicroShift, External Instrument. Not added: Little MicroShift, Waves Tune RT.
- Next: the other colours, one at a time, when Amir asks.

## 11-21 evening: new layout agreed step by step

- Rule from Amir: colours by job, not by usage (memory plugin-colours-by-job-not-usage). Chorus/flanger stay 🟢. Soundtoys Little/Jr out where the full version exists.
- Pending yes: 🟢 Little PrimalTap out, PrimalTap in. 🟣 Trigger 2 + Torque out.
- Plan: ⚪ Gray = Vocal tools + a few synths Amir picks; all synths as presets in a flat "Synths" place.
- ✅ Test 19:48: folder `~/Music/Ableton/User Library/Synths` (new), Serum 2 loaded at Init on a temp MIDI track in the open Untitled set, dragged into the folder → Live wrote `Serum 2.vstpreset` (2.9 KB, VST3 preset format, not .adv), temp track deleted. Folder dragged onto Places → "Synths" is a one-click flat list. Set not saved.
- Note: Cmd+Shift+T in his template makes a MIDI track with Drum Rack + 2 Utility + Tuner (his default); loading a synth replaces the Drum Rack only.

## 11-21 19:52-20:00: Gray trimmed + Synths place filled (Amir: "all synths to the folder, keep ... in grey")

- ⚪ Gray now (checked in Live's DB): Diva, Serum, Serum 2, Omnisphere, Osirus, OsTIrus, MonoPoly, M1, TRITON Extreme, Archetype Cory Wong X / Nolly X / Petrucci X + Live's Vocoder (left in: vocal tool, Gray is to become Vocal). 35 others untagged (list in tags-before).
- Method: select item, wait, press 7 (Gray toggle). Without ~0.6 s waits the key press is lost. Cmd-click multi-select is unreliable.
- 📂 `User Library/Synths` (also under Places): 19 presets, each loaded as it opens and saved by dropping the device on the Synths place (Live names it after the device): Analog, Diva, Junior, M1, MS-20, Meld, MonoPoly, Omnisphere, Operator, Osirus, OsTIrus, Serum, Serum 2, TRITON Extreme, UADx Anthem, UADx Moog Minimoog, UADx Opal, UADx PolyMAX, Wavetable. Plug-ins = .vstpreset, Live devices = .adv. Wavetable/Operator loaded Amir's own default presets ("Using Default Preset").
- Temp track 39 deleted. Track "38 MIDI" in the Untitled set is not mine (appeared during the session), left alone. Set not saved.
- Next: vocal tools into Gray (list to confirm), rename Gray → Vocal; green swap (Little PrimalTap → PrimalTap); purple: Trigger 2 + Torque out.

## 11-21 20:03-20:07: vocal tools into Gray (Amir: "all grey", 30+31 also purple)

- Snapshot before: `Documents/plugin-colours-2026-11-21/tags-snapshot-2026-11-21-2003.txt` (file_id|name|colors).
- 19 vocal tools: purple removed, Gray added (other colours kept: Auto-Tune 🟠, Little AlterBoy / Waves Harmony / King's Mics 🔵).
- Quadravox and MicroShift: Gray + Purple, blue removed (MicroShift keeps 🔴). Xvox Pro, PitchFunk: Gray, blue removed.
- Added Gray (Waves = Stereo version only): OVox Stereo, Doubler2 Stereo, Abbey Road Reel ADT Stereo, Silk Vocal Stereo, JJP-Vocals Stereo, UADx Topline Vocal Suite + Vocal Tune, Xpitch, Xvox Comp/DS/SFX/Space/Tone.
- Checked in Live's DB: Gray = 49 items (12 synths/amps + Vocoder + 36 vocal). Purple = 28.
- 20:09: blue removed from Waves Harmony + King's Mics Mono/Stereo (Amir). Gray collection renamed "Vocals" in Live (right-click → Rename).
- 20:11 (Amir "yes"): Trigger 2 + Torque Mono purple removed (no colour now); Little PrimalTap green removed, PrimalTap green added. Checked in DB.
- 🟠 EQ added (Amir picks 7 8 10 11 12 14; "use Mono version not stereo"): Neutron 5 Equalizer, API-550A/550B/560 Mono, Abbey Road RS56 Passive EQ Mono, Curves AQ Mono, Tonal Balance Control 2, UADx Hitsville EQ Mastering. Checked in DB; Stereo versions untagged.
- ⚠️ Slip, fixed: key 3 is Dynamic, not EQ. Live's shortcut keys: 0 clear, 1 Favorites, 2 EQ/Filter, 3 Dynamic, 4 Reverb/Delay, 5 FX, 6 Mix/Master, 7 Gray/Vocals (all toggles). Search results re-sort after a tag change: look before each click.
- Open: the vocal Waves entries were tagged as Stereo (Doubler2/4, OVox, Reel ADT, Silk Vocal, JJP, Harmony, Tune RT, Butch Vig is Mono); Amir prefers Mono, ask whether to switch.
- Mono switch for vocal Waves: cancelled by Amir (stopped mid-step, nothing changed: Doubler2 Stereo still tagged). His rule: Mono only for plugins he puts after a mono source; Doubler etc. stay Stereo; DeEsser + RVox keep Mono AND Stereo.
- 20:32 🟡/🔵 review (Amir picks): Glue Compressor → 🟡 (yes). Little AlterBoy: 🔵 out, 🟣 in (keeps Vocals). Checked in DB.
- Harmonics Analog Saturation, Live Compressor, ShaperBox 3 + Saturn 2: Amir "leave that" → unchanged.
- 20:33 after Amir's VST rescan: all tags unchanged (diff vs 20:03 snapshot = only tonight's edits). New plugin UADx Hemisphere Mic Collection → ⚪ Vocals. 20:52 UADx FATSO Sr → 🟡 (Jr had no tag).
- ✅ All 7 colours reviewed with Amir 11-21. Ticket can close once Amir approves.

## Facts found (checked on disk)

- Tags live in `~/Library/Application Support/Ableton/Live Database/Live-files-12300.db`, table `files`, column `colors` (bitmask: 1 none, 2 red Favorites, 4 orange, 8 yellow, 16 green, 32 blue, 64 purple, 128 gray). Checked against his screenshot: Crystallizer 19 = red+green, Auto Pan-Tremolo 81 = green+purple.
- Rows with `flags & 16` are stale (plugin gone); Live hides them. 36 stale tagged rows (plugins removed 10-12).
- `use_count` in the same table = Live's own load counter (Pro-Q 3 1358, Volcano 3 506).
- `.als`: VST3 name sits after `</Preset>` inside `Vst3PluginInfo`; `.adg` racks only store the VST3 Uid (4 signed ints) → mapped to names through `Live-plugins-1.db`.
- Scan: 578 files (PROJECTS, MIXING, User Library; Backup folders skipped). Scripts in `Documents/plugin-colours-2026-11-21/scripts/` (scan_als.py, propose.py, write_page.py).
- Today 264 tagged items. Proposal: 101 keep, 53 change colour, 4 new tags, 110 untag.
- ⚠️ Murda Melodies (14 sets in 2026) and Storch Filter (13 sets in 2026) are marked gone in Live's database. Not investigated (out of scope).

## Rule used

Job colour only if 10+ sets saved in 2026 or in a User Library rack. New tags also need Live use count 5+ (template devices excluded). 🔴 = 2 most used per job + Arpeggiator/LFO (MIDI, not scanned).

## Next

- On Amir's yes: close Live → fresh DB backup → script writes new `colors` → reopen Live → spot-check 5 items. Undo = copy backup back with Live closed. Not yet tested whether Live keeps DB edits made while closed: test on ONE item first.
- Rename 🔵 FX → Colour/FX and ⚪ Gray → Vocal (if A) in Live.
- Never uninstall anything (not asked).

## Ticket updates (for ⚙️ System to merge)

- 🎸 Studio (new, next free number; ⚙️ confirms):
  - `bucket`: 🔥 now
  - `who`: 🙋 amir (pick), then 🎃
  - `label`: Plugin colours · cleaner Live browser tags from usage evidence
  - `next_step`: done 11-21; Amir approves → close (scratch DB copies moved to Trash; backup-before/ kept as undo)
  - `chrome`: false
