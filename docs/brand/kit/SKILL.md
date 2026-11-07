---
name: brand
description: The Inch of Shadow brand kit. Use it BEFORE making, editing or judging anything visual for Inch of Shadow (Amir Miller) - a cover, a feed post, a story, a reel, a lyric video, a YouTube thumbnail or visualizer, a Spotify Canvas, the sting, a Canva design, an AI image, a HyperFrames video, a shoot brief - and whenever text, colour, a font, a logo, his face or a title goes on screen, even if the user never says "brand". It loads the approved type, sizes, colour moods, safe zones, face rules, motion library, the fixed set per single and the export rules, so the work starts on brand instead of being rebuilt from memory.
argument-hint: [what to make - e.g. "thumbnail for The Deceiver", "release reel", "cover at 4000", "check this frame"]
---

# Inch of Shadow brand kit

Everything here was decided by Amir on renders, ticket by ticket, on the control panel
board. This skill does not hold the decisions, it points at them, so there is one source
of truth. Paths are relative to the project root (`Inch of Shadow/`).

## 1. Read before you touch anything

| Read | When |
|---|---|
| `Inchofshadowcode/docs/brand/frame.md` | Always. The top block (YAML) holds the exact values: fonts, sizes per canvas, colour moods with hexes, safe zones. The text below it holds the rules, the Do / Don't list, Render & Export, and Known Gaps. |
| `Inchofshadowcode/docs/brand/machine.md` | You are not sure which tool makes the object. One owner per object, what stays by hand, and which old tools are out of date. |
| `Inchofshadowcode/docs/brand/formats.md` | The object belongs to a release. It says which objects a single gets (light lane = electronic drops, full lane = songs), their canvas, tool and timing. |
| `Inchofshadowcode/docs/brand/font-library.md` | A release wants its own font, or Amir asks about fonts. His categorised research: every face, where he saw it, where to get it, its status. All potentials; there is no one font for everything. Buy the licence before anything public. |
| `Inchofshadowcode/docs/brand/style-library.md` | A release wants its own look. Seven named looks (S1 Xerox to S7 Pictorialism) it can borrow, one per release. `python3 Inchofshadowcode/print_looks.py <photo> --sheet` shows all of them on one photo; `--look riso` makes one. Local, no AI, safe for photos of him. |
| `Inchofshadowcode/docs/brand/motion-library.md` | Anything that moves: title arrivals T1 to T4, the sting, what is never done, what is allowed. |
| `Inchofshadowcode/docs/brand/positioning.md` (PUBLIC STATUS block first) and `proof.md` | Any word, fact, date or credit appears on screen or in a caption. The songs are not public yet; nothing is claimed that `proof.md` does not list. |
| `Inchofshadowcode/releases/<slug>.json`, block `brand` | The object belongs to a release. `brand` holds that release's choices: `mood` (M2, F...), `accents` (hexes sampled from its artwork), `title_font` (empty = Marcellus), `artwork` (the file that is the released cover). If the block is missing, nothing was chosen yet: propose, let Amir pick, then write the block. Farewell and The Deceiver were made before the mood library; their sampled colours are listed in frame.md under Colors. `Inchofshadowcode/artwork/` holds drafts next to finals (one Deceiver draft misspells the name), so confirm which file is the released cover before sampling from it. |
| `Inchofshadowcode/plans/control-panel/shoot-catalogue.json` | You need a photo of him. 204 tagged edits (framing, face, light, styling, setting, motifs, feeling). The files are on the drive `/Volumes/Intenso/Inch of Shadow photoshoot`; copy a resized working file into your project, never move, rename or edit anything on the drive. |

Get the values from the file, do not retype them from memory, and look at photos before
choosing one (the tags say what is in a photo, not where the calm area for text is):

```bash
K=.claude/skills/brand/scripts
python3 $K/frame_tokens.py                 # everything, as JSON
python3 $K/frame_tokens.py --css M3        # CSS variables for one mood
python3 $K/contact_sheet.py --where "blue hour" --where sunglasses --orientation portrait --out sheet.jpg
```

For stills made with Pillow, `scripts/pillow_type.py` draws the brand face from `frame.md` (Albertus Nova; Marcellus
until that file is owned, the script falls back by itself) with the right
letter-spacing and the one approved shadow, scaled to the canvas (Pillow has no tracking).

If `frame.md` lists something under Known Gaps, it is NOT decided. Say so and ask, do not
fill the gap with a guess.

## 2. Pick the recipe

| Making | Read |
|---|---|
| Release cover, profile images | `references/cover.md` |
| Feed post, carousel, pre-save image | `references/post.md` |
| Reel, story, Shorts, TikTok, Spotify Canvas, lyric reel | `references/reel-story.md` |
| YouTube thumbnail or visualizer | `references/thumbnail.md` |
| The ending of any video | `references/sting.md` |

## 3. How Amir decides

Visual choices he decides by eye and answers with a number: a vague visual question
("hard cut or slow burn?") is hard to answer without seeing it. Everything else (words,
plans, facts about himself, preferences) just ask him, short and numbered; he has said
direct and even abstract questions are fine when they are needed.

Two different situations:
- **He asks for one thing** ("make me a thumbnail for X"): make ONE finished piece. Choose
  the photo, mood and placement yourself from the rules, say in two lines what you chose
  and why, and offer to swap. Do not turn a simple request into a questionnaire.
- **A choice will be reused** (a release's mood or font, a new title arrival, a look for a
  whole campaign), or he says he is unsure:

1. Make 3 or 4 real options on HIS photo or footage, numbered on screen.
2. Show them. He answers "3", or "3 and 4", or tells you what is wrong.
3. Record the decision where it belongs (the board ticket, `frame.md`, the release file).

Test renders for picking can be quick and default quality. Anything he will post goes
through the full export in step 5. Before building options by hand, look at what the tool
already has (HyperFrames has a catalogue of text effects, caption looks, transitions and
blocks; start at the `/hyperframes` skill).

## 4. Check before you show it

```bash
# does it still read at real display size? (safe zone drawn for 9:16)
python3 .claude/skills/brand/scripts/shrink_check.py <image.png> --format reel --text-px 36
# does a composition use only approved colours and fonts?
python3 .claude/skills/brand/scripts/adherence.py <composition.html> [--mood M3] [--allow "#D4B955"]
```

Then look at the result yourself, frame by frame for video: is any text on his face or
head at any moment of the move, is the text inside the safe zone, is there one light idea,
one text effect, does the name close the piece and not open it. The pop rule is the last
check: would a stranger feel something in one second, with no explanation.

## 5. Export

High quality, and each platform gets its own best file (frame.md, Render & Export):

```bash
npx hyperframes render . -q delivery                          # master
npx hyperframes render . -q delivery --resolution landscape-4k   # YouTube and archive
python3 Inchofshadowcode/video_resizer.py --from-hyperframes <project>    # platform files
python3 Inchofshadowcode/artwork_resizer.py <master image>                # stills and covers
```

A file that already fits a platform is passed through untouched. Nothing is upscaled.
Compose each aspect ratio on its own, never crop a reel into a YouTube video.

## Things that went wrong before, so they do not again

- **Electronic-era leftovers.** `docs/brand/VIDEO-BRAND-SESSION-KIT.md`, `CONTROL-PANEL-SETUP-ROADMAP.md` and the files in `videos/IOS-*.md` predate the songs. Never take options, fonts, anti-brand lines or the old lowercase sting from them.
- **One influence is not the look.** Tool, Alex Grey and sacred geometry are one influence among several. The library stays broad; a release borrows one named style on top of the constant brand.
- **Never IOS or IoS.** Write the name in full.
- **The brand face lives in one place:** the `face` block of `frame.md` (family, font file, fallback, licence status). Never type a font name into a tool. HyperFrames bundles none of these faces: `start_video_project.py` copies the files in and `frame_tokens.py --css` writes the `@font-face` lines. **Read the face's `status` line:** while it says TRIAL, everything rendered is a test and nothing made with it gets published; the trial file also lacks punctuation, so handles and titles with an apostrophe are set in the fallback face.
- **HyperFrames render variables only reach the top-level composition.** A reusable asset with variables lives in `index.html`, not in `compositions/`.
- **His files.** Propose before moving, renaming or deleting anything of his. Working copies go in the project or the scratchpad.
- **Copy rules.** No em-dashes, no meta lines, no feedback asks, nothing not in `proof.md`. Voice rules: `Inchofshadowcode/docs/brand/voice.md` (v2): warm, first person, any length (he plans to share more); usually nothing about a song's meaning.
