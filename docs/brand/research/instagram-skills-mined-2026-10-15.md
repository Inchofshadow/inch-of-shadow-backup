# Three Instagram skill repos, mined 2026-10-15

What this is: Amir sent three GitHub repos and asked whether any is relevant to
us and whether they hold something we do not have. All files were downloaded to
an isolated scratchpad and read at source (READMEs, every SKILL.md, the
reference docs, hooks.json, rubric.json, the Python tools). Nothing installed,
nothing changed in the repo except this file. Companion to
social-media-skills-mined-2026-10-06.md. Revert = delete this file.

| Repo | Stars | Last push | What it is |
|---|---|---|---|
| sergebulaev/instagram-skills | 436 | 2026-10-15 | 9 writing skills + Publora auto-publish + Apify read layer + Pixfaro AI images; by a content-engineering agency |
| vrajdesai78/instagram-skill | 1 | 2026-05-26 | one skill that calls Instagram's PRIVATE web API from inside the user's logged-in Chrome session |
| Jakeschincariol/instagram-agent-skill | 1,436 | 2026-09-13 | 13 skills + 5 offline Python tools (hook scorer, beat timer, caption linter, humanizer, swipe-file ranker); MIT; no network |

Verdict in one line: nothing to install; repo 2 is a hard no; repo 3 holds
five small offline tools and four methods worth taking; repo 1 adds one
humanizer insight and nothing else we lack.

## Repo 2: vrajdesai78/instagram-skill. REJECT.

It runs JavaScript inside the signed-in Instagram tab and calls
`instagram.com/api/v1/...` with the session cookie and the web app id. That is
the exact class of read that got the account four 429s in September and led
to the 09-14 decision: no logged-in reads, ever, all reads through HikerAPI.
The repo itself admits Instagram throttles after ~10 rapid calls. Its endpoint
catalogue (hashtag sections, location sections, shortcode-to-pk decoding,
saved collections) is competent, and HikerAPI already covers every one of
those reads without touching Amir's account. The only thing it can do that
HikerAPI cannot is read Amir's own DM threads and saved collections, and that
is not worth a flagged account. Its second skill (skill-cleaner) ships without
its own analyzer script.

## Repo 1: sergebulaev/instagram-skills. Nothing to adopt, one note.

| Repo says | We already have | Where |
|---|---|---|
| hook in the first 125 chars, body skimmable, one CTA | same | ig-agent-context §10 |
| 3-5 sized hashtags, size tiers, rotate sets | same, with the 10K-500K tier since 10-06 | ig-agent-context §9 |
| sends and saves over likes, first 30-60 minutes, reply fast | same, 60-minute rule | ig-agent-context §11, reel-craft §2 |
| Reels for reach, carousels for saves, stories for the base | same, measured on his own posts | reel-craft §1 |
| name field with a searched keyword, pinned 3, highlights, link | same (pinned 3 noted 10-06) | ig-agent-context §8 |
| voice profile file read by every skill | docs/brand/voice.md v2, built from his captions | docs/brand/voice.md |
| Apify read layer (hashtag reels, profile stats) | HikerAPI, deeper (follower lists, 163 routes) | scene_intelligence/ig_data_provider.py |

Rejected: Publora auto-publishing (Amir posts by hand, always); Pixfaro AI
illustrations (AI images only with his go per image, and never a stock
generator); the 10 hook formulas IG1-IG10, written for coaches and founders
("I cut my editing time from 6 hours to 47 minutes") and not usable in his
register without translation; the content planner's 40/30/20/10 pillar split
and "4-5 feed posts a week" cadence (ours is set by releases, and no posting
reminders); the em-dash rule (they cap at ~1 per 100 words and say zero
dashes is itself a tell; Amir's rule is zero, keep ours).

The one note worth keeping, from the Humanizer V3: the 2026 reader-tells are
structural, not vocabulary. "The result?" reveals, "It's not X, it's Y",
staccato stacks ("No X. No Y. Just Z."), one-word lines for drama, and
sincerity announcements as openers ("real talk", "not gonna lie", "honestly?",
"unpopular opinion:" on a popular one, "POV:" on something that is not a POV).
Our voice.md Never list has em-dashes, meta lines and feedback asks; it does
not name these shapes. Also their over-correction guard: a humanizer that
strips every triad, every emoji and every quirk leaves its own fingerprint,
so edits must be proportional to real problems.

## Repo 3: Jakeschincariol/instagram-agent-skill. Relevant. Take the methods, not the pack.

The honest one. It says what its scorer cannot do (it kills weak hooks, AUC
0.83 against deliberately bad ones, but does NOT pick winners, AUC 0.56, a coin
flip), its corpus is YouTube Shorts not Reels, and its formula classifier only
names 49% of real hooks. Written for creators who sell ("clients", "$18,000
mistake", keyword DM funnels), so the examples are off-register, but the
mechanics underneath are platform mechanics.

### Already covered by our own docs

| Repo says | We already have | Where |
|---|---|---|
| first two seconds decide, static opener loses | same, measured: ~50-65% gone by 0:02, slow walk-in lost people | reel-craft §1 |
| views but no follows = profile problem, not a hook problem | same: "reach does not turn into follows; the profile's first impression is its own job" | reel-craft §1 |
| hashtag cap 5 since 2025-12-18, tags are labels | same | ig-agent-context §9 |
| on-screen safe zone (nothing above y=230, below y=1440, right 230 px clear) | Meta safe zone 270/672/65 in the render-and-shrink check | docs/brand, memory |
| burn captions, muted-first viewing | same | ig-agent-context §11 |
| never invent a number; `{{your number}}` placeholder | same: never fabricate report numbers | memory, voice.md |
| 60-minute reply window | same | ig-agent-context §11 |
| engagement round before posting: 5 reach / 3 peers / 2 buyers | Track A reach + Track B scene lanes | ig-agent-context §13 |
| DM: they act first, reference the specific thing, give before asking, no link in message one | his own DM shape (warm line on their music + what he did + link last) | memory dm-style-cold-contacts |

### What we do not have (new or sharper, no clash)

1. **caption.py**: prints the first 125 characters as a box, the way the feed
   shows it, then lints: length, first-line cut mid-thought, concrete marker
   in the visible window, hashtag count vs the cap of 5, exactly one ask,
   search terms present, emoji density, no URL in the body. 300 lines,
   standard library only, no network. We have the 125-char rule and no tool
   that shows the cut.
2. **humanize.py + detect.py + slop.json**: strips invisible characters
   (zero-width spaces and joiners, soft hyphens, BOMs, tag characters) that
   survive copy-paste from AI drafts, normalises typography (em dash to comma,
   curly quotes straight, ellipsis to dots), swaps 154 stock terms, and flags
   structural tells for a hand rewrite. The invisible-character pass is the
   part we have nothing for; the em-dash-to-comma pass is Amir's rule in code.
   Offline. The Instagram block of the lexicon ("follow for more", "tag
   someone who", "double tap if", "run don't walk") matches our no-asks rule.
3. **Outlier multiple**: views divided by that account's own median over its
   last ~12 reels; only above 3x is a signal, below 1.5x is a normal day; read
   accounts within about 10x of our own size. Our reference loop (Shadow
   Archive, 10-06 item 8) reads technique but ranks nothing against the
   account's own baseline, so a big account's quiet Tuesday looks like a hit.
   With HikerAPI's user clips route (play counts per reel) this is a
   ~13-request job per account, no browser, no login.
4. **Audit columns**: hold at 3 seconds (viewers at 3s / starts), sends per
   reach, follows per reach, non-follower share of reach, outlier multiple.
   Our perf log tracks reach, views, likes, comments, saves, shares; it does
   not compute the four ratios, and they are the ones that say hook vs middle
   vs profile. Instagram's insights expose all of them.
5. **beats.py**: estimates seconds per spoken line at a given wpm, stacks
   them into timecodes, flags a hook past 3 s, any beat over 4 s with no frame
   change, and no loop back to the first line. For the songs (sung or spoken
   lines to camera) this is the first timing tool we would have; for music-only
   reels it does nothing.
6. **hookscore.py**: use only as the author says: to kill an obviously weak
   first line (greeting, preamble, "stop scrolling", nothing concrete) before
   a shoot. Never to choose between two decent hooks. Of the 26 formulas, the
   ones that fit a musician's register: #13 Before And After On Screen (a mix
   before/after, fits process over product), #18 Cold Open Demo (mid-action,
   hands already moving), #21 Mid-Sentence Start, #24 The Reveal (a new
   track, a new piece of gear), #6 The Receipt (an experiment with real
   numbers), #16 The Verbatim Question (a comment read out loud). The rest
   are coach formulas.
7. **Profile rubric** (12 items, 100 points): name field 12, bio line one 12,
   pinned three 10, recent activity 10, highlights 8, grid legibility 8, bio
   body 8, link 8, photo 6, handle 6, category 6, story presence 6. We have a
   setup list in §8, not a score; a score makes the before/after visible.
   Highlight names need translating (theirs: Pricing/Results; ours:
   Releases/Live/Studio/Visuals).
8. **Follow-up cadence for outreach**: two follow-ups and no third: +4 days
   with something new (never "just bumping"), +10 days the close-the-loop
   message that says you will stop. The collab pitch in four lines: what you
   watched them do, the specific idea, what they get, what you need. Our
   booking and DJ outreach rules say nothing about follow-up timing.
9. **Stories shape**: 3-7 frames, the sticker ask at frame 4 not at the end
   (completion drops per tap), a face or hand in frame one, the question box as
   a harvest of the audience's own words for later hooks, never repost a feed
   post to stories without a line on why. Our §12 has use cases and cadence,
   not the frame order.
10. **Comment and reply triage**: nine comment types (add a datum, the missing
    case, respectful disagree, extend one line, the real question, the receipt,
    the correction, the reframe, the one-liner) and six reply buckets (keyword,
    lead, substance, question, support, noise) written in that order; a
    question many people share becomes a Reel reply, not a text reply. Our
    Track B "scene likes" never defined what a good comment is.

### Rejected (clashes with our rules, or not for us)

- "No browser tool, the user pastes" and "never automate engagement": their
  product stance, same as the 10-06 verdict. Our engagement automation has its
  own guards and stays.
- Keyword CTAs ("comment CONTRACT"), keyword DM delivery, "what you sell",
  offer posts: selling funnels, off-brand. We describe the track, we do not
  solicit.
- 4-5 posts a week with at least three Reels: cadence is set by releases, and
  no posting reminders.
- Installing the 13 skills as /ig-* commands: they would compete with /ig,
  /promo, /release and the brand skill; the five tools are worth more as files
  than as skills.

## Proposed changes (none applied; each needs Amir's yes)

A. Copy the five tools (caption.py, humanize.py, detect.py, slop.json,
   beats.py, hookscore.py, swipe.py; MIT, 1,466 lines, standard library only)
   into a tools folder and run caption.py + humanize.py as the last pass in
   the Release Manager copy writers. The em-dash pass is already his rule.
B. ig-content-performance-log.md: add four computed columns per post (hold at
   3 s, sends per reach, follows per reach, non-follower %) from his insights
   screenshots. The diagnosis rule: no views = hook, views no follows =
   profile.
C. Shadow Archive / reference reads: adopt the outlier multiple as the
   ranking for other artists' reels, pulled through HikerAPI (user clips, ~13
   requests per account). Only accounts within ~10x of our size count as
   evidence.
D. docs/brand/voice.md Never list: add the structural tells (reveal
   bridges, staccato stacks, one-word drama lines, sincerity announcements,
   "POV:" misuse) in one block.
E. Outreach rules (booking emails, DJ promo DMs): the +4 / +10 day follow-up
   cadence and the four-line collab pitch. One paragraph each.
F. ig-agent-context §12: the story frame order (ask at frame 4, face in
   frame 1, question box as harvest). Three lines.
G. ig-agent-context §8: the 12-item profile score as a yearly check, with
   musician highlight names. One table.

Sources: the three repos above at HEAD on 2026-10-15; files read listed in the
session transcript. Local copies: session scratchpad igskills/.
