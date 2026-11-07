#!/usr/bin/env python3
"""caption_check.py - show an Instagram caption the way the feed shows it, then
check it against the house rules before it is pasted.

The feed shows roughly the first 125 characters, then "... more". The box at
the top prints exactly that window so you read the caption the way a scrolling
stranger reads it. The cut is approximate (device and font move it), which is
why a margin beats a caption engineered to end at 125.

The checks come from docs/brand/voice.md and docs/ig-agent-context.md:
  length          2,200 max
  first line      the first sentence should finish before the cut
  opener          no greeting, no hashtag, no @handle, no emoji as the first thing
                  ("Hi all" is message language, not caption language)
  dashes          no em dashes, no double hyphens (commas and full stops)
  asks            no asking for feedback, opinions, follows, tags or double taps
  hooks           no clickbait openers ("Wait for this part", "POV:", listicles)
  filler          no "go stream" marketing filler
  hashtags        3 to 5, at the end, none of the generic ones (#music #dj #techno)
  emojis          his set, lightly: no wall, never as bullet points
  link            no URL in the caption (not clickable, link in bio)
  name            never IOS / IoS; the handle is @inch_of_shadow with underscores
  credit          the photo credit is exactly  (camera emoji)@shirzilber.art
  keywords        with --keywords: each term present, and in the first 125 chars

Usage
  python3 caption_check.py caption.txt
  python3 caption_check.py caption.txt --keywords "berlin,dark disco"
  pbpaste | python3 caption_check.py -
  python3 caption_check.py caption.txt --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import unicodedata
from typing import List

LIMIT = 2200
CUT = 125
HASHTAG_MAX = 5
HASHTAG_MIN = 3
BOX_WIDTH = 54

HASHTAG_RE = re.compile(r"(?:(?<=\s)|^)(#[\wÀ-ɏ]+)")
MENTION_RE = re.compile(r"(?:(?<=\s)|^)(@[\w.]+)")
URL_RE = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|net|org|io|co|de|link|fm|to)/\S*", re.I)
SENTENCE_END_RE = re.compile(r"[.!?]\s|[.!?]$|\n")

GENERIC_TAGS = {"#music", "#dj", "#techno", "#love", "#instagood", "#viral", "#fyp",
                "#explorepage", "#foryou", "#follow", "#like4like", "#follow4follow"}

ASK_PATTERNS = [
    r"\bwhat do you think\b", r"\blet me know\b", r"\btell me\b.{0,30}\bcomments?\b",
    r"\bin the comments\b", r"\bcomment below\b", r"\bdrop a comment\b", r"\bthoughts\?",
    r"\byour (?:opinion|feedback|thoughts)\b", r"\bfeedback\b", r"\btag (?:a|someone|your)\b",
    r"\bdouble tap\b", r"\bfollow for more\b", r"\bhit (?:the )?follow\b", r"\bshare this\b",
    r"\bsave this\b", r"\bsmash\b", r"\bdo you (?:like|agree)\b", r"\bagree\?",
]
HOOK_PATTERNS = [
    r"\bwait for (?:this|the) part\b", r"^\s*pov\s*:", r"\bstop scrolling\b",
    r"^\s*\d+\s+(?:things|reasons|ways|tips|tracks)\b", r"\byou won'?t believe\b",
    r"\bnobody tells you\b",
]
FILLER_PATTERNS = [
    r"\bgo stream\b", r"\bstream (?:it )?now\b", r"\blink in bio\b.{0,20}\bnow\b",
    r"\brun,? don'?t walk\b", r"\bgame[- ]changer\b", r"\bbanger\b",
]
META_PATTERNS = [
    r"\bnot gonna lie\b", r"\bngl\b", r"\breal talk\b", r"\bhonestly\?", r"\bunpopular opinion\b",
    r"\blong caption\b", r"\bthis caption\b", r"\bi know this is long\b",
]
GREETING_RE = re.compile(r"^\s*(?:hi|hey|hello|yo|hi all|hey all|hello everyone)\b[ ,!]*", re.I)
CAMERA = "\U0001F4F8"
CREDIT_OK = CAMERA + "@shirzilber.art"


def _is_emoji(ch: str) -> bool:
    cp = ord(ch)
    if ch in ("️", "‍"):
        return False
    return (unicodedata.category(ch) in ("So", "Sk") or 0x1F000 <= cp <= 0x1FAFF
            or 0x2600 <= cp <= 0x27BF or cp == 0x2B1B)


def count_emoji(text: str) -> int:
    return sum(1 for ch in text if _is_emoji(ch))


def visible_window(text: str, cut: int = CUT) -> str:
    return text[:cut]


def _box(window: str, cut: int, total: int) -> List[str]:
    lines = ["  WHAT THE FEED SHOWS", "  +" + "-" * BOX_WIDTH + "+"]
    for raw in window.split("\n"):
        wrapped = textwrap.wrap(raw, BOX_WIDTH - 2) or [""]
        for w in wrapped:
            lines.append("  | " + w.ljust(BOX_WIDTH - 2) + " |")
    tail = " ... more " if total > cut else " (whole caption fits) "
    lines.append("  +" + "-" * (BOX_WIDTH - len(tail)) + tail + "+")
    return lines


def check(text: str, keywords: List[str] = None, cut: int = CUT) -> dict:
    text = text.replace("\r\n", "\n").rstrip("\n")
    keywords = [k.strip() for k in (keywords or []) if k.strip()]
    low = text.lower()
    window = visible_window(text, cut)
    window_low = window.lower()
    results = []

    def add(status, name, note):
        results.append({"status": status, "check": name, "note": note})

    # length
    n = len(text)
    add("FAIL" if n > LIMIT else "PASS", "LENGTH", "%d / %d characters" % (n, LIMIT))

    # first sentence vs the cut
    m = SENTENCE_END_RE.search(text)
    first_end = m.start() + 1 if m else n
    if n <= cut:
        add("PASS", "FIRST LINE", "the whole caption is visible before the cut")
    elif first_end <= cut:
        add("PASS", "FIRST LINE", "first sentence ends at %d, inside the %d window" % (first_end, cut))
    else:
        cut_word = text[cut - 1].isalnum() and cut < n and text[cut].isalnum()
        add("WARN", "FIRST LINE", "first sentence runs to %d, the feed cuts it at %d%s"
            % (first_end, cut, " mid-word" if cut_word else ""))

    # opener
    stripped = text.lstrip()
    first = stripped[:1]
    if not stripped:
        add("FAIL", "OPENER", "empty caption")
    elif GREETING_RE.match(stripped):
        add("WARN", "OPENER", "opens with a greeting; greetings belong to messages, not captions")
    elif first == "#":
        add("FAIL", "OPENER", "opens with a hashtag")
    elif first == "@":
        add("WARN", "OPENER", "opens with a handle; Instagram cuts it from the preview")
    elif _is_emoji(first):
        add("WARN", "OPENER", "opens with an emoji; the first words do the work")
    else:
        add("PASS", "OPENER", "starts with words")

    # dashes
    dashes = text.count("—") + text.count("―") + len(re.findall(r"--+", text))
    en_between_words = len(re.findall(r"(?<=\D)\s?–\s?(?=\D)", text))
    if dashes or en_between_words:
        add("FAIL", "DASHES", "%d dash%s; commas and full stops instead (run copy_clean.py)"
            % (dashes + en_between_words, "" if dashes + en_between_words == 1 else "es"))
    else:
        add("PASS", "DASHES", "none")

    # asks
    hits = [p for p in ASK_PATTERNS if re.search(p, low)]
    if hits:
        found = re.search(hits[0], low).group(0)
        add("FAIL", "ASKS", "asks the reader for something (\"%s\"); say it, share it, stop" % found)
    else:
        add("PASS", "ASKS", "no feedback or engagement asks")

    # clickbait hooks, filler, meta
    for name, patterns, msg in (("HOOKS", HOOK_PATTERNS, "clickbait opener"),
                                ("FILLER", FILLER_PATTERNS, "marketing filler"),
                                ("META", META_PATTERNS, "line that comments on itself")):
        hit = next((re.search(p, low, re.M) for p in patterns if re.search(p, low, re.M)), None)
        if hit:
            add("WARN", name, "%s: \"%s\"" % (msg, hit.group(0).strip()))
        else:
            add("PASS", name, "none")

    # hashtags
    tags = HASHTAG_RE.findall(text)
    tag_count = len(tags)
    generic = [t for t in tags if t.lower() in GENERIC_TAGS]
    last_block = text.rstrip().split("\n")[-1] if text.strip() else ""
    tags_in_last = len(HASHTAG_RE.findall(last_block))
    if tag_count > HASHTAG_MAX:
        add("FAIL", "HASHTAGS", "%d tags, Instagram's cap is %d" % (tag_count, HASHTAG_MAX))
    elif tag_count == 0:
        add("WARN", "HASHTAGS", "no hashtags; the rule is %d to %d precise ones at the end" % (HASHTAG_MIN, HASHTAG_MAX))
    elif tag_count < HASHTAG_MIN:
        add("WARN", "HASHTAGS", "%d tag%s; the rule is %d to %d" % (tag_count, "" if tag_count == 1 else "s", HASHTAG_MIN, HASHTAG_MAX))
    elif tags_in_last != tag_count:
        add("WARN", "HASHTAGS", "%d tags but only %d on the last line; put them all at the end" % (tag_count, tags_in_last))
    else:
        add("PASS", "HASHTAGS", "%d at the end: %s" % (tag_count, " ".join(tags)))
    if generic:
        add("WARN", "HASHTAGS", "generic tag%s with no targeting value: %s" % ("" if len(generic) == 1 else "s", " ".join(generic)))

    # emojis
    emoji_n = count_emoji(text)
    bullet_lines = sum(1 for ln in text.split("\n") if ln.strip() and _is_emoji(ln.strip()[0]) and len(ln.strip()) > 2)
    runs = re.findall(r"(?:[\U0001F000-\U0001FAFF☀-➿]️?){4,}", text)
    if runs:
        add("WARN", "EMOJIS", "a wall of %d in a row; his set is used lightly" % max(len(r) for r in runs))
    elif bullet_lines >= 3:
        add("WARN", "EMOJIS", "%d lines open with an emoji; never as bullet points" % bullet_lines)
    elif emoji_n > 8:
        add("WARN", "EMOJIS", "%d emojis; a few is the habit" % emoji_n)
    else:
        add("PASS", "EMOJIS", "%d" % emoji_n)

    # link
    if URL_RE.search(text):
        add("WARN", "LINK", "a URL in the caption is dead text; link in bio")
    else:
        add("PASS", "LINK", "none")

    # name and handle
    if re.search(r"\bIOS\b|\bIoS\b", text):
        add("FAIL", "NAME", "the name is never IOS or IoS; write Inch of Shadow")
    else:
        add("PASS", "NAME", "ok")
    bad_handles = [h.rstrip(".") for h in MENTION_RE.findall(text) if h.rstrip(".").lower() in ("@inchofshadow", "@inch.of.shadow", "@inch-of-shadow")]
    if bad_handles:
        add("FAIL", "HANDLE", "%s is wrong; the handle is @inch_of_shadow" % bad_handles[0])
    else:
        add("PASS", "HANDLE", "ok")

    # photo credit
    if "shirzilber" in low:
        if CREDIT_OK in text:
            add("PASS", "CREDIT", CREDIT_OK + " present in the exact form")
        else:
            add("WARN", "CREDIT", "photo credit must be exactly " + CREDIT_OK + " (camera emoji, handle, no space)")

    # keywords
    for kw in keywords:
        k = kw.lower()
        if k in window_low:
            add("PASS", "KEYWORD", "\"%s\" in the first %d characters" % (kw, cut))
        elif k in low:
            add("WARN", "KEYWORD", "\"%s\" present but after the cut; the opening is what search weighs" % kw)
        else:
            add("FAIL", "KEYWORD", "\"%s\" missing" % kw)

    worst = "PASS"
    for r in results:
        if r["status"] == "FAIL":
            worst = "FAIL"
        elif r["status"] == "WARN" and worst == "PASS":
            worst = "WARN"
    return {"verdict": worst, "chars": n, "visible": min(n, cut), "hashtags": tags,
            "emojis": emoji_n, "window": window, "results": results}


def format_report(rep: dict, cut: int = CUT) -> str:
    lines = _box(rep["window"], cut, rep["chars"])
    lines.append("")
    for r in rep["results"]:
        lines.append("  %-4s  %-11s %s" % (r["status"], r["check"], r["note"]))
    lines.append("")
    lines.append("  %s  %d characters, %d visible, %d hashtags, %d emojis"
                 % (rep["verdict"], rep["chars"], rep["visible"], len(rep["hashtags"]), rep["emojis"]))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Preview the feed cut and check a caption against the house rules.")
    ap.add_argument("path", help="caption text file, or - for stdin")
    ap.add_argument("--keywords", default="", help="comma-separated terms that must appear, ideally in the first 125 chars")
    ap.add_argument("--cut", type=int, default=CUT, help="where the feed cuts (default %d)" % CUT)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    rep = check(raw, [k for k in args.keywords.split(",")], cut=args.cut)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep, cut=args.cut))
    return 0 if rep["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
