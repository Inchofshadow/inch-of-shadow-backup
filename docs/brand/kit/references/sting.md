# Recipe: the sting (the ending of a video)

**Decided (Look-06):** B, on the flash. Warm black, one camera flash, "Inch of Shadow" is
simply there, rests, fades to black. 3 seconds, type only until Amir's hand-drawn ring
mark exists. NO handle by default; it appears only when a piece really needs it.

**Use the asset, do not rebuild it:** `videos/ios-sting/` (its CLAUDE.md has the commands).

```bash
cd videos/ios-sting && export PATH="$HOME/.local/bin:$PATH"
PRODUCER_BROWSER_GPU_MODE=hardware npx hyperframes render . -q delivery                    # platinum on warm black
... render . -q delivery --strict-variables --variables '{"ground":"#110D19","ink":"#C9C2D6"}' -o renders/sting_M3.mp4   # a release mood
... render . -q delivery --strict-variables --variables '{"handle":"@inch_of_shadow"}' -o renders/sting_handle.mp4
```

Variables only work because the sting lives in the top-level `index.html`.

**For short videos, maybe:** out of shadow on black (A) or over the picture itself instead
of cutting to black (D); both in `videos/look06-sting/`. In that effect nothing is on
screen until the light sweeps: the letters exist only where the light has passed, and the
shadow takes them away. Amir corrected an earlier version where dark text sat there first.

**Rules:** the name closes, it never opens (nothing brand-related in the first 3 seconds).
The old lowercase "inch of shadow" outro and the always-on handle from
`videos/IOS-VIDEO-MENU.md` are retired.
