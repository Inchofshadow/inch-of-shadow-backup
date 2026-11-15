# Half the Night EP: where a description shows, and what it does (2026-11-10)

Status labels: [VERIFIED] = from an official spec or our own data; [HYPOTHESIS] = my read, to check; [CHECK] = look on the live form.

| Place | Public? | Indexed by Google / platform search? | Length | What it does for us |
|---|---|---|---|---|
| Symphonic release form | ❓ | ❓ | ❓ | [CHECK] Symphonic's own XML docs and metadata guide list no description field ([XML docs](https://symphonic.com/wp-content/uploads/2023/09/Symphonic-XML-Documentation.pdf), [metadata guide](https://blog.symphonic.com/2023/04/18/how-to-input-your-metadata-in-the-sms/)). Our past releases have a `description` in the release file, but that's our own field. If the form has one, it's likely Beatport-only ([Revelator checklist](https://revelator.com/blog/metadata-checklist-for-music-distribution): "optional, recommended for platforms like Beatport"). We don't use Beatport. |
| Spotify | no public release text | no | pitch: 500 chars | [HYPOTHESIS] Spotify shows no release description. The only text is the **editorial pitch** in Spotify for Artists (editors only) and the artist bio. The pitch matters, the release text doesn't. |
| Apple Music | no field for indie releases | no | - | [HYPOTHESIS] Apple's notes are editorial only. |
| Bandcamp "about" | yes | yes, Google indexes Bandcamp album pages | long | The strongest public text: words people search ("acid", "dark disco", "Berlin") plus the credits. Feeds the Bandcamp tags we set on 11-03. |
| SoundCloud description | yes | yes (SoundCloud search + Google) | long | Discovery text + links (smart link, Bandcamp ?campaign=). Our SC tags are set (Dark Disco + electro, acid, EBM, italo disco, Berlin). |
| YouTube description | yes | yes, YouTube search reads it | 5000 | First 2 lines count most: track, artist, the sound words, then links and credits. Handled by yt_apply. |
| Spotify pitch | no (editors) | no | 500 | Sound + mood + context ("for the late hours, Berlin"), the genre fields set on 11-03, and the story. Written once the release shows in Spotify for Artists. |

## So what needs writing

1. **One core text** (2-3 lines, his voice): the sound in his words. It's reused on Bandcamp, SoundCloud and YouTube, each with its own top line and links. The draft in `plans/half-the-night-symphonic-sheet.md` is the starting point.
2. **The Spotify pitch** (500 chars): separate, written when the release appears.
3. **Symphonic:** only if the form has a field. If it does, use the core text. It doesn't block the submit if the field is optional. [CHECK on the form.]

All texts in his voice need Amir's approval in the main EP chat.
