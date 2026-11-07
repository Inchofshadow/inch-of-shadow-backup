# 🎬 Socials: YouTube (side chat)

Written 2026-11-05 by the YouTube side chat (under the 🎬 Socials parent). First handover for this lane.

## Where things stand

- **Channel:** @InchofShadow (`UC44w8onw7I0uTWD4ykPwdLQ`), 11 official audio videos (published 2026-08-17 to 09-04). Topic channel carries Farewell and The Deceiver.
- **Numbers (last snapshot 2026-10-13):** 507 views (299 at the 09-14 baseline, +70% in 29 days), 0 subscribers gained from the catalog, 5 subs total. Top sources: related videos, subscribers, playlists, search. Next planned snapshot ~2026-11-13: `python3 tools/yt_snapshot.py --since stats/2026-10-13.json` (3 API reads; needs a valid login).
- **API login: EXPIRED.** The OAuth app is in Testing mode, so the login lasts 7 days. Last renewal 2026-10-21 (token file written 18:20), so it ran out around 2026-10-28. Any API work (yt_apply, yt_thumbnails, yt_snapshot) needs Amir to run the renewal first: `python3 tools/yt_auth.py` in `/Users/amir/Desktop/Inch of Shadow/youtube/`, then click Allow in the browser (on 10-21 the first click did not save, the second did). Publishing the app is not possible without a website of Amir's own.
- **Pinocchio is paused** (Amir, 2026-11-02, no new date). The YouTube checklist in `releases/pinocchio-single.json` is untouched (no render, no metadata file, no upload). The planned 11-06 Premiere, and with it the open "does a Premiere accept a 4K file" question (PLAYBOOK §6 and §11), wait for the new date.
- **Last change on the channel:** 2026-10-21, Bandcamp campaign links (`?campaign=yt-desc`) on videos 06-11 (🎬 Socials 11 · YouTube descriptions Bandcamp link, done).

## Open decisions (Amir's call)

1. **When to renew the login.** Only needed right before API work; nothing is scheduled that needs it today. The next natural moment is the ~11-13 stats snapshot or Pinocchio's new date.
2. **Pinocchio's new date.** Decides when the YouTube release steps (render, metadata, Premiere, Shorts, end screen) start.

## Key files (all outside the repo unless noted)

- `/Users/amir/Desktop/Inch of Shadow/youtube/PLAYBOOK.md`: single source of truth (algorithm, runbook §5, formats §6, gotchas §10, open questions §11).
- `/Users/amir/Desktop/Inch of Shadow/youtube/PLAN.md`: original catalog plan.
- `youtube/tools/`: `yt_auth.py` (login renewal), `yt_apply.py` (metadata, playlists, publishAt; `PREMIERE: yes` mode), `yt_release.py <slug>` (prints the release steps, `--draft` writes a metadata file), `yt_thumbnails.py`, `yt_snapshot.py`, `render.py`, `gen_metadata.py`. Token: `youtube/tools/yt_token.json` (never print it).
- `youtube/metadata/NN-slug.txt` (one per video, 01-11), `youtube/backups/`, `youtube/stats/2026-09-14.json` + `2026-10-13.json`, `youtube/thumbnails/`.
- Repo: `releases/pinocchio-single.json` (YouTube checklist items `yt_*`), `plans/weekly-stats.md` (Monday summary, includes YouTube numbers).

## Linked tickets

| Ticket | Old id | Status |
|---|---|---|
| 🎬 Socials 2 · YouTube API login renewal | M-01 | waiting (login expired ~10-28; Amir clicks Allow) |
| 🎬 Socials 3 · YouTube stats snapshot vs 09-14 baseline | M-02 | done (10-13 run; next check ~11-13 noted in the ticket) |
| 🎬 Socials 11 · YouTube descriptions Bandcamp link | BC-03 | done (Bandcamp lane, touched YouTube) |

## Ticket updates (for ⚙️ System to merge into tickets.json)

- **M-01 (🎬 Socials 2):** `blocked_on` still says "next ~2026-10-20", which is stale. Suggested: `blocked_on` = "Login expired ~2026-10-28 (last renewal 10-21). Amir runs yt_auth.py and clicks Allow before the next API work." Add note: "2026-11-05: checked token file, expiry passed; not renewed, nothing scheduled needs it yet."
