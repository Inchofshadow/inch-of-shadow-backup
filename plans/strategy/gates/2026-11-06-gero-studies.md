# Fable gate: the four Gero follow-up studies (2026-11-06)

Amir's asks after the first transfer study: (1) research whether the clip pack is a good move on TikTok
and IG, (2) a better review system than folders, (3) go deeper into the control panel's code, metrics and
dashboard ("super accurate", ours should look better), (4) the product lens (brand = Inch of Shadow,
product = the songs), (5) GitHub and the ticket system. Website, X and LinkedIn are out.

Four files, each checked here. Claims about our own code were verified on disk; Gero claims were
spot-checked against the repo (its metrics core lives on `origin/main`, exported read-only into the
scratchpad and moved to the Trash afterwards).

## 1. `gero-cp-deep-dive-2026-11-06.md` (metrics, dashboard, review flow). Verdict: approve.

| Claim | Checked | Result |
|---|---|---|
| Gero's registry holds 80 metrics, pinned by a parity test | `src/lib/pm/__tests__/registry-parity.test.ts` on origin/main | Confirmed (the test pins the count) |
| Our verdict can print ON PACE while a card is red | `release_manager/score_board.py:192-199`: majority-green rule | **Confirmed.** Gero's rule (any red = off pace) is stricter and more honest |
| We define metrics in three places | `plans/targets.json`, `stats/propose_targets.py`, `stats/socials_digest.py` | Confirmed |
| Our collectors return None, no skip reason | by the agent; consistent with the 11-05 system-loop findings | Plausible, not re-read line by line |

What holds: Gero's accuracy is six habits, not its database: one registry, provenance per sample, skip
reasons instead of zeros, one freshness red line, frozen monthly gates, pure rule modules with `now` as a
parameter and tests. All six fit a JSON-file system. The dashboard brief (verdict first, freshness strip,
six cards with 🤖🎃🙋 per source, Marcellus numerals, Jost labels, warm black / platinum, never a zero that
means "not collected") is the right shape for ours.

Review flow: the hash-bound model (item = path + SHA-256, states draft / needs-you / approved / change /
dropped / superseded / used, approval bound to the hash, new version = new item) answers exactly what
Amir disliked about folders and what went wrong at Gero (silent "approved" files). RM `/review` plus a
phone page on the outreach-page pattern. The agent never posts, moves, renames, deletes or approves.
**This is the review system to build**, not the folders.

## 2. `product-lens-2026-11-06.md`. Verdict: approve.

The mapping table is sound and the eight methods are all S or M. The strongest line is the judgement
call: **a new fan gets nothing** after a follow or a sign-up (release-lessons shows 1.7% listener to
follower). One message, once, per door: a welcome mail, a pinned Artist Pick that names what comes next,
the SC follower-only drop already in the plan. Not a newsletter. Web evidence correctly tagged; Bandcamp
Friday dates (today 6 Nov, 4 Dec) agree with the listening research.

Skills verdict is honest: ads, ad-creative, influencer-marketing and most of analytics do not fit; launch,
co-marketing, public-relations and marketing-psychology fit in part; the IoS release/promo/ig/sc/bio skills
are the machine and need these methods as inputs.

## 3. `gero-github-tickets-2026-11-06.md`. Verdict: approve.

| Claim | Checked | Result |
|---|---|---|
| 10 open tickets on our board have no bucket | `plans/tickets.json` | **Confirmed**: M-13 and ST-01..09 (🎸 Studio never sent its buckets) |
| Nothing enforces the max-3-now cap; the board tests do not know `bucket`, `area`, `who` | `tests/test_tickets.py`, `test_board.py`: 0 mentions | **Confirmed** |
| Gero: 39 issues on the control panel, 30 cite a metric id, 100 PRs, 95 merged | `gh` read-only as ThirdEye707 | Taken as read (numbers from the live API) |
| Gero's pm-tickets collector dead since 1 Oct, milestones all open | Gero memory + issue #101 | Confirmed by the agent; the lesson stands: a metric tie is only as good as the collector |

Verdict I share: **no move to GitHub issues now**; take the shape today (metric + "done means" +
`updated` on every ticket, one priority axis instead of `priority` and `bucket` saying the same thing,
tests that know the fields and enforce the cap); mirror one-way to GitHub later for the phone; PR flow
with CI only after the history scrub. Never issues-as-board from chats.

## 4. `research-clip-pack-2026-11-06.md`. Verdict: approve with 2 wording fixes (applied).

| Claim | Checked at | Result |
|---|---|---|
| Instagram: identical pieces on Instagram, only the original is recommended; 10+ reposts in 30 days = no recommendations | creators.instagram.com/recommendations-and-originality | **Confirmed** (the file's phrase "already posted on Instagram" was not on the page; replaced with the page's own rule) |
| TikTok: duplicates not recommended | tiktok.com/community-guidelines integrity-authenticity | **Confirmed in substance**: the rule is "unoriginal or reused material without anything new" is ineligible for the For You feed; the file said "duplicated content", fixed to the real wording |
| YouTube: a Short over 1 minute with any active copyright claim is blocked | support.google.com/youtube/answer/15424877 | **Confirmed** (so his own Content ID can block his own long Shorts) |
| Spotify Canvas: 3-8 s, 9:16, 720-1080 px tall, MP4 or JPG, no talking or singing, no links, no follow calls, no other brands or the Spotify logo, text must relate to the song | Spotify Canvas guidelines + content policy pages | **Confirmed** |
| Symphonic 60 s Clip Start Time still the rule | read from the search index (symphonic.com returns 403 to every agent) | Plausible, unverified at the source, same gap as before |

What holds and what it changes in the idea: the clip pack is a good move **with four changes**. Export the
masters silent and attach the sound inside each app (TikTok library sound, IG named audio), so the sound
page collects every use. The fixed element is the audio section, not the opening shot: the first frame
changes per post, the hook bar stays. Most cuts 8 to 20 s, every TikTok cut inside the delivered 60 s
window. `used_in` blocks a second identical upload on the same platform instead of only logging it. Three
questions for Symphonic before relying on more: Shorts Previews on Starter, more than one TikTok clip per
track, Content ID whitelisting for his own channel. No study measures cross-posting penalties or hook
fatigue; those two are judgement, labelled as such in the file.

## What this changes
- Nothing starts on its own; Batch 3 stays paused.
- The review-flow model (1) and the ticket shape (3) belong in Batch 3's L3 and in the RM 2.0 blueprint;
  the dashboard brief (1) replaces the plain "scoreboard rows" idea in S1; the activation rule (2) is a new
  strategy card for the page. All of that waits for Amir's go.
- Scratch: the Gero `origin/main` export was moved to `~/.Trash/gero-main-export-2026-11-06/`.
