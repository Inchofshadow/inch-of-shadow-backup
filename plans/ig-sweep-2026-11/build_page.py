"""Write plans/ig-sweep-page/index.html from candidates.json + profiles.json.
Groups by IG account type (from HikerAPI profiles), sorted by size inside each group."""
import base64, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Re-run the contact cross-check first: new profiles add "linked to @contact" matches.
import subprocess, sys
subprocess.run([sys.executable, str(HERE / "cross_check.py")], check=True, stdout=subprocess.DEVNULL)
ROOT = HERE.parents[1]
cands = json.loads((HERE / "candidates.json").read_text())["candidates"]
profs = json.loads((HERE / "profiles.json").read_text()) if (HERE / "profiles.json").exists() else {}

GROUPS = [("contact", "In touch with you (DM, booking or outreach)"), ("music", "DJs and artists"), ("label", "Labels and record shops"), ("venue", "Clubs, events, collectives"),
          ("media", "Media and radio"), ("big", "Big accounts (10k+ or verified)"), ("brand", "Brands and other businesses"),
          ("personal", "Personal or no type"), ("gone", "Gone or private"), ("pending", "Not loaded yet")]
CAT = [("music", r"musician|band|artist|dj|producer|singer|composer|music"), ("label", r"record label|music store|record|label"),
       ("venue", r"club|bar|event|party|community|cultural|venue|festival|entertainment|concert|nightlife|arts"),
       ("media", r"media|news|magazine|radio|broadcast|publisher|blog|podcast|journal")]
BIO = [("music", r"\bdj\b|producer|live act|musician|singer|band\b|booking"), ("label", r"records|recordings|\blabel\b|vinyl"),
       ("venue", r"\bclub\b|festival|party|parties|rave|collective|events"), ("media", r"radio|magazine|zine|podcast")]


def group(r, p):
    if not p: return "pending"
    if p.get("status") != "ok" or p.get("private"): return "gone"
    cat = (p.get("category") or "").lower()
    for g, rx in CAT:
        if cat and re.search(rx, cat): return g
    if p.get("verified") or (p.get("followers") or 0) >= 10000: return "big"
    if cat: return "brand"
    t = (p.get("bio") or "") + " " + r["full_name"]
    for g, rx in BIO:
        if re.search(rx, t, re.I): return g
    return "personal"


SONG = re.compile(r"post.?punk|new.?wave|dark.?wave|cold.?wave|goth|synth.?pop|shoegaze|indie|minimal wave|singer|songwriter", re.I)


def suggest(r, p):
    """Amir's middle rule (11-12 "Yes, pre-mark"): keep songs lane/bands + small scene (score 4-5); cut the rest."""
    if not p: return None
    if p.get("status") != "ok" or p.get("private"): return "unfollow"
    cat = p.get("category") or ""
    t = " ".join([p.get("bio") or "", cat, r["full_name"]]); f = p.get("followers") or 0
    if SONG.search(t) or (cat.lower() == "musician/band" and f < 20000): return "keep"
    if p.get("verified") or f >= 10000: return "unfollow"
    musicish = bool(re.search(r"musician|band|artist|\bdj\b|record|label", cat + " " + t, re.I)) or r["si_name"]
    if musicish and (r["si_score"] or 0) >= 4: return "keep"
    return "unfollow"


xc = {}
if (HERE / "cross_check.json").exists():
    xc = {x["username"]: x["why"] for x in json.loads((HERE / "cross_check.json").read_text())}

# Shadow Archive refs (Amir 11-14: "mark ppl that we used from archive"): tag only, suggestion unchanged.
ARCH = {}
for f in sorted((ROOT / "docs/brand/shadow-archive/refs").glob("R-*.md")):
    txt = f.read_text(errors="replace").lower()
    for h in set(re.findall(r"instagram\.com/([a-z0-9._]+)", txt)) | set(re.findall(r"@([a-z0-9._]{3,30})", txt)):
        ARCH.setdefault(h.rstrip("."), f.stem)

rows = []
for r in cands:
    p = profs.get(r["username"])
    g = "contact" if r["username"] in xc else group(r, p)
    tags = [w for w in xc.get(r["username"], [])]
    if r["si_name"]: tags.append(f"scene contact{' · score ' + str(r['si_score']) if r['si_score'] else ''}")
    if p and p.get("status") == "ok":
        if p.get("category"): tags.append(p["category"])
        if p.get("verified"): tags.append("verified")
        if not p.get("posts"): tags.append("no posts")
    if r["username"] == "teder.fm": tags.append("your radio?")
    if r["username"] in ARCH: tags.insert(0, f"Shadow Archive {ARCH[r['username']]}")
    meta = []
    if p and p.get("status") == "ok":
        meta.append(f"{(p.get('followers') or 0):,} followers · {(p.get('posts') or 0):,} posts")
        if p.get("city"): meta.append(p["city"])
    pic = HERE / "pics" / f"{r['username']}.jpg"
    img = ("data:image/jpeg;base64," + base64.b64encode(pic.read_bytes()).decode()) if pic.exists() else ""
    rows.append({"img": img, "id": r["user_id"], "slug": r["username"], "full": r["full_name"], "g": g,
                 "f": (p or {}).get("followers") or 0, "meta": " · ".join(meta),
                 "bio": ((p or {}).get("bio") or "")[:140], "tags": tags, "s": "keep" if r["username"] in xc else suggest(r, p)})
order = {g: i for i, (g, _) in enumerate(GROUPS)}
rows.sort(key=lambda x: (order[x["g"]], -x["f"], x["slug"]))
labels = {g: l for g, l in GROUPS}


def esc_json(o):
    # Names/bios come from other people's IG profiles: never let them close the script tag.
    return (json.dumps(o, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


loaded = sum(1 for r in cands if r["username"] in profs)
tpl = (HERE / "page_template.html").read_text()
html = (tpl.replace("__ROWS__", esc_json(rows)).replace("__GROUPS__", esc_json(GROUPS))
        .replace("__TOTAL__", str(len(rows))).replace("__LOADED__", str(loaded)))
(ROOT / "plans/ig-sweep-page/index.html").write_text(html)
from collections import Counter
print(len(rows), "loaded", loaded, Counter(r["g"] for r in rows))
