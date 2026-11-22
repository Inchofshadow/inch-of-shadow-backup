# Gate: the parent chats' lists, part 3 (2026-11-15, Fable, on Amir's "Yes, read them")

Queue items 14 and 16 of `QUEUE.md`: the Symphonic checklist, the five rule memories, and the three small Socials items. All read in full. Each claim was checked on disk or at its source. Nothing was changed.

## 🎵 Release: Symphonic submit checklist (memory `symphonic-submit-lessons-htn`). Verdict: approve, add three facts.

- ✅ **The cut-off dates are right.** Symphonic's own page (posted 2026-10-27, read today as text): release Nov 27 to Dec 4 = submit by Nov 6; Dec 5 to Dec 29 = by Nov 20; Dec 30 to Jan 5 = by Dec 11.
- ✅ Credits and clip starts match the release file: every track has producer, mixer, mastering, writer and synthesizer = Amir Miller; clips 2:59 and 4:48.
- ❗ **The same table covers edits.** Its heading is "New releases and release edits". For the Dec 11 release that means any edit to the Half the Night release has to be submitted by Fri 20 Nov. The memory only speaks of the first submit. The EP chat should know.
- Add: Symphonic asks for no edits between Dec 14 and Jan 4, and its office is closed Nov 26 to 29 and Dec 19 to Jan 3. A problem on release day gets a slow answer.
- Not verified: "FastLane $15". The page names FastLane but no price.

## The five rule memories. Verdict: approve all five; four small wording fixes.

| Memory | Result |
|---|---|
| `no-key-bpm-in-copy` | Rule is clear in the file. The index line says "BPM only when he asks", but his later line allows BPM in tags and search fields where it helps discovery. A chat that reads only the index could strip the SoundCloud bpm tags. Fix the index line. |
| `side-chat-lessons-before-delete` | Followed this week (three System chats gave lessons before deletion). One link points to `side-chats-lifecycle`; the file is `side-ticket-chats-lifecycle`. |
| `check-memory-before-stating-facts` | Rule is right and matches the Amplify memory (one shot per track, so both tracks). The story line quotes the wrong reason next to the wrong advice and reads as a contradiction. Reword. |
| `dated-items-show-date` | Built (⚙️ System 103) and read in gate round 2. Nothing to fix. |
| `side-chat-names-show-kind` | Three kinds exist: 🎨 DESIGN, 📝 TEXT, ⬆️ UPLOADS. Code and tool work has no kind, so this week's System side chats carried none. A fourth kind is Amir's call. |

## 🎬 Socials: the three small items. Verdict: approve; one scoring gap found.

### Pool refill task (`ig-pool-refill-sun-1115`). Ran as approved.
- ✅ Ran today 09:01 to 09:09 (commit cfcb44b, only the target list). 61 new names: 38 open, 23 already ruled out by the filters.
- ✅ The HikerAPI cap held: 300 of 300 calls today (builder 204, checks 80, the rest 16). Nothing is left for today.
- Note: the task prompt said `python3`, so it ran on the old Python 3.9. It worked. One-time task, nothing to fix.
- Note: the target list's own `stats` block did not move (total_added 293 before and after). It is not kept up to date, so nobody should read it.
- Note: the list was last committed on 11-03, so this commit also holds 12 days of session changes. Git cannot undo this one refill alone.

### SoundCloud blocked-list entry (c9ce914). Correct.
- ✅ One name added to `ig_blocked_accounts.json`. The SoundCloud engine reads that file in all three places that pick targets (contact queue, promo queue, discovery) and matches on the profile slug, so the account cannot come back.
- ✅ Amir's words are in the handover ("Unfollow, drop from list", 11-13).

### sc-engagement end step (task prompt, 11-10). Correct, one gap next to it.
- ✅ The rule (no improvised shell at the end; Read and Write tools for the reports) is in the prompt, and every day from 11-11 to 11-15 has a full report and a score.
- ❗ **A retry day is never scored on volume.** When the 10:00 run finds no Chrome, it writes the marker line `SESSION_INCOMPLETE:` into the day's report. The 13:00 retry appends to the same file and rescores. The scorer finds the marker anywhere in the file and skips every volume target ("session truncated externally"). So a weak retry session would still score high. 11-14 was such a day: it scored 10, and the session did run in full, so no harm that day. Read from `close_loops.py` (lines 563 to 696), not seen in a loop note. Fix belongs to the SoundCloud chat: on a retry, the morning marker should not count once a real session ran.

## Still not read
- Item 17, the vinyl mark memory: 📅 5 Jan 2027.
- Item 18, the Studio service agreement: not ready for a gate.

## Done after the gate (2026-11-15, Amir: "Yes, do both")
- Four memory lines fixed: the index line of `no-key-bpm-in-copy` (BPM fine in tags where it helps search), the link in `side-chat-lessons-before-delete`, the story line in `check-memory-before-stating-facts`, and a note in `side-chat-names-show-kind` that code and tool work has no kind until Amir picks one. Fable wrote them, so Opus reads them (see `QUEUE.md`).
- The edits deadline went to the 🎵 Half the Night EP chat, the retry scoring gap to the 🎬 SoundCloud chat. Both delivered.
- 🎵 Release answered the same day: no Symphonic edit is open or planned before Fri 20 Nov (the vinyl cover batch is parked to 2027-01-05), and the checklist memory now holds the edits rule, the no-edit window, the closures and the unverified FastLane price. Checked in the memory file. 🎬 SoundCloud fixed the retry scoring gap on Amir's go (d40f70d): with a "## 13:00 retry run" section and logged actions, only the retry section decides truncation; a failed retry keeps the old path. Read by System (Opus) the same day: the diff does what it says, 18 tests in test_sc_score_calibration.py pass.
- Fourth side-chat kind added on Amir's "ok" (2026-11-15): 🛠 BUILD for code and tool work. In memory `side-chat-names-show-kind` and its index line. Existing chats are not renamed.
