# Melodyne 5 + VocAlign 6 Pro: manual notes for Amir's setup

🎸 Studio · 2026-11-13. Read from the official manuals (text only, scratch trashed).
Installed on this Mac (checked on disk): **Melodyne 5.4.2.006** (edition not readable from disk ❓) and **VocAlign 6 Pro 6.1.30** (VST3 + AU). Live 12.3, which uses VST3 (no AU in Live).

Sources:
- Melodyne 5 manual (studio edition, Live chapter): [Melodyne in Live](https://helpcenter.celemony.com/M5/doc/melodyneStudio5/en/M5tour_DAW_Live?env=live) and the [full manual PDF](https://helpcenter.celemony.com/M5/pdf/melodyneStudio5/en?env=live)
- VocAlign 6 Pro User Guide v1.1: [what it is](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/what-is-vocalign-6-pro.html), [VST3 real-time quick start](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/quick-start-guide-for-vst3-real-time.html), [timing + pitch controls](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/adjusting-the-automatic-time-and-pitch-matching.html), [presets](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/presets-and-getting-started.html), [SmartPitch](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/using-smartpitch.html), [process groups](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/process-groups.html), [protected areas](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/protected-areas.html), [saving audio](https://www.synchroarts.com/manuals/VocAlign6Pro/Manual/HTML/saving-vocalign-audio-data.html)

---

## Melodyne 5 in Live (manual)

- In Live, Melodyne is loaded as an **insert plug-in** and works by **"transfer"**: it records the track while the song plays. The Live chapter describes no ARA mode.
- **Put Melodyne first in the chain**, before the compressor, EQ or effects. Whatever sits before it is frozen into the transfer and can't be changed later.
- **Use the Arrangement View only.** In Session View, Melodyne plays in the wrong places or ignores clip changes.
- **Constant tempo only.** Tempo automation breaks sync. Recommended buffer: **1,024 samples**; bypass Melodyne while recording new takes.
- **Transfers folder**: create it inside each Live project folder (Project Browser > Set Path for Transfers), so the project stays complete when archived.
- **Printing**: Freeze to free the CPU (it can be undone), or Freeze + Flatten to make it permanent. Alternative edits can be saved as plug-in presets.

### Algorithms (which one for what)
| Material | Algorithm |
|---|---|
| Singing, monophonic bass, single-note lines | **Melodic** (it marks sibilants and breaths) |
| **Guitar riffs played as single notes** | Melodic |
| Guitars/piano where you want to edit **single notes inside chords** | **Polyphonic Decay** (DNA). Editor and studio editions only ❓ which one Amir has |
| **Rhythm guitars, distorted riffs, when you only need timing/transpose** | **Universal** |
| Drums | Percussive |
- Pick the algorithm **before** editing; switching later throws away the edits.
- The manual asks for recordings as **dry** as possible: reverb creates overlap and confuses detection.

### Correct Pitch macro
- **Upper slider: pitch center, 0-100%.** At low settings it only touches notes that are badly out of tune; higher settings pull in the closer ones too; 100% = all exactly in tune.
- **Lower slider: pitch drift**, the slow wavering. **Vibrato and fast modulation are not touched.**
- Notes you tuned by hand are **left out by default** (an option includes them).
- Option "Snap to Chord Scale": snaps to the scale or chord instead of the nearest semitone.
- Sibilants move on screen but are **not pitch-shifted acoustically**.

### Quantize Time macro
- It moves each note's **musical starting point** (not the blob's edge) towards the beat, with an intensity slider for how far.
- If Melodyne picks the wrong start point, correct it in Note Assignment Mode first.

### Pitch transitions and drift tools
- Transitions (the slides between notes) only exist across **soft** separations; the Pitch Tool on the back of a note makes them steeper or softer.
- The Pitch Modulation and Pitch Drift tools (sub-tools of the Pitch Tool) scale vibrato or drift per note; double-click resets them.

---

## VocAlign 6 Pro in Live (manual)

- It aligns a **Dub** to a **Guide** in timing and/or pitch: it time-stretches or compresses the Dub so its energy peaks line up, and can match its pitch. The manual names **double-tracking vocal AND instrumental parts** as a use.
- **Live uses the VST3 real-time (capture) version**: VocAlign goes as an **insert on the Dub track**, and the **Guide is chosen through the plug-in's sidechain input**.
  - If you take the Guide's track output, **bypass the Guide's own inserts (delay, reverb) during capture**.
  - Set the loop over the section, press **Capture**, then **Play**. It captures in real time, then processes with the selected preset and outputs the aligned Dub.
  - **Choose the preset BEFORE capturing.** Safe order for a new pair: capture the new Guide first, then change the preset.
  - Print it like Melodyne: freeze/flatten (the manual says "render/bounce" in your DAW).
  - Audio storage: Settings > **"With DAW Session"** keeps the aligned audio inside the Live project (the VST3 version can do this); "Local folder" goes to `~/Music/VocAlignUltraVst3/`.
- **Process Groups**: capture several dubs into a group, and any setting change applies to all of them. This is VocAlign's own grouping, not a Live group track.
- **Protected Areas**: exclude a range of the Dub from time and/or pitch processing (an octave jump, different words, a rasp the Dub doesn't have).
- **Sync Points**: pin matching events in Guide and Dub when different words throw the timing off.

### Controls
- **Match Timing > Max Difference**: the allowed timing window, **200 ms (loose) → 0 ms (tight)**.
- **Flexibility**: **Lowest/Low = small, loose changes: "the setting you should always try first"**. Normal + Pitch for legato lines; Maximum/Compression/Stretch only for takes that are way off (quality suffers).
- **SmartAlign**: leave it on. **Max Shift** of 10-150 ms is for dubs with gaps.
- **High Resolution Editing**: for pure tonal sounds (high voices, flutes, bells).
- **Dub/Guide type**: Normal (most instruments), High voice, Low voice, **High Pitched Instrument (incl. lead guitar)**, **Low instrument (bass)**.
- **Match Pitch**: Max Difference + Pitch Target (0% = Dub, 100% = Guide); a Mode 2 for vibrato-heavy dubs; Transpose up to ±1200 cents; Formant Shift.
- **SmartPitch** (for harmonies): *Match All To Guide* / **Match Unison Only** (tunes the unison parts, leaves the harmony notes) / *Match Unison & Tune Non-Unison*.
- **Presets** are task-based (signal type > task such as vocal or instrumental double > tightness: tight / slightly loose...). Treat them as starting points; save your own versions as User Presets.

---

## What this changes in the advice given in chat (11-13)
- "One VocAlign per double track": ✅ confirmed for Live (an insert on each Dub, Guide on the sidechain). A Live group bus still can't be aligned as one. Process Groups in VocAlign let several dubs share settings.
- Harmonies: the earlier rule was "time only". The manual offers **SmartPitch "Match Unison Only"**, which leaves harmony notes alone. Either works; time-only stays the safe default.
- Guitars: ✅ supported. Start with an **instrument double preset + Lowest/Low Flexibility + loose Max Difference** for L/R rhythm doubles, and go tighter for unison riffs. Pitch matching on chords isn't covered in the manual ❓, so keep guitars on timing only.
- Melodyne on guitars: single-note riffs = Melodic; **distorted rhythm parts = Universal** (timing only). Chord-note editing needs Polyphonic (edition ❓).
- Melodyne prep rules: add **"Melodyne first in the chain, Arrangement View, constant tempo, buffer 1024, transfers folder inside the project"**.
