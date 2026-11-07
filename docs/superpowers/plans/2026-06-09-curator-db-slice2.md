# Curator DB - Slice 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a playlist/curator channel to the `promotion-expert` agent (drafts free IG-DM + concise Groover pitches in Amir's voice) plus a Spotify-API checker that auto-detects playlist adds.

**Architecture:** Curators become the 3rd channel of the existing promo agent (DJ -> Label -> Curator), consuming the Slice 1 curator DB. A pitch-template doc guides the agent's voice; one small tested helper (`curator_check_adds.py`) reuses the engine's Spotify auth to mark adds.

**Tech Stack:** Python 3.9+ (stdlib + requests via the engine), pytest. Claude Code agent/skill (markdown). Spotify API (read-only) only in the adds-checker.

---

## File Structure

- `plans/curator-pitch-template.md` - NEW: the two pitch variants (free IG DM + Groover).
- `.claude/agents/promotion-expert.md` - EDIT: add the Playlist/Curator channel section.
- `.claude/skills/promo/SKILL.md` - EDIT: note it now covers curators.
- `scene_intelligence/curator_check_adds.py` (+ `tests/test_curator_check_adds.py`) - NEW: auto-detect adds.

`.claude/` is gitignored. The template, the helper, its test, the spec, and this plan are committed.

---

## Task 1: The curator pitch template

**Files:** Create `plans/curator-pitch-template.md`

- [ ] **Step 1: Write the template file**

Create `plans/curator-pitch-template.md`:

```markdown
# Curator Pitch Template (Inch of Shadow)

Two variants. The promotion-expert agent picks by the curator's `contact.route`.
Voice: genuine, peer-to-peer, in Amir's voice (the register of the Farewell DMs).
HARD: no clickbait, no em dash, no double dash. Light emoji ok.

Placeholders: `[CURATOR]` `[PLAYLIST]` `[TRACK]` `[LINK]` `[VIBE]` `[NEXT]` `[DATE]`.
`[LINK]` = the live track's Spotify URL from `releases/<slug>.json` `platform_links.spotify`.
`[VIBE]` = a one-line sound hook (e.g. "122 BPM, EBM weight under an acid lead").

## Free IG DM (route = free) - warm, personal

```
Hi, how are you? :)
I've been into [PLAYLIST] for a while, love the selection. I produce dark disco and EBM as
Inch of Shadow, based in Berlin. I just put out a track called [TRACK], [VIBE]. I really think
it would sit well on the playlist.
[LINK]
Would mean a lot if you gave it a listen. I've got another one, [NEXT], coming [DATE] too.
Thank you so much
```

## Groover (route = paid) - concise, skim-friendly

```
Dark disco / EBM from Berlin (Inch of Shadow). [TRACK]: [VIBE]. Feels right at home on
[PLAYLIST]. Would love your consideration. Thank you.
```

Personalize the playlist reference + genre angle per curator. Lead with the live track
(Farewell now; The Deceiver at its release); a one-line tease of the upcoming one is optional.
```

- [ ] **Step 2: Commit**

```bash
git add plans/curator-pitch-template.md
git commit -m "docs(curator): pitch template (free DM + Groover variants)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: curator_check_adds.py - pure helpers (TDD)

**Files:**
- Create: `scene_intelligence/curator_check_adds.py`
- Test: `tests/test_curator_check_adds.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_curator_check_adds.py`:

```python
import scene_intelligence.curator_check_adds as ca


def test_track_id_from_url():
    assert ca.track_id_from_url("https://open.spotify.com/track/6lOM9849xsWTUGiBJBjpuE?si=x") == "6lOM9849xsWTUGiBJBjpuE"
    assert ca.track_id_from_url("") == ""


def test_track_in_playlist():
    assert ca.track_in_playlist("ABC", ["X", "ABC", "Y"]) is True
    assert ca.track_in_playlist("ABC", ["X", "Y"]) is False
    assert ca.track_in_playlist("", ["X"]) is False
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/test_curator_check_adds.py -v`
Expected: FAIL - `ModuleNotFoundError`.

- [ ] **Step 3: Write the minimal implementation**

Create `scene_intelligence/curator_check_adds.py`:

```python
"""Auto-detect playlist adds: for each pitched curator, check via the Spotify API
whether the release's track is now on their playlist, and mark them 'added'.

Pure helpers are unit-tested; the API + I/O run in main(), reusing discover_curators'
Spotify auth. Read-only.
"""
import re
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def track_id_from_url(url):
    """Extract the Spotify track id from a URL, or '' if none."""
    m = re.search(r"track/([A-Za-z0-9]+)", url or "")
    return m.group(1) if m else ""


def track_in_playlist(track_id, playlist_track_ids):
    """True if the track id is present among a playlist's track ids."""
    return bool(track_id) and track_id in set(playlist_track_ids)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/test_curator_check_adds.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scene_intelligence/curator_check_adds.py tests/test_curator_check_adds.py
git commit -m "feat(curator): track-id parsing + playlist-membership helpers

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: curator_check_adds.py - fetch + CLI

**Files:**
- Modify: `scene_intelligence/curator_check_adds.py`

- [ ] **Step 1: Add the playlist-tracks fetch + CLI**

Append to `scene_intelligence/curator_check_adds.py`:

```python
def fetch_playlist_track_ids(playlist_id, eng, max_pages=4):
    """Return the track ids on a playlist (paginated, capped). Reuses engine auth."""
    ids = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"fields": "items(track(id)),next", "limit": 100}
    calls = 0
    while url and calls < max_pages:
        data = eng._spotify_get(url, params=params)
        calls += 1
        if not data:
            break
        for it in data.get("items", []):
            t = (it or {}).get("track") or {}
            if t.get("id"):
                ids.append(t["id"])
        url = data.get("next")
        params = None  # next is a full URL
    return ids, calls


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description="Mark curators who added the release track")
    ap.add_argument("slug", help="Release slug (matches releases/<slug>.json)")
    ap.add_argument("--base-dir", default=".")
    ap.add_argument("--dry-run", action="store_true", help="Report would-be adds, do not write")
    args = ap.parse_args()

    import discover_curators as eng  # scene_intelligence/ is on sys.path

    release = _load(f"{args.base_dir}/releases/{args.slug}.json")
    track_id = track_id_from_url((release.get("platform_links") or {}).get("spotify", ""))
    if not track_id:
        raise SystemExit("No Spotify track URL in the release JSON - cannot check adds.")

    contacts_path = f"{args.base_dir}/scene_intelligence/enriched_contacts.json"
    contacts = _load(contacts_path)
    pitched = [c for c in contacts if isinstance(c, dict) and c.get("category") == "curator"
               and c.get("promo_latest_status") in ("sent", "pitched")]
    n_pl = sum(len(c.get("curator_playlists", [])) for c in pitched)
    print(f"{len(pitched)} pitched curator(s), {n_pl} playlist(s) to check "
          f"(about {n_pl} to {n_pl * 4} Spotify API calls).")

    total_calls = 0
    added = []
    for c in pitched:
        hit = False
        for p in c.get("curator_playlists", []):
            if not p.get("id"):
                continue
            ids, calls = fetch_playlist_track_ids(p["id"], eng)
            total_calls += calls
            if track_in_playlist(track_id, ids):
                hit = True
                break
        if hit:
            added.append(c.get("name"))
            if not args.dry_run:
                c["promo_latest_status"] = "added"

    print(f"Made {total_calls} API calls. Added: {added or 'none'}")
    if added and not args.dry_run:
        with open(contacts_path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
        print("Marked the above curators as 'added' in enriched_contacts.json.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify it imports + helpers still pass**

Run: `python3 -m pytest tests/test_curator_check_adds.py -q`
Expected: PASS (2 passed).
Run: `python3 -c "import scene_intelligence.curator_check_adds as m; print('ok', bool(m.fetch_playlist_track_ids))"`
Expected: `ok True` (do NOT call it - that hits the API).

- [ ] **Step 3: Commit**

```bash
git add scene_intelligence/curator_check_adds.py
git commit -m "feat(curator): Spotify playlist-add auto-detection CLI

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Add the curator channel to the agent + skill

**Files:**
- Modify: `.claude/agents/promotion-expert.md`
- Modify: `.claude/skills/promo/SKILL.md`

- [ ] **Step 1: Insert the curator channel before `## Boundaries` in the agent**

In `.claude/agents/promotion-expert.md`, immediately BEFORE the `## Boundaries` heading,
insert:

```markdown
## Playlist / Curator channel
Reads curator-contacts (`category:"curator"`, from the Slice 1 DB) + their `curator_playlists`
+ the active release. Pitches playlists; the contact is the curator.
1. **Target selection** - prioritize by the tier: free verified routes (`contact.route=="free"`
   AND `contact_verified`) = draft all; paid = the proven set (`cross_list_count>=2` and fit
   top/good); SKIP and flag `suspect` curators and unverified-free ones. Order by
   `curator_pitch_sheet` logic (fit -> cross_list -> saves).
2. **Pitch drafting** - per curator, use `plans/curator-pitch-template.md`: route `free` ->
   the warm IG DM; route `paid` -> the concise Groover variant. Personalize to THAT playlist +
   its genre. Pull `[LINK]` (the live track) from `releases/<slug>.json` `platform_links.spotify`;
   lead with the live track, optionally tease the upcoming release.
3. **Outcome capture** - log per curator: `promo_latest_status` (sent / added / passed /
   ignored) + `last_engaged`. Adds can be auto-detected:
   `python3 scene_intelligence/curator_check_adds.py <slug>` (pre-announce the call count; it
   marks curators whose playlist now contains the release track).

### Curator-channel rules
- Drafts only. Amir sends IG DMs and submits to Groover himself. Never send/pay/submit.
- Copy: peer-to-peer in Amir's voice; no clickbait; no em dash; no double dash.
- Never draft for `suspect` or unverified-free curators without flagging them first.
```

- [ ] **Step 2: Update the skill description**

In `.claude/skills/promo/SKILL.md`, replace the `description:` line with:

```
description: Promotion helper for Inch of Shadow - DJ, label, and playlist-curator channels. DJs: DM drafts. Labels: demo-safe hooks for Tool 4. Curators: free IG-DM + Groover pitches off the curator DB. Use when the user wants to promote a release to DJs, labels, or playlist curators, or types /promo.
```

And add under the title heading:
```
Curator channel: drafts free IG-DM + Groover pitches from the curator DB (category:"curator"),
tracks adds via curator_check_adds.py. Amir sends/submits manually.
```

- [ ] **Step 3: Verify the edits**

Run: `python3 -c "a=open('.claude/agents/promotion-expert.md').read(); print('curator chan:', '## Playlist / Curator channel' in a); s=open('.claude/skills/promo/SKILL.md').read(); print('skill curators:', 'curator' in s.lower())"`
Expected: both `True`.

- [ ] **Step 4: (No commit - `.claude/` is gitignored.)**

---

## Task 5: End-to-end verification

- [ ] **Step 1: Full curator test suite + regression**

Run: `python3 -m pytest tests/ -q`
Expected: all PASS.

- [ ] **Step 2: Adds-checker dry-run (PRE-ANNOUNCE the API calls)**

There are no pitched curators yet (`promo_latest_status` is empty), so first set one for the
test: confirm the checker reports 0 calls when nothing is pitched -
Run: `python3 scene_intelligence/curator_check_adds.py farewell-single --dry-run`
Expected: "0 pitched curator(s), 0 playlist(s) to check..." and "Added: none". (No API calls
when nothing is pitched.)

- [ ] **Step 3: Live adds-check after a real pitch (when Amir has sent some)**

Once Amir marks a curator `sent` (via the agent's outcome capture), run
`python3 scene_intelligence/curator_check_adds.py farewell-single --dry-run` first to see the
pre-announced call count, then the live form to mark any adds. Confirm it only calls the API
for pitched curators' playlists and writes `added` correctly.

- [ ] **Step 4: Smoke-test the agent curator channel (after a Claude Code restart if needed)**

Run `/promo farewell-single` and ask for the curator channel. Expected: it reads the curator
DB, lists the free verified targets + the proven paid set (skipping suspect/unverified), drafts
a warm IG DM for a free curator and a concise Groover pitch for a paid one (no em/double dash),
with the Farewell Spotify link. Confirm it drafts only, never sends.

- [ ] **Step 5: Final commit (if any cleanup)**

```bash
git add -A
git commit -m "chore(curator): finalize slice 2 (curator pitch channel)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```
