# Clip pack schema (System 79, card S10)

Built 2026-11-06 from `plans/strategy/research-clip-pack-2026-11-06.md` (approved as S10).
Code: `release_manager/clips.py`. Page: the "Clip pack" block on RM `/release/<slug>`.
Tests: `tests/test_clips.py` with `tests/fixtures/clip-pack-release.json`.

## Where it lives

One `clips` block inside `releases/<slug>.json`, one entry per track. Everything is a
timecode in seconds inside the song. No audio files: the masters are exported silent and
the song is attached in each app (TikTok sound page, Instagram music library, Shorts audio
picker), so a cut's audio is a timecode, never a file.

```json
"clips": {
  "version": 1,
  "tracks": [
    {
      "number": 1,
      "tiktok": {"start": 72.0},
      "hook_bar": {"start": 72.0, "length": 3.5},
      "canvas": {"length": 5.0, "source": "night-walk-loop.mp4", "height_px": 1080, "confirmed": true},
      "shorts_preview": {"start": null, "duration": null, "start_date": ""},
      "used_in": [
        {"platform": "instagram", "post": "https://www.instagram.com/reel/abc/", "date": "2026-11-20", "cut": "A1", "kind": "post"}
      ]
    }
  ]
}
```

`ensure_clips(rel)` adds the block and one entry per track with every value empty.
Saving goes through `save_release_clips` / `save_clips`, which re-read the release file,
copy it once a day to `releases/<slug>.bak.<YYYYMMDD>_clips.json`, and write back through
the normal `save_release`, so every other key of the file stays as it is.

## Fields

| Field | Holds | Rule the validator enforces | Spec and source |
|---|---|---|---|
| `tiktok.start` | start of the 60 s clip Symphonic delivers to TikTok, in seconds | 0 or more; before the track end when the track duration is known. The window end (start + 60) and the HH:MM:SS Symphonic value are derived, not stored | "The duration of the clip we send to TikTok is 60 seconds long", field "Clip Start Time", format HH:MM:SS, editable after delivery (Symphonic TikTok Overview, OFFICIAL, read via search index); change takes up to about 2 weeks (TuneCore, OFFICIAL). Every TikTok cut with the library sound must sit inside this window |
| `hook_bar.start`, `hook_bar.length` | the fixed audio section that opens every reel, short and TikTok before release | both or neither; length 0.5 to 60 s; when a TikTok start is set the bar must sit inside the TikTok window; ends before the track end | one Shorts audio snippet for all pre-release content (artists.youtube pre-release guide, OFFICIAL); TikTok sound pages aggregate every video on one sound (OFFICIAL). Research change 1 and 2: the audio stays fixed, the first frame changes per post, and the bar sits inside the TikTok window so the best part is usable with the library sound |
| `canvas.length` | the Spotify Canvas loop length in seconds | 3 to 8 | Spotify Canvas guidelines (OFFICIAL): 3 to 8 s loop, 9:16, MP4 or JPG |
| `canvas.height_px` | the delivered height | 720 to 1080 when set | Spotify Canvas guidelines (OFFICIAL): 720 to 1080 px tall |
| `canvas.source` | the footage file or shot note the loop comes from | free text | research change 7: Canvas is its own object, footage, not a timecode of the song |
| `canvas.confirmed` | Amir ticked the content rules | boolean, shown as "rules confirmed" / "rules not confirmed yet" | Spotify Canvas content policy (OFFICIAL): silent, no talking or singing, no rapid cuts, no links, no handle, no other brands; our rule: no sting |
| `shorts_preview.start`, `shorts_preview.duration` | the YouTube Shorts Preview window | both or neither; duration 30 to 60 s; ends before the track end | DDEX ERN 3.6+ Shorts Preview: StartPoint and Duration (30 to 60 s), delivered only via the distributor (YouTube "Deliver Shorts previews", OFFICIAL). Leave empty until Symphonic says it delivers them (open question 1) |
| `shorts_preview.start_date` | ClipPreviewStartDate, when the preview goes live | YYYY-MM-DD, before the release date | same DDEX field; trailer about two weeks before release (artists.youtube, OFFICIAL) |
| `used_in[]` | every place a cut went: `platform` (tiktok, instagram, youtube), `post` (id or URL), `date` (YYYY-MM-DD), `cut` (label or hash of the cut), `kind` (post, trial, repost, replace_audio; default post) | all five present and in range; **the same cut never goes twice to the same platform**: a second `post` or `trial` of one cut label on one platform is refused. `repost` and `replace_audio` reuse a cut and pass | Instagram recommends only the original of identical content and ranks reels "already posted on Instagram" lower (Originality page, Mosseri 2023, OFFICIAL); TikTok does not recommend "duplicated content" (OFFICIAL 2020). Reuse goes to Repost (IG, TikTok), Replace audio (IG posts and carousels) or a new cut from the same footage (research change 5). A different first frame is a different cut: give it a new label or record its hash |

Time input on the page accepts seconds (`72.5`) or minutes (`1:12.5`); it is stored as a
float of seconds. Frames are never the unit.

Not in the block on purpose: `tiktok_extra_clips` (open question 2), `content_id_note`
(open question 3), Spotify Clips (closed to new uploads since 2026-06-17, research change 9),
`master_cuts[]` with files and safe-zone notes (the cuts themselves live in `videos/` and
`resized_video/`; the pack only names them through `used_in.cut`).

## Open: three Symphonic questions

Unanswered on 2026-11-06; the fields above are built so the answers slot in without a
schema change.

1. **Shorts Previews on Starter.** Can the Starter plan deliver YouTube Shorts Previews
   (DDEX ERN 3.6, StartPoint, Duration, ClipPreviewStartDate)? Until yes, `shorts_preview`
   stays empty and the page says "only if Symphonic delivers it".
2. **More than one TikTok clip per track.** TikTok accepts up to three clips per track via
   some distributors (EmuBands, OFFICIAL, 2026-07-06; UnitedMasters 15 to 60 s). Does
   Symphonic offer it? Until yes, there is one `tiktok.start` per track.
3. **Content ID whitelist.** Is Content ID on for his tracks, and can his own channel be
   whitelisted? Any Short over one minute with an active claim is blocked (YouTube, OFFICIAL),
   so until the answer every shared cut stays at 60 s or under.

Symphonic support pages returned 403 on 2026-11-06; the Clip Start Time text was read from
the search index. Symphonic mail is read in his browser, never through the connector
(memory: symphonic-account-number).
