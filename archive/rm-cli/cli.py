"""
release_manager/cli.py
-----------------------
Tool 3 — Release Manager

Manages metadata, checklists, and timelines for music releases.
One JSON file per release in releases/.

Usage:
  python3 release_manager/cli.py new
  python3 release_manager/cli.py list
  python3 release_manager/cli.py show <slug>
  python3 release_manager/cli.py edit <slug> [--title ...] [--date ...]
  python3 release_manager/cli.py track add <slug> --title "..."
  python3 release_manager/cli.py track edit <slug> <number> --bpm 125
  python3 release_manager/cli.py track remove <slug> <number>
  python3 release_manager/cli.py track list <slug>
  python3 release_manager/cli.py check <slug> <task_id>
  python3 release_manager/cli.py uncheck <slug> <task_id>
  python3 release_manager/cli.py checklist <slug>
  python3 release_manager/cli.py link <slug> --spotify "url" --beatport "url"
  python3 release_manager/cli.py timeline <slug>
  python3 release_manager/cli.py status
  python3 release_manager/cli.py validate <slug>
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser

from models import (
    RELEASE_TYPES, ALL_PLATFORMS, VALID_KEYS, DEFAULT_ARTIST,
    make_slug, validate_date, validate_duration, validate_bpm,
    new_release_dict, new_track_dict, validate_release,
)
from storage import (
    ensure_releases_dir, load_release, save_release,
    list_releases, find_release, release_exists, unique_slug,
)
from timeline import compute_timeline, recompute_dates, next_deadline, overdue_milestones
from checklist import (
    generate_checklist, mark_done, mark_undone,
    checklist_progress, overdue_items,
)
from display import header, section, row, divider, progress_bar, days_until, check_mark


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Release Manager — metadata, checklists, timelines.")
    sub = parser.add_subparsers(dest="command")

    # --- new ---
    p_new = sub.add_parser("new", help="Create a new release")
    p_new.add_argument("--title", help="Release title")
    p_new.add_argument("--type", choices=RELEASE_TYPES, help="Release type")
    p_new.add_argument("--date", help="Release date (YYYY-MM-DD)")
    p_new.add_argument("--genre", help="Primary genre")
    p_new.add_argument("--genre2", help="Secondary genre")

    # --- list ---
    sub.add_parser("list", help="List all releases")

    # --- show ---
    p_show = sub.add_parser("show", help="Show full release details")
    p_show.add_argument("slug", help="Release slug (or partial)")

    # --- edit ---
    p_edit = sub.add_parser("edit", help="Edit release metadata")
    p_edit.add_argument("slug", help="Release slug")
    p_edit.add_argument("--title", help="Release title")
    p_edit.add_argument("--date", help="Release date (YYYY-MM-DD)")
    p_edit.add_argument("--genre", help="Primary genre")
    p_edit.add_argument("--genre2", help="Secondary genre")
    p_edit.add_argument("--type", choices=RELEASE_TYPES, dest="release_type", help="Release type")
    p_edit.add_argument("--copyright", help="Copyright line")
    p_edit.add_argument("--description", help="Release description")
    p_edit.add_argument("--upc", help="UPC code")
    p_edit.add_argument("--distributor", help="Distributor name")
    p_edit.add_argument("--catalog", help="Catalog number")
    p_edit.add_argument("--notes", help="General notes")

    # --- track ---
    p_track = sub.add_parser("track", help="Manage tracks")
    track_sub = p_track.add_subparsers(dest="track_command")

    p_ta = track_sub.add_parser("add", help="Add a track")
    p_ta.add_argument("slug", help="Release slug")
    p_ta.add_argument("--title", required=True, help="Track title")
    p_ta.add_argument("--bpm", type=float, help="BPM")
    p_ta.add_argument("--key", choices=VALID_KEYS, help="Musical key")
    p_ta.add_argument("--duration", help="Duration (M:SS)")
    p_ta.add_argument("--genre", help="Track genre primary")
    p_ta.add_argument("--genre2", help="Track genre secondary")

    p_te = track_sub.add_parser("edit", help="Edit a track")
    p_te.add_argument("slug", help="Release slug")
    p_te.add_argument("number", type=int, help="Track number")
    p_te.add_argument("--title", help="Track title")
    p_te.add_argument("--bpm", type=float, help="BPM")
    p_te.add_argument("--key", choices=VALID_KEYS, help="Musical key")
    p_te.add_argument("--duration", help="Duration (M:SS)")
    p_te.add_argument("--isrc", help="ISRC code")
    p_te.add_argument("--genre", help="Track genre primary")
    p_te.add_argument("--genre2", help="Track genre secondary")
    p_te.add_argument("--producer", help="Producer credit")
    p_te.add_argument("--mixer", help="Mixer credit")
    p_te.add_argument("--mastering", help="Mastering credit")
    p_te.add_argument("--writer", help="Writer credit")

    p_tr = track_sub.add_parser("remove", help="Remove a track")
    p_tr.add_argument("slug", help="Release slug")
    p_tr.add_argument("number", type=int, help="Track number")

    p_tl = track_sub.add_parser("list", help="List tracks")
    p_tl.add_argument("slug", help="Release slug")

    # --- check / uncheck ---
    p_check = sub.add_parser("check", help="Mark a checklist task as done")
    p_check.add_argument("slug", help="Release slug")
    p_check.add_argument("task_id", help="Task ID")

    p_uncheck = sub.add_parser("uncheck", help="Mark a checklist task as not done")
    p_uncheck.add_argument("slug", help="Release slug")
    p_uncheck.add_argument("task_id", help="Task ID")

    # --- checklist ---
    p_cl = sub.add_parser("checklist", help="Show full checklist")
    p_cl.add_argument("slug", help="Release slug")

    # --- link ---
    p_link = sub.add_parser("link", help="Add platform links")
    p_link.add_argument("slug", help="Release slug")
    for platform in ALL_PLATFORMS:
        p_link.add_argument(f"--{platform.replace('_', '-')}", dest=platform, help=f"{platform} URL")

    # --- timeline ---
    p_tl2 = sub.add_parser("timeline", help="Show timeline")
    p_tl2.add_argument("slug", help="Release slug")

    # --- status ---
    sub.add_parser("status", help="Dashboard with all releases and deadlines")

    # --- validate ---
    p_val = sub.add_parser("validate", help="Check metadata completeness")
    p_val.add_argument("slug", help="Release slug")

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _get_release(slug: str) -> dict:
    """Load a release or exit with error."""
    rel = find_release(slug)
    if not rel:
        print(f"  ERROR: Release '{slug}' not found.")
        sys.exit(1)
    return rel


def cmd_new(args) -> None:
    title = args.title or input("  Title: ").strip()
    if not title:
        print("  ERROR: Title is required.")
        return

    rtype = args.type
    if not rtype:
        choice = input(f"  Release type [{'/'.join(RELEASE_TYPES)}]: ").strip()
        rtype = choice if choice in RELEASE_TYPES else "EP"

    date = args.date
    if not date:
        date = input("  Release date (YYYY-MM-DD): ").strip()
    if date and not validate_date(date):
        print(f"  ERROR: Invalid date format: {date}")
        return
    if not date:
        print("  ERROR: Release date is required.")
        return

    genre = args.genre or input("  Primary genre (optional): ").strip()
    genre2 = args.genre2 or ""

    slug = unique_slug(make_slug(title, rtype))
    rel = new_release_dict(title, rtype, date, genre, genre2)
    rel["slug"] = slug

    # Generate timeline and checklist
    rel["timeline"] = compute_timeline(date)
    rel["lane"] = "full"  # songs are the main line; set "light" by hand for an electronic drop
    rel["checklist"] = generate_checklist(rel["timeline"], lane=rel["lane"])

    path = save_release(rel)

    header(f"Release Manager \u2014 New Release")
    row("Title", title)
    row("Type", rtype)
    row("Date", date)
    row("Slug", slug)
    if genre:
        row("Genre", f"{genre}" + (f" / {genre2}" if genre2 else ""))
    done, total = checklist_progress(rel["checklist"])
    print(f"\n  [Checklist]  {total} tasks auto-generated")
    print(f"  [Timeline]   {len(rel['timeline'])} milestones computed from {date}")
    print(f"\n  Saved: {path.relative_to(path.parent.parent)}")
    print()


def cmd_list(args) -> None:
    releases = list_releases()
    if not releases:
        print("\n  No releases found. Run 'new' to create one.\n")
        return

    header("Release Manager \u2014 All Releases")
    fmt = "  {slug:<28} {rtype:<6} {date:<12} {prog:<12} {status}"
    print(fmt.format(slug="Slug", rtype="Type", date="Date", prog="Progress", status="Status"))
    divider()

    for rel in releases:
        done, total = checklist_progress(rel.get("checklist", []))
        if total == 0:
            status = "No checklist"
        elif done == total:
            status = "Complete"
        elif done > 0:
            status = "In progress"
        else:
            status = "Not started"

        bar = progress_bar(done, total)
        prog = f"{bar} {done}/{total}"
        meta = rel.get("metadata", {})
        print(fmt.format(
            slug=rel.get("slug", "?"),
            rtype=meta.get("release_type", "?"),
            date=rel.get("release_date", "?"),
            prog=prog,
            status=status,
        ))

    print(f"\n  {len(releases)} releases total\n")


def cmd_show(args) -> None:
    rel = _get_release(args.slug)
    meta = rel.get("metadata", {})

    header(f"Release Manager \u2014 {meta.get('title', '?')} {meta.get('release_type', '')}")

    # Metadata
    section("Metadata")
    row("Title", meta.get("title", ""))
    row("Artist", meta.get("artist", ""))
    row("Type", meta.get("release_type", ""))
    genre = meta.get("genre_primary", "")
    if meta.get("genre_secondary"):
        genre += f" / {meta['genre_secondary']}"
    row("Genre", genre)
    row("Release date", rel.get("release_date", ""))
    row("Copyright", meta.get("copyright", ""))
    row("Description", meta.get("description", ""))
    dist = rel.get("distribution", {})
    row("UPC", dist.get("upc", ""))
    row("Distributor", dist.get("distributor", ""))

    # Tracks
    tracks = rel.get("tracks", [])
    section(f"Tracks  ({len(tracks)} tracks)")
    if tracks:
        fmt = "    {n:<4} {title:<24} {bpm:<6} {key:<6} {dur:<10} {isrc}"
        print(fmt.format(n="#", title="Title", bpm="BPM", key="Key", dur="Duration", isrc="ISRC"))
        divider(width=60, indent=4)
        for t in tracks:
            print(fmt.format(
                n=t.get("number", ""),
                title=t.get("title", "")[:24],
                bpm=t.get("bpm", "") or "\u2014",
                key=t.get("key", "") or "\u2014",
                dur=t.get("duration", "") or "\u2014",
                isrc=t.get("isrc", "") or "\u2014",
            ))
    else:
        print("    No tracks yet. Use 'track add' to add tracks.")

    # Checklist summary
    cl = rel.get("checklist", [])
    done, total = checklist_progress(cl)
    section(f"Checklist  {done}/{total} complete")
    for item in cl:
        mark = check_mark(item["done"])
        label = item["label"]
        due = f"  (due {item['due_date']})" if item.get("due_date") and not item["done"] else ""
        print(f"    {mark}  {label}{due}")

    # Platform links
    links = rel.get("platform_links", {})
    has_links = any(v for v in links.values())
    section("Platform Links")
    if has_links:
        for platform, url in links.items():
            if url:
                row(platform.replace("_", " ").title(), url)
    else:
        print("    No links yet. Use 'link' to add URLs after release.")

    # Next deadline
    tl = rel.get("timeline", [])
    nd = next_deadline(tl)
    if nd:
        section("Next Deadline")
        eta = days_until(nd["date"])
        print(f"    {nd['label']} \u2014 {nd['date']} ({eta})")

    print()


def cmd_edit(args) -> None:
    rel = _get_release(args.slug)
    meta = rel["metadata"]
    changed = []

    if args.title:
        meta["title"] = args.title
        changed.append("title")
    if args.genre:
        meta["genre_primary"] = args.genre
        changed.append("genre_primary")
    if args.genre2:
        meta["genre_secondary"] = args.genre2
        changed.append("genre_secondary")
    if args.release_type:
        meta["release_type"] = args.release_type
        changed.append("release_type")
    if args.copyright:
        meta["copyright"] = args.copyright
        changed.append("copyright")
    if args.description:
        meta["description"] = args.description
        changed.append("description")
    if args.catalog:
        meta["catalog_number"] = args.catalog
        changed.append("catalog_number")
    if args.upc:
        rel["distribution"]["upc"] = args.upc
        changed.append("upc")
    if args.distributor:
        rel["distribution"]["distributor"] = args.distributor
        changed.append("distributor")
    if args.notes:
        rel["notes"] = args.notes
        changed.append("notes")

    # Date change triggers timeline recompute
    if args.date:
        if not validate_date(args.date):
            print(f"  ERROR: Invalid date: {args.date}")
            return
        rel["release_date"] = args.date
        recompute_dates(rel["timeline"], args.date)
        # Recompute checklist due dates from timeline
        tl_dates = {m["id"]: m["date"] for m in rel["timeline"]}
        from checklist import _CHECKLIST_TO_TIMELINE
        for item in rel["checklist"]:
            timeline_id = _CHECKLIST_TO_TIMELINE.get(item["id"], "")
            if timeline_id:
                item["due_date"] = tl_dates.get(timeline_id, item["due_date"])
        changed.append("release_date + timeline")

    if not changed:
        print("  Nothing to change. Use --title, --date, --genre, etc.")
        return

    save_release(rel)
    print(f"\n  Updated {rel['slug']}: {', '.join(changed)}")
    print()


def cmd_track(args) -> None:
    if not args.track_command:
        print("  Use: track add|edit|remove|list <slug>")
        return

    if args.track_command == "add":
        _track_add(args)
    elif args.track_command == "edit":
        _track_edit(args)
    elif args.track_command == "remove":
        _track_remove(args)
    elif args.track_command == "list":
        _track_list(args)


def _track_add(args) -> None:
    rel = _get_release(args.slug)
    number = len(rel["tracks"]) + 1
    track = new_track_dict(
        number=number,
        title=args.title,
        bpm=args.bpm or 0,
        key=args.key or "",
        duration=args.duration or "",
        genre_primary=args.genre or rel["metadata"].get("genre_primary", ""),
        genre_secondary=args.genre2 or rel["metadata"].get("genre_secondary", ""),
    )
    rel["tracks"].append(track)
    save_release(rel)
    print(f"\n  Added track {number}: {args.title}")
    print(f"  Release: {rel['slug']} ({len(rel['tracks'])} tracks)\n")


def _track_edit(args) -> None:
    rel = _get_release(args.slug)
    track = None
    for t in rel["tracks"]:
        if t["number"] == args.number:
            track = t
            break
    if not track:
        print(f"  ERROR: Track {args.number} not found.")
        return

    changed = []
    if args.title:
        track["title"] = args.title
        changed.append("title")
    if args.bpm is not None:
        track["bpm"] = args.bpm
        changed.append("bpm")
    if args.key:
        track["key"] = args.key
        changed.append("key")
    if args.duration:
        track["duration"] = args.duration
        changed.append("duration")
    if args.isrc:
        track["isrc"] = args.isrc
        changed.append("isrc")
    if args.genre:
        track["genre_primary"] = args.genre
        changed.append("genre_primary")
    if args.genre2:
        track["genre_secondary"] = args.genre2
        changed.append("genre_secondary")
    if args.producer:
        track["credits"]["producer"] = args.producer
        changed.append("producer")
    if args.mixer:
        track["credits"]["mixer"] = args.mixer
        changed.append("mixer")
    if args.mastering:
        track["credits"]["mastering"] = args.mastering
        changed.append("mastering")
    if args.writer:
        track["credits"]["writer"] = args.writer
        changed.append("writer")

    if not changed:
        print("  Nothing to change.")
        return

    save_release(rel)
    print(f"\n  Updated track {args.number}: {', '.join(changed)}\n")


def _track_remove(args) -> None:
    rel = _get_release(args.slug)
    found = False
    for i, t in enumerate(rel["tracks"]):
        if t["number"] == args.number:
            removed_title = t["title"]
            rel["tracks"].pop(i)
            found = True
            break
    if not found:
        print(f"  ERROR: Track {args.number} not found.")
        return

    # Renumber remaining tracks
    for i, t in enumerate(rel["tracks"]):
        t["number"] = i + 1

    save_release(rel)
    print(f"\n  Removed track {args.number}: {removed_title}")
    print(f"  {len(rel['tracks'])} tracks remaining (renumbered)\n")


def _track_list(args) -> None:
    rel = _get_release(args.slug)
    tracks = rel.get("tracks", [])
    meta = rel.get("metadata", {})

    header(f"Release Manager \u2014 {meta.get('title', '?')} \u2014 Tracks")
    if not tracks:
        print("  No tracks. Use 'track add' to add.\n")
        return

    fmt = "  {n:<4} {title:<26} {bpm:<6} {key:<6} {dur:<10} {isrc}"
    print(fmt.format(n="#", title="Title", bpm="BPM", key="Key", dur="Duration", isrc="ISRC"))
    divider(width=58)
    for t in tracks:
        print(fmt.format(
            n=t.get("number", ""),
            title=t.get("title", "")[:26],
            bpm=t.get("bpm", "") or "\u2014",
            key=t.get("key", "") or "\u2014",
            dur=t.get("duration", "") or "\u2014",
            isrc=t.get("isrc", "") or "\u2014",
        ))
    print()


def cmd_check(args) -> None:
    rel = _get_release(args.slug)
    if mark_done(rel["checklist"], args.task_id):
        # Also mark timeline milestone if matching
        for m in rel["timeline"]:
            if m["id"] == args.task_id:
                m["done"] = True
        save_release(rel)
        print(f"\n  \u2713 Checked: {args.task_id}\n")
    else:
        print(f"  ERROR: Task '{args.task_id}' not found.")
        print("  Available tasks:")
        for item in rel.get("checklist", []):
            print(f"    {item['id']:<24} {item['label']}")
        print()


def cmd_uncheck(args) -> None:
    rel = _get_release(args.slug)
    if mark_undone(rel["checklist"], args.task_id):
        for m in rel["timeline"]:
            if m["id"] == args.task_id:
                m["done"] = False
        save_release(rel)
        print(f"\n  \u2717 Unchecked: {args.task_id}\n")
    else:
        print(f"  ERROR: Task '{args.task_id}' not found.\n")


def cmd_checklist(args) -> None:
    rel = _get_release(args.slug)
    cl = rel.get("checklist", [])
    meta = rel.get("metadata", {})
    done, total = checklist_progress(cl)

    header(f"Release Manager \u2014 {meta.get('title', '?')} \u2014 Checklist ({done}/{total})")

    current_cat = ""
    for item in cl:
        if item["category"] != current_cat:
            current_cat = item["category"]
            section(current_cat.title())
        mark = check_mark(item["done"])
        due = ""
        if item.get("due_date") and not item["done"]:
            due = f"  (due {item['due_date']} \u2014 {days_until(item['due_date'])})"
        done_info = ""
        if item["done"] and item.get("done_date"):
            done_info = f"  (done {item['done_date']})"
        print(f"    {mark}  {item['id']:<24} {item['label']}{due}{done_info}")

    print()


def cmd_link(args) -> None:
    rel = _get_release(args.slug)
    changed = []
    for platform in ALL_PLATFORMS:
        val = getattr(args, platform, None)
        if val:
            rel["platform_links"][platform] = val
            changed.append(platform)

    if not changed:
        print("  Nothing to update. Use --spotify, --beatport, etc.")
        return

    save_release(rel)
    print(f"\n  Updated links: {', '.join(changed)}\n")


def cmd_timeline(args) -> None:
    rel = _get_release(args.slug)
    tl = rel.get("timeline", [])
    meta = rel.get("metadata", {})

    header(f"Release Manager \u2014 {meta.get('title', '?')} \u2014 Timeline")

    fmt = "  {mark}  {date:<12} {label:<44} {eta}"
    for m in tl:
        mark = check_mark(m["done"])
        eta = days_until(m["date"]) if not m["done"] else ""
        print(fmt.format(mark=mark, date=m["date"], label=m["label"], eta=eta))

    print()


def cmd_status(args) -> None:
    releases = list_releases()
    if not releases:
        print("\n  No releases found. Run 'new' to create one.\n")
        return

    header("Release Manager \u2014 Status Dashboard")

    # Upcoming deadlines across all releases
    all_deadlines = []
    for rel in releases:
        slug = rel["slug"]
        for m in rel.get("timeline", []):
            if not m["done"]:
                all_deadlines.append({"slug": slug, **m})
    all_deadlines.sort(key=lambda d: d["date"])

    section("Upcoming Deadlines")
    if all_deadlines:
        for d in all_deadlines[:10]:  # show top 10
            mark = check_mark(d["done"])
            eta = days_until(d["date"])
            print(f"    {d['date']}  {d['slug']:<26} {d['label']:<36} ({eta})")
    else:
        print("    None")

    # Overdue
    all_overdue = []
    for rel in releases:
        overdue = overdue_milestones(rel.get("timeline", []))
        for m in overdue:
            all_overdue.append({"slug": rel["slug"], **m})

    if all_overdue:
        section("Overdue")
        for d in all_overdue:
            print(f"    {d['date']}  {d['slug']:<26} {d['label']}")

    # Progress per release
    section("Release Progress")
    for rel in releases:
        done, total = checklist_progress(rel.get("checklist", []))
        bar = progress_bar(done, total)
        meta = rel.get("metadata", {})
        pct = f"({done * 100 // total}%)" if total > 0 else ""
        print(f"    {rel['slug']:<28} {bar}  {done:>2}/{total:<2}  {pct}")

    print()


def cmd_validate(args) -> None:
    rel = _get_release(args.slug)
    meta = rel.get("metadata", {})
    warnings = validate_release(rel)

    header(f"Release Manager \u2014 Validation: {meta.get('title', '?')}")

    if not warnings:
        print("\n  All metadata complete. Ready for submission.\n")
        return

    for w in warnings:
        print(f"    \u2717  {w}")

    total_fields = len(warnings) + 17  # rough estimate of total checkable fields
    complete = total_fields - len(warnings)
    print(f"\n  Score: {complete}/{total_fields} fields complete ({complete * 100 // total_fields}%)\n")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

DISPATCH = {
    "new":       cmd_new,
    "list":      cmd_list,
    "show":      cmd_show,
    "edit":      cmd_edit,
    "track":     cmd_track,
    "check":     cmd_check,
    "uncheck":   cmd_uncheck,
    "checklist": cmd_checklist,
    "link":      cmd_link,
    "timeline":  cmd_timeline,
    "status":    cmd_status,
    "validate":  cmd_validate,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    ensure_releases_dir()
    handler = DISPATCH.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
