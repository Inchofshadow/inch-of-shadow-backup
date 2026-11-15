# Gate: backup snapshot hardening (2026-11-15, Fable, on Amir's "gate")

Opus hardened `plans/cleanup/backup_snapshot.py` on 11-08 (commits 2d729e9, c45aea0) after a security review. Read: the whole script. Checked against the real snapshot in `~/Backups/inch-of-shadow-github` (last build Sun 11-08 12:04, commit 60ec6ee).

## Verdict: approve, one should-fix.

| Claim | Checked | Result |
|---|---|---|
| Reports are locked since 11-08 | the snapshot's `docs/reports/` | ✅ 236 files, all `.enc`, none plain; the SI cleanup plan is `.enc` |
| Secrets are caught by name in any case and with backup suffixes | `is_secret()` + its tests | ✅ `credentials.json.bak.1`, `YouTube_Token.json` sort as NEVER |
| No secret value is in any readable file of the snapshot | every value from `.env`, `credentials.json`, `youtube_token.json`, `.sc_user_token.json`, `.flask_secret` (25 values, none printed) searched in all 5,401 plain files | ✅ no secret found. The only matches are Amir's own artist Gmail address in 10 docs, which is not a secret |
| Unknown binaries and files too big to scan go up encrypted | `has_people_data()` | ✅ fails closed; fonts and media stay plain as intended |
| The key cannot sit inside the code folder or the snapshot | `build()` | ✅ refused with a clear message; test covers it |
| The build re-checks secrets before copying | `build()` calls `is_secret()` on every outgoing file | ✅ |

## Should-fix
- **Add the exact-value check as the last step of every build.** `is_secret()` reads content only in data files, with one JSON pattern. A token pasted into a `.md` note, a `.py` file or a `KEY=value` text file would go up readable. The check I ran today closes that hole for every current secret: before the build finishes, search all outgoing plain files for each value from `.env` and the token files, and stop the build on a hit. About 15 lines, no new dependency.

## Still open, not part of this gate
- The 11-07 commit (e0e9466) in the backup repo still holds the plain SI cleanup plan, and the weekly push adds history instead of replacing it. That is ⚙️ System 71, Amir's.
