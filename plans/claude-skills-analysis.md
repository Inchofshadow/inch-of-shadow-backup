# Claude Skills Analysis — Inch of Shadow Platform
**Last updated:** 2026-03-22
**Purpose:** Map all available and buildable Claude skills to the project's 5 tools and 8 career goals. Use this as a reference when deciding what to build next.

---

## What Claude Skills Are

A Claude skill is a folder with a `SKILL.md` file — YAML frontmatter (name, description, when to trigger) plus markdown instructions Claude follows whenever that skill activates. Skills can also bundle reference files, scripts, and templates. They load progressively: Claude only pulls in the full skill when it's relevant, so they stay lightweight.

You already have one custom skill: `.claude/skills/release-prep/SKILL.md` — the release preparation workflow that handles SoundCloud, Instagram, YouTube, Bandcamp, Beatport copy and premiere contacts. That's the right pattern. Everything below is what you have, what you should build, and what already exists as a built-in.

---

## Part 1: Built-In Skills (Available Now)

These live in `/mnt/.skills/skills/` and activate automatically when relevant.

### `docx` — Word Documents
**What it does:** Creates, edits, and formats professional `.docx` files with proper structure, tables of contents, headings, page numbers, letterheads.

**Where it fits in your project:**
- **Tool 3 (Promotion Engine):** Generate artist press kits as Word documents — bio, credits, release history, photo credits, booking contact, streaming links. The kind of document you send to blogs, festivals, and radio stations.
- **Goal 3 (Media/Premieres):** A ready-to-send press kit `.docx` for every EP. Include track notes, credits, social stats, and link to streaming platforms. Blogs and podcasts often want a Word doc they can pull quotes from.
- **Goal 4 (Label releases):** A demo submission package — short artist bio, release history, production notes, contact info. More professional than an email alone.
- **Goal 5 (Management):** The artist package — catalog summary, touring history, stats overview, vision statement. This is what goes to management companies.

### `pdf` — PDF Creation and Processing
**What it does:** Creates PDFs from scratch, merges/splits existing PDFs, fills forms, handles OCR on scanned documents.

**Where it fits:**
- **Press kits as PDF** — a PDF version of the press kit above. PDF is the standard format for festival submissions, booking inquiries, and label demos. More universal than `.docx`.
- **Festival submissions (Goal 7):** Festival application packages almost always want a PDF — artist bio, photo, EPK link, and a written statement about your sound.
- **Release one-pagers:** A single polished PDF per release — artwork mockup, tracklist, genre tags, release date, streaming links, booking email. The kind of thing you drop in a Dropbox link when a DJ asks "what's new?"

### `xlsx` — Excel Spreadsheets
**What it does:** Creates and edits `.xlsx` spreadsheets with formulas, formatting, charts, and data analysis.

**Where it fits:**
- **Tool 5 (Stats Dashboard):** Before you build the full Stats Dashboard in Flask, you can get real value now by generating per-release stats trackers in Excel. Stream counts, Spotify saves, Bandcamp sales, YouTube views — one row per release, one column per platform. Visualize what's growing.
- **Goal 0 (Audience growth):** A follower-growth tracker — one sheet per platform, weekly snapshots. Helps you see what's working across Bandcamp, SoundCloud, Instagram, Spotify.
- **SI contact enrichment tracking:** Track which of your 920 contacts have been emailed, which responded, and which converted. Pull from `enriched_contacts.json`, filter by score 4-5, add outreach status columns.
- **Revenue tracking:** Bandcamp payouts, Beatport royalties, streaming revenue per release. Simple spreadsheet until the full Stats Dashboard is built.

### `pptx` — PowerPoint Presentations
**What it does:** Creates `.pptx` slide decks with proper design, layouts, images, and speaker notes.

**Where it fits:**
- **Goal 5 (Management) / Goal 6 (Booking Agency):** An artist pitch deck — 8-10 slides covering your sound, catalog, audience stats, live setup, upcoming releases, and vision. Something a manager or booking agent can flip through in 5 minutes and understand who you are.
- **Goal 4 (Label releases):** Some labels (especially larger ones) appreciate a visual artist overview with artwork, release history, and key stats.
- **Festival pitch (Goal 7):** A few festivals (especially larger ones like ADE showcases) accept slide-based applications.

### `schedule` — Scheduled Tasks
**What it does:** Creates recurring automated tasks that run on a cron schedule.

**Where it fits:**
- **Automated stats pulls:** Once Tool 5 starts pulling platform data, you can schedule weekly stats updates to run automatically every Monday.
- **Release deadline reminders:** Schedule a task to check your release timeline milestones and notify you when something is due (e.g., "Spotify pitch window opens in 3 days").
- **Content calendar prompts:** A weekly task that checks your upcoming release schedule and prompts you with "what to post this week" based on the release timeline.
- **SI maintenance:** Schedule monthly re-enrichment runs against Discogs/SoundCloud to keep contact data fresh.

### `skill-creator` — Build and Improve Skills
**What it does:** Guides you through writing new `SKILL.md` files, running test cases against them, iterating based on feedback, and optimizing the trigger description.

**Where it fits:** Every custom skill listed below in Part 2 can be built using the `skill-creator`. It handles the full loop: draft → test → evaluate → improve → package.

---

## Part 2: Custom Skills to Build

These don't exist yet. Each maps to a specific gap in your platform.

---

### SKILL 1: `promo-email` — DJ and Label Promo Emails
**Priority: HIGH — blocks Goal 2 and Goal 4**

**What it does:** Takes a release JSON and a filtered list of SI contacts (score 4-5, genre match) and generates a personalized promo email for each contact — DJs, labels, media. Not a mass-blast template. Each email is tailored to the contact's genre, SoundCloud followers, location, and sub-type (DJ, label A&R, press/premiere).

**Trigger phrases:** "write promo emails for this release", "draft DJ promo for [release]", "email these contacts about [EP name]"

**What it reads:**
- `releases/<slug>.json` — release metadata, SEO copy, tracklist, links
- `scene_intelligence/enriched_contacts.json` — filtered by score + genre
- `.env` for the booking email

**What it produces:**
- One email per contact (subject + body, under 150 words for DJs, under 200 for labels)
- Subject lines: specific to genre, not generic ("Dark Disco Acid Promo // Inch of Shadow" not "New Release")
- For DJs: groove, energy, peak-time vs warm-up context, BPM, format (WAV/MP3 available)
- For labels: production story, genre fit, current catalog reference (e.g., "sounds like something on [label's recent release]")
- For media/premiere contacts: mood hook, streaming links, high-res artwork link

**Saves to:** `releases/<slug>_promo_emails.json`

---

### SKILL 2: `press-kit` — Full EPK Generator
**Priority: HIGH — needed for Goals 3, 4, 5, 6, 7**

**What it does:** Generates a complete Electronic Press Kit (EPK) for Inch of Shadow, either as a Word doc (`.docx`) or PDF, with all standard sections: artist bio, sound description, discography, technical rider, streaming links, booking contact, selected press quotes (when available), and a cover page with artwork.

**Trigger phrases:** "generate press kit", "make EPK", "create artist package", "I need something to send to [label/festival/blog]"

**What it reads:**
- `releases/` directory — all releases, most recent first
- `plans/project-brief.md` — artist info, labels, platforms
- A single configurable bio file (to be created if not present)

**What it produces:**
- A `.docx` and/or `.pdf` EPK using the `docx` and `pdf` built-in skills
- Sections: Cover, Artist Bio (short + long version), Discography, Sound/Style, Live Setup, Stats (placeholder), Contact, Links

---

### SKILL 3: `content-calendar` — 8-Week Content Plan
**Priority: MEDIUM — needed for Goal 0 and Goal 1**

**What it does:** Takes a release date and generates a week-by-week posting plan covering all platforms, following the timing guide already documented in `plans/release-manager.md`. Outputs a formatted calendar in Markdown or Excel.

**Trigger phrases:** "plan content for [release]", "what should I post this week", "content calendar for [EP name]", "release schedule for [date]"

**What it reads:**
- `releases/<slug>.json` for release metadata and platform links
- `plans/seo-strategy.md` Section 9 (cross-platform checklist)
- `release_manager/seo_platform_specs.json` for platform constraints

**What it produces:**
- An 8-week grid (W-6 to W+2): platform, action, content type, deadline
- Copy suggestions for each item where SEO copy already exists in the release JSON
- Outputs to either Markdown (for quick viewing) or `.xlsx` via the xlsx skill

---

### SKILL 4: `si-research` — Scene Intelligence Enrichment
**Priority: MEDIUM — improves Tool 1**

**What it does:** Researches a specific contact or category of contacts (e.g., "score 4-5 labels we haven't emailed") to find deeper context — recent releases, social links, preferred submission process, booking contact format. Uses web search to supplement the SI data.

**Trigger phrases:** "research [contact name]", "find submission info for [label]", "enrich [contact] from SI", "which labels should I demo to first"

**What it reads:**
- `scene_intelligence/enriched_contacts.json`
- Web search results for specific contacts

**What it produces:**
- A concise contact brief: who they are, what they release, how to approach them, any submission guidelines found
- Flags if contact data is stale (no recent activity)

---

### SKILL 5: `stats-brief` — Weekly Stats Summary
**Priority: LOW-MEDIUM — precursor to Tool 5**

**What it does:** Prompts you to paste in stats from each platform (Spotify for Artists, Bandcamp analytics, SoundCloud, Instagram) and formats them into a clean weekly brief — growth deltas, what's performing, what's not, and recommended actions.

**Trigger phrases:** "update my stats", "weekly stats", "how is [release] performing", "stats for this week"

**What it produces:**
- A `.xlsx` stats sheet with this week's data added to the running log
- A plain-language brief: "Spotify saves up 12% vs last week — the SoundCloud repost from [contact] likely drove this. Action: follow up with a thank-you and pitch the next track."

---

### SKILL 6: `festival-submission` — Festival Application Package
**Priority: LOW (needed by Goal 7, Q4 2026 / Q1 2027)**

**What it does:** Researches a specific festival, identifies their submission requirements, and drafts a tailored application — artist statement, setlist proposal, technical rider, links, and the right tone for that festival's aesthetic.

**Trigger phrases:** "prepare festival submission for [festival]", "apply to [festival name]", "festival application"

**What it reads:**
- `plans/project-brief.md`
- Web search for festival submission guidelines and past lineups

**What it produces:**
- Tailored artist statement (500-800 words, adapted to the festival's aesthetic)
- Technical rider template
- A `.pdf` application package if the festival accepts document-based submissions

---

## Part 3: Skills That Already Exist (Public/Community)

From research on the Claude skills ecosystem, several community-built skills are relevant:

**`brand-guidelines`** — You don't have formal Inch of Shadow brand guidelines in code form yet. A brand guidelines skill could encode your visual identity (dark/club aesthetic, Space Grotesk + Inter typography, #d4a94e gold, Berlin underground tone) and apply them consistently across all generated documents and content.

**Marketing skills** — The `marketingskills` repository on GitHub (github.com/coreyhaines31/marketingskills) includes CRO, copywriting, SEO, and analytics skills that could supplement your existing SEO knowledge from `seo-strategy.md`.

**`web-artifacts-builder`** — Useful when you eventually want a public-facing web presence or press/EPK page as a standalone HTML artifact.

---

## Part 4: Mapping Skills to Career Goals

| Goal | Built-In Skills | Custom Skills to Build |
|------|----------------|------------------------|
| Goal 0: Grow audience | `xlsx` (tracking), `schedule` (automation) | `content-calendar`, `stats-brief` |
| Goal 1: Catalog | `docx`, `pdf` (per-release docs) | Already covered by `release-prep` |
| Goal 2: DJ support | — | `promo-email` (DJ variant) |
| Goal 3: Media/Premieres | `docx`, `pdf` (press kit) | `press-kit`, `promo-email` (media variant) |
| Goal 4: Label releases | `pdf` (demo package) | `press-kit`, `promo-email` (label variant) |
| Goal 5: Management | `pptx` (pitch deck), `docx` (artist package) | `press-kit`, `stats-brief` |
| Goal 6: Booking | `docx`, `pdf` (booking materials) | `promo-email` (venue/booker variant) |
| Goal 7: Festivals | `pdf` (submission package) | `festival-submission` |

---

## Part 5: Recommended Build Order

**Immediate (before first EP release):**
1. Use `release-prep` skill — already done, already working
2. Build `content-calendar` skill — needed for the 8-week pre-release window
3. Use `docx` + `pdf` built-ins to generate a first press kit manually (then formalize into `press-kit` skill)

**After first EP release (Phase 2):**
4. Build `promo-email` skill — unlocks DJ outreach and label demos in one workflow
5. Build `press-kit` skill — formalizes the EPK into a repeatable automated process
6. Use `xlsx` skill for stats tracking until Tool 5 is built

**Later (Phase 3+):**
7. Build `stats-brief` skill — lightweight stats layer before the full Stats Dashboard
8. Build `festival-submission` skill — needed Q4 2026 for summer 2027 festival deadlines
9. Build `si-research` skill — improves contact quality for outreach

---

## Notes

- All custom skills go in `.claude/skills/<skill-name>/SKILL.md` to be project-local (only visible in sessions with this folder mounted).
- Use `skill-creator` to build any of the custom skills above — it handles drafting, testing, and iteration.
- The `release-prep` skill already follows the right pattern: reads release JSON, reads SI contacts, generates outputs, saves back to JSON. New skills should follow the same pattern.
- Privacy rule applies to skills too: no skills should send data externally without explicit approval. Promo email skill drafts — it does not send. Sending goes through Tool 4 (Email Outreach Manager) with SMTP, which is a separate tool.

---

*Research sources: Anthropic Claude skills documentation, support.claude.com, code.claude.com/docs/en/skills, github.com/travisvn/awesome-claude-skills, github.com/ComposioHQ/awesome-claude-skills*
