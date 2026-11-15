# Gate: the code review fixes of 11-08 (⚙️ System 68 follow-up) (2026-11-15, Fable, on Amir's "gate")

Opus wrote 18 commits starting "Gate fix:" (+394 / -61 lines); the IG and SC owner chats wrote three more (57f7d4c, 27f2b76, 198eafe). I read every source diff, not the reports. Suite today: 1,472 passed on the venv.

## Verdict: approve with one must-fix.

## Must-fix
- **A backup file inside `releases/` still loads as a release and can overwrite the live one** (left over from 704b2cb, the slug fix).
  - The fix blocks `../` paths. But `releases/` itself holds 10 backup files whose names pass the new check, for example `pinocchio-single.bak.20261108_date.json`.
  - Checked today: `storage.load_release("farewell-single.bak.20261106_review")` returns the old backup, and the slug inside it is `farewell-single`.
  - Every save writes to the slug inside the data. The release page migrates and saves on a plain page open. So opening `/release/pinocchio-single.bak.20261108_date` once could write the 8 November copy over the live Half the Night file.
  - Nobody links to those addresses, so it needs a mistyped or pasted URL. The cost if it happens is the release file four weeks before release.
  - Fix (3 lines + a test): `load_release` refuses a name with `.bak` in it (the filter `iter_release_paths` already uses) and refuses data whose own slug differs from the name asked for.

## Read and fine
| Commit | What I checked |
|---|---|
| d87f83c playground keeps | refuses at 200 instead of dropping old keeps; no silent loss |
| a5af692 checklist migration | done or noted items outside the template are kept once, at the end; stable when run again |
| d35c37c track delete | clip blocks follow their tracks; the deleted track's block is dropped |
| 42eeb8c Gap Radar | one run at a time by file lock; `last_run` saved after each paid profile; a dry run still writes nothing |
| ab45e67 daily brief | "Challenge: none" no longer flags; proposals find the real heading line |
| c7c122c bios latest release | with today's files it picks The Deceiver (out), not Half the Night (11 Dec) |
| 0610dac, 74112db review ticks + CLI | older tick never replaces a newer proposal; the documented command form imports |
| a249312 outreach | a handle with no check counts as unverified |
| b19826f, 3383f3b resizers | the error pages keep frames and trim (the variables exist before the early returns); an empty result is an error |
| 11320c2 tournament | a bye wins only when play reaches it |
| a02b3ad fetch_text | header charset, then the page's meta charset, then UTF-8 |
| 58e266d, 3a93428, 4297afa, a026fbd | ticket checker, pruner pattern, contact index, moon script: as described |
| 57f7d4c, 27f2b76, 198eafe (owner chats) | one-line counter; display-only filter; both follow-back keys; follow flags refuse a list with no profile count and save a failed fetch under another name |

## Notes
- 42eeb8c narrows the gap but does not close it: a run stopped in the middle of one profile has paid for that profile and still records nothing. One profile is about $1.10.
- The review file still lists 131 verified non-blocking findings and about 400 unverified low ones with no ticket. They were out of scope for the main move; they are still unread work.
