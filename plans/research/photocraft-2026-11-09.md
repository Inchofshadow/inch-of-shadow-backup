# PhotoCraft (ArtCraft) for our cover pipeline, research 2026-11-09

Asked by Amir in the Half the Night cover chat after the cover report ("the adobe clone github"). Text only, nothing downloaded or installed.

## What it is (from the repo page, github.com/storytold/photocraft, read 2026-11-09)
- Open-source "clean-room reimplementation of Adobe Photoshop, rebuilt in pure Rust", part of the ArtCraft suite (VectorCraft, FilmCraft, LightCraft, EffectCraft, DesignCraft, PdfCraft and more). Run by Brandon Thomas; press says built with Claude Opus.
- 78.2k stars, 13.8k forks, 11,187 commits, MIT or Apache-2.0. Status on the page: "early alpha", "not yet a Photoshop replacement for daily professional work".
- macOS: universal DMG (Apple silicon + Intel), "Signed and notarized"; CLI zip also signed. Also Windows, Linux, web (WebAssembly).
- Page says "Open source, offline, and yours"; security docs (threat model, fuzzing); no telemetry statement found.

## What matters for us
- Automation: `photocraft-cli` (run, batch with a JSON action list), an MCP server (`photocraft-cli mcp`, agent can drive it headless or bridged to the running app), a loopback JSON control channel, "500+ commands".
- Layers, groups, clipping masks, pixel + vector masks, 16 adjustment layers, layer styles, 27 blend modes, filters with live preview.
- Select Subject / Object Selection run locally ("no cloud and no account"); model not named.
- PSD/PSB read and write; type layers stay editable and round-trip through PSD (re-saved PSDs not byte-identical; 307 of 309 test files render the same).
- 8/16/32-bit, ICC colour management, CMYK.
- Gaps (stated): AI/generative features, Content-Aware Fill, 15 tools, typography depth, plug-in compatibility.

## Fit with the cover pipeline (Claude's read)
- Strongest fit: covers with Amir in the photo. Local Select Subject = the cutout we lack (never AI on his face; this runs locally). Adjustment layers = grading a real photo instead of repainting.
- Hand-off format: export the cover as a layered PSD (art / light / title / name) instead of a flat JPG, so the last touch keeps editable layers. Canva's PSD import is unchecked.
- MCP: Claude could apply looks, grades and masks by command and batch the campaign sizes. Unproven: the tool list is not on the page.
- Not a replacement for our Layout page: our live stages (calculated moonlight, smart colours, per-element effects, picks) are specific to us. PhotoCraft would sit beside it as the pixel editor.
- Risks: early alpha (crashes, PSD quirks), very fast AI-written codebase, legal questions raised by press about a clean-room clone. Fine for drafts and internal work; keep the release master check in our own export.

## Suggested trial (needs Amir's yes; he installs the DMG himself)
1. Amir downloads the signed DMG from the official releases page.
2. One test on the final cover: open the 3000 px JPG, Select Subject on a shoot photo, one adjustment layer, export PSD; check the PSD opens in Canva.
3. Try the MCP server read-only (list tools) before connecting it to any session.

Sources: github.com/storytold/photocraft; petapixel.com 2026-10-07; designcompass.org 2026-10-19; techstrong.ai; warp2search.net.
