# Fable gate: Gero transfer study (2026-11-06)

Reviewed: `plans/strategy/gero-transfer-2026-11-06.md` (written by an Opus-started agent, 252 lines, 9
ranked candidates). I read the Gero control-panel repo myself first (the gero-seo skill, the SEO
automation scripts, docs/music, docs/youtube, the videos review folders, the npm script list) so the
check is independent, then spot-checked the five claims the ranking rests on.

| Claim in the study | Checked where | Result |
|---|---|---|
| Gero's Video Desk has a five-check gate, any fail = held | `docs/superpowers/specs/2026-10-19-video-desk-design.md:218` | **Confirmed** |
| Gero once shipped silent "-APPROVED" files (why the ffprobe check) | Gero memory `video-review-folder.md:36` | **Confirmed** |
| Our YouTube OAuth expires every 7 days in Testing mode; publishing the app needs a site | `youtube/PLAYBOOK.md:456` | **Confirmed** (the "needs a home page and privacy policy" part is Google's publishing rule, stated in 10.4) |
| Gero's LinkedIn assistant was modelled on the IoS IG/SC engine | Gero memory `linkedin-engagement-assistant.md:3, :20` | **Confirmed**: nothing to bring back |
| X API is pay-per-use to post | Gero memory `x-content-engine.md:36` | **Confirmed** |

No secrets in the file (grep for the panel login and the IndexNow key: none). No em-dashes.

## Verdict: approve. Two changes to the ranking, one decision to surface.

1. **Rank 2 (clip pack per song) should be first.** It is S effort, it stores the TikTok 60 s start that the
   approved plan already calls a release decision, and it gives round one its "strongest bar from frame one".
   Rank 1 (the pre-publish check) is right but M effort and it sends frames of unreleased work to the
   Claude API; it belongs after round one has produced its first cuts, with Amir's "say AI first" rule applied.
2. **Rank 4 (review and approved folders) can go live with rank 2**: a playbook rule plus a tiny helper,
   and it answers a real risk (the file he posts is provably the final). It moves files, so one yes from him.
3. **Rank 5 (artist website) is a strategy decision, not a transfer.** The study is right to flag it and
   right not to make it a ticket. What it would change: the 7-day YouTube login, one EPK link, a home for the
   email sign-up, and Google's result for his name. What it costs: a domain, upkeep, and an Impressum with a
   name and address under German law. It should be a numbered decision on the Refresh page (D19) for when
   Amir wants it, not slipped into a batch.

## Honest notes
- The study's "ideas" section (link in the first reply, theme mix follows the week, numbers from code and
  words from the model, one-table link scheme) is the cheapest value here: rules, no code.
- Medium / long-form: correctly "low, later". There is no songs-era story to write until the switch.
- ElevenLabs: correctly "do not use for voice". Word timings for lyric videos run locally first; an
  unreleased vocal never leaves the machine without Amir's yes.
- The gero-seo skill pattern (keyword map, a fact sheet as the only source of claims, dedup before writing)
  is the model for the Semrush check (🎵 Release 11) when that moment comes.

Nothing from this study starts on its own. Batch 3 stays paused.
