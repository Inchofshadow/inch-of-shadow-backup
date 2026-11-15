"""Save contact details of every account on the IG picks list before any unfollow, so unfollowed
accounts stay findable as potential contacts (Amir 11-13). Same idea as the SC sweep 11-03.
Writes plans/ig-follow-contacts-2026-11.json + .md. No API calls: uses profiles.json, candidates,
cross_check.json and the picks snapshot.
    python3 plans/ig-sweep-2026-11/save_contacts.py
"""
import json, re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
J = lambda p: json.loads(p.read_text()) if p.exists() else {}
cands = J(HERE / "candidates.json")["candidates"]
profs = J(HERE / "profiles.json")
xc = {x["username"]: x["why"] for x in (J(HERE / "cross_check.json") or [])}
picks = J(HERE / "picks_snapshot.json")
page = (ROOT / "plans/ig-sweep-page/index.html").read_text()
i = page.index("const ROWS = ") + 13
sugg = {r["slug"]: r.get("s") for r in json.loads(page[i:page.index(";\n", i)])}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

out = []
for r in cands:
    u = r["username"]; p = profs.get(u) or {}
    bio = p.get("bio") or ""
    choice = picks.get(u) or sugg.get(u)
    out.append({"username": u, "url": f"https://www.instagram.com/{u}/", "full_name": r["full_name"],
                "choice": choice, "choice_by": "amir" if u in picks else ("suggested" if choice else None),
                "followers": p.get("followers"), "category": p.get("category"), "city": p.get("city"),
                "bio": bio, "emails": sorted(set(EMAIL.findall(bio))), "link": p.get("external_url"),
                "tagged": sorted(set(h.rstrip(".") for h in re.findall(r"@([A-Za-z0-9._]{2,30})", bio))),
                "si_name": r["si_name"], "si_category": r["si_category"], "si_score": r["si_score"],
                "in_touch": xc.get(u, []), "profile_loaded": bool(p)})
res = {"saved": date.today().isoformat(), "source": "IG following sweep 2026-11 (accounts that do not follow back)",
       "accounts": out}
(ROOT / "plans/ig-follow-contacts-2026-11.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")

lines = ["# Instagram contacts saved before the sweep (2026-11)", "",
         "Accounts Amir follows that do not follow back. Saved so they stay findable as potential contacts after an unfollow. JSON twin: ig-follow-contacts-2026-11.json.", ""]
for title, keep in (("Marked unfollow", "unfollow"), ("Kept", "keep"), ("Not decided yet", None)):
    rows = [a for a in out if a["choice"] == keep]
    lines += [f"## {title} ({len(rows)})", ""]
    for a in rows:
        lines.append(f"### {a['full_name'] or a['username']}")
        bits = [a["url"]]
        if a["followers"] is not None: bits.append(f"{a['followers']:,} followers")
        if a["category"]: bits.append(a["category"])
        if a["city"]: bits.append(a["city"])
        if a["si_name"]: bits.append(f"in scene database (score {a['si_score']})")
        lines.append("- Instagram: " + " · ".join(bits))
        if a["emails"]: lines.append("- Email: " + ", ".join(a["emails"]))
        if a["link"]: lines.append("- Link: " + a["link"])
        if a["tagged"]: lines.append("- Tags in bio: " + ", ".join("@" + t for t in a["tagged"]))
        if a["in_touch"]: lines.append("- In touch: " + "; ".join(a["in_touch"]))
        if a["bio"]: lines.append("- Bio: " + " ".join(a["bio"].split()))
        if not a["profile_loaded"]: lines.append("- Profile not loaded yet")
        lines.append("")
(ROOT / "plans/ig-follow-contacts-2026-11.md").write_text("\n".join(lines) + "\n")
from collections import Counter
print("saved", len(out), Counter(a["choice"] for a in out), "with email", sum(1 for a in out if a["emails"]),
      "profiles missing", sum(1 for a in out if not a["profile_loaded"]))
