# +500 EUR/month: build something new together (v3, 2026-11-05)

Brief from Amir: online, automated, no clients, no going out, built with Claude, something new that opens a door. Not selling what he already does.

v1 (freelance services) and v2 (workshop, Canvas studio, flat-hunt service) were rejected: both needed clients.

## The idea: a browser extension for people hunting flats in Germany

What a browser extension is: a small add-on people install in Chrome. It runs on pages they open themselves. Here it would wake up on ImmoScout, Kleinanzeigen, Immowelt, WG-Gesucht and Gewobag listing pages and add a panel next to the listing:

1. **Rent check:** is this rent legally too high? Germany has a rent cap law (Mietpreisbremse: in Berlin new rents may be max ~10% above the official local rent table, the Mietspiegel). The extension reads size, year built and address from the listing, compares with the public Mietspiegel, and says "this looks ~X EUR/month above the legal limit".
2. **English translation** of the listing.
3. **Nearest U/S-Bahn** and minutes to a place you choose.
4. **Red flags:** listing age, price changes, scam patterns (Western Union, "I am abroad", too-cheap Altbau).
5. **One-click application text** in good German, from the user's own profile.

Why this is new and fits you:
- You already solved the hard parts for yourself in the apartment bot: translation, transit, nice-score, German reply templates, WBS knowledge.
- Your real skill (SEO, proven at Gero) is exactly what this needs to get found: Chrome Web Store search + a landing site.
- No clients: users find it, install it, pay or click. No talking to anyone.
- Lower legal risk than the bot: no scraping server, it runs only on pages the user opens, like existing extensions (Rote Kapsel works on ImmoScout + Kleinanzeigen).

Gap check (2026-11-05): no extension found that combines a rent-cap check with listing pages. ImmoScout has its own rent check as a separate web tool (aimed at landlords). Existing extensions do alerts or price history only.

## How it makes money (no clients)

| Source | How | Notes |
|---|---|---|
| Paid tier | Free: translation + transit. Pro ~4-5 EUR/month: rent check, scam flags, German application texts, alerts | People search 2-6 months and already pay for bots (WohnungsBot, Homeboy, immonotify) |
| Referral (affiliate) | When rent looks too high, link to rent-reduction services (Conny/wenigermiete pays ~30 EUR min per Mietpreisbremse case, but its Awin program shows "closed", must be checked) | One referral = 6 months of a Pro user |
| Expat services | Insurance, banks, deposit insurance, moving, all have referral programs | Same model as All About Berlin (one person, full-time job since 2020, mostly affiliate) |

Math to 500 EUR: ~100 Pro users, or ~50 Pro + ~8 rent-case referrals a month. Germany has many cities with the same law, so it can grow past Berlin.

## What we would build (with me)

| Step | What | Rough time |
|---|---|---|
| 1 | Test demand: one landing page (EN) + post in r/berlin, r/germany, expat groups, count email sign-ups | 2-3 days |
| 2 | Extension v1: translation + transit + rent check for Berlin | 1-2 weeks |
| 3 | Chrome Web Store listing done with your SEO skills, landing site with Berlin rent guides | 3-4 days |
| 4 | Pro tier with payments (Stripe or Lemon Squeezy) | 2-3 days |
| 5 | More cities (Hamburg, Munich, Frankfurt, Cologne) | per city ~2 days |

Time to first money: realistic 1-3 months. Not instant.

## Honest risks
- Rent check is guidance, not legal advice: must say so clearly.
- Portals can change page layouts: the extension needs small fixes over time.
- Conny/expat referral terms are not confirmed yet.
- Mietpreisbremse rules and exceptions (new builds, renovated flats, furnished) must be built correctly. Status of the law in 2026 to be verified before building.
- Your free hours per week are unknown.

## Offer 2: "Fair price?" add-on for used music gear on Kleinanzeigen

- What: a Chrome add-on for musicians buying used gear. On a Kleinanzeigen (or eBay.de) listing for a synth, drum machine, interface or pedal it shows the real used market price (from Reverb's sold-price guide + eBay sold listings): "this Digitakt is ~80 EUR under market" or "~150 EUR over". Plus a saved-search alert: "tell me when a Digitakt appears under 450 EUR".
- Gap check: GearBook compares Reverb + eBay prices on its own site; no tool found that covers Kleinanzeigen, and no add-on on the listing page itself.
- Fits you: gear knowledge, the same keyword + price alert idea as your secondhand.py, Germany is a big used-gear market.
- Money: Pro alerts ~3 EUR/month, Reverb/Thomann referral links (Thomann pays 3.5-4.5%, needs 500 visits/day for websites). Honest: weaker than offer 1. Musicians pay little; referrals on used gear are small. 500 EUR needs ~170 Pro users.
- Risk: price data source must be allowed (Reverb API terms to check); Kleinanzeigen has no "sold" prices.
- Rating: B. Offer 1 (flats) stays stronger: more urgent need, more money at stake per user.

## Offer 3: supply AI companies with training material (video, music, your ear)

What this is: AI video and music models need real material to learn from. Companies now pay creators for raw footage, music and expert judgement. This is a market most musicians don't know exists.

| Lane | Who pays | Rate (2025-26 reports) | Fit |
|---|---|---|---|
| Raw video footage | Troveo (paid ~$5M for ~1M hours), Wirestock (700k contributors) | $0.75-3/min quoted, ~$0.55/min realised on big back catalogues; varied footage pays more than talking heads | Your own clips: 1,125 video files, ~432 min (~7 h) on disk (upper bound, includes reels/renders) = roughly $240-1,300 one-off |
| Your music | LANDR Fair Trade AI | $10/track advance (recoupable) + 25% revenue share | Small for 11 tracks |
| Your ear (rating AI music) | Outlier and similar | $20-40/hour, from home, no clients | ~15 h/month = ~500 EUR. Fast, online, but it is hours, not a product |

The build-with-Claude part: a footage pipeline. Claude sorts your clips, removes anything with other people's faces, logos or copyrighted music, cuts them into clean clips, writes the labels/descriptions buyers want, and uploads in batches. Then a monthly routine: film varied b-roll on walks you already do (Tempelhof, cemetery, streetlights, studio), drop it in a folder, the pipeline does the rest.

Honest limits:
- Footage income is mostly one-off unless you keep filming. ~5-8 h of new varied footage a month for ~500 EUR at quoted rates, less at realised rates.
- Troveo wants exclusive AI-training rights to what you send.
- Only footage you own: NOT Gero videos (A.D. Labs), NOT the photographer's photos, NOT clips with other people's music or faces without consent.
- Rates are from news reports and vendor guides, not confirmed contracts.

Rating: B+ as a door (new field, uses what you have, no clients). The fastest part is the "ear" lane.

### Deep check (same day) - verdict: C for a monthly 500 EUR
Music lane removed: Amir does not sell his tracks or make music for others.

Footage:
- Your on-disk footage is mostly NOT sellable: of ~432 min, ~341 min sit in Instagram exports (already-posted reels and DM videos from other people). Buyers want unpublished footage. Phone originals are probably only in iCloud, not counted.
- Troveo (troveo.ai/content-owners) is active ($20M paid, 7,000+ licensors claimed), but no public rate, paid only when a lab buys, ~95% of licensors signed exclusive. Country terms not confirmed.
- Only market benchmark: Bloomberg Jan 2025, $1-4/min, ordinary unused footage $1-2/min.
- Adobe Stock 2024 paid video buy ($2.62/min avg) was a one-time call; no 2026 bonus found. Shutterstock shares ~20% of data-licensing revenue, irregular.
- Germany: clear faces need consent (KUG, GDPR); DJ-set audio must be stripped.
- Result: one-off maybe 200-800 EUR if it sells. 500 EUR/month would need 5-10 h of new clean footage every month with steady demand; no evidence for that.

Ear lane (rating AI music):
- Mercor "Music Production Expert - German" is live: ~20 h/week, $11.37 per task, needs 2+ years producer/mix engineer, likely needs fluent German. English audio role closed (talent pool open).
- Alignerr "Audio Engineer, AI audio evaluation" asks for Berlin/Germany, $40-100/h listed, status unclear.
- Outlier allows Germany but empty queues for weeks are common. Hebrew roles are Israel-only.
- Projects end without warning and pay gets cut mid-project (Mercor $21 to $16/h, Nov 2025).
- Math: ~20-28 h/month at $30/h for 500 EUR net. Bursts, then gaps. 2-8 weeks to first pay.
- Tax: probably gewerblich, not Freiberuf: ask a Steuerberater.

## Offer 4: Gap Radar (an automation that finds the product for us)

Why: in this research, 9 of my ideas died on "already crowded" (plugin trackers, Ableton backup, letter apps, DJ library, Canvas tools...). Guessing ideas is the weak link. The flat add-on survived because it came from YOUR real pain. A machine can hunt real pains at scale.

What it does (runs daily, built with Claude, no clients):
1. Reads where people complain or ask "is there a tool that...": Reddit (r/berlin, r/germany, r/expats, r/ableton, r/WeAreTheMusicMakers, r/DJs, r/synthesizers...), 1-2 star App Store reviews of popular paid apps (Apple has a public reviews feed), Hacker News (free API).
2. Groups the same pain across many posts, counts how often and how angry.
3. For each top pain: checks who already solves it (like I did by hand today), and signals that people pay (paid apps with bad reviews = money + unhappy users).
4. Weekly page: top 5 gaps, with evidence links, competition, and a "can we build it in 2-3 weeks?" score.

You own it, it costs ~nothing (Claude API credit you already have), and every idea it gives comes with proof instead of my guess.

Honest limits:
- It earns 0 EUR itself. It finds the thing that earns. Expect 2-4 weeks of reports before a clear winner.
- Reddit's data terms are strict: GummySearch (a paid Reddit research tool) had to shut down in Nov 2025 after failing to get a commercial license. So the radar stays private, for us only, light reading, never sold. Reddit's 2026 personal-use limits are not verified yet.
- Build: ~3-5 days with me. Fits your "calculated API calls" rule: small daily budget, announced.

## Offer 5: KSK application builder (self-serve web tool)

What KSK is: the Kuenstlersozialkasse, Germany's social fund for freelance artists, musicians, designers and writers. If accepted, it pays about HALF of your public health and pension insurance, like an employer would. Worth thousands of EUR a year to a freelancer, so people care a lot.

The pain:
- ~14,475 applications in 2023, ~23% rejected, most often for missing or unclear information (ratgeber source, not official KSK stats).
- Long German forms, then follow-up questionnaires, proof of artistic work, income forecasts. Processing from weeks up to 18 months reported.
- Human help in English costs 104 EUR/hour (Red Tape Translation), 160-790 EUR packages (Kulturspace). Free guides exist (All About Berlin, Feather) but nobody fills it with you.

The product: a website, no humans involved.
- Guided questions in English (or German) about your work.
- Out comes: the filled application draft in correct German, a proof-of-work checklist matched to your field, an income forecast, and answer drafts for KSK's follow-up letters.
- Later add-ons: appeal letter after a rejection (Widerspruch), the yearly income estimate every member must send.
- Price ~29-49 EUR one-off. 500 EUR/month = ~12-17 sales/month.

Why it fits you: you live in exactly this scene (Berlin creative freelancers), your SEO skill gets the traffic ("KSK application English" type searches), Claude does the form logic and German writing, and the buyers are people who need it, not clients you manage.

Side note: you are a freelance musician in Berlin. Whether YOU could qualify for KSK is worth one check (your main income comes from Gero marketing work, which may not count as artistic). Not advice, just a question for your Steuerberater.

Honest limits:
- Must stay a document tool, not personal legal advice (German law on legal services, RDG). A 2021 BGH ruling (Smartlaw) allowed contract generators; needs a proper check before launch.
- Market is smaller than housing: ~14.5k applicants/year in all Germany, English speakers a fraction.
- Content-type searches are losing clicks to AI answers; a tool that DOES the work survives better than a guide.
- Build: ~2-3 weeks with me. First money: 1-3 months (SEO ramp).

Rating: B+ to A-. Clear pain, money at stake, existing proof people pay (100-790 EUR for humans), no self-serve tool found.

## Offer 6: Hebrew self-serve tool for the German passport by descent

What it is: Israelis whose parents or grandparents were persecuted by the Nazis can get German citizenship back (Art. 116(2) GG / §15 StAG). Demand is exploding.

The numbers:
- Israelis filed 5,924 applications in 2025, up from 3,640 in 2024 (Der Spiegel via Algemeiner, 4 Nov 2026). ~500 a month, growing.
- Israeli lawyers charge ~3,000-9,000 ILS, some 10,000-25,000 ILS per family. Doing it yourself costs ~1,500-2,000 ILS (translations, notary) if documents are in order.
- Many law firms compete for these clients in Hebrew; I found no self-serve Hebrew tool (search only, not proven absent).

The product: a Hebrew website where the user does it themselves, guided step by step:
1. Eligibility check (which route fits: Art. 116 or §15, which ancestor).
2. Personal document checklist for their family case.
3. Fills the German forms from Hebrew answers, explains every field in Hebrew.
4. Ready letters in German to archives (Arolsen, city archives) to find the ancestor's records.
5. Tracker for what's sent and what's missing.
- Price ~199-399 ILS (~50-100 EUR), vs thousands for a lawyer.
- 500 EUR/month = ~5-10 sales out of ~500 Israeli applicants a month (1-2%).

Why YOU: native Hebrew, you live in Germany and know the bureaucracy, SEO skill, Claude handles German forms and letters. No clients: users do it themselves. Nobody else on this list of ideas has this edge.

Honest limits:
- Hebrew SEO for this topic is fought over by law firms (they pay for ads).
- Must stay a self-help document tool, not legal representation (Israeli and German rules on legal services: check before launch).
- Sensitive topic (family persecution history): tone must be careful and respectful.
- Complex cases (missing documents, name changes) still need lawyers: the tool should say so.
- Build: ~3-4 weeks with me. First money: 1-3 months.

Rating: A-. Largest money-at-stake gap so far, clear price anchor (lawyers), and a language edge competitors in Germany don't have.

Checked and dropped in this round: German citizenship by naturalisation (civitas already sells a 99 EUR self-serve package in 6 languages), pension refund for people leaving Germany (services + calculators exist), utility-bill checks (5+ tools, one built on Claude), grant radar for artists (free aggregators exist). Side fact: Musicboard Berlin deadline 1 Dec 2026 (Karriereförderung, project money from 5,000 EUR, not a salary).

## Offer 7: your own media machine (the Gero engine, built for yourself)

Direction reset (Amir, 11-05): bigger, internet-wide, leverage/loopholes, passive or few decisions, something he controls, combining our tools. Offer 6 (passport) rejected hard.

The insight: at Gero you already built a money machine for someone else: keyword scoring, AI articles with a quality check, auto-posting to Reddit/Medium/LinkedIn, a video desk. Build the same machine once more, for a niche YOU own.

How the machine works (you approve, Claude runs):
1. Engine: finds topics with search demand + money (affiliate/sponsors) daily.
2. One idea becomes 5 outputs automatically: SEO article + newsletter issue + HyperFrames video (long) + 3 shorts/reels (resizers already exist) + social posts.
3. You: 20-30 min a few times a week to approve/adjust (your taste is what keeps it from being "AI slop").

The leverage ("loopholes", all legit):
- beehiiv Boosts: other newsletters pay you ~$1-3 per subscriber you send them, works from a small list (one creator: $328 from 1,300 subs). Scale plan reported at $99/month (to verify).
- AI-tool affiliate programs pay 20-30% recurring for 12 months (ElevenLabs ~22%, HeyGen ~20%, Synthesia 20-25%, Descript 15-30%; figures vary by source). One referral keeps paying a year.
- One piece of work published 5 ways = 5x reach for the same effort.
- YouTube is fine with AI-assisted video if there is real human direction; mass-produced repetitive videos lose monetization (policy renamed "inauthentic content", July 2025). Your edit/voice is the protection.

Niche options (to be chosen by a 2-day scan, not by guessing):
| Niche | Money | Competition | Your edge |
|---|---|---|---|
| "Build with AI, no coding": Claude Code for creators/non-coders | sponsors + dev-tool affiliates, high-value tech audience | growing fast, lots of content | you ARE the case study: release manager, video system, bots, all built this way |
| AI creative tools tested by a real creator (video, voice, image, music tools) | richest affiliate set (20-30% recurring) | very crowded | real renders/tests with your taste; video machine already exists |
| (scan may find a better one) | | | |

Realistic money: 0 in month 1-2, first Boosts/affiliate money month 2-4, 500 EUR/month more likely month 6-12. It's an asset that grows, not quick cash.

Costs: beehiiv plan (~$99/month if Boosts needs Scale, to verify), domain, Claude API (credit already).

Honest limits: content niches are crowded and AI answers take search clicks; the machine only wins with a sharp angle + consistency. Gero NDA: rebuild from scratch, no Gero code or data.

Rating: A for "fits what you described", B for speed.

## Offer 8: website template store on Framer's marketplace

What Framer is: a popular website builder (designers build sites visually, with code components). It has a marketplace where people buy ready-made website templates.

Why it's leverage:
- The marketplace brings the buyers: you don't market to clients, people search the store.
- Official (Framer help center, checked 11-05): you keep 100% of paid template sales. Free templates also earn: a commission when someone upgrades to a paid Framer plan through your template's remix link (percentage not on the page today; one blog said 50%, unverified).
- Make once, sell forever. Each new template adds to the pile. Few decisions after launch.

Combining your tools:
- Taste/brand design: your Look system, colour moods, type choices.
- Code: Claude writes the custom code components (animations, audio players, scroll effects).
- Video: HyperFrames makes the preview reels for each listing (listings with motion sell better).
- SEO: listing titles/descriptions/tags written for marketplace search, plus a small showcase site.

Niche angle: the store is full of SaaS/agency templates. Dark, editorial, music/creative-scene sites (artist, DJ, label, studio, photographer, event series, EPK) are your home turf: you've built an EPK, a brand system, studio pages.

Money (mostly blog estimates, treat as rough):
- Templates sell at ~$29-149.
- 1-2 templates: ~$50-500/month; 5-15 templates: ~$1,000-5,000/month; top sellers >$10k/month (outliers).
- One real first-person report: $233 in the first 2 months on paper, $51 cleared after the 30-day payout wait.
- 500 EUR/month = ~10-12 sales of a $49 template, or a catalog of ~5+ templates.

Honest limits:
- Building in Framer is hands-on design in its editor: Claude can't drive the Framer editor for you (code components and copy yes). ~3-5 days per template.
- Catalog-driven: the first template alone rarely makes 500 EUR.
- Commission percentage and payout terms need checking in the Creator dashboard.

Rating: A- (passive after launch, built-in buyers, uses design + code + video + SEO together).

## Offer 9: app factory (small paid phone apps, found through App Store search)

What it is: build many small, simple, useful iPhone/Android apps fast with Claude Code, each aimed at a search phrase people type in the App Store, each with a small subscription or one-time unlock. Not one big startup: a portfolio, where a few winners pay for everything.

Why it's leverage:
- Built-in distribution: the App Store and Google Play are search engines. Ranking there is called ASO (App Store Optimization), the same craft as your SEO: title keywords, conversion, reviews. A new skill, but a cousin of the one you already master.
- Claude Code now builds a small app in days, not months. That is the 2025-26 change that makes portfolios possible for one person.
- Once live, an app sells while you sleep. Few decisions: pick the next keyword, approve the build, ship.
- Uses your tools: Claude (code), HyperFrames (App Store preview videos), your design taste (screenshots/icons), SEO brain (keywords).

The honest numbers (RevenueCat State of Subscription Apps 2026 + summaries):
- ~17% of new subscription apps reach $1,000/month within 2 years; ~4.6% reach $10,000/month.
- One summary cites a median of ~$72/month one year after launch (unverified on RevenueCat's own page).
- New subscription apps launched per month rose from ~2,000 (2022) to 14,700+ (Jan 2026): much more competition, old apps still take 69% of the money.
- Apple added a second ad slot in search results in 2026, pushing organic results lower.
- So: one app is a lottery ticket; 8-12 apps, each aimed at a real low-competition keyword, gives decent odds that 1-2 reach a few hundred a month.

Costs: Apple developer 99 USD/year, Google Play 25 USD once, an ASO keyword tool (some free tiers).

Time: ~3-7 days per small app with me; first money weeks after launch if the keyword is right; 500 EUR/month realistically 6-12 months and several apps in.

Rating: B. Fits "code + internet-wide + passive", real upside, but statistically harsh. Works only with disciplined keyword picking before building (we'd measure demand and competition first, never guess).

## Offer 10: build to sell (the exit lever)

What it is: small internet businesses (content sites, newsletters, small apps, micro-SaaS) are bought and sold every day on marketplaces like Flippa, Empire Flippers and Acquire.com. The price is a multiple of profit. So an asset that earns 500 EUR/month is also worth a lump sum.

The numbers (broker/marketplace sources, rough):
- Content/affiliate sites: ~2.5-3.5x yearly profit (marketplaces say "30-40x monthly", same math).
- Micro-SaaS: ~2.5-4.5x yearly profit (Flippa 2026 average micro-SaaS 2.85x, top quarter 6.13x).
- So a project making 500 EUR/month profit = ~15,000-27,000 EUR if sold.

How it changes the plan:
- Build offers 7/8/9 as clean, sellable assets from day one: own domain, separate accounts, documented automation (Claude-run, so a buyer can run it), clean numbers.
- Choice later: keep the 500/month, or sell and start the next one with cash in hand.
- Few decisions: the machine runs; you decide only "keep or sell".

Honest limits:
- Buyers want 6-12+ months of stable profit history. Nothing to sell before that.
- Owner-dependent or traffic-unstable assets sell at the low end. Marketplaces take fees (to check per platform).
- It is an add-on to a money-making asset, not a money maker by itself.

Rating: A as a lever on top of 7/8/9; not standalone.

Checked and dropped this round: selling Claude Code skills (market early and small, most skills free, paid ones ~5-15 EUR), selling n8n automation templates (13,200 in n8n's library, paid ones ~$5-59, crowded).

## Offer 11: free tools website for creators (ads + affiliate, sellable on Flippa)

What it is: a website full of small free tools that people use and come back to, paid by ads around them. Not articles: tools. Niche: creators who publish video/audio/images on social platforms.

Example tools (we already own the data/know-how for many):
- Exact size/format/safe-zone spec per platform, always up to date (your artwork_resizer has 24 specs, video_resizer 10 presets, plus your Meta safe-zone rules).
- Resize/convert a video or image for every platform IN the browser (runs on the user's computer, so no server cost).
- Loudness targets per platform (Spotify, YouTube, TikTok, IG), BPM to delay/reverb times, video bitrate/file-size calculator, caption length checker per platform, thumbnail text-size checker.

Why it's leverage:
- A tool needs interaction, so an AI answer can't replace it the way it replaces an article (SEO-vendor claim, plausible, not proven). Simple conversions (time, units) are lost to Google's own boxes, so we pick tools Google doesn't do.
- Claude can build 30-50 tools; an automation checks the platforms monthly and updates specs (the "always correct" edge).
- Few decisions after launch. Clean asset to sell later (offer 10).
- Combines code + SEO + your video/audio knowledge.

Money (rough, vendor sources):
- Display ads: tech/creator-type pages ~$8-25 per 1,000 views (RPM); generic display $2-8. A Reddit thread says free-utility sites get lower rates.
- 500 EUR/month = ~40,000-70,000 page views/month at ~$8-12 RPM.
- Plus affiliate links to tools users need next (video editors, voice tools).
- Ramp: 6-12 months of SEO before real traffic.

Competition: big generic players (Canva, Kapwing, social-media size guides). Edge = niche precision, freshness, many small exact tools.

Rating: B+. Truly passive once it ranks, sellable, but slow to start.

## Offer 12: browser extension portfolio (build, or buy unmonetized ones on Flippa)

What it is: Chrome extensions are small add-ons (like offer 1, but any topic). Many have tens of thousands of users and earn nothing because the maker never added a paid tier. We build our own, or buy existing ones cheaply on Flippa, then add a fair paid tier.

The numbers (blogs + real Flippa listings, rough):
- Free-to-paid conversion ~2-5%. 10,000 users x 3% x ~3 EUR/month = ~900 EUR/month (blog math; real results vary a lot).
- Flippa examples: an extension with 10.5k users and $8.4k yearly profit listed at $10,000; an auto-refresh extension with ~61k weekly users listed at $24,999; several 40-100k-user extensions listed as "never monetized".
- Extensions sell at ~12-40x monthly revenue (vendor blogs), so they fit offer 10 (build/buy to sell).
- Chrome developer account: 5 USD once. Payments via ExtensionPay (~5%) or Stripe.

Why it's leverage:
- The Chrome Web Store is a search engine with built-in users (your SEO skill again).
- Claude builds and maintains extensions fast; small code, low running cost (mostly runs on the user's computer).
- Buying an unmonetized extension = buying an audience; we add the money layer.

Two routes:
- Build: 1-2 weeks per extension, 0 capital, months to grow users.
- Buy: users from day one, but needs a few thousand EUR+ and careful checks (real users vs fake, reviews, code quality, Chrome policy history).

Hard rule: monetize only with honest paid features. Buying extensions and adding hidden ads/tracking is a known malware pattern, Google bans it and it would be wrong. No data selling.

Rating: A- (code + Flippa + passive + sellable; buy route needs capital and diligence).

## Checked and dropped (round 4)
- App that explains German official letters with AI: already 7+ (Admina, expat.fyi, Ostrando, xPlainly, Amtli, Birocratie, open-source ones).
- Hebrew relocation guide site for Israelis in Germany: Hebrew guides already exist (reloways and relocation firms), audience ~10-15k Israelis in Berlin, content sites are losing traffic to AI answers.
- Ableton project backup/versioning: already 5 (DAWLab, TunesFork, WELX, Boombox, VersionAble).

## Checked and dropped this round
- Audio plugin price tracker: already 5+ sites (Music Software Deals, Audio Plugin Tracker, pluginplug, Plugin Dealz, plugindrop).
- DJ library tool: Lexicon dominates (115,000+ DJs claimed, free tier).
- Epidemic Sound (music library that pays artists per track): closed to new artists, doesn't work with artists in Germany.

## Sources
- Extension gap: https://chromewebstore.google.com/detail/rote-kapsel-das-immobilie/jnmbpmkphhcbhbfbcillhegbkipedapp?hl=de , https://www.immobilienscout24.de/lp/mietpreischeck.html , https://github.com/vrontos/immoscoutChromeExtension
- Conny affiliate: https://affi.io/m/conny , https://allaboutberlin.com/guides/conny-review
- All About Berlin model: https://nicolasbouliane.com/blog/health-insurance
- Paid flat bots: https://allaboutberlin.com/guides/find-a-flat-in-berlin
- Data/tool sites vs AI search: https://resollm.ai/blog/programmatic-seo-relevance/ , https://firstpagesage.com/seo-blog/ai-impact-on-website-traffic-report/
- Micro-SaaS benchmarks: https://dev.to/lufumeiying/i-built-a-500month-saas-in-7-days-using-claude-code-and-tdd-5hdo
- Plugin trackers: https://musicsoftwaredeals.com/ , https://audioplugintracker.com/ , https://pluginplug.io/
- Lexicon: https://www.digitaldjtips.com/lexicon-1-10-brings-serato-4-0-support-track-timeline-play-history/
- Epidemic Sound: https://www.epidemicsound.com/campaign/artist-faq/

## Checked and dropped (round 5, 2026-11-05): Apify Store data tools
- What: publish small scrapers ("Actors") on Apify's marketplace; Apify hosts, bills, keeps 20%.
- Proof people earn: Apify paid $563k to developers in one September; top creators >$10k/month MRR (help.apify.com).
- Crowding: ~24k Actors; most get few users; one dev: 64 users = $200/month after 3 months (dev.to).
- Our music niche is taken: 5 Resident Advisor scrapers, SoundCloud and Beatport scrapers already listed.
- Verdict: C for us. Only worth it if Gap Radar finds an empty niche.
- Darkwave/post-punk sample packs: niche already has 4+ packs on Loopmasters + Splice/TRAKTRAIN Darkwave II; no published per-download income (Splice gives totals only). Dropped.
- Canva Creators templates: Canva keeps payouts confidential; blog estimates $50-100/month typical, unverified. Dropped.

## Leverage we already own (2026-11-05, from repo data)
Options to explore. Not pitches yet: each still needs the Gap Radar crowding + income check.
1. Unused Claude API credit: $200/month, used $0.49 (Oct) and $2.88 (Nov). Any AI-powered product runs at near-zero cost. Open: read Anthropic's "Supplemental Credit Terms" (EU) before selling anything built on it.
2. Alert engine from apartmentcode (scrape -> filter -> Telegram bot): point it at other markets; Telegram channels can charge subscriptions in Stars.
3. Discogs API (token in .env): live used-record and gear prices, a data source few builders use.
4. Symphonic distribution: a label account could release other artists' music. Music rule applies: only with proof of income.
Also owned: HikerAPI ($83.59 = ~83.6k calls on 11-04, research only, never resold), YouTube/Spotify/SoundCloud API keys, Google Sheets API, HyperFrames video, Canva connector.
- 2026-11-05 Claude credit terms checked: Anthropic Credit Terms (eff. 2024-03-04) only ban transferring/selling the credits themselves (B.2 "No Transfer"); no rule against powering your own product. Support page: credits are "for building your own apps and agents". Not explicit for the monthly subscriber credits; treat as OK for our own product, never resell API access.
- 2026-11-05 Gap Radar run 2 (2344 items, 6 sources): 10/10 gaps crowded (~$6). Total radar spend today ~$13. Lesson: broad consumer complaints (invoices, fax, scanners, cleaners, shuffle, tuners) are always crowded; next runs need narrow niches.
- 2026-11-05 Gap Radar run 3, income-niches (262 items, Reddit throttled): 8 crowded, 2 unclear, 0 open (~$5.4). Unclear: (a) landlord compliance/deadline calendar (UK tools exist incl. a free one; US multi-state not checked), (b) multi-manager statement aggregator (Stessa etc. cover most). Month spend now ~$27.7.
- 2026-11-05 deep check, landlord deadline calendar ($1.13, 18 searches): radar said "open" (US), my own check says NOT clean: US has Insparisk Command (free tier), Lotkeeper (15-state deposit rules engine), Rentsolve, TenantCloud state notices; Germany has Landager reminders, objego, SafeBeep, Vermietler. Proven price is small (UK £5-12/month) -> ~60-100 subscribers for 500 EUR, plus legal-accuracy risk across states. Verdict: weak, dropped. Report: gap_radar/reports/income-niches/deepcheck-landlord-calendar.json

## Offer 13 (first radar pass, 2026-11-05): venue blog generator for wedding photographers
- Radar run 4 (income-niches alone, 492 items): 9 crowded, 1 open. My own check: competitors exist but partial: Venue Blog BFF ($97 one-time ChatGPT guide), PhotoBiz AI Blog Creator (only inside PhotoBiz sites), Narrative Publish ($6-15/mo, layout only), generic AI writers, Vulcaro. None does selects -> post + alt text + filenames + vendor credits + publish to WordPress/Showit.
- Pay proof: $97 GPT, $199-699 SEO courses, Narrative $6-15/mo, BlogStomp $49 (older).
- Math: at ~$19/month, ~29 subscribers = ~500 EUR. Conversion unknown.
- Risks: photographers can DIY with ChatGPT; website platforms may add it; US market; build fresh (no Gero code).
- Rating: B- (passes the check, thin moat). Report: gap_radar/reports/income-niches/2026-11-05T0619.md
- 2026-11-05 own check (side chat, web search only, $0 API): NOT open. Vowrio (vowrio.com, "brand new", (c) 2026) already sells exactly this at $29/month: up to 100-150 photos, AI venue post, unique alt text + SEO filenames, vendor credits, venue FAQ, JSON-LD, direct publish to WordPress/Showit via a plugin. It is still looking for its first 50 founding members, so there is no proof yet that photographers pay for it. PhotoBiz AI Blog Creator is open to all PhotoBiz accounts since 2026-04-09. Pictage (pictage.ai) is a free beta with its AI tools unverified. Narrative Publish: no AI writing found. Verdict: dropped (a direct copy at the same price, and the demand is unproven). The radar's crowding check missed Vowrio.

### Owned-leverage check (💰 Income 13, side chat 2026-11-05, web search only, $0 API)
- Telegram alert engine + Stars subscriptions. The payment side works: native Stars subscriptions, creator payout ~$0.013/Star (not an official figure), 1,000-Star minimum, 21-day hold, paid out in TON (USDT since May 2026). The only proof of paid ALERT demand is trading-signal channels: a median of 380 paid subs x $12.60 = $4.8k/month, but that comes from a survey of 47 surviving operators (telegram-bible.pages.dev, Apr 2026), and medians across everyone who tried are "3-5x lower". Our own market, Berlin flats: MietAlert already sells Telegram alerts at EUR 4.99/month and shows almost no traction. At EUR 5, 500 EUR needs ~100 paid users, about 1,100 free followers at ~9% conversion. Verdict: C. The engine is only a delivery channel; it still needs a niche where people already pay for alerts, and we found none outside trading. Trading signals are financial advice territory: no.
- Discogs price data. The API Terms of Use split CC0 data (monthly dumps) from "Restricted Data", which may NOT be used commercially or passed to third parties. I could not confirm whether marketplace prices count as Restricted Data (the support page returned 403). Wantlist alerts already exist for free: Discogs' own wantlist emails, open-source discogs_alert, and the Discogs Notifier Chrome extension (email/Telegram). Vinyl is also not his world. Verdict: dropped.
- Result: 0 vetted ideas from what we already own.

## First real test, night 2026-11-06 (radar + own checks)
- income-niches (tuned: QuickBooks, TaxPros, VideoEditing, teaching, sysadmin ...; 196 posts, $7.44): 0 open, 4 unclear, 6 crowded.
  Own checks (web search, $0 API): tax fee calculator DROPPED (free Intuit Fee Wizard + a paid Excel template);
  MSP firmware/EOL watcher DROPPED (endoflife.ai, Auvik CVE matching, OpenCVE; security liability);
  tax-return AI review DROPPED (5+ paid tools); broadcast deliverable versioning panel for Premiere = still unclear
  (no exact tool found, Plainly $69+/mo and Templater $225+ sell nearby AE versioning; demand evidence = 1 post).
- producer-tools (the duplicate run T0320 found 2 open):
  - Offer 14 candidate: "Set bridge" for live Ableton/hardware sets: keep sound and clock running while the next set loads.
    Own check: no gapless set-switch tool found; AbleSet 3 sells at $129/$179/$269 and still leaves a load gap
    (radar check); performers buy extra loopers as a workaround. Main risk = feasibility: a Max for Live device dies
    when Live unloads the set, so it needs a small helper app outside Live. Rating B- pending a feasibility test.
  - Elektron Overbridge templates DROPPED: paid ones exist at GBP 8.99 (Syntakt, Live 12), free RAFH templates; low price ceiling.
- income-trades (new profile) not run: radar at $63.77 of the $70 cap, run est. $9.10, waits for Amir.
- Overlap cost (two monthly runs at once, my mistake): $9.43 (producer-tools analysis + competitor check $8.65, 4 insight analyses $0.78).


## Premiere deliverable versioning panel: DROPPED (own check 2026-11-06, $0 API)
- Nearby tools already sell the core: Waymark Variations (lengths + ratios + languages in one click), AdPipe auto-resize (6 ratios),
  Invideo cutdowns, Cuttable (auto end frame), Plainly ($69+/mo), Creatopy ($39+/mo); market range quoted $59/mo to thousands/mo.
- Shops that need the exact matrix write their own scripts (Mixing Light promo workflow: marker-driven batch renders in Resolve;
  a 30/15/6 render-queue script blog; DVR-timeline-version-manager on GitHub). Premiere Batch Sequence Settings sells on Gumroad.
- Demand evidence = 1 forum post. Buyers = post houses and agencies (sales-led, not self-serve). Adobe updates break panels (upkeep).
  Far from Amir's world (fit 4 was the radar's guess).
- Result: the night-test list is now closed. Left: set bridge (B-, waits on the 5-minute test), income-trades run (waits for a cap raise).
