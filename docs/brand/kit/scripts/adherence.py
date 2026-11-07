#!/usr/bin/env python3
"""Does a composition (HTML/CSS) use only approved colours and fonts?

    adherence.py compositions/index.html [--mood M3] [--allow "#D4B955" ...] [--font "Release Font"]

Every hex colour must be in docs/brand/frame.md (its colours and mood library) or be
allowed by hand: accents sampled from the release artwork, or a release's own title face.
Fonts must be the brand face or its fallback (frame.md, block `face`) unless a release font is named. Exit code 1 when something is off.
This catches retyped or invented values; it cannot judge taste. Look at the render too.
"""
import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame_tokens import load  # noqa: E402

GENERIC = {"serif", "sans-serif", "monospace", "inherit", "initial", "unset", "system-ui", "ui-serif"}


def norm(h: str) -> str:
    h = h.upper()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h[:7]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--mood", help="the release's mood, to confirm ground and ink are that pair")
    ap.add_argument("--allow", nargs="*", default=[], help="extra hex colours (accents sampled from the artwork)")
    ap.add_argument("--font", nargs="*", default=[], help="a release's own title face")
    a = ap.parse_args()

    tokens = load()
    approved = {norm(v) for v in tokens["colors"].values() if isinstance(v, str) and v.startswith("#")}
    for m in tokens["moods"].values():
        approved |= {norm(m["light"]), norm(m["dark"])}
    approved |= {norm(x) for x in a.allow}
    approved |= {"#000000", "#FFFFFF"}  # masks, shadows and flash mixing
    face = tokens.get("face") or {}
    fonts_ok = {"marcellus", str(face.get("family", "")).lower(),
                str((face.get("fallback") or {}).get("family", "")).lower()} - {""}
    fonts_ok |= {f.lower() for f in a.font}

    problems = 0
    for f in a.files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        used = {norm(h) for h in re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", text)}
        bad = sorted(used - approved)
        fams = set()
        for decl in re.findall(r"font-family\s*:\s*([^;}{]+)", text):
            for fam in decl.split(","):
                fam = fam.strip().strip("\"'").lower()
                if fam and fam not in GENERIC and not fam.startswith("var("):
                    fams.add(fam)
        bad_fonts = sorted(fams - fonts_ok)
        print(f"{f}: {len(used)} colours, fonts: {', '.join(sorted(fams)) or 'none declared'}")
        for h in bad:
            print(f"  colour not in frame.md: {h}  (approved mood colour? sampled accent? pass it with --allow, else remove it)")
        for fam in bad_fonts:
            print(f"  font not approved: {fam}  (the brand face and its fallback come from frame.md; a release font is passed with --font)")
        if a.mood:
            m = tokens["moods"].get(a.mood)
            if not m:
                sys.exit(f"Unknown mood {a.mood}")
            for role in ("light", "dark"):
                if norm(m[role]) not in used:
                    print(f"  mood {a.mood} {role} colour {m[role]} is not used in this file")
                    problems += 1
        problems += len(bad) + len(bad_fonts)

    print("adherence: clean" if not problems else f"adherence: {problems} thing(s) to fix")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
