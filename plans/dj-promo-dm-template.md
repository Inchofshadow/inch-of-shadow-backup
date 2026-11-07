# DJ Promo DM Template

Reusable direct-message template for sending new releases to DJs. Use for the DJ
promo pool in `scene_intelligence/dj_promo_targets.json`. DJs only, not labels,
blogs, or premiere channels (those have their own templates).

Source: the message Amir sent to Ilayda (ilayddab) for the Farewell single on
2026-05-16. Kept verbatim in voice, emojis included, since this is Amir's
natural DM style.

## Template (cold / warm-discovery DJs)

```
Hi [NAME], how are you? :)

I've been listening to some of your sets and I really like your style and taste! I just released a new track, "[TRACK]" [ONE-LINE TRACK DESCRIPTION], and I'd love to send it to you.

[SOUNDCLOUD TRACK LINK]

Happy to send you the WAV as well if you want.

Hope you'll like it :)
Thank you so much! 🙏
```

## Placeholders

- `[NAME]` first name or handle of the DJ
- `[TRACK]` release title, e.g. Farewell
- `[ONE-LINE TRACK DESCRIPTION]` short sound hook. Farewell: `a heavy EBM bassline with an acid melody`
- `[SOUNDCLOUD TRACK LINK]` the SoundCloud track URL

## Filled example (Farewell, sent to Ilayda)

```
Hi Ilayda, how are you? :)

I've been listening to some of your sets and I really like your style and taste! I just released a new track, "Farewell" a heavy EBM bassline with an acid melody, and I'd love to send it to you.

https://soundcloud.com/inch-of-shadow/inch-of-shadow-farewell

Happy to send you the WAV as well if you want.

Hope you'll like it :)
Thank you so much! 🙏
```

## Tier adjustments

- **Cold / warm-discovery DJs** use as-is. Keep the "listening to your sets" line only if it is actually true for that DJ.
- **Personal contacts** (friends you already know) the "I've been listening to your sets, I really like your style" opener reads as inauthentic between people who know each other. Rewrite casually in your own voice.
- **Prior no-reply** (already pitched an earlier track, got no answer) do not frame it as a first contact. A lighter "new one is out, thought of you" works better than the full opener:

```
Hi [NAME], how are you? :)

I just released a new track, "[TRACK]" [ONE-LINE TRACK DESCRIPTION]. Thought of you, would love to send it your way.

[SOUNDCLOUD TRACK LINK]

Happy to send the WAV too if you want.

Hope you like it :)
```

## Notes

- Manual send only. Space DMs across days, do not fire many in one sitting. IG spam detection can flag a personal account even for hand-sent messages.
- Update the target's `status` to `sent` in `dj_promo_targets.json` after each send.
