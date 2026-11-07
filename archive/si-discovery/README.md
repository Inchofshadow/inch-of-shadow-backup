# archive/si-discovery

What: the Scene Intelligence discovery and enrichment scripts that built the industry contact DB
(DJ sets, rekordbox, Spotify, YouTube, Discogs, SoundCloud, label sites, websites), plus the
`run_sc_enrich.command` launcher. 13 scripts + 1 launcher, 5,325 lines.

Why: dead-code list `plans/strategy/dead-code-list-2026-11-05.md` row A1. Last enrichment
2026-04-28, no scheduled task, launchd job, live script or test calls or imports them. The data they
wrote (`scene_intelligence/enriched_contacts.json`) is live and stays where it is.
`extract_contacts.py` and `extract_ra.py` stay in `scene_intelligence/` (imported by
`promo_dj_shortlist`). `enrich_soundcloud.py` + `run_sc_enrich.command`: SoundCloud chat answer,
approved by Amir in that chat 2026-11-07.

Date: 2026-11-07. Approved by Amir 2026-11-07 ("Yes, your picks").

Note: the local skills `.claude/skills/discover/SKILL.md` and `.claude/skills/enrich/SKILL.md`
still name these paths; they were not edited here.

Undo (from the repo root):

```bash
for p in discover_contacts extract_rekordbox enrich_contacts enrich_spotify enrich_urls enrich_youtube re_enrich_discogs fetch_youtube_subs update_scores classify_subtypes scrape_label_emails scene_plan_recency_filter enrich_soundcloud; do git mv "archive/si-discovery/$p.py" "scene_intelligence/$p.py"; done
git mv archive/si-discovery/run_sc_enrich.command run_sc_enrich.command
git rm -q archive/si-discovery/README.md
```
