# Gap Radar: uses per repo (2026-11-05)

One engine (this folder), many "profiles". A profile = which sources, which search
phrases, which question Claude answers, and where the report goes. The engine stays
here; each repo gets profiles and reads its own reports.

Shared rules: private research only (Reddit terms), HikerAPI = IG agent first, radar
takes only the leftover of the 300/day cap. Gero data and code never come into this
repo (NDA); Gero reports live in the Gero folder.

## Lane 1: Income (+500 EUR) - main chat
| Profile | Question | Sources |
|---|---|---|
| income-gaps | What do people already pay for and hate? | Reddit, HN, App Store, Stack Exchange, GitHub |
| owned-leverage | Which gap runs on our paid tools (Claude credit, Discogs, alert engine)? | same + our asset list |

## Lane 2: Inch of Shadow (this repo)
| Profile | Question | Sources | Feeds |
|---|---|---|---|
| producer-tools | What tools/plugins/workflows do producers ask for or complain about? | r/WeAreTheMusicMakers, r/ableton, r/edmproduction, r/synthesizers, YouTube comments | his own music work, Gear/tools |
| song-ideas | What feelings, scenes, stories do darkwave/post-punk listeners talk about? | r/postpunk, r/darkwave, r/coldwave, YouTube comments on neighbour artists | songs (Words docs) |
| brand-marketing | What do listeners of R. Missing / The Cure / Crystal Castles share, love, hate about artist content? | Reddit, YouTube comments, IG comments (HikerAPI leftover) | brand, IG Expert content plan |
| ig-hooks | Which questions and words repeat in comments of top posts in our hashtags? | HikerAPI (leftover only), YouTube | IG captions, reel hooks |
| music-seo | Which words do people use to search/describe this sound? | Reddit, YouTube titles/comments, SoundCloud tags | music-platform-seo, release-platforms skills, Bandcamp/SC tags |
| scene-outreach | Which blogs, radios, playlists, promoters do fans recommend? | Reddit, YouTube | Scene Intelligence, Promotion agent |

## Lane 3: Gero (A.D. Labs work, separate folder)
| Profile | Question | Sources | Feeds |
|---|---|---|---|
| crypto-wallet-pains | What do Cardano / wallet users complain about or ask for? | r/cardano, r/CryptoCurrency, HN, App Store reviews of wallets | product + support content |
| gero-seo-topics | Which questions repeat that an article can answer? | Reddit, Stack Exchange (cardano.stackexchange), YouTube | Gero SEO content pipeline (keywords -> articles) |
| card-competitors | What do users say about Wirex / other crypto cards? | Reddit, App Store reviews | Gero Card marketing |

## Lane 4: apartmentcode (later)
The alert engine (scrape -> filter -> Telegram) is the reverse of the radar: radar
finds needs, alert engine delivers them. A weekly radar digest could go to Telegram.
