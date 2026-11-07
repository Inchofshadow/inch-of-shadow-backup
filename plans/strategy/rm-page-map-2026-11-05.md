# Release Manager: page map and RM 2.0 blueprint (2026-11-05)

Batch 1 of the ⚙️ System strategy refresh, M7 "RM 2.0 step 1". Read-only: no code was edited.
Source: `release_manager/webapp.py` on branch `score-board` today (5,710 lines with other sessions'
uncommitted edits, 145 routes), its 42 templates, the helper modules each route calls, and the data
files on disk. Builds on the RM pages table in `review-2026-11-05-code-map.md`.

Corrections to the code map: `/radar` is gone (removed by "Income 5", Amir: no pages for now), so
the RM has 23 pages, not 24. Of the 145 routes, 38 render a template (the 23 pages plus forms and
sub-pages), 71 answer JSON, 28 serve files, 8 redirect. Every rendered page also reads `theme.json` and `genres.json`
through the context processor.

"Last data change" = newest file the page reads or writes. Lane: songs / electronic / both / system.
"Keep / merge / drop?" is a question for Amir; the reason is mine. Nothing here is decided.

## 1. The 23 pages

| Page | Template | Reads | Writes | Lane | Last data change | Linked from | What it is for | Keep / merge / drop? (question + reason) |
|---|---|---|---|---|---|---|---|---|
| `/` Dashboard | `dashboard.html` | `releases/*.json`, `artwork/` scan, `plans/control-panel/tickets.json`, `plans/control-panel/backups.json`, `scene_intelligence/promotion_log.json`, `stats_snapshots/`, Intenso mount check | - | both | 11-05 | nav, every form page ("Back to Dashboard"), 404 page | briefing, overdue release tasks, release cards, 4 status lines | Keep, rebuild as the RM 2.0 home? It still reads the 09-01 promotion log and is release-shaped; the home page in section 3 replaces it |
| `/autopilot` | redirect | - | - | system | - | nothing (old links only) | redirect to Dashboard | Drop? 4 lines, nothing links to it |
| `/release/<slug>` (+ `/release/new`, `/edit`, tracks, `/links`, `/artwork`, 5 `/api/release/*`) | `release_detail.html`, `release_form.html`, `track_form.html` | `releases/<slug>.json`, `artwork/`, shadow-archive, fonts, effects indexes; Make-block scan of `resized/`, `resized_video/`, `generated_images/`, `../videos/`, `../youtube/renders/` | `releases/<slug>.json`, `genres.json`, `artwork/<slug>.<ext>` | both (data: 3 electronic releases; Half the Night EP lives inside `pinocchio-single.json`) | 11-04 | nav (New release), Dashboard, Archive, Effects, Fonts, Playground | the release record: metadata, tracks, timeline, checklist, links, refs | Keep. Question: EP gets its own file with an open date (code-map change 3)? Today the date 2026-11-06 is stale |
| `/tickets` | `tickets.html` | `plans/tickets.json`, `plans/control-panel/tickets.json` | - | system | 11-05 | nav, Board | the open queue, 6 areas, read-only | Keep. Merge with `/board` into one Work page? Two ticket files and two pages for one queue; Board is 48 of 56 done |
| `/board` (+ `/api/board/cards`) | `board.html` | `plans/control-panel/tickets.json` | - | system | 11-05 | nav, Tickets, Dashboard | Control Panel tower view | see `/tickets`: merge? Only 8 cards still open |
| `/outreach` (+ `/outreach/tick`) | `outreach.html` | `plans/outreach-batches.json`, `scene_intelligence/booking_targets.json` | `plans/outreach-batches.json` | electronic (DJ bookings) | 11-02 | nav | booking batches with Amir's try/drop ticks | Keep. Live since 10-14, batches 11-02/03 |
| `/palette` ("Settings" in nav; + `/api/palette/save`) | `palette.html` | `theme.json` | `theme.json` | system | 04-21 | nav | theme colour overrides | Drop, or fold into a System page? `theme.json` untouched since 2026-04-21 |
| `/edit` photo editor (+ preview, save, reveal, delete) | `photo_editor.html` | `artwork/`, `artwork/edits/`, `generated_images/imagine/`, shoot catalogue + Intenso edits, `~/.cache/inch-of-shadow/` | `artwork/edits/<stem>_edit_<ts>.jpg` + `.json`, cache previews, Trash on delete | both | 11-05 (1,787 files in `artwork/edits/`) | Artwork Resizer, Shoot photo, Shoot edit copies | one-picture editor, saves a new copy | Keep. Busiest Studio tool by output |
| `/imagine` (+ 14 sub-routes) | `imagine.html` | `releases/*.json`, `docs/brand/frame.md`, `options/<kind>/*.txt`, `references/imagine/`, `generated_images/imagine/*.json`, `docs/brand/ai-test-set.json`, style files | `generated_images/imagine/<id>.png + .json`, `references/imagine/<scope>/`, `releases/<slug>.json` (image brief, anchor), `stats_snapshots/claude_spend.json`, `openai_spend.json` | both | 11-05 | nav | AI image page: exact prompt first, paid render after a click, reviews, test set, local composite | Keep. 206 files in `generated_images/`; gpt-image-1.5 shuts 2026-12-01, so the render backend changes anyway |
| `/artwork-resizer` (+ `/resized/<f>`) | `artwork_resizer.html` | `artwork/`, `artwork/edits/`, `releases/*.json` | `artwork/<upload>`, `resized/` | both | `resized/` empty since 10-11 | nav | one image to the 24 platform sizes | Keep as a release-time tool, merge with Video Resizer into one Export page? Both read the same release metadata; together 320 lines of route code, the two biggest functions in the file |
| `/video-resizer` (+ source, `/resized_video/<f>`) | `video_resizer.html` | `videos/`, `releases/*.json` | `videos/<upload>`, `resized_video/` | both | `resized_video/` only `.gitkeep` | nav | video to 10 platform presets | see above. Has it ever produced a file that stayed? None in the folder |
| `/video` (+ start, render) | `video.html` | `../videos/*/` (hyperframes.json, meta, renders), `docs/brand/frame.md` | `../videos/<name>/` (new project via `start_video_project.py`) | both | 10-11 | nav | HyperFrames projects and their renders | Keep. Merge with Video Resizer under one Video page? Same Studio corner, both small |
| `/seo-copy` (+ 3 `/api/seo-copy/*`) | `seo_copy.html` | `releases/*.json`, `release_manager/seo_platform_specs.json`, `docs/brand/positioning.md`, `proof.md`, `voice.md` | `releases/<slug>.json` (seo_copy), spend ledgers | both | `seo_copy_artifacts/` 09-27; last release copy 11-04 | nav, Release page | Claude/GPT platform copy per release | Keep. Merge with Bio Manager into one Copy page? Same writers (`writers_ai`, `brand_context`, `copy_pass`), same spend ledgers |
| `/bios` Bio Manager (+ 6 `/api/bios/*`) | `bios.html` | `artist_profile.json`, `releases/*.json`, brand docs | `artist_profile.json`, spend ledgers | both (text still electronic-era, fixlist) | 09-21 | nav | per-platform bios with undo and "applied" stamps | see `/seo-copy`: merge? Bio rewrite for the songs lane is a content job, not a page job |
| `/engagement` (+ 11 `/api/engagement/*`, `/api/context/*`, `/api/contacts/*`) | `engagement.html` | `scene_intelligence/enriched_contacts.json`, `engagement_log.json`, `release_context.json`, `releases/*.json` | `engagement_log.json`, `enriched_contacts.json`, `release_context.json` | electronic (DJ-world contact DB) | 11-05 (written by automation) | nav | manual IG/SC queues, follow log, seeds, genre tags | Owners decide (IG/SC chats). Question: read-only view, write buttons off? The page and the automation both write `engagement_log.json`; since 10-07 sessions run without manual steps |
| `/promotion` (+ 11 `/api/promotion/*` incl. email compose and send) | `promotion.html`, `promotion_target_row.html` | `releases/*.json`, `promotion_log.json`, `enriched_contacts.json`, `email_send_state.json` (never created), `.env` Gmail | `promotion_log.json`, `release_context.json`, `email_send_state.json` | electronic (Farewell campaign) | 09-01 | nav | campaign targets per release, press kit text, Gmail sender (Tool 4) | Drop? Last write 2026-09-01, no email ever sent, superseded by `/outreach` plus the promotion-expert drafts Amir sends himself. Dropping it frees `email_outreach.py` and `contact_bridge.py` (1,027 lines) and the 160-line page function |
| `/shoot` (+ covers, photo, thumb, full, grid-tile, pfp, pull, out, font) | `shoot.html`, `shoot_covers.html`, `shoot_photo.html` | `plans/control-panel/shoot-catalogue.json`, Intenso photoshoot folder, `~/.cache/inch-of-shadow/`, `docs/brand/recipes/`, IG export media, `docs/brand/frame.md`, fonts | `generated_images/shoot/<id>_<fmt>.jpg`, cache grades and grid tiles | both | 10-14 | nav | the shoot catalogue: contact sheet, cover ideas, per-photo format sims and IG grid | Keep. The shoot is the content set; needs Intenso mounted for full size |
| `/fonts` (+ detail, file) | `fonts.html`, `font_detail.html` | `docs/brand/fonts/fonts.json`, `releases/*.json` | - | both | 10-14 (json), committed 11-03 | nav, Release page | font library with per-release use | Keep |
| `/playground` (+ `/playground/<slug>` and 24 sub-routes: wall, elements, ig-grid, layout, colours, accent, versions) | `playground.html`, `playground_wall.html`, `playground_elements.html`, `playground_iggrid.html`, `playground_layout.html`, `playground_colours.html` | `releases/<slug>.json`, `plans/playground-wall/<slug>*.json`, `artwork/**/playground-{covers,elements,iggrid,colours,extras}/<slug>/`, fonts, frame tokens | `plans/playground-wall/<slug>-{kept,layouts,elements,colours,hidden}.json`, `releases/<slug>.json` (versions), `$TMPDIR` cache | both (data: `pinocchio-single` only; nav hardwires "Cover: Half the Night") | 11-05 (uncommitted edits today) | nav x2 | the cover work for the next release, look by look | Keep. Question: one generic Cover page per release instead of a hard-coded nav link? The nav names one slug |
| `/effects` (+ detail, example, flag, release effects) | `effects.html`, `effect_detail.html` | `docs/brand/effects/effects.json`, `releases/*.json` | `effects.json` (flags), `releases/<slug>.json` (brand.effects) | both | 11-04 | nav, Release page, Archive | 122 named effects, Photo/Video tabs, per-release picks | Keep |
| `/archive` (+ detail, example, thumb, file) | `archive.html`, `archive_detail.html`, `archive_file.html` | `docs/brand/shadow-archive/index.json` + notes and examples, effects index, `generated_images/imagine/` | - | both | 11-04 | nav, Release page, Effects | Shadow Archive: design references with notes | Keep |
| `/stats` (+ thumb, sync, manual, 6 `/api/stats/*`) | `stats.html` | `stats_snapshots/*`, `spotify_s4a.json`, `ig_followback.json`, `plans/targets.json`, `data/bandcamp/*.csv`, `scene_intelligence/autonomy_state.json`, `ig_target_list.json`, `detection_events.json`, newest IG export | `stats_snapshots/snapshot_<ts>.json` (sync), `manual_entries.json`, `generated_images/stats_thumbs/`, `.sc_user_token.json` on refresh | both (account numbers for both lanes; per-track = electronic catalogue) | 11-05 | nav | score board vs targets, This-week panel, per-track metrics | Keep. Its score board becomes the top of the RM 2.0 home |
| `/sc-automation` (+ status, run, test-auth) | `sc_automation.html` | `engagement_log.json`, `sc_follow_tracker.json`, `.sc_user_token.json` | live run only with `SC_ALLOW_LIVE_RUNS` (blocked by default) | electronic / system | 11-05 (written by the SC tasks) | nav | SC engine status and a run button | Owners decide (SC chat). Question: status only, run button off? SC runs from scheduled tasks since 10-25 (06:30 to 13:00); the button is blocked anyway |

Pages with no data change since Oct 1: `/palette` (04-21), `/bios` (09-21), `/seo-copy` artefacts (09-27),
`/promotion` (09-01), `/artwork-resizer` and `/video-resizer` (no output on disk), `/autopilot`.
"No data change" is not "Amir never opened it": the RM has no page-view log (code-map change 8).

Decisions this map leaves to Amir: `/promotion` drop; `/palette` drop; `/autopilot` drop;
three merges (`/tickets`+`/board`, resizers (+ `/video`), `/seo-copy`+`/bios`); two owner questions
(`/engagement`, `/sc-automation` write buttons); EP as its own release file; Cover page per release.

## 2. All 145 routes

Line = decorator line in `webapp.py` today. Output: page / json / file / redirect / fragment.
Reads and writes per page are in section 1; here only the writes that differ from the page row.

### Release area (26 routes)

| Line | Route | Endpoint | Output | Writes | Helpers |
|---|---|---|---|---|---|
| 503 | `/` | `dashboard` | page | `promotion_log.json.bak` only if the log is corrupt | storage, timeline, checklist, stats/storage |
| 554 | `/release/new` GET,POST | `release_new` | page/redirect | `releases/<slug>.json`, `genres.json` | models, storage, timeline, checklist |
| 591 | `/release/<slug>` | `release_detail` | page | `releases/<slug>.json` only on timeline/checklist migration | storage, timeline, checklist, archive, fonts_page, effects_page |
| 704 | `/api/release/<slug>/delete` POST | `api_release_delete` | json | deletes `releases/<slug>.json` (permanent) | storage |
| 713 | `/release/<slug>/edit` GET,POST | `release_edit` | page/redirect | `releases/<slug>.json`, `genres.json` | storage, timeline (recompute), checklist |
| 832 | `/release/<slug>/track/new` GET,POST | `track_new` | page/redirect | `releases/<slug>.json`, `genres.json` | models, storage |
| 868 | `/release/<slug>/track/<num>/edit` GET,POST | `track_edit` | page/redirect | `releases/<slug>.json`, `genres.json` | storage |
| 939 | `/release/<slug>/track/<num>/delete` POST | `track_delete` | redirect | `releases/<slug>.json` | storage |
| 962 | `/release/<slug>/links` POST | `release_links` | redirect | `releases/<slug>.json` | storage |
| 984 | `/release/<slug>/artwork` POST | `release_artwork` | redirect | `artwork/<slug>.<ext>` | - |
| 2038 | `/api/release/<slug>/check/<task_id>` POST | `api_check` | json | `releases/<slug>.json` | checklist, storage |
| 2055 | `/api/release/<slug>/uncheck/<task_id>` POST | `api_uncheck` | json | `releases/<slug>.json` | checklist, storage |
| 2072 | `/api/release/<slug>/validate` | `api_validate` | json | - | models |
| 2082 | `/api/release/<slug>/metadata` | `api_release_metadata` | json | - | storage |
| 2103 | `/seo-copy` | `seo_copy_page` | page | - | seo_copy_generator |
| 2152 | `/api/seo-copy/generate` POST | `api_seo_copy_generate` | json | `releases/<slug>.json` (seo_copy), `claude_spend.json` | seo_copy_generator, writers_ai, claude_api, brand_context, copy_pass |
| 2205 | `/api/seo-copy/generate-both` POST | `api_seo_copy_generate_both` | json | both spend ledgers | + openai_api |
| 2226 | `/api/seo-copy/pick` POST | `api_seo_copy_pick` | json | `releases/<slug>.json` (seo_copy, written_by) | storage |
| 2252 | `/bios` | `bios_page` | page | - | bio_manager |
| 2265 | `/api/bios/generate` POST | `api_bios_generate` | json | `claude_spend.json` | bio_manager, writers_ai, claude_api, brand_context, copy_pass |
| 2283 | `/api/bios/generate-both` POST | `api_bios_generate_both` | json | both spend ledgers | + openai_api |
| 2299 | `/api/bios/save` PUT | `api_bios_save` | json | `artist_profile.json` | bio_manager |
| 2333 | `/api/bios/undo` PUT | `api_bios_undo` | json | `artist_profile.json` | bio_manager |
| 2359 | `/api/bios/applied` PUT | `api_bios_applied` | json | `artist_profile.json` | bio_manager |
| 2380 | `/api/bios/profile` PUT | `api_bios_profile` | json | `artist_profile.json` | bio_manager |
| 325 | `/artwork/<path>` | `serve_artwork` | file | - | - |

### Studio area (72 routes)

| Line | Route | Endpoint | Output | Writes | Helpers |
|---|---|---|---|---|---|
| 1205 | `/edit` | `photo_editor` | page | - | shoot_catalogue, shoot_pull, imagine |
| 1218 | `/edit/preview` | `photo_editor_preview` | file | `~/.cache/inch-of-shadow/edit-previews/<sha>.jpg` | PIL |
| 1241 | `/edit/save` POST | `photo_editor_save` | json | `artwork/edits/<stem>_edit_<ts>.jpg` + `.json` | photo_edit |
| 1273 | `/edit/reveal` POST | `photo_editor_reveal` | json | - (Finder `open -R`) | subprocess |
| 1284 | `/edit/delete` POST | `photo_editor_delete` | json | moves copy + json to `~/.Trash/` | shutil |
| 1344 | `/imagine` | `imagine_page` | page | - | imagine |
| 1363 | `/imagine/prompt` POST | `imagine_prompt` | json | - (free) | imagine |
| 1376 | `/imagine/generate` POST | `imagine_generate` | json | `generated_images/imagine/<id>.png + .json` (paid) | imagine, OpenAI images |
| 1393 | `/imagine/round` POST | `imagine_round` | json | same, only when confirmed | imagine |
| 1414 | `/imagine/decision` POST | `imagine_decision` | json | `<id>.json`; `releases/<slug>.json` on anchor | imagine, storage |
| 1449 | `/imagine/review` POST | `imagine_review` | json | `<id>.json`, spend ledger | imagine_review, claude_api, openai_api |
| 1472 | `/imagine/sharpen` POST | `imagine_sharpen` | json | `claude_spend.json` | imagine_subject, claude_api |
| 1487 | `/imagine/brief` POST | `imagine_brief` | json | `releases/<slug>.json` (image_brief) | imagine, storage |
| 1504 | `/imagine/reference` POST | `imagine_reference` | json | `references/imagine/<scope>/` + index | imagine |
| 1520 | `/imagine/as-reference` POST | `imagine_as_reference` | json | same | imagine |
| 1536 | `/imagine/test-set` POST | `imagine_test_set` | json | 5 renders (paid) | imagine |
| 1562 | `/imagine/composite` POST | `imagine_composite` | json | `generated_images/imagine/<id>.png + .json` (local) | imagine, shoot_catalogue |
| 1584 | `/imagine/img/<path>` | `imagine_image` | file | - | imagine |
| 1593 | `/imagine/ref/<scope>/<path>` | `imagine_ref_file` | file | - | imagine |
| 333 | `/resized/<filename>` | `serve_resized` | file | - | - |
| 1615 | `/artwork-resizer` GET,POST | `artwork_resizer_page` | page | `artwork/<upload>`, `resized/` | artwork_resizer, metadata_utils |
| 1606 | `/video-resizer/source/<path>` | `video_resizer_source` | file | - | - |
| 1863 | `/video-resizer` GET,POST | `video_resizer_page` | page | `videos/<upload>`, `resized_video/` | video_resizer, metadata_utils |
| 2008 | `/resized_video/<filename>` | `serve_resized_video` | file | - | - |
| 3801 | `/shoot` | `shoot_page` | page | - | shoot_catalogue |
| 3904 | `/shoot/thumb/<photo_id>` | `shoot_thumb` | file | `~/.cache/inch-of-shadow/shoot-grades/` | shoot_catalogue, edit_recipe |
| 4020 | `/shoot/covers` | `shoot_covers` | page | - | shoot_pull, cover_fonts |
| 4041 | `/shoot/font/<key>` | `shoot_font` | file | - | cover_fonts |
| 4051 | `/shoot/<photo_id>` | `shoot_photo` | page | cache grid tiles and grades | shoot_catalogue, shoot_pull, edit_recipe, cover_fonts |
| 4073 | `/shoot/full/<photo_id>` | `shoot_full` | file | cache grades | shoot_catalogue, edit_recipe |
| 4096 | `/shoot/grid-tile/<name>` | `shoot_grid_tile` | file | `~/.cache/inch-of-shadow/ig-grid/` | ffmpeg |
| 4104 | `/shoot/pfp` | `shoot_pfp` | file | - | - |
| 4111 | `/shoot/<photo_id>/pull` POST | `shoot_pull_route` | redirect | `generated_images/shoot/<id>_<fmt>.jpg` | shoot_pull |
| 4135 | `/shoot/out/<filename>` | `shoot_out` | file | - | - |
| 4205 | `/fonts` | `fonts_page_view` | page | - | fonts_page |
| 4223 | `/fonts/<fid>` | `font_detail` | page | - | fonts_page |
| 4238 | `/fonts/<fid>/file/<path>` | `font_file` | file | - | fonts_page |
| 4257 | `/playground` | `playground_index` | page/redirect | - | - |
| 4265 | `/playground/<slug>` | `playground_page` | page | - | playground, fonts_page, frame_tokens (subprocess) |
| 4292 | `/playground/<slug>/image` | `playground_image` | file | `$TMPDIR/ios-playground-cache/` | playground, print_looks |
| 4321 | `/playground/<slug>/overlay` | `playground_overlay` | file | - | playground |
| 4331 | `/playground/<slug>/wall` | `playground_wall` | page | - | playground, print_looks |
| 4349 | `/api/playground/<slug>/wall-kept` GET,POST | `playground_wall_kept` | json | `plans/playground-wall/<slug>.json` | playground |
| 4362 | `/playground/<slug>/elements` | `playground_elements` | page | - | playground |
| 4373 | `/playground/<slug>/elements/img` | `playground_element_img` | file | cache | playground |
| 4384 | `/playground/<slug>/ig-grid` | `playground_iggrid` | page | - | playground |
| 4396 | `/playground/<slug>/ig-grid/img` | `playground_iggrid_img` | file | - | playground |
| 4404 | `/playground/<slug>/layout` | `playground_layout` | page | - | playground |
| 4418 | `/playground/<slug>/layout/font` | `playground_layout_font` | file | - | playground |
| 4428 | `/playground/<slug>/layout/extra` | `playground_layout_extra` | file | - | playground |
| 4436 | `/api/playground/<slug>/layouts-kept` GET,POST | `playground_layouts_kept` | json | `plans/playground-wall/<slug>-layouts.json` | playground |
| 4449 | `/api/playground/<slug>/elements-kept` GET,POST | `playground_elements_kept` | json | `plans/playground-wall/<slug>-elements.json` | playground |
| 4463 | `/playground/<slug>/colours` | `playground_colours` | page | - | playground |
| 4476 | `/playground/<slug>/colours/file` | `playground_colour_file` | file | - | playground |
| 4484 | `/api/playground/<slug>/colours-kept` GET,POST | `playground_colours_kept` | json | `plans/playground-wall/<slug>-colours.json` | playground |
| 4497 | `/api/playground/<slug>/wall-hidden` GET,POST | `playground_wall_hidden` | json | `plans/playground-wall/<slug>-hidden.json` | playground |
| 4510 | `/playground/<slug>/accent` | `playground_accent` | file | - | playground |
| 4521 | `/api/playground/<slug>/versions` GET,POST | `playground_versions` | json | `releases/<slug>.json` (versions) | playground, storage |
| 4538 | `/api/playground/<slug>/versions/delete` POST | `playground_version_delete` | json | `releases/<slug>.json` | playground, storage |
| 4572 | `/effects` | `effects_page_view` | page | - | effects_page |
| 4600 | `/effects/<eid>` | `effect_detail` | page | - | effects_page |
| 4614 | `/effects/<eid>/example` | `effect_example` | file | - | effects_page |
| 4625 | `/api/effects/<eid>/flag` POST | `effect_flag` | json | `docs/brand/effects/effects.json` | effects_page |
| 4640 | `/api/releases/<slug>/effects` POST | `release_effect_set` | json | `releases/<slug>.json` (brand.effects) | effects_page, storage |
| 4694 | `/archive` | `archive_page` | page | - | archive, effects_page, imagine |
| 4715 | `/archive/<rid>` | `archive_detail` | page | - | archive |
| 4762 | `/archive/example/<rid>/<i>` | `archive_example` | file | - | archive |
| 4777 | `/archive/thumb/<rid>` | `archive_thumb` | file | - | archive |
| 4791 | `/archive/file/<path>` | `archive_file` | page | - | archive |
| 4820 | `/video` | `video_page` | page | - | frame_tokens |
| 4826 | `/video/start` POST | `video_start` | redirect | `../videos/<name>/` (new project) | start_video_project.py (subprocess) |
| 4846 | `/video/render/<project>/<filename>` | `video_render` | file | - | - |

### Socials area (30 routes)

| Line | Route | Endpoint | Output | Writes | Helpers |
|---|---|---|---|---|---|
| 420 | `/outreach` | `outreach_page` | page | - | outreach |
| 432 | `/outreach/tick` POST | `outreach_tick` | json | `plans/outreach-batches.json` (atomic) | outreach |
| 2896 | `/engagement` | `engagement_page` | page | `engagement_log.json` (queues, seeds) | contact_bridge, storage |
| 2992 | `/api/engagement/engage/<name>` POST | `api_engagement_engage` | json | `engagement_log.json` | - |
| 3025 | `/api/engagement/log-follow` POST | `api_engagement_log_follow` | json | `engagement_log.json` | - |
| 3064 | `/api/engagement/unfollow/<name>` POST | `api_engagement_unfollow` | json | `engagement_log.json` | - |
| 3084 | `/api/engagement/skip/<name>` POST | `api_engagement_skip` | json | `engagement_log.json` | - |
| 3101 | `/api/engagement/hide/<name>` POST | `api_engagement_hide` | json | `engagement_log.json` | - |
| 3111 | `/api/engagement/remove/<name>` POST | `api_engagement_remove` | json | `enriched_contacts.json`, `engagement_log.json` | - |
| 3133 | `/api/engagement/refresh` POST | `api_engagement_refresh` | json | `engagement_log.json` | contact_bridge |
| 3156 | `/api/context/release` POST | `api_context_set_release` | json | `release_context.json`, `engagement_log.json` | contact_bridge, storage |
| 3196 | `/api/context/release` DELETE | `api_context_clear_release` | json | deletes `release_context.json` | contact_bridge |
| 3203 | `/api/engagement/tag-genre` POST | `api_engagement_tag_genre` | json | `enriched_contacts.json` | - |
| 3277 | `/api/contacts/change-category` POST | `api_contacts_change_category` | json | `enriched_contacts.json` | - |
| 4906 | `/promotion` | `promotion_page` | page | `release_context.json` when `?release=` is real | contact_bridge, storage |
| 5069 | `/api/promotion/add-target` POST | `api_promotion_add_target` | json | `promotion_log.json` | - |
| 5097 | `/api/promotion/remove-target` POST | `api_promotion_remove_target` | json | `promotion_log.json` | - |
| 5117 | `/api/promotion/clear-targets` POST | `api_promotion_clear_targets` | json | `promotion_log.json` | - |
| 5134 | `/api/promotion/update-status` POST | `api_promotion_update_status` | json | `promotion_log.json` | - |
| 5165 | `/api/promotion/press-kit/<slug>` | `api_promotion_press_kit` | json | `promotion_log.json` (stamp) | `_generate_press_kit` |
| 5186 | `/api/promotion/update-bio` POST | `api_promotion_update_bio` | json | `promotion_log.json` | - |
| 5197 | `/api/promotion/update-press-contact` POST | `api_promotion_update_press_contact` | json | `promotion_log.json` | - |
| 5218 | `/api/promotion/email-compose/<slug>/<name>` | `api_email_compose` | json | - | email_outreach |
| 5305 | `/api/promotion/save-draft` POST | `api_save_draft` | json | `promotion_log.json` | - |
| 5330 | `/api/promotion/send-email` POST | `api_send_email` | json | `release_manager/email_send_state.json`, `promotion_log.json`; sends via Gmail SMTP | email_outreach |
| 5541 | `/api/promotion/check-file` POST | `api_check_file` | json | - (stat only, repo root) | - |
| 5588 | `/sc-automation` | `sc_automation_page` | page | - | sc_engagement |
| 5602 | `/api/sc-automation/status` | `api_sc_status` | json | - | sc_engagement |
| 5611 | `/api/sc-automation/run` POST | `api_sc_run` | json | live run only with `SC_ALLOW_LIVE_RUNS`: tracker, log, contacts, seeds, rejected; dry run ? | sc_engagement |
| 5675 | `/api/sc-automation/test-auth` | `api_sc_test_auth` | json | `.sc_user_token.json` only on refresh ? | sc_engagement |

### Stats area (10 routes)

| Line | Route | Endpoint | Output | Writes | Helpers |
|---|---|---|---|---|---|
| 5398 | `/stats` | `stats_page` | page | `generated_images/stats_thumbs/` | stats_tracks, score_board, stats/weekly_view, weekly_summary, storage, targets, spotify_s4a, ig_followback, bandcamp_import |
| 5413 | `/stats/thumb/<path>` | `stats_thumb` | file | - | stats/weekly_view |
| 5423 | `/stats/sync` POST | `stats_sync_form` | redirect | `stats_snapshots/snapshot_<ts>.json`, `.sc_user_token.json` on refresh | stats/collectors, storage |
| 5433 | `/stats/manual` POST | `stats_manual_form` | redirect | `stats_snapshots/manual_entries.json` | stats/storage |
| 5459 | `/api/stats/sync` POST | `api_stats_sync` | json | snapshot, token on refresh | stats/collectors, storage |
| 5474 | `/api/stats/overview` | `api_stats_overview` | json | - | stats/storage |
| 5480 | `/api/stats/time-series` | `api_stats_time_series` | json | - | stats/storage |
| 5499 | `/api/stats/manual-entry` POST | `api_stats_manual_entry` | json | `manual_entries.json` | stats/storage |
| 5530 | `/api/stats/snapshots` | `api_stats_snapshots` | json | - | stats/storage |
| 5566 | `/api/stats/bandcamp` | `api_stats_bandcamp` | json | - | stats/bandcamp_import |

### System area (7 routes)

| Line | Route | Endpoint | Output | Writes | Helpers |
|---|---|---|---|---|---|
| 392 | `/tickets` | `tickets_page` | page | - | tickets, board |
| 448 | `/board` | `board_page` | page | - | board |
| 461 | `/api/board/cards` | `api_board_cards` | json | - | board |
| 372 | `/palette` | `palette` | page | - | - |
| 2020 | `/api/palette/save` POST | `api_palette_save` | json | `theme.json` | - |
| 3706 | `/autopilot` | `autopilot_page` | redirect | - | - |
| 345 | `/favicon.ico` | `favicon` | file | - | PIL |

Shared, not in any area: context processor (line 258: theme + genres), 3 template filters, CSRF
set-up (lines 109-135), 404 handler (363). Files written by helpers that no route reaches (automation
or CLI): `stats_snapshots/ig_followback.json`, `spotify_s4a.json`, `plans/weekly-stats.md`,
`plans/control-panel/shoot-catalogue.json`, `docs/brand/recipes/*`, `scene_intelligence/sc_following_audit.json`.

Biggest route functions: `artwork_resizer_page` 178 lines, `promotion_page` 160, `video_resizer_page` 142,
`release_edit` 116, `engagement_page` 93, `release_detail` 87, `api_email_compose` 84. Biggest helpers
outside routes: `_generate_press_kit` (143 lines), `_daily_briefing` (136), `_build_platform_queue` (128).

## 3. RM 2.0 blueprint

### 3a. Five Flask blueprints

| Blueprint | Module | Pages | Routes | Helper modules it owns | Tests that guard it today |
|---|---|---|---|---|---|
| `release` | `release_manager/views/release.py` | `/`, `/release/*`, `/seo-copy`, `/bios` | 26 | models, storage, timeline, checklist, seo_copy_generator, bio_manager, writers_ai, brand_context, copy_pass | `test_dashboard_lines`, `test_finished_releases_go_quiet`, `test_make_block`, `test_write_with_both`, `test_copy_writers_api` |
| `studio` | `release_manager/views/studio.py` (one file per corner if it grows: edit, imagine, shoot, playground, library) | `/edit`, `/imagine`, `/artwork-resizer`, `/video-resizer`, `/video`, `/shoot`, `/fonts`, `/playground`, `/effects`, `/archive` | 72 | photo_edit, imagine*, artwork_resizer, video_resizer, shoot_catalogue, shoot_pull, edit_recipe, cover_fonts, fonts_page, playground, print_looks, effects_page, archive | `test_photo_editor_page`, `test_imagine_page/round/review/subject`, `test_resizer_pages`, `test_artwork_resizer`, `test_video_page`, `test_shoot_page`, `test_fonts_page`, `test_playground`, `test_effects_page`, `test_archive` |
| `socials` | `release_manager/views/socials.py` | `/outreach`, `/engagement`, `/promotion` (if kept), `/sc-automation` | 30 (19 if `/promotion` drops) | outreach, contact_bridge, email_outreach (both go with `/promotion`) | `test_engagement_page`, `test_email_outreach_hardening` |
| `stats` | `release_manager/views/stats.py` | `/stats` | 10 | score_board, stats_tracks, `stats/*` | `test_stats_page`, `test_stats_bandcamp_card`, `test_score_board`, `test_weekly_view` |
| `system` | `release_manager/views/system.py` | `/tickets`, `/board`, `/palette` (if kept), `/autopilot` (if kept), favicon, 404 | 7 | tickets, board | `test_tickets`, `test_board` |

`webapp.py` shrinks to the app object, CSRF, context processor, filters, blueprint registration and the
names tests import today (`app`, `list_releases`, `_dashboard_lines`, `VIDEOS_DIR`, `SHOOT_CATALOGUE`,
`ARTWORK_PRESETS`, `VIDEO_PRESETS`, `_video_frames`) re-exported, so `from release_manager.webapp import app`
in 14 test files keeps working.

The one real cost: blueprints prefix endpoint names (`stats.stats_page`). Templates call `url_for(...)`
176 times and `webapp.py` 47 times. Each area's move changes its `url_for` strings in the same commit,
nowhere else, which is why the order below starts with the areas few templates link to.

### 3b. The home page

Replaces the Dashboard briefing. Four blocks, all from files that exist today:

1. Scoreboard: `score_board.build()` over `plans/targets.json` (period 2026-11-01 to 12-31, approved by
   Amir 11-01): IG followers (ladder 996 / 1,026), IG follow-back (floor 20%), IG reach 30d (collecting),
   SoundCloud followers (ladder), Spotify monthly listeners (ladder), TikTok followers (collecting).
   One card per metric with the rung line and the 30-day sparkline, same as the top of `/stats` today.
   Adding Spotify followers, pre-saves and the email list is code-map change 2, not this step.
2. Now: tickets from `plans/tickets.json` with `bucket: now` (7 open today), shown as "🎵 Release 2"
   style labels, grouped by the six areas. Next (12) folded under one line.
3. Decisions waiting: open tickets with `who: amir` or `blocked_on` naming Amir (22 today), one line each
   with the `next_step` field. This is the list Amir reads first; it replaces the briefing text.
4. Next release: title, date or "open", days to go, checklist progress, from the one release file
   (change 3 makes that file exist for the EP). Release cards for finished releases move to `/release`.

Dropped from the home page: the Intenso mount check, the `promotion_log.json` read, the artwork scan.
The `/board` Control Panel count stays as one line until the merge question is answered.

### 3c. Order to split, tests green at every step

0. Guard first: one smoke test that GETs all 23 page routes and expects 200 or 302 (today only 16 of
   23 pages have a test), plus the one-line page-view log from code-map change 8. Commit. Run
   `pytest -q -x` (1,136 today).
1. `stats` blueprint (10 routes, 2 templates, `url_for` only inside `stats.html` and the nav): the
   smallest real area with the most tests per route.
2. `system` blueprint (`/tickets`, `/board`, `/palette`, `/autopilot`, favicon, 404): 6 routes, linked
   from the nav, `tickets.html`, `board.html`, `dashboard.html`. Drop `/autopilot` and `/palette` here
   if Amir says yes, so they are never ported.
3. `socials` blueprint, after Amir's `/promotion` answer and the owners' `/engagement` and
   `/sc-automation` answers: no template outside the area links in, so the move is mechanical. If
   `/promotion` drops, `email_outreach.py` and `contact_bridge.py` go to `archive/` in the same commit
   (they are listed in `dead-code-list-2026-11-05.md` section C for this reason).
4. `studio` blueprint in five commits, smallest coupling first: archive + effects + fonts (link to
   `release_detail`, which stays an app-level name until step 5); shoot + edit; imagine; playground
   (busiest today, uncommitted edits, so last of Studio); resizers + video (merge decision first).
5. `release` blueprint last: `release_detail` is linked from archive, effects, fonts, forms and the
   dashboard, so its `url_for` strings change in the most templates. Dashboard becomes the home page
   of 3b in this step or the next.
6. `webapp.py` is now the app factory (~300 lines). Delete nothing from `templates/` until the smoke
   test proves each page still renders.

Each step: one commit, `pytest -q -x`, start `python -m release_manager.webapp`, open the moved pages.
Parallel chats: one area per chat, never two chats in `webapp.py` at once (the reason for the split).
