"""Build the private phone review page (claude.ai artifact) from plans/review-export-*.json.

Run from the repo root:  python3 plans/review-page/gen.py
Output: plans/review-page/review.html, published with the Artifact tool (same URL every time).

The page shows the open review items of every exported release and lets Amir tick
approve / change / drop on his phone. A tick is written to the page's db collection
`ticks` as {id, action, note, sha256, at}; its tick_id is the db doc id. Ticks never move a
state: the System chat reads them back with ArtifactData, runs review.import_ticks (which
only fills item.proposed) and Amir confirms at the desk (RM /review or review.py confirm).
Schema: plans/review-flow-schema.md, "Phone page".
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load_exports():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "plans", "review-export-*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        items = [i for i in d.get("items", []) if i.get("state") in ("draft", "needs-you", "change")]
        if items:
            out.append({"slug": d["slug"], "title": d.get("title") or d["slug"],
                        "generated": d.get("generated", ""), "items": items})
    return out


PAGE = r"""<title>Phone Review</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Jost:wght@300;400;500&display=swap">
<style>
/* One column of review cards, made for a thumb: picture, what it is, three answers. */
:root {
  --bg: #0F0D0C; --panel: #181513; --line: #2B2622; --fg: #D6D1C8; --mute: #8E877D;
  --ok: #8FB08A; --warn: #D2A65A; --bad: #C97A6A;
  --display: "Marcellus", "Cormorant Garamond", Georgia, serif;
  --body: "Jost", "Helvetica Neue", Arial, sans-serif;
  color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font: 300 16px/1.5 var(--body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 20px 48px; }
main { max-width: 560px; margin: 0 auto; display: grid; gap: 22px; }
header h1 { font: 400 34px/1.1 var(--display); margin: 0; letter-spacing: .01em; }
header p { margin: 6px 0 0; color: var(--mute); font-size: 14px; }
.rel { display: grid; gap: 14px; }
.rel h2 { font: 400 13px/1 var(--body); letter-spacing: .16em; text-transform: uppercase; color: var(--mute); margin: 8px 0 0; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 14px; display: grid; gap: 12px; min-width: 0; }
.thumb { width: 100%; max-width: 100%; aspect-ratio: 1 / 1; object-fit: contain; background: #0b0a09; border-radius: 6px; }
.thumb.tall { aspect-ratio: 9 / 16; max-height: 70vh; }
.text { white-space: pre-wrap; background: #0b0a09; border-radius: 6px; padding: 12px; font-size: 15px; }
.top { display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; justify-content: space-between; }
.label { font: 400 21px/1.2 var(--display); min-width: 0; }
.meta { color: var(--mute); font-size: 13px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 12px; letter-spacing: .04em; padding: 3px 9px; border-radius: 999px; border: 1px solid var(--line); color: var(--mute); }
.chip.pass { color: var(--ok); border-color: color-mix(in srgb, var(--ok) 45%, var(--line)); }
.chip.manual { color: var(--warn); border-color: color-mix(in srgb, var(--warn) 45%, var(--line)); }
.chip.fail, .chip.held { color: var(--bad); border-color: color-mix(in srgb, var(--bad) 55%, var(--line)); }
.state { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; padding: 3px 9px; border-radius: 4px; background: #241f1b; }
.proposed { font-size: 13px; color: var(--warn); border: 1px dashed color-mix(in srgb, var(--warn) 60%, var(--line)); border-radius: 6px; padding: 6px 10px; }
.actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
button { font: 500 15px var(--body); color: var(--fg); background: #221e1a; border: 1px solid var(--line); border-radius: 8px; padding: 12px 6px; cursor: pointer; }
button:focus-visible, textarea:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
button.on { border-color: var(--fg); background: #2d2823; }
button:disabled { opacity: .45; cursor: default; }
textarea { width: 100%; box-sizing: border-box; min-height: 64px; font: 300 15px/1.4 var(--body); color: var(--fg); background: #0b0a09; border: 1px solid var(--line); border-radius: 8px; padding: 10px; }
.msg { font-size: 13px; color: var(--mute); min-height: 1.2em; }
.msg.err { color: var(--bad); }
.empty { color: var(--mute); }
footer { color: var(--mute); font-size: 12px; line-height: 1.5; }
@media (prefers-reduced-motion: no-preference) { button { transition: background .15s, border-color .15s; } }
</style>

<main>
  <header>
    <h1>Phone Review</h1>
    <p>Your tick is a proposal. Nothing is approved until you confirm it at the desk.</p>
  </header>
  <div id="rels"></div>
  <footer id="foot"></footer>
</main>

<script id="data" type="application/json">__DATA__</script>
<script>
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("data").textContent);
  var rels = document.getElementById("rels");
  var latest = {};          // item key -> newest tick body
  var db = null;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function key(slug, id) { return slug + "/" + id; }
  function when(iso) {
    try { var d = new Date(iso); return d.toLocaleDateString(undefined, {day: "numeric", month: "short"}) + " " + d.toLocaleTimeString(undefined, {hour: "2-digit", minute: "2-digit"}); }
    catch (e) { return iso; }
  }

  function render() {
    rels.textContent = "";
    if (!DATA.length) { rels.appendChild(el("p", "empty", "Nothing waits for review right now.")); return; }
    DATA.forEach(function (rel) {
      var sec = el("section", "rel");
      sec.appendChild(el("h2", null, rel.title));
      rel.items.forEach(function (it) { sec.appendChild(card(rel, it)); });
      rels.appendChild(sec);
    });
  }

  function card(rel, it) {
    var c = el("article", "card");
    if (it.thumbnail) {
      var img = el("img", "thumb" + (/(reel|story|9:16|render)/i.test(it.kind) ? " tall" : ""));
      img.src = it.thumbnail; img.alt = it.label;
      c.appendChild(img);
    } else if (it.text) {
      c.appendChild(el("div", "text", it.text));
    }
    var top = el("div", "top");
    top.appendChild(el("div", "label", it.label));
    var held = it.gate === "held";
    top.appendChild(el("span", "state", held ? "held" : it.state.replace("-", " ")));
    c.appendChild(top);
    c.appendChild(el("div", "meta", it.kind + ", version " + it.version + (it.name ? ", " + it.name : "")));

    var chips = el("div", "chips");
    (it.chips || []).forEach(function (ch) {
      if (ch.tone === "na") return;
      var x = el("span", "chip " + ch.tone, ch.name + (ch.tone === "pass" ? "" : ": " + ch.reason));
      chips.appendChild(x);
    });
    if (chips.childNodes.length) c.appendChild(chips);

    var t = latest[key(rel.slug, it.id)];
    if (t) c.appendChild(el("div", "proposed", "You proposed " + t.action + (t.note ? ": " + t.note : "") + " (" + when(t.at) + "). Confirm it at the desk."));

    var note = el("textarea");
    note.id = "note-" + rel.slug + "-" + it.id;
    note.placeholder = "Note (needed for change)";
    var msg = el("div", "msg");
    var row = el("div", "actions");
    [["approve", "Approve"], ["change", "Change"], ["drop", "Drop"]].forEach(function (a) {
      var b = el("button", t && t.action === a[0] ? "on" : null, a[1]);
      b.type = "button";
      if (held && a[0] === "approve") { b.disabled = true; b.title = "A held item cannot be approved; fix the file first."; }
      b.addEventListener("click", function () { send(rel, it, a[0], note, msg, row); });
      row.appendChild(b);
    });
    if (held) msg.textContent = "Held: a check failed, so this file cannot be approved. Change or drop it.";
    c.appendChild(row); c.appendChild(note); c.appendChild(msg);
    return c;
  }

  function send(rel, it, action, note, msg, row) {
    var text = note.value.trim();
    if (action === "change" && !text) { msg.className = "msg err"; msg.textContent = "Write what should change, then tap Change."; note.focus(); return; }
    if (!db) { msg.className = "msg err"; msg.textContent = "Saving is not available in this view. Open the page signed in to claude.ai."; return; }
    var buttons = row.querySelectorAll("button");
    buttons.forEach(function (b) { b.disabled = true; });
    msg.className = "msg"; msg.textContent = "Saving...";
    db.collection("ticks").add({slug: rel.slug, id: it.id, action: action, note: text, sha256: it.sha256, at: new Date().toISOString()})
      .then(function () { msg.textContent = "Saved. Claude reads it and your confirm at the desk makes it real."; note.value = ""; })
      .catch(function (e) {
        msg.className = "msg err";
        msg.textContent = (e && e.code === "not_granted") ? "Saving was not allowed. Check the page permissions." : "Could not save (" + ((e && e.code) || "error") + "). Try again in a moment.";
      })
      .then(function () { buttons.forEach(function (b) { b.disabled = (b.textContent === "Approve" && it.gate === "held"); }); });
  }

  var foot = document.getElementById("foot");
  var count = DATA.reduce(function (n, r) { return n + r.items.length; }, 0);
  foot.textContent = count + " open item" + (count === 1 ? "" : "s") + ", exported " + (DATA[0] ? when(DATA[0].generated) : "") + ". Hash-bound: a file that changed after this export is refused at the desk.";
  render();

  if (window.claude && window.claude.use) {
    window.claude.use("db").then(function (d) {
      if (!d) { foot.textContent += " Saving is off in this view."; return; }
      db = d;
      var timer = setTimeout(function () { foot.textContent += " Earlier ticks did not load yet."; }, 10000);
      db.collection("ticks").orderBy("at", "asc").onSnapshot(function (snap) {
        clearTimeout(timer);
        latest = {};
        snap.docs.forEach(function (doc) { var b = doc.data(); if (b && b.slug && b.id) latest[key(b.slug, b.id)] = b; });
        render();
      }, function () { clearTimeout(timer); });
    });
  }
})();
</script>
"""


def main():
    data = load_exports()
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = os.path.join(HERE, "review.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("__DATA__", blob))
    n = sum(len(r["items"]) for r in data)
    print("%s: %d release(s), %d open item(s), %d bytes" % (os.path.relpath(out, ROOT), len(data), n, os.path.getsize(out)))


if __name__ == "__main__":
    main()
