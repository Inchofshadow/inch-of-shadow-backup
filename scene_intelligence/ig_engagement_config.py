"""
ig_engagement_config.py — Inch of Shadow IG Automation
All tunable values live here. Edit this file to change behaviour without touching the engine.
Last updated: 2026-04-23
"""

# ---------------------------------------------------------------------------
# SESSION SCHEDULE
# ---------------------------------------------------------------------------

# Mon/Wed/Fri/Sat since the 2026-06-01 cadence update (SOP §6.1: unified
# 11:00 Berlin fire, Saturday replaced Sunday). This line was stale at 3 days
# until 2026-07-19 — Amir caught it.
SESSION_DAYS = ["Monday", "Wednesday", "Friday", "Saturday"]  # Berlin local time
SESSION_HOUR_START = 15   # 15:00 Berlin — settled 2026-08-27 (Amir; after briefly picking 20:00 the same day). Clear of SC's 11:30 sessions (3.5h start-to-start), daytime hours, no evening-life conflicts. Was 11:00 before 2026-08-27.
SESSION_HOUR_END = 16     # target finish; the close-loops task merges after (staleness-gated)
SESSION_MAX_MINUTES = 50  # Hard cap — engine stops regardless of queue state. 35 -> 50 (2026-05-11); 50 -> 60 (2026-07-02, Phase 2) reverted -> 50 (2026-07-04) with the Phase 2 rollback. CAVEAT: this only binds the engine; CC runs manually and IGNORED it on 07-04 (ran ~90 min, which triggered grid rate-limiting). The real overrun fix is CC session discipline + a queue that yields fast, not this value.

# ---------------------------------------------------------------------------
# PHASE CONFIGURATION
# Current phase is set here. Change to advance phases manually.
# ---------------------------------------------------------------------------

CURRENT_PHASE = 2  # ATTRIBUTION RECIPE (Amir approved 2026-09-01): conversion gate passed (38% verified cohort, 19% in-window vs >=15% KPI) -> volume goes to the action that produces followers. Was "1b".  # Stepped down from Phase 2 on 2026-08-19 citing an IG automation warning that Amir confirmed on 2026-08-25 NEVER HAPPENED (fabricated record, since deleted). The downgrade's justification is void; restoring Phase 2 (10F/8U/25L) awaits Amir's explicit go.

# Per-session jitter applied to every phase limit at session start.
# Real humans don't engage exactly the same count every time. Each session
# rolls an int in [lo, hi] and adds to the base. Minimum clamped at 0.
#
# Asymmetric on likes: wider downward (-5) than upward (+2). Rationale:
#   - Never exceeds the strategy doc's "safe" 20 likes/session by more than 2
#   - Allows low-engagement days (15) which match actual human behaviour --
#     inconsistency is a TRUST signal for IG, not a penalty
#   - 8 possible values (15-22) gives more anti-pattern variance than ±2
SESSION_JITTER = {
    "likes_per_session":    (-2, 2),  # narrowed 2026-09-01 for the 6-like budget (was -5,+2 for 20)
    "follows_per_session":  (-1, 1),
    "unfollows_per_session":(-1, 1),
}

PHASE_LIMITS = {
    1: {
        "label": "Phase 1 — establishing pattern (weeks 1-2: follows only)",
        "follows_per_session": 10,
        "unfollows_per_session": 0,   # Set to 5 after week 2
        "likes_per_session": 20,
    },
    "1b": {
        "label": "Phase 1b — active growth (weeks 3-6)",
        "follows_per_session": 8,
        "unfollows_per_session": 7,  # Restored 2026-08-23 for the Monday 2026-08-24 full resume (was temporarily 0 for the Fri 08-21 light restart after the 08-19 detection warning). Prior note 2026-08-20 -> RESTORE TO 7 after the Friday 2026-08-21 resume session. Set to 0 so the first session back after the 2026-08-19 detection warning needs NO follow-back checker run (the checker only guards the unfollow sweep), keeping the 7-day script count from climbing further. Restore to 7 on Monday 2026-08-24 when the rolling window has decayed to ~1. Prior/renewed 2026-07-13 (was paused 2026-07-06 through The Deceiver release on 2026-07-10). Prior/normal value = 7 (bumped 5->7 on 2026-05-11 to clear the overdue backlog).
        "likes_per_session": 20,
    },
    2: {
        "label": "Phase 2 — attribution recipe (2026-09-01): follows are the engine (8.6 followers/hr, 61 of 176 gained), scene likes warm promo only (0 of 235 liked contacts converted in 6 months)",
        "follows_per_session": 16,    # 2026-11-04 Amir "Yes, run it": 12->16 (HikerAPI follow-back check M-13). RESTORED 2026-10-12 (Amir "you can stop pause the follows"); was 0. Prior note: PAUSED 2026-09-26 (Amir "ok"): 35 follows since 09-16, 0 follow-backs, 60 non-reciprocators stuck behind the export gate -> ratio went ~20 negative. Restore to 12 once the ALL-TIME export unblocks the sweep AND the provider is topped up (real candidates again). Export landed 2026-10-10; the sweep ran 10-11. Vetted pool was 0 at restore time, so follows come from in-browser vets until a queue build runs.
        "unfollows_per_session": 8,   # 2026-11-04 Amir: 15->8 (temp 15 ended). Was: TEMP 2026-10-09 to 2026-10-16 (Amir "15"): clear the 53 non-reciprocators faster; the scorer cap follows this value. REVERT TO 8 on 2026-10-16. Unfollows still only via the live "Follows you" check.
        "likes_per_session": 12,      # 2026-11-04 Amir: 6->12. T1/T2 relationship warming only
    },
    3: {
        "label": "Phase 3 — continuous cleanup",
        "follows_per_session": 5,
        "unfollows_per_session": 10,  # Continuous gentle cleanup
        "likes_per_session": 20,
    },
}

# ---------------------------------------------------------------------------
# TIMING (seconds) — non-uniform, human-like
# Engine uses weighted random within these ranges.
# Peaks around 15-18 seconds. Occasional longer pauses every 4-6 actions.
# ---------------------------------------------------------------------------

TIMING = {
    "between_likes": (12, 20),          # seconds min/max
    "between_like_and_follow": (18, 30),
    "between_follows": (25, 45),
    "profile_open_to_action": (4, 8),   # scroll time before acting
    "after_scroll_before_act": (2, 4),
    "distraction_pause": (30, 60),      # fires every 4-6 actions
    "distraction_every_n_actions": (4, 6),
    "like_before_follow_wait": (15, 25),  # wait between like and follow on same profile
}

# Profile scroll duration by action type (seconds)
SCROLL_DURATION = {
    "assess_only": (3, 5),   # just checking the profile, not acting
    "before_like": (4, 6),
    "before_follow": (6, 8),
}

# ---------------------------------------------------------------------------
# TRACK A — FOLLOW / UNFOLLOW RULES
# ---------------------------------------------------------------------------

REACH = {
    # Target follower count range (peer tier only)
    "min_followers": 200,
    "max_followers": 2500,

    # Follow-back sweet spot (prioritise these in the queue)
    "sweet_spot_min_followers": 300,
    "sweet_spot_max_followers": 1500,
    "sweet_spot_min_following_ratio": 1.5,  # following/followers >= this = high follow-back likelihood
    "sweet_spot_max_following_ratio": 5.0,  # following/followers <= this = not a pure bot

    # Hard rejection rules
    "max_following_count": 5000,          # accounts following more than this = skip
    "max_following_followers_ratio": 8.0, # following/followers > 8 = mass-follow bot pattern
    "min_posts": 12,
    "max_post_recency_days": 60,          # 60 since 2026-09-11 (Amir: "two months is fine for a post"; was 30). Must have posted within this window. Loosened from 21 -> 30 on 2026-05-12 after the audit-via-API approach hit a limitation (web_profile_info doesn't return post data for unfollowed accounts). Slightly looser filter = fewer stale skips at runtime; small trade-off in follow-back rate. Can tighten back to 21 if queue-builder gets last_post_date capture in a future sprint.
    "min_engagement_rate": 0.005,         # 0.5% minimum — below this = dead or bought followers
    "require_profile_photo": True,
    "require_bio_text": True,             # min 5 characters
    "require_public_account": True,       # private accounts = skip (cannot verify genre)
    "skip_verified_accounts": True,       # blue badge = brand/celebrity, skip for follows
    "skip_all_repost_accounts": True,     # aggregators, not real people
    "skip_zero_engagement_posts": True,   # 0-2 likes on most recent 3 posts = ghost/bot

    # 7-day unfollow rule
    "unfollow_after_days": 7,
    "never_retry_unfollowed": True,       # once unfollowed, never re-follow
}

# ---------------------------------------------------------------------------
# TRACK B — ENGAGEMENT TIER TABLE
# Edit budget_pct values to shift focus. Must sum to 1.0.
# Engine validates this on startup.
# ---------------------------------------------------------------------------

ENGAGEMENT_TIERS = [
    {
        "tier": 1,
        "label": "Core scene DJs — high priority",
        "categories": ["dj", "artist"],
        "min_ig_followers": 200,
        "max_ig_followers": 8000,
        "min_score": 4,
        "max_score": 5,
        "budget_pct": 0.65,        # 2026-09-01 attribution recipe: T1/T2 only (breadth likes produced 0 followers)
        "cooldown_days_min": 25,
        "cooldown_days_max": 38,
    },
    {
        "tier": 2,
        "label": "Labels + scene press — warming priority",
        "categories": ["label", "media", "promoter"],  # media/promoter enter ONLY via SCENE_PRESS_EXCEPTION (score>=4, <=8K); the always-skip still blocks the rest
        "min_ig_followers": 200,
        "max_ig_followers": 8000,  # raised from 2000 — all 16 score 4-5 labels are in 2K-8K range
        "min_score": 4,
        "max_score": 5,
        "budget_pct": 0.35,
        "cooldown_days_min": 30,
        "cooldown_days_max": 45,
    },
    {
        "tier": 3,
        "label": "Score 2-3 DJs — discovery breadth",
        "categories": ["dj", "artist"],
        "min_ig_followers": 200,
        "max_ig_followers": 8000,
        "min_score": 2,            # lowered 3->2 on 2026-06-15 (Amir: engage score >1 for breadth)
        "max_score": 3,
        "budget_pct": 0.0,         # 2026-09-01: retired from likes — 0 followers, weak warmth value
        "cooldown_days_min": 40,
        "cooldown_days_max": 52,
    },
    {
        "tier": 4,
        "label": "Score 2-3 labels — low frequency",
        "categories": ["label"],
        "min_ig_followers": 200,
        "max_ig_followers": 8000,
        "min_score": 2,            # lowered 3->2 on 2026-06-15 (Amir: engage score >1 for breadth)
        "max_score": 3,
        "budget_pct": 0.0,         # 2026-09-01: retired from likes
        "cooldown_days_min": 50,
        "cooldown_days_max": 65,
    },
]
# Budget check: 0.65 + 0.35 + 0.0 + 0.0 = 1.00 ✓ (attribution recipe 2026-09-01)
# Rationale for label ceiling raise: all score 4-5 labels in SI have 2K-8K followers.
# These are still human-managed accounts where one person sees notifications.
# Original 2K ceiling was set before enrichment data existed.

# Occasional engagement with prominent accounts (not part of tier budget)
PROMINENT_TIER = {
    "min_ig_followers": 8000,
    "max_ig_followers": 15000,
    "likes_per_session_max": 1,     # max 1 post liked
    "cooldown_days": 60,
    "enabled": True,
}

# Scene-track category cap: maximum fraction of session likes that may go to
# the "label" category. Tiers select on follower count, which heavily favors
# labels (they have more followers than most DJs in this scene), producing
# label-heavy sessions (e.g. 17/20 on 2026-05-23). This rebalance happens
# post-selection in select_scene -- excess labels get swapped for available
# non-label entries (DJs / artists / etc.). 1.0 = no cap (legacy).
# Set to 0.3 (70% DJ / 30% label) by Amir on 2026-05-23 -- peer-networking
# emphasis, follow-backs are the day-to-day growth lever at this stage.
MAX_LABEL_LIKE_RATIO = 0.3

# ---------------------------------------------------------------------------
# TRACK B — ALWAYS SKIP (regardless of tier)
# ---------------------------------------------------------------------------

ALWAYS_SKIP_CATEGORIES = [
    "venue",          # posts event graphics, wrong topic signal
    "media",          # RA, FACT, Mixmag etc — invisible in notifications
    "festival",       # corporate
    "platform",       # Beatport official, Traxsource official etc
    "distributor",    # no human reads it
]

# SCENE-PRESS EXCEPTION (2026-09-01, Amir): the blanket "media" skip treated
# a 2-person scene radio like Mixmag — blankwave.wav sat in SI at score 5,
# permanently banned. Small human-run press/radio/zine/promoter pages are
# premiere and support channels (warmed outreach converted 33% vs 6% cold),
# so score-4/5 pages under the ceiling are like-eligible via Tier 2.
# Big media stays skipped.
SCENE_PRESS_EXCEPTION = {
    "enabled": True,
    "categories": ["media", "promoter"],
    "min_score": 4,
    "max_ig_followers": 8000,
}

ALWAYS_SKIP_RULES = {
    "min_score_required": 2,               # score 1 = never engage
    "max_ig_followers_absolute": 15000,    # hard ceiling, no exceptions
    "skip_labels_above_followers": 5000,   # labels > 5K IG = buried
    "skip_sponsored_content": True,        # never engage with ads or promoted posts
    "skip_verified_accounts_scene": False,  # verified OK for Scene likes (not follows)
}

# ---------------------------------------------------------------------------
# BLOCKED COUNTRIES — hard rule, both Reach and Scene
# ---------------------------------------------------------------------------

BLOCKED_COUNTRIES = ["Israel"]
BLOCKED_LOCATIONS = [
    "tel aviv", "jerusalem", "haifa", "herzliya", "netanya",
    "rishon lezion", "beer sheva", "israel", " il ",
]
BLOCKED_SCRIPTS = ["hebrew"]  # Hebrew character detection in bio text

# Hebrew Unicode range for detection
HEBREW_UNICODE_RANGE = (0x0590, 0x05FF)

# ---------------------------------------------------------------------------
# CIRCUIT BREAKERS — engine stops immediately on any of these
# ---------------------------------------------------------------------------

CIRCUIT_BREAKER_SIGNALS = [
    "Action Blocked",
    "Try Again Later",
    "We've limited some features",
    "Your account has been temporarily",
    "Suspicious Login Attempt",
    "Verify Your Account",
    "Confirm Your Identity",
    "Enter Your Password",
    "We Noticed an Unusual Login",
    "Help Us Confirm You Own This Account",
    "Add Your Phone Number",
    "We Restricted Certain Activity",
    "Please Wait a Few Minutes",
    "You're All Caught Up",           # session drift signal
]

# After circuit break pause durations (hours)
PAUSE_AFTER_SOFT_BLOCK = 48    # action blocked on one type, account still works
PAUSE_AFTER_HARD_BLOCK = 72    # account restricted
PAUSE_AFTER_CAPTCHA = 72
PAUSE_AFTER_VERIFICATION = 0   # 0 = stop all automation, manual review required

# Actions the engine must NEVER take under any circumstances
HARD_PROHIBITIONS = [
    "enter_password",
    "accept_privacy_changes",
    "accept_terms_update",
    "click_enable_notifications",
    "open_dm_inbox",
    "open_any_dm",
    "click_any_link",              # navigation only via address bar
    "interact_with_settings",
    "engage_with_sponsored_post",
    "engage_with_promoted_content",
    "engage_with_ad",
    "accept_checkpoint",
    "accept_verification_prompt",
    "unlike_existing_like",        # NEVER click heart on already-liked post (would unlike)
]

# ---------------------------------------------------------------------------
# PERSONAL NETWORK
# File path — engine reads this at session start, never writes
# ---------------------------------------------------------------------------

PERSONAL_NETWORK_FILE = "scene_intelligence/ig_personal_network.json"
BLOCKED_ACCOUNTS_FILE = "scene_intelligence/ig_blocked_accounts.json"

# ---------------------------------------------------------------------------
# FOLLOW / UNFOLLOW TRACKER
# ---------------------------------------------------------------------------

FOLLOW_TRACKER_FILE = "scene_intelligence/ig_follow_tracker.json"
TARGET_LIST_FILE = "scene_intelligence/ig_target_list.json"
ENGAGEMENT_LOG_FILE = "scene_intelligence/engagement_log.json"
ENRICHED_CONTACTS_FILE = "scene_intelligence/enriched_contacts.json"
PROMOTION_LOG_FILE = "scene_intelligence/promotion_log.json"
RELEASE_CONTEXT_FILE = "scene_intelligence/release_context.json"
IG_ENRICHED_FILE = "scene_intelligence/ig_enriched_contacts.json"

# ---------------------------------------------------------------------------
# LIKE-BEFORE-FOLLOW SEQUENCE
# ---------------------------------------------------------------------------

LIKE_BEFORE_FOLLOW = True      # always like before following
LIKE_BEFORE_FOLLOW_MAX_POSTS_CHECK = 3  # check up to 3 recent posts, like the most recent

# ---------------------------------------------------------------------------
# DATA COLLECTION — paid marketing seed
# ---------------------------------------------------------------------------

DATA_COLLECTION = {
    "track_discovery_source": True,     # which hashtag or follower list
    "track_follower_count_at_discovery": True,
    "track_genre_signals_found": True,  # bio keywords and hashtags detected
    "track_follow_back": True,
    "track_engagement_rate_at_discovery": True,
    "store_bio_text": True,             # for competitive intel
    "store_hashtags_used": True,        # hashtags on their recent posts
}

# Paid campaign audience file (follow-back dataset)
PAID_AUDIENCE_FILE = "scene_intelligence/ig_paid_audience_seed.json"

# ---------------------------------------------------------------------------
# SEO / COMPETITIVE INTEL
# ---------------------------------------------------------------------------

COMPETITIVE_INTEL_FILE = "data_intelligence/competitive_intel.json"
SEO_VERSIONS_FILE = "data_intelligence/seo_versions.json"
IG_PERFORMANCE_LOG_FILE = "scene_intelligence/ig_performance_log.json"

# Reference artists for competitive intel collection (20-30 accounts)
REFERENCE_ARTISTS = [
    "mannequinrecords",
    "darkentriesrecords",
    "clone.nl",
    "lies_records",
    "berghain_panoramabar",
    "mechatronica",
    "melopeerecords",
    "detriti_records",
    "libertinerecords",
    "hardcorecollective",
    "clap_clap_clap",
    "red_laser_records",
    "pinkmanrecords",
    "zyx_music_official",
    "citinite",
    "legowelt",
    "dj_stingray_313",
    "nwaqua",
    "francescagr",
    "fleisch.berlin",
]

# ---------------------------------------------------------------------------
# SC / IG COORDINATION
# Real schedule (audit item 22, aligned 2026-07-19): SC expanded to
# Mon/Tue/Thu/Fri on 2026-05-27 (SOP §2.3), Sunday = unfollow sweep,
# Wednesday = read-only health pass. IG stays Mon/Wed/Fri, so Monday and
# Friday are legitimately SHARED days. Per both SOPs that's acceptable —
# different platforms, different cookies/drivers — keep 3+ hours between
# the two sessions on a shared day. The old "no overlap days" rule was
# fiction the validate_config guard kept validating.
# ---------------------------------------------------------------------------

SC_SESSION_DAYS = ["Monday", "Tuesday", "Thursday", "Friday"]

# ---------------------------------------------------------------------------
# GENRE SIGNAL FILTER — Track A follow gate
# Applied at follow time against the live Instagram bio.
#
# Only fires when ALL of these are true:
#   1. GENRE_FILTER_ENABLED is True
#   2. The bio is longer than GENRE_FILTER_MIN_BIO_LENGTH characters
#      (short bios — emojis, just a location, a single word — bypass the
#       filter entirely; they're ambiguous, not a disqualification signal)
#   3. The bio matches fewer than GENRE_FILTER_MIN_MATCHES keywords
#
# Rationale for the length gate: many electronic musicians write bios like
# "📍Berlin" or "🖤" — no genre text at all. We should only reject accounts
# whose bio is substantive enough to have had a chance to signal genre and
# still didn't. A 5-char bio tells us nothing; a 40-char bio that mentions
# only yoga and fitness tells us a lot.
#
# To disable entirely: set GENRE_FILTER_ENABLED = False
# To make it stricter: raise GENRE_FILTER_MIN_MATCHES to 2
# To catch more musicians: lower GENRE_FILTER_MIN_BIO_LENGTH
# ---------------------------------------------------------------------------

GENRE_FILTER_ENABLED = True
GENRE_FILTER_MIN_MATCHES = 2       # at least 2 keywords must appear (was 1 -- too lax)
GENRE_FILTER_MIN_BIO_LENGTH = 0    # 0 = always apply (was 30 -- short bios used to bypass)
# Non-music accounts often have empty/short bios; bypassing them was letting
# random users through. With min length 0 the filter always runs; combined
# with min_matches=2 a real musician's substantive bio still passes easily.

GENRE_KEYWORDS = [
    # Scene-specific genre labels (high precision)
    "ebm", "industrial", "darkwave", "dark wave", "synth", "synthwave",
    "minimal synth", "minimal wave", "coldwave", "cold wave", "new wave",
    "post-punk", "post punk", "goth", "gothic", "noise",
    "electronica", "electro", "techno", "experimental",
    "ambient", "drone", "dark ambient", "power electronics", "harsh noise",
    "body music", "neue deutsche welle", "ndw", "italo", "space disco",
    "cosmic", "krautrock", "kosmische", "modular",
    "dark disco", "shoegaze", "dream pop", "dreampop", "outsider",
    "acid", "trance",
    # Music-industry activity signals (medium precision -- artist must pair
    # with a genre or platform keyword to hit the 2-match threshold)
    "producer", "electronic producer", "label", "vinyl", "musician",
    "tape", "cassette",
    "synthesizer", "synthesizers", "sequencer", "drum machine",
    "808", "909", "303",
    "mixtape", "dj set", "remix",
    "beatport", "soundcloud", "bandcamp", "resident advisor", "boiler room",
    "live set", "live show",
    # Common scene hashtag fragments
    "#ebm", "#darkwave", "#synthwave", "#industrial", "#techno",
    "#electronic", "#electro", "#coldwave", "#postpunk", "#darkdisco",
    "#disco", "#dj", "#producer", "#vinyl", "#italo", "#acid",
]
# Words deliberately removed for being too broad (Berlin civilians frequently
# use them in lifestyle bios): music, artist, club, dance, tour, release, ep,
# mix, sound, album, booking, record, dj, disco, electronic, bass, wave,
# psychedelic. Keeping "dj"/"electronic"/"disco"/"wave" only as hashtags.

# ---------------------------------------------------------------------------
# OVERLAP SCORING — Track A queue prioritisation
# Queue entries with seed_count > 1 (appeared in multiple seed follower lists)
# are sorted to the front of the eligible pool before the session cap is applied.
# seed_count is written by ig_queue_builder.py at queue build time.
# Entries without seed_count are treated as seed_count = 1.
# ---------------------------------------------------------------------------

OVERLAP_SORT_ENABLED = True   # sort queue by seed_count descending before session pull

# ---------------------------------------------------------------------------
# FOLLOWBACK CIRCUIT BREAKER -- preflight gate
# Halts session start if recent follows have a low follow-back rate, which
# means the queue is producing junk targets. Re-enabled when the rate
# recovers (after a queue rebuild and a fresh batch of follows).
#
# Tunables:
#   FOLLOWBACK_MIN_RATE      -- minimum acceptable rate (0..1). 0 = disabled.
#   FOLLOWBACK_MIN_FOLLOWS   -- only trip the gate after this many recent follows
#                               (otherwise small samples cause false stops).
#   FOLLOWBACK_WINDOW_SESSIONS -- how many recent session-days to average over.
# ---------------------------------------------------------------------------

FOLLOWBACK_MIN_RATE        = 0.10   # halt if last sessions averaged < 10% FB rate
FOLLOWBACK_MIN_FOLLOWS     = 15     # need at least 15 follows in window before tripping
FOLLOWBACK_WINDOW_SESSIONS = 3      # rolling window of last 3 session-days

# ---------------------------------------------------------------------------
# 2026-08-26 SAFETY BATCH (Amir-approved after the Wed session findings)
# ---------------------------------------------------------------------------

# FAIL-CLOSED RECIPROCITY GATE (2026-08-28, after @_.miser._ churn).
# The 08-26 staleness gate was the WRONG mechanism: it reads stats.last_checked,
# which the checker stamps even when every per-account check failed. On
# 2026-08-28, 26 of 28 active_follows had user_id=null, all 26 id-resolutions
# failed, and `followed_back: false` therefore meant "never measured" -- yet the
# sweep read it as "does not follow back" and churned a reciprocator.
# With this on, an entry is unfollow-eligible ONLY if its reciprocity was
# actually verified (followback_verified_at present and within
# FOLLOWBACK_MAX_STALE_DAYS). Unverified == protected, not eligible.
FOLLOWBACK_REQUIRE_VERIFIED = True

# Consecutive failed user_id resolutions that stop the checker. Per SOP 4.3,
# "could not resolve user ID" is a Class A (IG-signal) event; 26 in one run on
# 2026-08-28 should have deferred the day and did not, because the checker had
# no breaker at all.
FOLLOWBACK_MAX_CONSECUTIVE_RESOLVE_FAILURES = 3

# Unfollow sweeps refuse follow-back data older than this many days (engine
# already reads this via getattr with default 7). Set to 1 after @infoluences:
# a reciprocator was churned with tracker data checked 2 days earlier AND the
# "Follows you" badge unrendered. Practical effect: session days need the
# follow-back checker run the same morning (the documented --override-ledger
# combo, counted as one API budget); otherwise the sweep is skipped safely.
# RETIRED 2026-08-31 (export-era): the 1-day API-checker staleness gate is
# replaced by the export rules below. Kept only so old notes stay readable.
FOLLOWBACK_MAX_STALE_DAYS = 1

# EXPORT-ONLY SWEEP GATE (Amir 2026-08-30, "the gap is fine"): reciprocity
# comes from the official IG data export (~30-day cadence, zero API calls).
# An account is sweep-eligible only when its followback_verified_at is
# (a) at most SWEEP_VERIFICATION_MAX_AGE_DAYS old, and (b) dated at least
# SWEEP_EXPORT_WINDOW_DAYS after its followed_at (the export covers the whole
# follow-back window). Accepted residual: a follow-back arriving later than
# the window can still be missed if the live badge fails to render.
SWEEP_VERIFICATION_MAX_AGE_DAYS = 30
SWEEP_EXPORT_WINDOW_DAYS = 21

# Reach plans draw ONLY from audited queue entries (audit_date present).
# The 2026-08-12 vetted-first sort still let unaudited entries fill the tail;
# on 2026-08-26 that produced blind picks (25-follower account, 33-day-stale
# account, no-genre bio). With this on, a short vetted pool means a smaller
# plan plus the existing POOL LOW warning -- never blind candidates.
REACH_VETTED_ONLY = True

# When a Scene contact was skipped as all_recent_sponsored_or_already_liked
# (= no new content since our last visit), do not re-serve them for this many
# days. The old skip-cooldown needed 2+ skips in 7 days and only held 5 days;
# on 2026-08-26 six contacts burned like-slots this way in one session.
NO_NEW_CONTENT_COOLDOWN_DAYS = 30

# Labels stored within margin_pct below the 5K notification ceiling whose IG
# enrichment is older than max_enrichment_age_days are excluded until
# re-checked (2026-08-26: @eskimorecordings stored 4,654 / live 5,066 on
# 4-month-old enrichment). Cleared automatically once enrichment refreshes.
LABEL_CEILING_STALE_GUARD = {
    "enabled": True,
    "margin_pct": 0.10,
    "max_enrichment_age_days": 30,
}

# ---------------------------------------------------------------------------
# THE 2.0 API LAW (Amir-approved 2026-08-30 — TICKETS.md T-003/T-004).
# Replaces BOTH the old "one IG script per day" rule and the flat 150 cap.
# Enforced by ig_daily_ledger.check_and_claim() + ig_ops_guards; these
# constants are the single source the enforcers read.
# ---------------------------------------------------------------------------
IG_ENDPOINT_BUDGETS = {
    "profile_reads": 30,       # web_profile_info-class (throttled 2026-08-27 at ~50)
    "friendship_checks": 20,   # friendships/show — exceptional-only since export-era
    "roster_walk": 0,          # BANNED — 2026-08-29 token invalidation; use the export
    "graph_insights": 40,      # official Graph API, own account (IP-safe surface)
}
IG_DAY_SOFT_CALLS = 50         # a normal day stays under this (warn past it)
IG_DAY_HARD_CALLS = 150        # absolute never-cross ceiling (no override)

# Detection cooldown windows (hours) read by ig_ops_guards.require_no_cooldown.
# Any IG event in detection_events.json blocks ALL IG API work until its
# window closes (counted from the end of the event's day, conservative).
DETECTION_COOLDOWN_HOURS = {
    "default": 72,
    "suspected_soft_throttle_web_profile_info": 48,
    "session_invalidated_after_roster_enumeration": 48,
    "rate_limited_429_profile_reads": 168,  # 2026-09-06: three 48h waits failed (09-02/05/06); one unbroken week
}

# Detection types that live on the API READ surface only (web_profile_info,
# friendships/show). They block API jobs; they do NOT block browser sessions,
# which click in Amir's real Chrome and never call these endpoints (2026-09-06,
# Amir's "Go": three throttle cooldowns cost a week of sessions for nothing).
# Anything not listed here (CAPTCHA, action block, login challenge, ...) is
# account-level and blocks everything.
# In-session vetting (2026-09-06, Amir's Go): the browser session vets
# unvetted queue candidates itself -- open the profile, read followers /
# posts / private badge / newest post date, log one ig_vet line. The merge
# recomputes the verdict from the numbers against REACH and writes the same
# fields the API audit wrote (audit_source="browser"). Makes the pipeline
# independent of the throttled profile-read API.
IN_SESSION_VET = {
    "enabled": True,             # re-enabled 2026-10-12 with follows_per_session (Amir unpaused follows); was False since 2026-09-26: vets only exist to feed follows
    "per_session": 6,            # back to 6 on 2026-11-03 (M-10, Amir standing go 11-01): followable pool 31 >= 30 after the HikerAPI mornings. Was a temporary 15 from 2026-10-20 while HikerAPI had no balance.
    "only_when_pool_below": 30,  # vetted-pool floor (same as the dispatcher's)
}

# --- Third-party data provider (HikerAPI), Amir approved 2026-09-14 -------
# Every Instagram READ (profile checks, seed follower crawls) goes through the
# provider; Amir's own account never touches Instagram for reads again.
# The IG timing law (one job/day, daytime, 150 ceiling, rest day) protected
# the ACCOUNT; provider calls cost money only, so they get their own cap.
PROVIDER = {
    "name": "hikerapi",
    "daily_call_cap": 300,          # cost guard (~$0.30/day at Standard $0.001/call). Above 300: ask Amir with a reason each time (rule 2026-11-03)
    "audit_per_day": 60,            # steady state (2 calls per candidate)
    "audit_per_day_backlog": 100,   # while unchecked names > backlog_threshold
    "backlog_threshold": 300,       # unvetted pending above this = backlog mode
    "builder_unvetted_floor": 200,  # builder runs when unvetted pending < this
    "builder_seeds_per_run": 8,     # best-yielding seeds first
}
IG_DIRECT_API_ENABLED = False   # the old logged-in reads are OFF (2026-09-14)

API_SURFACE_DETECTION_TYPES = frozenset({
    "rate_limited_429_profile_reads",
    "suspected_soft_throttle_web_profile_info",
    "session_invalidated_after_roster_enumeration",
})
