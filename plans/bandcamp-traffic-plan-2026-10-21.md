# Bandcamp traffic + revenue plan (automation view)

2026-10-21, updated the same day after the deep research (`plans/bandcamp-discovery-research-2026-10-21.md`). Tickets BC-01 to BC-11 in `plans/tickets.json` (lane Bandcamp). Content is out of scope here.

## The rule that shapes everything

Bandcamp's Acceptable Use Policy (page dated 2026-06-10) bans scraping "through the use of scripts, robots, bots, spiders, scrapers, crawlers, or other automated means", any data mining, feeding Bandcamp content into AI models, and spam. Breaking it can cost the account, and Bandcamp is the one place that pays per sale. It has no clause on self-purchases or follow-for-follow, but that is not permission: buying his own releases would also pollute the recommender and his stats.

So there is **no IG/SC-style engine on Bandcamp**: no follow bot, no scraping other artists' buyers, no scripted stats reads. The automation happens around Bandcamp: our IG/SC/YT engines send traffic in, and Bandcamp's own tools (exports, campaign tracking, follower messages, listening parties, discount codes) measure and convert it.

Bandcamp has no likes, comments or DMs, and fans follow artists, not the other way round, so there is no follow-back loop to run.

## How discovery works (research 2026-10-21, corrects the June notes)

- **Sales drive placement.** Discover shows what fans are buying, in two views Bandcamp names: best-selling and new (GM Dan Melnick, Music Week 2026-02-09, checked). With 2 sales in 30 days he cannot reach best-selling. Tags only make a release eligible for a list.
- **There is a recommender, and it runs on purchases.** "A little bit of collaborative filtering... other fans who bought this also bought this" (Melnick, checked). No audio analysis, no personal feed. Every buyer who also owns similar Berlin / EBM / dark disco releases links him to those pages. This is why buyers from the scene (MM Discos audience, BC-10) are worth more than random buyers.
- **Followers are the owned channel.** Since 2026-07-16 fans can filter Discover to "artists you follow"; followers also get the release email and listening-party invites. It only reaches people who already follow, so the job is still turning outside traffic into followers and buyers.
- **Location filter uses the profile location**, not a "berlin" tag (Bandcamp blog 2023-12-12).
- **The featured track** is what a stranger hears when a release shows in Discover (official). Pick it on purpose.
- **Pay more:** 25-30% of transactions pay above the price (Melnick 2026). The old "40%" is from 2012.
- **Bandcamp Friday:** Nov 6 and Dec 4 left in 2026. Only Bandcamp's share is waived, processor fees stay. Small acts get buried that day (RA). Use it to message his own fans, not for discovery.
- **Bandcamp Daily:** no published submission route, editors claim strict independence, team cut in 2023. Low odds.

## Where we stand (his artist account, read by hand once, 2026-10-21)

| Metric | All time (since 2024-11-16) | Last 30 days |
|---|---|---|
| Plays | 2,333 | 49 |
| Visits | 595 | 20 |
| Sales | EUR 62.50, 31 sales, 27 buyers (incl. label releases) | EUR 2.50, 2 sales |
| Followers | 51 (44 at the July message) | |
| Mailing list | 16 addresses, 6 new since the 04-05 export | |
| Embed plays | 16 | 0 |

Top played: In Between Spaces 541, ACID Gangsta 376, Dark Scales 322, The Alchemist Ritual 289, The Cure 242. Top sellers: The Alchemist Ritual (6), The Tour Remix (4), The Cure (4).

Where visits come from (all time, 595):

| Source | Visits |
|---|---|
| Direct (unknown origin) | 266 |
| mmdiscos label page | 157 |
| Bandcamp home page | 49 |
| Google search | 46 |
| Bandcamp search | 13 |
| ecosia | 6 |
| Discover dark-disco | 5 |
| Facebook | 4 |
| chatgpt.com | 4 |
| soundcloud.com | 2 |

What this says:
- Outside traffic and the label page carry him; Discover sent 5 visits ever, which matches the research.
- SoundCloud sent 2 visits ever. Fixed on 2026-10-21 (BC-02: 9 tracks + 1 set now link with campaign links).
- 266 "Direct" visits cannot be traced. Campaign links (BC-07, done) fix that from now on.

## The plan (tickets, in order)

**Done**
- BC-07 Campaign links (`?campaign=<channel>`, `bandcamp_links.py`).
- BC-02 SC buy links on 9 tracks + Meltscape EP set (sc-buy, sc-mix).

**P1, send traffic in and measure it**
- BC-04 Bandcamp early in Hypeddit smart links + Linktree; release-checklist rule. (in progress)
- BC-03 YouTube descriptions, Bandcamp top line on the 11 videos (campaign=yt-desc).
- BC-01 Stats from official exports + RM block. Every 3 months (Amir, 10-21; next ~2027-01-21): raw data report + mailing list export, Stats-page numbers by hand.

**P2, convert visitors into followers and buyers**
- BC-06 Bandcamp Friday + Listening Party per release: release day of the Half the Night EP (date open) and Dec 4 follower messages, one free listening party per release (invite, reminder and follow-up buy emails to followers).
- BC-09 Pricing and bundles: keep EUR 1.50 per track (Bandcamp default) and "pay more" on; EP price about EUR 4 (Bandcamp's own guide for 6 tracks or fewer); discography bundle with discount. Fees eat about 23% of a EUR 1.50 sale, bundles keep more per sale.
- BC-10 Scene buyers (hand-read supporter names, matched to IG/SC). Matters more now: scene buyers feed the co-purchase recommender.
- BC-11 Artist page redesign in his vibe.

**P3, hygiene**
- BC-05 Page basics, checked by hand: profile location Berlin, featured track chosen per release, clean canonical tags. Needed, not a growth engine.
- BC-08 Bandcamp-based labels and curators into /outreach; Bandcamp Daily pitches lowest priority.

## Watching, no action

- Bandcamp Clubs (2025-09-01, USD 13/month, curator-picked): launch clubs do not fit his genres.
- Unknown: how best-selling is ranked, which fields search indexes, any limit on follower messages, whether discount codes need Bandcamp Pro.

## Dropped

- Supporter-graph scraping of other artists' buyers (policy). Replaced by BC-10 hand reading.
- Weekly scripted Stats read and tag-drift script (policy).

## Not doing

- No paid API calls, no edits to IG/SC engagement code/config/state.
- No Bandcamp setting changed without his go per change, old value recorded first.
