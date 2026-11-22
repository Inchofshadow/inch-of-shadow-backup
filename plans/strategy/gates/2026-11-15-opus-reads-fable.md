# Gate: Opus reads what Fable wrote on 2026-11-15 (Opus, on Amir's "Yes, read them")

The other model's read of the three Fable rows in `QUEUE.md`. Each diff was read in full. Checked on disk where possible. Full suite on the venv: 1,522 passed.

## Verdicts

| Work | Verdict |
|---|---|
| Backup files in `releases/` never load (2148cbc) | approve |
| Backup final exact-secret check (331339a) | approve |
| Drawer untagged chip, rose wording (ca0bc79) | approve, 1 small finding (older code, not Fable's) |
| Evening reports + LaunchAgent + two task prompts (d85b528) | approve; first scheduled run tonight 19:55 is the proof |
| Keeps file safe write (66d9175) | approve |
| Resizer hint, blocked pill, 13 px floor (23b9bc9) | approve |
| Overdue date tag + waits-on notes (2d45b82) | approve |
| Memory index repair + four wording fixes + 🛠 BUILD | approve |

## What I checked
- **Releases:** every live release still loads (farewell, pinocchio, the-deceiver) and all 9 backup copies in `releases/` return nothing. A file whose slug does not match its name is refused with a warning.
- **Backup:** the check reads `.env` values and the token files' key fields, never prints them, and stops the build before any readable file that holds one. The 11-15 12:04 backup ran after this commit (05:18) and went up, so the check did not block a real build.
- **Evening reports:** the job runs on the same Python as the other agents, logs off the Desktop, and skips a report whose file exists. The installed agent matches the copy in `stats/launchd/`. Dry run for today: both files would be written. The brief and digest write to the same paths the 20:00 tasks read. Both task prompts run the script only when the file is missing.
- **Keeps:** an unreadable or wrongly shaped keeps file now stops the save with an error the page shows (route returns 400), and the write goes through a temp file and `os.replace`.
- **Colours:** the blocked pill is now light text on oxblood (#FCFAF6 on #8E2A30, well above 4.5:1); the resizer hint uses the on-image colour on the black stage.
- **Overdue tag:** a past due date reads "⚠️ overdue since <date>", a future one "📅 <date>".
- **Memory:** every index link opens a file. Only the two SUPERSEDED memories have no index line, on purpose; both files say SUPERSEDED at the top. "Crowding is a score, not a veto" carries Amir's words of 11-15 ("Only lose points"). Today's link fixes resolve.

## Finding (small, older code from ⚙️ System 94)
- **The tag list itself is read from code, not from `docs/brand/tags.json`.** The drawer takes the list of tags and their meanings from `TAGS` in `release_manager/studio_tags.py`, and drops any tag that is not in it. The brand README calls `tags.json` "the one tag list". So a tag added or renamed by hand in `tags.json` does not show. Today both lists match (37 tags), because Fable changed the rose wording in both places. Fix later: read the list from the file, or say in the README that new tags go into `studio_tags.py`. No harm now.

## Notes, not findings
- The 20:00 chat tasks still need a model to post. On a day the weekly limit is hit, the files are written at 19:55 but not posted; Amir finds them in `docs/reports/`.
- Not proven yet: the first scheduled 19:55 run (tonight).

## Fixed (2026-11-16, Amir: "Yes, fix it")
- The tag list is now read from `docs/brand/tags.json` (`studio_tags.tag_list`); bad entries are skipped and the built-in list stands in only when the file has no usable list. The drawer and the item tags both use it. README says how to add a tag. 3 new tests; suite 1,525 passed. Drawer checked on the restarted Release Manager: 37 tags from the file + the untagged chip, 382 items. Opus wrote this fix, so Fable reads it (QUEUE.md).
