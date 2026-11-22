# ⚙️ System 102: Release SEO, release-prep skill with strategy / draft / audit (2026-11-16)

Side chat under ⚙️ System. Opus built it; **Fable read it 2026-11-16, found gaps, fixed them (section "Fable gate" below)**.
Nothing was changed live. No Gero content used (the 3-mode structure came from the one read-only look on 11-11).

## What changed

- `.claude/skills/release-prep/SKILL.md` (extended, not a second skill)
  - Step 0: three modes. **strategy** = keyword block per release (search words, text-only words, never list, per platform, timing, do-3-first). **draft** = SC / Bandcamp / YouTube field text, his-voice lines ✍️ for Amir's OK. **audit** = pass/fail per field from files on disk, top 3 fixes first, quoting the bad text.
  - Our rules win over `anthropic-skills:music-platform-seo` (reference only). Never live.
  - Fixed against the 11-11 pass: SoundCloud titles **plain** (no `Inch of Shadow - `); **no fixed 5 tags** (the locked set from the release JSON, BPM tags fine, never the key); **no "--"** in any title format; the YouTube sound line gets no BPM even though the `yt_release.py` [TODO asks for the tempo.
  - New section "Known out-of-date specs": the SC "5 tags / 20 chars" numbers in `seo_platform_specs.json` are unverified (the live HTN tracks carry 8 tags); the script does not enforce them.
- `.claude/skills/release-prep/examples/half-the-night-audit-2026-11-16.json`: the first audit fields file (worked example).
- `release_seo_check.py` (new, repo root): the guards as code. `facts <slug>` prints the only facts copy may use; `check <fields.json>` gives pass/fail per field. Fails on: facts not in the release JSON (ISRC, UPC, catalog no., dates, URLs, BPM numbers; artist links may come from `artist_profile.json`), placeholders, never-list tags and text-only words as tags, the key anywhere, em dash / "--" / en dash, BPM in copy (tags fine, `bpm_in_copy_ok` only when Amir asks), SC artist-prefix titles, "IoS", platform limits. Warns on: another of his labels, "EP" vs the record, YouTube hashtags outside 3-5, duplicate tags. No network code, refuses to write into `releases/`.
- `tests/test_release_seo_check.py`: 77 tests after the Fable gate (40 before). Full suite: **1602 passed**.
- ⚠️ `.claude/` is gitignored, so the SKILL.md and the example file are on disk only, not in git. Committed: the script, the tests, this note.

## 🟣 Fable gate (2026-11-16): first build NOT ready, fixed in the same chat

Fable probed the guard with hard cases. What the Opus build let through, now closed and tested:

| Gap | Now |
|---|---|
| A SoundCloud **secret link** (`/s-...`), the Bandcamp `edit_album` URL and the YouTube Studio URL passed as "facts", because every URL in the release file counted | new top check PRIVATE LINK = fail; URLs under `secret_*` / `edit_*` keys are no longer facts |
| `acid techno`, `tech house`, `#Techno` inside a description passed the never list (exact match only) | never word inside a longer tag = fail; glued hashtag (`#acidtechno`) = warn; hashtags in text are checked |
| Wrong dates passed as `04.12.2026`, `12/04/2026`, `4th of December`, `November 2026`; a wrong bare year passed | all formats checked; bare year = warn |
| Key passed as `F sharp minor`, `E-flat major`, `f minor`; "I Am the Night" failed as a key | spelled-out + the release's own key in any case = fail; "Am" = warn only |
| `TB-303` / `TR-808` failed as "catalog numbers"; `ICR004` passed | only the release's own prefix is checked, any spelling |
| `127 beats per minute` passed; `"bpm_in_copy_ok": "yes"` lifted the rule | caught; only a real `true` lifts it |
| A mistyped fields file (`"tag"`, `"txt"`, empty list) passed silently | INPUT fail; an empty fields file is an error |
| `--out plans/tickets.json` would have overwritten the file | `--out` only creates a new file or replaces an earlier report |
| A field marked "approved" with a different text passed | warn when the approved description is not in it word for word |

In the skill text:
- Two SoundCloud claims were stated as fact that the 11-15 gate had already marked NOT VERIFIED (genre = first tag, no boost from similar tags). Labelled again.
- The Instagram example hashtag was `#acidtechno` (a never word) and "exactly 5" disagreed with `caption_check.py` (3 to 5). Both fixed.
- The DJ-set title line had invented a rule; now only the "--" is gone and it says sets are not decided.
- New "cannot see" list: truth of a sentence, names of people / studios / gear, tag pages, form-only fields, whether Amir approved. Those stay manual in every audit.

Left as it is, on purpose: never-list words in running text pass (the approved HTN text says "trance arp"). The HTN audit result did not change with the stricter guard.

Residual risk, honest: the guard is pattern matching. A wrong label name it does not know, a wrong studio name, or a date written in words ("next Friday") still passes. Amir's read stays the last gate for his-voice text.

## Dry run: audit on Half the Night (as of 11-16, from files on disk)

Full report: side-session notes, `system-102-htn-audit-2026-11-16.md`.
Verdict FAIL: 20 fields, 18 pass, 2 fail (both YouTube drafts, not live yet).

- Top fixes:
  1. YouTube descriptions (both tracks): two [TODO lines still in (sound sentence, lead link). Expected at draft stage.
  2. YouTube descriptions: the [TODO prompt itself asks for "tempo 127.0 BPM", against the 11-11 no-BPM-in-copy rule.
  - Also warned: YouTube hashtags = 2 (`#Electronic #DarkDisco`), PLAYBOOK 5.4 wants 3-5.
- SoundCloud (titles, genre, tags incl. `acid disco` + BPM tags, approved description + Bandcamp `sc-desc` line): all ✅.
- Bandcamp (title, approved about, credits, 8 album tags): all ✅.
- Not on record, so not audited: SC playlist tags, Bandcamp track tags, Bandcamp track abouts.

## Compared with the 11-11 pass

| 11-11 said | 11-16 audit |
|---|---|
| SC titles plain, keep | ✅ plain on both tracks |
| SC tags keep + `acid disco` | ✅ done 11-11, passes the never list |
| SC link block, Bandcamp `sc-desc` first | ✅ done 11-13, URL matches the release file |
| BC tags + `acid disco` | ✅ done 11-11 |
| Do-first 1: BC about first line ✍️ | ❓ not on record as approved or added; the pre-order went public 11-13 with the approved text only (as far as the files say) |
| Do-first 3: SC first line ✍️ | ❓ same, not on record |
| (not covered on 11-11) YouTube | ❌ 2 template issues above |

The 11-11 ✍️ draft lines, run through the guard: dates, ICR-003 and wording all pass, but **every one warns RELEASE TYPE**: the copy says "Half the Night EP", the release file says `release_type: "Single"`. [CHECK] which one is true in Symphonic; the YouTube playlist pick ("Singles & Remixes") also follows that field.

Manual finding the script can't see: Bandcamp credits say "Ambertone **Studio**, Berlin"; `youtube/PLAYBOOK.md` 5.4 and the handle (@ambertone.studios) say "Ambertone **Studios**". [CHECK]

## Ticket updates (for the ⚙️ System chat to merge)

- ⚙️ System 102 "Release SEO skill": **done**. Fable gate passed 2026-11-16 after fixes; Amir approved 2026-11-16 ("Approve", in the side chat).
- NEW proposal (🎵 Release or ⚙️ System, Amir's call): `youtube/tools/yt_release.py` draft prompt asks for the tempo in the description and gives only 2 hashtags. Fix the [TODO wording (no BPM) and the hashtag line (3-5). Outside this ticket's files, so not touched.
- NEW proposal (🎵 Release, HTN): settle `release_type` in `releases/pinocchio-single.json` (Single vs EP) against Symphonic, before any "EP" first line goes live.
- NEW proposal (⚙️ System, small): `seo_platform_specs.json` SoundCloud tag numbers (5 per track, 20 chars) are unverified; mark them unverified or remove.

## Side chat summary, mistakes and lessons (for the System chat, before this chat is deleted)

- Summary: release-prep has strategy / draft / audit, the guard is `release_seo_check.py` (77 tests), the first audit example is Half the Night. Commits `0743b1a` (Opus build) and `ac3718a` (Fable gate fixes). The skill file and its example are on disk only (`.claude/` is gitignored).
- 🐞 Mistakes:
  - The first build called the guard done after tests written from the same head that wrote the code. They proved the happy path only; the Fable probe with hard cases found 9 gaps, one of them a secret link passing as a fact.
  - "Every URL in the release file is a fact" was a shortcut. The release file also holds secret and edit links.
  - Two SoundCloud claims went into the skill as fact although the 11-15 gate had marked them NOT VERIFIED in the source file.
  - The first tag-key pattern read the genre tag `ebm` as a key (caught by the dry run, before the gate).
- 📚 Lessons:
  - A guard script gets a probe with hostile inputs (private data, other formats, near misses, broken input) before it is called ready, not only tests of what it was built for.
  - When a rule is copied from an older file, its evidence label ([NOT VERIFIED], [HYPOTHESIS]) is copied with it.
  - Run the real data through a new checker early: the dry run found a false positive that the unit tests did not.
