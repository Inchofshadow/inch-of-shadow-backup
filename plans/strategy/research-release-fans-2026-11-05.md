# Release fans research, 2026-11-05

Text-only web research, builds on `review-2026-11-05-research.md` (not repeated here). Official = Spotify/vendor own pages. "(weak)" = practitioner, vendor marketing or secondhand. Prices fetched 2026-11-05, check again before paying.

## 1. Pre-save + follow tools in 2026

| Tool | Spotify follow on pre-save | Email capture | Free tier | Paid | Data/GDPR |
|---|---|---|---|---|---|
| Feature.fm | Yes: 1 follow button on Free; "Spotify multiple follows" on Artist (1) and Pro Artist (3) | Collects unlimited on all plans, but Free cannot SEE the emails ("upgrade to access"); Basic 50/link, Artist 200/link | 1 pre-save service, unlimited pre-save links, 7 days analytics | Basic $8, Artist $19, Pro Artist $39 /mo | Not checked on its policy page (gap) |
| Hypeddit | Follow steps on gates (weak, blog) | "Fan Email Collection" from Basic | Rookie: smart links + download gates; pre-saves NOT listed on Free | Basic $9, Pro $13, Elite $99 /mo | Acts as data controller (weak, unofficial processor list) |
| Laylo | "presaves and auto-follow" on drop pages | Email, SMS, IG DM per signup | "Try for free", limits not published | $25/mo + messaging ($10 per 5,000 emails, $10 per 650 SMS) | SOC 2 + GDPR badges; no retention detail on page |
| ToneDen | Not usable | n/a | n/a | n/a | Owned by Eventbrite; all FanLinks broke in March 2024 |
| Symphonic | Own pre-save under SymphonicMS "Share Music"; plus Feature.fm partner offer under Marketing > Featured Partners | Not stated | Included for clients (details unconfirmed) | Not stated | Not stated |

Sources:
- Feature.fm Pricing, feature.fm, fetched 2026-11-05, https://www.feature.fm/pricing
- Hypeddit Pricing, hypeddit.com, fetched 2026-11-05, https://hypeddit.com/pricing
- Laylo for music, laylo.com, fetched 2026-11-05, https://laylo.com/music ; Laylo Shopify listing (message bundles), https://apps.shopify.com/laylo
- "All ToneDen FanLinks are broken, admits Eventbrite", Hypebot, 2024-03, https://www.hypebot.com/all-toneden-fanlinks-tourlinks-biglinks-are-broken-admits-eventbrite
- "How to Set Up a Music Pre-Save Before Release Day", Symphonic Blog, https://blog.symphonic.com/?p=57369 ; "Symphonic partners with Hypeddit" (free pre-saves for clients), Symphonic Blog, 2021-06-24, https://blog.symphonic.com/2021/06/24/symphonic-partners-with-hypeddit-2 (old)
- Hypeddit data role: https://download.unison.audio/datasubprocessors (weak, not Hypeddit's own domain)

Spotify scope status:
- The `user-follow-modify` scope (Follow/Unfollow Artists) still exists with no deprecation note. Source: "Scopes", Spotify for Developers, fetched 2026-11-05, https://developer.spotify.com/documentation/web-api/concepts/scopes
- Since 2025-05-15 new Extended Quota access goes only to "established, scalable" apps; development-mode apps were cut further in Feb 2026 (Premium needed, small user cap). Effect: a self-built pre-save is not realistic; only existing large vendors can run pre-saves for strangers. Sources: "Updating the Criteria for Web API Extended Access", Spotify Developer Blog, 2025-04-15, https://developer.spotify.com/blog/2025-04-15-updating-the-criteria-for-web-api-extended-access ; "Update on Developer Access and Platform Security", Spotify Developer Blog, 2026-02-06, https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security (user cap of 5 is secondhand, weak)
- Privacy note: a pre-save asks the fan to grant a third party account permissions; 2019 reports showed label pre-saves requesting follow management and listening data. Source: "Spotify pre-saves give labels troubling data control", Hypebot, 2019, https://www.hypebot.com/spotify-pre-saves-give-labels-troubling-data-control (old)
- Fans must re-authorize third-party apps every 6 months, which limits "forever saves". Source: Hypebot "3 new Spotify updates", https://www.hypebot.com/3-new-spotify-updates-that-are-changing-music-marketing.md (weak, date unclear)

## 2. EP vs singles for a 2-track release

- A 2-track release is a SINGLE on Spotify (1-3 tracks under 30 min). So "Half the Night" as 2 tracks shows as a single, whatever we call it. Sources: FreshTunes "Release types", https://wiki.freshtunes.com/en/freshtunes/creating-managing-release/release-types ; Amuse "Singles, EPs and albums", https://support.amuse.io/en/articles/107733-singles-eps-and-albums (distributor docs, no Spotify primary found)
- Release Radar: each listener gets ONE song per artist per week; a pitched song (pitch 7+ days ahead) is the one included; without a pitch Spotify picks. A listener who already played that track can get another track from the same release; an unplayed track can stay up to 4 weeks. Source: "Getting music on Release Radar", Spotify for Artists Support, fetched 2026-11-05, https://support.spotify.com/us/artists/article/getting-music-on-release-radar/
- Pitch: "You can only pitch one song at a time"; after it goes live you can pitch another unreleased song. Released songs are no longer eligible, so track 2 of a released 2-track single can never be pitched. Editors may still pick a different song from the release. Source: "Pitching music to playlist editors", Spotify for Artists Support, fetched 2026-11-05, https://support.spotify.com/us/artists/article/pitching-music-to-playlist-editors/
- What happens to track 2 in one drop: it gets no pitch of its own, and only reaches Release Radar as a fallback for fans who already played track 1. Two separate releases = two pitches and two Release Radar pushes. (derived from the two official pages above)
- Common practice "waterfall": release track 1, then a 2-track release later containing track 1 + new track 2, so the new song gets a pitch while streams stay on one ISRC. (weak, practitioner) Source: Dynamoi "How many songs can you pitch from an album", https://dynamoi.com/learn/playlist-pitching/how-many-songs-can-you-pitch-from-an-album

## 3. Email list for small artists

| Option | Cost at our size (16 to ~250) | Double opt-in | Data/GDPR |
|---|---|---|---|
| Bandcamp followers + mailing list | Free | Not documented | Fans opt in on purchase/follow; free downloads can require email. Bandcamp help does not document an export or a send tool (gap). Source: "How do I collect emails", Bandcamp Help, https://get.bandcamp.help/en/articles/15263065-how-do-i-collect-emails |
| Buttondown | Free up to 100 subscribers; paid add-ons from $9/mo | Not stated on pricing page (gap, check docs) | US company; DPA covers EU subscribers, 72h breach notice, public sub-processor list (DPA updated 2026-03-16). Sources: https://buttondown.com/pricing ; https://buttondown.com/legal/data-processing-agreement ; https://buttondown.com/changelog/2026-03-16-legal-docs-refresh |
| Mailchimp | Free cut to 250 contacts / 500 sends per month in Feb 2026; unsubscribed contacts count | Available (not checked) | US company. (weak, third-party reports) Source: beehiiv "Mailchimp's 2026 free plan changes", https://www.beehiiv.com/blog/navigating-mailchimp-s-new-free-limits-essential-updates-for-newsletter-owners |
| Laylo | From $25/mo + messaging | Not stated | See section 1 |
| Feature.fm capture | Free collects but hides emails; $8/mo for 50 per link | Not stated | See section 1 |
| Substack | Not researched (gap) | | |

- Germany: UWG section 7 needs prior express consent; neither GDPR nor UWG names double opt-in, but the BGH (I ZR 164/09, 2011-02-10) treats confirmed opt-in as the workable proof of consent. So double opt-in is the practical standard here; the confirmation mail must contain no advertising. Sources: IT-Recht Kanzlei "Double-Opt-In Newsletter", https://www.it-recht-kanzlei.de/double-opt-in-newsletter.html ; CMS "Double-Opt-In nach dem OLG München", https://cms.law/de/deu/legal-updates/double-opt-in-nach-dem-olg-muenchen-beisst-sich-die-katze-in-den-schwanz (law-firm notes, not the rulings)
- Gig/merch-table opt-in rate: no published benchmark found. Only website pop-up figures exist (3% "strong", 5-6% niche genres, secondhand OptinMonster). (weak) Source: Orphiq "How to build an email list as a music artist", https://orphiq.com/resources/email-marketing-musicians . Practitioners advise a stage call-out + QR at merch and measuring your own rate per show. Source: CD Baby DIY Musician "Numbers don't lie", https://diymusician.cdbaby.com/music-career/numbers-dont-lie-live-show-effective/ (weak)

## 4. Spotify for Artists features under 1k followers

| Feature | Available to us? | Official rule |
|---|---|---|
| Artist Pick | Yes | Admin/Editor sets it; songs, albums, videos, playlists, concerts, merch; live 180 days. "Managing your Artist Pick", https://support.spotify.com/bf-en/artists/article/managing-your-artist-pick/ |
| Canvas | Yes | 3-8 s, 9:16, MP4/JPG; first main artist with Admin/Editor role. "Adding a Canvas", https://support.spotify.com/us/artists/article/adding-a-canvas/ ; "Canvas guidelines", https://support.spotify.com/us/artists/article/canvas-guidelines/ |
| Clips | No (for anyone) | New Clips uploads ended 2026-06-17; existing ones stay; full-length video upload rolling out to "eligible artists" (criteria not given). "Clips", https://support.spotify.com/us/artists/article/clips/ |
| Countdown Pages | No | 3,000 monthly ACTIVE listeners (page undated; other pages say 5,000), and albums/EPs only, singles not eligible. "Getting started with Countdown Pages", https://support.spotify.com/artists/article/getting-started-with-countdown-pages-on-spotify/ |
| Showcase | Probably no | 1,000 streams in last 28 days in one target market; Germany is a supported billing country; budget-based, 14 days. "Getting started with Marquee and Showcase", https://support.spotify.com/us/artists/article/getting-started-with-campaign-tools/ |
| Marquee | No | Same 1,000 streams + 5,000 monthly active listeners in target market; 10 days. Same source. |

Note: the 3,000 Countdown figure is lower than the 5,000 in the previous review; Spotify pages conflict. Either way, a 2-track release counts as a single and is not eligible.

## Options for us

- Feature.fm Free for the "Half the Night" pre-save with 1 Spotify follow button. Cost $0. Privacy: fan grants Feature.fm Spotify permissions; emails collected but we cannot see them, so turn email capture off on Free.
- Feature.fm Basic for one month around release ($8) only if we want the emails (50 per link). Privacy: Feature.fm holds fan emails as a third party; policy not yet read, read before buying.
- Symphonic's own pre-save in SymphonicMS first, to see if it has a follow step. Cost $0. Privacy: data stays with our existing distributor; check what it asks fans for.
- Split the two tracks into two releases (or waterfall track 1 into the second release) to get two pitches and two Release Radar pushes. Cost $0. Privacy: none.
- Email: keep Bandcamp as the free base; if we want our own list, Buttondown Free (to 100) with double opt-in turned on. Cost $0. Privacy: US processor with EU DPA, minimal data; Mailchimp's 250-contact Free is the fallback, also US.
