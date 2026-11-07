"""Profile quality check (GR-10, 2026-11-05).

Amir wants proof the radar uses real, specific keywords without reading profile files.
Three checks, each ending in ONE line he reads:

  pre_check(p)        before a run, free: subreddits / Stack Exchange sites exist, no
                      generic keywords ("app", "best", "help"...).
  yield_line(p, rep)  after a run, free: which keywords actually brought in the posts that
                      Claude cited as evidence (strong), only noise (weak), or nothing (dead).
  review(p)           once per profile, ~$0.10: Claude reads the profile and names generic
                      keywords plus better words this niche really uses.

  python3 gap_radar/gap_radar.py lint --profile <name>   # pre_check + review
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE / "source_check_cache.json"        # sub/site -> ok|missing, so each is checked once
REVIEWS = HERE / "profile_reviews"
UA = "Mozilla/5.0 (Macintosh) gap-radar/0.1 (private research)"
REDDIT_PAUSE = 8

GENERIC = {"app", "apps", "tool", "tools", "help", "best", "good", "software", "advice", "tips",
           "question", "questions", "need", "review", "reviews", "free", "cheap", "new", "easy",
           "top", "great", "recommend", "recommendation", "recommendations", "how", "what", "why"}
STOP = {"a", "an", "the", "to", "for", "of", "in", "on", "is", "are", "there", "i", "my", "me",
        "and", "or", "with", "any", "it", "that", "this", "do", "does", "be", "would", "you", "we"}


def _words(kw: str) -> list[str]:
    return re.findall(r"[a-z0-9'+#.-]+", kw.lower().replace('"', " "))


def keywords(p: dict) -> list[tuple[str, str]]:
    """(source, keyword) pairs the profile searches with."""
    s = p.get("sources") or {}
    out = [("reddit", k) for k in (s.get("reddit") or {}).get("phrases") or []]
    out += [("hn", k) for k in s.get("hn_queries") or []]
    out += [("stackexchange", k) for k in (s.get("stackexchange") or {}).get("queries") or []]
    out += [("youtube", k) for k in s.get("youtube_queries") or []]
    out += [("github", k) for k in s.get("github_queries") or []]
    return out


SCOPED = {"reddit", "stackexchange"}   # searched inside named communities only


def generic_keywords(p: dict) -> list[str]:
    """A keyword is generic when, after small words, nothing but generic words is left.
    Intent phrases ("is there a tool", "how do I") are fine inside a named subreddit or
    Stack Exchange site; they only pull noise in site-wide searches (HN, YouTube, GitHub)."""
    bad = []
    for src, kw in keywords(p):
        if src in SCOPED:
            continue
        content = [w for w in _words(kw) if w not in STOP]
        if not content or all(w in GENERIC for w in content):
            bad.append(kw)
    return bad


def _cache() -> dict:
    try:
        return json.loads(CACHE.read_text())
    except (OSError, ValueError):
        return {}


def _reddit_exists(sub: str) -> str:
    r = requests.get(f"https://www.reddit.com/r/{sub}/new.rss", headers={"User-Agent": UA},
                     timeout=20, allow_redirects=False)
    time.sleep(REDDIT_PAUSE)
    if r.status_code == 200 and b"<entry>" in r.content:
        return "ok"
    if r.status_code in (403, 404) or (r.status_code in (301, 302) and "search" in r.headers.get("location", "")):
        return "missing"
    if r.status_code == 200:
        return "empty"
    return "unknown"           # 429 and friends: try again next run, never cached


def _se_exists(site: str) -> str:
    r = requests.get("https://api.stackexchange.com/2.3/info", params={"site": site}, timeout=20)
    time.sleep(1)
    if r.status_code == 200:
        return "ok"
    # 400 is also returned for throttling; only "No site found" means the site is not real
    try:
        msg = r.json().get("error_message", "")
    except ValueError:
        msg = ""
    return "missing" if "No site found" in msg else "unknown"


def source_problems(p: dict, check=None) -> dict:
    """{'missing': [...], 'unknown': [...]} for subreddits and Stack Exchange sites."""
    s = p.get("sources") or {}
    cache, out = _cache(), {"missing": [], "unknown": []}
    targets = [("r/" + x, _reddit_exists, x) for x in (s.get("reddit") or {}).get("subs") or []]
    targets += [("se/" + x, _se_exists, x) for x in (s.get("stackexchange") or {}).get("sites") or []]
    for key, fn, arg in targets:
        state = cache.get(key)
        if state is None:
            try:
                state = (check or fn)(arg)
            except requests.RequestException:
                state = "unknown"
            if state != "unknown":
                cache[key] = state
        if state in ("missing", "empty"):
            out["missing"].append(key)
        elif state == "unknown":
            out["unknown"].append(key)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
    return out


def pre_check(p: dict, check=None) -> str:
    gen = generic_keywords(p)
    src = source_problems(p, check)
    n = len(keywords(p))
    parts = [f"Keywords: {n - len(gen)} of {n} specific"
             + (f", generic: {', '.join(gen)}" if gen else "")]
    parts.append("sources: " + ("all real" if not src["missing"] and not src["unknown"] else
                 "; ".join(x for x in (
                     ("missing " + ", ".join(src["missing"])) if src["missing"] else "",
                     ("not checked (rate limit) " + ", ".join(src["unknown"])) if src["unknown"] else "")
                     if x)))
    return "Check " + p["name"] + ": " + " | ".join(parts)


def keyword_yield(p: dict, items: list, findings: list) -> dict:
    """keyword -> 'strong' (in >=2 cited posts), 'weak' (only in uncited posts) or 'dead'."""
    cited = {i for f in findings for i in f.get("evidence_ids", []) if 0 <= i < len(items)}
    texts = [(it.get("title", "") + " " + it.get("text", "")).lower() for it in items]
    out = {}
    for _, kw in keywords(p):
        needle = " ".join(_words(kw))
        hits = [i for i, t in enumerate(texts) if needle and needle in " ".join(_words(t))]
        good = [i for i in hits if i in cited]
        out[kw] = "strong" if len(good) >= 2 else ("weak" if hits else "dead")
    return out


def yield_line(p: dict, report_json: Path, raw: Path) -> str:
    items = json.loads(Path(raw).read_text())
    findings = json.loads(Path(report_json).read_text())
    y = keyword_yield(p, items, findings)
    strong = [k for k, v in y.items() if v == "strong"]
    weak = [k for k, v in y.items() if v != "strong"]
    line = f"Keyword yield {p['name']}: {len(strong)} of {len(y)} strong"
    if weak:
        line += " | weak/dead: " + ", ".join(weak[:8]) + (" ..." if len(weak) > 8 else "")
    return line


REVIEW_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["verdict", "generic", "better_keywords", "better_sources"],
    "properties": {
        "verdict": {"type": "string", "description": "one short sentence"},
        "generic": {"type": "array", "items": {"type": "string"}},
        "better_keywords": {"type": "array", "items": {"type": "string"}},
        "better_sources": {"type": "array", "items": {"type": "string"}}}}


def review(p: dict, client=None) -> str:
    """One cheap Claude call: is this profile generic, and which words does the niche use?"""
    import claude_api
    msg = claude_api.ask(
        client or claude_api.client(), max_tokens=2000, effort="low", schema=REVIEW_SCHEMA,
        what="gap_radar_profile_review",
        system=("You review search profiles for a research tool that reads public posts. Judge "
                "whether the keywords and communities are specific enough to find this niche's "
                "real talk, or so generic they pull noise. Suggest words insiders actually use "
                "(jargon, product names, workflow terms). For German-language searches, German "
                "often has several everyday words for one thing (Erstattung / Rueckerstattung / "
                "Entschaedigung): list the common synonyms that are missing. Only suggest communities you are sure "
                "exist. Be brief."),
        messages=[{"role": "user", "content": json.dumps(
            {k: p[k] for k in ("name", "question", "sources")}, ensure_ascii=False)}])
    r = json.loads(claude_api.text_of(msg))
    REVIEWS.mkdir(exist_ok=True)
    (REVIEWS / f"{p['name']}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    line = f"Review {p['name']}: {r['verdict']}"
    if r["generic"]:
        line += f" | generic: {', '.join(r['generic'][:5])}"
    if r["better_keywords"]:
        line += f" | try: {', '.join(r['better_keywords'][:5])}"
    return line
