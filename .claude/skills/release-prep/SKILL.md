---
name: release-prep
description: Prepare and check the release copy for Inch of Shadow. Three modes - strategy (a keyword block per release), draft (SoundCloud, Bandcamp and YouTube field text, his-voice lines as drafts for Amir's OK) and audit (pass/fail per field, quoting the bad text, top 3 fixes first) - plus premiere contacts and the release checklist. Use when the user mentions releasing a track, uploading a set, release SEO, tags, descriptions, or preparing or checking a release.
argument-hint: [mode] [release slug or name]  (mode = strategy | draft | audit; default draft)
---

# Release Prep for Inch of Shadow

You are preparing or checking a release for Inch of Shadow. Two lanes: songs (guitars and voice, the main line, not public yet) and the electronic lane (dark disco, acid, electro, EBM, Berlin underground). Songs first: when the songs lane opens, every song release runs through this skill.

**Our rules win.** `anthropic-skills:music-platform-seo` and `anthropic-skills:release-platforms` are reference only. Where they disagree with this file, the release JSON or `youtube/PLAYBOOK.md`, this file wins.

**Never live.** This skill writes proposals and local files only. No SoundCloud, Bandcamp, YouTube or Symphonic edits; the uploads chat or Amir pastes. No Chrome for this skill unless the ticket says so.

## The guard script (run it, don't just read the rules)

`release_seo_check.py` in the repo root. Local text checks only, no network, never writes a release file.

```
python3 release_seo_check.py facts <slug>                 # the only facts copy may use
python3 release_seo_check.py check <fields.json>          # pass/fail per field, top 3 fixes first
python3 release_seo_check.py check <fields.json> --out plans/<slug>-seo-<date>.md
```

It **fails** a field on:
- a SoundCloud secret link (`/s-...`) or an edit/admin URL in copy
- a fact not in the release JSON: ISRC, UPC, catalog number, date (any common format), URL, BPM number. Public artist links may also come from `artist_profile.json`
- a placeholder or draft mark left in (`[TODO`, `<link>`, `[CHECK]`, ✍️)
- a tag on `platform_tags.tag_rules.never`, also inside a longer tag (`acid techno`) or as a hashtag in a description; a text-only word used as a tag
- the musical key anywhere (copy and tags, spelled any way)
- an em dash, "--" or an en dash between words
- BPM in copy (tags are fine; only when Amir asks, set `"bpm_in_copy_ok": true`)
- a SoundCloud title with the artist prefix, "IoS", a platform character limit
- a field with no text or tags (a mistyped fields file never passes silently)

It **warns** on: another of his labels, "EP" when the record says Single, a year that is not the release year, a field marked approved that lacks the approved description word for word, a glued hashtag that may hold a never word (`#acidtechno`), "Am" / "A minor" (word or key?), name casing, YouTube hashtags outside 3 to 5, duplicate tags.

It **cannot see**: whether a sentence is true, names of people, studios or gear, whether a tag page exists, form-only fields (Bandcamp top genre, profile location), or whether Amir really approved a text. Those stay manual checks in every audit. Never-list words in running text are allowed on purpose (the rule is about tags; the approved HTN text says "trance arp").

Fields file format: see the docstring at the top of `release_seo_check.py`, and the worked example `examples/half-the-night-audit-2026-11-16.json` next to this file. Mark every line in his voice `"voice": true`; add `"approved": "<date> Amir"` only when he approved that exact text in the main chat.

**Every draft and every audit goes through `check` before Amir sees it.** A FAIL is fixed before showing; never hand him copy the script fails.

## Step 0: Pick the mode

- **strategy**: a keyword block for one release (Step 3A). Before the first draft of a release.
- **draft**: field text per platform (Step 3B). The default.
- **audit**: check what is live or saved (Step 3C). Before release day, after any edit, or when Amir asks "is this right?".

## Step 1: Find or create the release JSON

Check if a release JSON already exists in `releases/` that matches $ARGUMENTS (by title or slug; note that the Half the Night EP lives in `releases/pinocchio-single.json`).
- If it exists, run `python3 release_seo_check.py facts <slug>` and work from that sheet. Don't re-ask for info that's there.
- If it doesn't exist, you'll create one after gathering info (Step 4).
- If `platform_tags.tag_rules` is missing (no `never` list, no `description_words_only`), say so first: the tag rules get locked with Amir before tags are proposed. The script warns about it.

## Step 2: Gather information

Ask the user for any missing details (don't assume):
- **What is it?** Track, remix, DJ set, EP?
- **Title**: full title including featured artists, remixer, venue if a set
- **Genre/vibe**: dark disco, acid, EBM, electro, new wave, post-punk, etc.
- **Tracklist** (if DJ set)
- **BPM** (for tags only) and **key** (for the record only, never in copy or tags)
- **Event/venue** (if live recording)
- **Date** of recording or release
- **Collaborators**: remixer, featured artists, label
- **Is there a video?** YouTube link?
- **Which platforms** is this going on? (SoundCloud, Bandcamp, Spotify, etc.)
- **Is there a premiere planned?** If yes, with whom?

## Step 3A: strategy mode (keyword block)

One block per release, saved as a plan file (`plans/<slug>-seo-<date>.md`), labels as in the 11-11 pass: [OWN DATA] · [OFFICIAL] · [HYPOTHESIS] · [CHECK].

1. **Inputs, our data first** (rule: our archive before the web):
   - the release JSON: `platform_tags` (genre per platform, tags, `tag_rules`), `metadata.description`, titles, ISRC, label, catalog number, date
   - `release_manager/seo_platform_specs.json` (limits; some numbers there are unverified, see "Known out-of-date specs" below)
   - our traffic: Bandcamp referrers (`plans/bandcamp-traffic-plan-2026-10-21.md` and newer), SoundCloud snapshots (`stats_snapshots/`), YouTube stats (`youtube/stats/`)
   - the scene's own words: genre counts in `scene_intelligence/dj_promo_targets.json`
   - the first worked example: `plans/htn-seo-pass-2026-11-11.md`
2. **The block**:
   - **Search words** (go in tags and text): the locked genre set, the city, the label.
   - **Text-only words** (description, never tags): `tag_rules.description_words_only` (for HTN: 303, rolling bass, dark trance atmosphere, house elements).
   - **Never**: `tag_rules.never`, repeated in the block so the draft can't miss it.
   - **Per platform**: SoundCloud genre field, Bandcamp top genre (a preset pick, separate from tags) + free tags, YouTube tags (minor role, PLAYBOOK 5.4).
   - **Timing**: which page Google sees first (for HTN: the Bandcamp pre-order four weeks before SoundCloud), so that field gets written first.
   - **Do these 3 first.**
3. Put the search words into a fields file as `{"platform": "strategy", "field": "tag_keywords", "tags": [...]}` and the text-only words as `{"platform": "strategy", "field": "text_keywords", "text": "..."}`, then run `check`.

## Step 3B: draft mode (field text)

Generate only the platforms this release is going on.

### SoundCloud
- **Title: plain.** `Half the Night`, never `Inch of Shadow - Half the Night`. SC builds the Google title from title + username ("Stream Half the Night by Inch Of Shadow"), so the prefix only repeats the name (11-11 pass, live Farewell page). Same title as the ISRC / Symphonic / Bandcamp metadata. Leave old catalogue titles and permalinks alone.
- DJ sets: `Inch of Shadow @ Event, Description | City Date`. A comma, never "--" or a dash as the separator. The 11-11 pass covered tracks only; whether sets drop the artist name is not decided.
- EP playlist title: the release title; "EP" in it only when the release JSON says EP (the script warns otherwise).
- **Genre field**: the locked SC genre from the release JSON. [NOT VERIFIED: that the genre is "the first tag" and shows on the waveform comes from SC help pages we could not re-read, 403 on 11-11 and 11-15. It only supports keeping the locked genre.]
- **Tags: no fixed count.** Use the locked set from `platform_tags.soundcloud.tags` plus, where they help search: the label (once it may show; HTN: from release day), exact scene phrases that exist as tag pages (`acid disco`, checked live 11-11), BPM tags (`127 bpm`, fine in tags). No near-duplicate genre tags (SC is cited as saying they give no boost, [NOT VERIFIED], same 403). Multi-word tags stay whole. Never the key.
- **Description**: the approved text from `metadata.description`, word for word. Optional first line above it (✍️ draft): release name · date, label from release day (11-11 pass). Then the link block: Bandcamp `?campaign=sc-desc` first, smart link second, two links at most. Human and evocative, NOT a press release.

### Instagram
- **Caption**: keyword-rich, evocative, max 125 chars visible before "...more". No hashtags in caption body. Check it with `python3 caption_check.py`.
- **Hashtags**: 3 to 5, at the end, niche and scene-specific, taken from `platform_tags.hashtags` (e.g., `#darkdisco`, `#italodisco`, `#berlin`). No generic ones. Never a never-list tag. (`caption_check.py` enforces 3 to 5.)

### YouTube
Do NOT invent title options. The title format, description order, credits, tags and hashtags
are fixed in `../youtube/PLAYBOOK.md` section 5.4 (title `Inch of Shadow - Title (Official Audio)`; a plain hyphen, no dash rule broken), and
`python3 ../youtube/tools/yt_release.py <slug> --draft` writes the file from the release
record. Your part is the one sentence on how the track sounds (never what it means) and the
lead link, in place of the [TODO lines. **No BPM and no key in that sentence**, even though the
script's [TODO prompt mentions the tempo. 3 to 5 hashtags.

### Bandcamp (if applicable)
- **About**: the approved text, word for word. Optional first line above it (✍️ draft): release name, date, label, catalog number; pre-order wording only until release day.
- **Track about**: one line naming the release (✍️ draft), e.g. `From the Half the Night EP (ICR-003).`
- **Credits**: real name in the credit box (`Amir Miller`), studio name as in PLAYBOOK 5.4.
- **Tags**: the locked `platform_tags.bandcamp.tags` (darkwave first is fine, no documented order ranking), copied to every track; exact Discover spellings (check the autocomplete). No fixed count.
- Top genre (preset pick) and profile location are form checks, not tags.

### Beatport
- Not used for new releases (bridge plan v2). Skip unless Amir adds it back.

### Every draft
- Write the fields file, run `check`, fix until no FAIL.
- Every line in his voice is shown to Amir in full, marked ✍️, and waits for his OK in the main chat (hard rule 13). Side chats hold drafts only.

## Step 3C: audit mode (pass/fail per field)

1. Collect the current text per field **from files on disk** (release JSON, upload packs, handovers, `yt_release.py` drafts generated in memory). If a field's live text is not on record, say "not on record" and leave it out; never guess. A read-only look at a public page is only for fields the ticket names.
2. Write `<fields>.json` (`"mode": "audit"`, `"as_of"`, `"source"` naming the files), run `check --out`.
3. Report to Amir: the top 3 fixes first, each quoting the bad text, then one line per field (✅ pass / ⚠️ warn / ❌ fail). Then what the script can't see (manual checks: form-only fields, open ✍️ drafts, data conflicts), labelled.

## Step 4: Save to release JSON

Only after Amir's OK, and only the release-copy part. Save generated copy into `releases/<slug>.json` under a `seo_copy` key:

```json
{
  "seo_copy": {
    "generated_at": "2026-03-17T14:30:00",
    "tone": "authentic",
    "soundcloud": {
      "title": "Half the Night",
      "genre": "Dark Disco",
      "description": "...",
      "tags": ["electro", "dark disco", "acid", "EBM", "italo disco", "Berlin"]
    },
    "instagram": {
      "caption": "...",
      "hashtags": ["darkdisco", "acid", "electro", "ebm", "berlin"]
    },
    "youtube": {
      "metadata_file": "youtube/metadata/NN-slug.txt"
    },
    "bandcamp": {
      "about": "...",
      "tags": ["...", "..."]
    },
    "premiere_contacts": [
      {"name": "...", "url": "...", "reason": "..."}
    ]
  }
}
```

Only include platforms that are relevant to this release. Merge into the existing JSON, don't overwrite other fields. Back up the file first (`releases/<slug>.bak.<date>_seo.json`, the existing pattern).

If the release JSON doesn't exist yet, create one with the full schema (copy structure from an existing release in `releases/`).

**Important:** After saving, tell the user the file path and that they can view/edit it in the Release Manager web UI.

## Step 5: Premiere contacts

Read `scene_intelligence/enriched_contacts.json` and find the top 5 premiere/media contacts for this release based on:
- Contacts with sub_type "premiere" or "radio" or "press"
- Genre match (compare release genre to contact's genre_main/genre_sub)
- Relevance score (higher = better)

Save them in the `seo_copy.premiere_contacts` array and also display them to the user with name, platform, URL, and a one-line reason why they're a good fit. Premieres always charge (EUR 30-80) unless verified free in writing.

## Step 6: Release checklist

Based on `plans/seo-strategy.md` section 9, output a tailored checklist for this specific release. Only include platforms the user is releasing on. Include timing notes (e.g., "Spotify pitch needed 31-40 days before release").

If the release JSON already has a `checklist`, don't overwrite it, just show the user what's missing.

## Known out-of-date specs (don't follow these numbers)

- `seo_platform_specs.json` > soundcloud > tags says "max_per_track 5" and "max_chars_per_tag 20". Neither is verified (SC help answers 403 to text readers; 11-11 pass) and the live HTN tracks carry 8 tags. The script does not enforce them.
- Same file, soundcloud > genre_field: "use SoundCloud's exact chart genre names". The 11-11 pass kept the custom genre "Dark Disco" on purpose (scene word, charts not reachable at our size).

## Style rules
- Write like a human, not a press release
- "Inch of Shadow" in full, never IoS
- No em dashes, no "--": commas and full stops (`python3 copy_clean.py` fixes a draft)
- No musical key anywhere. BPM in tags only, in copy only when Amir asks
- No "out now" (goes stale), no feedback asks, no meta lines about the message itself
- Bio mentions: "Inch of Shadow", Berlin, relevant labels (MM Discos, Stereo Society, NaNa Disc)
- Booking email: inchofshadow@gmail.com
- No emojis in copy unless the user requests
- Respect the character limits from `release_manager/seo_platform_specs.json` (except the SC tag numbers above)
- No IG or SC handle into public copy before it is checked on the real profile
