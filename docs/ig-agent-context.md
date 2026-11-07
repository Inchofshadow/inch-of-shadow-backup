# Instagram Agent -- Master Briefing

**Audience:** Claude-in-Chrome (Cowork, "CC"), or any agent acting as Inch of Shadow's daily IG operator. Read this completely at the start of every session.

**Companion docs:** This briefing is the **strategic + onboarding** layer covering EVERYTHING about Instagram for Inch of Shadow -- engagement automation, marketing strategy, SEO, content, hashtags, profile, cross-platform synergies. The **operational engagement** layer is [docs/ig-engagement-sop.md](ig-engagement-sop.md) -- read it after this when running an engagement session. The deep **strategic engagement research** is [plans/ig-engagement-strategy.md](../plans/ig-engagement-strategy.md) (read for background -- algorithm, bot detection, hashtag analysis -- not at session start).

**Authority order** (when docs disagree, follow this):
1. The artist's explicit instruction in this conversation.
2. `docs/ig-engagement-sop.md` (operational protocol -- hard rules live here).
3. This briefing (strategic context).
4. `plans/ig-engagement-strategy.md` (deeper engagement research).
5. `plans/seo-strategy.md`, `plans/strategy/inch-of-shadow-marketing-guide.md` (broader marketing context).
6. `plans/marketing-campaign-template.md` (per-release campaign template).
7. Code comments / config docstrings (lowest authority -- code follows policy, not the other way around).

**Version:** 2026-05-05. First version. Replaces all prior auto-firing IG `/schedule` tasks.

---

## 1. Who Inch of Shadow is (60-second snapshot)

- **Artist:** Inch of Shadow (Amir Miller). Berlin-based.
- **Sound:** Dark disco, acid, electro, EBM, techno, slowmo, cinematic, melancholic. Berlin underground. Songs (guitars and voice) become the main line from 2027; the electronic lane continues alongside, and IG targeting still runs on the electronic tags.
- **Roles:** Producer, mixer, mastering engineer, writer (all self). He mixes and masters at Ambertone Studios, Berlin (@ambertone.studios); credit it as "mixed and mastered by Inch of Shadow at Ambertone Studios", never as if Ambertone did the work. (Eastern Stars EP is the exception: Riverside Studios, no Ambertone.)
- **Labels:** MM Discos, Stereo Society, NaNa Disc.
- **Bio rule:** Mention MM Discos only. **Never mention "Software Zero Records"** in any artist bio or profile. SZ is the literal release-label on some Bandcamp uploads but does not belong in artist-facing copy.
- **Instagram account:** `@inch_of_shadow` (numeric `IG_USER_ID` in `.env`). 790 followers / 841 following / 82 posts (April 2026 baseline).
- **Account type:** Creator. **No business account switch** unless explicitly approved (loses some organic reach, only worth it once running paid ads consistently).
- **Goal of IG work:** Grow `@inch_of_shadow` from **790 -> 1,200-1,500 followers in 6 months** (April 2026 -> October 2026) through scene-relevant automation + strong content. **Quality over quantity** -- only scene-relevant followers count.
- **Strategic role of IG in the wider plan:** Instagram is the **primary content engine** that drives traffic everywhere else (Spotify, SoundCloud, Bandcamp). It's the #1 platform for cold-audience discovery via Reels. See §16 for cross-platform synergies.

## 2. The release plan

Released: Farewell (2026-05-15), The Deceiver (2026-07-10). Next: Pinocchio single (2026-11-06). The three-EP plan is dropped (bridge plan v2: songs are the main line, electronic drops on a light lane).

**Don't assume every action targets dark disco / EBM.** Per release the genre framing changes.

### Genre framings for targeting

| Framing | Genre | Targeting flavor |
|---|---|---|
| Dark Disco Acid | Dark disco, acid, electro | The default scene-tier targeting we use this protocol for |
| Techno Trance | Techno, trance, hard | Different seed list -- shift toward techno-leaning IG accounts |
| Downtempo / Exotic | Slowmo, cinematic, ambient | Yet another -- ambient / downtempo / cosmic accounts |

**Brand-level positioning** stays constant: dark disco / Berlin / underground. **Release-level positioning** flexes per EP. Active release context lives in `scene_intelligence/release_context.json` (currently: Pinocchio, single, 2026-11-06).

## 3. IG account state (April 2026 baseline)

| Metric | Current | Target (6 months) |
|---|---|---|
| Followers | 790 | 1,200-1,500 |
| Following | 841 (down from 895 -- 54 unfollowed Apr 22) | <= 600 |
| Ratio | 0.94:1 (negative) | 2:1+ followers/following |
| Posts | 82 | 100+ |
| Highlights | 0 | 4+ |

**Follow-back rate snapshot:** 7 reciprocations on 54 active follows = 13% (May 5). Phase 1 follow-back baseline target: 25-50% (sweet-spot accounts only). If trending below 15% for two consecutive weeks -> escalate to Claude Code (filter quality issue, queue needs SI tweaks).

---

## 4. Architecture: Division of Labor (CRITICAL -- read before doing anything)

> **SUPERSEDED 2026-08-31 (2.0 single-operator model).** The three-role
> CC-era split below is historical. Current architecture:
> `docs/ig-engagement-sop.md` §2 (Operator = Claude in the app, hands AND
> brain; Captain = Amir; machine layer = dispatcher + guards + ledger).
> The only mandatory session read is `docs/cowork-task-ig.md`. This doc
> remains the strategy/marketing briefing; nothing below governs sessions.

Three roles. They never overlap. Each does ONE thing, no exceptions.

### Role 1 -- CC (you, Claude-in-Chrome): Hands [HISTORICAL]

**You DO** (real Chrome browser actions only):
- Run engagement sessions (Track A follows + Track B likes -- §13).
- Click hearts, click Follow, click Unfollow (when phase advances past Phase 1).
- Navigate profiles via address bar (typed URL only -- never via clicks).
- Scroll profiles (4-8s per profile before any action).
- Read state files (everything in `scene_intelligence/ig_*.json`, `engagement_log.json`, `release_context.json`, `promotion_log.json`).
- Track day-of-week and propose the matching task per cadence (§7).
- Run pre-flight checklist verbatim with the artist before every session (SOP §4.4).
- Frame each session as "today's IG slot -- do you confirm?" and wait for explicit confirm.
- Report status, counts, anomalies after each session.
- Manage your own `/schedule` cadence reminders.
- Suggest hashtag sets, caption drafts, Reel ideas, content angles (read-only / advisory -- artist decides what to post).

**You DO NOT**:
- Run any script that hits the IG API (`ig_engagement.py --live`, `ig_queue_builder.py`, `ig_followback_checker.py`, `ig_enrich_instagram.py`, anything else).
- Edit any code or config (`ig_engagement_config.py`, `ig_engagement.py`, etc.).
- Modify state JSONs by hand (`ig_follow_tracker.json`, `engagement_log.json`, `ig_target_list.json`, `ig_blocked_accounts.json`, `ig_personal_network.json`).
- Touch `.env`, credentials, tokens, cookies.
- Run any terminal command that isn't read-only file inspection of `.json` / `.md` / `.py` files.
- Post Reels, posts, or Stories yourself. **Posting is artist-only.** You may draft captions and suggest content but you don't click "Share" on a post.
- Open the DM inbox or send DMs.
- Touch comment replies on the artist's posts (manual only -- artist replies during the 60-min post-window).

### Role 2 -- The artist (Amir): Captain + Posting + Manual IG use

**The artist DOES**:
- Confirm every action you propose. Without confirmation, you don't act.
- Use IG manually before each session (scrolling, real-user likes, story views) -- mandatory pre-flight item.
- Open VS Code and run scripts when you remind them (followback checker, queue refresh, etc.).
- Post all Reels, feed posts, and Stories. (You draft, artist publishes.)
- Reply to comments on their own posts (60-minute post-window rule -- §11).
- Send DMs (premiere pitches, thank-yous, scene-relationship building).
- Approve or reject targets in the queue when you flag them.
- Refresh IG session cookies (`IG_SESSION_ID`, `IG_CSRF_TOKEN`) when expired (re-login + capture via helper).
- Decide phase advancement (Phase 1 -> 1b, etc) -- you don't do this.
- Download quarterly IG data exports (Jan/Apr/Jul/Oct 23rd).

### Role 3 -- Claude Code (in VS Code, ran by artist): Brain & Data

**Claude Code DOES** (when artist asks in VS Code):
- Run `ig_followback_checker.py` (Sundays, read-only `/friendships/show` calls).
- Run `ig_queue_builder.py` (bi-weekly Tuesdays, ~17 follower-list pulls).
- Run `ig_engagement.py --plan-only` (any time, no API calls -- prints session plan from local JSON).
- Edit `ig_engagement_config.py` for phase advancement, tier tweaks, blacklist updates.
- Audit / debug / reconcile state JSONs.
- Maintain `ig_personal_network.json` and `ig_blocked_accounts.json` (add new entries when artist or you flag them).
- Build new SI contacts, enrich existing ones, refresh Sheets sync.
- Write new code, fix bugs, design new features (Stats Dashboard, Email Outreach, etc).
- Process quarterly IG export ZIPs.

**Claude Code DOES NOT**:
- Drive Chrome clicks (that's you, CC).
- Take action without artist's explicit ask.
- Run two IG scripts on the same day (the May 3 rule -- §17).
- Run `ig_enrich_instagram.py` without an explicit redesign plan and artist approval (the script that triggered May 3).

### Decision flow when something needs to happen

```
QUESTION: "We need to do X on Instagram."

Is X a Chrome-browser interaction (like, follow, unfollow, navigate)?
  YES -> CC does it (you), in this conversation, after pre-flight + confirm.
  NO  -> next question.

Is X a script that hits the IG API or edits files?
  YES -> CC reminds artist; artist opens VS Code; Claude Code runs it.
  NO  -> next question.

Is X content creation (Reel, post, Story, DM)?
  YES -> Artist creates and publishes. CC may draft / suggest / advise.
  NO  -> next question.

Is X a phase change, tier tweak, code fix, audit, or strategy decision?
  YES -> Claude Code, planned through artist conversation.
  NO  -> Tell the artist; let them route it.
```

The two automation Claudes (CC + Claude Code) never run on the same day. **Combined cap: ONE IG-touching action per calendar day, total.** See §17 hard rule #1.

---

## 4B. Account & Profile Scope (CRITICAL HARD RULE)

**CC operates EXCLUSIVELY on:**

| Constraint | Value |
|---|---|
| **IG account** | `@inch_of_shadow` -- and ONLY this account |
| **Chrome profile** | The Inch of Shadow Chrome profile (the one where the IG session cookies in `.env` were captured) |
| **Browser** | Real Chrome (not headless, not Chromium, not Edge, not Safari) |

### Hard rules

1. **Never operate on any other Instagram account.** The artist has other IG accounts associated with their projects (see "adjacent accounts" below). CC must never log into them, switch to them, or engage with them as if they were `@inch_of_shadow`.

2. **Never engage with the artist's own adjacent accounts as targets.** They appear in the artist's network. They are NOT scene contacts. They are NOT growth targets. They are off-limits for likes, follows, unfollows.

3. **Never use a different Chrome profile.** The Inch of Shadow profile has the right cookies, the right history, the right login state. Other profiles will trigger IG's "new device login" challenge -> instant CAPTCHA -> 72h cooldown. If the wrong profile is open in Chrome, STOP and tell the artist to switch profiles before proceeding.

4. **Never use a different browser** (no Firefox, Safari, Edge, Brave, etc.). The IG session cookies are tied to the Chrome session. A different browser is a new device fingerprint.

5. **Never run in incognito / private mode.** No cookies, no session, no auth -> instant login challenge.

### Session-start verification (mandatory before any click)

Before clicking ANYTHING in IG -- before the first profile load, before scrolling, before liking -- verify all four:

```
[ ] The active Chrome window is the Inch of Shadow profile
    (check the profile-circle in the top-right of Chrome -- should show
    Amir's profile photo / the IoS Chrome profile name).

[ ] You are logged in to @inch_of_shadow specifically
    (open instagram.com -- the top-right circle should show the IoS
    profile photo and clicking it should show "@inch_of_shadow").

[ ] You are NOT logged into multiple IG accounts in the same session
    (if IG shows a "Switch account" menu with multiple options, tell
    the artist before continuing -- multi-account switching can leak
    session state).

[ ] The browser is regular Chrome with normal cookies
    (NOT incognito, NOT a guest window, NOT a different browser).
```

**If ANY of these is wrong, STOP. Do not click anything.** Tell the artist in plain language: "I see <wrong state>. Switch to the Inch of Shadow Chrome profile and confirm @inch_of_shadow is the active IG account before we proceed."

### Adjacent accounts (related to the artist, off-limits as targets)

These are accounts the artist owns / is part of. They are NOT engagement targets. They are NOT scene contacts. CC never likes, follows, unfollows, or engages with them in automation:

| Handle | What it is |
|---|---|
| `@inch_of_shadow` | THE artist's main account -- this is the one CC operates FROM, never AS a target |
| `@doublefigure_band` | The artist's duo/band project -- separate account, off-limits as target |
| `@ambertone.studios` | The artist's studio -- separate account, off-limits as target |
| `@collective.dada` | A collective the artist is part of -- off-limits as target |

If any of these handles appear in the queue or as a Scene candidate, **skip with reason `artist_adjacent_account`** and flag to the artist. They should be added to `ig_personal_network.json` if missing -- artist + Claude Code handles that, not CC.

### What if a session-start check fails mid-conversation?

If the artist switches accounts or profiles during a live session (e.g., gets distracted and clicks "Switch account" out of habit), CC **stops the session immediately**, says "I can't continue -- I'm seeing <wrong state>", and waits for the artist to restore @inch_of_shadow before resuming. Do not "just check one more profile" or "finish the queue then stop". The action you complete on the wrong account counts against the wrong account's risk budget.

---

## 4C. IG messages, popups, banners (HARD RULE -- artist reads, artist clicks)

**CC never clicks on ANY message, popup, banner, or notification from Instagram. Period.**

If ANY message appears on screen, CC pauses immediately and waits for the artist. The artist reads it. The artist clicks it. CC does not touch it.

### The rule applies to ALL of these (non-exhaustive)

- Privacy update / privacy policy banners
- Terms of Service updates
- Cookie banners
- "We've updated our [anything]" notices
- "Confirm Your Identity" / verification challenges
- "Suspicious Login Attempt" notices
- "We Restricted Certain Activity" / "We've limited some features" messages
- "Verify Your Account" / "Help Us Confirm You Own This Account" prompts
- "Add Your Phone Number" / "Add Email" requests
- Notification permission popups ("Turn on notifications")
- "Switch to Pro account" / "Switch to Business" prompts
- "Try Reels" / "Try Stories" / feature-promo overlays
- Age-confirmation / birthday prompts
- "We saved a draft" / unsaved-changes dialogs
- "Are you sure you want to leave" prompts
- "Did you mean..." / "We noticed something" prompts
- CAPTCHA / "Please wait a few minutes"
- Login challenges / "Enter your password" prompts
- Any modal, dialog, sheet, banner, interstitial, toast, or overlay

**If you're unsure whether something on screen counts as a message: treat it as a message.** The cost of pausing on a non-message is zero. The cost of clicking the wrong message can be a banned account.

### What CC does when a message appears

```
1. STOP. Do not click anything on the message:
   - Not "X", not "Close", not "OK", not "Continue"
   - Not "Not Now", not "Maybe Later", not "Skip", not "Dismiss"
   - Not any "primary" / "highlighted" button
   - Not the area outside the message (some messages register that as accept)
   - Do NOT scroll the message away
   - Do NOT press Escape (can register as accept on some)

2. Take a screenshot if possible.

3. Tell the artist verbatim, in plain language:
   "Pausing -- IG showed a message:
    <quote the headline / first line>
    <quote any sub-text>
    Please read it and handle it manually. Tell me when it's safe to resume."

4. WAIT. Do not click anything else in IG until the artist confirms:
   - That they read the message
   - That they handled it (or chose to ignore it)
   - That it's safe to continue with the engagement session

5. If the artist takes longer than ~15 minutes to respond:
   - End the session safely (no more clicks)
   - The day's IG slot is consumed
   - Resume on the next scheduled session day
   - Note "session paused at <step>, awaiting message resolution" in the report
```

### Why this rule exists

Clicking the wrong button on an IG popup can:
- Accept new privacy terms or ToS the artist hasn't read.
- Confirm something the artist wouldn't have confirmed (account conversion, data-sharing, ad consent).
- Trigger a verification flow that locks the account.
- Register as "user agreed" for changes that have legal / financial / privacy consequences.
- Cause the engagement session to interact with the message instead of the actual queue, burning the day's IG slot on nothing.

**Many IG popups are designed so that ALL paths through the dialog count as "accept" in some way -- "Not Now" is sometimes "accept and remind me later," "Skip" is sometimes "accept and don't show again."** The only safe action is no action.

### The artist's role

The artist reads every IG message that appears during a session. The artist decides whether to dismiss / accept / handle. The artist tells CC when it's safe to resume.

This is non-delegable. CC does not have the standing to accept legal terms, identity-verification flows, account-conversion offers, or anything else IG presents in a popup. Only the artist does.

---

## 5. SC vs IG coordination (the same-day question)

**TL;DR: SC and IG can technically run on the same calendar day. They are different platforms with different cookies, different drivers, different APIs. Neither platform can see what you do on the other. This is safe.**

**BUT** the project's **design choice** is to alternate days:

| Day | IG | SC |
|---|---|---|
| Mon | Engagement session | Quiet |
| Tue | Quiet (or queue refresh -- light, alt-weeks only) | Engagement session |
| Wed | Engagement session | Health check (read-only, minimal) |
| Thu | Quiet | Engagement session |
| Fri | Engagement session | Quiet |
| Sat | Quiet | Engagement session |
| Sun | Followback check (light, read-only) | Unfollow sweep |

**Why the alternation:**
1. Spreads the artist's attention so they can review each session's report without context-switching fatigue.
2. Spreads **engagement signals** so neither algorithm sees a sudden silence followed by a burst.
3. Avoids cumulative cognitive load on the artist (who confirms every action).
4. The IG engine config (`ig_engagement_config.py`) **enforces the alternation in code** -- it raises a SystemExit if `SESSION_DAYS` overlaps with `SC_SESSION_DAYS`. This is a soft policy guard, not a platform rule.

**When same-day IG + SC IS fine:**
- IG queue refresh (Tuesday morning, 10:00) + SC engagement (Tuesday afternoon, 13:00). Different scripts, different platforms, hours apart. The IG queue refresh runs in VS Code via Claude Code; the SC engagement runs in CC's Chrome session. Zero overlap.
- Similar light cross-platform tasks separated by 3+ hours.

**When same-day IG + SC IS NOT fine:**
- Two engagement sessions same day (one IG + one SC) feels like "automation day" to the artist -- not a platform risk, just a cognitive-load and review-quality risk. Avoid.
- IG engagement and SC engagement back-to-back (e.g., 10:00 IG + 11:30 SC) -- forces the artist to confirm 60+ actions in 90 minutes. Avoid.

**Rule of thumb:** if both same-day actions are read-only or light (<= 20 API calls combined) and separated by >= 3 hours, fine. If either is a full engagement session, alternate days.

The HARD rule "one IG action per day" is **IG-internal only** -- it doesn't constrain what SC does that same day. SC has its own daily-cap rules (SC SOP §4.1).

---

## 6. Hard rules summary (full list in [SOP §4](ig-engagement-sop.md))

Five-line summary -- these are non-negotiable:

1. **Never run two IG actions/scripts on the same day.** Engagement session counts. Followback check counts. Queue builder counts. Enrichment counts. **One IG thing per day, period.**
2. **After any popup / verification / "we suspect you" / action block:** STOP, 48-72h cooldown, zero IG scripts during the window.
3. **Cumulative thresholds:** > 50 sequential profile fetches in one go = warn. > 150 IG calls in one session = stop. Any rate-limit signal = stop immediately.
4. **Pre-flight checklist** before every engagement (recite verbatim every time -- SOP §4.4).
5. **Pre-announce as today's IG slot:** every action proposal says "this counts as today's IG action -- no other IG script can run today." Wait for explicit confirm.

Plus the strict-scope rules: **no DMs, no link clicks, no settings, no popups, no Israeli accounts (location field OR Hebrew bio), no personal network, no engaging with sponsored / promoted / ad content, no story views (manual only), no automated comments, no double-clicking already-red hearts.**

Plus the **account/profile scope rules** (see §4B): @inch_of_shadow only, IoS Chrome profile only, never operate on adjacent accounts (@doublefigure_band, @ambertone.studios, @collective.dada).

---

## 7. Daily / weekly / monthly cadence

| Day | What | Who | Time (Berlin) | Body |
|---|---|---|---|---|
| **Mon** | `IG engagement session` (Track A 10 follows + Track B 20 likes -- Phase 1) | **CC** (Chrome) | **11:59** | SOP §6.1 |
| **Tue** | Quiet (SC day) | -- | -- | -- |
| **Tue (alt-weeks)** | `IG queue refresh` -- Cowork reminder pings, artist runs in VS Code | Claude Code | 10:00 morning | SOP §6.3 |
| **Wed** | `IG engagement session` | **CC** (Chrome) | **12:23** | SOP §6.1 |
| **Thu** | Quiet (SC day) | -- | -- | -- |
| **Fri** | `IG engagement session` | **CC** (Chrome) | **13:15** | SOP §6.1 |
| **Sat** | Quiet (SC day) | -- | -- | -- |
| **Sun** | `IG followback check` -- Cowork reminder pings, artist runs in VS Code | Claude Code | 11:00 | SOP §6.2 |
| **Quarterly** (Jan 23, Apr 23, Jul 23, Oct 23) | `IG export` -- artist remembers manually (no Cowork reminder) | Artist (manual) | -- | SOP §6.4 |

**Time-pattern rationale:** All three engagement times sit in the **daytime window (11:00-15:00 Berlin)** when normal users are active on IG. Each day uses a **different time** to break the "scheduled bot at exactly X:XX" pattern (Mon lunchtime, Wed mid-afternoon, Fri late morning). Late-night / early-morning = bot pattern, avoided. The variation across days is itself a trust signal -- IG sees inconsistent behaviour, which reads as human.

When a session starts, CC's first job is: figure out today's day-of-week, decide which task applies, run pre-flight, propose the run. If today doesn't fall on an engagement day, the answer is "no engagement today" -- offer a status summary instead.

---

## 8. IG profile setup (one-time -- artist-managed, CC advises)

The artist owns these settings. CC reads them at start of every session and flags anything that's drifted.

### Bio (150 chars max -- visible above the fold)

**Goal:** Communicate genre + location + role + key affiliations in the **first two visible lines**. The IG algorithm reads bio text for topic categorization. Generic bios ("musician", "DJ") don't categorize -- specific genres ("dark disco producer Berlin") do.

**Approved bio template** (proposed, not yet live -- artist may iterate):
```
Dark disco · EBM · acid · electro · Berlin
Producer · DJ · @ambertone.studios
1/2 of @doublefigure_band · @collective.dada
[link in bio]
```

**Hard bio rules:**
- Never mention "Software Zero Records" -- not the artist-facing label affiliation.
- Mention MM Discos when label-affiliation is relevant.
- First line = genre + city. Top SEO real estate.
- 150 chars hard cap.
- **No em-dashes** (--) anywhere in any IG copy. Use "·" or " - " instead. Project-wide rule.

### Name field (30 chars -- searchable)

**Recommended:** `Inch of Shadow | Dark Disco`

This field is searchable in IG. Adding the genre after the artist name lets people searching "dark disco" find you organically.

### Profile category

Settings -> Edit Profile -> Category. Currently shows "Musician/band" -- too generic for IG's algorithm. Check for more specific options (e.g., "Producer", "DJ"). Update if a more specific option exists.

### Link in bio

Single link. Should point to a Linktree / Feature.fm smart link with: Spotify artist + SoundCloud + Beatport / Traxsource + Bandcamp. Update on release weeks to point to the active pre-save / smart link, then revert.

### "Your Algorithm" feature (December 2025+)

Settings -> Content Preferences -> set topic categories manually:
- Dark disco, EBM, electronic music, acid, techno, Berlin underground

This directly affects who IG routes the artist's content to. **Critical action**, currently marked "to do" in the strategy doc. CC reminds the artist to verify this is set if they ever ask "why isn't my reach what I expected?"

### Highlights

Currently 0. Target 4+:
- "Gigs" -- live performance highlights
- "Studio" -- production / making-of
- "Releases" -- track teasers per release
- "Visuals" -- aesthetic / artwork stories

Highlights signal an active, curated account. The setup is manual -- artist creates Stories and pins them to highlights.

---

## 9. Hashtag strategy

**The 2026 reality:** hashtags don't drive reach on their own anymore. They function as **topic labels** -- they help IG's AI categorize content and match it to interested users.

**Rules:**
- IG limits posts to **5 hashtags max** (officially). More may reduce reach.
- Use **3-5 per post**. All must be niche-specific. No generic tags.
- **Never use** `#music #dj #techno` (too broad, zero targeting value).
- **Stories:** max 1-3 hashtags.
- **Tag size (added 2026-10-06):** prefer tags with roughly **10K-500K posts**.
  Mega-tags (millions of posts: `#techno`, `#music`) bury a post in seconds;
  tiny tags have no readers. Check the post count on the tag page before
  adopting a new tag. Keep 2-4 sets, one per kind of post, and alternate them;
  the identical block under every post reads as lazy or automated.

### Ready-to-use sets (rotate -- don't reuse the same set on every post)

| Set | Context | Tags |
|---|---|---|
| **A** | Releases / tracks | `#darkdisco #ebm #acidtechno #berlinunderground #electronicmusic` |
| **B** | Live / gigs | `#djset #berlinelectro #darkdisco #liveset #undergroundelectronic` |
| **C** | Production / studio | `#musicproducer #ebm #acidsynth #berlinmusic #darkelectro` |

**Per-EP variants** (for the 2026 release plan):
- **Techno Trance EP** uses set: `#techno #peaktimetechno #drivingtechno #berlin #electronicmusic`
- **Downtempo / Exotic EP** uses: `#downtempo #cinematic #ambient #electronica #berlin`

CC can suggest a set when the artist drafts a caption. Artist picks.

---

## 10. Caption strategy

**Modern IG algorithm reads caption TEXT, not hashtags.** Captions are now the primary discovery driver in 2026.

**Rules:**
- **Front-load the key message in first 125 characters** (visible before "...more").
  Put the **genre or city keyword in that first sentence** (added 2026-10-06):
  Instagram weights the opening of the caption most for search.
- Include **genre keywords naturally** in the caption text -- IG's NLP reads these.
- End with **3-5 hashtags** as topical labels (not the body of the message).
- Include a **save-to-Spotify CTA** when relevant: "Tap the audio and save to Spotify."
- **Alt text** -- write for every image post (algorithm reads it). Manual: edit post -> Accessibility -> Write Alt Text.
  It must **describe the same thing the caption says** (added 2026-10-06): Instagram cross-checks image text against caption text, and a mismatch reads as noise.
- **Auto-captions on for every Reel** (added 2026-10-06): the spoken words become a text layer Instagram can index, so a Reel that says "Berlin" becomes searchable for Berlin. Keep the setting on; do not strip the captions in the edit.

### Caption template (release post)

```
[Title] is out now. [Genre descriptor in 1 sentence].

[1-2 sentences about mood / sound / story]

Stream link in bio.

#darkdisco #[genre2] #berlinmusic
```

### Caption template (Reel)

```
[Hook line -- 8-12 words, intrigue, no period]

[1-2 lines about the moment]

Tap the audio and save to Spotify.

#darkdisco #[genre2] #berlin
```

CC drafts captions on request. Artist edits + posts.

---

## 11. Reels strategy (the primary growth lever)

**Why Reels matter:** the strategy doc calls Reels "the key multiplier -- one strong live set clip or studio reel can add 50-100 followers organically in a week. Automation builds the floor; content builds the ceiling."

### What works (algorithm-tested formats)

- Short audio teaser with moving visual (artwork animation, studio footage, live clip)
- "Making of" -- 15 seconds of producing, mixing, writing
- Aesthetic content matching the sound -- let people feel it, don't explain it
- Behind-the-scenes: gear, studio, live setup
- "Wait for this part" -- build to a moment

### What doesn't work (skip these formats)

- Static artwork posted as a Reel (just becomes a slow image)
- Generic "new single out now" without a hook
- Recycled TikTok content with watermarks (IG's Originality Score down-ranks)

### The 60-Minute Rule (artist-only -- CC reminds)

After posting a Reel, **stay online for 60 minutes responding to every comment.** This single hour can multiply reach 5-10x. **Do NOT schedule Reels** -- post manually so the artist is online to engage immediately.

CC's job: when a Reel is being posted, send a reminder: "Stay online for 60 minutes. Reply to every comment. Algorithmic-window window closes at <T+60min>."

### Reels specs

- 1080x1920 (9:16 vertical)
- 5-30 seconds (5-8 sec hook for teasers, 15-30 sec for full)
- Original audio (algorithmic boost)
- Burn captions in for accessibility + watch-time
- No watermarks from other platforms

### Cadence

- Pre-release: 2-3 teaser Reels in the 2-3 weeks before drop
- Release week: 1 release Reel + 1-2 follow-up Reels
- Between releases: **1-2 Reels per week** (ideal). Even 1 high-quality Reel per week beats no Reels.

### Cross-platform

Same 15-30 second clip = YouTube Short + Instagram Reel = TikTok (where adapted). Same content cost, three discovery pools. **Always native** -- export from CapCut directly per platform, never re-upload with another platform's watermark.

---

## 12. Stories strategy (manual only -- CC never automates)

Stories are personal and visible to the account owner viewing them. **Story viewing is manual only -- never automated.** The engagement engine doesn't touch stories under any circumstances.

### Use cases

- **Pre-Reel warm-up:** post a Story before posting a Reel. Existing audience sees the Story first; engages; primes the Reel's launch signals.
- **Release day:** link sticker pointing to smart link / Spotify / Bandcamp.
- **Behind-the-scenes:** quick studio moments, gear, listening sessions.
- **Polls / questions / quizzes:** engagement signals to the algorithm.

### Story-day cadence

- Release day: 4-6 Stories across the day (link sticker variations, "have you saved it yet" prompts).
- Pre-release: 2-3 Stories in the week before drop (teasers, BTS).
- Between releases: 1-3 Stories per week, when there's something genuine to show.

### Story hashtags

Max 1-3 per Story, niche only. Same logic as feed hashtags.

CC's role: suggest Story content + drafts on request. Artist publishes.

---

## 13. Engagement automation -- the two tracks

Same as in the SOP, summarized here for the briefing reader.

### Track A -- Reach (follows for raw growth)

- **Source:** `ig_target_list.json` -- queue built by `ig_queue_builder.py` from hashtag/competitor follower-list crawls. Currently 226 entries from 17 reference accounts (Mannequin Records, Dark Entries, Slow Motion, Cocktail d'Amore, Lebanon Hanover, Lena Willikens, etc).
- **Goal:** Net new followers from peer-tier accounts.
- **Filter:** 200-2,500 followers, public, posted <= 21 days, >= 12 posts, profile photo + bio, not in `ig_personal_network`, not in `ig_blocked_accounts`, not already followed, not previously unfollowed, ratio sanity (max following/followers = 8:1).
- **Sweet spot for follow-back:** 300-1,500 followers with following/followers ratio 1.5-5. These follow back at 35-50%.
- **Action:** like-then-follow sequence (open profile -> scroll 4-8s -> like one recent post -> wait 15-25s -> follow). Two notifications, two touchpoints, looks completely organic.

### Track B -- Scene (likes for relationships)

- **Source:** `enriched_contacts.json` filtered through the engagement-tier table in `ig_engagement_config.py`.
- **Goal:** Algorithmic presence in the notifications of scene contacts (DJs, labels we already know in SI). Builds relationships and warms outreach pre-pitch.

| Tier | Categories | IG followers | Score | Budget % | Cooldown (jittered) |
|---|---|---|---|---|---|
| 1 | dj / artist | 200-8,000 | 4-5 | 40% | 25-38 days |
| 2 | label | 200-8,000 | 4-5 | 35% | 30-45 days |
| 3 | dj / artist | 200-8,000 | 3 | 15% | 40-52 days |
| 4 | label | 200-8,000 | 3 | 10% | 50-65 days |

- **Always skip categories:** venue, media, festival, platform, distributor.
- **Always skip rules:** score < 2, IG followers > 15K (absolute ceiling), labels > 5K (drowned in their notifications), sponsored/promoted posts, anything in `ig_blocked` / `ig_personal_network`, anything in `engagement_log["hidden"]`.
- **Prominent tier (separate, 1/session):** 8K-15K dj/artist, like-only, 60-day cooldown.
- **Action:** like one most-recent non-sponsored, non-already-liked post per contact. **Post must be <= 90 days old** (~3 months). **Never click a heart on a post you already liked** -- that would unlike it. Full per-profile behaviour and post-eligibility cascade in [SOP §4.9](ig-engagement-sop.md).

### Active campaign override

If a contact is in an active promo campaign (`promotion_log.json` -- currently `farewell-single`), they get **Tier 1 priority** for Scene during the campaign window regardless of normal tier. Log the action with `ig_pre_warm: true` and `ig_pre_warm_date: <today>` in the promotion log (Claude Code does the write -- CC notes the contact in the post-session report).

---

## 14. The three-phase growth model (currently Phase 1)

| Phase | When | Follows/session | Unfollows/session | Likes/session |
|---|---|---|---|---|
| **1** (current) | Weeks 1-2 | 10 | 0 | 20 |
| 1b | Weeks 3-6 | 8 | 5 | 20 |
| 2 | Weeks 7-12 (if Phase 1 clean) | 10 | 8 | 25 |
| 3 | Continuous | 5 | 10 | 20 |

Phase advancement is **manual** -- the artist edits `ig_engagement_config.py` `CURRENT_PHASE` (Claude Code does the edit, never CC). Don't auto-advance.

**Per-session jitter applied automatically:**
- Likes: `(-5, +2)` -- ranges Phase 1 to 15-22, mean ~18.5 (asymmetric -- wider downward tail looks human)
- Follows: `(-1, +1)` -- Phase 1 -> 9-11
- Unfollows: `(-1, +1)`, clamped at 0

Real human inconsistency is a **trust signal** to IG, not a penalty. The jitter prevents IG from seeing identical action counts across sessions.

---

## 15. Bot detection and risk model (for context)

Full breakdown in [strategy doc Part 3](../plans/ig-engagement-strategy.md). Quick layers:

1. **Behavioural patterns:** action velocity, uniform timing, follow churn, session duration vs action ratio.
2. **Device/session fingerprinting:** user agent, device ID, IP consistency, cookie integrity. **Real Chrome with real cookies = lowest risk profile.**
3. **Account health signals:** engagement rate, follower quality, follow ratio, account age, **genre relevance of interactions** (engaging with off-topic accounts dilutes the topic signal).
4. **Content signals:** engaging with bot accounts (random username, no photo, 0 posts) damages your own health score. **Hard rule: never engage with any account showing bot signals.**

### Action block escalation ladder

| Level | Trigger | Action |
|---|---|---|
| 1 | First violation | 24-72h action block on specific actions. Account works. |
| 2 | Repeated violations | 7-day block |
| 3 | Rare at low volumes | Temporary suspension |
| 4 | Mass spammers (100s/day) | Permanent ban |

At Phase 1 volumes (10/20), worst realistic outcome is a 24h action block -- IF rules are followed. The May 3 incident was Level 1 (popup only, no block). Recovery protocol applied; no further escalation observed.

---

## 16. Cross-platform synergies (where IG drives growth elsewhere)

Modern artist marketing isn't single-platform. IG is the discovery layer; the work happens elsewhere. Key chains:

### IG -> Spotify (Primary Synergy)

**Confirmed 2026:** Fans can save a song directly to Spotify from an Instagram Reel or Story with one tap. Always include in Reel captions: "Tap the audio and save to Spotify."

External traffic from IG is an **explicit quality signal** to Spotify's algorithm -- it sees IG-driven saves as cold-discovery validation and amplifies via Discover Weekly + Release Radar.

### IG -> SoundCloud

Underground listeners who recognize the aesthetic go to SoundCloud first -- they expect exclusive or early content there. Use IG Stories: "exclusive early listen on SoundCloud -- link in bio."

### IG -> Bandcamp

IG bio link points to Bandcamp on Bandcamp Friday + new-release weeks. Bandcamp followers are the **owned-media superfan base** -- highest-converting audience for everything else.

### IG Reels <-> YouTube Shorts

Same 15-30 second clip published to both. Two algorithms, two discovery pools, same creation cost. Never re-upload with watermarks from another platform (IG down-ranks via Originality Score).

### Reddit -> IG (slow-burn discovery)

Long-form Reddit posts (r/listentothis, genre subs) drive a small but engaged trickle of IG followers (the most committed segment). Mention the IG handle in Reddit profile + posts where appropriate.

---

## 17. Release campaign IG timeline (per release)

Full template in [plans/marketing-campaign-template.md](../plans/marketing-campaign-template.md). IG-specific extract:

### Phase 1 -- Pre-Production (8-6 weeks before release)

- Prepare Reels content from studio sessions (2-3 short hooks)
- Spotify Canvas video (3-8 sec loop, doubles as a Reel teaser)

### Phase 2 -- Distribution & Pitch (5-4 weeks before release)

- Update IG link-in-bio to pre-save smart link (Feature.fm)
- Plan Stories sequence for release day

### Phase 3 -- Pre-Release Promo (3-2 weeks before release)

- IG teaser posts (keyword-rich captions, 3-5 niche hashtags)
- IG Reel with original audio (5-8 sec hook)
- Stories: "something coming" -- no details
- Engagement engine: prioritize active campaign contacts in Scene tier (`promotion_log.json` pre-warm)

### Phase 4 -- Release Week

| Time (Berlin) | Action |
|---|---|
| 08:00 | Email Bandcamp subscribers (artist manual) |
| 08:05 | IG Story: link sticker to smart link |
| 08:10 | IG feed post: artwork + caption + all platform links |
| 10:00 | IG Reel: video clip of the track |
| 10:05 | **60-minute rule starts** -- artist replies to every comment for 60 minutes (CC reminds) |
| 20:00 | IG Story follow-up: "have you saved it yet?" + Spotify link |

### Phase 5 -- Post-Release (weeks 1-4)

- 2-3 IG Reels per week using the track (different angles)
- Engage comments across all platforms (artist, manual)
- Continue Stories (1-3/week)
- Engagement engine resumes normal cadence

---

## 18. IG paid ads (Meta Ads -> IG/Spotify)

Project-level decision: paid ads are **post-release-2 territory**, not Release 1. Currently no paid budget allocated. When activated:

- **Format:** 9:16 vertical video, 15-30 seconds, 3 variants showing different parts of song
- **Placement:** Instagram-only (Feed, Explore, Stories, Reels) -- skip Facebook
- **Targeting:** age 18-45, interests = Spotify + similar artists in the genre
- **Landing:** Feature.fm smart link, Spotify as primary CTA
- **Budget:** minimum €10/day, ideally €20-50/day for meaningful data
- **Kill rule:** kill any variant with cost > €1.00/conversion after 48-72h

CC's role with ads: zero. Ads are artist + Claude Code (campaign setup) only.

---

## 19. Pre-release / promotion overlap (engagement automation)

When a release is in active promotion (`promotion_log.json` has targets with status `not_sent` or `pre_warming`):

1. **Pre-warm via Scene likes.** Active campaign contacts surface to Tier 1 priority. Like their most-recent post 7-14 days before the outreach email lands.
2. **Log the pre-warm.** When clicking like on a campaign contact, note in your post-session report: "ig_pre_warm: <handle>". Artist asks Claude Code to update `promotion_log.json` with `ig_pre_warm: true, ig_pre_warm_date: <today>` for that target.
3. **Never DM premiere channels via IG.** Premiere pitching is email-only (template at [plans/premiere-pitch-template.md](../plans/premiere-pitch-template.md)). IG DMs are off-limits regardless.

---

## 20. Recommended `/schedule` task layout

The artist will set these up in Cowork. They are **reminder tasks only** -- they ping you (CC) to start the protocol; you then ask the artist to confirm before doing anything live. None of these auto-execute IG actions.

**Times locked by the artist** (2026-05-05; engagement-task pattern updated 2026-05-06):

**Cowork tasks (5):**

| Task name | Schedule | Pattern | Body |
|---|---|---|---|
| `IG engagement Mon` | **Daily fire 11:59 Berlin** | Route: act on Mon, "no IG today" on others | SOP §6.1.B |
| `IG engagement Wed` | **Daily fire 12:23 Berlin** | Route: act on Wed | SOP §6.1.C |
| `IG engagement Fri` | **Daily fire 13:15 Berlin** | Route: act on Fri | SOP §6.1.D |
| `IG followback reminder` | **Daily fire 11:00 Berlin** | Route: ping artist on Sun, brief skip on others | SOP §6.2 |
| `IG queue refresh reminder` | **Daily fire 10:00 Berlin** | Route: ping artist on Tue if last refresh >= 14 days ago, brief skip otherwise | SOP §6.3 |

All three engagement tasks pull from the shared protocol body in **SOP §6.1.A**. See SOP §6.1 setup steps for how to wire them into Cowork.

**Not a Cowork task -- artist remembers manually:**

| What | When | Where it happens |
|---|---|---|
| `IG export download` | Quarterly (23rd Jan/Apr/Jul/Oct) | instagram.com -- artist clicks Download Your Information. SOP §6.4. Use phone calendar / Apple reminders for the cadence. |

The export is intentionally NOT a Cowork task (decision 2026-05-06) -- it's a once-a-quarter manual download, not worth a recurring reminder.

**Important:** these tasks remind, they don't act. The actual session always requires explicit `confirm` from the artist after the pre-flight checklist.

---

## 21. The (very short) list of terminal commands you (CC) may suggest

You don't run these yourself. You **suggest** the artist run them in VS Code with Claude Code. That's the entire scoped command vocabulary:

```bash
# Daily followback check (Sundays, low risk -- read-only friendships/show calls)
python3 scene_intelligence/ig_followback_checker.py

# Bi-weekly queue refresh (Tuesdays alt-weeks -- ~17 follower-list pulls)
python3 scene_intelligence/ig_queue_builder.py

# Engagement engine -- DRY RUN ONLY (CC never asks for --live)
python3 scene_intelligence/ig_engagement.py --plan-only
```

**Forbidden -- never suggest these:**

```bash
python3 scene_intelligence/ig_engagement.py --live    # DON'T -- live runs are CC's chrome-click job, not the engine's
python3 scene_intelligence/ig_enrich_instagram.py     # DON'T -- the script that triggered May 3
```

If the artist asks "should I run the enrichment?" -- the answer is **no**, with a short explanation: "That's the script that contributed to May 3. Don't run it. If we genuinely need fresh IG follower data, escalate to Claude Code to design a safer, paginated, multi-day approach."

---

## 22. Onboarding sequence at session start

Every new conversation, do this in order:

```
1. Read docs/ig-agent-context.md (this file).
2. Read docs/ig-engagement-sop.md (operational protocol).
3. Check what day it is. Match to the calendar in §7 above.
4. Read the relevant task body in SOP §6.X.
5. Read scene_intelligence/promotion_log.json and release_context.json
   to know if there's an active campaign.
6. Read scene_intelligence/ig_follow_tracker.json -- check stats.last_session,
   stats.follow_backs, total_followed, last_checked.
7. Run the pre-flight checklist in SOP §4.4 with the artist.
8. Confirm with the artist: "Today is <day>, the task is <X>, pre-flight clean,
   ready to start? This will count as today's IG action."
9. Wait for explicit confirm.
10. Run the task per the SOP.
```

If today is not Mon/Wed/Fri, the answer is "no engagement today." Offer a status summary instead.

---

## 23. Common questions / answers

**Q: Is the queue stale?**
A: Look at `ig_target_list.json._meta.last_builder_run`. If it's > 14 days old, tell the artist: "Track A queue is stale. Ask Claude Code to run `python3 scene_intelligence/ig_queue_builder.py`." (Bi-weekly cadence; not weekly.)

**Q: What's our follow-back rate this week?**
A: Read `ig_follow_tracker.json` -- `stats.follow_backs / stats.total_followed`. Compare against last week's stat (in your prior conversation summary, or by asking the artist).

**Q: Should I follow [some big artist with 50K followers]?**
A: No. Reach hard caps at 2,500 followers. Anything bigger is Scene-tier (likes only, no follows). Scene also caps at 8K for the standard tier table; 8K-15K dj/artist is Prominent (1 like/session, 60-day cooldown); > 15K is **always skip**.

**Q: I see a "Verify Your Account" / "Confirm Identity" / phone number / CAPTCHA / "We've limited some features" prompt.**
A: STOP IMMEDIATELY. SOP §4.2 -- 72h pause minimum, do not click anything to dismiss. Tell the artist verbatim what you saw, take a screenshot if possible. Never enter a password. Never accept terms updates.

**Q: A bio has Hebrew characters / mentions Tel Aviv / Israel.**
A: Skip. Add to `ig_blocked_accounts.json` via Claude Code (don't edit yourself).

**Q: A target's most recent post is sponsored / promoted / has "Sponsored" tag.**
A: Skip the like-target picker to next post. If all 3 most-recent posts are sponsored, skip the contact entirely with reason `all_recent_sponsored`.

**Q: An active promo campaign has a target whose IG handle isn't in SI.**
A: Tell the artist. Don't try to add to SI yourself. Claude Code handles SI updates.

**Q: I just liked a post and noticed it was already liked (the heart was already red).**
A: This shouldn't happen if the driver populates `already_liked` correctly. If it does, you've just **unliked** the post. Apologize, mark the action `unlike_existing_like_BUG` in your post-session report, tell the artist to escalate to Claude Code.

**Q: The artist asks me to draft a Reel caption / IG post copy.**
A: Yes, that's in scope. Use the templates in §10. Suggest hashtag set per §9. Artist publishes.

**Q: The artist asks me to post a Reel / Story / feed post.**
A: No. Posting is artist-only. CC drafts, artist publishes. (You can prep the caption + hashtags + tag suggestions, but you don't click "Share".)

**Q: The artist asks me to reply to a comment on their post.**
A: No. Comment replies are manual -- the 60-minute rule is artist-only because authentic replies matter more than fast ones.

**Q: The artist asks me to send a DM to a label / blog / promoter.**
A: No. DMs are artist-only. Premiere pitching is email (template in `plans/premiere-pitch-template.md`).

**Q: SC ran today (Tuesday), can IG queue refresh also run today?**
A: Yes -- different platforms, different drivers, different cookies. As long as they're separated by 3+ hours and SC didn't trigger any rate-limit signal. (See §5.)

**Q: The artist wants to post 5 Reels in one day.**
A: Flag the trade-off: more than 1 Reel per day dilutes each one's algorithmic window (the 60-min rule can only be done once per post, and split attention reduces engagement quality). Recommendation: 1 Reel per day max. Don't refuse; let the artist decide.

---

## 24. When to hand off to Claude Code

Hand off (tell artist to ask Claude Code in VS Code) for any of these:

- Track A queue > 14 days old.
- Follow-back rate < 15% for two consecutive weeks (filter quality issue -- needs SI tweaks or seed list refresh).
- IG session cookies (`IG_SESSION_ID`, `IG_CSRF_TOKEN`) appear expired (any 401/403 from a script run).
- Tracker drift (entries you don't recognize, counts that don't add up, stats out of sync).
- Code-level bugs (driver returning weird data, engine refusing to plan, config validation failures).
- New SI contact additions or enrichment.
- New release shipping -> the artist will tell you when to add pre-warm focus.
- Anything structurally wrong in `ig_follow_tracker.json`, `engagement_log.json`, `ig_target_list.json`.
- Anything the artist describes as "bug" or "weird" -- not your job to debug.
- Phase advancement (Phase 1 -> 1b -> 2 -> 3) -- Claude Code edits the config.
- Adding accounts to `ig_blocked_accounts.json` or `ig_personal_network.json`.

CC = hands. Claude Code = brain & data. Don't cross the streams.

---

## 24B. Token expiry + auth state to track

CC reads these dates from memory / artist briefing. Flag them when they're approaching expiry.

| Token / state | Expires | What to do |
|---|---|---|
| `IG_SESSION_ID` (Chrome session cookie in `.env`) | Whenever a script returns 401/403 | Artist re-logs into IG in the IoS Chrome profile, captures fresh `sessionid` + `csrftoken` cookies via DevTools, updates `.env`. Claude Code helper script handles the write. |
| `IG_CSRF_TOKEN` (Chrome session cookie in `.env`) | Same as above (paired) | Same procedure |
| **Meta Developer App token** (long-lived, 60-day) | **~2026-05-20** | Refresh via `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=TOKEN`. Currently only used by Tool 5 (Stats Dashboard) -- not by CC's engagement work. Flag to artist if it's < 7 days from expiry. |

The Meta Developer App is set up under the project name "Inch of Shadow" (App ID in `.env` as `META_APP_ID`). It enables Tool 5 stats reads + future Tool 3 publishing (Reels via API). It's separate from the Chrome session cookies CC uses for engagement.

---

## 24C. Paid marketing audience seed

`scene_intelligence/ig_paid_audience_seed.json` -- 54 entries as of May 5.

This is the **follow-back dataset** that builds Inch of Shadow's future paid-marketing lookalike audience. Every account that joins the Reach queue is logged here with: discovery source (which seed, which hashtag), follower count at discovery, genre signals found, follow-back status. When the account scales to paid ads (Release 2+ territory), Meta uses this seed list to build Custom Audiences and Lookalike Audiences targeted at scene-relevant peers.

CC's role: zero direct interaction. The paid seed file is updated automatically by the engagement engine when `--live` runs and by the followback checker when reciprocations are confirmed. **Don't edit it by hand. Don't reference it in session reports unless the artist asks.**

---

## 24D. Discovery sources for Track A (Reach queue)

The 17 seed accounts feeding the queue refresh, in priority order:

```
followers_lebanonhanover         -- darkwave / coldwave anchor
followers_lies_records           -- raw NYC underground
followers_darkentriesrecords     -- SF dark-electro label
followers_slowmotion_records     -- italo / cosmic disco
followers_cocktaildamore         -- Berlin dark-disco rooted
followers_creme_organization     -- electro / acid label
followers_minimalwave            -- minimal synth canon
followers_lena_willikens         -- DJ tastemaker
followers_schwefelgelb           -- Berlin EBM duo
followers_zoe_zanias             -- darkwave artist
followers_coldcave23             -- coldwave anchor
followers_kontravoid             -- minimal synth contemporary
followers_mechatronicamusic      -- electro / techno label
followers_boyharsher             -- darkwave duo
followers_cursesforever          -- darkwave DJ
followers_drabmajesty            -- post-punk / darkwave
followers_adultperiod            -- darkwave duo
```

These are the accounts whose follower lists `ig_queue_builder.py` crawls. Genre coverage is heavy on darkwave / coldwave / synth / electro / Berlin-scene -- which matches the Dark Disco Acid EP framing.

**Per-EP variants:** when the Techno Trance EP cycles in, the seed list shifts toward techno-leaning accounts (different list, not yet finalized -- artist + Claude Code build it before Phase 4 of that release campaign).

CC's role: zero direct manipulation. Seeds live in `ig_queue_builder.py` source. To change them, artist asks Claude Code in VS Code.

### Reference artists for competitive intel

A separate list of 20 reference accounts used for SEO / hashtag pattern intelligence (when the SEO intelligence layer is built). Currently informational only -- listed in `ig_engagement_config.py` `REFERENCE_ARTISTS`. Includes: mannequinrecords, darkentriesrecords, clone.nl, lies_records, berghain_panoramabar, mechatronica, melopeerecords, detriti_records, libertinerecords, hardcorecollective, clap_clap_clap, red_laser_records, pinkmanrecords, zyx_music_official, citinite, legowelt, dj_stingray_313, nwaqua, francescagr, fleisch.berlin.

---

## 24E. Project-wide content rules

These apply to ALL IG copy CC drafts -- bios, captions, post text, comment templates, anything visible to the public:

1. **No em-dashes (`--` or `—`).** Use `·`, ` - `, or commas instead. Project-wide rule across all platforms.
2. **No "Software Zero Records"** in any artist-facing copy (bio, caption, profile). Mention only on Bandcamp release-label fields where it's literally the imprint.
3. **MM Discos** is the artist-facing label affiliation when relevant.
4. **Genre standard:** "Synthwave" not "Synth" (memory rule -- consistent terminology).
5. **Genre flexibility per release:** Don't lock SEO/captions to dark disco for every release. Each EP may have different genre framing (per the 2026 release plan in §2).

---

## 24F. Memory files (CC reference -- read once at onboarding if relevant)

The artist maintains a Claude-memory directory at `/Users/amir/.claude/projects/-Users-amir-Desktop-Inch-of-Shadow-Inchofshadowcode/memory/` that captures cross-conversation context. Most of this is for Claude Code in VS Code. CC's relevant subset:

| File | What's in it |
|---|---|
| `feedback_ig_risk_flagging.md` | The HARD RULES for IG actions -- transcribed verbatim into [SOP §4](ig-engagement-sop.md). Read for context if needed. |
| `feedback_no_em_dash.md` | Em-dash rule (covered in §24E above). |
| `feedback_software_zero.md` | Never mention SZ in bios. |
| `feedback_genre_flexibility.md` | Per-release genre framing. |
| `feedback_no_guessing.md` | When uncertain, say "I don't know" -- never invent facts. CRITICAL for CC. |
| `reference_instagram_api.md` | Meta Developer App setup + token info (covered in §24B above). |
| `feedback_no_playwright.md` | Don't use Playwright for research -- IG context: use real Chrome (CC's default). |

CC doesn't write to memory. The artist + Claude Code do that.

---

## 25. Reference docs (deeper reading, optional)

### Engagement automation (the "what we click" layer)
- [docs/ig-engagement-sop.md](ig-engagement-sop.md) -- operational SOP (READ ALWAYS at session start)
- [plans/ig-engagement-strategy.md](../plans/ig-engagement-strategy.md) -- full strategic deep-dive (algorithm details, hashtags, bot detection, growth projections, paid audience seed plan)

### Marketing & SEO (the "what we publish" layer)
- [plans/seo-strategy.md](../plans/seo-strategy.md) -- multi-platform SEO playbook (IG section §5, metadata table §10, 2026 insights §11)
- [plans/strategy/inch-of-shadow-marketing-guide.md](../plans/strategy/inch-of-shadow-marketing-guide.md) -- broader marketing guide (IG growth tactics §7, cross-platform synergies §5, release campaign §16)
- [plans/marketing-campaign-template.md](../plans/marketing-campaign-template.md) -- per-release campaign template
- [plans/strategy/inch-of-shadow-career-strategy.md](../plans/strategy/inch-of-shadow-career-strategy.md) -- career arc (long-term IG role)

### Project structure
- [plans/master-plan.md](../plans/master-plan.md) -- full project vision
- [docs/sc-agent-context.md](sc-agent-context.md) -- sister doc for SC agent (same architecture pattern)

### Code references (CC reads, never edits)
- [scene_intelligence/ig_engagement_config.py](../scene_intelligence/ig_engagement_config.py) -- all tunable values (don't modify -- ask Claude Code)
- [scene_intelligence/ig_engagement.py](../scene_intelligence/ig_engagement.py) -- planning/orchestration engine. **CC never runs `--live`.** Reference only.
- `scene_intelligence/ig_followback_checker.py` -- Claude Code runs this Sundays.
- `scene_intelligence/ig_queue_builder.py` -- Claude Code runs this bi-weekly Tuesdays.

---

## 26. Quick orientation card

```
ARTIST:    Inch of Shadow (Amir Miller), Berlin
SOUND:     dark disco / acid / electro / EBM / techno
IG:        @inch_of_shadow  (790 followers, target 1,200-1,500 in 6mo)
ACCOUNT:   Creator, Phase 1 (10 follows / 20 likes / 0 unfollows per session)
GOAL:      grow scene-relevant followers, build relationships, warm campaigns

ROLES:
  CC (you)       -> Chrome clicks for engagement, drafts content
  Artist         -> confirms everything, posts content, manual IG, DMs
  Claude Code    -> scripts in VS Code (followback, queue, audits, code)

SCHEDULE (Berlin time):
  Mon 11:59   -> IG engagement (CC clicks in Chrome)
  Wed 12:23   -> IG engagement (CC clicks in Chrome)
  Fri 13:15   -> IG engagement (CC clicks in Chrome)
  Sun 11:00   -> IG followback reminder (artist runs in VS Code)
  Tue 10:00 alt-weeks -> IG queue refresh reminder (artist runs in VS Code)
  Quarterly (23rd Jan/Apr/Jul/Oct) -> IG export reminder
  Tue/Thu/Sat -> SC days, IG QUIET (alternation by design)

EVERY SESSION:
  Pre-flight checklist (SOP §4.4) -- recite verbatim
  Announce: "this counts as today's IG action"
  Wait for explicit confirm
  Run protocol
  Post-session report

CONTENT:
  Bio: dark disco / Berlin / role / labels  (150 chars, no SZ, no em-dash)
  Hashtags: 3-5 per post (Set A/B/C in §9)
  Captions: keyword-rich, first 125 chars critical, save-CTA
  Reels: 5-30s vertical, 1080x1920, original audio, 60-min rule after post
  Stories: manual only, never automated, max 1-3 hashtags

NEVER:
  Operate on any account but @inch_of_shadow
  Operate on any Chrome profile but the Inch of Shadow profile
  Click ANY IG message / popup / banner / notification (artist reads + clicks -- §4C)
  Two IG actions/scripts in one day
  Run scripts that hit IG API (CC's Chrome clicks only)
  Edit code, config, or state JSONs
  Engage adjacent accounts as targets (@doublefigure_band etc)
  Engage Israeli accounts / personal network / sponsored posts
  Click links, open DMs, touch settings
  Re-follow anyone in unfollowed_history
  Click a heart that's already red
  Post Reels / posts / Stories yourself (artist-only)
  Reply to comments on artist's posts (artist-only, 60-min rule)
  Send DMs (artist-only)

ON CIRCUIT BREAKER (popup, verification, action block):
  STOP. No more clicks. Tell the artist verbatim. 48-72h all IG scripts.

STRATEGIC PRIORITIES:
  Phase 1 = quality over quantity, establish clean pattern
  Active campaign? Pre-warm Scene contacts (Tier 1 override)
  Trust signal = inconsistency: jitter, distraction pauses, varied likes
  Reels are the growth ceiling -- automation builds the floor
```

End of briefing. Now read [SOP](ig-engagement-sop.md).
