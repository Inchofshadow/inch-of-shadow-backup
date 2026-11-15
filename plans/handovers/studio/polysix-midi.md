# Polysix MIDI: handover (🎸 Studio 12, proposed number)

Started 2026-11-13 from the 🎸 Studio parent chat. Amir asked: learn the Polysix manual and the
"Tubetech" MIDI manual, tell him how to check whether his Polysix gets MIDI and which channel it is on.

## State
- ✅ Notes written: `music-tools/gear/polysix-midi.md` (manual says vs ❓, sources listed).
- ✅ Steps given to Amir (test on OMNI first, then set channel, MPC MIDI track on MPC A/B).
- ✅ Kit confirmed by Amir 11-13: Tubbutec ModyPoly, he installed it himself, has the stickers.
  ❓ Asked: is one of the stickers the overlay strip (config-key labels)? If yes, it beats the
  key positions derived from the figure.
- ❓ Exact positions of the In / As-Played / As-Sounds keys were read from the manual figure's
  coordinates (In = 4th C from left, As-Played = C# above, As-Sounds = D above). Not stated in words.
- ❓ Manual has no MIDI LED and no way to read back the channel; factory default channel not stated.
- Nothing changed on his gear. Scratch PDFs/pages moved to the Trash.

- 11-13: Amir drives the Polysix straight from the RME (Fireface UFX II on USB), not the MPC.
  Mac shows MIDI ports "USB MIDI Device Port 1/2" (❓ RME or not). Steps moved to Ableton.

## Waiting for
- Amir's test results: does HOLD blink, does a note from the MPC play it, which channel he set.

## Next (after his results)
- If it plays: note the channel he set in this file + MPC.md (Studio gear setup).
- If not: check cable direction (MPC MIDI OUT A/B -> Polysix MIDI IN), port has Track on, note range,
  then identify the kit from a back-panel photo.

## Ticket updates (for ⚙️ System to merge)
- 🎸 Studio 12 (new):
  - `bucket`: 🔥 now
  - `who`: 🙋 amir
  - `label`: Gear · Polysix MIDI check (ModyPoly channel + MPC track)
  - `next_step`: Amir runs the 4 checks in polysix-midi.md (HOLD blink, OMNI test note, set channel, MPC A/B) and reports back
  - `chrome`: false
  - note: notes file `music-tools/gear/polysix-midi.md`, written 2026-11-13
