#!/usr/bin/env python3
"""Read the exact brand values out of docs/brand/frame.md so nobody retypes them.

    frame_tokens.py                 everything in the YAML block, as JSON
    frame_tokens.py --css           CSS variables for the default mood (M2)
    frame_tokens.py --css M3        CSS variables for another mood
    frame_tokens.py --moods         the mood library, one line each

frame.md is the single source of truth. This script never writes to it.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml


def find_frame() -> Path:
    here = Path(__file__).resolve()
    for root in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        for rel in ("Inchofshadowcode/docs/brand/frame.md", "docs/brand/frame.md"):
            p = root / rel
            if p.is_file():
                return p
    sys.exit("frame.md not found. Run from inside the Inch of Shadow project.")


def load(path: Path = None) -> dict:
    path = path or find_frame()
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        sys.exit(f"{path} has no YAML block at the top")
    return yaml.safe_load(text.split("---", 2)[1])


def face_files(tokens: dict = None, frame: Path = None) -> list:
    """[(family, path), ...]: the brand face first, then its fallback. A face whose file is
    missing (trial files are not under version control) is skipped, so the fallback leads."""
    frame = frame or find_frame()
    tokens = tokens or load(frame)
    face = tokens.get("face") or {"family": "Marcellus", "file": "fonts/Marcellus-Regular.ttf"}
    out = []
    for f in (face, face.get("fallback") or {}):
        if f.get("file") and (frame.parent / f["file"]).is_file():
            out.append((f["family"], frame.parent / f["file"]))
    if not out:
        sys.exit("No brand font file found. Check the face block in frame.md.")
    return out


def css(tokens: dict, mood: str) -> str:
    moods = tokens["moods"]
    if mood not in moods:
        sys.exit(f"Unknown mood '{mood}'. Moods: {', '.join(moods)}")
    m = moods[mood]
    t = tokens["typography"]
    faces = face_files(tokens)
    lines = [
        f"/* Inch of Shadow, mood {mood}: {m['name']} ({m['use']}) */",
        ":root {",
        f"  --ground: {m['dark']};",
        f"  --ink: {m['light']};",
        f"  --flash: color-mix(in srgb, {m['light']} 27%, white);",
        f"  --text-shadow: 0 2px 24px {tokens['colors']['text-shadow']};",
        "  --font: " + ", ".join(f'"{fam}"' for fam, _ in faces) + ", serif;",
    ]
    for key in ("title", "name", "small", "sting-name", "handle"):
        lines.append(f"  --{key}-size: {t[key]['px']}px;  --{key}-tracking: {t[key]['tracking']};")
    s = tokens["spacing"]
    lines += [
        f"  --safe-top: {s['safe-top']};  --safe-bottom: {s['safe-bottom']};  --safe-sides: {s['safe-sides']};",
        "}",
    ]
    for fam, path in faces:
        fmt = "opentype" if path.suffix.lower() == ".otf" else "truetype"
        lines.append(f'@font-face {{ font-family: "{fam}"; font-weight: 400; '
                     f'src: url("assets/fonts/{path.name}") format("{fmt}"); }}')
    status = (tokens.get("face") or {}).get("status")
    if status:
        lines.insert(1, f"/* FACE: {status} */")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--css", nargs="?", const="M2", metavar="MOOD")
    ap.add_argument("--moods", action="store_true")
    args = ap.parse_args()
    tokens = load()
    if args.moods:
        for k, m in tokens["moods"].items():
            print(f"{k:<3} {m['light']} on {m['dark']}  {m['name']}: {m['use']}")
    elif args.css:
        print(css(tokens, args.css))
    else:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
