# Polysix MIDI: notes (🎸 Studio 12)

Written 2026-11-13. Text notes only; the source PDFs were read in a scratch folder and trashed.
Tags: **manual says** = maker's manual · **forum** = user report · ❓ = not confirmed for his unit.

## 1. Which Polysix, which kit (to confirm on his unit)
- Korg PS-6 Polysix (1981): **manual says** rear panel = tape in/out, CHORD MEMORY footswitch,
  ARPEGGIO TRIG IN, VCF fcM IN, PHONES, OUTPUT. **No MIDI from the factory.** So any MIDI socket on
  it is a retrofit.
- ✅ CONFIRMED by Amir 2026-11-13: his kit is the **Tubbutec ModyPoly** (Berlin, older name: Modysix).
  He installed it himself in his Polysix and has the Tubbutec stickers. Chip revision (rev3 or older) unknown.
  - **manual says**: it replaces the key assigner chip (IC6, D8049C) inside. Adds MIDI in + out
    (two 5-pin DINs) and a sustain jack, drilled into the back, usually where the serial plate was.
    Comes with a sticker for the sockets. Rev3 chips have "rev3" printed on the bottom.
- Other Polysix MIDI kits that exist (different menus, different channel steps): Kenton,
  CHD P6-KBD / 8-427, Korg's own Polysix MIDI kit. Only the Tubbutec steps are below.
- How to tell: sticker or text near the MIDI sockets; or the test in 3. below (HOLD blinks = ModyPoly).

## 2. ModyPoly MIDI facts (manual v2.0, Polysix / Poly-61)
- MIDI in: one channel 1-16, or OMNI (all channels). Set in the config menu. **manual says**
- Notes it plays: MIDI notes 36-97 (manual's naming: "C0 to C5", the 5 keyboard octaves).
  Notes outside that range do nothing. **manual says**
- MIDI out: two channels at once, "as-played" (your key presses) and "as-sounds" (what the synth
  really plays: arp, chord, unison...). Each can be set or turned OFF. **manual says**
- MIDI clock: the arp and the S/H LFO can follow MIDI clock (config menu: ARP "m. clock"), with a
  divider. Default arp source = internal. **manual says**
- **No MIDI-activity LED is mentioned** in the user or install manual. ❓ The only proof of MIDI in is
  that the synth plays. **manual says** (absence)
- Factory default MIDI-in channel: **not stated** in the manual. ❓
- **Reading back the current channel: the manual has no way to display it** (the Polysix has no
  screen). ❓ So the practical way is: find it by testing, or just set it.

## 3. Config menu (manual v2.0, section 9 + Figure 3 / 4)
- Enter: hold **HOLD** until it blinks. Exit: press **HOLD** again. **manual says**
- Channel keys: the **lowest 17 keys**: lowest C = OFF / OMNI, C# = ch 1, D = ch 2 ... up to
  E (one octave + a third up) = ch 16. **manual says** (key 1 = C#, stated in 9.9)
- MIDI channel: press the **"In"** key, then a channel key. Same for "As-Played" and "As-Sounds".
  **manual says**
- Where the In / As-Played / As-Sounds keys sit: read from the figure's label positions (the PDF
  picture could not be viewed, only its text coordinates):
  - In = the **4th C** from the left (3 octaves above the lowest C)
  - As-Played = the black key right above it (C#)
  - As-Sounds = the next white key (D)
  - ARP internal / midi note / m. clock / divider ≈ F, F#, G, G# above that; S/H set at the 5th C.
  - Factory reset = the **top C** (manual: "highest note"). Don't touch.
  - ❓ Positions derived from the figure, not stated in words. Tubbutec sells an overlay strip
    (white on black, on the front lip) that labels these keys; if he has it, trust the overlay.
- Troubleshooting **manual says**: "Midi in not working: are you sending on the correct channel? Try
  all 16 channels or configure the midi in channel." Also check the note range.
- MIDI loop warning **manual says**: weird phasing or chord memory / arp acting wrong = MIDI loop back
  (the MPC echoing the Polysix's own MIDI out back into it). Test by pulling one MIDI cable.

## 3b. His actual route (Amir, 2026-11-13): Mac DAW -> RME MIDI out -> Polysix
- Amir triggers the Polysix straight from the RME, not from the MPC.
- On disk 11-13: a **Fireface UFX II** is connected over USB (system_profiler). Ableton Live 11 + 12
  Suite are installed.
- CoreMIDI ports seen on the Mac 11-13 (read-only check): OUT and IN = "USB MIDI Device Port 1",
  "USB MIDI Device Port 2". ❓ Not proven these are the RME (the name is generic, could be another
  USB MIDI box). Test: send a note to Port 1, then Port 2, and see which plays the Polysix.
- Ableton (standard Live setup, ❓ not re-checked in Live's manual this run): Settings > Link, Tempo
  & MIDI > Output row for that port: **Track** on (and **Sync** on for clock to the arp). MIDI
  track > "MIDI To" = that port, channel below = the Polysix In channel (or any channel while it is
  on OMNI).
- Loop risk (manual says, see 3.): if the Polysix MIDI OUT goes back into the RME MIDI IN and the
  Ableton track monitors that input, the Polysix gets its own notes twice.

## 4. MPC Live II side (not his current route for the Polysix) (Akai support article "Configuring MIDI Ports for Multi-MIDI Control")
- Live II physical MIDI outs = **"MPC A" and "MPC B"** (rear panel). **Akai says**
- Menu > Preferences > MIDI/Sync > Output Ports: the port must have **Track** on to show up in a
  track. **Sync** on = it sends clock/transport there (needed for arp on MIDI clock). **Akai says**
- Track: Main > Track View (or Channel Strip) > a **MIDI** track (MIDI program) > **MIDI Output** =
  MPC A or B, channel right below it. Only MIDI programs can send to the 5-pin outs. **Akai says**
- ❓ This article is written for newer 2.x (Multi-MIDI Control); his exact 2.x version is still
  unknown (Menu > Preferences > Info), so menu names may differ slightly.
- Note numbers: Akai shows MIDI note 60 as C3 ❓ (not checked in this run). Play the middle of the
  MPC pad range / keyboard to stay inside 36-97.

## Sources (maker pages and manuals; no Wikipedia)
- Tubbutec ModyPoly page: https://tubbutec.de/modypoly/
- ModyPoly User Manual v2.0 (Polysix / Poly-61): https://tubbutec.de/files/ModyPoly-User-Manual-v2.0.pdf
- ModyPoly Rev.3 install manual, Polysix: https://tubbutec.de/files/ModyPoly/ModyPoly%20Rev.3%20Installation%20manual%20for%20Korg%20Polysix.pdf
- Korg Polysix owner's manual (scan): https://www.vintagesynth.com/sites/default/files/2017-05/p6user.pdf
  (Korg's own download page: https://www.korg.com/us/support/download/manual/1/194/1640/)
- Akai MPC MIDI ports: https://support.akaipro.com/en/support/solutions/articles/69000804431-akai-pro-mpc-series-configuring-midi-ports-for-multi-midi-control
- Forum reports: none found on channel read-back or LEDs (one search, nothing useful).
