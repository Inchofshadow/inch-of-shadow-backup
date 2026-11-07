# MPC side chat: handover

Written 2026-11-04 from the Samples Audit chat, for the MPC side chat (a fork of Samples Audit).
Old chat: "MPC Live 2 to version 3+ upgrade analysis" (2026-10-22). Its transcript is
`~/.claude/projects/-Users-amir-Desktop-Inch-of-Shadow/0a255974-7f35-4855-8a2f-3b0be8b65257.jsonl`.

## Amir's setup
- MPC Live II, still on MPC 2.x (exact version unknown: Menu > Preferences > Info).
- It is his studio brain: everything runs through it, it sends MIDI notes and clock to other gear.
- Plays live with Next Sequence and mutes per sequence.

## What the old chat found (MPC 2.10 manual vs MPC 3.9 manual + 3.9 / 3.9.1 release notes)

**Risks for his setup (the reasons to stay on 2.x for now):**
1. Clip programs exist in 2.10 (37 mentions) and are not in the 3.9 manual at all.
2. Held notes cut off when the sequence changes: a known bug in 3.9 and 3.9.1 (Akai's own notes).
   Bad for long pads on external synths.
3. Incoming program change can switch Program, Sequence or Track on 2.x; only Sequence or Track on 3.9.
4. 3.9: audio recording is disabled while following external MIDI Clock (MTC needed instead).
5. Old projects get converted on import ("may not load with identical behavior"). Projects saved
   in 3.x do not open in 2.x. Firmware can be downgraded (Preferences > Info > Downgrade).
6. Users report a half-second skip when switching sequences in 3.6/3.7, worst on imported old
   projects. No official fix found. Other latency reports: 2-3 s lag switching drum tracks on a
   Live II (3.4 beta, maybe fixed); ~4-6 ms with insert effects is normal on 2.x too.
   Clock jitter: no source says 3.x is better or worse than 2.x.

**What stays the same or improves:**
- Next Sequence works the same (Next Bar / Sudden). Per-sequence mutes exist but must be switched on:
  Track Mute > settings > "Track Mute State Per Sequence". "Instant Track Mute" is replaced by an
  Event/Audio switch. Pad Mute only on drum tracks.
- MIDI out to synths, clock out, MMC, CV/Gate: all still there.
- New: arranger, knob macros / XY, MIDI knob mode, disk streaming. Clip launching on the Live II
  needs the paid Pro Pack (Akai's pages disagree on this).
- Live II limits unchanged: 8 plugin tracks, 64 voices.
- Corrected in the old chat: one track playing an internal sound AND external gear already works on
  2.x (MIDI Send / Send To), so it is not a reason to upgrade.

**Open questions the old chat left with Amir:** does he use clip programs? Do his synths hold long
notes across sequence changes? If either is yes, staying on 2.x is safer. He was also offered a
per-device check of his connected gear (not answered yet).

Sources: MPC 2.10 User Guide, MPC Standalone 3.9 User Guide, 3.9 and 3.9.1 Release Notes (cdn.inmusicbrands.com).

## From the Samples Audit chat (sample library side)
- `music-tools/STATUS.md` is the source of truth. Open item there: **MPC Live 2 `.xpm` programs,
  planning stalled at "too many programs"**.
- Ready one-shot sets that also suit the MPC (full quality, named by note):
  `SAMPLES MAC/CC Snares/` (64) and `SAMPLES MAC/Snares by Key/<note>/` (256).
  Digitakt copies (48k/16-bit mono) are in `SAMPLES MAC/Digitakt/`, not needed for the MPC.
- Vocal loops were kept whole on purpose: Amir slices them on the MPC.
- Intenso has an `MPC/` folder (Akai Scott Storch Presents packs).

## Rules that apply
- Never move/rename/delete his files without a yes per action; bulk jobs = dry run first.
- Verify before advising; say "user report" vs "Akai says".

## MPC side chat (🎸 Studio), from 2026-11-05
- Started 11-05 from the 🎸 Studio parent chat; replaces the old upgrade-analysis chat (left as is).
- 11-05: asked Amir the two open questions (clip programs? long held notes across sequence changes?)
  plus his exact 2.x version. Waiting for his answers. Nothing tested, nothing changed on the MPC.
- 11-05: PAUSED by Amir. Resume = he answers the two questions; nothing runs until then.

## Ticket updates (for ⚙️ System to merge)
| # | Ticket | State |
|---|---|---|
| 🎸 Studio 7 | MPC 3 upgrade decision: answer clip programs + long held notes, then test on a copy | open, waiting on Amir's two answers |
| 🎸 Studio 8 | MPC `.xpm` programs from the sorted sample sets, small scope restart | open, after 🎸 Studio 7 |
