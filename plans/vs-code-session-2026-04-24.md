# VS Code Session Report -- 2026-04-24
# IG Engagement Engine build + SI data fixes

**Artist:** Inch of Shadow
**Session goal:** Build the IG engagement engine from the Cowork spec and tie every data change back to SI (Scene Intelligence) as the single source of truth.

---

## Source of Truth -- READ THIS FIRST

**SI (Scene Intelligence) = `scene_intelligence/enriched_contacts.json`**

Every contact lives here. Every score, category, location, genre, and IG enrichment field is stored here. Other files (`ig_blocked_accounts.json`, `ig_personal_network.json`, `promotion_log.json`, etc.) reference contacts and hold relationship/state data, but **contact truth lives in SI**.

Rule for future work: any time a contact is mentioned, cross-reference SI before making assumptions. The ofra85 mistake from this session happened because that was skipped -- her SI record explicitly showed "Co-Founder @operator.radio" but the name-pattern Hebrew check fired first.

### Changes this session that landed in SI

| SI change | Why | Scope |
|-----------|-----|-------|
| 2 score upgrades (ofra85, tatajanashia: 1->4) | Both were media accounts misflagged; SI already had correct bio/location data | Contact records |
| 13 contacts marked `ig_blocked: true` + reason + source + date | Previously blocks lived only in `ig_blocked_accounts.json`; now SI is authoritative and every tool that reads SI respects the block | Contact records |
| Engine reads `ig_blocked` flag from SI first, block-list file second | SI becomes the primary skip source; block-list is backup for handles not in SI (e.g. teder.fm) | Engine behaviour |

**Net impact on Track B rejects:** `si_ig_blocked: 3` is now the dominant blocked-skip reason (was `in_blocked_list: 3` before); block-list-only contacts still skipped via `in_blocked_list`.

---

## 1. Phase & Session Schedule (from config)

- **Current phase:** 1 (weeks 1-2, establishing pattern)
- **Days:** Mon / Wed / Fri, 10:00-11:00 Berlin
- **SC conflict check:** IG days never overlap with SC's Tue/Thu/Sat -- validated on startup
- **Per-session hard cap:** 20 minutes

| Phase | Base follows | Base unfollows | Base likes | Effective range (with jitter) |
|-------|--------------|----------------|------------|-------------------------------|
| 1 (weeks 1-2) | 5 | 0 | 20 | 4-6 / 0 / 15-22 |
| 1b (weeks 3-6) | 8 | 5 | 20 | 7-9 / 4-6 / 15-22 |
| 2 (weeks 7-12) | 10 | 8 | 25 | 9-11 / 7-9 / 20-27 |
| 3 (ongoing) | 5 | 10 | 20 | 4-6 / 9-11 / 15-22 |

**`SESSION_JITTER` (new this session):** every session rolls a small offset per key so action counts look human instead of identical.

```python
SESSION_JITTER = {
    "likes_per_session":    (-5, +2),   # asymmetric: wider low tail, tight high tail
    "follows_per_session":  (-1, +1),
    "unfollows_per_session":(-1, +1),
}
```

**Why asymmetric on likes?** Strategy doc states 20 likes/session is the "safe" volume. The upward cap (+2 = 22 max) stays within 10% of that safe line. The downward tail (-5 = 15 min) is wider because low-engagement days match real human behaviour and IG reads inconsistency as a trust signal, not a penalty.

**Verified distribution over 1000 sessions:**
- Range: 15-22 (8 possible values, roughly uniform)
- Mean: 18.5 (below strategy baseline of 20)
- Max: 22 (+2 tolerance over strategy's safe line)
- No cycle, fresh `random.randint` per session.

Minimum clamped at 0 (never negative).

---

## 2. Track B Tier Table & Budget Ratios

| Tier | Categories | IG followers | Score | Budget | Cooldown | Phase-1 slots (base 20) |
|------|-----------|--------------|-------|--------|----------|-------------------------|
| T1 | dj, artist | 200-8,000 | 4-5 | 40% | 25-38 d jittered | 8 |
| T2 | label | 200-8,000 | 4-5 | 35% | 30-45 d | 7 |
| T3 | dj, artist | 200-8,000 | 3 | 15% | 40-52 d | 3 |
| T4 | label | 200-8,000 | 3 | 10% | 50-65 d | 2 |
| **Prominent** (additive) | dj, artist | 8,000-15,000 | 3+ | +1 max / session | 60 d fixed | +1 |

**Budget validation:** 0.40 + 0.35 + 0.15 + 0.10 = 1.00 exactly. Engine fails startup if broken.
**Total Phase-1 likes:** 15-22 regular (base 20 + jitter -5/+2) + up to 1 prominent = **16-23 per session** (mean ~19.5 with prominent enabled, ~18.5 without).

**Promo priority override:** any contact in the active campaign (today: `farewell-single`) gets moved to the front of T1 for Track B, regardless of their natural tier. Resolved via SI name cross-reference (Bug 2 fix this session) -- campaign targets whose URL points to YouTube or website are now matched correctly.

Current active promo handles resolved: **7** (was 4 before fix).

---

## 3. Track A (Follows) Rules

From `cfg.TRACK_A`:

- **Target range:** 200-2,500 followers
- **Sweet spot:** 300-1,500 followers, following/followers ratio 1.5-5.0
- **Rejections:** >5,000 following, following/followers > 8.0, <12 posts, >21d since last post, <0.5% engagement rate, verified accounts, repost-only accounts
- **Like-before-follow sequence:** scroll 4-8s -> like most recent eligible post -> wait 15-25s -> follow
- **7-day unfollow rule:** unfollow any non-follow-back after 7 days; `keep_following=true` or active-promo contacts never unfollowed
- **SI cross-check (Bug 3 fix this session):** Track A dedup now extracts handles from both `ig_username` (261 contacts) AND `url` field (extra 11 contacts). Previously those 11 SI contacts could have been followed twice.

**Queue status (`ig_target_list.json`):** **0 entries** -- Track A does nothing until seeded.

---

## 4. Always-Skip Rules (regardless of tier)

Applied in order by `contact_is_always_skip`:

1. No IG handle (`no_ig_handle`)
2. SI `ig_blocked: true` (new: `si_ig_blocked`)
3. Handle in `ig_blocked_accounts.json` (`in_blocked_list`)
4. Handle in `ig_personal_network.json` (`in_personal_network`)
5. Handle in `engagement_log["hidden"]` (`in_hidden_log`)
6. Category in `ALWAYS_SKIP_CATEGORIES`: venue, media, festival, platform, distributor
7. Score < 2 (`score_below_min`)
8. Private account (`private_account`)
9. No IG follower data (`no_ig_followers_data`)
10. > 15,000 followers absolute ceiling (`above_absolute_ceiling`)
11. Label + > 5,000 followers (`label_above_ceiling`)
12. Blocked country: Israeli location OR Hebrew script in bio

---

## 5. Already-Liked Protection (new safety rule this session)

**Problem:** clicking the heart on an already-liked post UNLIKES it. Before this fix, the engine could silently undo manual likes the artist had made.

**Fix:**
- `PostMetadata.already_liked: bool` field (driver MUST populate)
- `pick_likeable_post()` skips both sponsored AND already-liked posts
- If all recent posts on a profile are sponsored or already-liked, the contact is skipped with reason `all_recent_sponsored_or_already_liked`
- Driver contract docs: *"If unknown/indeterminate, set `already_liked=True` (fail-safe: never engage) rather than False (risk unliking)."*
- `HARD_PROHIBITIONS` extended: `"unlike_existing_like"` -- enforced by driver implementation

Verified via 5 unit-style test cases: normal pick, skip-liked, all-liked-returns-None, all-sponsored-returns-None, mixed.

---

## 6. Data Updates Applied (all reference SI)

### 6a. `ig_blocked_accounts.json`: 12 -> 14

**Removed (3 invalid entries that were silently ignored by the engine):**
- `Inner Zone`, `Malka Tuti`, `SOHO Tel Aviv` -- names not handles

**Added (5, all cross-referenced against SI):**

| Handle | SI category | SI location | Reason | Source |
|--------|-------------|-------------|--------|--------|
| moti_landes | promoter | (empty) | israeli_personal_contact | user_confirmed_2026-04-24 |
| eitan.shinder | dj | Berlin | israeli_personal_contact | user_confirmed_2026-04-24 |
| hadareich | promoter | (empty) | israeli_personal_contact | user_confirmed_2026-04-24 |
| 00000wraith | dj | (empty) | user_blocked | user_confirmed_2026-04-24 |
| anima_berlin | promoter | Berlin | user_blocked | user_confirmed_2026-04-24 |

### 6b. SI contact updates (13 contacts now carry block flags)

Every SI contact whose IG handle appears in the blocked-accounts file now has these four fields written directly on the SI record:

```json
{
  "ig_blocked": true,
  "ig_blocked_reason": "israeli_location | israeli_personal_contact | user_blocked",
  "ig_blocked_source": "si_auto_detected | user_confirmed_2026-04-24",
  "ig_blocked_at": "2026-04-24"
}
```

13 contacts matched (14 blocked handles, 1 `teder.fm` has no SI contact). Contacts now flagged in SI:

`i.am.avigal`, `00000wraith`, `maor_anava`, `moran_musicc`, `anima_berlin`, `du.duality`, `eitan.shinder`, `hadareich`, `moti_landes`, `ason_teva`, `garzen_records`, `redaxesofficial`, `Stereo Society`

Any other tool reading SI (Promotion Engine, outreach flows, Sheets push) will see the block and can choose to respect it.

### 6c. SI score updates

| SI contact | Old score | New score | Reason | SI category (unchanged) |
|------------|-----------|-----------|--------|-------------------------|
| ofra85 | 1 | 4 | Co-founder Operator Radio (Rotterdam); misflagged by name pattern | media |
| tatajanashia | 1 | 4 | Runs Mutant Radio Tbilisi + Berlin festival | media |

Note: both are `category: media` which is in `ALWAYS_SKIP_CATEGORIES` for Track B engagement. Score upgrade matters for Promotion Engine and outreach flows, not for IG likes.

---

## 7. Engine Architecture -- `scene_intelligence/ig_engagement.py`

~1100 lines. All config-driven, nothing hardcoded.

### Components

- **Config loader + validator:** budget sum = 1.0, phase exists, no SC-day overlap, per-tier cooldown min <= max. Fails fast on startup.
- **State loaders:** SI contacts, engagement log, follow tracker, target list, blocked accounts, personal network, release context, promotion log -- all via config-resolved paths.
- **Classifiers:** Hebrew-script detection (Unicode 0590-05FF), Israeli location list, sponsored-post heuristic.
- **Track B pool builder:** tier matching + cooldown check + promo priority override.
- **Track A pool builder:** all Track A criteria checked upstream; browser-level checks (profile photo, post recency, engagement rate, sponsored content) deferred to the driver at action time.
- **Prominent pool builder (Bug 1 fix):** separate 8k-15k pool with fixed 60-day cooldown, 1/session cap, random-position insertion into like queue.
- **Unfollow planner:** 7-day rule, respects `keep_following`, skips active promo contacts.
- **`BrowserDriver` abstract interface:** navigate / scroll / like_post / follow / unfollow / check_for_circuit_breaker / get_profile_state / close. All implementations MUST populate `PostMetadata.already_liked` and refuse to like already-liked posts.
- **`StubBrowserDriver`** (shipped): plans actions to an in-memory list, launches no browser, writes no state.
- **Live driver slot:** `build_driver(live=True)` raises `DriverNotConfigured` with a clear error. Cowork must wire computer-use MCP or approved alternative before any live session.
- **Session orchestrator:** preflight (day + hour window) -> build plan -> interleave unfollows/likes (~33% unfollow-first when available) -> Track A follows at end -> save state ONLY if `driver.LIVE`.
- **Atomic file writes:** temp-file + rename to prevent corruption on crash.

### Safety layers

- 14 circuit breaker signals (config list). Driver calls `check_for_circuit_breaker()` before each action returns.
- 14 hard prohibitions in `HARD_PROHIBITIONS`: no password, no DM, no Settings, no sponsored engagement, no link clicks (address-bar navigation only), no unliking existing likes.
- Session time cap (20 min) enforced in execution loop.
- State gate: `driver.LIVE` must be true for any state file to be written.
- SI `ig_blocked` field is checked before block-list (belt + suspenders).

---

## 8. Current Session Plan Snapshot

Live output from `python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight`:

```
Phase:              Phase 1 -- establishing pattern (weeks 1-2: follows only)
Likes per session:  15-22 (asymmetric jitter -5/+2 from base 20)
Follows per session: 4-6 (jittered from base 5)
Unfollows per sess: 0 (base 0 + clamp)

-- Track B: ~20 likes, tier budgets T1=8 / T2=7 / T3=3 / T4=2 --
  Promo priority (7 labels, farewell-single):
    melopeerecords, iptamenosdiscos, crave.tapes, 030303records,
    roamrecordings, lunardiskorecords, nervecollect
  Regular mix: T1 DJs + T2 labels + T3 DJs + T4 labels

-- Prominent tier (8k-15k, 1/session, 60d cooldown): andreikozyreff (9.2k)

-- Track A: 0 (queue empty)
-- Unfollows: 0 (Phase 1)

Track B rejects (top reasons):
    no_ig_handle: 711
    no_tier_match: 38
    category_always_skip:venue: 33
    score_below_min:1: 31
    category_always_skip:media: 20
    in_personal_network: 20
    in_hidden_log: 5
    private_account: 4
    si_ig_blocked: 3
    above_absolute_ceiling: 1
```

---

## 9. Pending for Cowork

### T1 remaining

- Review `ig_personal_network.json` (25 entries). Anyone to add/remove.
- Additional blocked accounts beyond the 14 already in the file.

### T3 decisions (already sent in chat; summary here)

- **Score 1 list (58 contacts):** individual decisions needed. Many are personal-category contacts that should migrate to `ig_personal_network.json`; others may deserve score upgrades (see full list in chat).
- **62 dropped contacts:** decisions on re-adds vs. permanent blocks. Notable scene-relevant misses: clonerecords, dfarecs, arbutusrecords, berghain_panoramabar, resident_advisor, postpunkonline, redlightradio, prachtwerkberlin.

### T4 critical path to first live session

1. **Seed `ig_target_list.json`** -- Track A produces 0 follows until this queue has entries. 20-50 peer accounts needed from hashtag / competitor / event sources per strategy doc.
2. **Pick and wire a browser driver.** Engine refuses `--live` until a `BrowserDriver` subclass with `LIVE = True` is registered. Candidates per strategy doc: computer-use MCP (lowest detection risk), approved alternative.
3. **Driver must populate `PostMetadata.already_liked`** for every recent post it returns. Failing-safe (True when unknown) is acceptable; False when unverified is not.
4. **Cowork reviews first live session plan** before greenlight. Safe entry point: dry-run -> review -> wire driver -> review -> live.

### Data hygiene follow-ups

- `teder.fm` in block list has no SI contact. Either add to SI (it's a dropped-contact re-add candidate anyway) or remove from block list for consistency.
- Score 3 contacts `ason_teva` classification: currently personal in SI but Israeli per user; blocked, so no engagement risk, but the SI category/score could be aligned.

---

## 10. How to Run / Verify

```bash
# Safe planning (default) -- prints the exact session plan, no browser
python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight

# Phase override to preview 1b / 2 / 3 behaviour
python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight --phase 1b

# Run 4 times to see jitter in action
for i in 1 2 3 4; do
    python3 scene_intelligence/ig_engagement.py --plan-only --no-preflight \
        | grep -E "^Likes|^Follows|^Unfollows"; echo ---
done

# Live attempt -- refuses with clear error until driver is wired
python3 scene_intelligence/ig_engagement.py --live
```

---

## 11. Files Touched This Session

| File | Change | Why |
|------|--------|-----|
| `scene_intelligence/ig_engagement.py` | **Created** (~1100 lines) | The engine itself |
| `scene_intelligence/ig_engagement_config.py` | Added `SESSION_JITTER`; `unlike_existing_like` in `HARD_PROHIBITIONS` | Anti-pattern + safety |
| `scene_intelligence/ig_blocked_accounts.json` | +5 new blocks, -3 invalid entries, `last_updated: 2026-04-24` | User-confirmed Israeli + personal blocks |
| `scene_intelligence/enriched_contacts.json` | 13 contacts flagged `ig_blocked`; ofra85/tatajanashia score 1->4 | SI as source of truth for blocks + score fixes |
| `scene_intelligence/ig_enriched_contacts.json` | Written earlier (enrichment pass) | 261 IG profiles fetched |
| `scene_intelligence/ig_follow_tracker.json` | Schema restored (last_session reverted to null) | Not touched by stub |
| `scene_intelligence/ig_target_list.json` | Schema unchanged, queue still empty | Awaiting Cowork seeding |

Nothing committed to git yet -- next commit decision is Cowork's.
