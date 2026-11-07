#!/usr/bin/env python3
"""Start a HyperFrames video project that is on brand from the first frame.

    start_video_project.py <name> [--mood M3] [--skill motion-graphics]

Creates videos/<name>/ with `npx hyperframes init`, then copies in the brand spec
(frame.md, which HyperFrames reads as its design spec), the Marcellus font file, and a
brand.css with the mood's colours, the type sizes and the safe zone as CSS variables, all
read from docs/brand/frame.md. Nothing is typed from memory. Refuses to touch an existing
project folder.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame_tokens import css, face_files, find_frame, load  # noqa: E402


CANVAS = {"reel": (1080, 1920), "wide": (1920, 1080), "square": (1080, 1080)}

# The scaffold from `hyperframes init` is a 1920x1080 page in Inter. Found in the rehearsal
# (Machine-09): every project then started with the wrong canvas and an off-brand font, and
# brand.css had to be pasted in by hand. So the starter writes the first index.html itself.
INDEX = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
{css}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; overflow: hidden; background: var(--ground); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--ground); }}
      .full {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="10" data-width="{w}" data-height="{h}">
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="kebab-case project name, e.g. song-title-release-reel")
    ap.add_argument("--mood", default="M2")
    ap.add_argument("--canvas", default="reel", choices=sorted(CANVAS),
                    help="reel 1080x1920 (default: reels, Shorts, TikTok, Canvas, stories), "
                         "wide 1920x1080 (YouTube), square 1080x1080")
    ap.add_argument("--skill", default="general-video",
                    help="the HyperFrames workflow that will build it (motion-graphics, music-to-video, general-video...)")
    a = ap.parse_args()

    frame = find_frame()
    root = frame.parents[3]                     # .../Inch of Shadow
    project = root / "videos" / a.name
    if project.exists():
        sys.exit(f"{project} already exists. Pick another name; this script never overwrites.")

    tokens = load(frame)
    brand_css = css(tokens, a.mood)             # exits on an unknown mood, before anything is created

    project.parent.mkdir(exist_ok=True)
    r = subprocess.run(["npx", "--yes", "hyperframes", "init", str(project), "--non-interactive",
                        "--example=blank", f"--skill={a.skill}"], capture_output=True, text=True)
    if r.returncode != 0 or not (project / "hyperframes.json").is_file():
        sys.exit(f"hyperframes init failed:\n{r.stdout[-400:]}\n{r.stderr[-400:]}")

    shutil.copy2(frame, project / "frame.md")
    fonts = project / "assets" / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for _fam, fpath in face_files(tokens, frame):
        shutil.copy2(fpath, fonts / fpath.name)
    (project / "brand.css").write_text(brand_css + "\n", encoding="utf-8")
    w, h = CANVAS[a.canvas]
    inlined = "\n".join("      " + line for line in brand_css.splitlines())
    (project / "index.html").write_text(INDEX.format(w=w, h=h, css=inlined), encoding="utf-8")

    print(f"ready: {project}")
    print(f"  frame.md (brand spec), assets/fonts/ (the brand face and its fallback), brand.css (mood {a.mood})")
    status = (tokens.get("face") or {}).get("status")
    if status:
        print(f"  FACE: {status}")
    print(f"  index.html: {w}x{h}, brand.css already inside its <style> (keep brand.css as the reference copy)")
    print("  next: build with /hyperframes;")
    print("        check with adherence.py and shrink_check.py; export with -q delivery.")


if __name__ == "__main__":
    main()
