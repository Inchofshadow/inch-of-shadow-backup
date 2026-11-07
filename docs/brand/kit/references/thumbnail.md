# Recipe: YouTube thumbnail and visualizer

> **PARKED 2026-09-21 (Amir, Formats-03): the live thumbnail is the plain cover on every
> video, songs included.** The designed, title-only thumbnail below is only for YouTube's
> Test & Compare, and only with his OK. Before any thumbnail change say in plain words: this
> replaces the picture people see on the channel page and in search. `youtube/PLAYBOOK.md`
> section 6.

**Thumbnail canvas:** 3840x2160 (YouTube's recommended size since 2026; up to 50 MB from a
computer, 2 MB from a phone, so a 1280x720 copy is kept for phone uploads). Shorts:
2160x3840. Title only: NO artist name, YouTube prints the channel name. The approved
150px title on 1280x720 is 450px on 3840x2160, tracking 0.03em, the brand face (Albertus Nova) or the release's
title face.

**It has to survive 120px wide** (mobile search). A busy photo stays weak there: use a
calm photo or a tight crop, the title on the calm area, never on the face.

**Layout:** no thumbnail safe zone was ever measured (frame.md, Known Gaps). What is
certain: YouTube prints the duration in the bottom-right corner, so nothing readable goes
there. Title colour: the mood's light colour by default; the release artwork's accent is
the alternative when the thumbnail should match the released cover. Which of the two is
not decided as a rule, so say which you used. A title wider than about three quarters of
the canvas, or a two-line title, has no approved treatment yet: show it, do not assume.

**Steps**
1. Photo or artwork? His face beats art in his own numbers, so a photo of him when one fits
   the track and has a calm band wide enough for the title (`contact_sheet.py`, then look);
   the release artwork when no photo fits or the video is an art track.
2. Compose at 3840x2160 (Pillow or HTML), mood colours from `frame_tokens.py`.
3. `shrink_check.py thumb.png --format thumb --text-px 450`, and LOOK at the 120px tile.
4. `artwork_resizer.py thumb.png --only youtube` writes 3840x2160, 1280x720 and the
   Shorts size.
5. Upload goes through the YouTube agent flow: read `youtube/PLAYBOOK.md` first, releases
   are applied with `youtube/tools/yt_apply.py`. Uploading is Amir's click.

**Visualizer (full lane, songs):** the whole song, 16:9, composed at 1920x1080 and
rendered 4K: `npx hyperframes render . -q delivery --resolution landscape-4k`.
`video_resizer.py --only youtube` then writes 1080p, 1440p and 4K from that master and
never upscales. YouTube's recommended bitrates are 8 Mbps for 1080p, 16 for 1440p, 35 to 45
for 2160p. One outside test found 1440p and 4K uploads get a better codec at every playback
size; YouTube does not state that, so say "likely", not "certain". An @handle in a YouTube
description links to a YouTube channel, not to Instagram. Audio for video: about -15 LUFS,
peaks under -1 dBFS, and check the encoded file, AAC can overshoot.
