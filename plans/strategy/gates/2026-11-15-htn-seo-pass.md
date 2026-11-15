# Gate: Half the Night SEO pass for SoundCloud and Bandcamp (2026-11-15, Fable, on Amir's "gate")

Opus wrote `plans/htn-seo-pass-2026-11-11.md`. Five load-bearing claims checked at the source today. Late gate: the Bandcamp page went live on 11-13 with the approved about line before this read.

## Verdict: approve with two small fixes. No recommendation changes.

| Claim | Checked | Result |
|---|---|---|
| SoundCloud builds the Google title from title + username | live page `soundcloud.com/inch-of-shadow/inch-of-shadow-farewell`, 11-15 | ✅ exact: "Stream Inch of Shadow - Farewell by Inch Of Shadow \| Listen online for free on SoundCloud". The Deceiver page reads the same way. So a plain title is the cleaner one |
| The SoundCloud username shows as "Inch Of Shadow" (capital O) | live profile title | ✅ "Stream Inch Of Shadow music ..." |
| Bandcamp: tags come from 5 places, no documented order, no limit, Discover needs the exact spelling | Bandcamp help "What are tags", 11-15 | ✅ all four points as the pass says |
| Bandcamp traffic: 595 visits, Google 46, Bandcamp search 13, Discover dark-disco 5 | `plans/bandcamp-traffic-plan-2026-10-21.md` lines 29 to 47 | ✅ |
| The proposed tags break no locked rule | `releases/pinocchio-single.json` tag_rules | ✅ electro, acid, EBM, italo disco, Berlin, acid disco, germany: none on the never list, no text-only word used as a tag |
| SoundCloud help: genre is the first tag, similar genre tags give no boost, multi-word tags stay whole | `help.soundcloud.com` | ❌ not verifiable: the help site answers 403 to text readers, as the pass's own check table says for the tag limit. The pass still labels these [OFFICIAL] |
| The scene's genre words: EBM 13, dark disco 8, electro 7, acid 6, industrial 5, post-punk 3 | `scene_intelligence/dj_promo_targets.json` (unchanged since 11-03), counted today | ⚠️ three counts are off: dark disco 7, acid 8, post-punk 2. EBM 13, electro 7, industrial 5 are right. The conclusion (the tag set matches how these DJs file music) holds |

## Fixes
1. Relabel the three SoundCloud help claims from [OFFICIAL] to [NOT VERIFIED 11-11, help site blocked]. They only support "keep" decisions, so nothing live changes.
2. Correct the three counts in "The scene's own genre words".

## Note for ⚙️ System 102 (the release SEO skill)
- Its input list names BPM and key from the release JSON. Amir's rule of 11-11 says no key in copy and BPM only when he asks. Put that into the skill's script guards, next to the no-em-dash and never-list checks.
