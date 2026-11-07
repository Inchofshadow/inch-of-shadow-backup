# Instagram Engagement Strategy — Inch of Shadow

**Last updated:** 2026-04-23
**Status:** Pre-build — export received, cleanup complete, engine not yet built
**Goal:** Grow @inch_of_shadow from 790 → 1,200+ followers in 6 months through strategic automation + organic improvements. Quality over quantity — scene-relevant followers only.

---

## Project Scope — Long-Term IG Assistant

This is not a one-off automation build. Claude operates as a permanent IG assistant for Inch of Shadow, with full awareness of:
- This strategy doc and all updates to it
- The SI enriched contacts (972 scene contacts as of April 2026)
- IG engagement log and follow tracker (live state)
- Release Manager stats (release dates, content calendar)
- Artist visual language and brand identity (to be documented)

Every session builds on the last. All decisions logged here.

---

## Account Status (as of April 2026)

| Metric | Current | Target (6 months) |
|--------|---------|-------------------|
| Followers | 790 | 1,200–1,500 |
| Following | 841 (down from 895 — 54 unfollowed April 22) | ≤ 600 |
| Ratio | 0.94:1 (negative) | 2:1+ (followers/following) |
| Posts | 82 | 100+ |
| Account type | Creator | Creator ✓ |
| Highlights | 0 | 4+ |

**Ratio goal:** Reach 2:1 followers/following by month 6. Not 1.5:1 — that's the midpoint milestone. The end state is ~1,200–1,500 followers against ~500–600 following.

**Note on 168 deferred accounts:** Accounts from 2018–2020 (pre-2021) were NOT reviewed in the April 22 cleanup — deferred to next quarterly export (due July 23, 2026). A scheduled reminder is active.

---

## Part 1 — Instagram Algorithm 2026 (Research-Based)

### How the algorithm works

Instagram uses separate AI ranking systems for each surface — there is no single algorithm.

| Surface | Primary signal | Secondary signal |
|---------|---------------|-----------------|
| Feed | Relationship strength | Save rate |
| Reels | Watch time + replays | Sends via DM |
| Explore | Engagement velocity | Topic match |
| Stories | Recency | Viewing history |

### The 3 signals that matter most (confirmed by Mosseri, April 2026)

1. **Sends per reach** — DM shares are the strongest signal. If someone sends your post to a friend, Instagram reads this as high-value content and pushes it harder.
2. **Watch time** — For Reels, watch time and replays are primary. If people rewatch, the algorithm boosts distribution aggressively.
3. **Saves** — Save rate outweighs likes significantly. A saved post signals "I want to come back to this" — much stronger than a passive like.

**Likes are the weakest signal in 2026.** Don't optimise for them.

### "Your Algorithm" feature (launched Dec 2025, global April 2026)

Instagram now gives every user a personal dashboard showing the topics it associates with their interests (Settings → Content Preferences). Users can add or remove topic categories.

**Action required:** Go to Settings → Content Preferences on @inch_of_shadow and manually set topic categories to: dark disco, EBM, electronic music, acid, techno, Berlin underground. This directly affects who Instagram routes your content to. If it's not set, Instagram guesses — and it guesses wrong for niche genres.

**Why niche matters:** Tags like "musician" or "DJ" are so broad Instagram cannot map them to a specific audience. "Dark disco producer from Berlin" is a matchable topic. "Musician" is not. Being specific is now a discovery requirement, not a preference.

### Content prioritisation rules (2026)

- Original content is boosted over reposts/aggregation
- Accounts posting 10+ reposts in 30 days are excluded from recommendations entirely
- Smaller creators get a discovery boost over large accounts on Explore
- Consistent posting cadence signals an active, legitimate account
- **Reels are the key multiplier** — one strong live set clip or studio reel can add 50–100 followers organically in a week. The automation builds the floor, content builds the ceiling.

### Also check

- **IG profile category** — currently shows "Musician/band" under the name. This is too generic. Check Settings → Edit Profile → Category for a more specific option.

---

## Part 2 — Hashtag Strategy 2026

Hashtags no longer drive reach on their own. They now function as topic labels — they help Instagram's AI categorise content and match it to interested users.

Instagram has officially limited posts to **maximum 5 hashtags**. Using more may reduce reach. Use exactly 3–5 per post. All must be niche-specific — no generic tags.

**Never use:** `#music #dj #techno` (too broad, zero targeting value)

### Ready-to-use sets for Inch of Shadow

| Set | Context | Tags |
|-----|---------|------|
| Set A | Releases / tracks | `#darkdisco #ebm #acidtechno #berlinunderground #electronicmusic` |
| Set B | Live / gigs | `#djset #berlinelectro #darkdisco #liveset #undergroundelectronic` |
| Set C | Production / studio | `#musicproducer #ebm #acidsynth #berlinmusic #darkelectro` |

Rotate between sets — don't use identical hashtags on every post. Stories: max 1–3.

---

## Part 3 — Bot Detection and Risk Model 2026

### How Instagram detects automation

**Layer 1 — Behavioural patterns**
- Action velocity (too many actions too fast)
- Uniform timing between actions (real humans are irregular — use non-uniform distributions)
- Follow churn pattern (follow → wait → unfollow at scale)
- Session duration vs. actions ratio

**Layer 2 — Device/session fingerprinting**
- User agent string, device ID, IP address consistency, cookie session integrity

**Layer 3 — Account health signals**
- Engagement rate vs. follower count ratio
- Follower quality (bot followers hurt your own detection score)
- Ratio of following to followers
- Account age and activity history
- **Genre relevance of interactions:** engaging with off-topic accounts dilutes your content topic signal. Every interaction must be with scene-relevant accounts.

**Layer 4 — Content signals**
- Accounts with bot signals (random username, no photo, 0 posts) that interact with you damage your account health score
- **Hard rule: never engage with any account showing bot signals regardless of discovery source**
- **Hard rule: never engage with sponsored posts, promoted content, or ads** — if the engine sees "Sponsored" on a post, skip immediately

### Why real Chrome browser is the safest approach

Using actual Chrome with real cookies means: real device fingerprint (macOS, genuine Chrome), real IP (same as normal browsing), real session (cookies Instagram already trusts), no headless browser detection signals.

| Method | Detection risk |
|--------|---------------|
| Headless Playwright / Puppeteer | Very high |
| API with fake tokens | High |
| Requests with Chrome cookies | Medium |
| Real Chrome (computer-use) | Lowest |

### Action block escalation ladder

| Level | Trigger | Action |
|-------|---------|--------|
| 1 | First violation | 24–72h action block on specific actions. Account still works. |
| 2 | Repeated violations | 7-day block |
| 3 | Rare at low volumes | Temporary suspension |
| 4 | Mass spammers (100s/day) | Permanent ban |

At Phase 1 volumes (5–8 follows/day, 20 likes/day), worst realistic outcome is a 24h action block.

### Timing rules (specific)

- Between two likes: 12–20 seconds
- Between like and follow: 18–30 seconds (bigger action = longer pause)
- Between two follows: 25–45 seconds
- After opening a profile: **scroll for 4–8 seconds before any action** — shorter before just assessing, longer before liking or following
- After scrolling, pause 2–4 seconds before acting
- Every 4–6 actions: one longer random pause of 30–60 seconds (simulates distraction)
- Timing uses a non-uniform weighted distribution peaking around 15–18 seconds — never a flat random

### Like-before-follow sequence (standard)

Every follow must be preceded by a like. The sequence is:
1. Open target profile
2. Scroll 4–8 seconds (simulate reading)
3. Like one recent post
4. Wait 15–25 seconds
5. Follow

This makes the interaction look completely organic — discovered their content, liked it, then followed. Two touchpoints: like notification + follow notification.

### Follow churn warning

Instagram specifically monitors follow/unfollow patterns. Mitigation:
- Keep unfollow volume at or below follow volume
- Space unfollows throughout the session — never batch all unfollows at the start
- Mix unfollows with likes across the session
- Never unfollow same day as following
- Always wait the full 7 days

---

## Part 4 — Engagement Strategy

### The two-track model

| Track | Goal | Source | Method |
|-------|------|---------|--------|
| A — Follow/unfollow | Raw follower count growth | Outside SI — hashtag/competitor discovery | Browser automation |
| B — Likes only | Algorithm signal + scene relationships | SI contacts (filtered) | Browser automation |

**Reach rationale:** SI contacts are mostly labels, venues, and DJs with 2K–50K+ followers. They almost never follow back a small account. For pure number growth we need peer-level accounts (under 2,500 followers) who are genre-relevant — found via hashtag exploration and competitor follower lists, not SI.

**Scene rationale:** SI contacts are verified scene-relevant. Liking their posts builds algorithmic presence (your name appears in their notifications) and signals genuine engagement to Instagram. Every Scene contact must be cross-checked to confirm they're not in `ig_personal_network.json` or `ig_blocked_accounts.json`.

**Important:** Before any account enters the Reach queue, it must be cross-checked against `enriched_contacts.json`. If they're already in SI, they belong in Scene, not Reach.

### The three-phase growth model

**Phase 1 — Weeks 1–2 (establishing clean pattern)**

| Action | Per session | Notes |
|--------|-------------|-------|
| Follows | 5 | No unfollows yet — 7-day window not elapsed |
| Unfollows | 0 | Nothing eligible yet |
| Likes (Scene) | 20 | Normal session |

**Phase 1 — Weeks 3–6 (active growth)**

| Action | Per session |
|--------|-------------|
| Follows | 8 |
| Unfollows | up to 5 (7-day non-returners only) |
| Likes (Scene) | 20 |

**Phase 2 — Weeks 7–12 (scaling if Phase 1 clean)**

| Action | Per session |
|--------|-------------|
| Follows | 10 |
| Unfollows | up to 8 |
| Likes (Scene) | 20–30 |

**Phase 3 — Continuous cleanup (not quarterly)**
Unfollow non-returners at up to 10/session whenever available. No big batch events — ratio improves gradually every week. Monthly review session (manual, with me) to assess progress and decide if a small boost is needed.

**All phases run:** Mon / Wed / Fri, 10:00–11:00 AM Berlin time
**SC runs:** Tue / Thu / Sat, ~11:00 AM Berlin time — no overlap

### Target criteria — Reach (strict, all must pass)

**Must have:**
- Genre-relevant bio OR posts (dark disco / EBM / acid / electro / techno / Berlin underground / darkwave / industrial / cold wave / italo)
- Exception: accounts discovered via competitor/event follower lists — presence on the list is sufficient genre signal, bio check optional
- Posted within last **21 days** (not 30)
- Public account (private accounts: skip — cannot verify genre relevance)
- Profile photo present
- Bio text present (minimum 5 characters)
- Minimum **12 posts** (not 5)
- Minimum **200 followers**
- Maximum **2,500 followers** (peer tier)
- Not already following @inch_of_shadow
- Not already followed by @inch_of_shadow
- Not previously unfollowed (no retry, ever)
- Not in `ig_blocked_accounts.json`
- Not in `ig_personal_network.json`
- Not in `enriched_contacts.json` (those go to Scene)
- Following/followers ratio below **8:1** (above = mass-follow bot pattern)

**Must not have:**
- Purely commercial/brand account
- Random-string username (bot pattern)
- Zero or near-zero likes on posts (engagement rate under 0.5% → dead or bought)
- All posts are reshares/reposts (aggregator, not a person)
- Blue verification badge (brand or celebrity — skip for Reach)
- Outside scene genres (psytrance, pop, hip hop, etc.)
- Following count above 5,000
- Israeli location or Hebrew text in bio (see blocked countries below)
- Any sponsored/ad content in their feed (signals commercial account)

**Follow-back likelihood scoring (high-value targets):**
Sweet spot: 300–1,500 followers, following count 1.5–5× their followers. These accounts follow back at 35–50%. Outside this band follow-back rates drop to 15–20%.

### Target discovery sources — Reach

| Priority | Source | How |
|----------|--------|-----|
| 1 | Hashtag exploration | Accounts posting under `#darkdisco #ebm #acidtechno #berlinunderground #coldwave #darkitalo` |
| 2 | Competitor follower lists | Followers of @mannequinrecords @darkentriesrecords @berghain_panoramabar @clone.nl @lies_records |
| 3 | Event follower lists | Followers of Berlin events Inch of Shadow plays alongside (DADA Collective, Cosmic Delay, In Between etc.) |
| 4 | RA event pages | People RSVPing to Berlin dark disco / EBM events on Resident Advisor |
| 5 | Berlin venue tagged posts | People tagging themselves at About Blank, Tresor, Suicide Circus in scene-relevant posts |
| 6 | Comment sections | People commenting on scene label release posts (Mannequin Records etc.) |
| 7 | Bandcamp fans | Fans of similar releases who link their IG in their Bandcamp profile |

**Social distance filter (event follower sources):**
When discovering from DADA Collective or other personal collective accounts, skip any account that:
- Is already in `ig_personal_network.json`
- Is already followed by @inch_of_shadow AND is also following @doublefigure_band (too close to personal circle)
- Is already in SI (route to Scene instead)

### Scene — Engagement rules

**Who to engage (live version -- matches `ig_engagement_config.py`):**

| Tier | Category | IG followers | Score | Engage? | Cooldown (jittered) | Budget % |
|------|----------|--------------|-------|---------|---------------------|----------|
| 1 | dj / artist | 200–8,000 | 4–5 | Yes | 25–38 days | 40% |
| 2 | label | 200–8,000 | 4–5 | Yes | 30–45 days | 35% |
| 3 | dj / artist | 200–8,000 | 3 | Yes | 40–52 days | 15% |
| 4 | label | 200–8,000 | 3 | Yes | 50–65 days | 10% |

**Changes from v1 of this strategy (2026-04-24):**
- **T2 label ceiling raised 2K -> 8K.** Enrichment revealed all 16 score 4–5 labels in SI sit in 2K–8K range; the old 2K ceiling would have excluded every one of them. Labels are still capped at 5K via `ALWAYS_SKIP_RULES["skip_labels_above_followers"]` in the always-skip layer, so T2 effectively engages labels up to 5K. Change came from real data, not a loosening of standards.
- **Budgets rebalanced 60/20/10/10 -> 40/35/15/10.** Pool sizes after enrichment: T1 has 8 eligible contacts, T2 has 16, T3 has 35, T4 has 2. Old 60% T1 budget couldn't be filled with only 8 available contacts; new split matches actual pool proportions.
- **Swapped T3 and T4 categories.** T3 now dj/artist at score 3 (discovery tier), T4 now label at score 3. Reflects the actual order of priority: score-3 peers before score-3 labels.
- **Cooldowns shifted.** T1 25–38d (was 28–35d), T2 30–45d (was 30–38d), T3 40–52d (was 45–55d), T4 50–65d (was 42–50d). Longer cooldowns on T4 reflect lower priority.

**Always skip (Scene):**
- Venues — wrong content topic signal
- Media / blogs (RA, FACT, Mixmag etc.) — invisible in their notifications
- Festival accounts — corporate
- Platform/distributor accounts (Beatport official etc.) — no human reads it
- Labels with > 5,000 IG followers — your like is buried (enforced in always-skip layer)
- Score 1 contacts — almost no genre relevance, damages topic signal
- Any contact with SI field `ig_blocked: true` (SI is source of truth, checked before the block list file)
- Any contact in `ig_blocked_accounts.json` (backup skip list for handles not in SI)
- Any contact in `ig_personal_network.json`
- Any contact in `engagement_log["hidden"]`
- Israeli accounts (location field OR Hebrew script in bio)
- Any sponsored / promoted content
- Any post already liked by @inch_of_shadow (see "Never unlike manual likes" below)

**Priority override:** Any contact in an active promo campaign (per `promotion_log.json`) gets Tier 1 priority for Scene for the duration of that campaign window, regardless of their normal tier. Target handles are resolved by cross-referencing campaign `target.name` against SI to get `ig_username` (campaign targets often carry only email/YouTube URLs). Scene primes contacts before outreach — engage with their post, then pitch them within 2 weeks for maximum warmth. Log `ig_pre_warm: true` and `ig_pre_warm_date` in the promotion log.

**Per-account cooldown:** Applied per-tier (see table above). Each check rolls a fresh jittered threshold within the tier's [min, max] window. Never exactly 30 days — varies every session.

**Large accounts (prominent tier, 8,000–15,000 followers):** Like only, max 1 post per session, fixed 60-day cooldown. Not included in standard tier budget — additive. Scoped to dj/artist only (labels excluded by 5K always-skip rule). Implemented in engine as a separate pool and randomly inserted into the like queue to avoid clustering.

**Per-session count jitter (`SESSION_JITTER` in config):** every session rolls a small offset applied to the phase's base counts, so action counts look human instead of identical.
- Likes: asymmetric `(-5, +2)` — range 15–22, mean ~18.5. Asymmetric because the strategy's "20 likes/session is safe" line should be the cap; wider downward tail matches real human inconsistency, which IG reads as a trust signal.
- Follows: `(-1, +1)` — e.g. Phase 1 = 4–6.
- Unfollows: `(-1, +1)` — clamped at 0 minimum.

**Never unlike manual likes:** the engine must never click the heart on a post already liked by @inch_of_shadow (clicking it again would unlike it). Browser drivers MUST populate `PostMetadata.already_liked` for every recent post returned from `get_profile_state()`. If the driver cannot verify, it MUST set `already_liked=True` (fail-safe). The engine's `pick_likeable_post()` filters out both sponsored and already-liked posts; if all recent posts are unavailable, the contact is skipped with reason `all_recent_sponsored_or_already_liked`. `"unlike_existing_like"` is listed in `HARD_PROHIBITIONS`.

### No story views

Story views are personal and visible to the account owner. Story viewing is **manual only** — never automated. The engine does not touch stories under any circumstances.

### Comment queue (manual, no automation)

The engine flags posts that are worth a genuine comment and appends them to a simple text log. You review and write the comment yourself. No automated comments ever — they look robotic and get flagged. Keep the log simple: one line per flagged post, that's it.

### Over-engagement prevention

- Per-account cooldown tracked in `engagement_log.json`
- Engine checks last engagement date before every action
- If last engagement was under cooldown threshold → skip, move to next contact

### Blocked countries — hard rule

Skip any account with Israeli location or Hebrew text in bio. Both layers checked:
- Location field: Israel / Tel Aviv / Jerusalem / Haifa / IL
- Bio text: Hebrew character detection

Applies to both Reach and Scene. No exceptions, including musicians.

### Blocked accounts files

**`ig_blocked_accounts.json`** — permanent hard skip list. Manually maintained. Engine reads at session start, never writes. Used for: Israeli accounts discovered during sessions, anyone you want permanently blocked regardless of how they appear in other systems.

**`ig_personal_network.json`** — personal contacts. Engine never produces any action toward these accounts. Not synced to SI or RM. Has `keep_following: true` flag for contacts you are and want to remain following (personal friends). Pre-populated from SI "personal" category contacts (32 accounts).

Current confirmed personal network (never engage):
- `delphy_dj`, `nivast`, `lagroovemachine_music`
- All score-1 personal category contacts from SI
- Additional friends added manually by you

Removed from personal network (neutral — still in SI personal category, engine ignores them but does not protect them):
- `italomario_`, `ladystarlightnyc`, `annahaletadj`, `stellarcompanion`, `iamgeorgekasradze`, `ruben_keyko`

Reclassified:
- `alenskanner` → DJ in SI, score updated to 4, full Scene eligible (EBM DJ, liked your track, SC confirmed 1,906 followers)

---

## Part 5 — Session Rules (Safety Envelope)

### Session schedule

- **Days:** Monday / Wednesday / Friday
- **Time:** 10:00–11:00 AM Berlin time
- **Max duration:** 20 minutes hard cap
- **Never run** while actively using Instagram on mobile
- **Method:** Real Chrome browser via computer-use

### Hard circuit breakers — stop immediately

Stop the session and log if ANY of these occur:

- "Action Blocked" message on screen
- Login or verification prompt appears
- CAPTCHA or any "prove you're human" challenge
- Phone number verification request
- "Confirm it's you" identity check
- Account temporarily locked notification
- "Unusual activity detected" alert
- Checkpoint challenge (any screen asking to review recent activity)
- Any screen appearing that is not a normal feed, profile, or post page
- Privacy policy update requiring acceptance
- Any notification prompt (enable push notifications, etc.)
- Instagram crashes or profile fails to load after 2 attempts
- **Never enter a password under any circumstances**
- **Never accept any privacy change, terms update, or settings notification**
- **Never open any DM or inbox — under any circumstances**
- **Never click any link anywhere in the browser** — not in posts, captions, bios, notifications, DMs, or anywhere. Navigation typed directly into address bar only.
- **Never engage with sponsored posts, ads, or promoted content**
- **Never interact with any Settings, Account, or notification preference screen**

### After a circuit break

- Soft block (one action type blocked, account still works): **48-hour pause**, then resume at reduced limits for 1 session before returning to normal
- Hard block (account restricted): **72-hour pause minimum**
- CAPTCHA or verification: **72-hour pause + manual review** before resuming
- Any identity verification request: **stop all automation, consult before resuming**

### Unfollow timing rules

- Wait exactly **7 days** after follow before checking follow-back status
- Followed back → permanent keep list, never auto-unfollowed
- No follow-back after 7 days → add to unfollow queue, execute in next eligible session
- Never unfollow same day as following
- Never re-follow a previously unfollowed account (logged permanently)
- Space unfollows across the session — mix them with likes, not batched at the start
- Personal contacts with `keep_following: true` in `ig_personal_network.json` → never unfollowed regardless of 7-day rule
- Contacts in active promo campaigns → never unfollowed during campaign window
- **Phase 3 (continuous):** Up to 10 unfollows/session when non-returners are available. Monthly review session with me to assess and decide on any boost. Never a single mass unfollow event.

---

## Part 6 — Pre-Automation Checklist

### Must be done before first automation session

- [x] New IG data export received and parsed — done 2026-04-22
- [x] Following cleanup done (54 accounts unfollowed, now at ~841 following) — done 2026-04-22
- [x] Chrome session verified on Instagram (@inch_of_shadow) — confirmed 2026-04-23
- [ ] **IG enrichment pass** — fetch IG follower counts for all 972 SI contacts. CRITICAL. Scene cannot function without this data. Only 3 contacts currently have `instagram_followers` populated.
- [ ] **Review 53 dropped contacts** — DJs (26), venues (15), labels (12), media (6) exist in `raw_contacts.json` with IG handles but were dropped during enrichment. Check each — some are real scene contacts that should be re-added to SI.
- [ ] **Review score 1 contacts** — 59 contacts with score 1 in SI. Some wrongly scored, some Israeli, some should be deleted. Manual review pass.
- [ ] **Review 32 personal category contacts** — split into: keep in SI (scene contacts), move to ig_personal_network.json, or delete. Partial decisions made (see Part 4). Remaining require your review.
- [ ] **Populate ig_personal_network.json** — add real friends not captured in SI exports. Engine file ready; you must fill it manually.
- [ ] **Populate ig_blocked_accounts.json** — add Israeli accounts found in SI + anyone else to permanently block.
- [ ] Bio updated with genre keywords in first two visible lines (proposed: `Dark disco · EBM · acid · electro · Berlin` / `Producer · DJ · @ambertone.studios` / `½ of @doublefigure_band · @collective.dada`)
- [ ] Link in bio updated (Linktree — Spotify artist + SoundCloud + Beatport/Traxsource + Bandcamp)
- [ ] **"Your Algorithm" feature** — Settings → Content Preferences on @inch_of_shadow. Manually set topic categories: dark disco, EBM, electronic music, acid, techno, Berlin underground.
- [ ] **IG profile category** — check Settings → Edit Profile → Category. "Musician/band" is too generic. Update if more specific option exists.
- [ ] At least 1 Story Highlight live (Gigs)
- [ ] Initial target list built (seed `ig_target_list.json` with 20–50 accounts from hashtag/competitor sources)
- [ ] `ig_engagement_log.json` created (or confirm `engagement_log.json` handles both SC and IG)
- [ ] `ig_follow_tracker.json` created
- [ ] `ig_engagement_config.py` reviewed and approved (includes tier table as live-editable config)
- [ ] `alenskanner` reclassified in SI: category → dj, score → 4

### Nice to have (not blockers)

- [ ] 3–4 Story Highlights live
- [ ] Hashtag sets tested on 2–3 posts
- [ ] Posting schedule defined (minimum 3x/week)
- [ ] Competitive intel pass — collect bio/hashtag/posting data from 20–30 reference artists for `competitive_intel.json`

---

## Part 7 — File Architecture

```
scene_intelligence/
  ig_engagement.py            # Main engine (Chrome browser automation)
  ig_engagement_config.py     # All tunable values + engagement tier table
  ig_follow_tracker.json      # Active follows + unfollow schedule (7-day window)
  ig_target_list.json         # Approved target accounts queue (Reach)
  ig_blocked_accounts.json    # Permanent hard skip list (manual)
  ig_personal_network.json    # Personal contacts — engine never touches (manual)
  ig_performance_log.json     # Your own post performance (manual monthly input)
  ig_enriched_contacts.json   # SI contacts with IG follower data (output of enrichment pass)

  engagement_log.json         # Shared log (IG + SC actions) — already exists
  enriched_contacts.json      # Master contact database — already exists
  promotion_log.json          # Campaign data — already exists
  release_context.json        # Active release context — already exists

data_intelligence/            # New directory
  competitive_intel.json      # Copy/hashtag/posting patterns from 20-30 reference artists
  seo_versions.json           # Your approved copy versions with performance data
```

### JSON sync rules

| File | Who writes | Who reads | Sync rule |
|------|-----------|-----------|-----------|
| `enriched_contacts.json` | SI scripts, RM webapp | IG engine (Scene), SC engine, Promotion Engine | Master. Any flag set in RM writes here → push_to_sheets.py syncs to Google Sheets |
| `engagement_log.json` | IG engine, SC engine | RM Promotion Engine, both engines | `hidden` list respected by all engines. IG actions logged with platform tag |
| `ig_follow_tracker.json` | IG engine only | IG engine only | Contacts in active promo campaigns get `keep_following: true` — never unfollow during campaign |
| `ig_blocked_accounts.json` | Manual only | IG engine (session start) | Standalone emergency brake. Not synced to SI or RM |
| `ig_personal_network.json` | Manual only | IG engine (session start) | `keep_following: true` entries never unfollowed |
| `promotion_log.json` | RM webapp | IG engine (Scene prioritisation), SC engine | Active campaign contacts get Tier 1 priority. IG pre-warm logged here |
| `release_context.json` | RM webapp | IG engine, SC engine | Active release genre used for boost mode |
| `competitive_intel.json` | Enrichment scripts | Copy generator | Reference style data for SEO copy generation |
| `seo_versions.json` | Manual + copy generator | Copy generator | Your copy history + performance. Generator weights toward better-performing versions |

---

## Part 8 — Data Collection and Intelligence

### Data collected per Reach account

Every account that enters the target queue is logged with:
- Discovery source (which hashtag, which competitor's follower list)
- Follower count at discovery
- Genre signals found (bio keywords, hashtags)
- Follow date
- Follow-back: yes/no, date
- Unfollow date (if applicable)

This dataset is the seed for future paid campaigns. Accounts that followed back are your highest-quality lookalike audience. Build it now even if you don't use it for 12 months.

### Data collected per SI contact (Scene enrichment)

During IG enrichment pass and subsequent sessions:
- IG follower count (with date — track growth over time)
- Post frequency (posts per week)
- Estimated engagement rate (visible likes ÷ followers)
- Bio text (for keyword analysis)
- Consistent hashtags used
- Content mix type (live photos, studio, artwork, Reels)
- Last engagement date by us

### Promotion log — enhanced fields per target

New fields added to each promo campaign target:
- `reply_content` — what they said when they replied (verbatim)
- `reply_date` — when they replied
- `reply_sentiment` — positive / neutral / negative / no_reply
- `follow_up_due` — date to chase if no reply
- `follow_up_sent` — boolean
- `ig_pre_warm` — did the IG engine like their post before pitching?
- `ig_pre_warm_date` — when
- `sc_pre_warm` — did SC engine engage before pitching?
- `result_detail` — optional free text (e.g. "Played at Tresor April 2026" — useful for future pitch hooks)
- `relationship_status` — cold / warm / active / advocate

### SEO intelligence system (7-step vision)

**Step 1 (now):** Collect bio text, hashtag patterns, posting frequency, engagement rate from 20–30 reference artists/labels (Mannequin Records, Dark Entries, Clone, Lies, etc.). Store in `competitive_intel.json`. Copy generator reads this as style reference before generating anything.

**Step 2 (ongoing, each session):** Every profile visited during Reach/B logs bio text and hashtag usage. Dataset of 200–400 scene accounts builds over 3 months. Patterns emerge: which hashtag combinations correlate with higher engagement rates.

**Step 3 (monthly, manual):** Log own post performance from IG Insights — saves, reach, profile visits triggered — into `ig_performance_log.json`. Links to which copy version and hashtag set was active at time of posting. Takes 5 minutes per month.

**Step 4 (after 2–3 releases):** Copy generator gets reference mode — reads performance log and competitive intel before generating. Weights toward patterns that performed better for you specifically. Rule-based, not ML: "Set A hashtags averaged 3× more saves than Set B in last 90 days — prefer Set A patterns."

**Step 5 (before paid campaigns):** Reach follow-back dataset + performance-correlated copy library + scene-level hashtag intelligence map = your paid campaign brief. Custom Audience seed from follow-back list. Lookalike audiences from it. Targeting based on real data, not guesswork.

**Step 6 (ongoing):** Paid campaign results feed back in. Which copy variants performed? Which audience segments converted? Into copy generator reference data. Three data sources now: organic performance, competitive intel, paid results.

**Step 7 (scale):** Proprietary dataset of scene-level copy intelligence, personal engagement history, and campaign performance. No tool you can buy gives you this — it's built on real scene relationships. Shows labels and agents not just follower counts but engagement patterns, audience quality, and campaign performance.

---

## Part 9 — Growth Projections

| Timeframe | Followers | Net new | Driver |
|-----------|-----------|---------|--------|
| 1 month | 840–860 | +50–70 | Cleanup + Phase 1 follows |
| 3 months | 950–1,050 | +160–260 | Phase 2, compounding |
| 6 months | 1,200–1,500 | +400–700 | Ratio improving, snowball |

Key multiplier: **Reels.** One strong live set clip or studio reel can add 50–100 followers organically in a week. The automation builds the floor, content builds the ceiling.

---

## Sources and Research

- [Instagram Algorithm 2026 — Buffer](https://buffer.com/resources/instagram-algorithms/)
- [Instagram Algorithm — Ranking Signals Mosseri Confirmed](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers)
- [Your Algorithm Feature — ALM Corp](https://almcorp.com/blog/instagram-expands-your-algorithm-to-explore/)
- [Hashtags 2026 — Edge Marketing](https://edgemarketingdesign.com/article/instagram-updates-for-2026-why-hashtags-dont-work-like-they-used-to)
- [Hashtag Best Practices 2026 — Social Pilot](https://www.socialpilot.co/instagram-marketing/instagram-hashtags-guide)
- [Follow/Unfollow Limits 2026 — FeedFlux](https://feedflux.app/blog/instagram-follow-unfollow-limits-2026)
- [Instagram Limits 2026 — Metricool](https://metricool.com/instagram-limits/)

---

## 2026-06-14 verified refresh (deep research)

Source of truth: `plans/platform-algorithm-research-2026-06.md` (Reddit-cross-checked, adversarially verified). Use that doc's Instagram section for citations. Net changes vs the older guidance above:

**Confirmed signal hierarchy (Reels/Explore drive non-follower reach for a small act):**
- Watch time / completion (the 3-second hook decides) — HIGH, Mosseri-confirmed top Reels signal.
- Sends per reach (DM shares) — HIGH, slightly more important than likes for cold reach.
- Originality — HIGH (native, non-watermarked, original audio).
- Keyword/search indexing of caption, on-screen text, alt text, name, bio — HIGH (hashtags only categorize).
- Likes per reach — MEDIUM (skews to existing followers).

**Busted myths (do NOT encode or repeat):**
- "Editing a Reel caption after posting kills reach" — REFUTED by Mosseri. Finalizing pre-publish is fine practice, but edits do not punish reach.
- "Sends are 3-5x a like" / "originality = 40-60% more reach" — the directions are real; the multipliers are fabricated. Never cite the numbers.
- "Small accounts get an automatic discovery boost" — CONTESTED. Correct framing: follower count no longer gates reach; expect no automatic boost.

**Highest-leverage actions:** set the IG Name field to "Inch of Shadow | Dark Disco / EBM" (searchable, one-time); engineer for sends; default to original audio (Amir's own tracks); burn a genre/context line as on-screen text; use Trial Reels to test hooks on cold audiences.

**Unchanged:** all IG risk hard-rules stand (one script/day, cumulative caps, 48-72h cooldown after detection, profile scope check). This refresh is content/strategy only, not an engagement-cadence change.
