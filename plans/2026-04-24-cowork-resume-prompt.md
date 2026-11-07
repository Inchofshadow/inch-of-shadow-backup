# Resume prompt for Cowork -- paste this when you come back

Hey. I was paused mid-conversation and went to VS Code to build the IG engagement engine. That work is done. Here is everything you need to know before we continue on your side.

Session date: 2026-04-24. Project state as of now:

---

## 1. Read these three files first, in this exact order

1. **`plans/vs-code-session-2026-04-24.md`** -- complete report of what the VS Code session did. Covers: tier allocation, jitter math, every data change, engine architecture, pending items. Start here, it is the fastest path to picking up context.

2. **`plans/ig-engagement-strategy.md`** -- the living strategy doc. **Updated this session.** Track B tier table was rewritten to match the engine's actual behaviour (your earlier 60/20/10/10 spec was superseded based on enrichment data -- see "Changes from v1" section for rationale). Also now includes: SESSION_JITTER, already-liked post protection, `ig_blocked` SI field, prominent tier.

3. **`plans/2026-04-23-vs-code-handoff.md`** -- the original handoff spec you gave me, renamed with date prefix. Path references fixed (was `~/Documents/Claude/...`, actual path is `~/Desktop/Inch of Shadow/Inchofshadowcode/`). Tier table annotated with the 2026-04-24 update.

---

## 2. The engine itself

**File:** `scene_intelligence/ig_engagement.py` -- ~1100 lines, created this session.

**Design decisions you should know:**

- Config-driven. Nothing hardcoded. Reads from `scene_intelligence/ig_engagement_config.py`.
- Engine ships with a `StubBrowserDriver` that plans and logs actions without launching a browser or writing any state. Dry-run safe.
- Live execution is gated. `python3 scene_intelligence/ig_engagement.py --live` raises `DriverNotConfigured` with a clear error until **you** wire in an approved driver (computer-use MCP per the strategy doc, or an alternative you approve). I did not wire a live driver -- that is your call.
- State files (`engagement_log.json`, `ig_follow_tracker.json`, `promotion_log.json`, etc.) are only written when `driver.LIVE == True`. Dry-runs write zero state. Verified.
- Session flow: preflight day/hour check -> build plan -> interleave unfollows with likes (~33% unfollow-first when both available) -> Track A follows at end with like-before-follow sequence -> save state (if live).

**How to review the plan without running anything live:**
```
python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight
```

---

## 3. Config changes you need to be aware of

`scene_intelligence/ig_engagement_config.py` -- new values I added this session:

- **`SESSION_JITTER`** -- per-session offset applied to phase limits so counts look human.
  - Likes: `(-5, +2)` asymmetric. Range 15-22, mean ~18.5. Asymmetric because strategy's "20 likes/session is safe" line should be the cap; the wider downward tail is deliberate (low-engagement days match real humans, IG reads inconsistency as trust).
  - Follows: `(-1, +1)`.
  - Unfollows: `(-1, +1)`, clamped at 0 minimum.
  - Amir and I discussed widening to symmetric ±5 but rejected it -- strategy doc caps safe volume at 20 likes/session and symmetric ±5 exceeds that 25% of the time. Asymmetric -5/+2 keeps cap but adds variance.

- **`HARD_PROHIBITIONS`** -- added `"unlike_existing_like"`. Clicking the heart on an already-liked post UNLIKES it, which would silently undo Amir's manual likes. Engine now skips already-liked posts via `pick_likeable_post()`. Driver contract specifies: `PostMetadata.already_liked` MUST be populated; if unknown, set True (fail-safe).

---

## 4. Engine bugs I found and fixed

All three were in my first pass. Amir caught them during audit; fixed before final.

- **Bug 1 -- PROMINENT_TIER was dropped.** Config had the 8k-15k prominent tier enabled (1/session, 60d cooldown) but the engine never referenced it. Now implemented: separate pool builder, additive to tier budget, randomly inserted into the like queue.

- **Bug 2 -- Promo campaign handles unresolvable.** Engine was resolving promo targets only via `target.ig_username` (never set) or `target.url` containing instagram.com (20/57 hits for farewell-single). The other 37 targets had YouTube/website URLs. Added SI name cross-reference as a 3rd fallback (`_build_name_to_handle`). Jumped from 4 resolved promo handles to 7 on farewell-single.

- **Bug 3 -- Track A dedup incomplete.** The SI handle set was built only from contacts with `ig_username` populated (261). Another 11 SI contacts carry IG in the `url` field with no `ig_username`; they were invisible to the Track A dedup. Now also extracts from `url` field. Prevents following SI contacts twice.

---

## 5. Data changes in SI (`enriched_contacts.json` is SI, authoritative)

**Rule I adopted this session and saved to memory:** SI is the single source of truth. Every contact change reflects in SI. Other tool-specific files (blocked list, personal network) are convenience overlays.

- **`ofra85` score 1 -> 4.** Co-founder @operator.radio (Rotterdam). Originally misflagged by me as Israeli based on name pattern; Amir corrected. I should have cross-referenced SI first -- her SI record explicitly showed the Operator Radio bio.
- **`tatajanashia` score 1 -> 4.** Runs Mutant Radio Tbilisi + Berlin festival. Same misflag pattern.
- Both are `category: media`, so still always-skip in Track B regardless of score. The score upgrade matters for Promotion Engine and outreach tools, not IG likes.

- **13 SI contacts now carry `ig_blocked: true`** + `ig_blocked_reason` + `ig_blocked_source` + `ig_blocked_at` fields. Engine reads this SI flag first, block-list file second. Means any tool reading SI will know these contacts are IG-blocked without having to also parse the block list.

Contacts flagged in SI: `i.am.avigal`, `00000wraith`, `maor_anava`, `moran_musicc`, `anima_berlin`, `du.duality`, `eitan.shinder`, `hadareich`, `moti_landes`, `ason_teva`, `garzen_records`, `redaxesofficial`, `Stereo Society`.

One block handle (`teder.fm`) has no SI contact -- needs either SI add or removal from block list for full consistency.

---

## 6. Block list changes (`ig_blocked_accounts.json`)

Count: 12 -> 14.

**Removed (3 invalid entries that the engine was silently ignoring):**
- `Inner Zone`, `Malka Tuti`, `SOHO Tel Aviv` -- all had spaces/caps, not valid IG handles.

**Added (5, all user-confirmed 2026-04-24, all have reason + source fields):**
- `moti_landes`, `eitan.shinder`, `hadareich` -- israeli_personal_contact (Amir knows them personally)
- `00000wraith`, `anima_berlin` -- user_blocked (Amir asked not to interact)

---

## 7. What is pending on your side

**T1 still open:**
- Review `ig_personal_network.json` (25 entries). Anyone to add/remove? Amir said he'd do this on your side.
- Any more blocked accounts you want added.

**T3 decisions (I prepared the lists in chat earlier; Amir may paste them to you):**
- 58 score-1 contacts -- individual decisions on reclassify/block/delete. Key candidates for score upgrade (scene-relevant but currently score 1): `giulyeaaah`, `patyvapor`, `freudenthal_of_pardonmoi`, `zaatar___`, `ana_molina_89`.
- 62 dropped contacts from `raw_contacts.json` that didn't make it into SI. Notable re-add candidates: `clonerecords`, `dfarecs`, `arbutusrecords`, `berghain_panoramabar`, `resident_advisor`, `redlightradio`, `postpunkonline`, `prachtwerkberlin`, `microverse__berlin`, `feinstoffberlin`, `sofarsoundsberlin`, `in.between.berlin`, `salo.community`.

**T4 critical path to first live session:**
1. Seed `ig_target_list.json` -- currently empty, so Track A produces 0 follows. Needs 20-50 peer accounts from hashtag / competitor follower / event sources per strategy doc section.
2. Pick and wire a `BrowserDriver` subclass with `LIVE = True`. The driver MUST populate `PostMetadata.already_liked` for every recent post.
3. Review the first live session plan with Amir before greenlight.

---

## 8. Feedback rules Amir set with me this session (saved to my memory, worth knowing)

- **Never guess.** If I state a number or a claim, either cite a source (strategy doc, config, SI data, research, measurement) or say explicitly "I don't know." I broke this twice this session -- once on ofra85 (pattern-matched her name as Israeli without checking SI), once on IG rate limits (cited "60/hour threshold" as if it were real when I actually had no source). Amir pushed back both times.
- **Flag IG risk before acting.** Always explain detection risk in plain language before running any IG-related script. Proactively warn when approaching grey zone.
- **SI is source of truth.** Cross-reference SI before making any contact claim.

---

## 9. Files I created or modified this session (for your situational awareness)

| File | Status | Notes |
|------|--------|-------|
| `scene_intelligence/ig_engagement.py` | NEW | The engine |
| `scene_intelligence/ig_engagement_config.py` | MODIFIED | SESSION_JITTER, unlike_existing_like prohibition |
| `scene_intelligence/ig_blocked_accounts.json` | MODIFIED | +5 adds, -3 invalid, 14 valid handles total |
| `scene_intelligence/enriched_contacts.json` | MODIFIED | ofra85/tatajanashia scores, 13 ig_blocked flags |
| `scene_intelligence/ig_enriched_contacts.json` | NEW | Output of the 268-contact enrichment pass (261 fetched, 10 private, 7 not found, 0 errors) |
| `scene_intelligence/ig_follow_tracker.json` | NEW schema only | Empty, ready for live driver |
| `scene_intelligence/ig_target_list.json` | NEW schema only | Empty, needs seeding |
| `scene_intelligence/ig_personal_network.json` | UNCHANGED | 25 entries, awaiting your review |
| `plans/ig-engagement-strategy.md` | MODIFIED | Tier table rewritten, new features documented |
| `plans/2026-04-23-vs-code-handoff.md` | RENAMED + MODIFIED | Was `vs-code-handoff-prompt.md`; paths fixed; tier table annotated |
| `plans/vs-code-session-2026-04-24.md` | NEW | Full session report |

Nothing committed to git. Commits are your call.

---

That is everything. Start with the three priority reads in section 1 and you will have the full picture. Ping if anything is unclear.
