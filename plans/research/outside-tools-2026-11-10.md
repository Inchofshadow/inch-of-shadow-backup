# Outside image and video tools: inspection before install (⚙️ System 91, 2026-11-10)

Read as text only (official download pages, the GitHub repo page, the darktable manual). Nothing was downloaded, cloned or installed. None of these tools is on the Mac today (`/Applications` checked). PhotoCraft details: `plans/research/photocraft-2026-11-09.md`.

## 1. What each one is today

| Tool | Version, date | Licence | Mac build | Signing | Verdict |
|---|---|---|---|---|---|
| darktable | 5.6.2 (date not on the page) | GPL 3.0 | Apple silicon only (arm64 DMG); "no official releases for Intel Macs" | Not notarized by the look of it: the install page explains the "Apple could not verify darktable.app" dialog and the Privacy and Security workaround | ✅ safe, first candidate, only if a release uses shoot photos |
| Krita | 5.3.4.1, 7 Oct 2026 | GPL 3 | DMG, macOS 10.15 or newer; Apple silicon not stated on the page | File named `-signed.dmg`; notarization not stated | ✅ safe, not needed now |
| GIMP | 3.2.8, 2 Nov 2026 | GPL (from gimp.org/about) | Separate DMGs for Apple silicon and Intel, macOS 11 or newer | Not stated on the page | ✅ safe, fallback for a local cutout |
| Inkscape | 1.4.4, 6 May 2026 (from its release notes; inkscape.org refused the text reader) | GPL (not re-checked today) | Separate DMGs for Apple silicon and Intel | Not found | ✅ safe, for the logo and vector type later (Look-02) |
| PhotoCraft (ArtCraft) | early alpha | MIT or Apache-2.0 | Universal DMG, "Signed and notarized" (repo page, 11-09) | Yes | ⏸️ wait, re-check in 1 to 2 months |
| Graphite | alpha ("available now in alpha"); no release listed on GitHub | MIT or Apache-2.0 | Web editor at editor.graphite.art; a `desktop` folder exists, no Mac app named | n/a | ⏸️ wait, idea only (node graph = our layer pipeline) |

Telemetry: none of the four mature tools states telemetry on its download page; GIMP links a privacy policy that was not read. Treat as unverified until the trial (check each app's settings for any usage-statistics switch, turn it off).

## 2. The job each one would do for us

| Tool | Pipeline module | How we would call it | In | Out |
|---|---|---|---|---|
| darktable | Grade: one "Half the Night" look over every shoot photo of a release | `darktable-cli <photo> <look.xmp> <out.jpg> --width N --height N` (no GUI; `--style <name>` needs `--core --configdir`) | shoot photo (NEF/JPG) + one saved look | graded JPG, new file |
| GIMP 3 | Local cutout of Amir before PhotoCraft is ready; batch fixes | batch mode with a Python 3 script (`gimp -i --batch-interpreter=python-fu-eval -b ...`, exact form checked at trial) | photo | PNG with alpha |
| Inkscape | Logo and vector type (Look-02 wordmark in Pirata One, the eclipse mark) | `inkscape <file.svg> --export-type=png --export-filename=<out> -w N` (1.x CLI; note 1.4.4 says extensions fail when started from the command line on macOS) | SVG | PNG / PDF at any size |
| Krita | Hand-drawn motion (owl wings, stars) for reels | `krita <file.kra> --export --export-filename <out.png>` for stills; animation export by hand | KRA | PNG frames, then HyperFrames |
| PhotoCraft | Later: layered PSD hand-off, Select Subject, MCP control | `photocraft-cli` or its MCP server (tool list unproven) | JPG/PSD + action list | PSD with live layers |

## 3. One connection shape for Release Manager (for every tool, now and later)

- **Adapter = one small Python file per tool** under `release_manager/tools/`, all with the same call: `run(tool, input_path, recipe) -> output_path`.
  - `recipe` is a short JSON (look name, size, cutout on/off).
  - The tool runs with a fixed argument list, never through a shell; the input path is checked to sit inside the project; a time limit stops a hung run.
- **Output is always a new file** in `artwork/edits/<release>/<tool>/`, with a JSON record beside it (tool, version, recipe, input). Nothing is overwritten, his originals never change.
- **Back into the pipeline:** the Layout page gets a "Run tool" chip per installed tool; the result lands as a new layer or keep, so the live stages and picks work as today.
- **Missing tool = greyed chip** with "not installed", nothing breaks.
- **Settings:** each tool's app path in one config entry, found once (`/Applications/...`), shown on RM /fonts-style "Tools" list.
- **Later tools** (PhotoCraft, Graphite) plug into the same shape; an MCP tool gets an adapter that sends the recipe as MCP calls instead of a command line.

## 4. What Amir decides (step 4 of the ticket)

1. Which tools to install now. Claude's pick: **none yet** for Half the Night (the cover is final and made without them). Install **Inkscape** when the logo round starts (Pirata One wordmark + eclipse), and **darktable** only if the next release uses shoot photos.
2. He installs each app himself from the official page; darktable needs the one-time "Open Anyway" in Privacy and Security.
3. One small trial per tool on real files, then what we keep goes into `docs/brand/toolkit.md` (few tools, one per job).

## Sources
- darktable install page, darktable.org/install (5.6.2, arm64 DMG, Gatekeeper notes, GPL 3.0)
- darktable-cli manual, docs.darktable.org/usermanual/development/en/special-topics/program-invocation/darktable-cli/
- Krita download page, krita.org/en/download (5.3.4.1, 7 Oct 2026, signed DMG, GPL v3)
- GIMP downloads, gimp.org/downloads (3.2.8, 2 Nov 2026, Apple silicon + Intel DMGs); gimp.org/about (GPL)
- Inkscape 1.4.4 release notes (6 May 2026) via a reader mirror; inkscape.org returned 403 to the text reader
- Graphite repo, github.com/GraphiteEditor/Graphite (alpha, MIT/Apache-2.0, 27.9k stars)
- PhotoCraft: plans/research/photocraft-2026-11-09.md
