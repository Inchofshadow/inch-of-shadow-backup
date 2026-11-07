# Gero control panel to Inch of Shadow: what to bring over (2026-11-06)

Read-only study. Nothing was edited, moved, run or installed in either repo. No secret values copied
(the Gero memory holds a panel login and an IndexNow key; neither appears here).

Read: the Gero memory index and ~45 of its files, the 5 Gero skills, `docs/` (seo, x-agent, youtube,
medium, music, gtm, superpowers, linkedin-agent), `docs/pm/*` and `src/lib/pm` from `origin/main`
(the local checkout sits on a branch without them), `scripts/`, `src/app`, `videos/`, the Video Desk
spec in the `video-desk` worktree, `README.md`, `SETUP-GUIDE.md`, `lighthouserc.json`, `tests/`,
`memory-bank/`. IoS side: `CLAUDE.md`, the 11-05 code map, the approved platform plan (D5), content
language section 5, `docs/brand/README.md` and `voice.md`, both skill folders, `../youtube/PLAYBOOK.md`.

## 0. Short answer

Most of Gero's power is built for a website with a blog (Contentful, Google Search Console, GA4)
and for X. Inch of Shadow has neither, and the approved plan does not need X. So the best transfers
are the **video and publishing discipline**, not the SEO machine: a pre-publish check on every
video, a clip pack per song, the YouTube API tricks, the review/approved folders. The SEO machine
only becomes useful if Amir decides to own an artist website, which is a separate decision (rank 5).

## 1. What Gero CP has

Maturity: live = in use now; built = works, not in daily use; draft = plan or spec; parked = stopped.

| Thing | What it does | Where it lives | Generic or Gero-only | Maturity |
|---|---|---|---|---|
| `gero-seo` skill | Strategy / draft / audit modes for blog SEO; drafts saved to Contentful as drafts, never published | `.claude/skills/gero-seo`, `docs/seo/gerowallet/` (strategy, keyword map, site snapshot, inventory, on-page checklist) | Pattern generic, content Gero | live |
| SEO automation | Keyword scoring, AI article generation, 16-point quality check (pass 80/100), save-draft with em-dash hard fail | `scripts/seo-automation/*`, `src/lib/seo/*`, `src/lib/ai/prompt-library.ts` | Gero (Contentful) | built, scheduler off |
| Indexing ping | Pings Google Indexing API + IndexNow for posts published in the last N days | `scripts/seo-automation/submit-indexing.ts` | Generic (needs an owned site) | built |
| Index check | Asks Search Console's URL Inspection API "is this page indexed", read-only service account | `scripts/medium/check-indexed.ts` | Generic (needs an owned site) | live |
| In-place refresh | Edit published posts via markdown, internal-link pass (dry run, manifest), separate publish step | `update-drafts.ts`, `internal-link-pass.ts`, `publish-changed.ts` | Gero (Contentful) | live (54 posts, 10-04) |
| Blog covers + inline images | gpt-image-1 at high quality + brand overlay; palette picked per topic, sampled from the real product | `src/lib/seo/cover-image.ts`, `art-palette.ts`, `inline-images.ts` | Pattern generic | live |
| `gero-medium` skill | Medium "kit" per post: one body, a Medium skin (headline, subtitle, hook, tags, alt text), canonical checked live after publish | `.claude/skills/gero-medium`, `docs/medium/` (README, voice, catalog), `scripts/medium/` | Pattern generic | live (pilot, Nov) |
| `nexus-content` skill | Comparison / pillar articles from a GTM foundation | `.claude/skills/nexus-content`, `docs/gtm/` | Gero-only | live |
| `nexus-tweets` skill + X engine | Data tweets from a live API; numbers built in code, the model writes only words; queue, mixer faders, image-batch composer, kill switch, best-hour slots | `.claude/skills/nexus-tweets`, `src/lib/x/*`, `/x` page | Gero-only; the "numbers in code" pattern is generic | live (Cloud Run) |
| X algorithm research | 2026 X ranking, cadence, link-in-reply, Premium+ as reach lever | `docs/x-agent/x-algorithm-and-growth-2026.md` | Generic for X | doc |
| Video Desk | One record per film, families + tiers + time slots, urgent mode, and a **5-check gate** before anything posts (numbers, banned words, keyframe visual check by Claude, series rules, format per destination) | spec `docs/superpowers/specs/2026-10-19-video-desk-design.md`, code in worktree `.claude/worktrees/video-desk` | Pattern generic | built, PR open, not live |
| Weekly data video series | launchd renders a Remotion film, writes the tweet, uploads to YouTube; 4 series a week | `scripts/*-weekly-*.sh`, `*-spotlight*.ts`, `videos/nexus-*` | Gero-only | live, run by hand (launchd blocked by macOS privacy) |
| Episode numbers | Every series run gets #N, stable across re-renders | `scripts/episode-number.ts` + `editions/episodes.json` | Generic | live |
| Remotion projects | Isometric "one world, one camera" films, Square + Vertical comps | `videos/gero-272-notifications`, `videos/nexus-*` | Gero visuals | live (approved films) |
| Review / approved folders | Every unapproved render in one flat `videos/_REVIEW/`; finals renamed `-APPROVED`, Green Finder tag, old cuts `-superseded`; ffprobe before sending | `videos/_REVIEW`, `videos/_APPROVED` (96 files) | Generic | live (one drift found 08-25: silent "APPROVED" files) |
| Video house style | 12 standing video rules (world not slideshow, same-size cards, zoompan gotcha, check the app has loaded before a still) | Gero memory `video-house-style.md` | Partly generic | standing |
| ElevenLabs skill | TTS narration per chapter, brand pronunciation dictionary, word timings returned (no Whisper) | `.claude/skills/elevenlabs` (`el.py`, `reference.md`) | Tool generic, dictionary Gero | live |
| Music families | Suno music as 13 reusable families, locked recipe, shared motif, cuts 15/20/60 s, VO bed, registry for licence proof | `docs/music/music-families.md`, `videos/_MUSIC/` | Pattern generic | draft (phase 1) |
| YouTube integration | OAuth on an Internal (Workspace) consent screen, upload, `thumbnails.set`, playlists, Home tab via `channelSections`, per-upload metadata JSON | `src/lib/youtube`, `scripts/youtube-*.ts`, `docs/youtube/` | Generic | live |
| Shorts playbook | Creator tips checked against YouTube 2026 | `docs/youtube/shorts-playbook.md` | Generic | doc |
| Channel refresh runbook | Step file for a browser agent: rules (never delete/hide), a check after every step, stop and report when the UI differs | `docs/youtube/youtube-channel-refresh.md` | Pattern generic | done 10-07 |
| OG card pipeline | HTML mockup rendered to 1200x630, new filename per version, `?utm_campaign=<version>` to bust X's card cache | gero-website repo + `OG_CARD_VERSION` | Generic (needs a site) | live |
| Metric registry `/pm` | ~69 metric IDs with baseline, target, gate flag; collectors for site health, GSC, GA4, YouTube, GitHub; monthly gate snapshots on the 1st, weekly digest, alerts, manual-entry page | `origin/main`: `src/lib/pm`, `src/app/pm`, `docs/pm/metrics.md` | Pattern generic | live (2 collectors stale since 10-01) |
| Q4 war plan + agile backlog | Strategy artifact; 71 GitHub issues in 4 monthly milestones (BUILD, CLIMB, PRESS, CLOSE), 8 sprints; every ticket = Why / Outcome / metric ID / How / Verify | GitHub + claude.ai artifact | Pattern generic | live |
| Ticket metric citation | Every ticket cites the metric it moves as a backticked registry ID; a cron grades compliance | `docs/pm/ticket-metric-citation.md` | Generic | live |
| UTM scheme | One table of link tags per channel, checked by a test | `docs/pm/utm-scheme.md` | Generic | live |
| Semrush pull + war room | One-time competitor pull via a friend's account | `New Foundings/`, artifact | Gero-only | one-off |
| LinkedIn content + engagement + connect | Adam's posts, likes and connects via Claude-in-Chrome; **its architecture was copied from the IoS IG/SC automation** | `src/lib/linkedin`, `docs/linkedin-agent` | Gero-only | built, dormant |
| GTM foundation | positioning, messaging, voice, proof, ICP, competitive | `docs/gtm/` | Pattern | live |
| Lighthouse CI, Playwright e2e, `memory-bank/` | Leftovers from the May 2026 website-redesign template; they test pages (`/about`, `/features`, `/search`) this app does not have | `lighthouserc.json`, `tests/`, `memory-bank/` | n/a | dead |
| `gero-cp-114`, `cp-pool-track` | Git worktrees of the same repo (DexHunter lead list; pool track-record frame) | sibling folders | Gero-only | nothing the main repo lacks for us |

## 2. What IoS already has for the same job

| Job | Gero tool | IoS already has | Gap |
|---|---|---|---|
| Platform SEO copy | gero-seo, prompt-library | `/seo-copy`, `seo_platform_specs.json`, `seo_copy_generator.py`, music-platform-seo + release-platforms skills, `/bios` | `/seo-copy` and `/bios` data untouched since Sep (code map); bio still electronic era |
| Copy bans | em-dash hard fail, banned-word grep | `caption_check.py` (dashes, emojis, name spelling), `copy_pass.py`, `copy_clean.py` | Not run on video on-screen text or YouTube fields |
| Brand foundation | `docs/gtm/` | `docs/brand/` positioning, proof, voice, frame, formats, reel-craft (same shape, already done) | none |
| Video tooling | Remotion + house style | HyperFrames (default) + Remotion skills, `videos/IOS-*` playbooks, motion library, sting | No pre-publish check; no review/approved folder flow |
| YouTube ops | `src/lib/youtube`, uploader, playlists, `channelSections` | `../youtube/tools/` (`yt_apply`, `yt_release`, `yt_thumbnails`, `yt_snapshot`), PLAYBOOK incl. Shorts 6.1 (same Dan-the-creator check, same date) | OAuth expires every 7 days (Testing mode, no website); tools not in git; no edit scope noted |
| Metrics | `/pm` registry, gates, digest | `plans/targets.json` (baseline, rungs, source, rule), score board, `stats/manual_entry.py`, `socials_digest.py`, `weekly_summary.py` | Tickets do not cite a target ID; Spotify followers and email list not in targets (code map item 2) |
| Ticket board | GitHub issues + milestones | `plans/tickets.json` (sections, P1-P3, `why` / `helps`), RM `/tickets`, `/board` | `helps` is prose, not a metric ID |
| Link tracking | UTM scheme | `bandcamp_links.py` (`?campaign=`) | No one table for all outgoing links |
| Image AI | gpt-image-1 covers | `/imagine`, `image_generator.py`, `raw_render.py`, AI-image rules | none |
| Long-form | Medium syndication | voice.md "Letter for Listeners" (IG carousel, EP only), Bandcamp descriptions | No long-form web channel (by choice so far) |
| Website / Google | gero-website, GSC, IndexNow | **No artist website** (PLAYBOOK 10.4: "he has no website") | Everything that needs an owned domain |

## 3. Transfer candidates, ranked by value for the music project

### 1. A pre-publish check for every video and post (from the Video Desk gate)

- **Take:** the pattern of Video Desk section 3: checks run when a file lands, each gives pass / fail
  plus one plain reason, any fail = held, results shown as chips. Not the code (TypeScript, Postgres, X).
- **IoS version, five checks:**
  1. Copy: `caption_check.py` over the caption, YouTube title and description, and the on-screen text list.
  2. Visual: 6 keyframes (0/20/40/60/80/100 %) through the bundled imageio-ffmpeg, sent to Claude with the
     expected content; fixed JSON answer: name spelled right (the "SHDAOW" cover shipped once), text over
     the face, Meta safe zone 270/672/65, no branding in the first 3 s, sting present, right cover.
  3. Format per destination: IG Reel, TikTok, YT Short (vertical, up to 180 s), YT long (16:9), Spotify
     Canvas (3-8 s, 9:16, no audio), using the `video_resizer.py` presets.
  4. Audio: an audio stream exists and the length matches the project (Gero's silent "-APPROVED" drift).
  5. Public status: no song-lane audio or title in a file meant for a public destination before Amir's switch.
- **Gives IoS:** content round one makes many short reels (experiments 1, 2, 5, 7) and the TikTok plan
  posts the same clips clean; one check catches the mistakes that cost a re-post (comments and reels
  cannot be edited). Ties to the IG, TikTok and YouTube jobs.
- **Effort:** M (one Python module + a chip row on RM `/video`, tests).
- **Must change:** all Gero checks (numbers vs edition JSON, Nexus white / Gero dark, cashtags, episode
  rules) drop out; IoS rules come from `frame.md`, reel-craft and the memory rules.
- **Risk:** the vision step sends frames of unreleased work to the Claude API (same path as today's API
  use, but say so first). A false "pass" is not proof: Amir still watches the render (render-and-shrink rule).
  It must never post anything; it is a report.

### 2. A clip pack per song (from Gero's music families)

- **Take:** the "pack" idea from `docs/music/music-families.md`: a locked recipe, fixed cuts (15 / 20 / 60 s),
  a stripped bed, a sting, and a registry of which video used which cut. Not Suno: his own masters are the music.
- **IoS version:** per single, stored in `releases/<slug>.json`: the 60 s TikTok start (the plan calls it a
  release decision), the reel hook bar (round one experiment 1 needs "the strongest bar from frame one"),
  a Spotify Canvas loop point, a Shorts Preview window; plus a `used_in` list per cut.
- **Gives IoS:** every reel, TikTok and Short starts from the same agreed timecodes; the `used_in` list
  answers Content ID questions later (PLAYBOOK section 9) and stops re-using a clip that already ran.
- **Effort:** S (schema fields + a small form on the release page).
- **Must change:** no families or brand motif; no AI music, ever.
- **Risk:** low. The choice of the bars stays Amir's.

### 3. The YouTube ops pack

- **Take (facts and small tools, all from `docs/youtube/` and the Gero youtube memory):**
  - `thumbnails.set` works through the API for long-form; Shorts covers are a frame pick, so put the
    title frame at about 2 s.
  - Playlists and the Home tab (`channelSections`) can be set through the API.
  - Shorts descriptions have no clickable links: set the "related video" per Short instead. End screens
    need 25 s or more.
  - Editing metadata needs the `youtube.force-ssl` scope (Gero hit "insufficient scopes" with upload-only).
  - Private-then-publish loses nothing, since ranking uses the publish time (Gero's claim from their research;
    check before relying on it).
  - Since 15 Sep 2026 `videos.insert` has its own bucket of 100 a day (Gero research; verify on first use).
  - A one-file uploader that needs `--confirm`, and one metadata JSON per upload plus an upload log.
  - The channel-refresh runbook format (rules for the agent, a check after every step, stop and report).
- **Gives IoS:** the YouTube job ("one finished official video per single, Shorts Previews before it")
  with less Studio clicking; the IoS tools already do metadata and thumbnails, this fills scopes, playlists,
  related video and the runbook.
- **Effort:** S to M (scope change + re-auth, two small scripts, bring `../youtube/tools` into git first,
  which the code map already proposes).
- **Must change:** Gero's Internal consent screen trick needs a Google Workspace domain; Amir's account is
  Gmail, so it does not apply. The 7-day OAuth expiry stays until there is a domain (see rank 5).
- **Risk:** API uploads stay private on an unaudited project (already known, PLAYBOOK 10.3). Made-for-kids
  must be forced false (PLAYBOOK 10.1).

### 4. Review and approved folders for renders

- **Take:** Gero's flat `videos/_REVIEW/` (everything waiting on Amir) and `videos/_APPROVED/` (finals,
  `-APPROVED` suffix, Green Finder tag written with `xattr`, older cut renamed `-superseded`), plus the
  check Gero added after its drift: before sending, `ffprobe` duration and audio stream against the project.
- **Gives IoS:** round one produces several cuts per experiment across HyperFrames projects; one place to
  look, and the file Amir posts is provably the final.
- **Effort:** S (a rule in the video playbook + a tiny helper script).
- **Must change:** the folder lives in `Inch of Shadow/videos/`; only Claude's own renders move there.
- **Risk:** it moves files. Under the ask-before-moving rule Amir must approve the flow once, and it never
  touches his own footage or older folders.

### 5. An artist website, and then Gero's Google kit (decision for Amir, not a ticket yet)

- **Take, only if a site exists:** the indexing ping (IndexNow + Google), the GSC index check, the nightly
  site-health ideas (sitemap URLs, non-200, double h1, titles over 60), the OG card pipeline (render
  1200x630, new filename per version), and Gero's schema lesson: Nexus showed the parent brand in Google
  because its home page lacked `WebSite` schema. For an artist: `MusicGroup` + `sameAs` to Spotify,
  Bandcamp, IG, SC, YouTube, plus one page per release.
- **Gives IoS:** (a) the 7-day YouTube OAuth expiry goes away, because PLAYBOOK 10.4 says publishing the
  app needs a home page and privacy policy on a domain he owns; (b) one EPK link for booking and press
  (today the EPK is attached by hand); (c) a home for the email sign-up the plan asks for "in bios and on
  every release page"; (d) Google's result for "Inch of Shadow" points at something he controls.
- **Effort:** L (domain, a small static site generated from `releases/*.json` and `docs/brand/`, hosting,
  upkeep).
- **Must change:** everything Contentful, GA4 and X. No cookies, so no GA4; Search Console alone is enough.
- **Risk:** it is new scope and not in the approved plan. External services (domain registrar, host) need
  the CLAUDE.md "inform first" step. A German artist site needs an Impressum with a name and an address
  (privacy cost; check the rule before deciding). It is one more thing to keep fresh.

### 6. Tickets cite a target, plus a look-back on the 1st

- **Take:** the citation rule (`docs/pm/ticket-metric-citation.md`): every ticket names the metric it moves
  by ID; and the monthly gate (snapshot on the 1st + one-line note).
- **Gives IoS:** the `helps` field on each ticket points at a key in `plans/targets.json`; the score board
  can show which tickets moved which number. Fits the code map's item 2 (add Spotify followers, email list,
  pre-saves).
- **Effort:** S (a `moves` field + a check in the tickets test).
- **Must change:** no GitHub, no cron grading; a field in `tickets.json` is enough.
- **Risk:** low. Do not turn tickets into paperwork; one ID per ticket, blank allowed for chores.

### 7. One-table link scheme

- **Take:** `docs/pm/utm-scheme.md` (one table: where the link lives, the tag, the channel).
- **Gives IoS:** Bandcamp `?campaign=` values, Spotify and pre-save links, email footers and bios follow one
  table, so "where did that sale or follower come from" has an answer. Ties to the Bandcamp and email jobs.
- **Effort:** S (a doc + `bandcamp_links.py` reading it).
- **Must change:** GA4 parts drop; Bandcamp only reads `?from=` / campaign (check what it shows).
- **Risk:** low.

### 8. Numbers built in code, words by the model

- **Take:** the `nexus-tweets` / X engine rule: figures come from code, the model writes only the prose
  around them, validators check the result.
- **Gives IoS:** session reports, the socials digest and release-day stats lines can never carry an invented
  number (memory: never fabricate report numbers).
- **Effort:** S per report, only where a model writes text with numbers.
- **Risk:** none; check first which IoS reports are model-written today.

### 9. Long-form, Medium style (low, later)

- **Take:** "one body, a skin" and "canonical to your own home" from `docs/medium/voice.md`.
- **Gives IoS:** little today. voice.md says usually nothing about a song's meaning, and the Letter for
  Listeners is an IG carousel for EPs only. The one fit: a Bandcamp release text (Bandcamp pages rank in
  Google, `plans/seo-strategy.md`) reused as the YouTube description and the email, same body, platform skin.
- **Effort:** S as a copy rule. A blog: not recommended.
- **Risk:** drifting into explaining the songs, which Amir does not do.

## 4. Ideas, not code

- **Timing test by week.** Gero runs hero posts at 10:00 in week 1 and 19:00 in week 2, then compares. Round
  one's rhythm container (2 reels + 1 carousel a week, 4 weeks) could split the same way at no cost.
- **Tag the people in the clip.** Gero's tagged spotlight posts got 2.3x the views (their data, X). Matches
  round one experiment 3 (collabs started by the bigger account) and the verify-handles rule.
- **Link in the first reply / comment, never the body.** Gero's rule on X; research says it is
  best-practice-consistent but unverified for 2026. On IG the link lives in the bio anyway; useful on
  YouTube comments and SC.
- **Theme mix as a dial, set by the numbers.** Gero rebalances theme weights when the market turns. For IoS:
  after each content round, face / hands / carousel shares move by what carried the ratio, Amir sets them.
- **Image-batch flow.** Amir drops a set of photos, Claude drafts one caption per photo as review cards,
  he picks. Fits carousels from the shoot catalogue (489 photos already tagged).
- **Urgent mode.** "We announce in 2 days": give the item a tier, take the slot, push the rest one slot.
  Useful for the release-day morning and a surprise gig.
- **Never delete and re-upload a stuck Short.** Already in IoS PLAYBOOK 6.1; keep it.
- **Series get numbers.** If a recurring format appears (studio notes, a mix series), number every run.
- **Resume from a ledger, not memory.** Gero's long builds log "Task N: complete" lines; worth it for any
  multi-session IoS build.
- **Datestamp facts and keep a fact sheet.** Gero's `gerowallet-fact-sheet.md` is the only allowed source of
  claims; IoS `proof.md` does the same job. Keep it that way.

## 5. Do not take

| Thing | Why not |
|---|---|
| X content engine, X API, nexus-tweets | X is not in the approved plan. The scene evidence (17 IG profiles, TikTok, YouTube channels) does not show darkwave growing there, and the X API now charges per post. Honest view: X does not matter for this act right now. At most, hold the handle so nobody else takes the name. |
| ElevenLabs voice | Amir sings and the brand is his face and process; never an AI voice on his work without his yes. HyperFrames already has TTS if a neutral voice is ever wanted. The one non-voice use, word timings for a lyric video, should run locally first (HyperFrames transcribe); sending an unreleased vocal to a third party needs his yes. |
| Suno music families | His own music is the music. The pack idea is taken (rank 2), not the generator. |
| Gero Remotion projects and the iso engine | Gero's look (isometric, white/dark product worlds) is not his; IoS keeps HyperFrames as default and already has the Remotion skills. |
| Video house style rule "open on the logo alone" | Clashes with the IoS rule: no branding in the first 3 s. Other house rules are product-UI specific. |
| gero-seo, SEO automation pipeline, in-place refresh, internal-link pass | Built for a Contentful blog of 58 posts. No blog here. |
| Lighthouse CI, Playwright e2e tests, `memory-bank/` | Template leftovers that test pages the Gero app does not have; RM is a local Flask app, not a public site. IoS has 1,136 passing pytest tests. |
| LinkedIn agent | Not a music channel. It was itself modelled on the IoS IG/SC engine, so there is nothing new to bring back. |
| GA4 and Semrush pulls | No site; Semrush was a one-time borrowed login. |
| GTM foundation docs | IoS `docs/brand/` already has the same shape (positioning, proof, voice). The "ICP" part clashes with the IoS rule that the audience gets no tag. |
| Featuring policy, cashtags, Gero Card bans, Nexus pricing bans | Gero-only rules. |
| Gero's Internal OAuth consent screen | Needs a Google Workspace domain; Amir's YouTube runs on a Gmail account. |
| Next.js / Postgres / Cloud Run stack | IoS is local Python on one Mac, by design (privacy first). Patterns travel, the stack does not. |

## 6. Notes

- Already transferred before today: the Shorts creator-tips check exists in both repos on the same date
  (10-14), and Gero's "no em dashes" rule matches IoS copy rules.
- Gero's launchd video jobs hit the same macOS Full Disk Access block IoS solved on 09-03 (FDA on the real
  python binary). The fix may be worth telling the Gero side; not our scope.
- Out of scope, one line: the IoS memory index is over its size limit (28.4 KB of 24.4 KB), so 23 lines are
  cut off at load; Gero keeps its index lines short.
