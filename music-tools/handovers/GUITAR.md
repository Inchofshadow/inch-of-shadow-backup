# Guitar side chat: handover

Written 2026-11-04 from the Samples Audit chat, for the Guitar side chat (a fork of Samples Audit).
Old chat: "Guitar learning focus" (2026-10-02 to 10-17). Its transcript is
`~/.claude/projects/-Users-amir-Desktop-Inch-of-Shadow/81de6cda-49a7-4df3-9679-559fdcee1185.jsonl`.

## The tool: Music Theory Reference
- File: `Inchofshadowcode/music-tools/Music Theory Reference/index.html`. One self-contained file,
  fonts from Google. The folder is its **own small git repo** (no remote). 11-05: the October
  guitar work was committed there (b8825ce, Amir's pick "its own repo"). `Archive.zip` (June copy
  of index.html + theory.js) stays untracked. The parent repo sees all of `music-tools/` as untracked.
- Phone link (private artifact): https://claude.ai/artifact/14cHwebTcq4puFcv5UtJbL
  Republish to the same link after every change.
- Look (10-14): refined "method book" style, bright white page that stays bright in dark mode,
  elegant serif + sans, one deep red for the root. Colors menu: Ink & Oxblood, Prussian & Brass,
  Forest & Rose, Graphite. Sharps/flats use a music-symbol font.

## What it does (built in the old chat)
- Fretboard with tunings, scale degrees, pentatonics, chord shapes, circle of fifths.
- **Follow the chords:** tap a diatonic chord button (no typing chords, Amir said no), and the
  fretboard shows its 5 spots on the neck, low to high, each labelled `Pos N · X shape` +
  `fret a–b · stay / ↑ +3 / ↓ -7` (jump distance from where the hand was). The closest spot is
  picked for you. Chord tones bright, other scale notes faint.
- **+ next spot up / − next spot down:** neighbouring positions in a lighter colour, shared notes
  with a dashed ring.
- **Second guitar:** tuning menu `F B♭ E♭ A♭ C C` (his tuning) and `Drop C · C G C F A D`.
  On the second guitar only `Pos 1–5 + frets` show, no shape names (the top C string breaks the
  CAGED shapes).

## What Amir wants from it
- To jump positions and know the whole neck while playing, not stay in one pentatonic box.
- Inspired by a YouTube video, not a copy of it.
- He said no to: sound/click-to-hear, a note quiz, a backing drone (10-03).

## Deftones tunings (10-14), sources: Premier Guitar interview, Songsterr, sharinglungs fan forum
- White Pony: drop C (Stephen), most trusted. Around the Fur: mostly drop C#.
- From the self-titled album on, Stephen plays 7/8-string tuned much lower; drop C there is Chino's part.
- No band source lists tunings song by song: check the tab and the recording per song.

## From the Samples Audit chat
- Neural DSP presets: `/Library/Audio/Presets/Neural DSP/<Archetype>/User/`
  (Petrucci X 4, Nolly X 18, Cory Wong X 10 on 11-04). The first bytes of a preset file name the
  plugin; the displayed name is the internal `name` field.

## Rules that apply
- **Never use Wikipedia** for music or gear facts: interviews, tabs, musician forums instead.
- Verify before advising; mark unsure facts with ❓.

## Ticket updates (for ⚙️ System to merge into tickets.json)
- 🎸 Studio 9 (new, ST-): "Commit `music-tools/Music Theory Reference/` to git" -> DONE 2026-11-05.
  Committed in the folder's own repo (b8825ce), not the parent repo, per Amir. Archive.zip left untracked.
