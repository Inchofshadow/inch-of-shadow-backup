# Social-data API providers: which one(s) to buy (research 2026-10-15)

Question (Amir, 2026-10-15): if we fund an API provider for about a year, should it be one that also
covers TikTok, Threads, Spotify, SoundCloud and YouTube later, instead of HikerAPI (Instagram only)?

Method: four parallel reads of the providers' OWN docs, pricing pages and OpenAPI specs (no competitor
blogs). Every claim below has a source in the URL list at the end. "Unverified" means the provider does
not publish it. Specs are saved in the session scratchpad (hiker, socialfetch, scrapecreators,
sociavault, ensembledata).

## 0. Conclusion

1. Top up HikerAPI with $100 once. That unlocks the Standard rate ($0.001 per request), which stays on
   the account for good. At our planned volume the balance lasts about three years; at the daily cap
   about one year. Earlier notes ("$5 = 4 months", "83k calls per $50") were wrong: they assumed the
   Ultra rate, which needs a $599 balance. The September top-up ran at the Start rate ($0.02) and was
   gone in five days.
2. No multi-platform provider can replace HikerAPI for the main job. The queue builder lives on
   follower LISTS of seed artists. Of the seven alternatives read, only Apify (via Store actors) has
   Instagram follower lists, and it costs 6-10x more per year with a monthly plan on top.
3. Buy nothing else now. When a second platform becomes an actual job, add a small one-time pack:
   Social Fetch ($14 for 1,000 credits, never expires) covers TikTok follower lists, Threads, Spotify
   artist (monthly listeners) and SoundCloud profile/tracks. ScrapeCreators ($47 for 25,000) is the
   alternative with Spotify playlists. Both packs are one-time, not per month or per year.
4. SoundCloud and YouTube need no purchase. YouTube runs on Google's free Data API already. SoundCloud's
   official API is self-serve again (needs an Artist Pro subscription), gives follower/following lists
   by URN and play counts, and would replace browser-scrolling for the reciprocity check. Its terms
   forbid scripted follows, so the follow lane itself stays as it is.
5. Spotify: there is no API for Spotify for Artists numbers, never was. Our curator-research app
   (client credentials, created before Feb 2026) may still return playlist data today but will be cut
   over to the reduced endpoint set on an unannounced date. One test call before relying on it.

Spend now: $100. Expected run cost after that: about $35 per year for Instagram.

## 1. Our usage model (from ig_engagement_config.PROVIDER and ig_queue_builder)

| Job | Calls | Frequency | Per year |
|---|---|---|---|
| Audit (2 calls per candidate: profile + medias) | 60/day steady, 100/day in backlog | daily | ~22k-30k |
| Queue build (8 seeds x (1 + 200 followers / 25 per page)) | 72 per run | ~2 runs/week | ~7.5k |
| Ad hoc (handle checks, outreach enrichment, stats) | | | ~1k-3k |
| Daily cap `daily_call_cap` | 300/day | | 110k max |

Typical: ~35k calls/year. Ceiling: ~110k calls/year. Ledger history: 90 + 20 + 4 est. calls on
09-14/17/18, then balance 0 from 09-19 to today (dispatcher wrote "audit 0 / builder 0" 27 days in a row).

## 2. Cost of the Instagram job per provider (our model)

| Provider | What we pay | Typical year (35k) | Ceiling year (110k) | IG follower lists? |
|---|---|---|---|---|
| HikerAPI, Start rate (balance < $100) | $0.02/req | $700 | $2,200 | yes |
| HikerAPI, Standard rate ($100 balance once, locked) | $0.001/req | $35 | $110 | yes |
| HikerAPI, Business ($299) / Ultra ($599) | $0.00069 / $0.0006 | $24 / $21 | $76 / $66 | yes, not worth the lock-up |
| Apify Starter + apify/instagram-followers-following-scraper | $19/mo plan + $1.75 per 1k follower RESULTS + $2.30 per 1k profiles | $228 plan covers ~$340 usage -> ~$340 | ~$700+ | yes (per result, not per page) |
| Apify Starter + community follower actor (scraping_solutions) | $19/mo + $0.70 per 1k results | ~$228-$250 | ~$400 | yes |
| Social Fetch | $14/1k, $59/25k, $379/230k one-time | n/a | n/a | NO (no followers/following route) |
| ScrapeCreators | $47/25k, $497/500k one-time | n/a | n/a | NO |
| SociaVault | $29/6k ... $399/200k one-time | n/a | n/a | NO |
| EnsembleData | $100/month minimum (1,500 units/day) | $1,200 | $1,200 | NO (count only; marketing says lists, spec has none) |
| Data365 | EUR 300/month minimum | EUR 3,600 | EUR 3,600 | unverified, no public docs |
| Bright Data | $1.50/1k records, 5k free records/month | ~$50 if follower lists existed | | unverified (samples show one record per profile) |

Notes on HikerAPI billing: follower pages are one request each (~25 users per page on v1 chunk, 50 on
the gql route which bills 2); 404 and private (403) are billed, 5xx/401/402/410 are not; balance never
expires; rate stays after the balance drops; 15 requests/second default; no daily cap.

## 3. Platform coverage matrix (routes we would actually use)

| Need | HikerAPI | Social Fetch | ScrapeCreators | SociaVault | EnsembleData | Apify |
|---|---|---|---|---|---|---|
| IG profile by username | yes | yes (1 cr) | yes (1 cr) | yes | yes (3 units) | yes ($2.30/1k) |
| IG posts/reels with dates | yes | yes | yes | yes | yes (1 unit/post) | yes |
| IG followers list | yes | no | no | no | no | yes |
| IG following list | yes | no | no | no | no | yes |
| IG hashtag posts | yes (native) | yes | Google-indexed only | Google-indexed only | no | yes |
| IG location posts | yes | places lookup only | places lookup only | places lookup only | places lookup only | yes |
| IG comments | yes (15/page) | yes | yes (~90% success) | yes | yes | yes |
| TikTok profile / videos | no | yes | yes | yes | yes | yes |
| TikTok followers list | no | yes (1 cr/page) | yes (1 cr/page) | yes | yes (2 units/100) | yes ($1/1k) |
| Threads profile / posts | advertised, NO routes in spec | yes | yes (last 20-30 posts) | yes | yes | profile only ($5/1k) |
| Spotify artist (monthly listeners) | no | yes (monthlyListeners, followers) | artist route, fields unverified | no | no | community actor ($3.20/1k) |
| Spotify playlist | no | no | yes (50 tracks/page) | no | no | no |
| SoundCloud profile (followers count) / tracks (plays) | no | yes / yes | yes / yes | no | no | community actors, fields unverified |
| SoundCloud followers list | no | no | no | no | no | one brand-new actor, 3 users, unproven |
| YouTube channel / videos | no | yes | yes | yes | yes | yes |

## 4. Pricing shapes (what "$14" means)

| Provider | Shape | Smallest buy | Expiry | Free |
|---|---|---|---|---|
| HikerAPI | prepaid balance, rate tiers unlocked at $20 / $100 / $299 / $599 | any amount ($100 for the sane rate) | never | 100 req |
| Social Fetch | one-time credit packs OR optional monthly subs ($29/$79/$225 per month) | $14 pack (1,000 credits) one-time | packs never; monthly sub credits reset each month | 100 (+250 with card) |
| ScrapeCreators | one-time packs | $47 (25,000) | never | 100 (+ bonus) |
| SociaVault | one-time packs | $29 (6,000) | never | 50 |
| EnsembleData | monthly sub with DAILY units, reset 00:00 UTC | $100/month | daily | 50 units/day |
| Data365 | monthly sub, sales-issued key | EUR 300/month | monthly | 14-day trial |
| Apify | monthly plan credits + per-result actor fees drawn from them | Free ($5 usage/mo) or Starter $19/mo | monthly, no rollover | $5/mo usage |
| Bright Data | pay as you go per record | none | monthly free pool | 5,000 records/month |

## 5. Official platform APIs (October 2026)

| Platform | Own stats via API | Others' public data | Follower lists of others | Cost | Blocker |
|---|---|---|---|---|---|
| Instagram (Meta) | yes (insights, some need 100+ followers) | Business Discovery counts + media (Facebook-Login setup only); hashtag 30 per 7 days | no (no followers edge) | free | App Review + Business Verification |
| Threads (Meta) | yes (views, likes, followers_count, demographics) | keyword search, profile lookup gated (standard access = Meta accounts only) | no | free | App Review per permission |
| TikTok | yes (Display API, own counts) | no | Research API only (academia, not creators) | free | eligibility |
| YouTube | yes (Analytics API) | yes | no | free, 10,000 units/day + 100 searches/day | quota extension needs compliance audit |
| SoundCloud | yes (/me, followers, playback_count) | yes (users, followers/followings lists by URN, tracks) | YES | API free, registration needs Artist Pro subscription (price not verified) | terms: follows/likes only as user-initiated clicks, no scripted loops |
| Spotify | NO (no Spotify for Artists API) | shrinking: Dev Mode = 5 users, owner needs Premium, search limit 10, /users/{id} and others' playlist items removed, artist followers/popularity removed | no | free (Premium for owner) | Extended Quota = organisations with 250k MAU; cut-over date for pre-2026 apps unannounced |

## 6. Reliability and trust signals

| Provider | Entity | Status page | Notes |
|---|---|---|---|
| HikerAPI | no legal entity named, "based in Kazakhstan", ToS dated 2022 | self-hosted, 99.59% 90-day | the one that works for us since 09-14; Python SDK 1.8.2 (2026-09-28), MCP server; suspension "without prior notice" |
| Social Fetch | Social Freak Ltd, UK (co. 14659411), ToS 2026-10-14 | reliability page 99.8%, no incident history | public SDK ~6 months old |
| ScrapeCreators | Austin TX, founder-run, Texas law | 36 incidents May-Oct 2026, six on Instagram | refunds discretionary |
| SociaVault | Ziddec Inc., Delaware | hourly checks, no history | spec mirrors ScrapeCreators 1:1 (reseller? unverified) |
| EnsembleData | EnsembleData Pte. Ltd., Singapore, since 2020 | 5 incidents since Dec 2024 | Warner/UMG logos; $100/mo floor |
| Apify | Apify Technologies, Prague | all operational, 0 incidents Oct 1-15 | Apify-maintained IG follower actor since 2026-06-30 |
| Data365 | unnamed, England & Wales law, since 2018 | none found | sales-gated |

All scrapers put platform-terms responsibility on the customer. None of them touches Amir's own
account (API key only, no Instagram login), which is the rule since 09-14.

## 7. Recommendation, step by step

| # | Action | Cost | When |
|---|---|---|---|
| 1 | HikerAPI: top up $100, pick the Standard rate on the pricing page (it does not switch by itself) | $100 once | now; the dispatcher resumes the next morning |
| 2 | Fix our own notes: dispatcher notify text "$5 = 4 months" and config comment "$0.18/day at $0.0006" | 0 | next engagement-code window |
| 3 | Spotify: one test call with the existing curator app (playlist detail) to see what the Feb 2026 rules left us | 0 | when curator work comes up |
| 4 | SoundCloud: if Artist Pro is in place, register an API app (free) and move the reciprocity read to the official followers/followings endpoints; follows stay manual/browser | 0 (+ Artist Pro) | when SC reciprocity is next rebuilt |
| 5 | TikTok / Threads / Spotify-of-others: Social Fetch $14 pack (one-time) when a job exists; ScrapeCreators $47 if Spotify playlists are the job | $14-$47 once | only on demand |
| 6 | Do not buy: EnsembleData, Data365, Bright Data, SociaVault, Apify (for Instagram) | | |

Open / unverified: SoundCloud Artist Pro price; Spotify cut-over date for existing apps; HikerAPI
Threads routes (advertised, absent from spec); Social Fetch page sizes; Bright Data follower lists.

## 8. Sources

HikerAPI: https://hikerapi.com/p/pricing , https://hikerapi.com/instagram-api , https://hikerapi.com/instagram-followers-api , https://api.hikerapi.com/openapi.json , https://hikerapi.com/help/refund-policy , https://hikerapi.com/help/terms-of-service , https://hikerapi.com/help/privacy-policy , https://hikerapi.com/status , https://hikerapi.com/threads-api , https://github.com/subzeroid/hikerapi-mcp , https://pypi.org/pypi/hikerapi/json
Social Fetch: https://www.socialfetch.dev/pricing , https://www.socialfetch.dev/docs/credits.mdx , https://www.socialfetch.dev/llms-endpoints.txt , https://www.socialfetch.dev/llms-instagram.txt , https://www.socialfetch.dev/llms-tiktok.txt , https://www.socialfetch.dev/llms-spotify.txt , https://www.socialfetch.dev/llms-soundcloud.txt , https://www.socialfetch.dev/llms-threads.txt , https://www.socialfetch.dev/openapi.json , https://www.socialfetch.dev/reliability , https://www.socialfetch.dev/terms
ScrapeCreators: https://scrapecreators.com , https://docs.scrapecreators.com/openapi.json , https://docs.scrapecreators.com/v1/instagram/profile , https://docs.scrapecreators.com/v2/instagram/user/posts , https://docs.scrapecreators.com/v1/tiktok/user/followers , https://docs.scrapecreators.com/v1/spotify/artist , https://scrapecreators.com/status , https://scrapecreators.com/terms
SociaVault: https://sociavault.com/pricing , https://docs.sociavault.com/api-reference/openapi.json , https://sociavault.com/refund-policy , https://status.sociavault.com
EnsembleData: https://ensembledata.com/pricing , https://ensembledata.com/apis/openapi.json , https://ensembledata.com/status , https://ensembledata.com/terms-and-conditions
Data365: https://data365.co/pricing , https://data365.co/instagram , https://data365.co/terms
Apify: https://apify.com/pricing , https://docs.apify.com/platform/actors/running/actors-in-store , https://apify.com/apify/instagram-followers-following-scraper.md , https://apify.com/scraping_solutions/instagram-scraper-followers-following-no-cookies.md , https://apify.com/clockworks/tiktok-followers-scraper.md , https://apify.com/augeas/spotify-monthly-listeners.md , https://apify.com/apify/threads-profile-api-scraper.md , https://apify.com/jupri/soundcloud.md , https://status.apify.com
Bright Data: https://brightdata.com/pricing/web-scraper , https://brightdata.com/products/web-scraper/instagram/followers , https://docs.brightdata.com/products/scrapers/error-codes.md
Spotify: https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide , https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security , https://developer.spotify.com/blog/2026-07-23-web-api-quota-updates , https://developer.spotify.com/documentation/web-api/concepts/quota-modes , https://developer.spotify.com/documentation/web-api/references/changes/february-2026
YouTube: https://developers.google.com/youtube/v3/getting-started , https://developers.google.com/youtube/v3/determine_quota_cost , https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits , https://developers.google.com/youtube/analytics
SoundCloud: https://developers.soundcloud.com/docs/api/register-app , https://developers.soundcloud.com/docs/api/guide , https://developers.soundcloud.com/docs/api/rate-limits , https://developers.soundcloud.com/docs/api/terms-of-use , https://github.com/soundcloud/api
TikTok: https://developers.tiktok.com/products/research-api/ , https://developers.tiktok.com/doc/research-api-faq , https://developers.tiktok.com/doc/display-api-overview , https://developers.tiktok.com/doc/content-posting-api-get-started
Threads: https://developers.facebook.com/documentation/threads/overview , https://developers.facebook.com/documentation/threads/insights , https://developers.facebook.com/documentation/threads/keyword-search , https://developers.facebook.com/documentation/threads/threads-profiles
Instagram: https://developers.facebook.com/docs/instagram-platform/overview , https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user , https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery , https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/hashtag-search
