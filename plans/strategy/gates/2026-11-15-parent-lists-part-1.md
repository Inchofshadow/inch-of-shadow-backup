# Gate: the parent chats' lists, part 1 (the three riskiest) (2026-11-15, Fable)

From the queue of 18 items in `QUEUE.md`. Read first because they touch live automation or the release day.

## 1. Instagram follow-back check combines follower lists (aa09659, 🎬 Socials). Verdict: approve with fixes, one before the next engine unfollows.

- **What it does:** a single HikerAPI follower fetch is partial now (286 to 876 of about 995), so the check takes the union of every list of the last 12 days. In any list = follows back. Not in the union = non-follower, but only when the union's count is within 2% of the profile count. That mark (`followback_verified_at`) is what lets the engine unfollow.
- **What holds:** a positive is always safe. The tracker today: 165 active follows, 53 marked followed back (27 found by these lists), 112 marked verified non-followers, all dated 11-12.
- **The weak spot is exactly the engine's own accounts.** The engine follows people now; about a quarter follow back within days. A follow-back from the last few days can only be in the newest list, and the newest list is partial. The count test cannot see that: older lists and people who left fill the count. So a fresh reciprocator can be marked "verified non-follower" and unfollowed when due. That is the one thing the system must never do.
- **MUST, before the next engine unfollows:** the regular session playbook has no "Follow Back" rule. `docs/cowork-task-ig.md` lines 353-354 only say "verify the button returns to Follow, retry once". The sweep runbook has the right rule (button reads "Follow Back" = re-follow at once, log `ig_unfollow_aborted`, tell Amir). Copy it into the regular unfollow step, or a missed reciprocator gets a second click instead of a re-follow.
- **SHOULD, the real fix:** do not trust absence from a union for a recent follow. Either check each due candidate directly on the day (8 or fewer per session), or count an account as a non-follower only when it is missing from two lists fetched on different days after its follow date.

## 2. Follows per session 16 to 10 during the sweep (f6def47, 🎬 Socials). Verdict: approve, one small fix.

- One number in `ig_engagement_config.py`, with Amir's words ("A", "approve", 11-14) in the comment and the handover.
- **Fix:** the "Dec 5 check, back to 16 if the ratio is 1.2 or more" lives only in that comment and one handover line. Nothing will bring it up on Dec 5. Give it a dated ticket.

## 3. Release-day playbook, Fri Dec 11 (🎵 Release). Verdict: approve with fixes. The structure is right; it is two days old and already out of date in five places.

| Claim | Checked | Result |
|---|---|---|
| Bandcamp does not release a pre-order by itself | Bandcamp help, "Can I set my pre-order to automatically release at a certain time?" | ✅ manual: "release pre-order now", then Update. The old playbook's "auto-flip" was wrong; this one is right |
| Dec 10 / 11 / 12 / 14 are Thu / Fri / Sat / Mon | calendar | ✅ |
| Listening party 19:00 Berlin = 10:00 Pacific | 9 hours apart in December | ✅ |
| Links and values come from the release file | `releases/pinocchio-single.json` today | ✅ ISRCs, UPC, label, the restore list; the Bandcamp link and 8 campaign links are in the file now |
| Every text in his voice waits for his OK in the main EP chat | the file itself | ✅ it holds no captions, only pointers |

**Fixes (the EP chat owns the file):**
1. **Stale since 11-13:** "Bandcamp pre-order published (still a draft today)" is done (live 11-13). "Listening party scheduled" is done (announced, 54 fans notified). `bandcamp_links.py` has run (campaign links are in the release file). The YouTube Official Artist Channel is granted (11-13). "Follower notify timing is open" is settled.
2. **The party time is no longer a free choice.** The party is announced for 19:00, so the clash with the reel's 18:30 to 19:30 reply hour can only be solved by moving the reel (17:30 was the playbook's own example) or by accepting the overlap. Amir decides; the playbook should say that only the reel can move.
3. **Refresh date:** a runsheet goes stale fast. Add one line on top: "re-check every ⚠️ against the release file on Tue Dec 8".
4. The open ⚠️ items that need an owner before Dec 10: which Canvas goes to Spotify, the story set (no owner), Amplify on both tracks or one, SoundCloud downloads on or off, the label line's place on SoundCloud.

## Still in the queue
Items 4 to 18 of the parent lists (Booking drafts, description map, EP plan, ratio plan, content and party plans, the Income plans, the rule memories, small ones). Next in line: the 26 unsent label drafts and the description map.

## Follow-up, same day: the Instagram chat's fixes (Amir decided both there)
- ✅ The "Follow Back" rule is in the regular unfollow step (3d82f38, `docs/cowork-task-ig.md` line 355).
- ✅ Amir picked "check each one live": `scene_intelligence/ig_unfollow_precheck.py` searches his followers for each of today's unfollow candidates (about 12 calls) and the engine only unfollows a name cleared today (`UNFOLLOW_PRECHECK_REQUIRED`). A skipped or failed run means no unfollows. Design approved.
- Two points sent back: an empty or None answer from the search is read as "not a follower" (`users = ... or []`), which must count as an error; and one known follower should be searched as a control each run, so a broken search clears nobody.
