# Inch of Shadow: prompting OpenAI image models (research, 2026-09-27)

What this is: how to write prompts for OpenAI's image models (ChatGPT images and the API), how
to keep the look consistent across one release and across years, what it costs, and the
checklist Claude walks through with Amir before every paid render. Built from three research
passes that used **2026 sources only** (Amir's condition), with the model, shutdown and price
facts re-checked by Claude on OpenAI's own pages the same day. Sources with dates at the end.

It sits on top of what already exists: the brand core `inch_of_shadow_style.txt`, the option
library `options/<kind>/`, `image_generator.py`, and the rule in `machine.md` (say "local" or
"AI" first; prompt shown free first; Amir's go per render; never AI on his face).

---

## 1. The models today (checked 2026-09-27)

| Model | Status | Use it for |
|---|---|---|
| **gpt-image-2.5-sunburst** | new, 2026-09-08; OpenAI: "optimized for quality" | finals |
| **gpt-image-2.5-flare** | new, 2026-09-08; OpenAI: "optimized for speed", quality about gpt-image-2 | drafts, everyday |
| gpt-image-2 | 2026-04-21, now "earlier"; supports Batch (half price) | fallback, bulk |
| gpt-image-1.5 | **shuts down 2026-12-01** (OpenAI deprecations page) | nothing new. **`image_generator.py` still defaults to it: must change** |
| gpt-image-1 | **shuts down 2026-10-23** | nothing |

OpenAI's image guide for new integrations: "Choose Sunburst for workflows where editing
precision matters most, and Flare for fast, high-quality everyday image generation."

**Limits that shape our work** (OpenAI guide and API reference):
- **Sizes:** any size in multiples of 16, ratio between 1:3 and 3:1, longest edge up to 3840.
  Above 2560x1440 is "experimental". For a 3000x3000 cover: render 2048x2048, upscale locally.
- **Batch:** 1 to 10 images per call.
- **References:** up to 16 reference images per request.
- **Masks:** a mask is "entirely prompt-based" and the model "may not follow its exact shape".
- **No seed.** An image can never be reproduced exactly. Consistency has to come from the same
  text, the same references, the same model snapshot, and editing a chosen image.
- **Slow:** up to 2 minutes per image. The 2.5 models are about half as slow as 2.
- **Invisible labels:** every image carries C2PA metadata and an invisible watermark.

## 2. What it costs

- **Official token rates (2.5 Flare, 2.5 Sunburst and 2 are the same):** $30 per 1M image
  output tokens; $8 per 1M image input tokens (reference images); $5 per 1M text input tokens.
- **Per image**, from OpenAI's own table for gpt-image-2 (output only):

| Quality | 1024x1024 | 1024x1536 or 1536x1024 |
|---|---|---|
| low | $0.006 | $0.005 |
| medium | $0.053 | $0.041 |
| high | $0.211 | $0.165 |

- **2.5 per-image cost is not published yet.** OpenAI says its calculator "does not estimate
  GPT Image 2.5 token consumption". The API reports the real tokens of every render, so the log
  will show the true cost after the first renders.
- **References cost extra.** gpt-image-2 reads references at high fidelity, so they "can use more
  input tokens".
- **Realistic session:** 6 low drafts (about $0.04) plus 2 high finals (about $0.42) is about $0.50.
  A release's full set (cover, canvas still, banner, story) is roughly $1 to $3.

## 3. How the model reads a prompt

OpenAI 2026, both guides, confirmed by practitioners:

1. **Format is free.** "Short prompts, descriptive paragraphs, JSON-like structures, instructions,
   and tags can all express the same intent." Pick what is easy to maintain. We use **labelled
   sections**, which OpenAI recommends for anything complex.
2. **Order:** scene, then subject, then key details, then constraints. Also name the **use**
   ("square album cover", "background plate for a composite"). The use sets the level of polish.
3. **Write sentences, not keyword piles.** "8k, masterpiece, trending on artstation" does nothing.
4. **Show, don't name the mood.** For cinematic or night images, "specify scale, atmosphere, and
   color instead of relying on mood words alone". "Cinematic" and "premium" on their own give
   the generic average.
5. **Name visible things:** materials, the light source and its direction, colour, medium, grain.
6. **Camera terms are hints, not guarantees** (OpenAI): "cues for appearance, not a guarantee".
   One named real device or medium often beats a paragraph (one 2026 case replaced 2,300
   characters with one sentence naming a camera).
7. **Say "photograph" when you want a photograph.** Otherwise cinematic prompts drift to
   concept art.
8. **Exclusions work when stated plainly:** "no text, no logos, no watermark". No weights, no
   `--no` flags.
9. **Shorter and clean first.** A base prompt that states the essentials, then one change per
   follow-up. Long prompts where each clause fixes the previous one fall apart.

## 4. The Inch of Shadow prompt, section by section

Every prompt is assembled from the four layers (core, release brief, per-image choices, subject)
into the same labelled sections, in the same order, every time.

```
USE: [what it is and where it goes]
  e.g. "Square album cover artwork for a single. Artwork only, no lettering."

SCENE: [place, time, weather, scale]            <- subject sentence from Amir + setting option

SUBJECT: [the one thing the eye goes to]        <- one focal idea, readable at 64 px

DETAILS:
  Light: [one light idea, source + direction + colour]      <- options/light (L1..L9)
  Medium: [photograph on film / engraving / riso print...]   <- options/medium
  Texture: [grain, dust, colour cast]                        <- options/texture
  Palette: [2-3 colours, plain words + hex]                  <- release mood pair (frame.md)
  Motifs: [at most one or two]                               <- options/motif, release brief

COMPOSITION: [where the subject sits; which area stays quiet for the title and how big]
  e.g. "Subject in the lower third. Keep the top 30% quiet: no strong edges, props or bright
  highlights, reserved for type added later."

BRAND: [inch_of_shadow_style.txt, verbatim, never edited per image]

CONSTRAINTS: No text or letters anywhere. No logos, no watermark. No people unless asked.
  No crowds. [release "never" list]. Not in the style of any named living artist.
```

Why these choices:
- **Title space, not titles.** 2026 models write text well (about 99% in reviews), but the title
  is set by us in the brand face with `pillow_type.py`, for exact spelling, exact font and one
  look across releases. The prompt only reserves a quiet area and says how big it is.
- **Palette:** 2026 sources disagree on hex codes (OpenAI never mentions them). We write both,
  e.g. "platinum white (#D6D1C8) and warm black (#0F0D0C)", and check the colour after rendering.
- **The warm-yellow cast:** "cinematic", "golden hour" and "warm film look" pull in ChatGPT's warm
  default. Use L3 golden hour only when warmth is the point. Otherwise add "neutral white balance".
- **Movements, not artists.** Name a medium, a movement, an era (Art Nouveau botanical plate,
  1980s xerox flyer, pictorialist photograph), never a living artist or a real cover. That is
  both the legal advice (2026) and OpenAI's tightened policy.

## 5. Consistency: one release, and one artist over years

**Inside one release: the anchor method** (agreed across 2026 sources, OpenAI's own advice):
1. **Draft cheap:** 4 to 6 low-quality drafts on Flare. Change **one** thing between rounds.
2. **Anchor:** Amir picks one. It becomes the release's **anchor image**. Its exact prompt,
   model snapshot, size and quality are saved next to it.
3. **Finish:** render the final from the anchor's prompt on Sunburst, high quality.
4. **Derive every other format from the anchor**, not from a fresh prompt: canvas still,
   banner, story, thumbnail. Pass the anchor as a reference with a labelled role
   ("Image 1: style and palette reference. Do not copy its subject."), or edit the anchor itself.
5. **Edits:** "change only X", then a **preserve list** (light, palette, crop, texture), repeated
   on every turn. After 3 or 4 edits, branch from the best saved version rather than keep
   stacking.

**Across releases: fixed vs free** (July's release and January's):

| Stays the same (the brand) | Changes per release |
|---|---|
| the core block, word for word | the mood pair (colours) |
| one light idea per image | the subject and motifs |
| the section order of the prompt | the medium, if the release asks |
| the constraints list | the anchor image |
| the type is added by us, in the brand face | the release "never" list |
| composition logic: one focal point, quiet area for type | |

A label's 2026 advice: artists who change everything each release "signal no identity"; a cover
should work as a thumbnail and still belong to one visual world. Hence a **brand reference
set**: 6 to 10 approved images (anchors of past releases, chosen shoot frames as mood
references, never his face as a generation input). They are passed as labelled style references
when a new release starts.

**The log** (every 2026 brand-system source asks for it): next to each image, a JSON record of
the full prompt, every reference and its role, the model **snapshot**, size, quality, date,
real cost, and Amir's decision (anchor / keep / reject). That makes any image continuable, lets a
new model be tested against the same set, and is the evidence of human authorship a 2026
music lawyer recommends keeping (purely AI images get no copyright; the human work does).

**When OpenAI changes models:** do not switch mid-release. Re-render the brand reference set's
prompts on the new model, compare side by side, then switch. (Model shutdowns force this:
1.5 goes on 2026-12-01.)

## 6. Photos of Amir: the composite route

- **The method.** Never send his face through the model. To put him in a new place: cut him out
  locally (`image_generator.py composite`), have the AI make **only the background plate**
  described with the same light direction and height as his photo, then composite and grade
  locally.
- **It is the professional method in 2026 too.** PetaPixel, 2026-05-10: shoot the person,
  generate the environment, composite; "the lighting has to be consistent with the imagined
  environment."
- **Why the upload route is off by default.** The 2.5 models claim better identity preservation,
  but OpenAI itself warns repeated edits "can still change details you intended to preserve".
  Uploading a photo of him stays off unless Amir says yes for that one photo. His rule.
- **Data (OpenAI API policy, current).** Prompts and images sent to the API are "not used to
  train or improve OpenAI models" unless opted in. They are kept 30 days for abuse monitoring.

## 7. Music-specific

- **Thumbnail test.** The cover must read at 64 px (Spotify's list size). One dominant focal
  idea, big simple shapes. Check every candidate at that size before choosing.
- **Clichés to avoid:** the synthwave grid sun, neon rain crossroads, glitch scan lines, neon
  Tokyo streets. They are the stock looks even 2026 prompt guides still sell.
- **Store rejection triggers** (DistroKid and Apple, 2026): URLs, QR codes, social or streaming
  logos, prices, blurry or rotated images, unlicensed stock, "CD" references, the same artwork
  reused. Any name or title on the cover must match the metadata exactly.
- **Specs:** RGB, 3000x3000 (Apple asks at least 4000 now, see `frame.md`). `artwork_resizer.py`
  handles every size.
- **AI labels:** Apple plans "Made With AI" labels in 2026 (single source). Keeping the human
  part real (his photo, his composite, his type) matters for that too.

## 8. Failure patterns and fixes

| You see | Fix |
|---|---|
| Too clean, corporate, plastic | name a real medium or device; add grain and wear; a style reference image |
| Concept art instead of a photo | say "photograph"; add a photo reference |
| Yellow / warm cast | "neutral white balance"; avoid "cinematic, golden hour" unless intended; correct locally |
| Evenly spaced, synthetic detail; bad reflections | simpler scene; check reflections; no crowds |
| Parts of a long prompt ignored | cut to the core; add the rest in follow-up edits |
| Edits drift (surfaces repaint, light moves) | one change per turn + preserve list; branch from the best after 3-4 edits |
| Style reference copies its subject too | label the role; "do not borrow its subject" |
| Generic mood-board look | fewer adjectives, more visible specifics; one light idea |

## 9. Checklist before every paid render (Claude runs it with Amir)

1. **Local or AI?** Said out loud. AI only for pictures that do not exist and cannot be shot.
2. **No face.** His face is not an input. If he is in it, it is the composite route.
3. **Release brief.** Loaded: the mood pair, motifs, the "never" list, the anchor if there is one.
4. **Prompt.** In the section order, core block verbatim, the use named, the quiet area for type
   sized, the constraints present.
5. **Model and cost.** Flare low for drafts, Sunburst high for finals. Size at 2560 or below.
   The estimated cost is shown.
6. **The prompt is shown free first** (`--print-prompt`), then **Amir's go**, then the render.
7. **Logged.** Every result is saved with its prompt, references, model snapshot, cost and decision.
8. **Judged.** At display size and at 64 px, against `frame.md`: one light idea, nothing random,
   no stray text, no clichés.

## 10. What this changes in the plan (the Imagine page)

- **Model default.** `image_generator.py` moves off gpt-image-1.5 (shuts 2026-12-01) to
  gpt-image-2.5-flare for drafts and gpt-image-2.5-sunburst for finals, after one test render on
  Amir's key. OpenAI says Organization Verification "may" be required.
- **Prompt builder.** It writes the section format above from the four layers. "Show prompt"
  displays exactly what is sent.
- **Anchors and references.** An anchor per release; a brand reference set; references
  passed with labelled roles.
- **Log.** A JSON record per image, with real cost from the API's usage numbers. A monthly
  spend line against Amir's cap.

**Still to test on the first renders:**
- the real 2.5 cost per image;
- whether the 2.5 models work in the multi-turn Responses tool (OpenAI's pages disagree);
- how Flare and Sunburst differ on our kind of image, dark and textural.

---

## Sources (all 2026; OpenAI pages undated but current on 2026-09-27)

OpenAI
- Image generation guide: https://developers.openai.com/api/docs/guides/image-generation (undated, lists 2026-09-08 models)
- Image prompting guide (GPT Image 2.5): https://developers.openai.com/api/docs/guides/image-prompting (undated, 2.5-era)
- Cookbook, image generation models prompting guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide (2026-04-21)
- Introducing ChatGPT Images 2.5: https://openai.com/index/introducing-chatgpt-images-2-5/ (2026-09-08)
- Deprecations: https://developers.openai.com/api/docs/deprecations (gpt-image-1.5 announced 2026-06-02, shutdown 2026-12-01; gpt-image-1 shutdown 2026-10-23)
- Pricing: https://developers.openai.com/api/docs/pricing (undated)
- Your data: https://developers.openai.com/api/docs/guides/your-data (undated)
- ChatGPT Images 2.5 system card: https://deploymentsafety.openai.com/chatgpt-images-2-5 (2026-09-08)

Practice and brand systems
- ImageLayer, brand guidelines for gpt-image-2 (2026-05-05): https://imagelayer.app/blog/gpt-image-2-brand-guidelines-consistency/
- Nightjar, brand visual system for teams (2026-05-09, updated 2026-09-17): https://nightjar.so/blog/build-brand-visual-system-team
- LeftHD, brand guidelines for AI images (2026-09-08): https://lefthd.com/insights/brand-guidelines-for-ai-generated-images/
- ChatGPTImages, reference image prompts (2026-04-28): https://chatgptimages.app/guides/gpt-image-2-reference-image-prompts
- Prompt Architects, colour prompting (2026-09-03): https://prompt-architects.com/blog/563-colour-and-palette-prompting-getting-exact-colours
- fal.ai, prompting gpt-image-2 (2026-04-21): https://fal.ai/learn/tools/prompting-gpt-image-2
- Atlabs, gpt-image-2 prompting guide (2026): https://www.atlabs.ai/blog/the-ultimate-gpt-image-2-prompting-guide-how-to-use-openai%E2%80%99s-best-image-model-2026
- Promptessor, 2.5 prompting guide (2026-09-09): https://promptessor.com/blog/gpt-image-2-5-prompting-guide
- PixVerse, 2.5 review (2026-09-20): https://pixverse.ai/en/blog/gpt-image-2-5-review-and-prompt-guide
- dev.to, one-sentence prompt (2026-09-26): https://dev.to/super_lewis/we-replaced-a-2300-character-image-prompt-with-one-sentence-3hl6
- Popular AI, the warm cast (2026-03-02): https://www.popularai.org/p/chatgpts-piss-filter-why-ai-images
- Everypixel, gpt-image-2 test (2026-05-18): https://research.everypixel.com/gpt-image-2-0/
- AILearningGuides, edits in ChatGPT Images (2026-09-09): https://ailearningguides.com/chatgpt-images-2026-faces-pets-edits/
- PetaPixel, when to use AI (2026-05-10): https://petapixel.com/2026/05/10/a-commercial-photographers-take-on-when-to-use-ai-and-when-not-to/
- Eclipse Records, electronic music visual identity (2026-08-05): https://www.eclipserecs.com/en/blog/eclipse-journal-1/album-art-failing-electronic-music-visual-identity-2026-75
- Echonos, AI album covers (2026-05-08, updated 2026-09-05): https://echonos.ai/blog/ai-album-cover-2026-guide
- ZSky, album cover prompts (2026-03-27): https://zsky.ai/blog/ai-album-cover-prompts-guide
- DontSleepGFX, DistroKid cover rules (2026-01-27): https://dontsleepgfx.com/blogs/marketing/distrokid-cover-art-requirements-what-actually-matters-for-approval
- Entertainment lawyer, AI album cover copyright (2026-02-10): https://entertainmentlawyermiami.com/ai-album-cover-copyright/
- Holland & Knight, Supreme Court on AI authorship (2026-03): https://www.hklaw.com/en/insights/publications/2026/03/the-final-word-supreme-court-refuses-to-hear-case-on-ai-authorship

Caveat: many 2026 practice sources are vendor blogs. Where they agree it is written as advice
here. Single-vendor numbers (reference counts, conformity scores) were left out.
