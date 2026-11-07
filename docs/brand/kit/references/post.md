# Recipe: feed post, carousel, pre-save image

**Canvas:** 1080x1440 (3:4) fills the profile grid tile since Instagram's grid change;
1080x1350 (4:5) is the size Look-01 approved type on: title 96px, name 56px, small 34px.
3:4 has no approved type sizes yet (frame.md, Known Gaps): use the 4:5 sizes and confirm
with the shrink check, and say that you did.

**What posts are for (his own numbers):** a carousel is follower depth, not discovery
(98% followers, but 21 comments on 162 reach). His portrait out-liked the statues, so the
face goes in, slide 3 worked on The Deceiver. A photo carousel cannot carry original audio
on Instagram; if the audio matters, make it a reel.

**Steps**
1. Photo: search `plans/control-panel/shoot-catalogue.json` by framing, light, feeling,
   sunglasses on or off (on is his natural state; off is the rare, deliberate, vulnerable
   move). Copy a working file, never touch the drive.
2. Text only on a calm area (sky, wall, shadow, floor), never on the face, head, gear or
   detail. No calm area: a soft dark band behind light text. Dark ink only on plain light.
3. Default mood M2 (platinum on warm black) for non-release content; the release's mood
   for release content.
4. `shrink_check.py post.png --format post --text-px 34`, then
   `artwork_resizer.py` for the Instagram sizes (1:1, 4:5, 3:4, story, reel cover 420x654).
5. Before he shares: location, tag or collab users. Caption rules live in `voice.md` (v2):
   warm, first person, any length, his usual emojis lightly, 3 to 5 tags at the end, usually
   nothing about the song's meaning.
