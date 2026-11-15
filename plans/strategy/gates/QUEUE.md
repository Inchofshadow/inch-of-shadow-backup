# Gates waiting for the other model

Empty since 2026-11-15: Fable read all seven queued items on Amir's "gate".

| Item | Verdict | File |
|---|---|---|
| Instagram sweep runs 11-17 to 11-29 | approve with fixes (2 before the first run) | 2026-11-15-ig-sweep.md |
| Half the Night SEO pass | approve, 2 text fixes | 2026-11-15-htn-seo-pass.md |
| Backup snapshot hardening | approve, 1 should-fix | 2026-11-15-backup-hardening.md |
| Python switch (System 69) | approve | 2026-11-15-python-switch.md |
| Code review fixes of 11-08 | approve with 1 must-fix | 2026-11-15-gate-fixes.md |
| Studio drawer + tag list (System 94) | approve, 3 small fixes | 2026-11-15-studio-drawer.md |
| Memory index trim | approve with fixes, applied | 2026-11-15-memory-index.md |
| Round 2: RM work of 11-08 to 11-13 (keeps, palette, Layout, graphs, small ones) | approve, 6 small fixes | 2026-11-15-round-2-rm-work.md |

New items go below this line (date, what, why the other model).
| 2026-11-15 | Fable's own fixes of 11-15: storage.py backup filter (2148cbc), backup final secret check (331339a), drawer untagged chip (ca0bc79), stats/evening_reports.py + LaunchAgent + the two task prompts (d85b528), memory index repair | Fable wrote them; Opus reads (the other model) |
| 2026-11-15 | Fable's round 2 fixes: keeps file safe write (66d9175), RM contrast + 13 px (23b9bc9), overdue date tag + waits-on notes (2d45b82) | Fable wrote them; Opus reads |

## Waiting for Fable: lists from the parent chats (2026-11-15, Amir: "send all other parent chats that Fable returned")

| # | Area | What | File or commit | Why |
|---|---|---|---|---|
| 1 | 🎬 Socials | IG follow-back check now combines recent follower lists | aa09659 | unblocks engine unfollows; a wrong merge unfollows people who follow back |
| 2 | 🎬 Socials | IG follows per session 16 -> 10 during the sweep; the "back to 16 on Dec 5" rule is text only | f6def47, scene_intelligence/ig_engagement_config.py | live engine cap |
| 3 | 🎵 Release | Release-day playbook Dec 11 | plans/htn-release-day-playbook-2026-12-11.md | the live-day runsheet |
| 4 | 🎧 Booking | 26 unsent label drafts (batch 2 to 5) | plans/htn-label-drafts-batch*-2026-11-11.md | go out next; contact facts, routes, greeting names, own-network rules |
| 5 | 🎧 Booking | Post-release DJ wave (38 drafts, Dec 14 to 19) + show hosts | plans/handovers/booking/htn-dj-promo.md | handles still unverified, Dec 11 dates, links |
| 6 | 🎧 Booking | DJ outreach week 1 + 2 cards (10 drafts) | plans/outreach-batches.json, plans/handovers/booking/dj-outreach.md | facts and open flags |
| 7 | 🎵 Release | Description map + drafts D1 to D4 | plans/htn-description-map-2026-11-12.md | store-display claims; D3 pitch goes out about Dec 2 |
| 8 | 🎵 Release | EP plan date logic | plans/half-the-night-ep-plan.md | body still says Dec 4 |
| 9 | 🎬 Socials | IG ratio plan (option B) | plans/ig-ratio-plan-2026-11-12.md | drives follows and unfollows to Dec 31 |
| 10 | 🎬 Socials | HTN content plan + listening party plan | plans/half-the-night-content-plan.md, plans/bc-htn-listening-party-2026-12-11.md | his steps on the day |
| 11 | 💶 Income | Income brief v4 "learn then build" | memory income-brief-learn-then-build, plans/handovers/income/income-500.md | changes how every idea is scored |
| 12 | 💶 Income | App factory plan v1 (on hold, costs $99/year if started) | plans/app-factory/PLAN.md | second view before Amir decides |
| 13 | 💶 Income | Radar cap and spend rules | gap_radar/schedule.json, gate() in gap_radar/schedule.py | Amir decides any cap raise |
| 14 | 🎵 Release | Symphonic submit checklist + rule memories of 11-11 to 11-13 | memory symphonic-submit-lessons-htn, no-key-bpm-in-copy, side-chat-lessons-before-delete, check-memory-before-stating-facts, dated-items-show-date, side-chat-names-show-kind | rules every chat follows |
| 15 | 💶 Income | Reddit back-off | 13c5e19 | small code change |
| 16 | 🎬 Socials | Pool refill task, SC blocked-list entry, sc-engagement end step | ig-pool-refill-sun-1115, c9ce914 | small, optional |
| 17 | 🎵 Release | Vinyl frame mark memory | memory vinyl-frame-marks-dance-releases | before 2027-01-05 |
| 18 | 🎸 Studio | Client service agreement (after Amir's 4 numbers and address) | plans/studio-service/service-agreement.md | a contract clients sign; not ready for the gate yet |

**Read 2026-11-15 (Fable):** items 1 to 3 in `2026-11-15-parent-lists-part-1.md`; items 4 to 13 and 15 in `2026-11-15-parent-lists-part-2.md` (item 6 and the small ones only lightly, as that file says).
**Still to read:** item 14 (Symphonic checklist + the five rule memories, in full), 16 (small Socials items), 17 (vinyl memory, before 2027-01-05), 18 (Studio service agreement, when it is ready).
