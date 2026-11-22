# 🎸 Studio · Melodyne prep (first pass) · handover

2026-11-14 · side chat started from the 🎸 Studio research chat (vocal chains).
Set: "D minor 112 BPM voc rec" (Live 12.3, saved by Amir; NOT saved by Claude after the edits).

## What Amir asked
- "lets give it a try now i have 4 voclas track i need u to melodine" (first pass, he does the final touch).
- Key: "its d minor". Scope: "edit on melodine only on bar 9-25 other audio not needed". "Mic 1 is the lead all the others are layers".
- Direction (from the research chat, safe default): Lana Del Rey = lightest correction (center 30-50 %, drift 0-20 %).

## Setup done in Live (screen control)
- 4 copies made with Cmd+D: track 5 = copy of Mic 1 (lead), tracks 7 / 9 / 11 = copies of the 3 layer "Mic" tracks.
- Originals 4 / 6 / 8 / 10 turned OFF (track activator), their chains untouched. Short "Mic" track 12 not touched.
- On each copy Melodyne was dragged to the FRONT of the chain (originals keep Melodyne after Utility/Utility/Tuner).
- Arrangement loop 9-25 is back ON (Claude had switched it off for one transfer pass, then restored it).
- Nothing frozen, flattened, printed or comped. Live set not saved.
- Melodyne edition: Polyphonic Decay is in the Algorithm menu, so it is **editor or studio** (not essential/assistant).

## Per track (bars 9-25 only)
| Track | Role | Algorithm | Applied | Flagged |
|---|---|---|---|---|
| 5 Mic 1 copy | lead | was Polyphonic Decay -> switched to **Melodic** (redetect, no edits lost) | Correct Pitch 43 % / drift 12 % | see below |
| 7 Mic copy | layer | Melodic | Correct Pitch 46 % / 12 % (bars 9-19.5), 45 % / 12 % (19.5-25) | see below |
| 9 Mic copy | layer | Melodic | nothing | reads only as quiet held tones (D3 bars 9-13, a low ~E2 line after); not a clear sung line |
| 11 Mic copy | layer | Melodic | nothing | whole line sits +27 to +90 ct sharp (B3 +74, F3 +82, Gb3 +90, Eb3 +65, C3 +56...); auto-correct would snap notes to the wrong semitone |

Flags (positions are read off Melodyne's grid, about +-1 beat; lyric words not audible to Claude):
- Lead, ~bar 12 beat 1-2: C3 still **-41 ct** after the macro. Suggestion: pull to C by hand, or check if it is a slide into D.
- Lead, ~bar 22 beat 2-3: D3 still **+32 ct**. Suggestion: pull to D by hand.
- Lead, ~bar 20 beat 1: C3 -29 ct (just inside the 30 ct line). Taste call.
- Lead, ~bar 23 beat 1: short **Gb2 +21 ct** blip, out of D minor. Probably a breath or scoop; left alone.
- Layer 7, ~bar 9 beat 2-3: **B2 -15 ct**, out of D minor (B natural). Sounds like a scoop into C3; left alone.
- Layer 7, ~bar 15 beat 2: short **Gb2** blip, out of key; left alone.
- Layer 9: what is this layer? Re-transfer gave only quiet held tones. Check by ear before tuning.
- Layer 11: decide if the sharp line is intended (a detuned layer?) or should be pulled to the grid by hand. Claude did not check the clip's Detune setting.

Left alone on purpose: slides, vibrato, breaths, short blips; no Quantize Time on the lead.
Not done: layer timing alignment to the lead (rule: max ~50 %). That needs VocAlign (capture per layer, lead on the sidechain); not started.

## Round 2 (2026-11-14, Amir: "adjust the things u flagged"; layer 9 = whisper; 11 = a higher-voice try, not detuned on purpose)
- Amir had grouped the set meanwhile: **4 Group** = originals (tracks 5-8, all ON again), **9 Group** = Claude's Melodyne copies (10 lead, 11 layer, 12 whisper, 13 high layer). Loop now bars 9-17. Claude left the groups and the loop as they are.
- Method: select the note, type cents into the inspector first, then the note name (typing the name keeps the cents). Result ~+-10 ct so it stays human.
- Layer copy 11 (was "7"): bar ~9 scoop B2 -> **C3 -15 ct**; bar ~15 blip Gb2 -> **G2 0 ct**.
- High layer copy 13 (was "11"), bars 9-25: every note set onto D minor at +-10 ct, nearest scale note by Hz (C4, G3, F3, E3, Bb3, C3, A2, A3, Bb2). Ab3 notes went to G3 (bar ~12) or A3 (bars ~17 and ~24). Correction to round 1: Melodyne shows cents against its own label, so "Gb3 +90" was really G3 -10; that layer was less off than first reported.
- Whisper copy 12: left alone (no pitch to tune).
- **Lead copy 10: its Melodyne data is gone** (window shows only a short line before bar 9; layer copies kept theirs). Cause unknown. Not redone: needs a new transfer of bars 9-25 (loop is now 9-17), then Melodic + Correct Pitch 43/12 + the 4 lead flags. Waiting for Amir's go.

## Round 3: lead redone (2026-11-14, Amir: "Yes, redo lead")
- Lead copy (track 10, 9 Group): new transfer of bars 9-25 (loop switched off for the pass, back ON at 9-17 after). Algorithm Melodic. Correct Pitch **42 % / drift 11 %** on bars 9-25 only.
- The new transfer detects notes slightly differently, so the round-1 lead flags (C3 -41, D3 +32) no longer show up as such. After the macro, every note over +-25 ct (or out of key) was fixed by hand:
  - ~bar 10: Ab2 -29 scoop (out of key) -> **G2 +10**
  - ~bar 10/11: C3 -25 -> **C3 -10**
  - ~bar 15: C3 -29 -> **C3 -10**
  - ~bar 21: G2 -27 blip -> **G2 -10**
  - ~bar 23: Gb2 +21 blip (out of key) -> **G2 -10**
- All other lead notes in 9-25 read between -21 and +19 ct, left as they are.
- Melodyne still holds notes after bar 25 (left over from the first, interrupted bar-1 transfer). Not touched. Ignore them, or re-transfer if that section is ever needed.
- Slips: one click meant for bar 9 selected the C Plate Reverb return and opened its EMT 140 window (nothing changed, closed). The first re-transfer pass captured nothing because my click had switched Transfer OFF. Always check the dot is red before playing.

## Later 11-14: vocal recording template (built in the open set "D minor 112 BPM voc rec", NOT saved by Claude)
- Amir cleaned the test tracks himself (4 Group / Melodyne copies group removed). Set now: SC, 2 Audio (playback), Vocal group, Returns A-G.
- Vocal (→ Main) holds 5 sub-groups, each → Vocal:
  - LEAD: Lead · Double L · FX Return
  - HARMONY: Harm 3rd L · Harm 5th L · Octave · FX Return
  - BVOX: BV Pad 1 · BV Pad 2 · Whisper · FX Return
  - ADLIB: Adlib · FX Return
  - GUIDE: Guide (MIDI) · FX Return
- Vocal audio tracks: input Ext. In 10 "Arp/Mic" (RME), monitor Off. FX Return tracks: Ext. In 11/12 Return, monitor Off. Live's default track preset (Utility, Utility, Tuner) came with each new track.
- Plan agreed in chat (lean layout: no stereo pairs, names end in L). Two templates wanted: RME (input 10) and Apollo (input 1). Live stores only the input number; the interface is a Live setting.
- Also agreed: Crystallizer "Original Crystals" for an H3000 Crystal Echoes feel; stutter send on hold (Beat Repeat is not what he wants; ShaperBox Volume/TimeShaper explained, still not it).
- Recording advice given: Unison 610-B or 1073, Distressor light (not LA-2A: CL 1B in the racks is already opto), UAD Auto-Tune Realtime (Access/Advanced/X installed, licence unknown) on Console inserts in Mon to hear it without printing; fallback = Auto-Tune Artist in Live with monitor Auto.
- 11-14 the Crystal Castles rack was re-saved from Live and replaced the old file on Amir's yes; old file in the Trash as "FX - Vocal Crystal Castles (old 2026-11-13).adg".

- 15:04-15:06 saved with Live's "Save Live Set As Template" (Amir: no "IoS" in names), checked on disk:
  - `~/Music/Ableton/User Library/Templates/Vocal Template - RME (In 10).als`: 9 vocal tracks on input 10
  - `~/Music/Ableton/User Library/Templates/Vocal Template - Apollo (In 1).als`: 9 vocal tracks on input 1
  - Both also hold the vocal racks Amir loaded on the Vocal group, and the 5 FX Return tracks (11/12).
  - The open set "D minor 112 BPM voc rec" was not saved; its vocal tracks were set back to input 10 on Amir's yes.

- 11-15 VocAlign sidechains set in the open set (VocAlign stays bypassed; only the Sidechain box changed; Amir: no VocAlign on Lead):
  - Double L, Harm 3rd L, Harm 5th L, Octave, Whisper -> Lead, Pre FX
  - BV Pad 2 -> BV Pad 1, Pre FX
  - BV Pad 1, Adlib: none (leaders / free). Live defaults new sidechains to Post FX; each was switched to Pre FX.
  - 11-15 14:23/14:24 both templates re-saved with the sidechains (Amir: "update both"); checked on disk RME = 9x input 10, Apollo = 9x input 1. The 11-14 versions are in the Trash as "... (old 11-14).als". Open set back on input 10, not saved. High-pass agreed for the 5 sub-groups only (CPU), not built yet.

- 11-15 RX in the process: Nectar is NOT installed (checked on disk). Amir set RX 11 Audio Editor as Live's Sample Editor himself. Workflow: Consolidate (Cmd+J) the take first, clip view Edit -> RX -> Cmd+S -> Live reloads. Order: record -> comp -> RX -> Melodyne -> VocAlign -> mix. RX Connect not added to the templates.

## 11-19: second song "Night voc rec II com" (119 BPM, key F Dorian per Amir; Live shows A minor)
- Tracks 10 Lead (Bounce) sm7b and 11 Lead (Bounce) tlm, already transferred by Amir (whole take, Melodic).
- Both: Correct Pitch 46% / drift 12% on all notes.
- Hand fixes: t11 A2 grace note (out of key) -> Bb2 -10 ct (~bar 13); t11 G2 -24 -> -10; t10 Bb2 -27 -> -10. Everything else within +-21 ct.
- Line levels (Melodyne Amplitude, per phrase, from RMS read off the transfer wavs; targets ~-33 dB):
  - t11: L1 -1, L2 -1, L3 +2, L4 +2, L5 +1, L6 +1, L7 -1 dB (last short phrase untouched)
  - t10: L1 +2, L3 +2, L4 -3, L5 +3, last -2 dB (L2, L6 untouched)
- Melodyne ruler shows bars offset by -640 (Live bar 11 = -629); sync fine. Set not saved.

- 11-19 round 2 (Amir: vibrato/drift/transitions/formant/amplitude/attack; TLM sibilants -20%; do 1-4):
  - t11 (tlm): Sibilant Balance -20% on all notes; breath/scoop blobs before phrases -6 dB.
  - t10 (sm7b): Formants -10 ct on all notes (so the two takes stack wider); 8 breath blobs -6 dB.
  - Vibrato (Pitch Modulation), Pitch Drift, transitions, Attack Speed: checked, left as sung (long notes steady; no shaky vibrato found).
  - Line levels from round 1 re-verified on both tracks after a selection slip (see lessons).
- Lesson: in Melodyne, SHIFT-click selects a RANGE, not single notes. Use CMD-click to add single notes, and check the selection before typing a value. A shift-click selection pulled whole lines to -6 dB on both tracks; fixed by Undo (t10) and by re-setting each line (t11), all values verified note by note.

## Lessons / mistakes (for the next Melodyne run)
- Claude first started a transfer from bar 1 with the loop off; Amir stopped it: only the recorded section (the loop) matters. Ask the range first.
- One device move first landed on the ORIGINAL Mic 1 (view scrolled after the duplicate); undone at once with Cmd+Z.
- A vertical drag in Melodyne's time ruler zooms but also starts Melodyne's own preview playback with auto-scroll; that made box selections fail. Stop it before selecting.
- Melodyne disarms Transfer by itself after one pass; check the button before playing.
- Box-select works with mouse-down / slow moves / mouse-up starting inside the note rows (not the top 20 px).

## Ticket updates (for ⚙️ System to merge)
- 🎸 Studio 13 (new, next free number after Studio 12; ⚙️ System to confirm):
  - `label`: Vocals · Melodyne first pass (D minor 112 voc rec)
  - `bucket`: 🔥 now
  - `who`: 🙋 amir
  - `next_step`: Amir listens to copies 5/7 (bars 9-25), fixes the flags by taste, decides on layers 9 and 11; then save the set and move the Melodyne transfers folder into the project folder
  - `chrome`: false
  - note: handover `plans/handovers/studio/melodyne-prep.md`
