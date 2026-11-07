# Product lens: Inch of Shadow as a brand, the songs as the product (2026-11-06)

Read-only study. Nothing edited, moved or run in either repo. No secret values copied.
Amir's framing: "Inch of Shadow is the brand, my songs are my product. Can we learn something
from selling a product, and which skills?"

What was read. Gero: `docs/gtm/` (README, positioning, messaging, icp, voice, proof,
competitive, maestro-campaign, research), `docs/gerowallet-fact-sheet.md`,
`nexus-pricing-playbook.html`, `content/nexus/email/IMPLEMENTATION.md`,
`content/gerowallet/announcement/v27-launch-week-tweets.md`, and the Gero memory files on
launches, the email sequence, the Q4 war plan and backlog, banned claims, the CTA rule,
content strategy, partner announcements, featuring policy, social copy style. IoS:
`docs/brand/positioning.md`, `proof.md`, the release guide headings, `release-day-playbook.md`,
`release-lessons.md`, `marketing-campaign-template.md`, the four pitch templates, the
promotion-expert agent, the /promo and /release skills, both skill folders, the approved
platform plan (D5) and the 11-05 release-fans research. The Gero code, metrics dashboard and
the TikTok/IG clip question are covered by two other agents (`gero-transfer-2026-11-06.md`)
and are not repeated here.

Tags on web evidence: [OFFICIAL] the platform's or publisher's own page, [REPORTED] trade press
or a survey write-up, [CLAIMED] vendor or practitioner blog.

---

## 1. The mapping table

| Product concept | Music equivalent | What we have | Gap |
|---|---|---|---|
| The product | The single (one song, one ISRC) | `releases/<slug>.json` per release, 3 so far (electronic lane) | Songs-era release files start with the first song (D8) |
| The product line | The catalogue: album, EPs, the two lanes | Bridge plan v2 (songs main line, electronic drops light lane), waterfall idea in the release guide s.13 | No written line plan: which singles become which album, in what order |
| Positioning | Who the artist is, for whom, against what | `docs/brand/positioning.md` v2 (QUICK PULL, neighbourhood, tags, influences) | Fine. Missing only the per-audience message layer (see method 1) |
| Ideal customer profile | Listener segments with triggers and where they are | Audience notes inside positioning.md; curator DB, DJ pool, SI contacts | No segment sheet: who buys, who follows, who shares, what triggers each, where to reach them |
| Fact sheet (single source of claims) | `proof.md` | `docs/brand/proof.md` (facts only, 125 lines) and the applied bios | No CONFIRMED / NOT YET / UNCERTAIN tags, no "pitfalls to catch" list, no "do not publish" block |
| Pricing and tiers | Bandcamp price, name-your-price floor, Bandcamp subscription, SC Fan Support, premieres that charge | Bandcamp plan 10-21 (BC-01..11); premieres charge | No written price stance per item (digital single, album, bundle, subscription) and no decision rule for discounts |
| The store | Bandcamp | Bandcamp traffic plan, 51 followers, 16 on the list | Mailing-list sign-up not yet on every release page and gig; no bundle |
| Subscription | Spotify follow (Release Radar), Bandcamp subscription, YouTube subscribe | Spotify 68 followers, platform plan makes the follow the Spotify job | A follow asks for nothing in return; no "why follow" moment in the content |
| Owned customers | The email list | 16 on Bandcamp; Buttondown chosen in D5 (free to 100) | No welcome mail, no release mail template, no sign-up link in bios yet |
| Lead capture | Pre-save page, link in bio, gated SC drop | Hypeddit smart link via Symphonic (free tier cannot see emails); SC follower-only drop planned | Pre-save captures Spotify follows, not emails; email capture needs Bandcamp or Buttondown link |
| Launch sequence | Announce, teaser, release day, follow-up | `release-day-playbook.md` (ordered, battle-tested), `marketing-campaign-template.md` (phases T-8w to T+), release guide s.1 and s.9 | No one-story-per-post library with asset per story and a "verified live" gate |
| Lifecycle messages | What a fan gets after joining | Nothing after a follow or sign-up | The biggest product gap (section 5) |
| CTA and link rules | One next action per piece, real link where links work | IG caption rules in voice.md, pitch templates "one link on its own line" | No standing rule for captions, YouTube descriptions, SC descriptions, Bandcamp "about" |
| Partner co-marketing | Peer collab per song, premiere channel, Ambertone, photographer credit | Collab rules in memory (credits, handles), one peer collab per song in D5 | No per-collab dossier: verified facts, what each side may say, tags, blockers |
| Press list | Premiere channels, blogs, radio, curators | SI DB, curator DB, `promo_press_shortlist.py`, premiere ladder, templates | Songs-era channel list not built (the lists are electronic-lane) |
| Metric per campaign | A number per release, per platform | `plans/targets.json`, `releases/<slug>.json outcomes.stats`, perf log, release-lessons | Tickets do not name their metric; no monthly gate date |
| War plan | Quarter plan with tracks, EOY targets, monthly gates, a task board, a gaps section | `next-six-months.md`, platform plan D5, tickets.json | No named monthly gate and no look-back ritual |
| Banned claims | Things copy must never say | Memory rules: no em-dashes, no feedback asks, no meta lines, never "IOS/IoS", never beyond proof.md, songs era not public yet | Scattered across memory; no single list in the repo, no grep gate before a caption or pitch ships |
| Trial | Free listen: SC stream, YouTube, the 60 s TikTok clip | SC and YouTube catalogue live | Fine. The trial exists; the conversion step after it does not |
| Event | A gig, a listening party, a premiere date | Booking email rules, RA | A gig has no "buy or join" moment attached yet |
| Social proof | Playlist adds, plays, radio plays, a premiere channel's name | proof.md Radio/Curation sections | Small numbers: do not broadcast (Gero rule holds here too) |
| Support | Replying to DMs and comments | SC inbox rule (every reply attaches a track), DM style | Fine |
| Merch | T-shirt, poster, vinyl later | None | None planned; see section 4 before deciding |
| Community | Broadcast channel, Discord | None | Too early at this size (section 4) |

---

## 2. Methods from Gero worth taking (8)

### 1. A messaging layer under the positioning (message house, per-segment lines, pain to message, objections, CTAs)

- What: Gero's `docs/gtm/messaging.md` sits under `positioning.md`: one primary line, alternates,
  per-pillar value statement with a proof point, a headline and three bullets per segment, a
  pain-to-message table, objection handling, and the CTAs. `icp.md` names three segments with
  pains, triggers, criteria and "where to reach them". Agents load only the file they need.
- Where: `/Users/amir/Desktop/Gero/CPcode/gero-control-panel/docs/gtm/messaging.md`, `icp.md`,
  `README.md` (the "how agents use this" block).
- How it maps: positioning.md already holds the one line, the mood words and the neighbourhood.
  The missing layer is "what we say to whom": a DJ, a curator, a premiere channel, a press
  writer, a listener who found the song on TikTok, a Bandcamp buyer. Each gets a headline, three
  lines and one CTA, all pulled from proof.md. Objections for music: "another dark artist from
  Berlin", "no live shows yet", "two lanes under one name".
- Effort: M (one file, written once, refreshed per release).
- What must change: nothing in voice. Keep the artistic words / platform tags split from
  positioning.md. The segment file replaces nothing; the pitch templates read from it.

### 2. Status tags and a pitfalls list in proof.md (the fact sheet pattern)

- What: Gero's fact sheet opens with "Release state (read this first)", tags every fact
  CONFIRMED / NOT SHIPPED / UNCERTAIN, ends with "Top factual pitfalls to catch in articles",
  "UNCERTAIN (do not assert)" and, in proof.md, "Claims removed as unverifiable" and "Do NOT
  publish (internal only)".
- Where: `docs/gerowallet-fact-sheet.md`, `docs/gtm/proof.md`.
- How it maps: proof.md is already the honest source. Add: a "public status" block per lane
  (songs not public until the switch), tags on facts that move (OAC pending, Symphonic
  features unconfirmed, TikTok not open), a pitfalls list (IOS abbreviation, "Cardano"-style
  wrong credits like Ambertone vs Riverside, photo 55 retouched copy, handle underscores), and a
  "removed claims" log so a wrong fact is never re-added.
- Effort: S.
- What must change: proof.md gains three short blocks; the bio skill and promo agent read the
  status block first.

### 3. One banned-claims list in the repo, plus a grep gate

- What: Gero keeps two memory rules that were "already recorded" but shipped anyway on 20 posts,
  so a separate hard-ban file was made and the bans were written into the generator prompt and
  grepped before shipping. Also `voice.md` "Content rules" that override older wording.
- Where: memory `nexus-banned-claims.md`, `docs/gtm/voice.md` (Content rules), `featuring-policy.ts`
  as a single list read by every script.
- How it maps: our bans live in memory files (no em-dashes, no feedback asks, no meta lines, never
  "IOS"/"IoS", "Hi all / hope you will like it" only in messages, describe the track musically,
  songs era not announced, no handle from a search snippet, premiere channels are paid). A
  `docs/brand/banned.md` list plus a tiny checker (regex over a draft: em-dash, "let me know",
  "IoS", "IOS", a handle not in the export/SI) run by the ig, promo and bio skills before a draft
  is shown.
- Effort: S.
- What must change: skills get one "run the check" line. No engagement code touched.

### 4. The launch library: one story per post, asset per story, gated on "verified live"

- What: the v2.7 campaign was seeded as an ordered library (announcement, multichain, design,
  DUST, token depth, perps, search, staking, security), one story per post, an image per story,
  a "needs shot" column, items dropped by Amir, and a hard gate: verify the store shows 2.7.0
  before the announcement posts. Social copy rule: one hook, not a feature dump; no sirens, no
  "now available".
- Where: `content/gerowallet/announcement/v27-launch-week-tweets.md`, memory `gero-v27-release.md`,
  `social-copy-style.md`, `confirm-post-time.md` (post at the planned traffic hour, never "now").
- How it maps: the release-day playbook already orders the day. What it lacks is the story table
  for the whole release window: T-14 teaser (process), T-7 the video, day 0 morning (face into the
  lens), day 0 evening (Bandcamp), day 2 the collab, day 5 the studio, day 10 the live or radio
  thing. One story per post, asset per story, "needs shot" column, and the gate: Spotify link
  live and clean, Bandcamp flipped, before anything audience-facing posts.
- Effort: S for the table, M to fill it per single.
- What must change: `marketing-campaign-template.md` gets the story table; the release skill shows
  it at the plan stage. Post time stays the traffic hour, as D5 says (release morning).

### 5. A lifecycle sequence keyed on behaviour, not on the calendar

- What: Nexus trial mail: welcome on verification, day 3 split on whether the person did
  anything, day 6 notice, day 7 converted. Framed as relationship mail, not marketing; no prices
  except where they belong; every link carries UTM.
- Where: `content/nexus/email/IMPLEMENTATION.md`, memory `nexus-email-sequence.md`.
- How it maps: D5 says "one mail per release, nothing else", and that stays. The welcome mail is
  not a newsletter, it is the relationship mail Gero also separated: when someone joins the list
  (Bandcamp or Buttondown) they get one mail with the track, the next date, and where to follow.
  Then one release mail per single. The behaviour branch (opened vs not, bought vs not) is a
  later test once the list passes 100.
- Effort: M (two templates, Buttondown automation for the welcome).
- What must change: a decision whether Buttondown or Bandcamp's own message tool sends it
  (Bandcamp help does not document a send tool, per the 11-05 research). Copy follows the DM
  shape: warm open, the track, one link, "Hope you will like it".

### 6. The CTA and link rule: every mention is a real link, every piece has one next action

- What: in Gero blogs every product mention must be a real link with a CTA, never plain text or a
  placeholder; every article ends with one linked CTA. On X the link goes in the first reply, the
  pointer emoji is fixed, the CTA phrase is fixed ("Start the 7-day Builder trial").
- Where: memory `blog-link-cta-rule.md`, `nexus-tweets-agent.md`, `x-algorithm-research-2026.md`.
- How it maps: pick one CTA per platform job from D5 and never swap it: Spotify "follow", Bandcamp
  "buy or join the list", YouTube "subscribe", TikTok "use the sound". Where links work (YouTube
  and SC descriptions, Bandcamp about, Stories link sticker, bio, email) the link is real and
  campaign-tagged (`bandcamp_links.py` already does `?campaign=`). Captions carry the action in
  words. One CTA per piece, never two.
- Effort: S.
- What must change: a six-line table in voice.md; ig and promo skills read it.

### 7. Every ticket names its metric; monthly gate with a look-back

- What: Q4 backlog rule: every ticket body is Why / Outcome / How we measure (metric ID) / How to
  execute / Verify / Source, and must cite a registered metric. Monthly gates with names (BUILD,
  CLIMB, PRESS, CLOSE) reviewed on the 1st, a gaps section, a trigger rule written down in
  advance (green market doubles the ads budget). The pricing playbook treats a promo as an
  experiment with the decision it will answer.
- Where: memory `q4-agile-backlog.md`, `q4-war-plan.md`, `nexus-pricing-playbook.html` (TL;DR
  and status board).
- How it maps: we already have `targets.json`, the D5 measures per platform, `outcomes.stats` per
  release and the SC 600-1000 pre-committed rule. Missing: a metric line on every ticket in
  `tickets.json` (one field), a gate on the 1st of each month that reads targets vs actual, and
  one written trigger rule per experiment (TikTok go/no-go at 8 weeks already is one).
- Effort: S for the field, M for the gate page.
- What must change: tickets without a metric go to "proposed" until one is named.

### 8. A partner dossier before any collab goes public, and favour who we work with

- What: before the FluidTokens announcement Gero wrote a dossier: who they are (verified), their
  products, numbers "handle with care", reputation signals, the relationship as the partner
  describes it, which claims are safe, announcement angles, open blockers. Then: "design partner"
  framing, never "customer #1", never dunk on the partner's past vendors. Featuring policy: favour
  who we work with, one shared list every script reads.
- Where: `docs/gtm/research/fluidtokens-partner-dossier.md`, memory
  `nexus-official-announcement.md`, `featuring-policy.md`.
- How it maps: D5 has one peer collab per song. Each collab gets a half-page: verified handle
  (export/SI/profile, rule 10-13), what they did, what each side may say, tags and credits, the
  photographer credit rule, blockers (did they approve the clip). The favour list is our
  reciprocators and collaborators; the never list is only accounts that asked not to be tagged.
- Effort: S per collab.
- What must change: the promo agent and ig skill read the dossier before a caption with a tag.

Not taken into the eight but worth a line: the pricing stance ("premium, and we can prove why";
discounts time-boxed as experiments, never a permanent floor change) maps cleanly onto Bandcamp:
keep a real price, use Bandcamp Fridays as the honest time-boxed moment, test a bundle, and never
run the "free download" as the default. Also the series rule (number every recurring format #1,
#2) fits the studio and process formats if a series starts.

---

## 3. Installed skills: which fit the songs-era launches

Parent folder `/Users/amir/Desktop/Inch of Shadow/.claude/skills/`:

- `launch`: partial. Built for SaaS and Product Hunt. The launch-tier idea (big, medium, small
  release treated differently) and the pre-launch QA checklist transfer; the channel list does not.
- `co-marketing`: partial. The partner-finding frame (shared audience, what each side gives)
  fits the peer collab per song; the integration and webinar playbooks do not.
- `community-marketing`: later. A Discord or broadcast channel at 16 emails and 68 Spotify
  followers is a room with nobody in it (section 4). Keep for the album phase.
- `influencer-marketing`: low. Paid creator deals are out; the vetting and disclosure parts
  could apply if a TikTok creator ever uses the sound for a fee, which D5 does not plan.
- `marketing-psychology`: small and careful. Anchoring helps set the Bandcamp price and bundle;
  scarcity and urgency clash with the voice unless the deadline is real (Bandcamp Friday is).
- `public-relations`: partial. The journalist etiquette and podcast prep are usable; our press
  template already covers the pitch shape. Do not let it rewrite the premiere ladder.
- `ads` and `ad-creative`: no. No budget, and Spotify Marquee, Countdown and Discovery Mode are
  closed at our size (D5). Revisit only if a single breaks out.
- `analytics`: no, except the UTM habit. There is no website or GA4; Bandcamp campaign links and
  the stats snapshots are the analytics.
- `reverse-engineer-marketing`: yes. A dated growth teardown of one artist in our scene (when
  they grew, what they did that month) is exactly what the 11-05 research did by hand; the skill
  makes it a method. Good fit for the next-six-months questions.
- `research`, `research-deep`, `research-report`: yes, already in use.
- `llm-council`: yes for pre-committed decisions (the pricing stance, the album order).
- `brand`: yes, always, for anything visual.

Synced skills (`~/.claude/skills/synced/...`):

- `release-platforms`: yes for the Spotify pitch part; the Beatport and Traxsource parts are
  electronic-lane only.
- `music-platform-seo`: yes for SoundCloud and Bandcamp bios, tags and descriptions, songs
  included.
- `premieres`: yes, but its channel logic is electronic-lane; the songs-era channel list must be
  built before it ranks anything.

Inchofshadowcode skills: `release`, `release-prep`, `promo`, `bio`, `ig`, `sc`, `discover`,
`enrich`, `sync` are the actual machine. They fit; they need the methods above (message layer,
status tags, banned list, story table, CTA table, metric field) as inputs, not replacing.

---

## 4. Web evidence per practice (light, no Wikipedia)

Pre-save as lead capture vs email

- A self-built pre-save is not realistic any more: Spotify restricted extended Web API access to
  established apps (2025-04) and cut development mode further (2026-02). Only large vendors can run
  pre-saves for strangers. [OFFICIAL, Spotify developer blog, read in the 11-05 research]
- Feature.fm Free collects emails but will not show them; Hypeddit Rookie lists no pre-save;
  Laylo $25/mo. [OFFICIAL vendor pricing pages, 11-05 research]
- Trade and vendor pieces agree a pre-save without an audience is a vanity number, and the email
  list is the lasting asset ("an artist with 500,000 listeners cannot email any of them").
  [CLAIMED, interspacemusic.com, patchbay, Hypebot summary]
- Read for us: the pre-save's real yield is the Spotify follow (Release Radar), not emails. Emails
  come from Bandcamp and the Buttondown link. Matches D5.

Superfan tiers (Bandcamp subscription, Patreon style, SoundCloud Fan Support)

- Bandcamp subscriptions: artist sets the price, picks which back-catalogue items come with it,
  same 15% then 10% share as digital. No public 2026 take-up data found. [REPORTED, Rain News,
  Complex; no primary 2026 figure]
- SoundCloud Fan Support: on Artist Pro, waitlist, US artists and US payers only at launch, no
  SoundCloud cut (processing fees only), "more markets in 2026" with no date. Not available to a
  Berlin account today. [OFFICIAL, soundcloud.com/getstarted/fan-support]
- Patreon: State of Create (2025) reports about $52 per fan per year and $110 per paying member on
  average; an older Hypebot piece notes only about 2% of Patreon creators earn above minimum wage.
  [REPORTED, Hypebot coverage of Patreon's report]
- Read for us: a paid tier needs a base first. Bandcamp subscription is the only one open to us
  and costs nothing to switch on; earliest sensible moment is the album, with the singles as
  the back catalogue it unlocks.

Merch as the product line

- Hypebot merch margins guide (2026-02-06): tees 50-70%, hoodies the highest revenue per unit,
  pins, stickers and totes the highest percentage; start with a core three (a good tee, a
  heavyweight hoodie, a limited vinyl) and impulse add-ons; order small batches; drop anything
  under 50% margin. [REPORTED, Hypebot; the listed margins do not all match the cost ranges]
- MIDiA merch and ticket buyer survey (1,000 US buyers, write-up 2026-03-25): expanded rights
  grew 21.5% in 2025; just under half mainly buy from big artists; 39% sometimes feel exploited;
  younger buyers want variety and subtle insider branding over a logo; "nurture fandom before
  monetising it". [REPORTED, Hypebot write-up of MIDiA]
- Read for us: merch is a product-line extension for later, not a launch tool. If anything, one
  subtle item that fits the look (a tote or a pin), after the first songs have an audience.

Launch cadence: singles as product drops

- Luminate 2025 year-end, via Hypebot (2026-06-09): 88% of tracks on streaming got under 1,000
  plays in 2025. Advice: plan one to two months before, keep promoting one to two months after,
  pitch editorial 10-14 days ahead, keep metadata clean, review after each release. [REPORTED]
- Spotify: one song per artist per week in Release Radar; only one song can be pitched at a time;
  track 2 of a released two-track single can never be pitched. [OFFICIAL, Spotify for Artists
  support, 11-05 research]
- Waterfall: each drop is its own release with its own pitch; distributor and vendor blogs
  recommend 4-8 weeks between singles; no primary dataset shows waterfall outperforming.
  [CLAIMED, Symphonic blog 2026-02, OnesToWatch, playlistsupply]
- Read for us: the cadence is already right (one single, one pitch, one Release Radar push). The
  product lesson is the "after": a release is a 2-month window, not a day.

Community before launch (Discord, broadcast channels)

- Luminate 2025 midyear, via trade press: fans on Discord are about 200% more likely to tip
  artists than the average US listener. [REPORTED]
- Instagram broadcast channels: anyone can view, only joined followers get notifications,
  collaborators can be added; guides say open a few weeks before a release and that Discord makes
  sense once there are roughly 500-1,000 engaged fans. [OFFICIAL for the feature; CLAIMED for the
  thresholds, musictech.com, orphiq.com]
- Read for us: an IG broadcast channel is free and fits "the first hours of each release" job; a
  Discord is premature.

"1,000 true fans" evidence

- The idea is Kevin Kelly's 2008 thesis; Li Jin's 100 true fans (2020) is also a thesis. No source
  found that tests whether 1,000 fans sustain a career. [REPORTED, Hypebot, recordjet]
- What is measured: Luminate puts superfans at about 20% of US listeners (2024 and 2025);
  Hypebot's Superfan Week cites Luminate's year-end: superfans spend 68% more on music per month,
  126% more on merch, 76% more on physical. MIDiA with SoundCloud: about 1.9% of listeners drove
  about 42% of revenue under fan-powered royalties. [REPORTED, secondhand for the 2025 figures]
- Read for us: the number that matters is not 1,000; it is the ratio. The 11-05 lessons file
  shows 3,850 listeners to 64 followers (1.7%). A product would call that the conversion problem,
  and that is where D5 already points.

Direct-to-fan sales data (Bandcamp Fridays)

- Bandcamp Fridays paid $154m since March 2020, $19m in 2025; artists get about 82% on regular
  days (15% digital, 10% physical, waived on Fridays). Eight dates in 2026: Feb 6, Mar 6, May 1,
  Aug 7, Sep 4, Oct 2, Nov 6 (today), Dec 4. [REPORTED, Music Business Worldwide 2025-12-22]
- First 2026 Friday: $3.6m in 24 hours; May 1: $3.3m; $6.9m year to date by May. [REPORTED,
  RouteNote, Digital Music News]
- Bandcamp's own guide asks for an 8-week private draft for a Bandcamp Daily pitch; Discover ranks
  by sales. [OFFICIAL, read in the 10-21 Bandcamp research]
- Read for us: Bandcamp Friday is the one honest, pre-dated urgency in music. Line the Bandcamp
  release of a single up with a Friday when the Spotify date allows (D5 already says so).

MIDiA, Bandcamp, Music Ally, Hypebot in 2026

- MIDiA: merch and ticket buyer survey (March 2026), as above; its SoundCloud fan-powered royalties
  study and the "artist subscriptions are the superfan opportunity" report are older. No 2026
  MIDiA independent-artist report was found. [REPORTED]
- Bandcamp: 2026 Friday totals as above; no 2026 subscription data published. [REPORTED]
- Music Ally: no 2026 piece on pre-save vs email found in this pass. [not found]
- Hypebot: merch margins (Feb 2026), the 88% problem (Jun 2026), MIDiA survey write-up (Mar 2026).
  [REPORTED]

---

## 5. The one product rule we lack (my judgement)

**A new fan gets nothing.** In product terms: there is no activation step. Someone follows on
Spotify, subscribes on YouTube, joins the Bandcamp list, or follows on SC, and the next thing they
hear from Inch of Shadow is the next release, weeks or months later. Gero's single most
product-like asset is the welcome-then-branch sequence; every other method above is a
discipline, this one is a mechanism.

What it would be, in our terms: the moment someone joins the list they get one mail (the track,
the next date, where to follow, "Hope you will like it"); a new Spotify follower meets a pinned
Artist Pick that says what comes next; a new SC follower gets the follower-only early drop that
D5 already plans. One message, once, per door. It is not a newsletter and does not break "one
mail per release, nothing else".

Why this over the others: the 1.7% listener-to-follower ratio in `release-lessons.md` says the
reach exists and the catch does not. The research in section 4 says the same from the market
side (the list is the asset, the pre-save is a vanity number). The rest of Gero's method (facts,
bans, metrics, story table) we mostly have in weaker form; this one we do not have at all.

Marked as judgement; Amir decides.

---

## 6. Do-not-take list

- The X content engine and anything that posts on a schedule from a queue. D5 needs no X; the IG
  and SC engagement code is hands-off, and posting is Amir's.
- The blog SEO machine (Contentful, GSC, GA4, indexing pings). No website; the other agent covers
  the "if we ever own a site" case.
- Paid ads logic ($200/mo, exact-match claims). Closed at our size; the voice does not sell.
- "Never give rivals free publicity" as a policy. In a music scene the peers are the network;
  tagging and reposting them is how the collab per song works. Keep only "verify the handle".
- "No free tier" as a literal rule. SoundCloud, YouTube and the TikTok sound are the free trial
  and must stay free. Keep the stance behind it: Bandcamp has a real price, premieres charge,
  discounts are time-boxed experiments, never the default.
- Competitor comparison pages, pain-to-message tables against named artists, objection handling
  that names rivals. Positioning names a neighbourhood, not an enemy.
- Data-tweet formats (Top-5 lists, weekly market video) and hook-first "reply-bait" closers.
  Feedback asks are banned in our copy and meta lines are out of tune.
- B2B sales CTAs ("contact sales", pricing anchors, trial countdown mails with prices). Our CTAs
  are follow, join, buy, use the sound.
- Enterprise proof assets (status page, SLA, SOC 2). The music equivalent is a radio play or a
  premiere channel, and small numbers are not broadcast (Gero's own rule).
- Fake or undisclosed engagement accounts. Declined on the Gero side too; not a question here.
- Em-dashes from the Gero internal docs. Their own rule bans them in published copy; ours bans
  them everywhere.
