# SC Session Report — Tuesday 2026-06-16

**Session time:** ~11:53 Berlin (manual trigger — scheduled 11:30 missed, cause TBD)
**Discovery file:** discovery_candidates_20260616.json (fresh today)
**Brief:** STATUS: APPROVED 2026-06-16 ✓

---

## PASS 0 — Identity: PASS
Chrome profile: Inch of Shadow | SC session: inch-of-shadow (user_id 16014870)

---

## PASS A — Likes: 7/12

| Artist | Track | Track ID | Age | Notes |
|--------|-------|----------|-----|-------|
| Djane MariaFM | Special Request - Pull Up (Extended) | 1969558155 | ~1mo | Track 1 already liked; used track 2 |
| ROG333R | MIDNIGHT JAM #3 | 2335238492 | 8d | Within window |
| Anna Karina | Addicted-2-Bass / Episode 205 / Anna Karina / 12.04.2026 | 2302660139 | ~48d | No ≤21d track; used most recent |
| Anna Pronicheva | what about self-distructuve anger | 2300395868 | ~50d | No ≤21d track; used most recent |
| dOctOr doms | dOctOr doms - FLIP-FLAP x Pulse Friction 16.05 | 2324372072 | 25d | No ≤21d track; used most recent |
| Brother Of Your Mother | BROTHER OF GROOVE | 2290386008 | ~83d | Most recent already liked; used next |
| Out of Body (O.O.B.) | Out of Body - Explorations #1 | 1736354235 | ~16mo | No ≤21d track; used most recent |

**Skipped PASS A (5) — most recent track already liked, no fallback:**
- contredanse — "Stoss #1" (Apr 10) already liked
- Satori Rotors — "Superluminal" (Jun 12, 4d) already liked
- MARIANNA — "Marianna Pirate Sessions" (Jun 15, yesterday) already liked
- Ecotono — "EcoTape #012 - TSCHINI" (May 8) already liked
- GOJAS — all tracks from Aug 2024, one already liked

---

## PASS B — Follows: 1/12 new

| Artist | User ID | Followers | SC URL | Notes |
|--------|---------|-----------|--------|-------|
| Djane MariaFM | 1355285121 | 100 | /djane-mariafm | New follow ✓ |

**Already following — 11/12 candidates (discovery filter miss — see anomalies):**

| # | Artist | User ID | Followers |
|---|--------|---------|-----------|
| 2 | ROG333R | 14033433 | 100 |
| 3 | contredanse | 840981994 | 102 |
| 4 | Anna Karina | 492825348 | 113 |
| 5 | Anna Pronicheva | 139035591 | 113 |
| 6 | Satori Rotors | 3784941 | 122 |
| 7 | MARIANNA | 421490 | 125 |
| 8 | Ecotono | 1290025175 | 127 |
| 9 | GOJAS | 314263040 | 142 |
| 10 | dOctOr doms | 306133314 | 147 |
| 11 | Brother Of Your Mother | 239204 | 154 |
| 12 | Out of Body (O.O.B.) | 1225462927 | 155 |

---

## PASS C — Maintenance Likes: 0/12
All active reciprocators still within 30-day cooldown. Not padded per brief.

---

## ⚠ Anomalies for Claude Code

### CRITICAL: Discovery filter not excluding already-followed accounts
11 of 12 candidates from discovery_candidates_20260616.json were already being followed (SC button showed "Following" on arrival). This is a major discovery_v2 filter failure — the "not in tracker / permanently_unfollowed" check is not working against the live follow tracker. The brief was prepared fresh today (2026-06-16) from the same day's discovery file, so the tracker state should have been current at prep time.

**Action required:** Claude Code must audit discovery_v2 filter logic to confirm it is correctly excluding accounts with follow_date present in sc_follow_tracker.json. Check if tracker lookup uses permalink vs. user_id matching and whether any indexing issue is causing misses.

### Djane MariaFM follow log deduplication (carried from Mon 2026-06-15)
Follow log returned "Already in tracker" after the like was logged, yet the physical follow was new (button changed Follow → Unfollow). Suggests the --log-action sc_like call pre-creates a tracker entry before the sc_follow log, causing the follow log to see a duplicate and no-op. Follow was confirmed real on screen. Claude Code should review entry creation order in sc_engagement.py.

### GOJAS (goja-s) — stale profile
All tracks titled "COLLABORATIONS" from Aug 2024 only. One already liked. Profile appears inactive since Aug 2024. Add age-of-last-upload check to discovery filter.

### Out of Body (O.O.B.) (out-of-body-dj) — stale profile
Most recent upload February 2024 (~16 months ago). Add age-of-last-upload check to discovery filter.

---

*All actions logged via sc_engagement.py --log-action. No SC API writes. Session complete.*
