# A Letter for Listeners (Formats-06, spec 2026-09-21)

Amir's own idea. This file is the OBJECT: what it is, what shape it is, how it is set.
**He writes the words.** Nothing here decides the writing, and no part of it may be drafted
for him.

## What it is, in his words

A piece of **poetry** reflecting the period of his life the record comes from. Something for
listeners to engage with, and maybe a **"playbook" of feelings, moods and colours**.

The idea comes from 1990s album inserts that carried "a word to the listeners": a full text,
a song or a poem, set inside the record's own artwork. It can vary from record to record.

**It is NOT a thank-you letter. It is NOT a making-of.** Those were Claude's first
suggestions on 2026-09-20 and Amir dropped them.

## When

**For an EP or an album, never for a single.** Singles are the working mode; the Letter is
what the longer record adds on top of them (`formats.md`, Open, the album wrap).

## The shape

| | |
|---|---|
| Form | Instagram carousel |
| Canvas | 1080x1440 (3:4, fills the grid tile) |
| Slides | title page, then the text. 20 maximum, Instagram's limit |
| Body size | 40px = **14.4pt** on a 390px phone feed. Checked, minimum is 11pt |
| Labels | 32px = 11.6pt. Labels only, never the poem |
| Margins | 96px sides, 150 top and bottom |
| Alignment | **flush left**, the block centred as a whole |
| Colour | one mood from `frame.md`, chosen per record (Look-03) |

**Budget, measured not guessed:** about **17 lines, 119 words a slide**. A whole carousel
holds about 2,000 words after the title page, which is far more than it should ever use.
Re-run `letter_slides.py --budget` if any of the sizes change.

## Why flush left

A poem is written to a left edge. Its line breaks ARE the writing, so the tool keeps every
break exactly as typed and only wraps lines that are too wide. Centring every line makes the
wrap remainders float and turns the page into a greeting card. Both references this is drawn
from set their words flush left.

## The visual rule (Amir, 2026-09-20)

**The Letter takes something from the record's own cover art**, so it speaks the same visual
language. He does not know what yet, maybe a texture. The tool's `--texture` takes the cover
file, blurs it heavily, lifts its contrast so a dark cover does not vanish, dims it and lays
a scrim of the mood's dark over it. The cover is FELT, not repeated.

## How the words are set

Two references, both from his own Look-12 collection:

- **Leonard Cohen's lyrics booklet, c. 1971** (reference 26): letterpress on kraft paper,
  visible imperfections, his name small and brushy. The feeling of a printed object.
- **The Metamorphoses of Ovid, 1993** (reference 35): the title page sets **Castellar with
  Diotima Italic**, and the body is Bembo at about 14 point. This is a BOOK title page, not
  a sleeve, and the Letter is closer to a book than to a cover.

So the title page is built like a book's: a small letterspaced INCH OF SHADOW, the record's
name, a short rule, then the words A Letter for Listeners. The text slides are one calm
column.

The face follows `frame.md`: Albertus Nova since 2026-09-21. No Albertus Nova file is owned
yet, so `letter_slides.py` draws Marcellus today and switches by itself once the file is
saved where `frame.md` expects it. (History: the Ogg trial file, default for one day, could
not draw a comma, an apostrophe, a hyphen or a question mark. Any new face gets that check
before a poem is set in it.)

## The tool

    letter_slides.py letter.txt --title "Record Name" --mood M2 --texture artwork/cover.jpg
    letter_slides.py --budget

The text file is plain UTF-8. **A blank line starts a new slide.** Line breaks inside a
slide are kept. The tool warns when a slide runs over and when the carousel passes 20.

## Rules

- He writes it. Claude sets it, and never drafts the poetry.
- Nothing in it explains a song. He does not explain the songs (`positioning.md`, `voice.md`).
- No em-dashes, no feedback asks, no meta lines (`voice.md`).
- Every fact on screen comes from `proof.md`.
- The publish checklist still applies: location, tags, and the audio renamed.

## Still open, for Amir

- **What it takes from the cover.** A texture is the tool's default guess. It could as
  easily be one colour, a crop, a mark, a grain. His call, per record.
- **Whether the title page carries the record's name or its first line.**
- **Where it goes.** A carousel on the grid, or also a story set, or also inside the
  physical insert if there ever is one.
- **A second face.** Castellar with Diotima Italic is the Ovid pairing; neither is in the
  library yet as a bought file, and neither is in Canva. `font-sources.md` has the links.
