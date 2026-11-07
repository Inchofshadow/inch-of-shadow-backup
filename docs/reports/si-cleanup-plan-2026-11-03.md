# SI cleanup dry run (2026-11-03)

Nothing has changed yet. On Amir's yes, `si_cleanup.py apply` backs up SI, then applies the OK items only.
REVIEW items are skipped unless he names them (for example "also I-012, M-004").

| | OK | REVIEW |
|---|---|---|
| Step 2: new SI contacts | 109 | 54 |
| Step 3: duplicate merges | 21 | 11 |

SI now: 1214 contacts. After OK items: 1302.

## Step 3, REVIEW (looks like different contacts)

| id | records | why |
|---|---|---|
| M-001 | melopeerecords + Melopee Records | different SoundCloud accounts |
| M-002 | Positive Source + Positive Source | different kinds (dj/label) |
| M-003 | discopastors + Disco Pastors | different kinds (dj/label) |
| M-007 | espaciocielo + Espacio Cielo | different kinds (dj/label) |
| M-019 | cultivated_electronics + Cultivated Electronics | different IG handles; different SoundCloud accounts; different kinds (dj/label) |
| M-021 | Pye Corner Audio + Pye Corner Audio | different SoundCloud accounts; different kinds (dj/label) |
| M-022 | Mechatronica + Mechatronica | different SoundCloud accounts; different kinds (dj/label) |
| M-023 | Axylone Recordings + Gated Recordings | names differ |
| M-027 | Local Suicide + Local Suicide + Local Suicide | different kinds (curator/dj) |
| M-029 | Unhuman + Unhuman | different IG handles |
| M-032 | Casket Cassette + Casket Cassette | different kinds (curator/dj) |

## Step 3, OK (same contact twice)

| id | records | kept as |
|---|---|---|
| M-004 | belaria___ + Belaria | Belaria |
| M-005 | bonnie_spacey + Bonnie Spacey | Bonnie Spacey |
| M-006 | artoffact_records + Artoffact Records | Artoffact Records |
| M-008 | bitterbabe_ + Bitterbabe | Bitterbabe |
| M-009 | triplevisionrecorddistribution + Triple Vision Record Distribution | Triple Vision Record Distribution |
| M-010 | sano_musik + Sano Musik | Sano Musik |
| M-011 | Iamantro + Iamantro | Iamantro |
| M-012 | thisisdjkitty + This Is DJ Kitty | This Is DJ Kitty |
| M-013 | lunchboxcandy + Lunchbox Candy | Lunchbox Candy |
| M-014 | patyvapor + Paty Vapor | Paty Vapor |
| M-015 | Luccaleeloo + Luccaleeloo | Luccaleeloo |
| M-016 | freudenthal_of_pardonmoi + Freudenthal of Pardon Moi | Freudenthal of Pardon Moi |
| M-017 | hugot_habitacion615_radio + Hugo T — Habitacion 615 Radio | Hugo T — Habitacion 615 Radio |
| M-018 | tigerweeds_ath + Tigerweeds | Tigerweeds |
| M-020 | I Hate Models + I Hate Models | I Hate Models |
| M-024 | Sepehr + Sepehr;Sahra | Sepehr |
| M-025 | Heinrich Dressel + Heinrich Dressel | Heinrich Dressel |
| M-026 | Route 8 + Route 8co | Route 8 |
| M-028 | Samo Records + Samo Records | Samo Records |
| M-030 | Expeditions Berlin + expeditions.berlin | Expeditions Berlin |
| M-031 | afterhoursounds + After Hour Sounds | After Hour Sounds |

## Step 2, REVIEW

| id | name | category | why |
|---|---|---|---|
| I-003 | Metropol | venue | name close to an SI contact (metropolis) |
| I-005 | Tresor | venue | name close to an SI contact (tresorberlin) |
| I-014 | AMANO East Side Rooftop Bar (Daytona) | venue | no IG, email or url |
| I-016 | NYX Hotel Berlin Köpenick, Clash Bar DJ Nights | venue | no IG, email or url |
| I-025 | Restaurant Borchardt | venue | no IG, email or url |
| I-026 | Casa Bellucci | venue | no IG, email or url |
| I-033 | Small Bar listening lounge (House of Small Wonder building) | venue | no IG, email or url |
| I-034 | Neukölln Kneipe (unnamed, Kleinanzeigen ad 24.09.2026) | venue | no IG, email or url |
| I-037 | Best Works (Daniel W. Best) | agency | no IG, email or url; name close to an SI contact (daniel) |
| I-041 | Superbooking | agency | no IG, email or url |
| I-042 | DJ Service Agentur Berlin | agency | no IG, email or url |
| I-043 | Listen2 | agency | no IG, email or url |
| I-045 | Cueup | agency | no IG, email or url |
| I-046 | Gig Heaven | agency | no IG, email or url |
| I-047 | MAV Music (UK) | agency | no IG, email or url |
| I-050 | Kleinanzeigen 'dj gesucht' Berlin | job_board | job board, not a contact; no IG, email or url |
| I-051 | gigmit | job_board | job board, not a contact; no IG, email or url |
| I-052 | Backstage PRO | job_board | job board, not a contact; no IG, email or url |
| I-053 | Hotelcareer | job_board | job board, not a contact; no IG, email or url |
| I-054 | StepStone | job_board | job board, not a contact; no IG, email or url |
| I-055 | Indeed | job_board | job board, not a contact; no IG, email or url |
| I-056 | Facebook groups (names only) | job_board | job board, not a contact; no IG, email or url |
| I-057 | Resident Advisor club pages (source, not a board) | job_board | job board, not a contact; no IG, email or url |
| I-060 | EBM-Radio.com | media | name close to an SI contact (ebmradio) |
| I-062 | GROOVE | media | name close to an SI contact (lagroovemachinemusic) |
| I-077 | Disorder Festival: A Dark Celebration | festival | no IG, email or url |
| I-079 | BIMFest XXIV | festival | no IG, email or url |
| I-082 | Winter Prague Gothic Treffen | festival | no IG, email or url |
| I-085 | Owls'n'Bats Winterfest | festival | no IG, email or url |
| I-090 | Fete de la Musique Berlin | festival | no IG, email or url |
| I-091 | Wilde Mohre Festival | festival | no IG, email or url |
| I-092 | NCN Nocturnal Culture Night | festival | no IG, email or url |
| I-093 | Dark City Fest | festival | no IG, email or url |
| I-105 | Dark Disco Berlin (DARKDISCO.org) | promoter | name close to an SI contact (darkdiscoorg) |
| I-112 | Blank Wave (hosts) | promoter | no IG, email or url |
| I-113 | Slave To The Rave (Quest Agency) | promoter | no IG, email or url |
| I-114 | Killekill | promoter | no IG, email or url |
| I-115 | Les Mirages x Love Reaction | promoter | no IG, email or url |
| I-116 | Das Zuendet | promoter | no IG, email or url |
| I-117 | Power Up (Powernap) | promoter | no IG, email or url |
| I-118 | Unkompress Deep Dive | promoter | no IG, email or url |
| I-120 | The Dark Disko | promoter | no IG, email or url |
| I-121 | ADAM Berlin | promoter | no IG, email or url |
| I-122 | Herrensauna | promoter | no IG, email or url |
| I-124 | Remoto Records | promoter | no IG, email or url |
| I-125 | Zenith Bookings | promoter | no IG, email or url |
| I-126 | Expeditions | promoter | no IG, email or url; name close to an SI contact (expeditionsberlin) |
| I-127 | Nachtboutique | promoter | no IG, email or url |
| I-128 | KitKat Halloween/Kater Katernacht (venue nights) | promoter | no IG, email or url |
| I-130 | DARKDISCO.ORG podcast | media | name close to an SI contact (darkdiscoorg) |
| I-132 | Side-Line Magazine | media | name close to an SI contact (sideline) |
| I-151 | IM MIX (Italo Moderni) | media | name close to an SI contact (italomoderni) |
| I-152 | Disco Pastors Mix | media | name close to an SI contact (discopastors) |
| I-163 | Intergalactic FM Black Monday (Black Mixx call) | media | name close to an SI contact (intergalacticfm) |

## Step 2, OK

| id | name | category | city | IG | source |
|---|---|---|---|---|---|
| I-001 | Refuge Worldwide | media | Berlin (Neukoelln) |  | booking_2026-10 |
| I-002 | KitKat | venue | Berlin |  | booking_2026-10 |
| I-004 | Cashmere Radio | media | Berlin (Wedding) |  | booking_2026-10 |
| I-006 | Soho House Berlin | venue | Berlin | sohohouse | booking_2026-10 |
| I-007 | Hotel Telegraphenamt, ROOT Bar | venue | Berlin | telegraphenamt.berlin | booking_2026-10 |
| I-008 | Monkey Bar (25hours Hotel Bikini Berlin) | venue | Berlin | monkeybarberlin | booking_2026-10 |
| I-009 | GRACE Bar, Hotel Zoo Berlin | venue | Berlin |  | booking_2026-10 |
| I-010 | The Hoxton, Charlottenburg (lobby, Wine & Vinyl) | venue | Berlin |  | booking_2026-10 |
| I-011 | AMANO Bar, 5PM Club | venue | Berlin |  | booking_2026-10 |
| I-012 | JOSEPH by AMANO | venue | Berlin |  | booking_2026-10 |
| I-013 | MANI Restaurant (AMANO) | venue | Berlin |  | booking_2026-10 |
| I-015 | VOX Bar, Grand Hyatt Berlin (GRAND Live Music Nights) | venue | Berlin |  | booking_2026-10 |
| I-017 | Hotel de Rome Rooftop Terrace | venue | Berlin |  | booking_2026-10 |
| I-018 | Michelberger Hotel | venue | Berlin | michelbergerhotel | booking_2026-10 |
| I-019 | Lang Bar, Waldorf Astoria Berlin | venue | Berlin |  | booking_2026-10 |
| I-020 | The Social Hub Berlin | venue | Berlin | thesocialhub.berlin | booking_2026-10 |
| I-021 | nhow Berlin, BPM Bar | venue | Berlin |  | booking_2026-10 |
| I-022 | Provocateur Hotel bar | venue | Berlin |  | booking_2026-10 |
| I-023 | Dorotheá | venue | Berlin | dorothea_restaurant | booking_2026-10 |
| I-024 | Crackers | venue | Berlin | crackersberlin | booking_2026-10 |
| I-027 | Bar Tausend | venue | Berlin | bar.tausend.berlin | booking_2026-10 |
| I-028 | Repeat Bar | venue | Berlin | repeatbar | booking_2026-10 |
| I-029 | YSY | venue | Berlin | ysy.berlin | booking_2026-10 |
| I-030 | 100 Gramm Bar + Lounge | venue | Berlin | 100gramm.bar | booking_2026-10 |
| I-031 | Bar bOx | venue | Berlin | bar_box_berlin | booking_2026-10 |
| I-032 | Pawn Dot Com Bar | venue | Berlin | pawndotcombarberlin | booking_2026-10 |
| I-035 | Weekend Club (House of Weekend) rooftop | venue | Berlin |  | booking_2026-10 |
| I-036 | Künstlervermittlung Berlin / A. Földessy Entertainment GmbH | agency | Berlin |  | booking_2026-10 |
| I-038 | Public Image Events (Stephan Endmann) | agency | Berlin |  | booking_2026-10 |
| I-039 | DJ Pool Berlin (Sebastian Hultzsch) | agency | Berlin |  | booking_2026-10 |
| I-040 | Noble Event | agency | Berlin |  | booking_2026-10 |
| I-044 | ORDO Events | agency | Berlin | ordo.events | booking_2026-10 |
| I-048 | blackbird/berlin | agency | Berlin |  | booking_2026-10 |
| I-049 | DNA Art Club | agency | Berlin |  | booking_2026-10 |
| I-058 | Secret Thirteen | media | Vilnius | secretthirteen | booking_2026-10 |
| I-059 | The Ransom Note | media | London | thisisransomnote | booking_2026-10 |
| I-061 | Kiosk Radio | media | Brussels | kiosk.radio | booking_2026-10 |
| I-063 | FAZEmag | media | Wuppertal | fazemag | booking_2026-10 |
| I-064 | KALTBLUT | media |  | kaltblut_magazine | booking_2026-10 |
| I-065 | Truants | media |  | truantsblog | booking_2026-10 |
| I-066 | Test Pressing | media | UK | test_pressing_official | booking_2026-10 |
| I-067 | Resident Advisor | media |  | resident_advisor | booking_2026-10 |
| I-068 | Crack Magazine | media |  | crackmagazine | booking_2026-10 |
| I-069 | DJ Mag | media |  | djmagofficial | booking_2026-10 |
| I-070 | HHV Mag | media |  | hhvrecords | booking_2026-10 |
| I-071 | Decoded Magazine | media |  | decodedmagazine | booking_2026-10 |
| I-072 | Electronic Groove | media |  | electronicgroove | booking_2026-10 |
| I-073 | DMY (Dummy) | media |  | dmymag | booking_2026-10 |
| I-074 | Data Transmission | media |  | datatransmission | booking_2026-10 |
| I-075 | Noods Radio | media | Bristol | noodsradio | booking_2026-10 |
| I-076 | Grauzone Festival | festival | The Hague |  | booking_2026-10 |
| I-078 | International EBM Day 2027 (BodyBeats) | festival | Sint-Niklaas area |  | booking_2026-10 |
| I-080 | Resistanz Festival | festival | Sheffield |  | booking_2026-10 |
| I-081 | Dark Malta Festival | festival | Malta |  | booking_2026-10 |
| I-083 | Tallinn Music Week 2027 | festival | Tallinn |  | booking_2026-10 |
| I-084 | CTM Festival: Vorspiel 2027 | festival | Berlin |  | booking_2026-10 |
| I-086 | Dark Disco Festival (Winterthur) | festival | Winterthur | dark_disco_winterthur | booking_2026-10 |
| I-087 | Wave-Gotik-Treffen (WGT) | festival | Leipzig |  | booking_2026-10 |
| I-088 | Castle Party | festival | Bolków |  | booking_2026-10 |
| I-089 | 48 Stunden Neukolln | festival | Berlin (Neukolln) |  | booking_2026-10 |
| I-094 | Out Of Line Weekender | festival | Berlin |  | booking_2026-10 |
| I-095 | Electric Monday | promoter | Berlin |  | booking_2026-10 |
| I-096 | SELF.CONTROL. | promoter | Berlin | selfcontrolbln | booking_2026-10 |
| I-097 | EISENGRAU | promoter | Berlin |  | booking_2026-10 |
| I-098 | RITMO3000 | promoter | Berlin | ritmo3000berlin | booking_2026-10 |
| I-099 | Effetto Notte x Process Party: Hall of Bats | promoter | Berlin | effetto.notte.berlin | booking_2026-10 |
| I-100 | Wired | promoter | Berlin |  | booking_2026-10 |
| I-101 | Pleasure Patterns | promoter | Berlin | pleasure.patterns.berlin | booking_2026-10 |
| I-102 | Electric Baile | promoter | Berlin |  | booking_2026-10 |
| I-103 | Flowers Of Romance / TerrorWave events | promoter | Berlin |  | booking_2026-10 |
| I-104 | Dancing on Our Graves (Darkstore) | promoter | Berlin |  | booking_2026-10 |
| I-106 | ELSI | promoter | Berlin | elsi_berlin | booking_2026-10 |
| I-107 | Tresor New Faces | promoter | Berlin | tresorberlin | booking_2026-10 |
| I-108 | Disco Bizarre | promoter | Berlin |  | booking_2026-10 |
| I-109 | Dance Dance Revolution | promoter | Berlin |  | booking_2026-10 |
| I-110 | Daemonenball | promoter | Berlin | daemonenball | booking_2026-10 |
| I-111 | Toy Tonics ITALOMANIA | promoter | Berlin |  | booking_2026-10 |
| I-119 | Master & Servant | promoter | Berlin |  | booking_2026-10 |
| I-123 | Gegen | promoter | Berlin |  | booking_2026-10 |
| I-129 | Subtle Radio | media | London | subtleradio | booking_2026-10 |
| I-131 | Nocturnazine | media |  | nocturnazine | booking_2026-10 |
| I-133 | Insomnia (venue) | venue | Berlin | insomnia.berlin | booking_2026-10 |
| I-134 | Slave to Rock (Insomnia) | promoter | Berlin |  | booking_2026-10 |
| I-135 | Kinktastisch! and Flashback Friday (Insomnia) | promoter | Berlin | kinktastisch | booking_2026-10 |
| I-136 | KitKatClub (venue) | venue | Berlin |  | booking_2026-10 |
| I-137 | CarneBall Bizarre (KitKat Saturday) | promoter | Berlin |  | booking_2026-10 |
| I-138 | Symbiotikka (KitKat Wednesday) | promoter | Berlin | symbiotikka | booking_2026-10 |
| I-139 | Unity (KitKat Thursday) | promoter | Berlin |  | booking_2026-10 |
| I-140 | Nachspiel (KitKat Sunday day rave) | promoter | Berlin | nachspielclub | booking_2026-10 |
| I-141 | Four Play (KitKat Friday) | promoter | Berlin | fourplayberlin | booking_2026-10 |
| I-142 | Pornceptual (PRNCPTL) | promoter | Berlin | pornceptual | booking_2026-10 |
| I-143 | German Fetish Ball Weekend | promoter | Berlin | gfb.weekend | booking_2026-10 |
| I-144 | Wasteland Berlin | promoter | Berlin |  | booking_2026-10 |
| I-145 | Unterwelt Festival + Klubnacht | promoter | Berlin |  | booking_2026-10 |
| I-146 | Echos Nocturnes Drive (mix series) | media | UNKNOWN | dj_kurt_kjergaard | booking_2026-10 |
| I-147 | Counterterraism Guest Mix | media | UNKNOWN | counterterraism | booking_2026-10 |
| I-148 | Ego Riot Podcast | media | Berlin |  | booking_2026-10 |
| I-149 | Dark Science Electro | media | UNKNOWN | dvsnme | booking_2026-10 |
| I-150 | Kri Podcast | media | Ljubljana |  | booking_2026-10 |
| I-153 | DARK DISCO podcast | media | Berlin | dark_disc0 | booking_2026-10 |
| I-154 | Oberwave Mix | media | St Petersburg |  | booking_2026-10 |
| I-155 | Feed Your Head Guest Mix | media | UNKNOWN |  | booking_2026-10 |
| I-156 | Meta Moto Podcast | media | UNKNOWN | metamotometamoto | booking_2026-10 |
| I-157 | Darkness Calls Podcast | media | Tbilisi | georgestoker_ | booking_2026-10 |
| I-158 | TANK Radio (TR series) | media | UNKNOWN | tank_kollektiv | booking_2026-10 |
| I-159 | Disco Tic Guest Mix | media | UNKNOWN |  | booking_2026-10 |
| I-160 | Brain Food Radio (KissFM) | media | Melbourne |  | booking_2026-10 |
| I-161 | PDU Guest Mix | media | Groningen |  | booking_2026-10 |
| I-162 | Line Out Radio (Dark Discoheads show and others) | media | Paris |  | booking_2026-10 |
