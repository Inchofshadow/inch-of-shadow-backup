# 🎸 Studio · Night vocals · Melodyne prep (read only, 11-18)

Set: `~/Desktop/PROJECTS/Night F Dorian 119/Night \`voc rec II Project/Night \`voc rec II.als` (saved 22:12, read from disk only; no screen control, Amir has not approved that yet).
Amir: no comp now, Melodyne on everything, song in F minor, In 1 = SM7B, In 2 = TLM. Channels to work on come from him after the transfer.

## What is in the set (from the file)
- Loop = beats 48-128 = bars 13-33 (20 bars, ~40 s at 119 BPM). Almost every take sits in this range.
- Lead: 4 tracks, two mic pairs recorded together.
  - Pair A: tracks 122 (In 1, SM7B) + 144 (In 2, TLM). 35 take lanes, 21 full loop takes. Main lane: Lead 28 / 35 / 34 / 4, beats 48-208.
  - Pair B: tracks 148 (In 1) + 149 (In 2). 43 take lanes (looks like pair A's lanes + 8 more), 27 full loop takes. Main lane: Lead 36 + Lead 42, beats 35-128.
- BV Pad 1 (In 1): 6 lanes. BV Pad 2 (In 2): 5 lanes. Whisper (In 1): 6 lanes.
- Adlib: 2 tracks, In 1 + In 2, 10 lanes each.
- Double L, Harm 3rd/5th, Octave: empty.
- Melodyne is not on any track yet in the saved file. The set's own Key/Scale setting reads root 9 (A), not F.

## Settings (from what we decided in the D minor round)
| Track kind | Algorithm | Correct Pitch | Hand fixes |
|---|---|---|---|
| Lead | Melodic | center 42 %, drift 11 % | any note over +-25 ct or out of key -> +-10 ct |
| Layers (BV pads, adlibs, doubles) | Melodic | center 45 %, drift 12 % | out-of-key scoops -> nearest scale tone, +-10 ct |
| Whisper | none | none | no pitch to tune |
Always: only the loop range (bars 13-33); leave slides, vibrato, breaths and short blips; no Quantize Time on the lead; layer timing later with VocAlign (max ~50 %), not Melodyne.
Scale: F minor = F G Ab Bb C Db Eb. The project is named "F Dorian" (D natural, not Db). Check the sung D's before any snap.

## Open points for Amir
1. Transfer records only what plays, and Live plays only the main lane. Take lanes are not captured. "Melodyne everything" = each take moved to the main lane (or its own track) and transferred.
2. Two mics, one performance: if both mics stay in the mix, different Melodyne edits on each will phase. Tune one mic per part, or tune both with exactly the same edits.
3. F minor or F Dorian (Db or D)?

## Amir 11-18 (answer)
- Key = **F minor** (F G Ab Bb C Db Eb). Dorian question closed.
- He recorded one long looped take (~16 min) and is transferring it into Melodyne himself now. Claude tunes that whole capture with the settings above. Then Amir consolidates and picks the takes himself (easier after tuning).
- Claude waits for: his go for screen control + the list of channels.

## Measured on THIS song (11-18, `music-tools/melodyne/pitch_measure.py`, read-only, numpy YIN, seconds per file)
Amir: settings must fit this song, not the D minor one. Files -> tracks from the .als: SM7B (In 1) = Lead 0004 [205257] / Lead 0005 [211808]; TLM (In 2) = Lead 0003 [205257] / Lead 0004 [211808].
- Lead long take [205257] (16.6 min, the G/Bb line), both mics agree: G sung **-15 ct** (250 notes), Bb **-30 ct** (~95 notes), plus 41-74 notes read as "A +32..+40" = Bb about 60 ct flat. Systematic flat on the top notes.
- Lead take [211808] (7.8 min, C/Db/Eb line): per-note medians +3..+7 ct, only scatter, no pattern.
- BV Pad 1/2: scatter, about +9 ct sharp on average. Adlibs: scatter, 18 % out of key (slides/scoops).
- All parts: median |offset| ~19-20 ct, in-note drift median ~25-31 ct (counts scoops too; Melodyne's own blobs will read a bit cleaner).

Settings for this song (scale F minor, NOT chromatic: then the flat Bb's go up to Bb, not down to A):
| Part | Center | Drift | By hand |
|---|---|---|---|
| Lead, G/Bb line [205257] | 50 % | 15 % | > +-25 ct -> +-10 ct |
| Lead, C/Db/Eb line [211808] | 40 % | 12 % | > +-25 ct -> +-10 ct |
| BV Pad 1/2, Adlib | 45 % | 12 % | out-of-key scoops left unless held |
| Whisper | none | none | none |
Both mics of one part: same macro + the same typed cents per note, so they stay together when blended. Amir blends SM7B + TLM; mic timing (TLM above him) not touched.

## All takes (11-18, Amir: "It's should read all takes!")
`music-tools/melodyne/take_measure.py SET.als` reads every take-lane clip via its warp markers (18 s for the whole set). Full list: `music-tools/melodyne/night-takes.txt` (+ .csv). 242 clip pieces, 148 unique (the second Lead pair repeats the first). Empty: Adlib 214057 (0 bytes); Whisper has no pitch to score.
| Section | Takes | Median off | Notes > 25 ct | Average | Best by pitch (both mics agree) |
|---|---|---|---|---|---|
| Lead bars 13-33 | 26 | 18 ct | 39 % | -5 to -7 ct (flat) | Lead 42, Lead 41, Lead 5 / Lead 4 |
| Lead bars 29-49 | 10 | 18 ct | 35-39 % | +6 to +8 ct (sharp) | Lead 35, Lead 33, Lead 15 |
| BV Pad 1 / 2 bars 13-33 | 4 / 3 | 16 ct | 37 % | +8 to +9 (sharp) | Pad 1: take 4 · Pad 2: take 3 |
| Adlib bars 13-33 | 9 | 18-19 ct | 41-43 % | +2 to +3 | Adlib 6, Adlib 8 |
Per take the average runs from -16 ct (Lead 9, 11) to +11 ct. Pitch only: says nothing about feel or words.

Settings, final for this song (F minor scale):
| Part | Center | Drift | By hand |
|---|---|---|---|
| Lead bars 13-33 (flat G/Bb) | 50 % | 15 % | > +-25 ct -> +-10 ct |
| Lead bars 29-49 (sharp side) | 45 % | 12 % | > +-25 ct -> +-10 ct |
| BV Pads, Adlibs | 45 % | 12 % | held notes only |
| Whisper | none | none | none |

## CORRECTION 11-18 23:00: key = **F Dorian** (F G Ab Bb C D Eb), Amir: "i confused!! its F dorian". Replaces every "F minor" above. Only D vs Db differs.

## Done in Live 11-18 22:50-23:03 (Amir: "go"; set NOT saved by Claude)
- Melodyne scale (project-wide): was **G Minor** -> F Minor -> **F Dorian**.
- Lead 8 + 9 (long take, 18 min): Melodic. Correct Pitch 50 % / 15 %, snap to scale. First run was in F minor; restored with Restore Original > Pitch > Undo All Pitch Changes, then re-run in F Dorian. Check: a Bb3 went +36 -> +21 ct.
- Lead 10 + 11 (Lead 42): were detected **Percussive** -> redetected Melodic (no edits existed). Correct Pitch 45 % / 12 %, snap F Dorian.
- Adlib 31 + 32 (the active Melodyne at the END of the chain; the template Melodyne before VocAlign stays off): were **Polyphonic Decay** -> redetected Melodic. Correct Pitch 45 % / 12 %, snap F Dorian.
- Not done: hand fixes (> +-25 ct -> +-10 ct). Too many notes over 16 min to do by screen; better on the takes Amir picks after consolidating.
- Slip: one menu click landed off target while switching Lead 10 and closed the window; nothing changed by it.
- Amir 11-18: hand fixes "Only picked takes" -> Claude waits until he has consolidated and named the takes.
