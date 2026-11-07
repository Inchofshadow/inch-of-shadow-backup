"""Read-only contact index: one row per contact across all our contact stores.

SI cleanup step 1 (docs/reports/si-audit-2026-11-03.md, Amir "Yes, start step 1").
Joins, by Instagram handle, then SoundCloud slug, then name:
  - scene_intelligence/enriched_contacts.json   (SI master)
  - scene_intelligence/booking_targets.json     (booking targets)
  - plans/outreach-batches.json                 (outreach batches + status)
and annotates each row with:
  - scene_intelligence/ig_follow_tracker.json   (automation follows on IG)
  - scene_intelligence/sc_follow_tracker.json   (automation follows on SC)
  - newest plans/outreach-page/dj07-own-lists-*.json (who follows Amir / whom he follows)

It READS those files and WRITES only scene_intelligence/contact_index.json.
No network, no API, no edits to any source. Safe to re-run any time.

  python3 scene_intelligence/contact_index.py           # build + summary
  python3 scene_intelligence/contact_index.py --gaps    # also list rows missing from SI
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SI = ROOT / "scene_intelligence" / "enriched_contacts.json"
BOOKING = ROOT / "scene_intelligence" / "booking_targets.json"
OUTREACH = ROOT / "plans" / "outreach-batches.json"
IG_TRACKER = ROOT / "scene_intelligence" / "ig_follow_tracker.json"
SC_TRACKER = ROOT / "scene_intelligence" / "sc_follow_tracker.json"
OWN_LISTS_GLOB = str(ROOT / "plans" / "outreach-page" / "dj07-own-lists-*.json")
OUT = ROOT / "scene_intelligence" / "contact_index.json"

_HANDLE_RE = re.compile(r"^[a-z0-9._]{1,30}$")


# --- normalisers (pure) -------------------------------------------------------

def ig_handle(value) -> str:
    """'@Foo', 'instagram.com/foo/', 'https://www.instagram.com/foo?x' -> 'foo'; junk -> ''."""
    if not isinstance(value, str):
        return ""
    v = value.strip().lower()
    if "instagram.com" in v:
        path = urlparse(v if "://" in v else "https://" + v).path
        v = path.strip("/").split("/")[0] if path.strip("/") else ""
    v = v.lstrip("@").strip().rstrip("/")
    return v if _HANDLE_RE.match(v) else ""


def sc_slug(value) -> str:
    """'https://soundcloud.com/mmdiscos?utm=..' -> 'mmdiscos'; non-SC -> ''."""
    if not isinstance(value, str) or "soundcloud.com" not in value.lower():
        return ""
    path = urlparse(value if "://" in value else "https://" + value).path
    parts = [p for p in path.lower().split("/") if p]
    return parts[0] if parts else ""


def name_keys(name) -> list[str]:
    """Full normalised name, plus the name without a trailing '(...)' part."""
    if not isinstance(name, str) or not name.strip():
        return []
    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
    keys = [norm(name)]
    bare = re.sub(r"\(.*?\)", "", name).strip()
    if bare and norm(bare) not in keys:
        keys.append(norm(bare))
    return [k for k in keys if len(k) >= 3]


# --- source readers -----------------------------------------------------------

def _load(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return default


def si_records(data) -> list[dict]:
    rows = data if isinstance(data, list) else data.get("contacts", [])
    out = []
    for c in rows:
        ig = ig_handle(c.get("ig_username")) or ig_handle(c.get("instagram")) or ig_handle(c.get("instagram_url"))
        out.append({"name": c.get("name", ""), "ig": ig,
                    "sc": sc_slug(c.get("soundcloud_url", "")),
                    "category": c.get("category", ""), "city": c.get("location", ""),
                    "score": c.get("match_score", "")})
    return out


def booking_records(data) -> list[dict]:
    out = []
    for b in (data or {}).get("targets", []):
        out.append({"name": b.get("name", ""), "ig": ig_handle(b.get("instagram")),
                    "sc": "", "type": b.get("type", ""), "city": b.get("city", ""),
                    "status": b.get("status", ""), "in_si_flag": bool(b.get("in_si"))})
    return out


def _outreach_ig(c: dict) -> str:
    st = c.get("send_to") or {}
    if isinstance(st, dict) and "instagram" in str(st.get("channel", "")).lower():
        h = ig_handle(st.get("value"))
        if h:
            return h
    for ch in c.get("channels") or []:
        if isinstance(ch, dict) and "instagram" in str(ch.get("type", "")).lower():
            h = ig_handle(ch.get("value"))
            if h:
                return h
    for it in ((c.get("prior_contact") or {}).get("items") or []):
        if isinstance(it, dict) and it.get("role") == "their Instagram":
            h = ig_handle(it.get("who"))
            if h:
                return h
    return ""


def outreach_records(data) -> list[dict]:
    out = []
    for b in (data or {}).get("batches", []):
        for c in b.get("contacts", []):
            out.append({"name": c.get("name", ""), "ig": _outreach_ig(c), "sc": "",
                        "batch": b.get("id", ""), "status": c.get("status", ""),
                        "channel": c.get("channel", "")})
    return out


def ig_tracker_map(data) -> dict:
    """handle -> 'active' | 'followed_back' | 'unfollowed'."""
    m = {}
    for r in (data or {}).get("unfollowed_history", []) or []:
        h = ig_handle(r.get("username"))
        if h:
            m[h] = "unfollowed"
    act = (data or {}).get("active_follows", []) or []
    if isinstance(act, dict):
        act = list(act.values())
    for r in act:
        h = ig_handle(r.get("username"))
        if h:
            m[h] = "followed_back" if r.get("followed_back") else "active"
    return m


def sc_tracker_map(data) -> dict:
    """slug -> 'active' | 'followed_back' | 'unfollowed'."""
    m = {}
    for r in (data or {}).get("follows", []) or []:
        s = sc_slug(r.get("url", ""))
        if not s:
            continue
        if r.get("followed_back"):
            m[s] = "followed_back"
        elif r.get("no_longer_following"):
            m.setdefault(s, "unfollowed")
        else:
            m[s] = "active"
    return m


def own_lists(path: str | None):
    """-> (followers set, following set, file name) from the newest DJ-07 list file."""
    if not path:
        return set(), set(), ""
    d = _load(Path(path), {})
    fol = {ig_handle(u.get("username")) for u in d.get("followers", []) if isinstance(u, dict)}
    fwg = {ig_handle(u.get("username")) for u in d.get("following", []) if isinstance(u, dict)}
    return fol - {""}, fwg - {""}, Path(path).name


# --- join ---------------------------------------------------------------------

def build(si, booking, outreach, igt, sct, followers, following) -> list[dict]:
    rows: list[dict] = []
    by_ig, by_sc, by_name = {}, {}, {}

    def index(i, rec):
        if rec.get("ig"):
            by_ig.setdefault(rec["ig"], i)
        if rec.get("sc"):
            by_sc.setdefault(rec["sc"], i)
        for k in name_keys(rec.get("name")):
            by_name.setdefault(k, i)

    def find(rec):
        if rec.get("ig") and rec["ig"] in by_ig:
            return by_ig[rec["ig"]]
        if rec.get("sc") and rec["sc"] in by_sc:
            return by_sc[rec["sc"]]
        for k in name_keys(rec.get("name")):
            if k in by_name:
                return by_name[k]
        return None

    def attach(rec, source, fields):
        i = find(rec)
        if i is None:
            rows.append({"name": rec.get("name", ""), "ig": rec.get("ig", ""), "sc": rec.get("sc", ""),
                         "in": [], "booking": [], "outreach": []})
            i = len(rows) - 1
        row = rows[i]
        if not row["ig"] and rec.get("ig"):
            row["ig"] = rec["ig"]
        if not row["sc"] and rec.get("sc"):
            row["sc"] = rec["sc"]
        if source not in row["in"]:
            row["in"].append(source)
        if source == "si":
            row.setdefault("si", []).append({k: rec.get(k, "") for k in fields})
        else:
            row[source].append({k: rec.get(k, "") for k in fields})
        index(i, row | {"name": rec.get("name", "")})

    for r in si:
        attach(r, "si", ("name", "category", "city", "score"))
    for r in booking:
        attach(r, "booking", ("name", "type", "city", "status", "in_si_flag"))
    for r in outreach:
        attach(r, "outreach", ("name", "batch", "status", "channel"))

    for row in rows:
        ig, sc = row["ig"], row["sc"]
        row["ig_automation"] = igt.get(ig, "") if ig else ""
        row["sc_automation"] = sct.get(sc, "") if sc else ""
        row["follows_amir"] = bool(ig) and ig in followers
        row["amir_follows"] = bool(ig) and ig in following
        row["si_duplicates"] = len(row.get("si", [])) if len(row.get("si", [])) > 1 else 0
    return rows


def summary(rows: list[dict]) -> dict:
    def n(pred):
        return sum(1 for r in rows if pred(r))
    return {
        "rows": len(rows),
        "in_si": n(lambda r: "si" in r["in"]),
        "booking": n(lambda r: "booking" in r["in"]),
        "booking_not_in_si": n(lambda r: "booking" in r["in"] and "si" not in r["in"]),
        "outreach": n(lambda r: "outreach" in r["in"]),
        "outreach_not_in_si": n(lambda r: "outreach" in r["in"] and "si" not in r["in"]),
        "with_ig": n(lambda r: r["ig"]),
        "follows_amir": n(lambda r: r["follows_amir"]),
        "amir_follows": n(lambda r: r["amir_follows"]),
        "warm_outreach": n(lambda r: "outreach" in r["in"] and (r["follows_amir"] or r["amir_follows"])),
        "ig_automation_touched": n(lambda r: r["ig_automation"]),
        "sc_automation_touched": n(lambda r: r["sc_automation"]),
        "si_duplicate_groups": n(lambda r: r["si_duplicates"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the read-only contact index.")
    ap.add_argument("--gaps", action="store_true", help="list booking/outreach rows missing from SI")
    a = ap.parse_args()
    lists = sorted(glob.glob(OWN_LISTS_GLOB))
    fol, fwg, lists_name = own_lists(lists[-1] if lists else None)
    rows = build(si_records(_load(SI, [])), booking_records(_load(BOOKING, {})),
                 outreach_records(_load(OUTREACH, {})), ig_tracker_map(_load(IG_TRACKER, {})),
                 sc_tracker_map(_load(SC_TRACKER, {})), fol, fwg)
    s = summary(rows)
    out = {"built": datetime.now().isoformat(timespec="seconds"),
           "read_only_view": True,
           "sources": [str(p.relative_to(ROOT)) for p in (SI, BOOKING, OUTREACH, IG_TRACKER, SC_TRACKER)] + [lists_name],
           "summary": s, "rows": rows}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"[contact_index] wrote {OUT.relative_to(ROOT)}")
    for k, v in s.items():
        print(f"  {k:24s} {v}")
    if a.gaps:
        for r in rows:
            if "si" not in r["in"]:
                src = "+".join(r["in"])
                print(f"  NOT IN SI  {src:17s} {r['name'][:50]:50s} @{r['ig']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
