# 💶 Income Track 3: build & sell (2026-11-17)

Side chat under 💶 Income. Goal: something we build in a few weeks of hard work that then earns passive
income (+500 EUR/month), plus a short list of direct pitches. Research = web search only, $0 API.
Nothing built, bought or signed up for.

Scale (same as the 11-16 v4 score in `handovers/income/income-500.md`):
learn in ~2 weeks 0-2 · build together 0-2 · earns without clients 0-2 · money proof 0-2 · crowding 0 to -2 (minus only, never a drop).
Tie-break = how many sales a month 500 EUR needs, and whether that many buyers are visible.

---

## 1. 🧰 Inventory: what we already own (read on disk 11-17)

| Asset | What it is (facts from the files) | Sellable as is? |
|---|---|---|
| `artwork_resizer.py` (1,151 lines) | 1 master image -> every music platform: Spotify/Apple/Bandcamp 4000², Beatport 3000², SoundCloud, Spotify/Apple/YouTube/Bandcamp/SC profile sizes, YT thumbs incl. 4K + Shorts, IG; focal crop, ICC kept, EXIF stripped, 4:4:4 JPEG q97, preview grid, quality report | Code yes, as a CLI only. Needs a web or app front for buyers |
| `video_resizer.py` (775 lines) | 1 video -> all platforms (Reels/Shorts/TikTok, square, 4:5, story, landscape, Spotify Canvas), trim, CRF, metadata tags | Same: CLI, needs ffmpeg on the buyer's machine |
| Release Manager (`release_manager/`, 35 py modules, ~9,000 lines, 48 templates) | Local Flask app: releases, tickets/board, fonts, effects, archive, playground, stats, outreach, SEO copy, Claude/OpenAI calls | No. Built around his brand and files; a multi-user SaaS is a new build |
| Gap Radar (`gap_radar/`) | Reddit RSS/HN/App Store/StackExchange/YouTube/GitHub -> Claude analysis -> crowding check; 83 tests | Technically yes. Our own result: 60 income ideas, 0 survived (handover 11-16) |
| Gero AI marketing stack (`~/Desktop/Gero/CPcode/gero-control-panel`) | Next.js panel: SEO pipeline (competitor scrape, GSC+GA4, keyword score, Claude/GPT articles, 16-point QA, Contentful drafts, Reddit/Medium/LinkedIn distribution), LinkedIn + X scripts, YouTube pages | ⚠️ No. USES.md: "Gero data and code never come into this repo (NDA)". Hypothesis: the code belongs to the employer. The know-how can be sold as a service, not the code |
| Claude skills/agents | Own: `music-platform-seo.skill`, `release-platforms.skill`, `premieres.skill`, `brand` skill, agents ig-expert / promotion-expert / sc-expert (438 lines). Installed 3rd-party (Corey Haines marketing, research, hyperframes, remotion) = not ours | The 3 music skills yes, after stripping his personal data |
| Sample library + racks (`music-tools/STATUS.md`) | 41+ drum racks, Digitakt set (810 samples), Serum presets, `drumrack_tool_v2.py` (folder -> racks, pitch detect, "Snares by Key", waveform tracing of names), 4 mastering chains in `User - MIX` | ⚠️ The SAMPLES and presets are 3rd-party (Splice, machine packs, Tonepusher, NODE...): no resale. The TOOL and his own mastering chains are his |

---

## 2. 🏆 Ranked list (best first)

| # | Idea | Learn | Build | No clients | Proof | Crowd | Total | Sales/month for 500 EUR |
|---|---|---|---|---|---|---|---|---|
| 1 | KSK application builder (English, self-serve) | 1 | 2 | 2 | 1 | 0 | **6** | ~12-17 at 29-39 EUR |
| 2 | Music skills pack for Claude (release SEO, store SEO, premieres) | 2 | 2 | 2 | 1 | -1 | **6** | ~25-50 at 10-20 EUR |
| 3 | Release asset exporter (resizers as a browser tool, free + paid tier) | 2 | 2 | 2 | 1 | -1 | **6** | ~30-50 at 10-15 EUR, or ad traffic |
| 4 | Chrome extension with a paid tier (music/marketing niche) | 2 | 2 | 2 | 1 | -1 | **6** | ~170 subs at 3 EUR |
| 5 | Framer templates (music / DJ / label / EPK) | 1 | 1 | 2 | 2 | -1 | **5** | ~10-12 at 49 USD |
| 6 | Drum rack builder tool (`drumrack_tool_v2`) | 2 | 1 | 2 | 0 | -1 | **4** | ~25 at 20 EUR |
| 7 | His mastering chains as Ableton racks | 2 | 2 | 2 | 1 | -2 | **5 (low price)** | ~35-50 at 10-15 EUR |

Ranks 1-4 tie on points; the tie-break puts KSK first (fewest sales needed, no tool found, real money already paid to humans).

### 🥇 1. KSK application builder (score 6)
- What: an English (and German) web tool that walks a Berlin freelancer through the KSK application, fills the form
  draft, builds the proof checklist and income forecast. Users do it themselves = no clients.
- Proof ✅
  - KSK forms are German only; info "only partially" in English ([All About Berlin](https://allaboutberlin.com/guides/ksk-kuenstlersozialkasse)).
  - People already pay: agencies such as Inbound (Neukölln) help English speakers "for a few hundred euros" (same source); Feather sends users to a partner for form help ([Feather FAQ](https://faq.feather-insurance.com/en/articles/28745-can-you-help-me-fill-out-the-ksk-application-forms)).
  - Volume: ~14,475 applications in 2023, ~23% rejected (ratgeber source, from `income-500-options-2026-11-05.md` Offer 5).
- Crowding 0: no dedicated online KSK tool found in this search; only human help, free seminars ([Creative City Berlin](https://www.creative-city-berlin.de/en/events/event/05-get-started-kuenstlersozialkasse-ksk-and-social-insurance-basics-session-2)) and guides ([Accountable](https://www.accountable.de/en/blog/ksk-insurance-for-freelancers)).
- Why learn = 1: German social law + the legal-advice law (RDG). The BGH Smartlaw ruling (I ZR 113/20, 2021) allows a rules-based
  document generator, "like a form handbook" ([LTO](https://www.lto.de/recht/juristen/b/bgh-urteil-izr11320-vertragsgenerator-smartlaw-keine-unzulaessige-rechtsdienstleistung-rak-hamburg-rdg-legal-tech)).
  ⚠️ Hypothesis: AI-written answers to a user's own KSK letters could count as advice in a concrete case. Keep v1 rules-based; ask a lawyer before any letter feature.
- Fees: Stripe/Lemon Squeezy ~3-5% + tax handling (hypothesis, not checked today).
- Risk: one-time buyers, so traffic must keep coming (his SEO craft: "KSK application English", "Künstlersozialkasse Antrag").
- Hypothesis: English-speaking share of applicants is unknown; the 12-17 sales/month target is not proven.

### 🥈 2. Music skills pack for Claude (score 6)
- What: his 3 music skills (`music-platform-seo`, `release-platforms`, `premieres`) cleaned of personal data, sold as one pack.
- Proof (weak, all self-reported):
  - Guide: top skills ~$500-3,000/month, median listed skill under $50/month ([agensi guide](https://www.agensi.io/learn/how-to-monetize-skill-md-skills-developer-guide-2026)).
  - BuySkills claims $14,358.96 from 642 sales across creators, 85% split ([BuySkills](https://buyskills-ai-landing.pages.dev/)), vendor page.
  - Gumroad: a 167-skill marketing bundle at $167, no sales count shown ([listing](https://inflectual.gumroad.com/l/master-marketing-claude-skills-bundle)).
  - Anthropic launched Claude Marketplace on 2026-09-23 (2,000+ connectors/plugins) ([gHacks](https://www.ghacks.net/2026/09/27/anthropic-launches-claude-marketplace-with-more-than-2000-connectors-and-plugins/)); no payout terms for small authors found.
- Crowding -1: free marketing packs are huge (Corey Haines pack, "2.9M total installs" on one directory). Music release SEO is thinner (hypothesis: no paid music-release skill pack found).
- Fees: Gumroad 10% + $0.50 direct, 30% via Discover ([Checkout Page](https://checkoutpage.com/blog/gumroad-fees)).
- Change vs 11-05: market now has a real marketplace + a few sales claims; still a long tail. Best as a side product, not 500 EUR alone.

### 🥉 3. Release asset exporter (score 6)
- What: `artwork_resizer` + `video_resizer` logic in the browser (no upload, runs on the user's computer): one master -> every music
  platform incl. Spotify Canvas. Free single exports (SEO traffic, ads), paid batch/video/Canvas pack. Merges with open idea "free tools site" (Offer 11).
- Proof:
  - Single-platform resizers are everywhere and free (Kapwing, ytgrowth, Rybbit, resizebox); Pixa claims one "cover art resizer" for music platforms ([Pixa](https://www.pixa.com/create/cover-art-resizer)). No tool found that does every music platform + Canvas video in one go.
  - Ad income on small tool sites: ~$90/month AdSense ([Indie Hackers](https://www.indiehackers.com/post/i-built-a-free-no-login-tools-site-and-it-quietly-made-90-with-adsense-this-month-842b010af3)); ~$300 on 3.2K views (~$14 RPM); Jimpl ~EUR 1,000/month from ads (secondhand) ([Goodreads blog](https://www.goodreads.com/author_blog_posts/24798700-this-5-page-website-earns-1000-per-month)).
- Crowding -1: free generic resizers. Edge = music-exact specs + Canvas + kept up to date.
- Risk: ads need 6-12 months of SEO; paid tier conversion unknown (hypothesis).

### 4. Chrome extension with a paid tier (score 6)
- Proof is split:
  - Bad median: one dev with 38 extensions = $31 MRR, $165 lifetime ([DEV](https://dev.to/ktg0215/monetizing-chrome-extensions-with-freemium-real-numbers-from-7-paid-extensions-5cj)).
  - Outliers: indie extensions at $2.1k -> $3k/month ([ExtensionPay](https://extensionpay.com/articles/browser-extensions-make-money)); Superpower ChatGPT at 5-figure MRR, solo ([Indie Hackers](https://www.indiehackers.com/post/building-a-free-chrome-extension-in-3-days-and-turning-it-into-a-5-figure-mrr-ecosystem-3rIbjigZxiFsrgqJjJYp)).
  - Freemium conversion "2-5%" = vendor estimate only.
- Music niche: PromoTrack (Spotify for Artists capture) and Soundverse already sit inside S4A/YouTube Studio ([Soundverse](https://www.soundverse.ai/features/chrome-extension)).
- Needs one concrete pain first; no specific extension idea passed a check yet. Hypothesis: a "metadata + artwork checker" on distributor upload pages.

### 5. Framer templates, music niche (score 5)
- Best money proof of the list: Framer keeps 0%, 50% referral on templates ([Framer creators](https://framer.com/creators)); one creator ~$2,500/month by May 2026, peak $2,832.69 (mostly referrals); another $1,038.54 for June 2026 ([Framer community](https://www.framer.com/community/creator/@amar-kzr/)). Self-reported.
- Crowding -1: 10+ music templates already (MusicPeak, Record Label, Aftertone, DJLR, Vesper Music, free Musician & Singer, Common Static) ([Framer](https://www.framer.com/marketplace/templates/record-label/)). No template labelled EPK found = small gap.
- Learn/Build = 1: Framer editor is hands-on design work for Amir; Claude can only do code components and copy. ~3-5 days per template, catalog of 5+ needed (Offer 8).

### 6. Drum rack builder tool (score 4)
- His tool does what paid tools do partly: Kit Maker / Kit Creator (folders -> racks), free Drum Racks Diesel ([KVR](https://www.kvraudio.com/news/jesse-white-releases-drum-racks-diesel---automatically-generate-drum-racks-for-ableton-live-17371)); big players XO ~$79-129, Atlas 2 $99, Sononym $99, ADSR free ([EDMProd](https://www.edmprod.com/sample-manager/)).
- "Snares by key" not found in a named app = his unique feature. No sales counts found anywhere (proof 0).
- Build = 1: today it runs on his Mac, his paths; packaging for other machines and Live versions + support.

### 7. His mastering chains as racks (score 5, but low price)
- Gumroad racks sell at $5-30: Dafresh Instant Master EUR 29.90 (16 ratings), Solenoid Finalizer $10, a Drive Rack with 124 sales ([Dafresh](https://dafresh.gumroad.com/l/instantmaster)); many free racks (Dafresh free one: 55 ratings).
- Crowding -2. Only works if it rides on his mastering name; small money. Fine as a lead magnet for item 2 or 3.

---

## 3. 🗒️ Notes (weak, not pitched)
- Release Manager as SaaS: learn 2 · build 0 (multi-user SaaS = months) · no clients 1 · proof 0 · crowd -2 = **1**. Rivals: ArmaTune, ReleaseJet, Orphiq, Releasify ([Orphiq](https://orphiq.com/resources/music-release-planning-software)).
  Notion version: musician templates show 8 sales at $35, 3 sales at $17 ([Artist Label OS](https://loopartisans.gumroad.com/l/artistlabelos), [Release Roadmap](https://adventura.gumroad.com/l/releaseroadmap)) = **4**, tiny money.
- Gap Radar as a product: 2 · 1 · 2 · 0 · -2 = **3**. GummySearch shut down; rivals already fill the hole (PainOnSocial from $19/month, Sai $39-99) ([Sai](https://simular.ai/alternatives/gummy-search-alternatives)). Our own result: 0 of 60 ideas survived. Reddit use is "private research only" in our rules.
- Gero SEO pipeline as an n8n/Make template: 2 · 1 · 1 · 0 · -2 = **2**. NDA/IP block (hypothesis on ownership); n8n sellers say "template + setup" sells, template alone barely ([n8n forum](https://community.n8n.io/t/do-people-actually-pay-for-n8n-templates-or-only-for-someone-to-set-them-up/326627)) = client work.
- Sample packs from the library: blocked, 3rd-party sounds. Own darkwave packs = 11-05 check (no income data), score 3 on 11-16.

---

## 4. 📨 Direct pitches: music-tech / AI-music startups (drafts only, Amir sends)
None in Tel Aviv. Reason = a public fact that shows a growth need. Contact names are from press; check before use.

| # | Company | Where | Fact | Why a pitch |
|---|---|---|---|---|
| 1 | Tamber | Los Angeles, USA | $5M (Adobe Ventures), launched 18 May 2026, assistive AI inside Ableton/Logic ([MBW](https://www.musicbusinessworldwide.com/after-raising-5m-adobe-backed-tamber-officially-launches-its-ai-music-making-platform/)) | Fresh launch to producers; needs search traffic from "Ableton sound search" type queries. His producer + SEO mix fits |
| 2 | Just 4 Noise | Berlin, Germany | $1M Feb 2026, Just 4 Kicks plugin, ~4,000 creators ([MBW](https://musicbusinessworldwide.com/ai-sample-generator-just-4-noise-raises-1m-from-badideas-fund-sound-hub-denmark-and-more)) | Small team, local, kicks = his world (Eitan kick racks). Small budget (hypothesis) |
| 3 | Mozart AI | London, UK | ~$6M seed Feb 2026 (Balderton), mobile app launched ([SiliconANGLE](https://siliconangle.com/2026/02/11/mozart-ai-raises-6m-bring-generative-ai-music-creation-masses/)) | Mass-market app = ASO + SEO + content need |
| 4 | ArtMaster (Artie) | Prague, Czechia | $2.4M seed Oct 2026, 500k users, iOS only ([MBW](https://www.musicbusinessworldwide.com/ai-piano-learning-startup-artmaster-previously-backed-by-robert-kyncl-raises-2-4m-seed-round-with-moises-among-new-investors/)) | Growth so far from social views; web search for "learn piano" is a big open lane (hypothesis) |
| 5 | GRAI | Warsaw, Poland | $9M seed Apr 2026 (Khosla) ([Vestbee](https://vestbee.com/blog/articles/grai-raises-9-m)) | New consumer product, needs organic growth (hypothesis); English product |
| 6 | Tonada | Stockholm, Sweden | ~EUR 2.6M pre-seed Jun 2026, B2B AI music for shops/hotels, DACH customers ([raising.fi](https://raising.fi/news/tonada-pre-seed-june-2026)) | B2B SEO in DACH + English; he is German-market based. FOH/venue know-how fits hospitality sound |
| 7 | Chaos | London, UK | GBP 1M pre-seed Oct 2026, Amuse joined (single source, [aimusicpreneur](https://www.aimusicpreneur.com/ai-tools-news/artmaster-2-4m-seed-round-artie-ai-piano-teacher-2026/)) | Very early, no marketing team likely (hypothesis). Verify what it does first |
| 8 | Sound Credit | Memphis, USA (remote) | Hiring a Director of Marketing + Senior Marketing Manager ([Sound Credit](https://soundcredit.com/blog/careers-at-sound-credit-senior-marketing-manager)) | Proven marketing need; pitch fractional SEO until they hire. US time zone |
| 9 | Songscription | San Francisco, USA | Hiring a Growth Engineer for SEO infrastructure ([careers](https://www.songscription.ai/careers/growth-engineer)) | Proven SEO need; fractional/contract pitch |

⚠️ This is client work (service lane), not passive. Hypothesis to check: his Gero CMO contract may limit side work or competing roles.

### Draft (DRAFT ONLY, Amir approves in the main chat before any use)
Subject: SEO for [Company] after the launch

Hi [first name, only if confirmed; else "Hi [Company] team"],

I'm Amir, a Berlin producer and mastering engineer, and I run SEO and growth as CMO at a crypto wallet company. [one result line from his CV, his number]

I saw [the fact from the table]. I think [Company] can win search traffic from [one concrete query group]. I'd be happy to send a short free audit of three quick wins.

Would that be useful?

All the best,
Amir

(Rules applied: no em-dashes, no feedback ask, link last if any, Berlin, one personal draft per contact before sending.)

---

## 5. ▶️ Suggested next step (Amir's pick)
- Option A: KSK builder, week 1 = learn (KSK rules, RDG line, search volume for the English queries) $0, then decide build.
- Option B: skills pack + release exporter together (both reuse our own code; fastest to a first sale, smaller ceiling).
- Option C: pitches only (service lane, not passive).

## Sources not linked above
- [Agent37 on skills marketplaces](https://www.agent37.com/blog/monetize-claude-code-skills), [Claude Marketplace article](https://claude.com/ja/resources/articles/claude-marketplace)
- [Gumroad fees (Sellfy)](https://sellfy.com/blog/gumroad-pricing/), [n8n creator docs](https://docs.n8n.io/contribute/create-templates)
- [Framer creator guide](https://framerwebsites.com/blog/framer-creator-program-guide), [ArmaTune](https://www.softwareadvice.co.uk/software/555068/ArmaTune)
- [Kit Maker (Ableton forum)](https://forum.ableton.com/viewtopic.php?p=1773003), [Chaos/ArtMaster round-up](https://www.aimusicpreneur.com/ai-tools-news/artmaster-2-4m-seed-round-artie-ai-piano-teacher-2026/)
