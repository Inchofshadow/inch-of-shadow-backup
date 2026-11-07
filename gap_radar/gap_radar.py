"""Gap Radar (v1 2026-11-05, profiles GR-03): one engine, many research questions.

Private research tool, for us only, never sold (Reddit data terms). Light reading:
public RSS/JSON feeds, a few seconds between requests.

  python3 gap_radar/gap_radar.py run     [--profile NAME]  # collect + analyze (+ crowding check)
  python3 gap_radar/gap_radar.py collect [--profile NAME]  # posts -> gap_radar/raw/<profile>/<date>.json
  python3 gap_radar/gap_radar.py analyze [--profile NAME]  # one Claude call -> <output_dir>/<date>.md
  python3 gap_radar/gap_radar.py check   [--profile NAME] [report.json]  # crowding check only

A profile is gap_radar/profiles/<name>.json (default: income-gaps):
  name, question, system_extra, output_dir (repo-relative or absolute), crowding (bool),
  sources = {reddit: {subs, phrases}, hn_queries, stackexchange: {sites, queries},
             youtube_queries, github_queries, appstore: {genres, app_ids},
             hikerapi: {hashtags, accounts, max_calls}}
A missing or empty source is skipped. crowding true = product gaps + competitor check;
false = an insight report (findings, no competitor check).
HikerAPI runs only with max_calls > 0, inside what is left of the day's 300 provider
calls after the IG agent (read from the shared ig_daily_ledger, claimed there first).

Ledgers and .env are always the MAIN checkout's (main_root()), also when run from a git
worktree, so the HikerAPI day cap and the Claude monthly cap stay true.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import time
import defusedxml.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
PROFILES_DIR = HERE / "profiles"
DEFAULT_PROFILE = "income-gaps"
sys.path.insert(0, str(HERE.parent / "release_manager"))

UA = "Mozilla/5.0 (Macintosh) gap-radar/0.1 (private research)"
PAUSE = 2.5

# income-gaps defaults (the profile file holds the same lists)
PHRASES = ['"would pay for"', '"is there a tool"', '"is there an app"', '"wish there was"',
           '"shut up and take my money"', '"any alternative to"']
SUBREDDITS = ["SaaS", "Entrepreneur", "smallbusiness", "freelance", "SideProject", "startups",
              "productivity", "selfhosted", "ecommerce", "youtubers", "NewTubers", "podcasting",
              "WeAreTheMusicMakers", "ableton", "edmproduction", "DJs", "musicmarketing",
              "socialmedia", "Etsy", "realtors"]
HN_QUERIES = ["I would pay for", "is there a tool", "wish there was a", "any alternative to",
              "Ask HN: is there"]
APPSTORE_GENRES = {"Productivity": 6007, "Business": 6000, "Music": 6011,
                   "Photo & Video": 6008, "Utilities": 6002}   # niche categories, not Roblox/Gmail
APPSTORE_TOP = 12          # top-grossing apps per category
REDDIT_PAUSE = 8           # unauthenticated RSS is rate-limited (429 at 2.5s)
REDDIT_WAITS = (60, 180)   # back-off on 429 (GR-10): wait 60s, then 180s, then skip the sub
REDDIT_MAX_BLOCKED = 2     # this many subs in a row still 429 = stop Reddit for this run, with a reason
APPSTORE_PAGES = 2         # review pages per app (50 reviews each)

HIKER_DAY_CAP = 300        # provider calls/day for everything; the IG agent comes first
HIKER_MEDIAS_PER_TAG = 9   # top posts kept per hashtag / account (captions)
HIKER_MIN_CHARS = 25       # skip "fire" comments

PROFILE_KEYS = ("name", "question", "system_extra", "output_dir", "crowding", "sources")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,60}$")
SUB_RE = re.compile(r"^[A-Za-z0-9_]{2,40}$")


# --- profiles -------------------------------------------------------------------------------

def main_root() -> Path:
    """The main checkout (not a worktree): shared ledgers and .env live there."""
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=HERE, text=True,
                                capture_output=True, timeout=10, check=True).stdout.strip()
        return (HERE / common).resolve().parent
    except (OSError, subprocess.SubprocessError):
        return HERE.parent


def load_profile(name: str = DEFAULT_PROFILE, folder: Path | None = None) -> dict:
    if (name or "").endswith(".json"):          # GR-08: a profile file from another repo
        path = Path(name).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"no profile file: {path}")
        return load_profile(path.stem, path.parent)
    if not NAME_RE.match(name or ""):
        raise SystemExit(f"bad profile name: {name!r} (lowercase letters, digits, - and _)")
    path = (folder or PROFILES_DIR) / f"{name}.json"
    if not path.exists():
        have = ", ".join(sorted(x.stem for x in (folder or PROFILES_DIR).glob("*.json")))
        raise SystemExit(f"no profile {name!r}; have: {have}")
    p = json.loads(path.read_text())
    missing = [k for k in PROFILE_KEYS if k not in p]
    if missing:
        raise SystemExit(f"profile {name}: missing {', '.join(missing)}")
    if p["name"] != name:
        raise SystemExit(f"profile file {path.name} says name {p['name']!r}")
    p["sources"] = p.get("sources") or {}
    p["crowding"] = bool(p["crowding"])
    return p


def report_dir(p: dict) -> Path:
    d = Path(p["output_dir"]).expanduser()
    return d if d.is_absolute() else HERE.parent / d


def raw_dir(p: dict) -> Path:
    return HERE / "raw" / p["name"]


def latest_raw(p: dict) -> Path:
    files = sorted(raw_dir(p).glob("*.json"))
    if not files and p["name"] == DEFAULT_PROFILE:      # raw files from before GR-03
        files = sorted((HERE / "raw").glob("*.json"))
    if not files:
        raise SystemExit(f"no raw data for {p['name']}: run collect first")
    return files[-1]


# --- sources --------------------------------------------------------------------------------

def get(url: str, pause: float = PAUSE, waits=(60,), **kw):
    """GET with a back-off on 429: one wait per entry in `waits`, then raise."""
    for wait in (*waits, None):
        r = requests.get(url, headers={"User-Agent": UA}, timeout=25, **kw)
        time.sleep(pause)
        if r.status_code == 429 and wait is not None:
            print(f"  429, waiting {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r


def clean(s: str, n: int = 700) -> str:
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def reddit(subs=SUBREDDITS, phrases=PHRASES) -> list[dict]:
    out, ns = [], {"a": "http://www.w3.org/2005/Atom"}
    q = " OR ".join(phrases)
    subs, blocked = list(subs), 0
    for sub in subs:
        if not SUB_RE.match(sub):
            print(f"  reddit: skipped bad subreddit name {sub!r}")
            continue
        url = f"https://www.reddit.com/r/{sub}/search.rss"
        try:
            root = ET.fromstring(get(url, pause=REDDIT_PAUSE, waits=REDDIT_WAITS,
                                     params={"q": q, "restrict_sr": 1, "sort": "relevance",
                                             "t": "year", "limit": 50}).content)
            blocked = 0
        except requests.HTTPError as e:
            if e.response is None or e.response.status_code != 429:
                print(f"  reddit r/{sub}: skipped, HTTP {getattr(e.response, 'status_code', '?')}")
                continue
            blocked += 1
            print(f"  reddit r/{sub}: skipped, still 429 after back-off")
            if blocked >= REDDIT_MAX_BLOCKED:
                left = [s for s in subs[subs.index(sub) + 1:] if SUB_RE.match(s)]
                print(f"  reddit: rate-limited ({blocked} subs in a row), skipping the last {len(left)}"
                      f" subs this run: {', '.join(left) or '-'} (reason: 429, no API access yet, GR-06)")
                break
            continue
        except Exception as e:  # one bad feed never stops the run
            print(f"  reddit r/{sub}: skipped, {type(e).__name__}")
            continue
        for e in root.findall("a:entry", ns):
            link = e.find("a:link", ns)
            out.append({"src": f"reddit r/{sub}", "title": clean(e.findtext("a:title", "", ns), 200),
                        "text": clean(e.findtext("a:content", "", ns)),
                        "url": link.get("href") if link is not None else "",
                        "date": (e.findtext("a:updated", "", ns) or "")[:10]})
        print(f"  reddit r/{sub}: {len(out)} total")
    return out


def hn(queries=HN_QUERIES) -> list[dict]:
    out, since = [], int((datetime.now() - timedelta(days=60)).timestamp())
    for q in queries:
        try:
            hits = get("https://hn.algolia.com/api/v1/search_by_date",
                       params={"query": f'"{q}"', "hitsPerPage": 100,
                               "numericFilters": f"created_at_i>{since}"}).json()["hits"]
        except Exception as e:
            print(f"  hn {q}: {e}")
            continue
        for h in hits:
            oid = h.get("story_id") or h.get("objectID")
            out.append({"src": "hackernews", "title": clean(h.get("title") or h.get("story_title") or "", 200),
                        "text": clean(h.get("comment_text") or h.get("story_text") or ""),
                        "url": f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                        "date": (h.get("created_at") or "")[:10], "points": h.get("points"), "thread": oid})
        print(f"  hn '{q}': {len(out)} total")
    return out


def appstore(genres=tuple(APPSTORE_GENRES), app_ids=()) -> list[dict]:
    """1-2 star reviews of the top-grossing apps in `genres` (names from APPSTORE_GENRES or
    numeric genre ids) plus the apps listed by id in `app_ids`."""
    out, apps = [], []
    for g in genres:
        gid, label = (APPSTORE_GENRES[g], g) if g in APPSTORE_GENRES else (g, f"genre {g}")
        if not str(gid).isdigit():
            print(f"  appstore: unknown genre {g!r}, skipped")
            continue
        try:
            feed = get(f"https://itunes.apple.com/us/rss/topgrossingapplications/limit={APPSTORE_TOP}"
                       f"/genre={int(gid)}/json").json()
            apps += [(e["id"]["attributes"]["im:id"], e["im:name"]["label"], label)
                     for e in feed["feed"]["entry"]]
        except Exception as e:
            print(f"  appstore {label} list: {e}")
    for a in app_ids:
        if str(a).isdigit():
            apps.append((str(a), f"id{a}", "listed"))
    for app_id, name, cat in apps:
        for page in range(1, APPSTORE_PAGES + 1):
            try:
                entries = get(f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={app_id}"
                              f"/sortby=mostrecent/json").json().get("feed", {}).get("entry", [])
            except Exception:
                break
            for e in entries if isinstance(entries, list) else [entries]:
                rating = int(e.get("im:rating", {}).get("label", 5))
                if rating <= 2:
                    out.append({"src": f"appstore {name} ({cat})", "title": clean(e["title"]["label"], 200),
                                "text": clean(e["content"]["label"]), "rating": rating,
                                "url": f"https://apps.apple.com/us/app/id{app_id}",
                                "date": (e.get("updated", {}).get("label") or "")[:10]})
        print(f"  appstore {name}: {len(out)} low-star total")
    return out


def _hiker_list(data, *keys) -> list:
    """HikerAPI answers [items, next_cursor], a plain list, or a dict holding the list."""
    if isinstance(data, list) and len(data) == 2 and isinstance(data[0], list):
        return data[0]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in keys + ("items",):
            if isinstance(data.get(k), list):
                return data[k]
        if isinstance(data.get("response"), dict):
            return _hiker_list(data["response"], *keys)
    return []


def _hiker_date(v) -> str:
    if isinstance(v, (int, float)) and v > 0:
        return datetime.fromtimestamp(v).strftime("%Y-%m-%d")
    return str(v or "")[:10]


def hikerapi(cfg: dict, profile: str, provider=None, ledger_path: Path | None = None,
             today: str | None = None) -> list[dict]:
    """Instagram captions + comments via HikerAPI, only inside the day's leftover.

    Budget = min(max_calls, 300 (or the lower config cap) - provider calls already on today's
    ledger). The budget is claimed on the shared ledger BEFORE the first call (kind="provider",
    like every other HikerAPI job), and the run stops at it."""
    want = int(cfg.get("max_calls") or 0)
    tags = [t.lstrip("#") for t in cfg.get("hashtags") or [] if t]
    accounts = [a.lstrip("@") for a in cfg.get("accounts") or [] if a]
    if want <= 0 or not (tags or accounts):
        return []
    root = main_root()
    for d in (root / "scene_intelligence", HERE.parent / "scene_intelligence"):
        if str(d) not in sys.path:
            sys.path.append(str(d))
    import ig_daily_ledger as L
    from ig_data_provider import Provider, ProviderError
    path = ledger_path or root / "scene_intelligence" / "ig_daily_ledger.json"
    day = today or date.today().isoformat()
    cap = min(HIKER_DAY_CAP, L.provider_cap())
    used = L.provider_calls_today(day, path)
    budget = min(want, cap - used)
    print(f"  hikerapi: {used}/{cap} provider calls used today, radar may use {max(budget, 0)}")
    if budget <= 0:
        return []
    try:
        L.check_and_claim(f"gap_radar_{profile}", kind="provider", est_calls=budget,
                          endpoint="provider_gap_radar", path=path, today=day)
    except L.LedgerRefused:
        return []
    prov = provider or Provider(sleep=0.5)
    left = [budget]

    def call(endpoint, **params):
        if left[0] <= 0:
            return None
        left[0] -= 1
        try:
            return prov._get(endpoint, **params)
        except ProviderError as e:
            print(f"  hikerapi {endpoint}: {str(e)[:120]}")
            return None

    medias = []      # (src, media dict)
    for tag in tags:
        ms = _hiker_list(call("/v1/hashtag/medias/top/chunk", name=tag), "medias")
        medias += [(f"instagram #{tag}", m) for m in ms[:HIKER_MEDIAS_PER_TAG] if isinstance(m, dict)]
    for acc in accounts:
        u = call("/v1/user/by/username", username=acc)
        if isinstance(u, dict) and u.get("pk"):
            ms = _hiker_list(call("/v1/user/medias", user_id=str(u["pk"]), amount=HIKER_MEDIAS_PER_TAG))
            medias += [(f"instagram @{acc}", m) for m in ms if isinstance(m, dict)]
    out = []
    for src, m in medias:
        cap_txt = m.get("caption_text") or ((m.get("caption") or {}).get("text") if isinstance(m.get("caption"), dict) else "")
        url = f"https://www.instagram.com/p/{m['code']}/" if m.get("code") else ""
        if cap_txt:
            out.append({"src": src, "title": "caption", "text": clean(cap_txt), "url": url,
                        "date": _hiker_date(m.get("taken_at")), "likes": m.get("like_count")})
    medias.sort(key=lambda sm: -int(sm[1].get("comment_count") or 0))
    for src, m in medias:
        if left[0] <= 0:
            break
        mid = m.get("pk") or m.get("id")
        if not mid or not int(m.get("comment_count") or 0):
            continue
        url = f"https://www.instagram.com/p/{m['code']}/" if m.get("code") else ""
        for c in _hiker_list(call("/v1/media/comments/chunk", id=str(mid)), "comments"):
            text = clean((c or {}).get("text", "")) if isinstance(c, dict) else ""
            if len(text) >= HIKER_MIN_CHARS:
                out.append({"src": src, "title": "comment", "text": text, "url": url,
                            "date": _hiker_date(c.get("created_at_utc") or c.get("created_at")),
                            "likes": c.get("comment_like_count") or c.get("like_count")})
    print(f"  hikerapi: {budget - left[0]} calls, {len(out)} items")
    return out


def collect(profile: dict | None = None) -> Path:
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import sources_extra as sx  # GR-04 sources + balance
    p = profile or load_profile()
    s = p["sources"]
    today = date.today().isoformat()
    jobs = []
    r = s.get("reddit") or {}
    if r.get("subs") and r.get("phrases"):
        jobs.append(("Reddit", lambda: reddit(r["subs"], r["phrases"])))
    if s.get("hn_queries"):
        jobs.append(("Hacker News", lambda: hn(s["hn_queries"])))
    a = s.get("appstore") or {}
    if a.get("genres") or a.get("app_ids"):
        jobs.append(("App Store", lambda: appstore(a.get("genres") or [], a.get("app_ids") or [])))
    se = s.get("stackexchange") or {}
    if se.get("sites") and se.get("queries"):
        jobs.append(("Stack Exchange", lambda: sx.stackexchange(se["sites"], se["queries"])))
    if s.get("youtube_queries"):
        jobs.append(("YouTube", lambda: sx.youtube(s["youtube_queries"])))
    if s.get("github_queries"):
        jobs.append(("GitHub", lambda: sx.github(queries=s["github_queries"])))
    hk = s.get("hikerapi") or {}
    if int(hk.get("max_calls") or 0) > 0:
        jobs.append(("HikerAPI", lambda: hikerapi(hk, p["name"])))
    print(f"Collecting for {p['name']} ({', '.join(n for n, _ in jobs) or 'no sources'})...")
    items = [it for _, job in jobs for it in job()]
    seen, uniq = set(), []
    for it in items:
        key = it["url"] + it["text"][:80]
        if key not in seen and (it["text"] or it["title"]):
            seen.add(key)
            uniq.append(it)
    uniq = sx.balance(uniq)
    counts: dict = {}
    for it in uniq:
        counts[sx.family(it)] = counts.get(sx.family(it), 0) + 1
    print("Per source: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    folder = raw_dir(p)
    path = folder / f"{today}.json"
    if path.exists():  # second run the same day: never overwrite; 'T' sorts after '.', so analyze picks it
        path = folder / f"{today}T{datetime.now():%H%M}.json"
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(uniq, indent=1, ensure_ascii=False))
    print(f"Saved {len(uniq)} items -> {path}")
    return path


# --- analysis -------------------------------------------------------------------------------

PRODUCT_SYSTEM = """You are a product researcher. {question}

From the posts given, find REPEATED unmet needs where people show willingness to pay
(they say they would pay, already pay for a bad tool, or complain about a paid app).
Ignore one-off rants, generic complaints, and needs only a big company could solve.
Every claim must cite item ids from the input. Never invent evidence."""

INSIGHT_SYSTEM = """You are a research analyst. You read public posts and comments and answer
one research question. {question}

Find REPEATED patterns: things several different people say, ask, use or feel. Ignore
one-off remarks, spam and self-promotion. Every finding must cite item ids from the input.
Never invent evidence, names, outlets, numbers or quotes. In examples, paraphrase briefly in
your own words; copy at most a few words (a term, a name) from a post, never whole
sentences, and never song lyrics."""

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["gaps"],
    "properties": {"gaps": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["name", "pain", "who_pays", "evidence_ids", "pay_signal", "product_idea",
                     "build_weeks", "fit_for_us", "known_competitors", "check_next"],
        "properties": {
            "name": {"type": "string"},
            "pain": {"type": "string"},
            "who_pays": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "integer"}},
            "pay_signal": {"type": "string"},
            "product_idea": {"type": "string"},
            "build_weeks": {"type": "integer"},
            "fit_for_us": {"type": "integer", "description": "1-5"},
            "known_competitors": {"type": "string"},
            "check_next": {"type": "string"}}}}}}

INSIGHT_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["findings"],
    "properties": {"findings": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["name", "insight", "examples", "evidence_ids", "use", "strength"],
        "properties": {
            "name": {"type": "string"},
            "insight": {"type": "string"},
            "examples": {"type": "array", "items": {"type": "string"}},
            "evidence_ids": {"type": "array", "items": {"type": "integer"}},
            "use": {"type": "string"},
            "strength": {"type": "integer", "description": "1-5"}}}}}}


def system_prompt(p: dict) -> str:
    base = PRODUCT_SYSTEM if p["crowding"] else INSIGHT_SYSTEM
    out = base.format(question=p["question"].strip())
    return out + ("\n\n" + p["system_extra"].strip() if (p.get("system_extra") or "").strip() else "")


def _ask_claude(p: dict, items: list) -> tuple[list, float]:
    import claude_api
    lines = [f"[{i}] ({it['src']}{', ' + str(it['rating']) + '*' if 'rating' in it else ''}) "
             f"{it['title']} :: {it['text'][:400]}" for i, it in enumerate(items)]
    body = "\n".join(lines)[:600_000]
    key, schema = ("gaps", SCHEMA) if p["crowding"] else ("findings", INSIGHT_SCHEMA)
    msg = claude_api.ask(
        claude_api.client(), max_tokens=16000, system=system_prompt(p), effort="high", schema=schema,
        what="gap_radar" if p["name"] == DEFAULT_PROFILE else f"gap_radar_{p['name']}",
        messages=[{"role": "user", "content": f"{len(items)} posts:\n\n{body}\n\n"
                   f"Return the 10 strongest {key}, strongest first."}])
    return json.loads(claude_api.text_of(msg))[key], claude_api.usage_of(msg)["cost_usd"]


def _evidence(g: dict, items: list) -> tuple[list, list]:
    ids = [i for i in g["evidence_ids"] if 0 <= i < len(items)]
    return sorted({items[i]["url"] for i in ids if items[i]["url"]}), sorted({items[i]["src"] for i in ids})


def analyze(raw: Path | None = None, gaps: list | None = None, profile: dict | None = None,
            out_dir: Path | None = None) -> Path:
    """One Claude call -> <out_dir>/<raw stem>.md + .json. With gaps given (the check command,
    GR-02), no call is made: the report is rewritten from those gaps, open first, crowded dropped.
    Without a profile: the default profile, report in gap_radar/reports (pre-GR-03 behaviour)."""
    p = profile or load_profile()
    out_dir = Path(out_dir) if out_dir else (report_dir(p) if profile else HERE / "reports")
    raw = raw or latest_raw(p)
    items = json.loads(raw.read_text())
    md_path = out_dir / f"{raw.stem}.md"
    if not p["crowding"]:
        if gaps is None:
            gaps, cost = _ask_claude(p, items)
        else:
            cost = 0.0
        out = _insight_md(p, raw, items, gaps, cost)
    else:
        if gaps is None:
            gaps, cost = _ask_claude(p, items)
        else:
            old = re.search(r"Claude cost \$([0-9]+\.[0-9]+)", md_path.read_text()) if md_path.exists() else None
            cost = float(old.group(1)) if old else 0.0
        out = _product_md(p, raw, items, gaps, cost)
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(out))
    md_path.with_suffix(".json").write_text(json.dumps(gaps, indent=1, ensure_ascii=False))
    print(f"Report -> {md_path}")
    return md_path


def _insight_md(p: dict, raw: Path, items: list, findings: list, cost: float) -> list:
    out = [f"# Gap Radar: {p['name']} - {raw.stem}", "",
           f"{len(items)} posts scanned. Claude cost ${cost:.2f}. Insight report (no competitor check).",
           "", f"Question: {p['question'].strip()}", ""]
    for n, f in enumerate(findings, 1):
        links, srcs = _evidence(f, items)
        out += [f"## {n}. {f['name']}  (strength {f['strength']}/5, {len(f['evidence_ids'])} posts)", "",
                f"- {f['insight']}", f"- Use: {f['use']}"]
        if f.get("examples"):
            out += ["- Examples: " + "; ".join(f["examples"])]
        out += [f"- Evidence: {len(f['evidence_ids'])} posts from {', '.join(srcs)}", ""]
        out += [f"  - {u}" for u in links[:8]] + [""]
    return out


def _product_md(p: dict, raw: Path, items: list, gaps: list, cost: float) -> list:
    checked = [g for g in gaps if "crowding" in g]
    if checked:
        rank = {"open": 0, "unclear": 1}
        shown = sorted([g for g in gaps if g.get("crowding", {}).get("verdict") != "crowded"],
                       key=lambda g: rank.get(g.get("crowding", {}).get("verdict"), 2))
        dropped = [g for g in gaps if g.get("crowding", {}).get("verdict") == "crowded"]
        ccost = sum(g["crowding"].get("cost_usd", 0) for g in checked)
        n_open = sum(1 for g in checked if g["crowding"]["verdict"] == "open")
        head = (f"{len(items)} posts scanned. Claude cost ${cost:.2f} (analysis) + ${ccost:.2f} "
                f"(crowding check, web search). {n_open} open, "
                f"{len(shown) - n_open} unclear, {len(dropped)} crowded (dropped, bottom). "
                "Sources marked (unverified) were not returned by the search itself.")
    else:
        shown, dropped = gaps, []
        head = (f"{len(items)} posts scanned. Claude cost ${cost:.2f}. "
                "Competitors below are Claude's first guess: every gap still needs a hand crowding check.")
    title = f"# Gap Radar - {raw.stem}" if p["name"] == DEFAULT_PROFILE else f"# Gap Radar: {p['name']} - {raw.stem}"
    out = [title, "", head, ""]
    for n, g in enumerate(shown, 1):
        links, srcs = _evidence(g, items)
        c = g.get("crowding")
        tag = f"[{c['verdict'].upper()}] " if c else ""
        out += [f"## {n}. {tag}{g['name']}  (fit {g['fit_for_us']}/5, ~{g['build_weeks']} wk)", ""]
        if c:
            out += [f"- Crowding: {c['verdict']}. {c['reason']}"]
            out += [f"  - Competitor: {x['name']}, {x['price']}, {x['url']}"
                    f"{'' if x['verified'] else ' (unverified)'}" for x in c["competitors"]]
            out += [f"  - Pay proof: {x['claim']} {x['url']}{'' if x['verified'] else ' (unverified)'}"
                    for x in c["pay_proof"]]
        out += [f"- Pain: {g['pain']}", f"- Who pays: {g['who_pays']}",
                f"- Pay signal: {g['pay_signal']}", f"- Product: {g['product_idea']}",
                f"- Known competitors (first guess): {g['known_competitors']}", f"- Check next: {g['check_next']}",
                f"- Evidence: {len(g['evidence_ids'])} posts from {', '.join(srcs)}", ""]
        out += [f"  - {u}" for u in links[:8]] + [""]
    if dropped:
        out += ["## Dropped (crowded)", ""]
        out += [f"- {g['name']}: {g['crowding']['reason']} ("
                + ", ".join(x["name"] for x in g["crowding"]["competitors"][:5]) + ")" for g in dropped]
        out += [""]
    return out


def check_report(p: dict, rep: Path | None = None) -> Path:
    """GR-02 crowding check on a report's gaps, then the report is rewritten."""
    from crowding import check
    if not p["crowding"]:
        raise SystemExit(f"profile {p['name']} has crowding false: insight report, no competitor check")
    if rep is None:
        reps = sorted(report_dir(p).glob("*.json"))
        if not reps:
            raise SystemExit(f"no report for {p['name']}: run analyze first")
        rep = reps[-1]
    raw = raw_dir(p) / rep.name
    if not raw.exists() and p["name"] == DEFAULT_PROFILE:
        raw = HERE / "raw" / rep.name
    return analyze(raw, gaps=check(json.loads(rep.read_text())), profile=p, out_dir=rep.parent)


def main(argv: list | None = None) -> None:
    ap = argparse.ArgumentParser(description="Gap Radar: profile-driven research engine")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "collect", "analyze", "check", "lint"))
    ap.add_argument("report", nargs="?", help="check only: report .json (default: the latest)")
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    a = ap.parse_args(argv)
    p = load_profile(a.profile)
    root = main_root()
    from dotenv import load_dotenv
    load_dotenv(root / ".env")
    import claude_api
    claude_api.LEDGER = root / "stats_snapshots" / "claude_spend.json"   # one ledger for the monthly cap
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    import profile_check as pc  # GR-10: one-line quality proof per run
    if a.cmd == "lint":
        print(pc.pre_check(p))
        print(pc.review(p))
    elif a.cmd == "collect":
        print(pc.pre_check(p))
        collect(p)
    elif a.cmd == "analyze":
        analyze(profile=p)
    elif a.cmd == "check":
        check_report(p, Path(a.report) if a.report else None)
    else:
        print(pc.pre_check(p))
        raw = collect(p)
        md = analyze(raw, profile=p)
        print(pc.yield_line(p, md.with_suffix(".json"), raw))
        if p["crowding"]:
            check_report(p, md.with_suffix(".json"))


if __name__ == "__main__":
    main()
