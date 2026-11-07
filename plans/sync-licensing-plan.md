# Sync Licensing Plan — Inch of Shadow

Created: 2026-07-27. Owner: Amir. Status: DRAFT for review.
Horizon: August 2026 to June 2027 (11 months, reviewed monthly).

## 1. Objective

Build sync licensing into a real revenue channel for the catalog:
first placements within 6-9 months in the most accessible lanes (indie games,
trailer libraries, boutique agencies), building toward premium lanes (TV drama,
ads, AAA games) as the vocal pop/rock material arrives from Q1 2027.

Two catalog phases drive the whole plan:

- **Phase A (now):** dark disco, EBM, acid, electro, techno. Mostly instrumental,
  analog, self-owned. Best lanes: video games (narrative, horror, cyberpunk,
  racing), trailer music, thrillers and club scenes in film/TV, fashion film.
- **Phase B (from ~Q1 2027):** electronic pop/rock with own vocals. Unlocks the
  vocal-driven lanes: prestige TV drama, ad campaigns, EA FC-type game
  soundtracks, sync agencies that favor "authentic vocals" (Bank Robber,
  Secret Road). Rule from day one: every Phase B song is written and delivered
  sync-ready (see section 4).

## 2. Ground truth (verified 2026-07)

- **Money shape.** Upfront sync fee plus backend performance royalties when the
  placement airs on broadcast. Games pay upfront only; interactive play sits
  outside performance-royalty collection, so on game deals the fee is the whole
  deal and must be negotiated accordingly.
  Source: themusiccourse.com/blog/video-game-sync-licensing
- **Typical fees.** Indie games $500-2,000 per track; royalty-free library
  placements $100-600; a 15-track indie game soundtrack runs ~$1.5k (library
  sourced) to ~$30k (traditional licensing). TV/film/ads range far wider and
  scale with the production. AAA pays well above all of this.
- **One-stop is the trump card.** Inch of Shadow ICR releases are fully
  self-written, self-produced, self-owned: one email clears everything.
  Productions on deadline pay a premium for that. Tracks released via MM Discos,
  Stereo Society, NaNa Disc are NOT automatically pitchable; sync rights depend
  on those label deals (see 3.2).
- **The anti-AI angle is live.** Supervisors in 2026 are nervous about AI
  provenance and clearance risk. "All analog, no AI, one owner" is a real
  differentiator; lead with it in every pitch (same angle that converts
  curators).
- **EA FC reality check.** ~100-117 songs/year, curated for almost a year by
  EA's music department (Steve Schnur). No open submission funnel; tracks
  arrive via sync agents, labels, distributors with EA relationships, plus EA's
  own scouting. Route = get represented, not "submit a form". EA FC skews
  vocal/global/anthemic, so this is a Phase B target at best.
  Source: bbc.com/news/articles/cr75zmr0m8vo
- **Supervisors' filter.** Winning pitches: 3-5 relevant tracks (never a dump),
  100% confirmed clearance, WAV quality, an instant-play link (no login, no
  attachment), metadata visible (BPM, key, mood, contact). One follow-up after
  two weeks, never more. Source: dropcue.app/blog/how-to-pitch-music-supervisors-2026

## 3. Foundation phase (August 2026) — blockers first

Nothing gets pitched until these four are done.

### 3.1 PRO decision (open decision — Amir decides)

Not registered anywhere yet. Without a PRO, backend royalties from any broadcast
placement evaporate. Two routes:

| Route | For | Against |
|---|---|---|
| **GEMA** (€90 one-off admission, may be waived for newcomers, + €50/year) | Strongest collection for German exploitation: club plays, live sets, German radio/TV. Natural for a Berlin club artist. | Members must register ALL works with GEMA; no flexibility for PRO-free deals (some royalty-free libraries and buyout game deals want non-PRO music). Hard to exit. |
| **US PRO (BMI free / ASCAP $50) + publishing admin (e.g. Songtrust)** | More flexible for international sync; admin registers works with PROs worldwide and collects globally. | Weaker/slower collection of German performance income via reciprocal deals; admin takes a cut (~15%). |

Recommendation: decide AFTER the rights inventory (3.2) and after confirming
with GEMA directly how they handle gratis/direct sync licenses in 2026. This is
a one-way door; worth one hour of verification. If mostly targeting
international sync and buyout-friendly game deals, the US PRO + admin route is
the flexible one; if German club/radio/live income matters most, GEMA wins.

### 3.2 Rights inventory (one afternoon)

For every released track, record in a single sheet: writer share, master owner,
sync rights holder, PRO status, samples (none expected), co-writers (none
expected). Specifically: pull the MM Discos, Stereo Society and NaNa Disc
contracts and answer "who can approve a sync and who gets what split?" Only
one-stop tracks go into the pitch catalog; anything ambiguous is excluded until
clarified. Never pitch an uncleared track: one blown clearance burns the
supervisor relationship permanently.

### 3.3 Sync-ready deliverables per track

For the 8-10 strongest one-stop tracks:

- Full mix WAV (mastered)
- Instrumental (trivial for Phase A; mandatory habit for Phase B)
- Clean edit where relevant
- Stems (grouped: drums, bass, synths, atmos, vocals)
- Alt edits: 30s, 60s, loop-friendly cut (games loop for 45 minutes; clean loop
  points are a selection criterion)
- Metadata embedded and in the catalog sheet: BPM, key, moods (3-5), genre
  tags, "sounds like" references, duration, contact, rights line
  ("100% one-stop, Inch of Shadow / ICR")

Candidate for tooling: generate the sync catalog sheet from `releases/*.json`
plus a new per-track sync block (instrumental path, stems path, loop points,
moods). Extend `metadata_utils.py` later; manual sheet first.

### 3.4 Pitch kit

- One-sheet: who (Berlin, analog hardware, self-owned, dark dance wave), what
  (lanes served), the no-AI line, placements as they come.
- Instant-play pitch link (requirement: opens in browser, no login, shows
  metadata). Options: DISCO (industry standard, paid), Bandcamp private
  streams, or a small self-hosted player page (privacy-friendly, fits the
  local-first stack). Decide in August.
- Email templates per lane (game audio director, trailer house, agency,
  supervisor) — 5 sentences max, specific reference to their work, one link.

## 4. Channels, ranked by fit and effort

### Lane 1 — Indie video games (best Phase A fit, most underfished)

Instrumental, loopable, atmospheric dark electronic is exactly what narrative,
horror, cyberpunk and racing games license. Developers list contact emails on
their sites; audio directors are findable on LinkedIn.

Process: study Tunefind's game pages (800+ games indexed) for what actually gets
placed in the lane; build a target list of 30-50 indie studios whose aesthetic
matches (Berlin/EU studios first); short personal note + 2-3 relevant links.
Store targets as a new contact category in Scene Intelligence; send via Tool 4
(Email Outreach) with the existing throttling discipline.
Expected: $500-2,000 per track, upfront-only. Slow, compounding.

### Lane 2 — Trailer music houses (dark hybrid electronic wanted)

Dark tension, atmospheric, electronic-hybrid cues are core trailer inventory.
From the verified 2026 open-submission list (dropcue.app/blog/best-sync-licensing-companies-2026):

- **Gothic Storm** (UK) — volume-driven, most accessible entry point, open to
  newer composers; dark ambient/suspense/action fits.
- **Elephant Music** (UK) — contemporary palette, dark atmospheric and
  electronic-infused cues; accepts submissions.
- **Tonal Chaos Trailers** (LA) — dark tension/hybrid; wants full packages
  (mix + instrumental + stems + edits); selective.
- Position Music / Audiomachine — top tier, revisit after first placements.

Note: trailer work may mean writing TO the format (energy arcs, impact
moments), not just licensing existing catalog. Treat as a craft experiment in
Q4: 2-3 purpose-built dark trailer cues.

### Lane 3 — Sync agencies (representation; the road to EA-tier doors)

- **Terrorbird Media** — most accessible major indie agency; explicitly open to
  electronic and experimental, takes DIY artists, values prolific output.
  Submit Phase A. First-choice application.
- **Bank Robber Music** — indie/alternative/electronic but favors authentic
  vocals; prime Phase B target (Q1-Q2 2027).
- **Secret Road** — genre-agnostic, quality-obsessive; Phase B target.
- **Musicbed** — platform/agency hybrid; cinematic instrumental + ambient +
  electronic fits Phase A; curated, non-exclusive-friendly.
- **Bodega Sync (Symphonic)** — zero cost, commission-only, existing client
  priority in their supervisor blast. Low conviction is fine: treat as a free
  parallel bet (30 minutes to apply), not the strategy.

Rule for all agency/library deals: read exclusivity terms. Non-exclusive keeps
options open. Never accept re-titling deals. Never sign per-track exclusivity
casually; exclusive is acceptable only with a rep actively pitching (agencies),
not with passive libraries.

### Lane 4 — Direct-to-supervisor (highest ceiling, most work)

Build a list of 20-30 supervisors working on productions that fit the dark lane
(thrillers, Berlin-set shows, club scenes, fashion/doc). Sources: IMDb Pro
(~$20/mo, only needed during list-building months), trade production
announcements, supervisor directories, LinkedIn. 3-track pitches, one follow-up
at two weeks, track opens/plays. This lane matures in 2027 when vocal material
widens what can be offered.

### Lane 5 — Marketplaces (passive floor, not the strategy)

Songtradr (free, non-exclusive, all genres): upload the cleared catalog once
deliverables exist; treat any income as bonus. Skip paid brief-services for
now: TAXI (~$300/yr) and Music Gateway get mixed-to-negative value reviews from
working composers for pure sync. Avoid Artlist/Epidemic-style exclusive
creator-economy catalogs; they conflict with everything else.

### Lane 6 — Events (relationship accelerant)

- **Most Wanted: Music 2026, Berlin, November 3-5** (nhow Hotel). Local, cheap,
  music-business focused with sync programming. Book it. Goal: 5 real
  conversations (supervisors, publishers, sync reps), not badge-collecting.
- **ADE, Amsterdam, October 2026** — electronic-industry density, sync panels;
  optional if budget allows.
- **GDC (San Francisco, March 2027) / PAX** — where game audio people actually
  are; decide in January once the game lane shows traction.

## 5. Month-by-month

| Month | Focus |
|---|---|
| **Aug 2026** | Foundation: PRO decision + registration; rights inventory; deliverables for top 8-10 tracks; pitch kit + catalog sheet; pick pitch-link tool. |
| **Sep 2026** | First wave: Terrorbird + Musicbed + Bodega applications; Gothic Storm + Elephant submissions; Songtradr catalog up. Build game target list (30-50 studios) from Tunefind research. |
| **Oct 2026** | Game outreach wave 1 (15-20 studios via Tool 4); ADE optional; start 2-3 purpose-built trailer cues; register everything with chosen PRO as it releases. |
| **Nov 2026** | Most Wanted: Music Berlin (Nov 3-5) with pitch kit ready; follow-ups from Sep/Oct waves; game outreach wave 2. |
| **Dec 2026** | Trailer cues finished and submitted; year-one review: response rates per lane, kill or double down; Half the Night EP tracks get sync deliverables at release, not after. |
| **Jan 2027** | Phase B begins: every pop/rock song written sync-aware (clean vocal takes, instrumental bounce, stems archived from the session). Supervisor list built (IMDb Pro month). GDC go/no-go. |
| **Feb-Mar 2027** | Direct supervisor pitching starts with mixed catalog (dark instrumentals + first vocal tracks); Bank Robber + Secret Road applications once 3-4 vocal tracks are release-ready; GDC if go. |
| **Apr-Jun 2027** | Compound: second submission round to every lane that responded; refresh agencies with new vocal material; re-pitch game studios that opened but passed; full plan review June 2027. |

## 6. KPIs (reviewed monthly, logged in this file)

- Pitches sent per lane / responses / catalog requests / placements / revenue.
- Leading indicator to trust: response and request rate, not placements
  (placements lag 6-12 months industry-wide).
- Kill rule: any lane with zero responses after two full waves and one rework
  of the pitch gets parked, and the effort moves to the lanes that answer.

## 7. Budget (nothing committed yet)

| Item | Cost | When |
|---|---|---|
| PRO: GEMA €90+€50/yr (or BMI $0 / ASCAP $50 + admin ~15% cut) | <€150 | Aug |
| Pitch link tool (DISCO or self-hosted) | €0-30/mo | Aug |
| IMDb Pro (list-building months only) | ~$20/mo x 2 | Jan-Feb |
| Most Wanted: Music ticket | ~€100-200 (verify) | Nov |
| ADE / GDC | optional, decide later | Oct / Mar |

Everything else in this plan is free and runs on existing tools (SI contact DB,
Tool 4 outreach, release JSONs).

## 8. Risks and honest expectations

- Sync is a 6-12 month lag business; silence is normal volume, not rejection.
- Dark electronic is a niche demand lane: steady but thin. The Phase B vocal
  material is what widens the funnel; protect that timeline.
- Exclusivity traps and re-titling deals are the main contractual danger; every
  contract gets read for grant scope, term, territory, and exit.
- The 2026-07 label-contract question (3.2) can shrink the pitchable catalog;
  resolve before any pitching, not after interest arrives.

## Open decisions for Amir

1. PRO route: GEMA vs US PRO + publishing admin (section 3.1).
2. Pitch-link tool: DISCO (paid, industry standard) vs self-hosted player.
3. Most Wanted: Music ticket — book?
4. Bodega Sync free application — file it as the parallel bet, or skip entirely?
