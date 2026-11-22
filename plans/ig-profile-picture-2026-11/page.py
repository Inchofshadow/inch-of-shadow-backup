"""Builds index.html (the V-tick side page) from previews.json."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
D = json.load(open(HERE / "previews.json"))
INFO = {
 "in-003": ("Starry blue, white shirt", "Songs (main line)",
   "Face fills the circle, lit from the front against a deep blue backdrop: the brightest, cleanest read of the five. Eyes straight to the lens, head level and centred, so it still reads as a face at 40 px."),
 "out-087": ("Golden hour, daylight", "Songs (main line)",
   "The warm, sunny side of the brand. Wide-open eyes to the lens, head centred. Leaf shadows cross the mouth and cheek, so at 40 px it reads busier than the others; the eyes still carry it."),
 "in-125": ("Red gel, fingers at the temples", "Electronic lane (dark disco)",
   "One colour, very high contrast: the red stands out in any feed or story row, even at 40 px. Eyes to the lens, head centred. Club light, so it leans to the electronic lane rather than the songs."),
 "in-189": ("Green gel, open black shirt", "Songs (new wave colour), works for both",
   "A flat green backdrop with a dark shirt around the face, so the head sits in a clear shape. Eyes to the lens, head level. Her 2-star pick. A new-wave colour that is not dark-only."),
 "in-129": ("Black and white, noir", "Songs (post-punk)",
   "The only black-and-white pick: one hard light on the face on full black, so the face pops at any size. The head sits left of centre and the pointing hand is cut off at the right, which reads as a slight lean at 110 px."),
}
GROUPS = [
 ("Finals: night flash family", ["out-037", "out-039", "out-038", "out-036"]),
 ("Finals: memorial evening family", ["out-142", "out-079", "out-077", "out-080", "out-081", "out-082", "out-150", "out-083", "out-152", "out-144", "out-078"]),
 ("Looking at the lens", ["in-003", "out-087", "in-125", "in-189", "in-129"]),
 ("Sunglasses", ["out-027", "in-056", "out-149", "out-190", "out-001"]),
 ("Looking away", ["out-166", "in-193", "in-238", "out-151", "in-023"]),
 ("New: black and white", ["in-124", "in-136", "out-023", "out-050"]),
 ("New: sunglasses", ["out-067", "out-117"]),
 ("New: red and looking away", ["in-138", "in-210", "in-225", "out-011"]),
 ("Newest: sunglasses", ["out-024", "out-076", "out-128", "out-145", "out-049", "out-025"]),
 ("Newest: red light and noir", ["in-211", "in-214", "in-232", "in-135", "in-001"]),
 ("Last round: black tank, full hair", ["out-026", "out-035", "out-129"]),
 ("Last round: more with full hair", ["in-212", "in-209"]),
]
INFO.update({
 "out-027": ("Black and white, hands on the frames", "Songs (post-punk), works for both",
   "Flash, black and white, both hands lifting the sunglasses, tank top. The dark lenses and the white hands make a hard graphic shape that holds at 40 px. Her 1-star set, from the night flash series."),
 "in-056": ("Green shirt, peeking over the frames", "Songs, works for both",
   "Sunglasses lowered with both hands, eyes over the frames, on full black. Cheeky and warm. The dark frames sit right across the middle of the circle, so it reads as a face with sunglasses even at 40 px. Her 2-star pick."),
 "out-149": ("Blue hour, white shirt, head tilted", "Songs (main line)",
   "Sunglasses on, head tilted against the memorial stone, white satin shirt, soft evening light. Calmer and more summery than the night flash shots. Daylight background, so it looks lighter in a dark-mode feed."),
 "out-190": ("Red shirt on granite", "Electronic lane, works for both",
   "Sunglasses on, red shirt against pale granite, soft daylight. The red collar frames the bottom of the circle, the dark lenses the middle: two strong shapes, readable at 40 px. Brighter and warmer than the red gel pick."),
 "out-001": ("Golden hour, polka-dot shirt", "Songs (main line)",
   "Sunglasses on, both hands at the frames, sunny park and sky behind. The playful, daylight side of the brand. Her 2-star pick. The hands and leaves make it busier at 40 px than out-149."),
 "out-166": ("Profile in late warm light", "Songs (main line)",
   "Side profile, looking right, one warm light on the face and the rest in deep shadow, black jacket. Classic and quiet. The nose and beard line carry it at 40 px; leaf shadow on the cheek."),
 "in-193": ("Teal gel, eyes to the side", "Songs (new wave colour)",
   "Teal backdrop, head tilted, eyes off to the left, hands at the collar. One flat colour around a dark head, so the shape is clear at 40 px. A colour nobody else on his grid has. Her 2-star pick."),
 "in-238": ("Red gel, roses, three-quarter", "Electronic lane, songs ballads",
   "Red light, head turned in three-quarter, eyes off left, the top of a rose bouquet at the bottom of the circle. Romantic and dark. Low contrast at 40 px: it turns into a red disc with a face in it. Her 2-star pick."),
 "out-151": ("Sepia profile against stone", "Songs (main line)",
   "Profile to the left, sepia tone, pale stone behind, white shirt. Soft and quiet, the light version of the profile look. The face sits right of centre, the light background makes it look lighter than the rest."),
 "in-023": ("Black and white, hands on the chest", "Songs (post-punk)",
   "Three-quarter face looking left, hands crossed on the chest, one hard light on a dark textured backdrop. Calm and serious. The hands add a second shape under the face that still reads at 110 px. Her 2-star pick."),
})
INFO.update({
 "in-124": ("Black and white, fingers at the eyes", "Songs (post-punk)",
   "Same noir light as in-129, but straight on and centred: eyes to the lens, two fingers framing the face. Very clear at 40 px, white face on full black."),
 "in-136": ("Black and white, sheer shirt, straight on", "Songs (post-punk)",
   "Calm and direct, one hard light, sheer black shirt. The plainest noir option: just the face and the collar on black, so it holds at any size."),
 "out-023": ("Night flash, sunglasses, over the shoulder", "Songs, works for both",
   "Black and white flash, back half turned, looking over the shoulder in sunglasses, tank top and tattoo. Same night series as out-027, a harder and cooler pose."),
 "out-050": ("Black and white profile on the steps", "Songs (main line)",
   "Profile to the right, white tank top, pale stone behind. Looking away, quiet, the light version of noir. Her 1-star set."),
 "out-037": ("Black and white, glasses pulled down", "Songs, works for both",
   "Flash at night, sunglasses pulled down, eyes over the frames, from above. The cheeky sibling of out-027. Her 2-star pick."),
 "out-067": ("Night flash in colour, sunglasses", "Electronic lane, works for both",
   "Colour flash from above on dark paving, sunglasses, sheer black shirt. Club-night feeling. Her 2-star pick."),
 "out-077": ("Sunglasses at sunset, white shirt", "Songs (main line)",
   "Leaning on the memorial at sunset, pink sky and trees behind, head tilted. The warmer twin of your out-149 tick."),
 "out-117": ("Sunglasses behind the gate bars", "Electronic lane, works for both",
   "Red shirt, sunglasses, iron bars on both sides of the face. The bars frame the circle. Darker and greener than out-190."),
 "in-138": ("Dark red light, sheer shirt", "Electronic lane, songs ballads",
   "Low red light on a dark room, face to the lens, the rest falls into black. The moodiest red option, between in-238 and the noir set."),
 "in-210": ("Amber-red profile with a rose", "Songs ballads, electronic lane",
   "Profile to the left in amber-red light, a rose low in the frame, his shadow on the wall. Same series as your in-238 tick, warmer colour. Her 2-star pick."),
 "in-225": ("Red light, roses at the chin", "Electronic lane, songs ballads",
   "Very close, head tilted, eyes to the lens from under the hair, roses at the chin. The photo is so close that the face fills most of the circle. Her 2-star pick."),
 "out-011": ("Red shirt, profile behind the bars", "Songs (main line)",
   "Looking away to the right at dusk, red shirt, a bar on each side. Quiet and wistful, the outdoor answer to out-166."),
})
INFO.update({
 "out-038": ("Night flash in colour, glasses pulled down", "Songs, works for both",
   "Crouching on the kerb at night, sunglasses pulled down, eyes over the frames. The colour twin of your out-037 tick."),
 "out-024": ("Colour flash, over the shoulder", "Electronic lane, works for both",
   "Back turned, sunglasses, looking over the shoulder with a half smile against a metal grid. Warmer and friendlier than out-023, which you removed."),
 "out-076": ("Sunglasses at the memorial, blue sky", "Songs (main line)",
   "Leaning on the curved memorial wall, face turned past the camera, white satin shirt, blue sky and trees. Same evening as your out-077 and out-149 ticks, a different angle."),
 "out-128": ("Red shirt, sunglasses, sitting on granite", "Electronic lane, works for both",
   "Sitting against the pale granite, red shirt, sunglasses, head tilted. Same day as your out-190 tick, a more relaxed pose."),
 "out-145": ("Sunglasses at sunset, hand in pocket", "Songs (main line)",
   "Standing at the memorial edge at sunset, head tilted, white shirt. A looser, wider version of your out-077 tick."),
 "out-049": ("Sunglasses on the steps, white tank", "Songs, works for both",
   "Sitting on the monument steps in a white tank top, head turned to the side, warm dusk light on the stone."),
 "out-025": ("Black and white flash, side on", "Songs (post-punk)",
   "Standing side on in a black tank top, sunglasses, face turned to the lens over the shoulder, iron fence behind. Same night series as your out-027 and out-037 ticks."),
 "in-211": ("Amber-red profile, rose", "Songs ballads, electronic lane",
   "Profile to the left in amber light, shadow on the wall, a rose low in the frame. Sister frame of your in-210 tick, the head turned further away."),
 "in-214": ("Red profile, eyes down, rose", "Songs ballads, electronic lane",
   "Bright red wall, profile to the left with the eyes down, earring catching the light. The head sits right of centre in the circle. Her 2-star pick."),
 "in-232": ("Red light, head bowed over the roses", "Songs ballads, electronic lane",
   "Eyes down to the bouquet, hair falling forward. Quiet and inward, the bowed version of your in-238 tick."),
 "in-135": ("Deep red, crouching, eyes up", "Electronic lane, songs ballads",
   "Crouching in deep red on black, head tipped, eyes to the lens from under the hair. Close to your in-138 tick, more playful."),
 "in-001": ("Black and white, head bowed, white shirt", "Songs (post-punk)",
   "Side on, head bowed, eyes down, one hard light on a glittering black backdrop. Noir like your in-129 tick, but looking away. Her 2-star pick."),
})
INFO.update({
 "out-026": ("Black tank, crouching, black and white", "Songs (post-punk), works for both",
   "Night flash, crouching by the iron fence, sunglasses, the full messy hair lit white against black. Same night as your out-027 and out-037 ticks, a calmer pose."),
 "out-035": ("Black tank on the steps, from above", "Songs (post-punk), works for both",
   "Black and white flash from above, sitting on the steps, sunglasses, face turned to the side. The hair is the brightest thing in the frame."),
 "out-039": ("Black tank, glasses pulled low, colour", "Songs, works for both",
   "Colour flash at night from above, sunglasses pulled low, eyes up to the lens, hair loose all round. The colour sibling of your out-037 tick."),
 "out-129": ("Black tank, crouching, daylight", "Electronic lane, works for both",
   "Colour flash in daylight against a dark fence, sunglasses, finger at the temple, full hair. Warmer and more casual than the night series."),
 "in-212": ("Red profile, rose, full hair", "Songs ballads, electronic lane",
   "Profile to the left on the red wall, a rose low in the frame, the whole head of hair in profile. Same series as your in-210 and in-214 ticks. The head sits right of centre in the circle."),
 "in-209": ("Red light, three-quarter, rose", "Songs ballads, electronic lane",
   "Head turned to the left in three-quarter, his shadow on the wall, rose low in the frame. Between your in-238 and in-210 ticks. Her 2-star pick."),
 "out-142": ("Sunglasses at the memorial, sky behind", "Songs (main line)",
   "Leaning on the memorial wall at sunset, head tilted, white shirt, sky and trees behind. The hair stands out against the light sky."),
 "out-079": ("Sunglasses, arms crossed, violet evening", "Songs (main line)",
   "Straight on against the memorial, arms crossed, white shirt, violet evening light. Same evening as your out-149 and out-145 ticks, the most front-on of them."),
})
INFO["out-166"] = (INFO["out-166"][0], INFO["out-166"][1], INFO["out-166"][2] + " Her photo itself cuts the top of the hair.")
INFO["in-225"] = (INFO["in-225"][0], INFO["in-225"][1], INFO["in-225"][2] + " Her photo itself cuts the top of the hair.")
INFO.update({
 "out-036": ("Black tank on the steps, head down", "Songs (post-punk), works for both",
   "Same minute as out-037 (20:45), black and white flash from above, sunglasses on, head tipped far down, the hair falling forward. The hidden, moody frame of the series."),
 "out-080": ("Arms crossed, violet evening", "Songs (main line)",
   "One second after out-079: arms crossed, face to the lens, head level. A touch less stern than 079."),
 "out-081": ("Lowering the sunglasses at the memorial", "Songs, works for both",
   "The 037 move in the memorial family: both hands lowering the glasses, head tipped down, white satin shirt, sky and trees behind. Playful and candid."),
 "out-082": ("Framing the camera with his fingers", "Songs (main line)",
   "No sunglasses, fingers making a frame at the lens, eyes to the lens through it. Playful and sly. The hands sit above the head in the circle."),
 "out-150": ("Finger frame, wide", "Songs (main line)",
   "The wider take of out-082: finger frame at the camera, head tilted, eyes to the lens, more sky around."),
 "out-083": ("No sunglasses, direct look, memorial", "Songs (main line)",
   "Same evening, glasses off, eyes to the lens, steady, head level, mouth closed. Open and soft: the only straight eye contact of the family."),
 "out-152": ("No sunglasses, leaning, soft look", "Songs (main line)",
   "Glasses off, leaning on the wall, head slightly tilted, eyes to the lens. Soft and searching, sky behind the full hair."),
 "out-144": ("Sunglasses, leaning, warm and easy", "Songs (main line)",
   "Leaning on the memorial wall with sunglasses, head tilted, a warm and easy face. Between 142 and 145."),
 "out-078": ("Sunglasses, pink clouds, trees", "Songs (main line)",
   "Leaning on the wall, hand in pocket, sunglasses, pink clouds and dark trees behind. Calm, cool, elegant."),
})
cards = []
for gname, ids in GROUPS:
  cards.append(f'<h2 class="group">{gname}</h2>')
  for k in ids:
    name, lane, why = INFO[k]
    d = D[k]
    cards.append(f'''
<article class="card" data-id="{k}">
  <div class="top"><h2>{name}</h2><span class="id">{k} · her rating {d["rating"]}★</span></div>
  <div class="row">
      <figure class="full"><img src="{d["full"]}" alt="Full photo {k} on warm black" data-zoom="zoom/full_{k}.jpg" tabindex="0"><figcaption>Whole photo</figcaption></figure>
      <div class="previews">
        <div class="ig light"><img class="c110" src="{d["c110"]}" alt="Circle crop {k}" data-zoom="zoom/crop_{k}.jpg" data-round="1" tabindex="0"><img class="c40" src="{d["c40"]}" alt=""><span>IG light</span></div>
        <div class="ig dark"><img class="c110" src="{d["c110"]}" alt="Circle crop {k}" data-zoom="zoom/crop_{k}.jpg" data-round="1" tabindex="0"><img class="c40" src="{d["c40"]}" alt=""><span>IG dark</span></div>
      </div>
  </div>
  <p class="lane">{lane}</p>
  <p class="feel">Feeling: {d["tags"]["feeling"]}</p>
  <p class="why">{why}</p>
  <p class="file">{d["edit"]}<br>Upload file: plans/ig-profile-picture-2026-11/upload_1080_{k}.jpg</p>
  <div class="acts"><button class="tick" id="tick-{k}" aria-pressed="false"><span class="v">V</span><span class="lbl">Tick this one</span></button>
  <button class="drop" id="drop-{k}" aria-pressed="false"><span class="v">X</span><span class="lbl">Remove</span></button></div>
</article>''')
MOODS = [
 ("Cool and playful, night flash", "Fun with a secret. Rock and roll, a bit naughty, never sad.",
  [("out-027", "playful, hidden, mischievous"), ("out-037", "cheeky, sly, caught"), ("out-039", "cheeky, direct, playful"), ("out-067", "calm, cool, laid back")]),
 ("Cool confidence, memorial at dusk and daylight", "From charming (head tilted, slight smile) to closed (arms crossed, mouth flat). The glasses hide the eyes, so the feeling sits in the tilt and the mouth.",
  [("out-149", "charming, easy"), ("out-145", "easy, warm"), ("out-142", "cool, elegant"), ("out-190", "cool, elegant"), ("out-077", "guarded, cool, stylish"), ("out-079", "guarded, stern"), ("out-049", "distant, cool, elegant")]),
 ("Longing, noir and red", "Roses, profiles, eyes down: the singer thinking of someone. Only in-129 and in-138 look at you.",
  [("in-129", "pointed, direct, noir"), ("in-138", "brooding, dark"), ("in-238", "wistful, romantic"), ("in-209", "wistful, romantic"), ("in-210", "pensive, romantic"), ("in-211", "pensive, romantic"), ("in-212", "distant, romantic"), ("in-214", "pensive, romantic"), ("in-232", "tender, inward"), ("out-166", "pensive, classic, quiet")]),
]
mood_html = []
for title, line, items in MOODS:
    chips = "".join(f'<figure class="chip"><img src="{D[k]["c110"]}" alt="Circle crop {k}" data-zoom="zoom/crop_{k}.jpg" data-round="1" tabindex="0"><figcaption><b>{k}</b><br>{f}</figcaption></figure>' for k, f in items)
    mood_html.append(f'<div class="mood"><h3>{title}</h3><p>{line}</p><div class="chips">{chips}</div></div>')
ANALYSIS = f'''<section class="analysis" aria-labelledby="an-h">
  <h2 class="group" id="an-h">Your 21 picks, by feeling</h2>
  <p class="intro">Feelings from the shoot catalogue's face tags (read eyes first, at full size), grouped by mood. Tap a circle to open it large.</p>
  {"".join(mood_html)}
  <div class="mood"><h3>What the whole set says</h3>
  <ul>
    <li>Two moods stayed: cool and playful (the 11 with sunglasses) and romantic and inward (the 10 noir and red).</li>
    <li>Everything bright or plain went (green and teal gel, golden sun, plain straight-on black and white, most over-the-shoulder and behind-bars poses). Mystery and attitude won over openness.</li>
    <li>The mouth is closed in all 21, and only 4 look into the lens with open eyes (in-129, in-138, out-037, out-039). You kept a little distance.</li>
    <li>For the circle: sunglasses = fun, cool, a bit dangerous. Red and profile = songs about love and longing, closest to the sung songs. out-037 and out-039 are the only picks that are playful and make real eye contact.</li>
  </ul></div>
</section>'''
TOURNEY = json.load(open(HERE / "tourney" / "entrants.json"))
TOUR = f'''<section class="tour" aria-labelledby="tr-h">
  <h2 class="group" id="tr-h">Tournament: out-037 effects</h2>
  <p class="intro">Your pick, out-037: as it is against 6 clearly different effect versions from your saved mixer settings (near-twins left out). Round one ended with 037 plain beating 039, 142 and 079. Two at a time, tap the one you would rather see as your profile picture. The winner stays and meets the next one. {len(TOURNEY) - 1} taps to a champion. Your progress is saved.</p>
  <p class="status" id="t-status">Loading…</p>
  <div class="tmatch" id="t-match"></div>
  <div class="tdone" id="t-done" hidden></div>
  <div class="acts"><button class="drop" id="t-restart"><span class="v">↺</span><span class="lbl">Start over</span></button></div>
</section>'''
LOOKS_META = json.load(open(HERE / "looks" / "looks.json"))
MIX_PHOTOS = ["out-037", "out-039", "out-142", "out-079", "out-077"]
look_opts = '<option value="">None</option>' + "".join(f'<option value="{n}">{v["code"]} {v["name"]}: {v["what"]}</option>' for n, v in LOOKS_META.items())
mix_thumbs = "".join(f'<button class="mph" data-ph="{k}" aria-pressed="false"><img src="{D[k]["c40"]}" alt="">{k}</button>' for k in MIX_PHOTOS)
MIXER = f'''<section class="mixer" aria-labelledby="mx-h">
  <h2 class="group" id="mx-h">Effects mixer</h2>
  <p class="intro">Your 5 finalists through our own looks (print_looks.py: local, no AI, your face is never redrawn). Pick a photo, tap a look in the strip (that is look A), then slide its strength. Look B is laid over look A (a blend of the two, not B applied on top of A). Fine textures like halftone, dither and ASCII disappear at 40 px; strong colour looks hold. Tap the big square to see it large.</p>
  <div class="mphs" role="group" aria-label="Photo">{mix_thumbs}</div>
  <div class="mstrip" id="m-strip" role="group" aria-label="Look A, tap to pick"></div>
  <div class="mgrid">
    <div class="mstage" id="m-stage" tabindex="0" aria-label="Preview, tap to enlarge"></div>
    <div class="mctl">
      <label for="m-a">Look A</label><select id="m-a">{look_opts}</select>
      <label for="m-wa">Strength A <output id="m-wa-o">100%</output> <span class="hint" id="m-wa-h"></span></label><input type="range" id="m-wa" min="0" max="100" value="100">
      <label for="m-b">Look B</label><select id="m-b">{look_opts}</select>
      <label for="m-wb">Strength B <output id="m-wb-o">50%</output> <span class="hint" id="m-wb-h"></span></label><input type="range" id="m-wb" min="0" max="100" value="50">
      <label for="m-bm">B blend</label><select id="m-bm"><option value="normal">Normal</option><option value="multiply">Multiply</option><option value="screen">Screen</option><option value="overlay">Overlay</option><option value="soft-light">Soft light</option><option value="color">Colour only</option></select>
      <div class="ig light mig"><div class="stk c110" data-stk></div><div class="stk c40" data-stk></div><span>IG light</span></div>
      <div class="ig dark mig"><div class="stk c110" data-stk></div><div class="stk c40" data-stk></div><span>IG dark</span></div>
      <div class="acts"><button class="tick" id="m-save"><span class="v">V</span><span class="lbl">Save this setting</span></button><button class="drop" id="m-reset"><span class="v">0</span><span class="lbl">Reset</span></button></div>
      <p class="status" id="m-status">Nothing saved yet.</p>
    </div>
  </div>
  <div id="m-saved" class="msaved"></div>
</section>'''
html = f'''<title>Profile Picture Picks</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Jost:wght@300;400;500&display=swap">
<style>
/* Layout: one column of option cards, each = whole photo + circles at real IG size on light and dark */
:root {{ --bg:#0F0D0C; --card:#1a1715; --fg:#D6D1C8; --dim:#9a948b; --line:#2b2724; --tick:#D6D1C8;
  --display:"Marcellus", Georgia, serif; --body:"Jost", system-ui, sans-serif; color-scheme:dark; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--body); font-weight:300;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:24px 48px; }}
main {{ max-width:760px; margin:0 auto; display:grid; gap:20px; }}
h1 {{ font-family:var(--display); font-weight:400; font-size:1.7rem; letter-spacing:.05em; margin:0; text-wrap:balance; }}
.intro {{ color:var(--dim); line-height:1.55; margin:0; max-width:65ch; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:16px; display:grid; gap:12px; min-width:0; }}
.card.on {{ border-color:var(--tick); }}
.top {{ display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between; gap:4px 12px; }}
h2.group {{ font-family:var(--display); font-weight:400; font-size:1.35rem; letter-spacing:.06em; margin:16px 0 0; border-bottom:1px solid var(--line); padding-bottom:8px; }}
.card h2 {{ font-family:var(--display); font-weight:400; font-size:1.2rem; letter-spacing:.04em; margin:0; }}
.id {{ font-size:.8rem; color:var(--dim); letter-spacing:.06em; }}
.row {{ display:flex; flex-wrap:wrap; gap:16px; align-items:center; }}
.full {{ margin:0; width:220px; max-width:100%; }}
.full img {{ display:block; width:100%; aspect-ratio:1; }}
figcaption, .ig span {{ font-size:.72rem; color:var(--dim); letter-spacing:.08em; text-transform:uppercase; margin-top:6px; }}
.previews {{ display:flex; flex-wrap:wrap; gap:12px; }}
.ig {{ display:grid; grid-template-columns:auto auto; align-items:end; gap:10px 14px; padding:14px; border-radius:4px; }}
.ig span {{ grid-column:1 / -1; margin:0; }}
.ig.light {{ background:#ffffff; }} .ig.light span {{ color:#737373; }}
.ig.dark {{ background:#000000; }}
.c110 {{ width:110px; height:110px; border-radius:50%; display:block; }}
.c40 {{ width:40px; height:40px; border-radius:50%; display:block; }}
.lane {{ margin:0; font-weight:500; letter-spacing:.03em; }}
.why {{ margin:0; line-height:1.55; max-width:65ch; }}
.file {{ margin:0; font-size:.78rem; color:var(--dim); overflow-wrap:anywhere; }}
.acts {{ display:flex; flex-wrap:wrap; gap:10px; }}
.tick, .drop {{ display:flex; align-items:center; gap:10px; background:transparent; color:var(--fg); border:1px solid var(--line);
  border-radius:999px; padding:8px 16px 8px 8px; font:inherit; cursor:pointer; }}
.tick .v, .drop .v {{ width:28px; height:28px; border-radius:50%; border:1px solid var(--dim); display:grid; place-items:center; font-family:var(--display); color:transparent; }}
.tick[aria-pressed="true"] {{ border-color:var(--tick); }}
.tick[aria-pressed="true"] .v {{ background:var(--tick); color:var(--bg); border-color:var(--tick); }}
.drop[aria-pressed="true"] .v {{ background:#8a3b2f; color:var(--fg); border-color:#8a3b2f; }}
.card.gone {{ opacity:.45; }}
.card.gone .row, .card.gone .why, .card.gone .file, .card.gone .lane, .card.gone .tick {{ display:none; }}
.tick:focus-visible, .drop:focus-visible {{ outline:2px solid var(--fg); outline-offset:2px; }}
[data-zoom] {{ cursor:zoom-in; }}
[data-zoom]:focus-visible {{ outline:2px solid var(--fg); outline-offset:2px; }}
.zoom {{ position:fixed; inset:0; z-index:50; background:rgba(8,7,6,.96); overflow:auto; display:grid; place-items:center;
  padding:calc(48px + env(safe-area-inset-top, 0px)) max(16px, env(safe-area-inset-right, 0px)) calc(16px + env(safe-area-inset-bottom, 0px)) max(16px, env(safe-area-inset-left, 0px)); }}
.zoom[hidden] {{ display:none; }}
.zoom img {{ max-width:100%; max-height:calc(100vh - 80px); cursor:zoom-in; display:block; }}
.zoom img.round {{ border-radius:50%; }}
.zoom.big {{ place-items:start; }}
.zoom.big img {{ max-width:none; max-height:none; width:auto; cursor:zoom-out; }}
.zoom .close {{ position:fixed; top:calc(10px + env(safe-area-inset-top, 0px)); right:max(12px, env(safe-area-inset-right, 0px)); z-index:51;
  background:var(--card); color:var(--fg); border:1px solid var(--line); border-radius:999px; padding:8px 16px; font:inherit; cursor:pointer; }}
.zoom .hint {{ position:fixed; top:calc(16px + env(safe-area-inset-top, 0px)); left:max(16px, env(safe-area-inset-left, 0px)); font-size:.75rem; color:var(--dim); }}
.feel {{ margin:0; font-size:.85rem; color:var(--dim); font-style:italic; }}
.analysis {{ display:grid; gap:14px; }}
.mood {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:14px 16px; display:grid; gap:8px; min-width:0; }}
.mood h3 {{ font-family:var(--display); font-weight:400; font-size:1.05rem; letter-spacing:.04em; margin:0; }}
.mood p, .mood ul {{ margin:0; line-height:1.5; max-width:65ch; }}
.mood ul {{ padding-left:1.1em; display:grid; gap:6px; }}
.chips {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(96px, 1fr)); gap:12px; }}
.chip {{ margin:0; display:grid; justify-items:center; gap:6px; text-align:center; }}
.chip img {{ width:72px; height:72px; border-radius:50%; display:block; }}
.chip figcaption {{ font-size:.72rem; color:var(--dim); line-height:1.3; }}
.chip b {{ color:var(--fg); font-weight:500; }}
.filters {{ display:flex; flex-wrap:wrap; gap:8px; }}
.flt {{ background:transparent; color:var(--fg); border:1px solid var(--line); border-radius:999px; padding:6px 14px; font:inherit; font-size:.85rem; cursor:pointer; }}
.flt[aria-pressed="true"] {{ background:var(--fg); color:var(--bg); border-color:var(--fg); }}
.flt:focus-visible {{ outline:2px solid var(--fg); outline-offset:2px; }}
main.f-v .card:not(.on), main.f-nx .card.gone {{ display:none; }}
main.f-v h2.group:not(#an-h), main.f-v .analysis {{ display:none; }}
.tour {{ display:grid; gap:14px; }}
.tmatch {{ display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:14px; }}
.tcard {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px; display:grid; gap:10px; min-width:0; justify-items:center; text-align:center; }}
.tcard.champ {{ border-color:var(--fg); }}
.tbig {{ width:min(100%, 220px); aspect-ratio:1; border-radius:50%; display:block; }}
.tsm {{ display:flex; gap:8px; flex-wrap:wrap; justify-content:center; }}
.tsm .ig {{ padding:10px; }}
.tlabel {{ font-size:.85rem; color:var(--dim); min-height:2.6em; }}
.tpick {{ background:var(--fg); color:var(--bg); border:0; border-radius:999px; padding:10px 22px; font:inherit; font-weight:500; cursor:pointer; }}
.tpick:focus-visible {{ outline:2px solid var(--fg); outline-offset:3px; }}
.tdone {{ display:grid; gap:12px; justify-items:center; text-align:center; background:var(--card); border:1px solid var(--fg); border-radius:6px; padding:16px; }}
.tdone ol {{ text-align:left; margin:0; padding-left:1.4em; display:grid; gap:4px; }}
@media (max-width:560px) {{ .tbig {{ width:min(100%, 150px); }} .tsm .c110 {{ width:72px; height:72px; }} }}
.mixer {{ display:grid; gap:14px; }}
.mphs {{ display:flex; flex-wrap:wrap; gap:8px; }}
.mph {{ display:flex; align-items:center; gap:8px; background:transparent; color:var(--fg); border:1px solid var(--line); border-radius:999px; padding:4px 12px 4px 4px; font:inherit; font-size:.85rem; cursor:pointer; }}
.mph img {{ width:32px; height:32px; border-radius:50%; }}
.mph[aria-pressed="true"] {{ border-color:var(--fg); background:var(--card); }}
.mgrid {{ display:grid; grid-template-columns:minmax(0, 360px) minmax(0, 1fr); gap:16px; align-items:start; }}
@media (max-width:640px) {{ .mgrid {{ grid-template-columns:minmax(0, 1fr); }} }}
.mstage, .stk {{ position:relative; overflow:hidden; background:#000; }}
.mstage {{ width:100%; aspect-ratio:1; cursor:zoom-in; }}
.mstage img, .stk img {{ position:absolute; inset:0; width:100%; height:100%; display:block; }}
.mstage.full {{ position:fixed; z-index:60; inset:0; margin:auto; width:min(94vw, 94vh); height:auto; cursor:zoom-out; box-shadow:0 0 0 100vmax rgba(8,7,6,.96); }}
.stk.c110 {{ width:110px; height:110px; border-radius:50%; }}
.stk.c40 {{ width:40px; height:40px; border-radius:50%; }}
.mctl {{ display:grid; gap:8px; min-width:0; }}
.mctl label {{ font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:var(--dim); }}
.mctl select {{ width:100%; background:var(--card); color:var(--fg); border:1px solid var(--line); border-radius:4px; padding:8px; font:inherit; }}
.mctl input[type=range] {{ width:100%; accent-color:var(--fg); }}
.mig {{ justify-self:start; }}
.mstrip {{ display:flex; gap:10px; overflow-x:auto; padding-bottom:6px; }}
.mlook {{ flex:0 0 auto; display:grid; justify-items:center; gap:4px; width:72px; background:transparent; color:var(--dim); border:1px solid transparent; border-radius:6px; padding:4px; font:inherit; font-size:.68rem; line-height:1.2; cursor:pointer; text-align:center; }}
.mlook img {{ width:56px; height:56px; border-radius:50%; display:block; }}
.mlook[aria-pressed="true"] {{ border-color:var(--fg); color:var(--fg); }}
.mctl input[type=range]:disabled {{ opacity:.35; }}
.hint {{ text-transform:none; letter-spacing:0; color:var(--dim); }}
.msaved {{ display:grid; gap:8px; }}
.msv {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; background:var(--card); border:1px solid var(--line); border-radius:6px; padding:8px 12px; }}
.msv button {{ background:transparent; color:var(--fg); border:1px solid var(--line); border-radius:999px; padding:4px 12px; font:inherit; font-size:.8rem; cursor:pointer; }}
.status {{ font-size:.8rem; color:var(--dim); margin:0; }}
</style>
<main id="main" class="f-nx">
  <h1>Profile picture picks</h1>
  <p class="intro">Fifty-six of her photos from the July and August shoots, all clearly different from the current picture (set 17 April). The tournament, the effects mixer and the finals come first: the night flash family (037, 039) and the memorial evening family (142, 079, 077) with every sibling from the shoot. Your 21 V picks are analysed by feeling below. Every circle shows the full hair with room above it, at the sizes Instagram draws: 110 px on your profile, 40 px next to comments and in the story row. Tick V to keep, X to remove (Show removed too brings them back). Tap any photo or big circle to open it large.</p>
  <p class="status" id="status">Loading your ticks…</p>
  <div class="filters" role="group" aria-label="Show">
    <button class="flt" id="f-nx" aria-pressed="true">Open picks</button>
    <button class="flt" id="f-v" aria-pressed="false">Only my V</button>
    <button class="flt" id="f-all" aria-pressed="false">Show removed too</button>
  </div>
  {TOUR}
  {MIXER}
  {ANALYSIS}
  {"".join(cards)}
</main>
<script>
(async () => {{
  const E = {json.dumps(TOURNEY)};
  const $ = id => document.getElementById(id);
  const byKey = Object.fromEntries(E.map(e => [e.key, e]));
  const img = k => "tourney/" + k + ".jpg";
  const fresh = () => ({{ order: E.map(e => e.key), champ: 0, next: 1, beaten: [], done: false }});
  let T = fresh(), db = null;
  const card = (k, isChamp) => {{
    const c = document.createElement("div"); c.className = "tcard" + (isChamp ? " champ" : "");
    const tag = document.createElement("div"); tag.className = "tlabel"; tag.textContent = (isChamp && T.next > 1 ? "Holding: " : "") + byKey[k].label;
    const big = document.createElement("img"); big.className = "tbig"; big.src = img(k); big.alt = byKey[k].label; big.dataset.zoom = img(k); big.dataset.round = "1"; big.tabIndex = 0;
    const sm = document.createElement("div"); sm.className = "tsm";
    ["light", "dark"].forEach(m => {{ const box = document.createElement("div"); box.className = "ig " + m;
      [110, 40].forEach(px => {{ const i = document.createElement("img"); i.className = "c" + px; i.src = img(k); i.alt = ""; box.appendChild(i); }}); sm.appendChild(box); }});
    const b = document.createElement("button"); b.className = "tpick"; b.textContent = "This one"; b.addEventListener("click", () => pick(k));
    c.append(big, tag, b, sm); return c;
  }};
  const render = () => {{
    const m = $("t-match"), d = $("t-done"); m.textContent = "";
    if (T.done) {{
      m.hidden = true; d.hidden = false; d.textContent = "";
      const w = T.order[T.champ];
      const h = document.createElement("h3"); h.textContent = "Champion"; h.className = "group";
      const big = document.createElement("img"); big.className = "tbig"; big.src = img(w); big.alt = byKey[w].label;
      const l = document.createElement("p"); l.textContent = byKey[w].label;
      const ol = document.createElement("ol"); [...T.beaten].reverse().forEach(x => {{ const li = document.createElement("li"); li.textContent = byKey[x.key].label + " (lost to " + byKey[x.by].label + ")"; ol.appendChild(li); }});
      const p2 = document.createElement("p"); p2.className = "intro"; p2.textContent = "Last to fall is listed first: those came closest.";
      d.append(h, big, l, p2, ol);
      $("t-status").textContent = "Done. Tell Claude in the chat and the 1080 upload file gets made with this exact setting.";
      return;
    }}
    m.hidden = false; d.hidden = true;
    m.append(card(T.order[T.champ], true), card(T.order[T.next], false));
    $("t-status").textContent = "Match " + T.next + " of " + (T.order.length - 1) + ".";
  }};
  const save = async () => {{ if (!db) return; try {{ await db.doc("tournament/run37").set(Object.assign({{}}, T, {{ at: new Date().toISOString() }})); }} catch (e) {{ $("t-status").textContent = "Not saved: " + (e && e.message || "error"); }} }};
  const pick = k => {{
    const a = T.order[T.champ], b = T.order[T.next];
    if (k === a) T.beaten.push({{ key: b, by: a }}); else {{ T.beaten.push({{ key: a, by: b }}); T.champ = T.next; }}
    T.next += 1; if (T.next >= T.order.length) T.done = true;
    render(); save(); document.getElementById("tr-h").scrollIntoView({{ block: "start" }});
  }};
  $("t-restart").addEventListener("click", () => {{ T = fresh(); render(); save(); }});
  render();
  try {{ db = await claude.use("db"); }} catch (e) {{ db = null; }}
  if (!db) {{ $("t-status").textContent += " (progress is not saved outside claude.ai)"; return; }}
  try {{ const s = await db.doc("tournament/run37").get(); const v = s && s.data && s.data();
    if (v && Array.isArray(v.order) && v.order.length === E.length && v.order.every(k => byKey[k])) {{ T = {{ order: v.order, champ: v.champ, next: v.next, beaten: v.beaten || [], done: !!v.done }}; render(); }} }} catch (e) {{}}
}})();
</script>
<script>
(async () => {{
  const META = {json.dumps(LOOKS_META)};
  const $ = id => document.getElementById(id);
  const S = {{ ph: "out-037", a: "riso", wa: 100, b: "", wb: 50, bm: "normal" }};
  const strip = $("m-strip");
  const looks = ["", ...Object.keys(META)];
  looks.forEach(l => {{ const bt = document.createElement("button"); bt.className = "mlook"; bt.dataset.look = l;
    const im = document.createElement("img"); im.alt = ""; im.loading = "lazy"; bt.appendChild(im);
    bt.appendChild(document.createTextNode(l ? META[l].name : "No look"));
    bt.addEventListener("click", () => {{ S.a = l; if (l && S.wa === 0) S.wa = 100; render(); }}); strip.appendChild(bt); }});
  const stacks = [$("m-stage"), ...document.querySelectorAll("[data-stk]")];
  stacks.forEach(s => {{ for (let i = 0; i < 3; i++) s.appendChild(document.createElement("img")); s.children[0].alt = "Preview"; s.children[1].alt = ""; s.children[2].alt = ""; }});
  const src = (ph, look) => "looks/" + ph + "/" + (look || "original") + ".jpg";
  const name = l => l ? META[l].code + " " + META[l].name : "none";
  const label = s => s.ph + ": " + (s.a ? name(s.a) + " " + s.wa + "%" : "no look") + (s.b ? " + " + name(s.b) + " " + s.wb + "% (" + s.bm + ")" : "");
  const render = () => {{
    stacks.forEach(s => {{ const [o, a, b] = s.children;
      o.src = src(S.ph); a.hidden = !S.a; b.hidden = !S.b;
      if (S.a) {{ a.src = src(S.ph, S.a); a.style.opacity = S.wa / 100; }}
      if (S.b) {{ b.src = src(S.ph, S.b); b.style.opacity = S.wb / 100; b.style.mixBlendMode = S.bm; }} }});
    $("m-a").value = S.a; $("m-b").value = S.b; $("m-wa").value = S.wa; $("m-wb").value = S.wb; $("m-bm").value = S.bm;
    $("m-wa-o").textContent = S.wa + "%"; $("m-wb-o").textContent = S.wb + "%";
    document.querySelectorAll(".mph").forEach(b => b.setAttribute("aria-pressed", b.dataset.ph === S.ph ? "true" : "false"));
    strip.querySelectorAll(".mlook").forEach(bt => {{ bt.firstChild.src = src(S.ph, bt.dataset.look); bt.setAttribute("aria-pressed", bt.dataset.look === S.a ? "true" : "false"); }});
    $("m-wa").disabled = !S.a; $("m-wb").disabled = !S.b;
    $("m-wa-h").textContent = S.a ? "" : "(pick look A first)"; $("m-wb-h").textContent = S.b ? "" : "(pick look B first)";
  }};
  document.querySelectorAll(".mph").forEach(b => b.addEventListener("click", () => {{ S.ph = b.dataset.ph; render(); }}));
  $("m-a").addEventListener("change", e => {{ S.a = e.target.value; render(); }});
  $("m-b").addEventListener("change", e => {{ S.b = e.target.value; render(); }});
  $("m-wa").addEventListener("input", e => {{ S.wa = +e.target.value; render(); }});
  $("m-wb").addEventListener("input", e => {{ S.wb = +e.target.value; render(); }});
  $("m-bm").addEventListener("change", e => {{ S.bm = e.target.value; render(); }});
  $("m-reset").addEventListener("click", () => {{ Object.assign(S, {{ a: "riso", wa: 100, b: "", wb: 50, bm: "normal" }}); render(); }});
  const stage = $("m-stage");
  const toggle = () => stage.classList.toggle("full");
  stage.addEventListener("click", toggle);
  stage.addEventListener("keydown", e => {{ if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); toggle(); }} if (e.key === "Escape") stage.classList.remove("full"); }});
  render();
  let db = null;
  try {{ db = await claude.use("db"); }} catch (e) {{ db = null; }}
  if (!db) {{ $("m-status").textContent = "Saving needs you signed in on claude.ai."; $("m-save").disabled = true; return; }}
  const box = $("m-saved");
  db.collection("looks").onSnapshot(snap => {{
    box.textContent = "";
    snap.docs.forEach(d => {{ const v = d.data() || {{}}; const row = document.createElement("div"); row.className = "msv";
      const t = document.createElement("span"); t.textContent = "Saved " + label(v); row.appendChild(t);
      const b1 = document.createElement("button"); b1.textContent = "Load"; b1.addEventListener("click", () => {{ Object.assign(S, {{ ph: v.ph, a: v.a || "", wa: v.wa ?? 100, b: v.b || "", wb: v.wb ?? 50, bm: v.bm || "normal" }}); render(); stage.scrollIntoView({{ block: "center" }}); }});
      const b2 = document.createElement("button"); b2.textContent = "Delete"; b2.addEventListener("click", async () => {{ try {{ await db.doc("looks/" + d.id).delete(); }} catch (e) {{ $("m-status").textContent = "Not deleted: " + (e && e.message || "error"); }} }});
      row.append(b1, b2); box.appendChild(row); }});
    $("m-status").textContent = snap.docs.length ? snap.docs.length + " saved." : "Nothing saved yet.";
  }}, err => {{ $("m-status").textContent = "Saved settings could not load: " + (err && err.message || "error"); }});
  $("m-save").addEventListener("click", async () => {{
    const id = S.ph + "_" + Date.now();
    try {{ await db.doc("looks/" + id).set(Object.assign({{}}, S, {{ at: new Date().toISOString() }})); $("m-status").textContent = "Saved: " + label(S); }}
    catch (e) {{ $("m-status").textContent = "Not saved: " + (e && e.message || "error"); }}
  }});
}})();
</script>
<div class="zoom" id="zoom" hidden><span class="hint">Tap the photo to zoom</span><button class="close" id="zoom-close">Close</button><img id="zoom-img" alt=""></div>
<script>
(() => {{
  const box = document.getElementById("zoom"), img = document.getElementById("zoom-img");
  let last = null;
  const open = (el) => {{ last = el; box.classList.remove("big"); img.classList.toggle("round", !!el.dataset.round);
    img.src = el.src; img.alt = el.alt; const hi = new Image(); hi.onload = () => {{ if (last === el) img.src = hi.src; }}; hi.src = el.dataset.zoom;
    box.hidden = false; document.getElementById("zoom-close").focus(); }};
  const close = () => {{ box.hidden = true; img.removeAttribute("src"); if (last) last.focus(); }};
  document.addEventListener("click", e => {{ const el = e.target.closest("[data-zoom]"); if (el && !box.contains(el)) open(el); }});
  document.addEventListener("keydown", e => {{ const el = e.target.closest && e.target.closest("[data-zoom]");
    if (el && (e.key === "Enter" || e.key === " ")) {{ e.preventDefault(); open(el); }}
    if (e.key === "Escape" && !box.hidden) close(); }});
  img.addEventListener("click", e => {{ e.stopPropagation(); box.classList.toggle("big"); }});
  box.addEventListener("click", e => {{ if (e.target === box) close(); }});
  document.getElementById("zoom-close").addEventListener("click", close);
  const main = document.getElementById("main"), fl = {{ "f-all": "", "f-v": "f-v", "f-nx": "f-nx" }};
  Object.keys(fl).forEach(id => document.getElementById(id).addEventListener("click", () => {{
    main.classList.remove("f-v", "f-nx"); if (fl[id]) main.classList.add(fl[id]);
    Object.keys(fl).forEach(o => document.getElementById(o).setAttribute("aria-pressed", o === id ? "true" : "false"));
    try {{ localStorage.setItem("pp-filter2", id); }} catch (e) {{}} }}));
  try {{ const s = localStorage.getItem("pp-filter2"); if (s && fl[s] !== undefined) document.getElementById(s).click(); }} catch (e) {{}}
}})();
</script>
<script>
(async () => {{
  const status = document.getElementById("status");
  const state = {{}};
  const paint = (id) => {{ const st = state[id] || {{}}; const card = document.querySelector('.card[data-id="' + id + '"]'); if (!card) return;
    const t = document.getElementById("tick-" + id), x = document.getElementById("drop-" + id);
    t.setAttribute("aria-pressed", st.v ? "true" : "false"); t.querySelector(".lbl").textContent = st.v ? "Ticked" : "Tick this one";
    x.setAttribute("aria-pressed", st.x ? "true" : "false"); x.querySelector(".lbl").textContent = st.x ? "Removed, tap to bring back" : "Remove";
    card.classList.toggle("on", !!st.v); card.classList.toggle("gone", !!st.x); }};
  const summary = () => {{ const v = Object.values(state); const nv = v.filter(s => s.v).length, nx = v.filter(s => s.x).length;
    status.textContent = (nv || nx) ? nv + " ticked, " + nx + " removed. Saved." : "Nothing ticked or removed yet."; }};
  const btns = [...document.querySelectorAll(".tick, .drop")];
  let db = null;
  const timer = setTimeout(() => {{ if (!db) status.textContent = "Ticks could not load here. Open the page on claude.ai to tick."; }}, 10000);
  try {{ db = await claude.use("db"); }} catch (e) {{ db = null; }}
  if (!db) {{ clearTimeout(timer); status.textContent = "Ticks need you signed in on claude.ai."; btns.forEach(b => b.disabled = true); return; }}
  db.collection("ticks").onSnapshot(snap => {{ clearTimeout(timer);
    snap.docs.forEach(d => {{ const v = d.data() || {{}}; state[d.id] = {{ v: !!v.v, x: !!v.x }}; paint(d.id); }}); summary(); }},
    err => {{ clearTimeout(timer); status.textContent = "Ticks could not load: " + (err && err.message || "error"); }});
  btns.forEach(b => b.addEventListener("click", async () => {{
    const id = b.closest(".card").dataset.id; const prev = Object.assign({{ v: false, x: false }}, state[id]);
    const next = Object.assign({{}}, prev);
    if (b.classList.contains("tick")) {{ next.v = !prev.v; if (next.v) next.x = false; }} else {{ next.x = !prev.x; if (next.x) next.v = false; }}
    state[id] = next; paint(id); summary();
    try {{ await db.doc("ticks/" + id).set({{ v: next.v, x: next.x, at: new Date().toISOString() }}); }}
    catch (e) {{ state[id] = prev; paint(id); status.textContent = "Not saved: " + (e && e.message || "error"); }}
  }}));
}})();
</script>
'''
(HERE / "index.html").write_text(html)
print(len(html))
