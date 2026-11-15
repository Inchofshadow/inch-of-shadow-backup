"""Build the IG picks list (option B, Amir "go" 2026-11-12). Read-only on all engine files.

Follows-you set = union of the follower lists 11-03, 11-10, 11-12 (v1 + g2): anyone seen
following in the last 9 days counts as a follower and is never offered.
Excluded: engine-tracked follows (the engine handles those), personal network, tracker
keep_following, blocked list, outreach contacts (handle or name match).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SI = ROOT / "scene_intelligence"
sys.path.insert(0, str(SI)); sys.path.insert(0, str(ROOT))
import ig_engagement as E  # noqa: E402

norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
J = lambda p: json.loads(Path(p).read_text())

fol = set()
for p, key in ((ROOT / "plans/outreach-page/dj07-own-lists-2026-11-03.json", "followers"),
               (SI / "own_lists/own-lists-2026-11-10.json", "followers"),
               (SI / "own_lists/failed-own-lists-2026-11-12.json", "followers")):
    fol |= {u["username"].lower() for u in J(p)[key]}
fol |= set(J(SI / "own_lists/probe-g2-followers-2026-11-12.json")["followers"])
fol |= set(J(SI / "own_lists/probe-g2-followers-2026-11-12b.json")["followers"])  # recheck 11-12 01:00 (Amir "check now")
following = J(SI / "own_lists/failed-own-lists-2026-11-12.json")["following"]  # complete: 1030/1032

cfg = E._import_config()
tracker = E.load_follow_tracker(cfg)
tracked = {x["username"].lower() for x in tracker.get("active_follows", [])}
keep = {x["username"].lower() for x in tracker.get("active_follows", []) if x.get("keep_following")}
personal, pkeep = E.load_personal_network(cfg)
blocked = E.load_blocked_accounts(cfg)
contacts = E.load_enriched_contacts(cfg)
si_by_h = {E.contact_ig_handle(c): c for c in contacts if E.contact_ig_handle(c)}

ob = J(ROOT / "plans/outreach-batches.json")
ob_text = json.dumps(ob, ensure_ascii=False).lower()
ob_handles = set(re.findall(r"instagram\.com/([a-z0-9._]+)", ob_text))
ob_names = {norm(c.get("name")) for b in ob["batches"] for c in b.get("contacts", []) if len(norm(c.get("name"))) >= 4}

rows, out = [], {"follows_you": 0, "engine_tracked": 0, "personal_or_keep": 0, "blocked": 0, "outreach": 0}
for u in following:
    h = u["username"].lower()
    if h in fol: out["follows_you"] += 1; continue
    if h in tracked: out["engine_tracked"] += 1; continue
    if h in personal or h in keep or h in pkeep: out["personal_or_keep"] += 1; continue
    if h in blocked: out["blocked"] += 1; continue
    si = si_by_h.get(h) or {}
    if h in ob_handles or norm(u.get("full_name")) in ob_names or norm(si.get("name")) in ob_names or norm(h) in ob_names:
        out["outreach"] += 1; continue
    rows.append({"username": h, "full_name": u.get("full_name", ""), "private": bool(u.get("is_private")),
                 "verified": bool(u.get("is_verified")), "user_id": str(u.get("pk") or u.get("id") or ""),
                 "si_name": si.get("name"), "si_category": si.get("category"),
                 "si_score": E.parse_score(si.get("match_score")) if si else None})
rows.sort(key=lambda r: (r["si_name"] is None, r["username"]))
res = {"built": "2026-11-12", "followers_seen": len(fol), "following": len(following),
       "excluded": out, "candidates": rows}
(Path(__file__).parent / "candidates.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v for k, v in res.items() if k != "candidates"}), "candidates", len(rows),
      "| SI contacts among them", sum(1 for r in rows if r["si_name"]), "| verified", sum(r["verified"] for r in rows))
