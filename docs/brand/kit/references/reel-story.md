# Recipe: reel, story, Shorts, TikTok, Spotify Canvas, lyric reel

**Canvas:** 1080x1920, 30 fps. Safe zone: top 270, bottom 672, sides 65 stay free of
anything readable. Type: title 104px, name 60px, small 36px.

**What his numbers say:** reels are the discovery format (55 to 62% non-followers). The
ceiling on every reel so far is the first 2 seconds: about 65% gone by 0:02, skip rate 75%.
The process reel beat the release reel. So:
- Open on the strongest frame and the strongest bar. Never a title, a name or a logo first.
- One build, the first 2 seconds as a variable, 2 or 3 versions batch-rendered and run as
  trial reels; the winner goes out (HyperFrames `--batch` with a variables file).
- The name closes the piece: the sting (`references/sting.md`). No handle unless needed.

**Motion:** nothing is fixed except the title arrivals and the ending. Pace, camera,
transitions and effects come from the reel Amir sends at that time: run it through
`/video-analyze`, build from its playbook, and if he likes the result save it in
`motion-library.md` as M1, M2... Title arrival is one of T1 soft fade, T2 letter by
letter, T3 out of shadow, T4 on the flash; working copies in `videos/look06-title-arrivals/`.
One text effect per video.

**Start** the project already on brand (frame.md, the font and the mood's CSS variables
copied in): `python3 .claude/skills/brand/scripts/start_video_project.py <name> --mood M3`.

**Build** with `/hyperframes` (it routes: a beat-synced piece is `/music-to-video`, a short
type piece is `/motion-graphics`, anything custom is `/general-video`). Copy
`docs/brand/frame.md` and `fonts/Marcellus-Regular.ttf` into the project; get CSS variables
from `frame_tokens.py --css <mood>`. Known traps: video clips need
`position:absolute; top:0; left:0`, never tween opacity on a `.clip`, `<audio>` needs an id,
pre-cut footage with `/video-editing` first, never join clips with stream copy.

**Check:** `adherence.py` on the composition; snapshots at the opening, the signature
move and the end; look at every snapshot for text on his face or head DURING the move, not
only at rest; `shrink_check.py frame.png --format reel --text-px 36`.

**Export:** `npx hyperframes render . -q delivery`, then
`video_resizer.py --from-hyperframes <project>`. The 1080x1920 master passes through
untouched as reel, story (60 s cap), Shorts and TikTok.
- **Spotify Canvas:** vertical only, 3 to 8 seconds, no audio, a seamless loop (end state =
  first frame). `--only spotify`.
- **Lyric reel:** the lyric look is not decided yet; it gets decided on the first one, by
  eye, from the T1 to T4 family applied line by line.
- Audio on Instagram gets renamed "Inch of Shadow - Track" at publish.
