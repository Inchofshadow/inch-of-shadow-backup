# Engagement Automation Log Design - Lessons from Nina

Source: code review of the Nina daily hub automation (2026-06-12), after Nina Protocol announced shutdown.
Apply this checklist BEFORE running the first engagement session on any new platform (Catalog, Audius, or whatever replaces Nina in the web3 strategy).

## What went wrong on Nina

The automation ran 2026-05-16 to 2026-06-11. By the end, the follow log had 145 entries with 9 duplicate artists (AD 93 and Downwards followed 3x each), every entry collapsed into a single ambiguous state, three entries with a boolean where a release title belongs, and unfollows logged as completed that were never verified. None of this was caught while the task was live.

## Design rules for the next platform

### 1. Follow-state is an enum, not a boolean

`followed_back: false` -> `"unfollowed"` (string) destroyed the distinction between "currently following, not yet reciprocated" and "was followed, then unfollowed". Use explicit string states:

- `following` - new follow, awaiting reciprocation
- `reciprocated` - they followed back; never unfollow
- `unfollowed` - confirmed unfollow (button was present, click succeeded, UI flipped to Follow)
- `unfollow_attempted_unverified` - action attempted but platform gave no confirmation; stays eligible for re-check next run

Never mark an action as done that the platform did not confirm. "No button, so I marked it done anyway" launders broken platform state into the log as completed work.

### 2. Dedup before append, by canonical key

The Nina SOP rule "skip artists already in the log UNLESS followed_back is 'unfollowed'" inverted the guard: once everything was unfollowed, every artist was eligible to be re-followed forever. Rules:

- One entry per artist, keyed on canonical profile URL (normalize `/hubs/x` vs `/profiles/x` variants). Update in place; never append a second entry for the same artist.
- Re-follow only after an explicit cooldown (90+ days) AND explicit approval from Amir. Default is: unfollowed = permanently done.

### 3. Fixed schema, typed fields, full stats row

- Define the schema in the SOP exactly as the file should look, including ALL fields. The Nina SOP listed 5 stats fields while the live file used 11; an agent following the SOP strictly would have dropped `run_timestamp` and `notes`, the two fields needed to audit session authenticity.
- `run_timestamp` and `notes` are mandatory on every stats row.
- Each field has one type. Nina ended up with `release_reposted: true` (boolean) where a release title string belonged.
- Catch-up/missed runs: one row, logged under the actual execution date, with a `covers_missed_date` field. Never split one session into two rows sharing a timestamp.

### 4. Verify actions, then log

The single best improvement made during the Nina run was the APPEARS IN check for reposts (added June 10) - it immediately caught reposts that reported success but were silently discarded by the backend. Generalize it:

- Every action (follow, favorite, repost) gets a platform-side verification step before it is logged as done: re-read the profile/release and confirm the state actually changed.
- If verification is impossible, log the action as `*_unverified`, never as completed.

### 5. Auto-stop rules in the SOP

Nina's automation ran 11 days past the point of having anything to do, because the SOP's stop conditions only covered captcha/rate-limit/error/logout. Add:

- "If all core actions fail or are disabled in a single run, STOP and message Amir: the task may need to be suspended. Do not continue to the next scheduled run automatically."
- "If the platform shows any wind-down / sunset / migration banner, STOP and report it the same day."

### 6. UI-selector scripts: exact matches only

The Nina repost JS skipped buttons via `title.includes('post')` - a substring match that also matches "repost", the very button it was looking for. Any embedded JS in a task body must use exact label comparisons (`aria === 'Add to Queue'`), not substring guards.

## Reusable asset from the Nina run

`scene_intelligence/nina_follow_log.json` holds 145 hand-vetted dark-electronic artists/labels (EBM, acid, electro, industrial) engaged between May and June 2026. The Nina URLs die with the platform, but the names are a curated target list: cross-reference against SI contacts and SoundCloud before the next platform launch instead of discovering from zero.
