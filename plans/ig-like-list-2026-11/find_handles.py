"""Find IG handles for score 4-5 SI DJs/artists/labels with none (Socials 27, 2026-11-06).

Read-only: HikerAPI search + profile + newest post, results to this folder only.
Hard stop at --max-calls. Never writes SI or engagement files.
"""
from __future__ import annotations
import argparse, json, re, sys, time
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scene_intelligence")); sys.path.insert(0, str(REPO))
import ig_engagement as E  # noqa: E402

OUT = HERE / "handle_candidates.json"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
STRIP = ("records", "recordings", "music", "official", "label", "dj", "productions")


def core(s):
    n = norm(s)
    for w in STRIP:
        if n.endswith(w) and len(n) > len(w) + 2:
            n = n[: -len(w)]
    return n


def match(name, u):
    c = core(name)
    if not c:
        return 0
    un, fn = core(u.get("username")), core(u.get("full_name"))
    if c == un or c == fn:
        return 3
    if len(c) >= 5 and (c in norm(u.get("username")) or c in norm(u.get("full_name"))):
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max-calls", type=int, default=128)
    ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    cfg = E._import_config(); cs = E.load_enriched_contacts(cfg)
    known = {E.contact_ig_handle(c) for c in cs if E.contact_ig_handle(c)}
    tg = [c for c in cs if E.parse_score(c.get("match_score")) >= 4
          and str(c.get("category")).lower() in ("dj", "artist", "label")
          and not E.contact_ig_handle(c) and not c.get("ig_username_cleared")]
    print("contacts to search:", len(tg))
    if a.dry_run:
        return 0
    import ig_daily_ledger as ledger
    from ig_data_provider import Provider, ProviderError, normalise_profile
    ledger.check_and_claim("ig_like_handle_search", kind="provider", est_calls=a.max_calls,
                           endpoint="provider_search+profile+media")
    p = Provider(sleep=0.3); now = time.time(); res = []
    for c in tg:
        if p.calls + 3 > a.max_calls:
            res.append({"name": c.get("name"), "status": "not_checked_budget"}); continue
        r = {"name": c.get("name"), "category": c.get("category"), "score": E.parse_score(c.get("match_score")),
             "soundcloud_url": c.get("soundcloud_url")}
        try:
            users = p._get("/v1/search/users", query=c.get("name")) or []
        except ProviderError as exc:
            r["status"] = "error"; r["error"] = str(exc)[:120]; res.append(r); continue
        users = users if isinstance(users, list) else (users.get("users") or [])
        best = sorted(((match(c.get("name"), u), u) for u in users[:10] if isinstance(u, dict)),
                      key=lambda x: -x[0])
        if not best or best[0][0] == 0:
            r["status"] = "no_match"; r["seen"] = [u.get("username") for u in users[:5] if isinstance(u, dict)]
            res.append(r); print(c.get("name"), "no match"); continue
        conf, u = best[0]
        r["candidate"] = u.get("username"); r["match"] = "exact" if conf == 3 else "partial"
        r["already_in_si"] = u.get("username") in known
        try:
            prof = p.profile(u.get("username"))
        except ProviderError as exc:
            r["status"] = "error"; r["error"] = str(exc)[:120]; res.append(r); continue
        if not prof:
            r["status"] = "gone"; res.append(r); continue
        r.update(followers=prof["follower_count"], posts=prof["media_count"], private=prof["is_private"],
                 full_name=prof["full_name"], bio=prof["biography"][:160], external_url=prof["external_url"])
        if prof["is_private"] or not prof["media_count"]:
            r["status"] = "private" if prof["is_private"] else "no_posts"; res.append(r); continue
        try:
            ep = p.newest_post_epoch(prof["id"])
        except ProviderError:
            ep = None
        r["post_age_days"] = round((now - ep) / 86400) if ep else None
        r["status"] = "active" if ep and (now - ep) / 86400 <= 90 else "inactive"
        res.append(r); print(c.get("name"), "->", r["candidate"], r["match"], r["followers"], r["status"])
    OUT.write_text(json.dumps({"checked_at": date.today().isoformat(), "calls": p.calls, "results": res},
                              indent=2, ensure_ascii=False) + "\n")
    print("calls used:", p.calls)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
