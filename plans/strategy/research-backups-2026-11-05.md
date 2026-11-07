# Backups: research and options (2026-11-05)

Text-only research. All prices checked 2026-11-05 on the linked page unless a different date is given. USD prices are list prices, without EUR conversion.

## What we need to protect

- Mac: 926 GB disk, about 888 GB used. Intenso (931 GB) is full.
- Irreplaceable and not backed up now: Ableton DONE about 57 GB, Doom 13.7 GB, Men Machine 8.6 GB, plus smaller projects (80-100 GB in total). Also the Inch of Shadow folder (19 GB) and the code folder (2.5 GB plus git, which holds contact data).
- Offsite core set: about 120-150 GB. A full-Mac backup: about 1 TB now, closer to 2 TB with versions.

## Comparison

| Option | ~150 GB | ~2 TB | Who holds the key | EU location | Versions | Mac app | Restore |
|---|---|---|---|---|---|---|---|
| 2nd external HDD 4 TB + Time Machine | one-off EUR 101 (EUR 25/TB) [1] | same drive | you (TM encryption) | your desk | hourly/daily/weekly until full | built in | Finder / Migration |
| External SSD | about EUR 62/TB (T7 2 TB EUR 125, deal, undated) [2] | about EUR 125+ | you | your desk | same | built in | same |
| Backblaze Personal | $9/mo, $99/yr (unlimited) [3][4] | same | optional private key [3] | EU region (Amsterdam), chosen only at sign-up [5] | 30 days or 1 yr included; Forever costs extra [6] | own app, backs up external drives [4] | web zip up to 500 GB, app, USB drive (deposit refunded) [3][4] |
| Backblaze B2 + Arq | about $1/mo (first 10 GB free) [7] | about $14/mo | you (Arq) [8] | EU-Central, Amsterdam [9] | Arq retention rules | Arq 7: $49.99 once, $25/yr for updates [10] | Arq app |
| IDrive Personal | no small plan, 5 TB is the minimum: $6.99/mo in year 1, then $9.99 [11] | same | optional private key [12] | Frankfurt/Ireland reported, not confirmed for Personal [13] | 30 versions [14] | own app | web/app; one free Express drive per year (not certain) [11] |
| iCloud+ | 200 GB EUR 2.99/mo [15] | 2 TB EUR 9.99/mo [15] | you, only with Advanced Data Protection [16] | no region choice | sync, not backup | built in | Finder |
| Dropbox Plus / Essentials | Plus 2 TB EUR 9.99/mo, 30 days of history [17] | Essentials 3 TB $16.58/mo, 180 days [18] | Dropbox (no client-side encryption) [19] | not selectable for personal plans | 30 or 180 days | good | app / web |
| pCloud | 500 GB lifetime EUR 219 [20]; about EUR 50/yr (3rd party) [21] | 2 TB lifetime EUR 499 [20]; about EUR 100/yr [21] | pCloud, unless you pay for Crypto (about EUR 48/yr or EUR 150 lifetime, 3rd party, sources disagree) [22] | Luxembourg, chosen at sign-up [23] | 30 days [20] | sync app | app / web |
| Hetzner Storage Box + Arq/rsync | BX11 1 TB EUR 3.20/mo before VAT (EUR 3.81 with VAT) [24] | BX21 5 TB EUR 10.90 before VAT (EUR 12.97 with VAT) [24] | you (Arq/restic) | Germany or Finland, GDPR DPA available [24] | 10-20 snapshots plus Arq versions | Arq, or rsync/restic in Terminal | Arq / SFTP |

## Notes per option

- **Second drive:** an HDD costs about 2.5 times less per TB than an SSD, and for backups the HDD's slower speed does not matter. Time Machine keeps versions and can restore the whole Mac. Plain copies (Finder or rsync) keep no history, so a file that gets corrupted is copied over the good copy. With two drives in rotation, one stays off site (for example at Ambertone) and gets swapped each week, which also covers theft and fire. Time Machine handles two destinations natively.
- **Backblaze Personal:** set it and forget it, it backs up the whole Mac and attached drives, and it has an EU region. Its owner is a US company (a jurisdiction caveat from a third party) [25]. Choose the region at sign-up, because it cannot be changed afterwards [5].
- **B2 + Arq:** cheapest offsite storage for 150 GB. Arq encrypts on the Mac before upload, and the format is open and documented [8].
- **IDrive:** good value only above 2 TB, and the price rises after year 1. EU storage is not confirmed for Personal.
- **iCloud+:** the cheapest Apple option, but Time Machine cannot back up to it and it only syncs. It is end-to-end encrypted only with ADP turned on.
- **Dropbox:** a sync service, not a backup. Dropbox holds the keys [19], so contact data should not go there unencrypted. It is fine for the masters he already keeps there.
- **pCloud:** an EU (Luxembourg) region, but zero-knowledge encryption costs extra and only covers one Crypto folder. It is cloud storage, not a backup tool.
- **Hetzner:** a German company with data in Germany, no minimum term, and Arq/restic/Borg/rsync support [24]. The only option here that is both EU-owned and encrypted with a key only he holds. The page mentions a one-time setup fee without stating the amount [24].

## 3-2-1 for this setup

3 copies, on 2 kinds of media, 1 of them off site.

1. Copy 1: the Mac itself.
2. Copy 2: a new 4 TB HDD with an encrypted Time Machine backup of the whole Mac, hourly versions. This also absorbs the 80-100 GB of unbacked Ableton projects at once.
3. Copy 3 (off site): Arq to Hetzner BX11 (Germany, his key), covering the core set: Ableton projects, the Inch of Shadow folder, the code folder. About 150 GB of the 1 TB plan.
4. Intenso stays a cold archive (the 2025-07 PROJECTS copy). Dropbox stays for the masters.

Cost: EUR 101 once for the drive, plus about EUR 3.81/mo, plus Arq $49.99 once. This covers disk failure, a deleted or corrupted file (versions), theft or fire (Hetzner), and keeps contact data encrypted with a key only he holds.

## Options for us

1. **Cheapest, about EUR 1/mo:** a 4 TB HDD with Time Machine (EUR 101 once), plus Arq to B2 EU for about 150 GB (about $1/mo, Arq $49.99 once). Offsite copy, his own key, data in Amsterdam under a US company.
2. **Balanced, about EUR 8/mo:** a 4 TB HDD with Time Machine, plus Backblaze Personal in the EU region with a private key ($99/yr, about $8.25/mo). Unlimited, the whole Mac plus drives off site, 1 year of versions, the least setup.
3. **Most private, about EUR 4/mo:** two 4 TB HDDs in rotation with Time Machine, one at Ambertone (EUR 202 once), plus Arq to Hetzner BX11 in Germany (EUR 3.81/mo). EU-owned, his key only, nothing at a US provider.

## Sources (all read 2026-11-05)

1. https://storagediskprices.com/de/4tb/ (Amazon.de, dated 2026-11-05)
2. https://www.pcgames.de/SSD-Hardware-255552/News/externe-SSD-Samsung-Portable-SSD-T7-2-TB-guenstig-kaufen-Media-Markt-Angebot-1488844/ (undated deal)
3. https://www.backblaze.com/cloud-backup/pricing
4. https://www.backblaze.com/cloud-backup/personal
5. https://help.backblaze.com/hc/en-us/articles/360034360834-EU-Region-FAQ
6. https://www.backblaze.com/computer-backup/docs/version-history
7. https://www.backblaze.com/cloud-storage/pricing ($6.95/TB/mo)
8. https://www.arqbackup.com/
9. https://www.backblaze.com/docs/cloud-storage-data-regions
10. https://arqbackup.com/documentation/arq7/English.lproj/arq7Pricing.html
11. https://www.idrive.com/pricing
12. https://www.idrive.com/help/Mac/encryption.htm
13. https://expertinsights.com/backup-and-recovery/idrive-par (third party)
14. https://www.itpro.com/software/backup-software/358753/idrive-personal-review-set-it-and-forget-it (third party)
15. https://www.apple.com/de/icloud/
16. https://support.apple.com/en-us/102651
17. https://www.dropbox.com/plans
18. https://www.dropbox.com/partners/plans-comparison
19. https://help.dropbox.com/accounts-billing/security/how-security-works
20. https://www.pcloud.com/cloud-storage-pricing-plans.html
21. https://eupicks.pages.dev/blog/pcloud-review-2026/ (third party)
22. https://europeanstack.pages.dev/software/pcloud (third party)
23. https://pcloud.com/data-regions
24. https://www.hetzner.com/storage/storage-box/
25. https://sota.io/blog/backblaze-b2-eu-alternative-gdpr-cloud-act-object-storage-2026 (opinion)
