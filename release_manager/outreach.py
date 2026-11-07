"""Outreach page: load, validate and shape plans/outreach-batches.json.

Read-only, like the tickets page. Each batch lists contacts by the exact `name`
used in scene_intelligence/booking_targets.json; the page joins the two files so
general info, links and hooks come from the targets file and the batch file only
holds what is batch-specific: scene score, draft, channel, review status.
"""
from __future__ import annotations

import json
from pathlib import Path

STATUSES = ("proposed", "needs_rewrite", "drafted", "waiting_on_mix", "approved", "sent", "replied", "booked", "passed")
CHANNELS = ("email", "instagram", "form", "ra", "soundcloud", "phone", "in person", "")
SCORE_LABEL = {5: "exact lane", 4: "adjacent", 3: "broad electronic", 2: "out of genre, DJ friendly", 1: "mainstream or wrong fit"}

REQUIRED_BATCH = ("id", "title", "created", "contacts")
REQUIRED_CONTACT = ("name", "scene_score", "scene_reason", "status")


class OutreachError(ValueError):
    """Raised when a file is unreadable or fails validation."""


def validate(data: dict, target_names: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["top-level must be an object"]
    batches = data.get("batches")
    if not isinstance(batches, list):
        return ["top-level 'batches' must be a list"]
    seen: set[str] = set()
    for b in batches:
        if not isinstance(b, dict):
            errors.append("a batch is not an object")
            continue
        bid = str(b.get("id", "?"))
        for f in REQUIRED_BATCH:
            if f not in b or b[f] in ("", None):
                errors.append(f"{bid}: missing {f}")
        if bid in seen:
            errors.append(f"{bid}: duplicate batch id")
        seen.add(bid)
        if not isinstance(b.get("contacts"), list):
            errors.append(f"{bid}: contacts must be a list")
            continue
        for c in b["contacts"]:
            if not isinstance(c, dict):
                errors.append(f"{bid}: a contact is not an object")
                continue
            cname = str(c.get("name", "?"))
            for f in REQUIRED_CONTACT:
                if f not in c or c[f] in ("", None):
                    errors.append(f"{bid}/{cname}: missing {f}")
            if c.get("name") and c["name"] not in target_names:
                errors.append(f"{bid}/{cname}: not found in booking_targets.json")
            if c.get("status") not in STATUSES:
                errors.append(f"{bid}/{cname}: bad status {c.get('status')!r}")
            s = c.get("scene_score")
            if not isinstance(s, int) or not 1 <= s <= 5:
                errors.append(f"{bid}/{cname}: scene_score must be 1 to 5")
            if not isinstance(c.get("channel", ""), str):
                errors.append(f"{bid}/{cname}: channel must be text")
            if "draft" in c and c["draft"] is not None and not isinstance(c["draft"], dict):
                errors.append(f"{bid}/{cname}: draft must be an object with subject/body")
    return errors


def load(batches_path: Path, targets_path: Path) -> tuple[dict, dict]:
    try:
        data = json.loads(Path(batches_path).read_text(encoding="utf-8"))
        targets = json.loads(Path(targets_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise OutreachError(f"cannot read: {e}") from e
    tlist = targets.get("targets") if isinstance(targets, dict) else None
    if not isinstance(tlist, list):
        raise OutreachError("booking_targets.json: 'targets' must be a list")
    by_name = {t.get("name"): t for t in tlist if isinstance(t, dict) and t.get("name")}
    errors = validate(data, set(by_name))
    if errors:
        raise OutreachError("\n".join(errors))
    return data, by_name


def _links(t: dict) -> list[dict]:
    out = []
    def add(label, url):
        if url and isinstance(url, str) and url.startswith(("http://", "https://")):
            out.append({"label": label, "url": url})
    add("website", t.get("website") or t.get("url"))
    add("RA", t.get("ra_url") or t.get("ra_promoter_url"))
    add("form", t.get("form_url"))
    ig = (t.get("instagram") or "").strip()
    if ig:
        handle = ig.lstrip("@").split("/")[-1] if "instagram.com" not in ig else ig.rstrip("/").split("/")[-1]
        if handle:
            out.append({"label": "instagram @" + handle, "url": "https://www.instagram.com/" + handle + "/",
                        "unverified": not t.get("instagram_verified", True)})
    for u in t.get("proof_urls") or []:
        add("proof", u)
    src = t.get("hook_source") or ""
    for u in [p.strip() for p in src.replace(" (", " ").split(";")]:
        u = u.split(" ")[0]
        if u.startswith("http"):
            add("proof", u)
    seen = set(); dedup = []
    for l in out:
        if l["url"] in seen:
            continue
        seen.add(l["url"]); dedup.append(l)
    return dedup


def _facts(t: dict) -> list[tuple[str, str]]:
    keys = [("type", "type"), ("lane", "lane"), ("kind", "kind"), ("category", "category"), ("city", "city"),
            ("district", "district"), ("country", "country"), ("dates", "dates"), ("deadline", "deadline"),
            ("genre", "genre_lane"), ("style", "style"), ("nights", "nights"), ("series", "series"),
            ("latest", "latest"), ("runs it", "runners"), ("runs it", "runner"), ("venues", "venues"),
            ("how DJs get on", "how_djs_get_on"), ("booker", "booker"), ("fee signal", "fee_signal"),
            ("relationship", "relationship"), ("route", "route"), ("route", "submit_route"),
            ("target status", "status"), ("style warning", "style_warning")]
    out = []
    for label, k in keys:
        v = t.get(k)
        if not v:
            continue
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        out.append((label, str(v)))
    return out


def _num(v):
    """Numbers arrive as int, float or str from different sources; None when unusable."""
    if v in (None, ""):
        return None
    try:
        return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return None


def build_view(data: dict, by_name: dict) -> dict:
    batches = []
    for b in data["batches"]:
        contacts = []
        for c in b["contacts"]:
            t = by_name[c["name"]]
            draft = c.get("draft") or {}
            prof = c.get("profile") or {}
            contacts.append({
                "image": prof.get("image", ""),
                "ig_followers": _num(prof.get("ig_followers")),
                "ig_following": _num(prof.get("ig_following")),
                "ig_posts": _num(prof.get("ig_posts")),
                "sc_followers": _num(prof.get("sc_followers")),
                "numbers_date": prof.get("fetched", ""),
                "ig_handle": (t.get("instagram") or "").lstrip("@"),
                "name": c["name"],
                "category": c.get("category", "") or "",
                "try": c.get("try"),
                "score": c["scene_score"],
                "score_label": SCORE_LABEL[c["scene_score"]],
                "reason": c["scene_reason"],
                "status": c["status"],
                "channel": c.get("channel", "") or (t.get("route") or ""),
                "email": t.get("email") or "",
                "to": c.get("to") or t.get("email") or "",
                "lane": t.get("lane") or "",
                "type": t.get("type") or "",
                "hook": t.get("hook") or "",
                "gap": t.get("hook_gap") or "",
                "facts": _facts(t),
                "links": _links(t),
                "draft_subject": draft.get("subject", ""),
                "draft_body": draft.get("body", ""),
                "notes": c.get("notes", []) or [],
            })
        counts = {s: sum(1 for c in contacts if c["status"] == s) for s in STATUSES}
        ticked = sum(1 for c in contacts if c["try"] is True)
        dropped = sum(1 for c in contacts if c["try"] is False)
        cat_labels = data.get("categories") or {}
        groups = []
        for key, label in cat_labels.items():
            members = [c for c in contacts if c["category"] == key]
            if members:
                groups.append({"key": key, "label": label, "contacts": members})
        rest = [c for c in contacts if c["category"] not in cat_labels]
        if rest:
            groups.append({"key": "other", "label": "Other", "contacts": rest})
        batches.append({"id": b["id"], "title": b["title"], "created": b["created"], "groups": groups,
                        "note": b.get("note", ""), "contacts": contacts, "counts": counts,
                        "ticked": ticked, "dropped": dropped,
                        "drafted": sum(1 for c in contacts if c["draft_body"])})
    return {"updated": data.get("updated", ""), "batches": batches,
            "scale": [(k, SCORE_LABEL[k]) for k in (5, 4, 3, 2, 1)]}


def set_try(batches_path: Path, batch_id: str, name: str, value) -> dict:
    """Amir's review tick: value True (try), False (drop) or None (undecided).
    Writes the batch file atomically and returns the contact's new state."""
    if value not in (True, False, None):
        raise OutreachError("value must be true, false or null")
    path = Path(batches_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise OutreachError(f"cannot read: {e}") from e
    for b in data.get("batches", []):
        if b.get("id") != batch_id:
            continue
        for c in b.get("contacts", []):
            if c.get("name") == name:
                c["try"] = value
                c.setdefault("notes", [])
                tmp = path.with_suffix(".json.tmp")
                tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                tmp.replace(path)
                return {"batch": batch_id, "name": name, "try": value}
    raise OutreachError(f"{batch_id}/{name}: not found")
