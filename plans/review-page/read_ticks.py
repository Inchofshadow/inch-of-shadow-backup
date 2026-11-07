"""Read phone ticks back into the review blocks (proposals only, never a state change).

The System chat lists the page db collection `ticks` with ArtifactData (out_dir mode), then:
    python3 plans/review-page/read_ticks.py <dir with ticks/*.json>
Each tick file is {slug, id, action, note, sha256, at}; its file name (the db doc id) is the
tick_id. Ticks are grouped per release and passed to review.import_ticks, which only fills
item.proposed and records every tick_id in review.consumed_ticks (replays are ignored).
Amir then confirms at the desk (RM /review or review.py confirm). Prints one line per tick.
Only real releases (exact slug, file on disk) are touched; the page's db rules let only the
owner (Amir) write ticks, so a tick can only come from him.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from release_manager import review, storage  # noqa: E402


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    base = Path(argv[1])
    files = sorted(base.rglob("*.json"))
    by_slug = defaultdict(list)
    for f in files:
        body = json.loads(f.read_text(encoding="utf-8"))
        body = body.get("data", body) if isinstance(body, dict) else body
        slug = str(body.get("slug", "")).strip()
        tick = {"tick_id": f.stem, "id": body.get("id", ""), "action": body.get("action", ""),
                "note": body.get("note", ""), "sha256": body.get("sha256", ""), "at": body.get("at", "")}
        by_slug[slug].append(tick)
    if not files:
        print("no ticks")
        return 0
    # Only a real release, by exact slug: page rows are untrusted text (security review 2026-11-07).
    known = {p.stem for p in storage.iter_release_paths()}
    for slug, ticks in by_slug.items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,80}", slug or "") or slug not in known:
            for t in ticks:
                print("refused %s: unknown release %r" % (t["tick_id"], slug))
            continue
        rel = storage.load_release(slug)
        if not rel or rel.get("slug") != slug:
            for t in ticks:
                print("refused %s: release %s did not load" % (t["tick_id"], slug))
            continue
        results = review.import_ticks(rel, ticks)
        for tick_id, item_id, ok, message in results:
            print("%s %s/%s: %s" % ("ok" if ok else "--", slug, item_id, message))
        # consumed_ticks changes even for refused ticks (replay guard), so save whenever any tick was looked at,
        # through the review module's own save (it backs the file up first).
        if results:
            review.save_release_review(rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
