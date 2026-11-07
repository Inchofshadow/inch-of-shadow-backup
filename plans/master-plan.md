# Inch of Shadow -- Master Plan

> **History (2026-11-05).** Electronic-era document from March 2026, kept as background: songs are the main line since 2026-09-13, no 3 EPs, no Beatport for new releases, next release Half the Night EP (date open).
> Current truth: `plans/strategy/refresh-page/` and `plans/strategy/review-2026-11-05-facts.md`.

**Artist:** Amir / Inch of Shadow
**Location:** Berlin, Germany
**Sound:** Dark disco, acid, electro, EBM, techno, slowmo, cinematic, melancholic
**Last updated:** 2026-03-24

---

## The Big Goal

Accelerate Inch of Shadow's career from local Berlin presence to a recognized name in the underground electronic scene. Release consistently, grow audiences across all platforms, generate revenue, and turn music into a sustainable career. More releases, more followers, more gigs, more income, more opportunities -- faster than doing it all manually.

This platform is the engine behind that. Every tool exists to eliminate friction between finishing a track and getting it heard by the right people, bought by the right fans, and played by the right DJs.

---

## Vision

A personal music platform -- Python tools automating the full release lifecycle from research to stats. Local-first, privacy-first, secure by design. No database (JSON + Google Sheets), dark-themed web UI via Flask. One artist, one machine, total control.

The platform's real value: every tool reduces the time between "I finished a track" and "the right people are hearing it." The faster and more consistently that loop runs, the faster the numbers grow -- and growing numbers unlock everything else.

---

## Security and Privacy

This platform handles personal data, industry contacts, API credentials, and creative assets. Security and privacy are non-negotiable.

**Security rules:**
- ALL API keys in `.env` only -- never hardcoded, never committed
- `.env` always in `.gitignore`
- No command injection, no XSS, no SQL injection, no OWASP top 10 vulnerabilities
- Sanitize all user input at system boundaries
- Never expose API keys, credentials, or internal paths to the client
- Code must be secure -- every tool, every route, every script

**Privacy rules:**
- Privacy first: no data sent to third-party services without explicit approval
- No external APIs that log or store user data without consent
- Prefer local/self-controlled solutions over hosted services
- When a tool could be upgraded using an external service or API, always inform the user first -- explain what the service does, what data it would send, what it costs, and any privacy implications. Let the user decide.
- Contact data (938 industry contacts) is sensitive -- treat it accordingly
- No tracking, no analytics on the web UI, no data leaks

---

## Tool Overview

| Tool | Name | Status | Details |
|------|------|--------|---------|
| 1 | Scene Intelligence Engine | Partial | 938 contacts, 10 Sheets tabs, 4 enrichment APIs, label tiers, engagement tracking. See `plans/scene-intelligence.md` |
| 2 | Release Manager | Done | Artwork/Video/SEO/Distribution tracking/UI all integrated. See `plans/release-manager.md` |
| 2+ | Content Calendar | Planned | Extension of RM, week-grid view |
| 3 | Promotion Engine | Partial | Press list, genre/location filters, campaign tracking, contact discovery, press kit generation. Integrated into RM web UI. |
| 4 | Email Outreach Manager | Not started | Email sending (SMTP), templates, rate limiting, tracking |
| 5 | Stats Dashboard | Not started | Spotify/Bandcamp/SoundCloud stats aggregation |

### Tool Connections

```
Tool 1 (Scene Intelligence) -- 938 contacts, enrichment, Sheets sync
    |-- shared file: enriched_contacts.json (both SI and RM read/write)
    |-- feeds contacts into --> Tool 3 (Promotion Engine)
    |-- feeds contacts into --> Tool 4 (Email Outreach)
    |-- pushes to Google Sheets (10 tabs, auto-sync back)

Tool 2 (Release Manager) -- central hub
    |-- Artwork Resizer (17 platform exports, metadata embedding)
    |-- Video Resizer (9 platform exports, metadata embedding)
    |-- SEO Copy Generator (Claude API, 7 platforms)
    |-- Distribution Tracking (Symphonic, status/UPC/dates)
    |-- Content Calendar (planned, release date --> content schedule)
    |-- metadata_utils.py (shared by artwork + video resizers)
    |-- will feed into --> Tool 5 (Stats Dashboard) for release tracking

Tool 3 (Promotion Engine) -- integrated into RM web UI
    |-- reads from --> Tool 1 (enriched_contacts.json for targets)
    |-- reads from --> Tool 2 (release data for campaign context)
    |-- writes to --> promotion_log.json (campaigns, targets, status)
    |-- writes to --> engagement_log.json (follows, likes, comments)
    |-- promo/engagement data syncs to Sheets on push

Tool 4 (Email Outreach) -- NOT STARTED
    |-- depends on --> Tool 1 (contact emails)
    |-- depends on --> Tool 3 (press kits, campaign targets)
    |-- needs: SMTP setup, templates, rate limiting, tracking

Tool 5 (Stats Dashboard)
    |-- depends on --> Tool 2 releases list (to match stats to releases)
    |-- will require --> platform API keys (Spotify for Artists, Bandcamp, SoundCloud)
```

### RM-SI Sync Architecture

Shared data files live in `scene_intelligence/`:
- `enriched_contacts.json` -- all 938 contacts, both RM and SI read/write directly
- `promotion_log.json` -- campaigns, targets, status per release
- `engagement_log.json` -- daily engagement queue, follows, hidden contacts
- `release_context.json` -- active release genre context for scoring
- `label_tiers.json` -- auto-generated on every push (big/mid/small)

**SI --> Sheets (on push):** All contact fields + Last Engaged, Campaigns, Promo Status columns
**Sheets --> SI (on push):** category, sub_type, genre, score, promo_list, delete markers
**RM --> SI:** genre tags, category changes, contact removal (via Engagement page)
**Promo/Engagement --> Sheets:** auto-populated on each push (read-only in Sheets)

---

## Career Goals

**Current position:** Active locally in Berlin. Playing semi-regularly. Growing scene connections (938 contacts in SI, 30 engaged so far). No management, no booking agent, no label releases yet. 3 EPs planned for 2026. Both DJ sets and live performance. Symphonic distribution active. Spotify for Artists and Apple Music for Artists claimed.

### Goal 0 -- Grow Audience and Revenue (TOP PRIORITY)
**What:** Increase followers, listeners, streams, and sales across all platforms. This is the metric that unlocks everything else -- labels, management, bookings, festivals all look at your numbers.

**Why it matters:** Numbers are proof. Proof that people care about your music. Every other goal (labels, management, agency, festivals) becomes easier with growing numbers. A label is more likely to sign you if your Bandcamp is selling. A booking agent is more interested if your Instagram is growing. This isn't vanity -- it's leverage.

**Key targets:**
- Grow followers on Instagram, SoundCloud, Spotify, Bandcamp, YouTube, Beatport
- Grow Spotify monthly listeners, saves, and playlist placements
- Generate revenue through Bandcamp sales, Beatport/Traxsource purchases, and streaming royalties

**Platforms to grow (priority order for underground electronic):**
1. **Bandcamp** -- direct sales, fan email list, Bandcamp Fridays = zero commission
2. **Beatport/Traxsource** -- DJ charts, credibility in electronic music scene
3. **Instagram** -- visual presence, direct artist-to-fan connection, story engagement
4. **SoundCloud** -- reposts, community engagement, free tracks build audience
5. **Spotify** -- editorial playlists, algorithmic reach, saves/follows matter
6. **YouTube** -- music videos, visualizers, premieres, evergreen discovery

**What "done" looks like (measurable):**
- Monthly follower growth on Instagram, SoundCloud, Spotify, Bandcamp
- Bandcamp sales on every release (even small numbers matter early)
- Beatport/Traxsource chart appearances
- Spotify editorial playlist consideration (requires 7-day advance pitch)
- SoundCloud reposts from other artists in the scene
- YouTube views growing on music content

**Tools that accelerate this:**
- SEO Copy maximizes discoverability on every platform
- Artwork/Video Resizer ensures professional presence everywhere
- SI identifies who to connect with (DJs, blogs, playlists that amplify reach)
- Stats Dashboard (planned) will track what's working so you double down
- Content Calendar (planned) will systematize posting around releases

**Immediate actions (no new tools needed):**
- Optimize all platform profiles using SEO Copy Generator
- Resize artwork for all platforms to look consistent and professional
- Post regularly on Instagram (behind-the-scenes, studio clips, artwork previews, release teasers)
- Upload free tracks/previews to SoundCloud to build followers before release
- Engage with other artists in the scene -- comment, repost, support. The underground is a community, not an algorithm
- Cross-link all platforms from every profile
- Use Bandcamp fan messaging for every release

---

### Goal 1 -- Build a Professional Catalog
**What:** Release 3 EPs in 2026. Every release is airtight -- artwork, metadata, SEO, platform presence, pre-release campaign.

**Why it matters:** Nobody -- no manager, no agent, no label -- takes you seriously without a catalog. The catalog is the product. Everything else is marketing the product.

**What "done" looks like:**
- 3 EPs released on all platforms via Symphonic
- Each EP went through the full RM pipeline (9 milestones, all checklists, all platform specs)
- Consistent visual identity across all platforms (artwork resized to all 17 specs per release)
- SEO-optimized presence on every platform (copy generated for all 7 platforms per release)
- Bandcamp, Beatport, Traxsource presence established (these matter more than Spotify in underground electronic)
- Video content for every release (at least 1 promo video per EP, resized to all 9 specs)

---

### Goal 2 -- Get DJ Support from the Right People
**What:** Get your tracks played and charted by DJs in your scene -- dark disco, acid, electro, EBM circles.

**Why it matters:** In underground electronic, DJ support is the primary discovery channel. A track in the right DJ's set or chart is worth more than 10,000 Spotify streams. It signals to labels, promoters, and audiences that you belong.

**Current status:** 611 DJs in SI (321 with verified SoundCloud). Engagement system active -- 30 contacts engaged so far. Promo campaigns running (farewell-single: 34+ targets). Campaign status tracked per contact and visible in Sheets.

**What "done" looks like:**
- Promo copies sent to 30-50 high-match DJs (score 4-5 in SI) before each release
- Tracks appearing in DJ charts on Beatport, Traxsource, RA
- Feedback from DJs ("played this at X club", "charted this week")
- Growing network of DJs who expect your promos

---

### Goal 3 -- Secure Media Coverage and Premieres
**What:** Get tracks premiered on blogs, YouTube channels, and podcasts that cover your genres. Get reviews and features.

**Why it matters:** Premieres give you reach beyond your existing audience. A premiere on a respected channel validates your music to labels and managers. It's permanent -- a review or premiere lives on the internet forever and shows up when people search your name.

**What "done" looks like:**
- At least 1 premiere per EP on a relevant blog/channel
- Reviews or features on 2-3 media outlets per year
- Press kit ready to send at any time (bio, photos, tracklist, links, key stats)
- Media contacts built and maintained in SI

---

### Goal 4 -- Get Label Releases
**What:** Sign 1-2 EPs or tracks to established labels in your genre. Self-release the rest.

**Why it matters:** A label release gives you credibility, reach, and their promotional machine. The mix strategy (self-release some, label some) keeps you independent while leveraging label infrastructure.

**Current status:** 207 labels in SI (104 big, 61 mid, 42 small). ~120 verified demo emails. 104 labels have boss identified. Label tier system auto-colors Sheets (green/yellow/red). Promo campaigns targeting labels already running.

**What "done" looks like:**
- Demo submissions sent to 15-20 aligned labels (filtered from SI by score 4-5)
- At least 1 label offer or release deal by end of 2026
- Relationship built with 2-3 label A&Rs who know your sound
- Self-releases on Bandcamp/Beatport building your direct audience in parallel

---

### Goal 5 -- Sign with Management
**What:** Find management that understands underground electronic music and can handle bookings, strategy, and industry connections.

**Why it matters:** Management frees you to focus on music. A good manager opens doors you can't open alone. In electronic music, management often comes after you've proven you can release and perform consistently.

**What "done" looks like:**
- Artist package ready: consistent catalog, press kit, stats, social presence, visual identity
- Approached 5-10 management companies that handle similar artists
- Conversations started based on traction (releases, DJ support, media coverage, gig history)

---

### Goal 6 -- Secure Booking Agency and Regular Gigs
**What:** Sign with a booking agency. Expand from Berlin to other European cities. Both DJ sets and live shows.

**Why it matters:** A booking agent gets you into venues and festivals you can't access directly. They handle negotiations, logistics, and have relationships with promoters across Europe.

**What "done" looks like:**
- Performing regularly in Berlin (monthly or more)
- Expanded to 2-3 other cities (e.g., Amsterdam, London, Paris, Tbilisi)
- Signed with a booking agency that covers European circuit
- Both DJ and live sets available (different pricing, different contexts)

---

### Goal 7 -- Play Festivals (Summer 2027 Target)
**What:** Secure 2-3 festival slots for summer 2027. Dark disco / acid / techno / EBM festivals and stages.

**Why it matters:** Festivals are where you reach new audiences at scale. A festival set can convert hundreds of new listeners. Festival lineups are social proof -- being on the bill with established artists positions you in the scene.

**Strategy:** Start with smaller festivals that book emerging artists, local Berlin all-nighters, ADE off-program showcases, and label showcase slots. Research specific targets closer to submission time (most deadlines Oct-Jan for summer).

**What "done" looks like:**
- Festival submissions sent 6-9 months ahead
- Booking agent pitching on your behalf
- At least 2-3 festival confirmations for summer 2027
- Professional press kit with festival-specific materials

---

### How the Tools Map to Career Goals

```
                        Career Goals
                        ────────────
GROW AUDIENCE & REVENUE (0) <-- SEO Copy, Artwork, Video, Calendar, Stats, Engagement Queue
          Catalog (1) <-- RM, Artwork, Video, SEO, Distribution Tracking, Calendar
       DJ Support (2) <-- SI (611 DJs, score 4-5), Promo Engine campaigns, Email Outreach
  Media/Premieres (3) <-- SI (44 media), Promo Engine, Email Outreach, Press Kit
  Label Releases  (4) <-- SI (207 labels, ~120 emails), Promo Engine campaigns, Email Outreach
     Management   (5) <-- Stats Dashboard, Press Kit, all tools prove professionalism
 Booking Agency   (6) <-- SI (35 venues, 20 promoters), Email Outreach, Stats
    Festivals     (7) <-- SI (festival contacts), Booking Agent, Stats, Press Kit
```

---

## Distribution

- **Distributor:** Symphonic Starter ($19.99/yr) -- account opened March 2026
- **Platforms:** Spotify, Apple Music, Beatport, Traxsource, Bandcamp, SoundCloud, YouTube Music, Audius, Catalog, Deezer, Tidal
- **2026 releases:** 3 EPs planned (Dark Disco Acid, Techno Trance, Downtempo/Exotic)

---

## Technical Phases

### Phase 1 -- Ship the First EP with Full Platform Support
Use existing tools to release Dark Disco Acid EP end-to-end. Build Content Calendar. First real-world test of the platform.

**Status:** In progress. RM pipeline ready (artwork, video, SEO, distribution tracking). Symphonic account active. Content Calendar designed but not coded.

**Depends on:** Content Calendar (planned), Symphonic account (done)

### Phase 2 -- Automate the Outreach Loop
Build Promotion Engine + Email Outreach. One-click "promote this release" workflow. Press kit generator. Demo submission tracking.

**Status:** Partially done.
- Promotion Engine (Tool 3) built into RM: release selector, press list with genre/location filters, campaign tracking (56 targets across 4 campaigns), contact discovery with genre-aware scoring, press kit generation
- Engagement system built: daily engagement queues (IG + SoundCloud), follow/unfollow tracking, discovery seeds
- Promo activity stored per contact in enriched_contacts.json and synced to Sheets
- Missing: Email sending (Tool 4 -- needs SMTP setup, templates, rate limiting)

**Depends on:** SI promo list (done), validated demo emails (~120 available)

### Phase 3 -- Measure What Matters
Build Stats Dashboard. Per-release and per-platform views. Audience geography. Release comparison. Prove traction to management/agents.

**Status:** Not started. IG API configured (token expires ~May 20, 2026) but only useful for own account stats. Spotify/SoundCloud APIs available.

**Depends on:** Platform API access, at least 1 released EP with real data

### Phase 4 -- Intelligence Feedback Loop
Connect all tools. Stats feed back into SI scores. Successful contacts rank higher. Release health scores. Calendar learns from performance data.

**Status:** Not started. Foundation laid -- promo status and engagement data now flow back to contacts and Sheets, enabling future scoring improvements.

**Depends on:** All previous phases, 2+ EPs with data

---

## Long-Term Vision (Beyond 2026)

- **Self-contained artist command center** -- one local app: create, prepare, distribute, promote, measure, learn, repeat
- **Scene graph** -- SI evolves from flat contacts into a relationship graph (who plays where, who releases on which labels, who playlists whom)
- **Smart recommendations** -- "this label released 3 artists in your genre this month" or "your saves spiked after blog X covered you -- pitch them again"
- **Multi-release strategy** -- cross-EP analytics, catalog management, backcatalog promotion triggers
- **Touring support** -- gig calendar, travel logistics, setlist planning, merch tracking
- **Portable** -- the platform stays local-first but could be packaged for other independent artists
