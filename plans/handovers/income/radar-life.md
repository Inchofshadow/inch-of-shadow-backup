# 💶 Radar · Life (handover, 2026-11-05)

Chat: "💶 Radar · Life" side chat of 💶 Income (replaces the old "💶 Radar · Life" chat once Amir has checked this one).
Job: get the Life radar profiles merged into apartmentcode, on Amir's decision.

## Result (2026-11-05)
- ✅ Merged with option 2 (Amir: "Option 2: profiles + line") as **0af378e** on `gewobag-wbs-form-variant` in apartmentcode. Its tree is the same as e07515c.
- ✅ `tests/test_radar_profiles.py`: 24 passed.
- ✅ Amir's 2 `.gitignore` lines (`.chrome_profile_gewobag/`, `.brave_profile_bot/`) stay uncommitted. All his other uncommitted bot files are untouched.
- Not on `main` yet: it reaches `main` when `gewobag-wbs-form-variant` is merged.
- `refs/heads/claude/radar-life-02d979` + its worktree are now redundant (safe to delete later, on Amir's OK).

## Facts on disk (checked 2026-11-05, read-only)
- Work = commit e07515c on `refs/heads/claude/radar-life-02d979` (worktree `apartmentcode/.claude/worktrees/radar-life-02d979`).
  10 files, +517: `radar/README.md`, 7 profiles in `radar/profiles/` (money-back, deal-alerts, free-stuff-berlin,
  before-you-sign, regret-check, trip-prep, english-doctors-berlin), `tests/test_radar_profiles.py`, 3 lines in `.gitignore`.
- e07515c sits directly on c2f245b = tip of `gewobag-wbs-form-variant` (the branch the main checkout is on).
  So it is a fast-forward for that branch. That branch is 2 commits ahead of `main` (80304ce, c2f245b: Gewobag apply work), not merged to main.
- Clash: only `.gitignore`. Branch adds `radar/reports/` at the end; Amir's uncommitted edit adds
  `.chrome_profile_gewobag/` + `.brave_profile_bot/` at the same spot. A normal merge refuses while his edit is uncommitted.
- No other overlap: `radar/` and `tests/test_radar_profiles.py` don't exist in the main checkout.
- ~104 other uncommitted/untracked files of the flat bot in the checkout: not touched.

## Merge options (for Amir)
1. Profiles now, `.gitignore` line later: commit only `radar/` + test on `gewobag-wbs-form-variant`. Add the `radar/reports/` line when he commits his bot edits. Until then, don't run a Life report (reports could get committed by mistake).
2. Profiles + the one line now: same commit, plus only the `radar/reports/` line staged into `.gitignore`. His 2 lines stay uncommitted, untouched. The file gets one extra line appended in the working tree.
3. Wait: he commits his `.gitignore` edits first, then a clean fast-forward.
Side question: land on `gewobag-wbs-form-variant` (where it is built) or on `main` (would need a cherry-pick so the 2 Gewobag commits don't come with it).

## Open decisions (Amir)
- None for the merge. Later: delete the old radar-life branch/worktree?

## Ticket updates (for the ⚙️ System chat to merge)
- 💶 Income 8: status `waiting` -> `done`; clear blocked_on. Add note: "2026-11-05 Amir chose option 2: merged as 0af378e on gewobag-wbs-form-variant (apartmentcode); radar/reports/ ignored; his .gitignore edits left uncommitted; 24 tests pass. Reaches main with that branch."
- income-500.md Side chats table: Radar · Life -> merged (0af378e).
