# Fable audit of the strategy review (2026-11-05)

Reviewer: Claude Fable 5.1, same chat, after the Opus work. Read: the Refresh page v6, the 6 deep-pass files,
the facts page, the drafts, the handover. Spot-checked the load-bearing claims at the source and the code
facts on disk. Opinion, then what to redo.

## Verdict in one line
The structure is right and most of it holds. Two things are missing: research on the one job Amir will spend
the next 2-3 months on (content language), and a primary-source check on two claims the page leans on.

## What I checked at the source

| Claim on the page | Checked | Result |
|---|---|---|
| Spotify: one pitch at a time, 7 days minimum, released songs cannot be pitched, video pitch separate | Spotify for Artists support page | **Confirmed, word for word** |
| Release Radar listener filters since 10 Jul 2026, up to five | Spotify newsroom | **Confirmed** |
| SoundCloud Follower Exclusive Releases, Artist Pro, 30 Mar 2026 | SC help centre article exists + Hypebot/MBW | **Confirmed** |
| Meta Q3: ~45% of recommended Reels under a day old, sequence ranking | 4 secondary write-ups, no transcript | **Consistent, secondary only** |
| Trial Reels: 200 followers for professional accounts | 6 vendor pages quoting the help centre; 2 say 1,000 | **Likely, unsettled**: the app toggle decides (already planned) |
| Amazon Music pitch up to 14 days after release, one track per release | Amuse, iGroove, Dynamoi, RouteNote | **Confirmed by vendors**; owner/admin detail unverified |
| SoundCloud Terms ban automated follow/unfollow (19 Jan 2026) | soundcloud.com/terms-of-use | **Not verifiable by fetch** (error page). The agent read it; I could not. Amir has decided anyway |
| Code: side branch ahead of main, stale branches, Python 3.9 in launchd, tests | git + plists + pytest | **Confirmed**: 99 ahead (was 91 this morning), 22 branches, 4 plists on 3.9, 1,136 pass |
| Spend: Gap Radar $32.68 of $36.14 in Nov | stats_snapshots/claude_spend.json | **Confirmed** |

## What holds up well
- The tagging system (OFFICIAL / REPORTED / CLAIMED / MYTH) is applied consistently across 4 files. Blog numbers are
  marked as blog numbers. That is the main reason the page can be trusted.
- Code first, then decisions: right order. Batch 1 has no item that needs a decision, and each item gives data.
- Keeping the electronic stats in the scoreboard and refusing to archive anything that feeds RM: right.
- The myths found in our own docs (saves top-3, "Your Algorithm" routing our posts, Discorank, "pitching can hurt",
  Apple via Symphonic) are real finds and all have a source for the correction.

## What I would redo or add

1. **Content language research (missing, highest value).** S7 is Amir's main work for 2-3 months and rests on
   general IG rules plus the brand kit. No pass looked at what post-punk / darkwave / new wave solo acts actually
   post in 2026 and what of it works: formats, hooks, face and process, length, music tools, how often. Needs its
   own deep pass: 10-15 named accounts in the neighbourhood (R. Missing, Boy Harsher, Lebanon Hanover, Twin
   Tribes, Molchat Doma, smaller Berlin acts), per account the formats that get reach vs the ones that do not,
   with numbers from their public pages, feeding the Shadow Archive. Effort: high. Do this before the first content round.
2. **SoundCloud Terms quote.** Open soundcloud.com/terms-of-use in Amir's Chrome once and paste the exact sentence
   into the listening file. Not for the decision (made) but so the record is primary.
3. **Half the Night pitch timing is not on the page, on purpose, but the release chat needs the two confirmed rules
   now:** 7 days minimum, and the pitch is the only way to choose the Release Radar song. One line to 🎵 Release.
4. **Symphonic Starter facts.** symphonic.com returned 403 to every agent. What Starter can deliver (video to
   Spotify, Shorts Previews, TikTok) decides three cards. One support ticket or one look in SymphonicMS settles it.
5. **The ask-rules draft can stall scheduled runs.** `settings-enforced-rules.draft.json` puts `mv`, `rm`,
   `rsync` on "ask". The draft notes it; the gate must grep the IG/SC scripts for those commands before it goes
   live. Do not apply D12 item 4 without that check.
6. **Process.** The page went through 6 versions today because the frame (what Amir wants to see) came after the
   build. The gate below fixes that: frame first, one paragraph, his yes, then build.

## Not needed again
- TikTok, Berlin calls, backups, pitching mechanics, listening platforms: good enough for this review cycle.
- Money in/out: out by his call.

## Rule 1: the Fable gate (our standard from 2026-11-05)
For every big plan, important change or decision, the songs included. The reviewer is never biased toward
the chat's own work and always tells Amir the truth, "redo" included. Gates and the work under review use the
new agents and skills (llm-council for real trade-offs, code-review / ultra, research-deep, the brand kit,
ig-expert, sc-expert, promotion-expert), not one model's opinion.

| When | What Fable does | Output |
|---|---|---|
| Before a plan or strategy page goes to Amir | reads it with its sources, checks 3-5 load-bearing claims at the source, checks it against the rules in memory | approve / approve with fixes / redo, in 10 lines |
| Before a draft that changes rules, settings, schedules or memory goes live | reads the draft and the scripts it touches | same |
| After each batch | reads the diff and the tests, checks the numbers moved | same |
| Before `main` gets the side branch | `/code-review ultra` | findings list |

How the hand-off works: the Opus chat ends the turn with the line **"🟣 Fable gate: <what to review>"** in the
wrap-up question. Amir switches with `/model claude-fable-5-1` in the same chat (or opens a side chat on Fable),
says "gate", Fable writes the verdict into `plans/strategy/gates/<date>-<what>.md`, Amir switches back.

## Rule 2: when to raise effort or use ultra
| Use | For |
|---|---|
| Default effort | page copy, ticket merges, one-file fixes, reports, handovers |
| **High / xhigh** | research where sources disagree or a number drives a decision; any change to settings, schedules, memory or the engagement side; the content-language pass |
| **`/code-review ultra`** | before merging `score-board` into `main`; after each RM 2.0 batch |
| **Ultracode (workflow)** | RM 2.0 split (142 routes), the dead-code move, the Python 3.12 move: many files, tests must stay green at each step |
| **Max** | only when Amir asks, or for a decision that cannot be undone (account risk, money) |

Rule of thumb: raise effort when a wrong answer costs more than the tokens: anything irreversible, anything
many agents read, anything with money or an account attached.
