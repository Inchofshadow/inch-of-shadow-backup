#!/usr/bin/env python3
"""copy_clean.py - clean a draft before it is pasted anywhere.

What it fixes, in this order:
  1. Invisible characters that AI drafts and copy-paste leave behind: zero-width
     spaces and joiners, word joiners, soft hyphens, byte-order marks, direction
     marks, invisible separators, Unicode tag characters. A keyboard never
     types these; they are the clearest machine fingerprint there is.
     Zero-width joiners inside emoji sequences are kept (a black cat emoji is
     a cat, a joiner and a black square).
  2. Odd spaces (no-break, narrow, thin, hair, en, em, ideographic) -> a plain
     space.
  3. Typography: em dash, en dash between words, horizontal bar and double
     hyphen -> a comma (the house rule: commas and full stops, never dashes);
     curly quotes -> straight; the ellipsis character -> three dots.
     Number ranges keep a plain hyphen (7-9, 2026-10-15).

What it never touches: emojis, the middle dot, URLs, @handles, #hashtags,
line breaks, the words themselves.

Usage
  python3 copy_clean.py draft.txt                 # cleaned text to stdout
  python3 copy_clean.py draft.txt -o clean.txt    # write to a file
  python3 copy_clean.py draft.txt --report        # cleaned text + what changed
  pbpaste | python3 copy_clean.py - | pbcopy      # clean the clipboard in place
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from typing import List, Tuple

ZWJ = "‍"
VARIATION_SELECTORS = ("︎", "️")

# Spaces that look like a space and are not one.
ODD_SPACES = {
    " ": "no-break space", " ": "narrow no-break space",
    " ": "thin space", " ": "hair space", " ": "en space",
    " ": "em space", " ": "three-per-em space", " ": "four-per-em space",
    " ": "six-per-em space", " ": "figure space", " ": "punctuation space",
    "　": "ideographic space", " ": "medium mathematical space",
}

QUOTES = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "′": "'", "″": '"',
}

DASHES = "—―–‒"          # em dash, horizontal bar, en dash, figure dash
# A dash used as a joiner between words, with or without spaces, or "--".
DASH_RE = re.compile(r"[ \t]*(?:[—―‒]|--+|–)[ \t]*")
# An en dash or hyphen between two digits is a range, keep it as a hyphen.
RANGE_RE = re.compile(r"(?<=\d)\s?[–‒]\s?(?=\d)")
ELLIPSIS_RE = re.compile(r"…")


def _is_emoji_like(ch: str) -> bool:
    if not ch:
        return False
    if ch in VARIATION_SELECTORS:
        return True
    cat = unicodedata.category(ch)
    return cat in ("So", "Sk") or 0x1F000 <= ord(ch) <= 0x1FAFF or 0x2600 <= ord(ch) <= 0x27BF


def strip_invisible(text: str) -> Tuple[str, List[str]]:
    """Remove every Unicode format character (category Cf) except joiners that
    sit inside an emoji sequence. Returns (text, list of removed names)."""
    out = []
    removed: List[str] = []
    n = len(text)
    for i, ch in enumerate(text):
        if unicodedata.category(ch) == "Cf":
            if ch == ZWJ:
                prev = out[-1] if out else ""
                nxt = text[i + 1] if i + 1 < n else ""
                if _is_emoji_like(prev) and _is_emoji_like(nxt):
                    out.append(ch)
                    continue
            removed.append(unicodedata.name(ch, "U+%04X" % ord(ch)).lower())
            continue
        out.append(ch)
    return "".join(out), removed


def normalise_spaces(text: str) -> Tuple[str, List[str]]:
    removed: List[str] = []
    for ch, name in ODD_SPACES.items():
        if ch in text:
            removed.extend([name] * text.count(ch))
            text = text.replace(ch, " ")
    return text, removed


def _dash_to_comma(line: str) -> Tuple[str, int]:
    """Replace joiner dashes in one line with a comma, tidying what that leaves."""
    count = 0
    line = RANGE_RE.sub("-", line)           # 7–9 -> 7-9, before the general pass
    # A dash that opens a line is a list marker: keep it as a hyphen.
    lead = re.match(r"^(\s*)(?:[—―–‒]|--+)\s*", line)
    if lead:
        line = lead.group(1) + "- " + line[lead.end():]

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        start, end = m.start(), m.end()
        before = line[:start].rstrip()
        after = line[end:].lstrip()
        if not before:
            return ""
        if not after:                          # dash at the end of the line
            return ""
        if before[-1] in ",.;:!?":            # already punctuated, just drop it
            return " "
        if after[0] in ",.;:!?":
            return ""
        return ", "

    line = DASH_RE.sub(repl, line)
    line = re.sub(r" {2,}", " ", line)
    line = re.sub(r"\s+([,.;:!?])", r"\1", line)
    return line.rstrip(), count


def normalise_typography(text: str) -> Tuple[str, dict]:
    changes = {"dashes": 0, "quotes": 0, "ellipsis": 0}
    for ch, rep in QUOTES.items():
        if ch in text:
            changes["quotes"] += text.count(ch)
            text = text.replace(ch, rep)
    if "…" in text:
        changes["ellipsis"] = text.count("…")
        text = ELLIPSIS_RE.sub("...", text)
    lines = []
    for line in text.split("\n"):
        if any(d in line for d in DASHES) or "--" in line:
            line, n = _dash_to_comma(line)
            changes["dashes"] += n
        lines.append(line)
    return "\n".join(lines), changes


def clean(text: str) -> Tuple[str, dict]:
    """Run every pass. Returns (clean text, report dict)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text, invisible = strip_invisible(text)
    text, spaces = normalise_spaces(text)
    text, typo = normalise_typography(text)
    report = {"invisible": invisible, "odd_spaces": spaces, **typo}
    report["total"] = len(invisible) + len(spaces) + sum(typo.values())
    return text, report


def format_report(report: dict) -> str:
    lines = ["CLEANED  %d change%s" % (report["total"], "" if report["total"] == 1 else "s")]
    if report["invisible"]:
        counts = {}
        for name in report["invisible"]:
            counts[name] = counts.get(name, 0) + 1
        for name, n in sorted(counts.items()):
            lines.append("  removed  %-32s x%d" % (name, n))
    if report["odd_spaces"]:
        lines.append("  spaces   %d odd space%s -> plain space" % (len(report["odd_spaces"]), "" if len(report["odd_spaces"]) == 1 else "s"))
    if report["dashes"]:
        lines.append("  dashes   %d -> comma" % report["dashes"])
    if report["quotes"]:
        lines.append("  quotes   %d curly -> straight" % report["quotes"])
    if report["ellipsis"]:
        lines.append("  ellipsis %d -> ..." % report["ellipsis"])
    if report["total"] == 0:
        lines.append("  nothing to fix")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Clean a draft: invisible characters, odd spaces, dashes, curly quotes.")
    ap.add_argument("path", help="text file, or - for stdin")
    ap.add_argument("-o", "--out", help="write the cleaned text here instead of stdout")
    ap.add_argument("--report", action="store_true", help="print what changed (to stderr when writing to stdout)")
    args = ap.parse_args(argv)

    raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    text, report = clean(raw)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        if args.report:
            print(format_report(report))
    else:
        sys.stdout.write(text)
        if args.report:
            sys.stderr.write("\n" + format_report(report) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
