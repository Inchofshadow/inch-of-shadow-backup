"""SI cleanup steps 2 + 3 (docs/reports/si-audit-2026-11-03.md, Amir "do 1 and 2").

Step 2 (import): booking targets and outreach contacts that are not in SI become
new SI records (name, category, city, IG, email, url, source, statuses).
Step 3 (merge): SI records that are the same contact (shared IG handle, SC slug
or name) are merged into one; empty fields are filled from the others and the
removed names are kept in `merged_from`.

Bulk-job rule (CLAUDE.md): this script only PLANS by default.
  python3 scene_intelligence/si_cleanup.py plan        # writes the dry-run list, changes nothing
  python3 scene_intelligence/si_cleanup.py apply       # after Amir's yes: backup, apply OK items only
  python3 scene_intelligence/si_cleanup.py apply --include I-012 M-004   # + REVIEW items he approved
  python3 scene_intelligence/si_cleanup.py undo        # restore the backup taken by apply

Only scene_intelligence/enriched_contacts.json is ever changed (by apply/undo).
Booking and outreach files are read, never written. No network.
"""
from __future__ import annotations

import argparse
import difflib
import json
import shutil
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contact_index as ci  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SI = ROOT / "scene_intelligence" / "enriched_contacts.json"
BOOKING = ROOT / "scene_intelligence" / "booking_targets.json"
OUTREACH = ROOT / "plans" / "outreach-batches.json"
PLAN_JSON = ROOT / "scene_intelligence" / "si_cleanup_plan.json"
PLAN_MD = ROOT / "docs" / "reports" / "si-cleanup-plan-2026-11-03.md"
BACKUP = ROOT / "scene_intelligence" / "backups" / "enriched_contacts.pre-si-cleanup.json"

BOOKING_CAT = {"mix_series": "media", "radio": "media", "streaming_channel": "media",
               "promoter": "promoter", "paid_venue": "venue", "venue": "venue",
               "festival": "festival", "agency": "agency", "job_board": "job_board"}
OUTREACH_CAT = {"radio": "media", "clubbing": "promoter", "paid": "venue", "festival": "festival"}
SKIP_BOOKING_STATUS = {"excluded", "duplicate"}
BASE_CATS = ("dj", "label", "curator", "media", "venue", "promoter", "artist", "personal",
             "platform", "distributor", "agency", "festival")


def _empty(v) -> bool:
    return v in ("", None, [], {})


def base_category(cat) -> str:
    c = str(cat or "").lower()
    for b in BASE_CATS:
        if c.startswith(b):
            return b
    return c


# --- step 2: imports ----------------------------------------------------------

def _outreach_email(c: dict) -> str:
    st = c.get("send_to") or {}
    if isinstance(st, dict) and "email" in str(st.get("channel", "")).lower() and "@" in str(st.get("value", "")):
        return st["value"].strip()
    for ch in c.get("channels") or []:
        if isinstance(ch, dict) and ch.get("type") == "email" and "@" in str(ch.get("value", "")):
            return ch["value"].strip()
    return c.get("to", "") if "@" in str(c.get("to", "")) else ""


def _outreach_url(c: dict) -> str:
    st = c.get("send_to") or {}
    v = str(st.get("value", "")) if isinstance(st, dict) else ""
    if v.startswith("http"):
        return v
    for ch in c.get("channels") or []:
        if isinstance(ch, dict) and str(ch.get("value", "")).startswith("http"):
            return ch["value"]
    return ""


def _booking_url(b: dict) -> str:
    for k in ("ra_url", "form_url", "ra_promoter_url"):
        if str(b.get(k, "")).startswith("http"):
            return b[k]
    return ""


def candidate_imports(si: list, booking: dict, outreach: dict) -> list[dict]:
    """New SI records for booking/outreach contacts not matched to SI."""
    rows = ci.build(ci.si_records(si), ci.booking_records(booking), ci.outreach_records(outreach),
                    {}, {}, set(), set())
    braw = {}
    for b in (booking or {}).get("targets", []):
        for k in ci.name_keys(b.get("name")):
            braw.setdefault(k, b)
    oraw = {}
    for bt in (outreach or {}).get("batches", []):
        for c in bt.get("contacts", []):
            for k in ci.name_keys(c.get("name")):
                oraw.setdefault(k, (bt.get("id", ""), c))
    out = []
    for r in rows:
        if "si" in r["in"]:
            continue
        key = (ci.name_keys(r["name"]) or [""])[0]
        b = braw.get(key)
        bid, o = oraw.get(key, ("", None))
        if b and b.get("status") in SKIP_BOOKING_STATUS:
            continue
        cat = BOOKING_CAT.get((b or {}).get("type", ""), "") or OUTREACH_CAT.get((o or {}).get("category", ""), "")
        rec = {
            "name": r["name"],
            "category": cat or "other",
            "location": (b or {}).get("city", ""),
            "ig_username": r["ig"],
            "email": (b or {}).get("email", "") or (b or {}).get("email_alt", "") or (_outreach_email(o) if o else ""),
            "url": (_booking_url(b) if b else "") or (_outreach_url(o) if o else ""),
            "source": "booking_2026-10" if b else "outreach_2026-11",
            "si_added": date.today().isoformat(),
        }
        if r["booking"]:
            rec["booking_status"] = r["booking"][0]["status"]
        if r["outreach"]:
            rec["outreach_status"] = r["outreach"][0]["status"]
            rec["outreach_batch"] = r["outreach"][0]["batch"]
        out.append({k: v for k, v in rec.items() if not _empty(v)} | {"name": rec["name"], "category": rec["category"]})
    return out


def review_reasons_import(rec: dict, si_keys: list[str]) -> list[str]:
    why = []
    if rec.get("category") == "job_board":
        why.append("job board, not a contact")
    if not any(rec.get(k) for k in ("ig_username", "email", "url")):
        why.append("no IG, email or url")
    key = (ci.name_keys(rec.get("name")) or [""])[0]
    if key:
        close = difflib.get_close_matches(key, si_keys, n=1, cutoff=0.86)
        sub = [k for k in si_keys if len(key) >= 6 and len(k) >= 6 and (key in k or k in key)]
        hit = (close or sub[:1])
        if hit:
            why.append(f"name close to an SI contact ({hit[0]})")
    return why


# --- step 3: merges -----------------------------------------------------------

def duplicate_groups(si: list) -> list[list[int]]:
    par = list(range(len(si)))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    seen = {}
    for i, c in enumerate(si):
        keys = []
        ig = ci.ig_handle(c.get("ig_username")) or ci.ig_handle(c.get("instagram"))
        if ig:
            keys.append("ig:" + ig)
        sc = ci.sc_slug(c.get("soundcloud_url", ""))
        if sc:
            keys.append("sc:" + sc)
        keys += ["n:" + k for k in ci.name_keys(c.get("name"))[:1]]
        for k in keys:
            if k in seen:
                par[f(i)] = f(seen[k])
            else:
                seen[k] = i
    g = defaultdict(list)
    for i in range(len(si)):
        g[f(i)].append(i)
    return [v for v in g.values() if len(v) > 1]


_GENERIC = ("recordings", "records", "music", "radio", "official", "the", "dj", "label", "berlin", "events")


def _core(name) -> str:
    """Name without generic words, so 'Axylone Recordings' vs 'Gated Recordings' differ."""
    import re
    words = re.findall(r"[a-z0-9]+", str(name or "").lower())
    words = [w for w in words if w not in _GENERIC]
    core = "".join(words)
    for g in _GENERIC:                     # handle-style names: 'melopeerecords'
        if core.endswith(g) and len(core) > len(g) + 2:
            core = core[: -len(g)]
    return core


def review_reasons_merge(recs: list[dict]) -> list[str]:
    why = []
    names = sorted({_core(r.get("name")) for r in recs} - {""})
    if any(difflib.SequenceMatcher(None, a, b).ratio() < 0.8 and not (a in b or b in a)
           for i, a in enumerate(names) for b in names[i + 1:]):
        why.append("names differ")
    igs = {ci.ig_handle(r.get("ig_username")) for r in recs} - {""}
    if len(igs) > 1:
        why.append("different IG handles")
    scs = {ci.sc_slug(r.get("soundcloud_url", "")) for r in recs} - {""}
    if len(scs) > 1:
        why.append("different SoundCloud accounts")
    cats = {base_category(r.get("category")) for r in recs} - {""}
    if len(cats & {"dj", "label", "curator", "media", "venue", "promoter"}) > 1:
        why.append("different kinds (" + "/".join(sorted(cats)) + ")")
    return why


def merge_records(recs: list[dict]) -> dict:
    """Keeper = most filled record; fill its empty fields from the others."""
    order = sorted(range(len(recs)), key=lambda i: -sum(not _empty(v) for v in recs[i].values()))
    keep = dict(recs[order[0]])
    pretty = [r.get("name", "") for r in recs if " " in r.get("name", "") or any(ch.isupper() for ch in r.get("name", ""))]
    if pretty and keep.get("name") not in pretty:
        keep["name"] = pretty[0]
    for i in order[1:]:
        for k, v in recs[i].items():
            if _empty(keep.get(k)) and not _empty(v):
                keep[k] = v
            elif isinstance(keep.get(k), list) and isinstance(v, list):
                keep[k] = keep[k] + [x for x in v if x not in keep[k]]
    keep["merged_from"] = sorted({r.get("name", "") for r in recs} - {keep["name"]}) or [keep["name"]]
    keep["merged_at"] = date.today().isoformat()
    return keep


# --- plan / apply / undo -------------------------------------------------------

def make_plan(si: list, booking: dict, outreach: dict) -> dict:
    si_keys = [k for c in si for k in ci.name_keys(c.get("name"))[:1]]
    imports = []
    for n, rec in enumerate(candidate_imports(si, booking, outreach), 1):
        why = review_reasons_import(rec, si_keys)
        imports.append({"id": f"I-{n:03d}", "review": why, "record": rec})
    merges = []
    for n, grp in enumerate(duplicate_groups(si), 1):
        recs = [si[i] for i in grp]
        why = review_reasons_merge(recs)
        merges.append({"id": f"M-{n:03d}", "review": why, "indexes": grp,
                       "names": [r.get("name", "") for r in recs],
                       "keep_name": merge_records(recs)["name"]})
    return {"made": date.today().isoformat(), "si_count": len(si), "imports": imports, "merges": merges}


def plan_markdown(plan: dict) -> str:
    imp_ok = [x for x in plan["imports"] if not x["review"]]
    imp_rv = [x for x in plan["imports"] if x["review"]]
    mrg_ok = [x for x in plan["merges"] if not x["review"]]
    mrg_rv = [x for x in plan["merges"] if x["review"]]
    L = [f"# SI cleanup dry run ({plan['made']})", "",
         "Nothing has changed yet. On Amir's yes, `si_cleanup.py apply` backs up SI, then applies the OK items only.",
         "REVIEW items are skipped unless he names them (for example \"also I-012, M-004\").", "",
         "| | OK | REVIEW |", "|---|---|---|",
         f"| Step 2: new SI contacts | {len(imp_ok)} | {len(imp_rv)} |",
         f"| Step 3: duplicate merges | {len(mrg_ok)} | {len(mrg_rv)} |", "",
         f"SI now: {plan['si_count']} contacts. After OK items: "
         f"{plan['si_count'] + len(imp_ok) - sum(len(x['indexes']) - 1 for x in mrg_ok)}.", "",
         "## Step 3, REVIEW (looks like different contacts)", "", "| id | records | why |", "|---|---|---|"]
    L += [f"| {x['id']} | {' + '.join(x['names'])} | {'; '.join(x['review'])} |" for x in mrg_rv]
    L += ["", "## Step 3, OK (same contact twice)", "", "| id | records | kept as |", "|---|---|---|"]
    L += [f"| {x['id']} | {' + '.join(x['names'])} | {x['keep_name']} |" for x in mrg_ok]
    L += ["", "## Step 2, REVIEW", "", "| id | name | category | why |", "|---|---|---|---|"]
    L += [f"| {x['id']} | {x['record']['name']} | {x['record']['category']} | {'; '.join(x['review'])} |" for x in imp_rv]
    L += ["", "## Step 2, OK", "", "| id | name | category | city | IG | source |", "|---|---|---|---|---|---|"]
    L += [f"| {x['id']} | {x['record']['name']} | {x['record']['category']} | {x['record'].get('location', '')} | "
          f"{x['record'].get('ig_username', '')} | {x['record']['source']} |" for x in imp_ok]
    return "\n".join(L) + "\n"


def apply_plan(si: list, plan: dict, include: set[str]) -> tuple[list, dict]:
    if plan["si_count"] != len(si):
        raise SystemExit("SI changed since the plan was made; run `plan` again.")
    take = lambda x: not x["review"] or x["id"] in include  # noqa: E731
    drop, merged = set(), {}
    for m in plan["merges"]:
        if take(m):
            recs = [si[i] for i in m["indexes"]]
            merged[m["indexes"][0]] = merge_records(recs)
            drop.update(m["indexes"][1:])
    out = [merged.get(i, c) for i, c in enumerate(si) if i not in drop]
    added = [x["record"] for x in plan["imports"] if take(x)]
    out.extend(added)
    return out, {"merged_groups": len(merged), "removed": len(drop), "added": len(added), "total": len(out)}


def main() -> int:
    ap = argparse.ArgumentParser(description="SI cleanup steps 2 + 3 (dry run by default).")
    ap.add_argument("cmd", choices=["plan", "apply", "undo"])
    ap.add_argument("--include", nargs="*", default=[], help="REVIEW ids Amir approved")
    a = ap.parse_args()
    if a.cmd == "undo":
        if not BACKUP.exists():
            raise SystemExit("no backup to restore")
        shutil.copy2(BACKUP, SI)
        print(f"[si_cleanup] restored {SI.name} from {BACKUP.name}")
        return 0
    si = ci._load(SI, [])
    if a.cmd == "plan":
        plan = make_plan(si, ci._load(BOOKING, {}), ci._load(OUTREACH, {}))
        PLAN_JSON.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
        PLAN_MD.write_text(plan_markdown(plan))
        print(f"[si_cleanup] dry run written: {PLAN_MD.relative_to(ROOT)} (nothing changed)")
        print(plan_markdown(plan).split("## ")[0])
        return 0
    plan = json.loads(PLAN_JSON.read_text())
    out, stats = apply_plan(si, plan, set(a.include))
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SI, BACKUP)
    tmp = SI.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=2, ensure_ascii=False))  # same format as the file today
    tmp.replace(SI)
    print(f"[si_cleanup] applied: {stats}. Backup: {BACKUP.relative_to(ROOT)}. Undo: si_cleanup.py undo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
