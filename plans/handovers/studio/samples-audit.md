# 🎸 Studio: Samples Audit (handover)

Chat: "Samples Audit" (local_de737ae8-bb3a-4886-861f-37031376c43d), running since 2026-08-31.
Written 2026-11-05. Source of truth for the library: `music-tools/STATUS.md`.

Side topics have their own handovers, not copied here:
- MPC: `music-tools/handovers/MPC.md`. It holds everything from the "MPC Live 2 to version 3+
  upgrade analysis" chat (checked 11-05: that chat has had no new messages since 10-22).
- Guitar / music theory: `music-tools/handovers/GUITAR.md` (from the "Guitar learning focus" chat).

## Where it stands

| Area | State |
|---|---|
| Drum racks (Live User Library, `User - Drum Racks/`) | 41 racks from Sep (Drum Machines 26, Eitan Kicks 6, Splice 9), verified 09-11 |
| CC Snares (2 racks, 64 pads) | built 10-22, **untested** until Amir loads them. 11 real CC snares + closest matches by fingerprint |
| Snares by Key (12 racks, 256 pads) | built 10-22, **untested**. One rack per body note, clear-note snares only (prominence >= 24 dB) |
| Digitakt set `SAMPLES MAC/Digitakt/` | 810 + CC Snares 64 + Snares by Key 256, all 48k/16 mono -6 dB. **Not transferred** |
| Serum presets | organised 10-20: 287 new in 13 theme folders, vibe-first names (file names only). 207 that need Serum 2.1.5 parked in `SAMPLES MAC/_Presets not in use yet/_Serum 2 presets waiting for update (need 2.1.5)/` with `PUT_BACK.sh` |
| Diva / Neural DSP | presets filed in their plugin folders. Diva favourites live in its presetsdb by folder+name |
| Vocal chops | Stickz Vocal Chop Toolkit key-checked and sorted into `Vocals & Acapellas/Chops by Key/` |
| Duplicates | 9,437 samples scanned, 20 in-pack copies moved to `~/.Trash/SAMPLES MAC duplicates 2026-10-22` (PUT_BACK.sh). Cluster/Studio Real and Eitan/Primal copies kept on purpose (projects use them) |
| ZERO G discs | scanned, pitch-tagged in names (zerog_pitch/, undo script) |
| PROJECTS backup | 10-25 to Intenso `PROJECTS BACKUP/2026-10-25/` (33 projects, 38.6 GB, md5-verified). Intenso is now full |

## Decisions made (Amir)
- Serum 1 presets are renamed by FILE only. Never rewrite an `.fxp` chunk (crashed Serum 1 on 10-20, all restored).
- Old Serum presets keep their old names; only the new ones got vibe names.
- Serum 2 may show S1 presets; that's fine.
- CC snares: 2 racks (64). Snares by Key: clear-note only, no "leaning" or no-note snares.
- The Witch House snare kit (`DRUM - Snare Witch House.adg`) stays: only 5 of 22 pads overlap with the CC racks.
- PROJECTS backup: DONE folder skipped (his call). Picked list in the restore note on the drive.

## Open decisions / next steps
- Amir loads CC Snares 1/2 and one Snares by Key rack in Live: only that proves the racks work.
- 7 ZERO G files carry an old pitch tag that disagrees with their Snares by Key rack (e.g. `Snare [D# -44] 49` sits in D). Re-check or leave?
- Witch House racks: agreed plan in STATUS.md (3 drum racks + 57 melodic Simplers), not started.
- Tags / description for older Serum presets: wanted, needs a one-preset test in Serum 2 first.
- After a Serum 2 update to 2.1.5+: run PUT_BACK.sh for the 207 parked presets.
- Not backed up anywhere current: DONE (~57 GB), Doom changes (13.7 GB), Men Machine Remix (8.6 GB), Double Figure changes, Dark Morning, Harmony Test Em, dubby, Inch G#. Needs a second drive.
- `music-tools/Music Theory Reference/` has never been committed to git.
- MPC `.xpm` programs: planning stalled at "too many programs".

## Key files
- `music-tools/STATUS.md` (state + rules), `music-tools/SERUM_PLAN.md`
- `music-tools/drumrack/drumrack_tool_v2.py` (rack builder), `drumrack/snare_pitch/` (cc_style_match.py, build_cc_racks.py, build_key_racks.py, *_built.csv, undo_*.sh)
- `music-tools/drumrack/serum_sort/` (names, plan, backups, undo scripts), `drumrack/vocal_keys/`, `drumrack/zerog_pitch/`, `music-tools/dupes/`
- `music-tools/backup/projects_backup.py` + logs; restore note on Intenso `PROJECTS BACKUP/2026-10-25/HOW-TO-RESTORE.md`

## Ticket updates (proposed, not in tickets.json yet)

| # | Ticket | Area note |
|---|---|---|
| 🎸 Studio 1 | Load-test CC Snares 1/2 + one Snares by Key rack in Live; fix if pads load empty | samples |
| 🎸 Studio 2 | Transfer the Digitakt folder (now incl. CC Snares + Snares by Key), then trash `_removed from Digitakt 2026-09-11` | samples |
| 🎸 Studio 3 | Witch House racks (3 drum racks + 57 melodic Simplers), per the STATUS.md plan | samples |
| 🎸 Studio 4 | Re-check the 7 ZERO G pitch tags that disagree with Snares by Key | samples |
| 🎸 Studio 5 | Serum: update to 2.1.5+, run PUT_BACK.sh; then a one-preset test of tags/description for old presets | samples |
| 🎸 Studio 6 | Second backup drive for DONE + Doom + Men Machine + the other unbacked projects | samples / backup |
| 🎸 Studio 7 | MPC 3 upgrade decision: answer the two questions in MPC.md (clip programs? long held notes?), then test on a copy | MPC |
| 🎸 Studio 8 | MPC `.xpm` programs from the sorted sample sets (restart the stalled plan with a small scope) | MPC |
| 🎸 Studio 9 | Commit `music-tools/Music Theory Reference/` to git | guitar |

### Priority fields (Studio parent chat, 2026-11-05, per AREAS.md "Priority"; 0 now)

| # | bucket | who | label | next_step | chrome |
|---|---|---|---|---|---|
| 🎸 Studio 1 | next | amir | Live: test new snare racks | Load CC Snares 1/2 + one Snares by Key rack in Live; report any empty pads | false |
| 🎸 Studio 2 | next | amir | Digitakt: transfer set | Transfer `SAMPLES MAC/Digitakt/` to the Digitakt; then OK trashing the `_removed` folder | false |
| 🎸 Studio 3 | parked | claude | Live: Witch House racks | Build per the STATUS.md plan when Amir asks | false |
| 🎸 Studio 4 | parked | amir | Samples: ZERO G pitch tags | Amir decides: re-check the 7 tags or leave them | false |
| 🎸 Studio 5 | parked | amir | Serum: 2.1.5 update | Amir updates Serum 2 to 2.1.5+; then Claude runs PUT_BACK.sh | false |
| 🎸 Studio 6 | next | amir | Backup: second drive | Get a second drive for DONE + Doom + Men Machine + other unbacked projects | false |
| 🎸 Studio 7 | parked | amir | MPC: 3.x upgrade decision | Amir answers: clip programs? long held notes across sequence changes? | false |
| 🎸 Studio 8 | parked | claude | MPC: .xpm programs | Small-scope restart after 🎸 Studio 7 | false |
| 🎸 Studio 9 | DONE 2026-11-05 | claude | Guitar: theory tool in git | Committed in the folder's own repo (b8825ce), see GUITAR.md | false |
