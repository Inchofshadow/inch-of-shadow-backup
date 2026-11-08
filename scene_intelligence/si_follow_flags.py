"""Refresh the SI follow flags from inch_of_shadow's own follower/following lists.

Ticket SI-02 (Amir "y", 2026-11-04). Before this, ig_i_follow / ig_follows_me /
ig_mutual in enriched_contacts.json only changed when an IG data export was
applied by hand (last: 2026-10-10).

Two steps:
  --fetch   pull both own lists through HikerAPI (~50 calls, provider ledger,
            once a day max) into scene_intelligence/own_lists/own-lists-DATE.json
  --apply   write the flags onto every SI contact with an ig_username
            (backup first; undo restores it)
Default is a dry run: it prints what would change and writes nothing.

Safety: a list that is incomplete, or shorter than 97% of the profile count,
is never applied (a short list would wrongly flip contacts to "not following").
The *_at dates from the export are kept; only the booleans, the checked date
and the source change.

  python3 scene_intelligence/si_follow_flags.py                 # dry run on newest lists
  python3 scene_intelligence/si_follow_flags.py --fetch --apply # monthly job (dispatcher)
  python3 scene_intelligence/si_follow_flags.py --undo
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

SI_DIR = Path(__file__).resolve().parent
ROOT = SI_DIR.parent
sys.path.insert(0, str(SI_DIR))

CONTACTS = SI_DIR / "enriched_contacts.json"
LISTS_DIR = SI_DIR / "own_lists"
LIST_GLOBS = [str(LISTS_DIR / "own-lists-*.json"),
              str(ROOT / "plans" / "outreach-page" / "dj07-own-lists-*.json")]
BACKUP = SI_DIR / "backups" / "enriched_contacts.pre-follow-flags.json"
MIN_COVERAGE = 0.97
FETCH_BUDGET = 85
OWN = "inch_of_shadow"


def _h(v) -> str:
    return str(v or "").strip().lstrip("@").lower()


def newest_lists() -> Path | None:
    files = [Path(f) for g in LIST_GLOBS for f in glob.glob(g)]
    if not files:
        return None
    return max(files, key=lambda p: (p.stem[-10:], p.stat().st_mtime))


def lists_age_days(today: date) -> int | None:
    p = newest_lists()
    if not p:
        return None
    try:
        return (today - date.fromisoformat(p.stem[-10:])).days
    except ValueError:
        return None


def usable(d: dict) -> tuple[bool, str]:
    prof = d.get("profile") or {}
    for side, count_key in (("followers", "follower_count"), ("following", "following_count")):
        got = len(d.get(side) or [])
        want = int(prof.get(count_key) or 0)
        if not d.get(f"{side}_complete"):
            return False, f"{side} list incomplete"
        if not want:
            # Socials 39: no profile count = the 97% guard cannot run; an empty
            # "complete" list would flip every contact to not-following.
            return False, f"{side}: profile count missing, coverage cannot be checked"
        if want and got < MIN_COVERAGE * want:
            return False, f"{side} list {got} < 97% of profile count {want}"
    return True, "ok"


def plan(contacts: list[dict], followers: set, following: set) -> list[tuple]:
    """-> [(contact, new_i_follow, new_follows_me)] for contacts whose flags change."""
    out = []
    for c in contacts:
        h = _h(c.get("ig_username"))
        if not h:
            continue
        fi, fm = h in following, h in followers
        if (bool(c.get("ig_i_follow")), bool(c.get("ig_follows_me"))) != (fi, fm) \
                or "ig_relationship_checked" not in c:
            out.append((c, fi, fm))
    return out


def apply(contacts: list[dict], followers: set, following: set, checked: str, source: str) -> int:
    n = 0
    for c in contacts:
        h = _h(c.get("ig_username"))
        if not h:
            continue
        fi, fm = h in following, h in followers
        if (bool(c.get("ig_i_follow")), bool(c.get("ig_follows_me"))) != (fi, fm):
            n += 1
        c["ig_i_follow"], c["ig_follows_me"], c["ig_mutual"] = fi, fm, fi and fm
        c["ig_relationship_checked"] = checked
        c["ig_relationship_source"] = source
    return n


def fetch_lists(today: date) -> Path:
    import ig_daily_ledger as L
    import ig_data_provider as P
    L.check_and_claim("si_follow_flags", kind="provider", est_calls=FETCH_BUDGET,
                      endpoint="provider_lists")
    p = P.Provider()
    me = p.profile(OWN)
    if not me:
        raise SystemExit("[FLAGS] own profile not returned by the provider")
    res = {"fetched": datetime.now().isoformat(timespec="seconds"), "profile": me}

    def pull(path, side):
        users, max_id = [], None
        while p.calls < FETCH_BUDGET:
            params = {"user_id": me["id"]}
            if max_id:
                params["max_id"] = max_id
            page, max_id = P._unpack_chunk(p._get(path, **params))
            users += [P.normalise_follower(u) for u in page]
            if not max_id or not page:
                return users, True
        return users, False

    try:
        res["followers"], res["followers_complete"] = pull("/v1/user/followers/chunk", "followers")
        res["following"], res["following_complete"] = pull("/v1/user/following/chunk", "following")
    except P.ProviderError as exc:
        res["error"] = str(exc)
    res["calls"] = p.calls
    LISTS_DIR.mkdir(exist_ok=True)
    ok = not res.get("error") and res.get("followers_complete") and res.get("following_complete")
    # Socials 39: a failed/incomplete fetch must not look like today's lists
    # (lists_age_days would read 0 and the dispatcher would wait 7 days).
    name = f"own-lists-{today.isoformat()}.json" if ok else f"failed-own-lists-{today.isoformat()}.json"
    out = LISTS_DIR / name
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(f"[FLAGS] fetched {len(res.get('followers') or [])} followers / "
          f"{len(res.get('following') or [])} following in {p.calls} calls -> {out.name}")
    return out


def _write(blob) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(SI_DIR), prefix=".ec_tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, CONTACTS)


def main() -> int:
    ap = argparse.ArgumentParser(description="Refresh SI follow flags from own IG lists")
    ap.add_argument("--fetch", action="store_true", help="pull fresh lists first (provider calls)")
    ap.add_argument("--apply", action="store_true", help="write the flags (default: dry run)")
    ap.add_argument("--undo", action="store_true", help="restore the pre-apply backup")
    a = ap.parse_args()
    if a.undo:
        if not BACKUP.exists():
            raise SystemExit("[FLAGS] no backup to restore")
        shutil.copy2(BACKUP, CONTACTS)
        print(f"[FLAGS] restored {CONTACTS.name} from {BACKUP.name}")
        return 0

    today = date.today()
    src = fetch_lists(today) if a.fetch else newest_lists()
    if not src:
        raise SystemExit("[FLAGS] no own-lists file found")
    d = json.loads(src.read_text(encoding="utf-8"))
    ok, why = usable(d)
    if not ok:
        print(f"[FLAGS] {src.name} not used: {why}. Nothing written.")
        return 2
    followers = {_h(u.get("username")) for u in d["followers"]} - {""}
    following = {_h(u.get("username")) for u in d["following"]} - {""}
    blob = json.loads(CONTACTS.read_text(encoding="utf-8"))
    contacts = blob if isinstance(blob, list) else blob.get("contacts", [])
    changes = plan(contacts, followers, following)
    flips = [(c, fi, fm) for c, fi, fm in changes
             if (bool(c.get("ig_i_follow")), bool(c.get("ig_follows_me"))) != (fi, fm)]
    gained_f = sum(1 for c, fi, fm in flips if fm and not c.get("ig_follows_me"))
    lost_f = sum(1 for c, fi, fm in flips if not fm and c.get("ig_follows_me"))
    gained_i = sum(1 for c, fi, fm in flips if fi and not c.get("ig_i_follow"))
    lost_i = sum(1 for c, fi, fm in flips if not fi and c.get("ig_i_follow"))
    print(f"[FLAGS] lists {src.name}: {len(followers)} followers / {len(following)} following")
    print(f"  contacts with a handle: {sum(1 for c in contacts if _h(c.get('ig_username')))}")
    print(f"  flag changes: {len(flips)}  (follows you +{gained_f} -{lost_f}, "
          f"you follow +{gained_i} -{lost_i}); first-time checks: {len(changes) - len(flips)}")
    for c, fi, fm in flips[:15]:
        print(f"    @{_h(c.get('ig_username'))}: you follow {bool(c.get('ig_i_follow'))}->{fi}, "
              f"follows you {bool(c.get('ig_follows_me'))}->{fm}")
    if not a.apply:
        print("[DRY-RUN] nothing written. Add --apply to write.")
        return 0
    shutil.copy2(CONTACTS, BACKUP)
    checked = str(d.get("fetched", today.isoformat()))[:10]
    apply(contacts, followers, following, checked, f"own_lists_{checked}")
    _write(blob)
    print(f"[FLAGS] applied; backup {BACKUP.name} (undo: --undo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
