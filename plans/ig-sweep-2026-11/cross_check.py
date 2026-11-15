"""Cross-check the picks list against booking/outreach/DM contacts (Amir 11-12: "check there is no user
we unfollow that I messaged for booking"). Reads only who is in a thread and who sent, never message text."""
import glob, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
cands = json.loads((Path(__file__).parent / "candidates.json").read_text())["candidates"]
by_user = {r["username"]: r for r in cands}

hits = {}  # username -> reasons
def add(u, why):
    hits.setdefault(u, set()).add(why)

# 1. IG DM threads (all exports with an inbox)
dm = {}
for f in glob.glob(str(ROOT / "data/instagram-*/your_instagram_activity/messages/inbox/*/message_1.json")):
    j = json.loads(Path(f).read_text())
    folder = Path(f).parent.name.rsplit("_", 1)[0].lower()
    me_sent = sum(1 for m in j.get("messages", []) if m.get("sender_name") in ("Amir Miller", "inch_of_shadow", "Inch of Shadow"))
    names = {norm(p.get("name")) for p in j.get("participants", [])} | {norm(folder)}
    for n in names:
        if n and n not in ("amirmiller", "inchofshadow"):
            prev = dm.get(n, (0, 0)); dm[n] = (max(prev[0], me_sent), max(prev[1], len(j.get("messages", []))))
for r in cands:
    for key in {norm(r["username"]), norm(r["full_name"])} - {""}:
        if key in dm:
            sent, total = dm[key]
            add(r["username"], f"DM thread ({total} msgs, {sent} from you)")

# 2. Handles and instagram links in booking / outreach / promo files
files = [ROOT / "plans/outreach-batches.json", ROOT / "scene_intelligence/promotion_log.json",
         ROOT / "scene_intelligence/dj_promo_targets.json"] + \
        [Path(p) for p in glob.glob(str(ROOT / "plans/handovers/booking/*.md"))] + \
        [ROOT / "plans" / n for n in ("berlin-promoters-2026-10.md", "booking-profile.md", "booking-wave1-drafts.md",
         "sisyphos-booking-2026-10.md", "outreach-prior-contact-audit.md", "farewell-curator-outreach-tracker.md",
         "the-deceiver-outreach-tracker.md", "dj-outreach.md", "htn-dj-promo.md")]
for fp in files:
    if not fp.exists(): continue
    t = fp.read_text(errors="replace").lower()
    handles = set(re.findall(r"instagram\.com/([a-z0-9._]+)", t)) | set(re.findall(r"@([a-z0-9._]{3,30})", t))
    names = set(re.findall(r'"name":\s*"([^"]+)"', t))
    tn = norm(t)
    for r in cands:
        u = r["username"]
        if u in handles or u.rstrip(".") in handles:
            add(u, f"handle in {fp.name}")
        elif len(u) >= 6 and re.search(r"(?<![a-z0-9._])" + re.escape(u) + r"(?![a-z0-9_])", t):
            # bare handle without @ (Amir 11-13: mala_.ika is written that way in htn-dj-promo.md)
            add(u, f"handle in {fp.name}")
        elif len(norm(r["full_name"])) >= 6 and norm(r["full_name"]) in {norm(n) for n in names}:
            add(u, f"name in {fp.name}")
        elif r.get("si_name") and len(norm(r["si_name"])) >= 6 and norm(r["si_name"]) in {norm(n) for n in names}:
            add(u, f"SI name in {fp.name}")

# 3. Linked: the account's bio tags one of the matches above or a DM partner (Amir 11-12: delia_plangg -> @jonnyknueppel)
profs_p = Path(__file__).parent / "profiles.json"
if profs_p.exists():
    profs = json.loads(profs_p.read_text())
    dm_handles = {Path(f).name.rsplit("_", 1)[0].lower() for f in glob.glob(str(ROOT / "data/instagram-*/your_instagram_activity/messages/inbox/*"))}
    direct = set(hits)
    for r in cands:
        bio = ((profs.get(r["username"]) or {}).get("bio") or "").lower()
        for h in re.findall(r"@([a-z0-9._]{2,30})", bio):
            h = h.rstrip(".")
            if r["username"] not in direct and (h in direct or h in dm_handles):
                add(r["username"], f"linked to @{h}")

out = [{"username": u, "full_name": by_user[u]["full_name"], "user_id": by_user[u]["user_id"], "why": sorted(w)} for u, w in sorted(hits.items())]
(Path(__file__).parent / "cross_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "matches")
for o in out: print(o["username"], "|", o["full_name"], "|", "; ".join(o["why"]))
