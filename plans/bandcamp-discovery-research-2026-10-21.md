# Bandcamp discovery and sales research (2026-10-21)

For: Inch of Shadow (51 followers, ~600 visits all time, 5 digital releases, EUR 1.50 per track, no merch).
Builds on: `plans/platform-algorithm-research-2026-06.md` (section "## Bandcamp") and `plans/bandcamp-traffic-plan-2026-10-21.md`.
Method: web search plus a small number of official pages (blog.bandcamp.com yearly archives 2023-2026, 6 help articles, Bandcamp Notes). No Bandcamp artist, fan, tag or Discover pages were opened.

Labels: **OFFICIAL** = Bandcamp says so (blog, help centre, or a named Bandcamp executive quoted in press). **REPORTED** = credible press or practitioner. **VENDOR/UNVERIFIED** = marketing blogs, PR agencies, SEO sites, scraper docs. Vendor numbers are never planning inputs. **STALE?** = source older than 2024.

Note: the help centre moved to `get.bandcamp.help/en/articles/...` (pages dated 2026-06-10 to 2026-06-30). Old `/hc/en-us/` links still resolve.

---

## 1. Bottom line

- **Still no personalized feed, but there IS a behavioural recommender.** Bandcamp's GM Dan Melnick (Music Week, 2026-02-09) says it uses "basic collaborative filtering" ("fans who bought this also bought this") and does not analyse audio. So "you may also like" on release pages is driven by co-purchases. One buyer who also owns similar records is what puts him on other artists' pages. OFFICIAL.
- **Discover ranks by people buying, not by tags alone.** Keyes (Hypebot, 2026-05-26) describes Discover as showing "albums and merch that other Bandcamp fans are buying". Melnick names two views: best-selling and new. With 2 sales in 30 days he cannot reach best-selling. Tags only get him into "new" lists, briefly, right after release. No source explains the ranking formula.
- **The location filter uses the artist's profile location**, not a "berlin" tag (Bandcamp blog 2023-12-12: browse "by genre, category, or artist location"). Setting the profile to Berlin is what counts. The "berlin" tag still helps tag search and combined tags. This corrects the June research.
- **The featured track is a real Discover lever** (OFFICIAL, 2023-12-12): it is the track a stranger hears when the release shows in Discover. Pick the strongest opening track on purpose.
- **Followers now matter in two places**: the release email (OFFICIAL) and, since 2026-07-16, a Discover filter that shows only artists you follow (OFFICIAL). Both reach only people who already follow him. Growing followers from outside traffic stays the main job.
- **The best thing a fan can do for him is buy and stay public.** Purchases go to the buyer's followers' feeds and into a newsletter of "what fans you follow bought" (Keyes, 2026-05). Each purchase is also a co-purchase signal for the recommender.
- **Pricing**: EUR 1.50 per track equals Bandcamp's own default since 2025-04-25 ($1.50). Bandcamp's data: albums at $7-10 make the most revenue per release, and "nearly 20%" of fans add extra in that range. Keep "let fans pay more" switched on. At EUR 1.50 the fees take roughly 23% (15% share + 5% + $0.05 processor rate), so bundles and full-price EPs keep more per sale.
- **Remaining Bandcamp Fridays: 2026-11-06 and 2026-12-04** (OFFICIAL). Only Bandcamp's share is waived; processor fees still apply. RA's "all fees waived" is wrong.

---

## 2. Surface by surface

| Surface | How placement works | Evidence | What he can do |
|---|---|---|---|
| **Discover** (bandcamp.com/discover) | Shows what fans are buying. Filters: genre/tag (combine several tags, 2024-04-25), format, artist location, and since 2026-07-16 "artists you follow" (`?fb=1`). Views named by Bandcamp: best-selling and new. The ranking formula, time window and whether a default/"surprise me" order exists are **not published**. | OFFICIAL: [blog 2023-12-12](https://blog.bandcamp.com/2023/12/12/discover-a-new-way-to-shop-on-bandcamp/), [blog 2024-04-25](https://blog.bandcamp.com/2024/04/25/new-in-discover-search-and-filter-by-combining-tags/), [blog 2026-07-16](https://blog.bandcamp.com/2026/07/16/discover-improvements-and-subsonic-implementation/), Melnick in [Music Week 2026-02-09](https://www.musicweek.com/digital/read/as-bandcamp-friday-returns-gm-dan-melnick-says-the-platform-is-an-even-playing-field-for-artists/093521), Keyes in [Hypebot 2026-05-26](https://www.hypebot.com/bandcamp-exec-shares-how-artists-and-music-get-discovered/). "Surprise me" sort: no source found. | Accurate genre tags; profile location = Berlin; choose the featured track; concentrate sales in a short window so a release has any chance in a niche tag's best-selling list. His own stats: "Discover dark-disco" = 5 visits all time. |
| **Search box** | Bandcamp has never documented which fields are indexed (title, artist, tags are visible in results; description, credits, location: unknown). | No official source. Scraper docs only (VENDOR). | One hand test: search a word that appears only in one of his descriptions or credits and see if the release appears. Record result. |
| **Tag pages** | Since the 2023 Discover relaunch, tag browsing runs through Discover (tag search, combined tags). Whether old `/tag/x` pages are separate surfaces is unverified. | OFFICIAL for tag search in Discover (2024-04-25). Tag spelling rules: [help: tags](https://get.bandcamp.help/hc/en-us/articles/23020708170519-What-are-tags-and-how-do-I-use-them). | Use autocomplete-matched tags (BC-05). |
| **Location** | "Artist location" filter in Discover. | OFFICIAL (2023-12-12). | Profile location = Berlin (check by hand). |
| **Fan feed (app + web)** | Follow-based, not recommended: shows new releases from followed artists/labels and purchases by followed fans. | OFFICIAL in substance (Keyes 2026-05: followers of a buyer "will be able to see that"). Feed design described in older sources (STALE? 2013). | Get buyers who are active fans (with public collections). Nothing to set. |
| **"What fans you follow bought" newsletter** | Bandcamp emails a roundup of purchases by fans you follow. | OFFICIAL (Keyes, Hypebot 2026-05-26). | Same as feed: real buyers spread him. |
| **Follower release email** | Sent to all followers when a release is published; artist can attach a message. Mailing list is told when a pre-order goes live in full. | OFFICIAL: [blog 2020-05-27](https://blog.bandcamp.com/2020/05/27/new-messaging-features-up) (STALE? but still the documented flow), [help: pre-order 2026-06-30](https://get.bandcamp.help/en/articles/15263066-how-do-i-set-up-a-pre-order). | Always write the release message. Timing of the send and behaviour for backdated releases: unknown. |
| **"You may also like" / bought-together** | Collaborative filtering on co-purchases; no audio analysis. Shows "supported by N fans who also own". | OFFICIAL (Melnick, 2026-02-09). | Buyers who also own similar Berlin/EBM/dark disco releases link him to those pages. Scene-adjacent outreach (MM Discos audience) is the route. |
| **Fan collections / wishlists / "supported by"** | Every purchase shows on the buyer's public collection and on his release page as a supporter. | OFFICIAL in substance; well known. | Nothing to set. Each sale is visible proof. |
| **Bandcamp Playlists** | Beta since 2025-05-22. Fans build playlists only from owned music, in the mobile app. Non-owned tracks play a limited number of times (3 by default "unless the artist sets a different limit"). Web editing and playlist following were "coming later"; shipped status unknown. Since 2026-07-16 playlists also sync to Subsonic clients. | OFFICIAL: [blog 2025-05-22](https://blog.bandcamp.com/2025/05/22/introducing-bandcamp-playlists-beta), [blog 2026-07-16](https://blog.bandcamp.com/2026/07/16/discover-improvements-and-subsonic-implementation/). Practitioner: [Yewknee 2025](https://yewknee.com/blog/bandcamp-playlists-2025) says web adding was still missing. | Low value at his size. Note the per-track play limit is an artist setting. |
| **Bandcamp Daily** (incl. Album of the Day, "Best Electronic" monthly, Essential Releases, Scene Reports) | Editor-chosen. "Strict independence", no paid placement (Melnick). No submission process is published. Bandcamp Daily lost about half its editorial staff in Oct 2023 (DJ Mag reported 3 left). Keyes still Editorial Director (2026). | OFFICIAL (independence, Keyes role). REPORTED (staff cut). Pitch-success rates ("~5%", "95% rejected"): VENDOR/UNVERIFIED. | Long shot. Realistic only through a label or a scene story. Keep BC-08 as low priority. |
| **Bandcamp Notes** (Substack) | Weekly-ish newsletter since 2025-05-05. "Cool Band Alert" (Wednesdays, one artist), "I Love This Record" (first Friday), "The Helpline" (last Friday). | OFFICIAL: [Introducing Bandcamp Notes](https://daily.bandcamp.com/features/introducing-bandcamp-notes), [archive](https://bandcamp.substack.com/archive). | One artist per week across all genres. Not a plan input. |
| **Bandcamp Radio** | Genre shows (electronic among them) built around an artist interview. | OFFICIAL (Keyes 2026-05). | Editorial; no pitch route known. |
| **Bandcamp Clubs** | New since 2025-09-01. $13/month subscribe-to-own clubs, one curator-picked record per month plus interview and listening party. Launch clubs: Dance Around the World, Jazz-ish, Kosmos Klub, The Hard Stuff. | OFFICIAL: [blog 2025-09-01](https://blog.bandcamp.com/2025/), [MBW](https://www.musicbusinessworldwide.com/bandcamp-launches-human-curated-bandcamp-clubs-at-13-a-month/). | Not reachable for him now. Watch for an electronic/EBM club curator. |
| **Homepage "Now Selling" ticker** | Live stream of sales. Any sale can appear. | OFFICIAL (Keyes 2026-05). | Pure luck of timing. His stats: "Bandcamp home page" = 49 visits all time, more than Google. |
| **Mobile app home / feed** | Follow-based feed; no evidence of a recommendation home screen. | No 2025-2026 official app post found. | Nothing. |
| **Listening Parties** | Artist schedules a timed playthrough of any public release (pre-order counts) with chat. Followers get an invite email; RSVPs get reminders; attendees get a follow-up buy email. Free. Still promoted by Bandcamp in 2026. | OFFICIAL: [blog 2023-08-08](https://blog.bandcamp.com/2023/), Keyes 2026-05. Mechanics: [Hypebot / Brian Hazard 2023-10-26](https://www.hypebot.com/how-to-set-up-a-bandcamp-listening-party-and-why-you-still-should/) (STALE?). | One extra follower email per release at zero cost. Reach = his 51 followers plus whoever he brings. |
| **Google / web search** | Each release and track has its own clean-URL page. Bandcamp publishes nothing on SEO. | REPORTED, old (waxy.org, STALE?). His own data: Google 46 + ecosia 6 + chatgpt.com 4 = ~9% of visits. | Title + description text with genre, city, gear words. Low effort, small but real. |

---

## 3. Artist levers ranked for a 51-follower act

1. **Send outside traffic to Bandcamp, tagged with campaign links.** OFFICIAL: a campaign code on a link shows visits in the Campaign Tracker (Tools page) and sales under "referrer" in the exported sales report ([help: promote live stream](https://get.bandcamp.help/en/articles/15263381-how-should-i-promote-my-live-stream)). Bandcamp's own advice: make Bandcamp "the primary place you direct fans" (Keyes 2026-05). Matches BC-07 and BC-02 to BC-04.
2. **Turn visitors into followers and buyers, because both feed the platform surfaces.** Followers get release emails and the new follow filter. Buyers feed the co-purchase recommender and their own followers' feeds.
3. **Pricing.** OFFICIAL [help: what pricing performs best (2026-06-10)](https://get.bandcamp.help/en/articles/15263322-what-pricing-performs-best): about $4 for EPs of 6 tracks or fewer, $9 for albums of 7+, "let fans pay more" on, no .99 prices. Default prices since 2025-04-25: $1.50 track, $9 album ([blog](https://blog.bandcamp.com/2025/04/25/default-album-price-change-what-artists-need-to-know/)). His EUR 1.50 tracks are fine. Check that EP prices are not just the sum of tracks, and that "pay more" is on everywhere.
4. **Bandcamp Friday (2026-11-06, 2026-12-04).** Bandcamp share waived from 00:00 to 23:59 Pacific (09:00 Fri to 08:59 Sat Berlin). Processor fees still apply ([help](https://get.bandcamp.help/hc/en-us/articles/23006342800407)). Practitioners warn small acts get buried in the flood of releases ([RA 2025-08-17](https://ra.co/news/83402)). So use it as a reason to message followers and outside fans, not as discovery.
5. **Release message + Listening Party per release.** Two free follower touchpoints. Pre-order also notifies the mailing list when it goes live (OFFICIAL). Bandcamp's own advice to emerging artists: release a full album before trying pre-orders.
6. **Full discography bundle.** Feature exists (account setting). Bandcamp has published no data on it. Makes sense with 5 releases; a bundle sale also beats per-track fees.
7. **Discount codes and download codes.** Codes can target one item or the whole site, can expire, and redemptions are counted ([blog 2010](https://blog.bandcamp.com/2010/01/25/discount-codes), STALE?). Whether Pro is required is unclear; the plan says the feature shows in his account.
8. **Messaging followers.** Community tab, delivered on Bandcamp and by email (OFFICIAL 2020). Location targeting is documented for the artist app (2017, STALE?). **No official send limit or frequency rule was found.** Keep it rare (release, Bandcamp Friday).
9. **Featured track + profile location + tags.** Cheap, needed, not a growth engine.
10. **Subscriptions (fan club).** Exists since 2015 (REPORTED). Not worth it at 51 followers.
11. **Private streaming (Pro, $10/month).** Named links for press, no hard play limit, alerts on traffic spikes ([blog 2024-06-24](https://blog.bandcamp.com/2024/)). Only worth it for a premiere or label pitch season.
12. **Merch.** Discover and Clubs lean on physical goods, and Keyes lists merch first among Discover filters. Not relevant without merch. EU parcel duty (EUR 3 from 2026-07-01) and handling fee (EUR 2 from 2026-11-01) apply to parcels entering the EU from outside. My reading (not checked against the posts): a Berlin seller shipping inside the EU is not hit.

---

## 4. Changes timeline 2023-2026

| Date | Change | Label |
|---|---|---|
| 2023-08-08 | Listening Parties launched | OFFICIAL |
| 2023-10 | Songtradr buys Bandcamp from Epic; ~50% of staff not kept; Bandcamp Daily editorial cut sharply (DJ Mag: 3 left) | OFFICIAL (sale), REPORTED (cuts) |
| 2023-12-12 | Discover relaunched: music + merch in one place, genre / category / artist location | OFFICIAL |
| 2024-04-25 | Discover: tag search and combined tags, dark mode | OFFICIAL |
| 2024-06-24 | Pro: named private streaming links | OFFICIAL |
| 2024-08-23 | Linkfire integration | OFFICIAL |
| 2025-03-04 | Feature.fm smart links integration | OFFICIAL |
| 2025-03-17 | Bluesky account link (Pro) | OFFICIAL |
| 2025-04-25 | New default prices: album $7 to $9, track $1 to $1.50 | OFFICIAL |
| 2025-05-05 | Bandcamp Notes newsletter (Substack) | OFFICIAL |
| 2025-05-22 | Playlists beta (app, owned music only) | OFFICIAL |
| 2025-08-11 | Payouts moving from PayPal to Stripe, phased | OFFICIAL |
| 2025-09-01 | Bandcamp Clubs ($13/month curated subscribe-to-own) | OFFICIAL |
| 2025-12-03 | 8 Bandcamp Fridays announced for 2026 | OFFICIAL |
| 2026-01-13 | "Keeping Bandcamp Human": music wholly or substantially AI-generated banned | OFFICIAL |
| 2026-02-09 | GM Dan Melnick confirms collaborative filtering, no audio analysis, no streaming tier planned | OFFICIAL (quoted) |
| 2026-02-25 | Publishing-rights fields on upload pages | OFFICIAL |
| 2026-04-27 | Shipping labels via EasyPost | OFFICIAL |
| 2026-05-26 | Keyes lists discovery routes: Discover, Daily, Radio, Notes, Now Selling ticker, fan-follow newsletter, Listening Parties | OFFICIAL (quoted) |
| 2026-06-10 | Acceptable Use Policy page dated (scraping, bots, data mining, AI training, spam) | OFFICIAL |
| 2026-07-16 | Discover filter "artists you follow"; Subsonic API beta | OFFICIAL |
| 2026-10-20 | EU EUR 2 handling fee from 2026-11-01 | OFFICIAL |

No ownership change since Songtradr (2023). No reports of a sale or restructuring in 2025-2026 were found. A Nov 2025 commentary ([First Floor](https://firstfloor.substack.com/p/bandcamp-was-supposed-to-be-dead)) says the platform "seems to be doing just fine". Business health numbers: $19m paid out on Bandcamp Fridays in 2025, $154m since 2020 ([MBW](https://www.musicbusinessworldwide.com/bandcamp-fridays-hit-154m-in-payouts-since-2020-with-19m-paid-in-2025-alone)).

---

## 5. Myths and contested claims (adversarial checks)

**Five key claims, each checked against a contradicting source:**

1. **"Bandcamp has no algorithm."** Partly wrong. No personalized feed, but Melnick (2026-02-09) confirms collaborative filtering on co-purchases. Discover "new" and "best-selling" are sales/date-ordered lists. Corrected version: no personal recommendations, yes behavioural (purchase-based) placement.
2. **"Tags place you in Discover; tags do the work algorithms do elsewhere."** Contested. Keyes describes Discover as what fans are buying; tags only decide which list you are eligible for. r/BandCamp practitioners call tags table stakes, not growth (June research). His own data: 5 visits from Discover dark-disco in ~2 years. Keep tags clean; expect little.
3. **"Fans pay more than the asking price 40% of the time."** Contradicted. The 40% comes from a Bandcamp blog post of 2012-01-03 and is still repeated in the 2026 help page. Newer official figures are lower: "nearly 20%" add extra at $7-10 album prices (blog 2025-04-25); "25-30% of transactions" (Melnick 2026-02-09). Use 20-30%.
4. **"Bandcamp Friday: artist keeps everything."** Contradicted. RA (2025-08-17) says all fees are waived; Bandcamp's help page says only the revenue share is waived and "transaction fees still apply". Official wins: about 93-95% to artist on that day, less on small tickets.
5. **"Bandcamp Friday boosts sales for every artist."** Contested. Platform totals are large ($3.5-3.8m per day), but RA quotes artists saying small acts get buried in the flood. No data split by artist size exists. Treat it as a messaging occasion for his own audience.

**Other myths:**
- **"Set Berlin and tag berlin to appear in location filtering."** The location filter is "artist location" (profile). The tag is separate.
- **"Bandcamp algorithm rewards sales velocity / 18-24% of new customers come from bought-together / 8-25% follower conversion in 72h."** Chartlex and similar: VENDOR/UNVERIFIED, no Bandcamp source.
- **"30% of monthly sales come from discovery features."** Seen in a 2022-era Hypebot/Jazzfuel guide without a primary source. STALE?, UNVERIFIED.
- **"Bandcamp Daily accepts ~5% of pitches."** PR-vendor estimate. No submission process is published at all.
- **"Album of the Day brings several times normal traffic."** onestowatch, unsourced. UNVERIFIED.
- **"Self-purchases or buying your own release to chart is banned."** The Acceptable Use Policy (page dated 2026-06-10) has **no clause** on self-purchases, fake sales, paid streams or follow-for-follow. Closest rules: content must be "accurate" and not "likely to deceive", plus a ban on spam ("unsolicited or unauthorized advertising or promotional material"). Absence of a rule is not permission; buying his own releases would also pollute the co-purchase recommender and his own stats.

**AUP wording confirmed** ([help: AUP](https://get.bandcamp.help/en/articles/15263124-bandcamp-s-acceptable-use-and-moderation-policy)): "Not to scrape any text, media, or other data or content from the site ... including through the use of scripts, robots, bots, spiders, scrapers, crawlers, or other automated means"; "Not to undertake any form of text and/or data mining of content"; "Not to train any machine learning or AI model using content on our site". The plan's reading is correct.

---

## 6. Open questions

- How "best-selling" is computed (window, paid only, per tag) and whether a default or random sort exists. Not published.
- Which fields search indexes (description, credits, location). Testable by hand once.
- Whether followers get an email for a backdated release, and when the release email is sent.
- Any limit on follower messages per period.
- Whether discount codes need Pro (his account shows the feature; check by hand).
- Whether Playlists web editing and playlist following have shipped.
- Whether there is an electronic/EBM Bandcamp Club or plans for one.
- Exact Stripe fees once his account moves from PayPal (help pages still show PayPal-style rates: 5% + $0.05 under $8.07).

---

## 7. Sources

Official (Bandcamp):
- Blog archives: [2023](https://blog.bandcamp.com/2023/), [2024](https://blog.bandcamp.com/2024/), [2025](https://blog.bandcamp.com/2025/), [2026](https://blog.bandcamp.com/2026/)
- [Discover relaunch 2023-12-12](https://blog.bandcamp.com/2023/12/12/discover-a-new-way-to-shop-on-bandcamp/)
- [Combine tags 2024-04-25](https://blog.bandcamp.com/2024/04/25/new-in-discover-search-and-filter-by-combining-tags/)
- [Default price change 2025-04-25](https://blog.bandcamp.com/2025/04/25/default-album-price-change-what-artists-need-to-know/)
- [Payments to Stripe 2025-08-11](https://blog.bandcamp.com/2025/08/11/a-better-way-to-get-paid-on-bandcamp/)
- [Playlists beta 2025-05-22](https://blog.bandcamp.com/2025/05/22/introducing-bandcamp-playlists-beta)
- [Discover follow filter + Subsonic 2026-07-16](https://blog.bandcamp.com/2026/07/16/discover-improvements-and-subsonic-implementation/)
- [Messaging features 2020-05-27](https://blog.bandcamp.com/2020/05/27/new-messaging-features-up) (STALE?)
- [Discount codes 2010-01-25](https://blog.bandcamp.com/2010/01/25/discount-codes) (STALE?)
- [Discoverinator 2012-06-07](https://blog.bandcamp.com/2012/06/07/behold-the-glory-of-the-discoverinator/) (STALE?, no ranking definition)
- Help: [AUP](https://get.bandcamp.help/en/articles/15263124-bandcamp-s-acceptable-use-and-moderation-policy), [pricing](https://get.bandcamp.help/en/articles/15263322-what-pricing-performs-best), [pre-order](https://get.bandcamp.help/en/articles/15263066-how-do-i-set-up-a-pre-order), [Bandcamp Friday](https://get.bandcamp.help/hc/en-us/articles/23006342800407), [campaign tracking via live stream article](https://get.bandcamp.help/en/articles/15263381-how-should-i-promote-my-live-stream), [processor fees](https://get.bandcamp.help/en/articles/15263218-how-much-are-payment-processor-fees-for-digital-sales), [tags](https://get.bandcamp.help/hc/en-us/articles/23020708170519-What-are-tags-and-how-do-I-use-them)
- [Introducing Bandcamp Notes 2025-05-05](https://daily.bandcamp.com/features/introducing-bandcamp-notes), [Notes archive](https://bandcamp.substack.com/archive)

Press quoting Bandcamp executives:
- [Music Week 2026-02-09, Dan Melnick](https://www.musicweek.com/digital/read/as-bandcamp-friday-returns-gm-dan-melnick-says-the-platform-is-an-even-playing-field-for-artists/093521)
- [Hypebot 2026-05-26, J. Edward Keyes](https://www.hypebot.com/bandcamp-exec-shares-how-artists-and-music-get-discovered/)

Reported:
- [MBW: Bandcamp Fridays $154m](https://www.musicbusinessworldwide.com/bandcamp-fridays-hit-154m-in-payouts-since-2020-with-19m-paid-in-2025-alone), [MBW: Bandcamp Clubs](https://www.musicbusinessworldwide.com/bandcamp-launches-human-curated-bandcamp-clubs-at-13-a-month/)
- [Hypebot: 2026 Bandcamp Friday dates](https://www.hypebot.com/here-are-your-bandcamp-friday-dates-for-all-of-2026/)
- [RA 2025-08-17: Bandcamp Friday + small-artist concerns](https://ra.co/news/83402)
- [DJ Mag 2023: Songtradr layoffs](https://djmag.com/news/50-bandcamp-staff-laid-amid-songtradr-acquisition), [Mixmag 2023](https://mixmag.net/read/bandcamp-layoffs-songtradr-acquisition-union-epic-games-news)
- [Hypebot / Brian Hazard 2023-10-26: listening party how-to](https://www.hypebot.com/how-to-set-up-a-bandcamp-listening-party-and-why-you-still-should/)
- [AlternativeTo 2026-07: follow filter](https://alternativeto.net/news/2026/7/music-platform-bandcamp-adds-artist-follow-filtering-and-subsonic-api-support-in-open-beta/)
- [Yewknee 2025: Playlists review](https://yewknee.com/blog/bandcamp-playlists-2025)
- [First Floor Nov 2025 commentary](https://firstfloor.substack.com/p/bandcamp-was-supposed-to-be-dead)

Vendor / unverified (not planning inputs): Chartlex, Total Audio Promo, onestowatch.com guides, Apify scraper docs, mastering.com blog list, Jazzfuel.
