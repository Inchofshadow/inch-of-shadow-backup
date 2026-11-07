# IG export analysis, 2026-10-10 (All-time export, read-only)

Source: data/instagram-inch_of_shadow-2026-10-10-HHMbmVAJ/connections/followers_and_following/
Compared against: ig_follow_tracker.json, enriched_contacts.json (SI), ig_target_list.json (queue).
Nothing was written from this analysis. Proposed writes are listed at the end and need Amir's go.

## 1. The account

| | |
|---|---|
| Followers in export | 955 (profile shows 948; the export keeps a few deactivated/removed) |
| Following in export | 970 |
| Mutual | 579 |
| You follow, no follow-back | 391 |
| Follow you, you don't follow | 376 (331 of them unknown to SI and the queue) |
| Hashtags followed | 13 |
| Pending requests / blocked / restricted | 0 / 0 / 0 |

## 2. Growth, by the month people followed (export timestamps)

| Month | New followers | Follow lane |
|---|---|---|
| 2026-01 | 12 | off |
| 2026-02 | 8 | off |
| 2026-03 | 13 | off |
| 2026-04 | 23 | starting |
| 2026-05 | 34 | full |
| 2026-06 | 40 | full |
| 2026-07 | 39 | full |
| 2026-08 | 24 | throttled (429s) |
| 2026-09 | 25 | thin supply |
| 2026-10 (to the 10th) | 8 | paused since 09-26 |

Since the 08-17 baseline (925): +40 followers. Follows ARE the growth engine: months with the lane at full pace run 34-40, months without it run 8-13.

## 3. Automation follow-back rate (export = truth)

| Cohort | Followed | Follow back today | Rate |
|---|---|---|---|
| May | 54 | 14 | 26% |
| June | 91 | 16 | 18% |
| July | 81 | 18 | 22% |
| August | 34 | 7 | 21% |
| September | 58 | 17 | 29% |
| All since May | 319 | 72 | 23% |

KPI is >= 15% on the genre-seed queue. Every month clears it; September, the provider-vetted + browser-vetted supply, is the best.

Follow-back latency (n=77): median 0 days; 72 within 7 days; 2 between 22 and 60 days; 3 followed Amir before we followed them. The 7-day unfollow window is right. Follow-backs that come, come fast.

## 4. The tracker was wrong about reciprocity, twice over

- Active: 26 of the 59 active automation follows follow Amir back. The tracker had 10. Sixteen were marked no-follow-back, and five of those were on the 10-09 hand-unfollow list.
- History: 46 accounts were unfollowed (44 by the automation, 2 by hand) WHILE they were already following Amir. Dates: 2026-05-21 to 2026-08-28. They all still follow him today. The follow-back checker of that era simply did not see them. Churn stopped once the export gate came in (last case 08-28). Per Amir's rule of 2026-08-30 this is reported as data only; no re-follow recommendation.
- Drift: @rotkha.delirium is tracked but no longer followed.
- Everything else matches: every October unfollow IG recorded is in the tracker (the two not tracked, @aenima87 and @science.cult, were legacy follows).

## 5. Scene Intelligence contacts (490 with an IG handle)

| | |
|---|---|
| Follow Amir | 79 |
| Mutual | 78 |
| Follow Amir, not followed back | 1 (@berlinesk) |
| Amir follows, they don't | 145 |

The Scene likes lane warms T1/T2 relationships. 79 of those contacts already follow him; 145 don't. SI has no field for this today.

## 6. Queue

12 pending candidates already follow Amir: feller008, transgression_music, daribone, reelmastering, iswhatsheis, lobotomy_____berlin, heinrichdressel, nastiaydj, sabs.krebaer, mike_inzinger, shialabiff, hugot_habitacion615_radio. Following them is a certain mutual, not a bet. (transgression_music is also on the protected list pending keep_following.)

## 7. Followers nobody in the system knows (331)

376 people follow Amir without a follow back; 331 are in neither SI nor the queue. Recent ones: rob.morris.9461 (10-09), romironofficial (10-07), jonlivert (09-27), kul_feryadi, andre_heil991, herrektor. These already chose him. They are the cheapest scene-relevance candidates there are, but nobody has vetted them.

## 8. Hashtags followed (13)

engravingtattoo, berlinmusic, abletontips, idm, shoegazemusic, mufc, analogfour, bassline, acidmusic, digitakt, tb303, ballacid, joeyanderson. Two are off-topic for how Instagram categorises the account (mufc, engravingtattoo). Small signal, zero cost to fix.

## Proposed writes (none applied)

A. Tracker: mark the 26 active reciprocators followed_back + verified 2026-10-10; move @rotkha.delirium to history as drift. Then rebuild the sweep list from verified data only (about 30 names).
B. Tracker history: annotate the 46 churned-while-following entries with `followed_back_at_unfollow: true` so the stat is honest. Data only.
C. Queue: when the follow lane resumes, the 12 already-following candidates go first.
D. SI: add a `follows_me` flag (from this export) to enriched contacts so the Scene lane can prefer the 79; needs the sheet, which writes back into SI.
E. Followers unknown to SI (331): vet in batches through the provider once topped up, or by hand on the phone; the scene-relevant ones become queue entries with the highest certainty we have.
F. Hashtags: unfollow mufc and engravingtattoo. Amir's hand, two taps.
