# Kepler Bonus extension and matched null control (2026-10-11)

Scope: this applies Codex's own Kepler Bonus pilot code (`evidence/codex/database_expansion/kbonus/pilot.py`, logic unchanged) to more of the same frozen selection. It is a search extension, not a new validated result.

## What was run
- Selection: the same frozen rule as the Codex pilot (eligible background M dwarfs, Kepler primary targets excluded, ranked by Gaia G magnitude before any photometry was seen). Codex searched ranks 1-64. This extension searched ranks 65-576.
- 512 stars selected, 497 searched, 15 skipped for fewer than 6 usable quarters (`stars_searched.csv`).
- Same split rule: last ceil(25%) usable quarters reserved before the period search. 0.5-25 d band. Same first screen.
- A matched inverted (flux = 2 - flux) run was done on the same 497 stars with identical processing (`signals_real_and_inverted.csv`, column `inverted`).
- Scripts: `batch2.py` (real), `inv.py` (inverted). They import `pilot.py` from the Codex pack. Environment here was Python 3.10 with unpinned recent numpy/scipy/astropy/lightkurve, not the Codex lock file.

## Result
| | stars searched | signals passing first screen |
|---|---|---|
| real | 497 | 10 signals on 9 stars |
| inverted null | 497 | 10 signals on 9 stars |

The real run did not produce more first-screen passes than the null. Six of the nine real passing stars have no inverted pass, but two (KIC 7436275 at 0.614 d, KIC 6206697 at 0.567 d) pass in both polarities, and KIC 5790842 (4.87 d) passes in both. Those are variability or systematics, not transits.

Nothing here approaches KIC 5689121 (BLS SNR 26.7, holdout 15.5 in the same pipeline).

## Individual real passes
| KIC | P (d) | depth ppm | holdout SNR | status |
|---|---|---|---|---|
| 9851000 | 8.482 | 3243 | 12.2 | Rejected: matches KOI K04879.01 (KIC 9850966, 8.4803 d, false positive, 58 arcsec away) |
| 6629201 | 2.638 | 697 | 16.0 | Unresolved, weak. Faint (G 17.9), no KOI/TCE match, no localization done |
| 7436275 | 0.614 | 252 | 8.9 | Rejected: also passes inverted |
| 6206697 | 0.567 | 581 | 10.8 | Rejected: also passes inverted |
| 5790842 | 4.867 | 2345 | 6.1 | Rejected: also passes inverted, deep |
| 6604266, 6266847, 9896737, 8758092 | 0.5-1.0 | 390-1380 | 4.2-13 | Ultra-short; same regime where nulls pass; not leads |

## Limits
- No pixel/PRF localization was done on any of these. No Gaia-neighbor, TRICERATOPS or formal false-positive analysis.
- The catalog check for KIC 9851000 and 6629201 used the Exoplanet Archive KOI/TCE tables only.
- The strict-screen analysis (period > 1.5 d, 12.5-14.5 d excluded, holdout SNR >= 5, event-sign and single-event limits) was tuned after seeing these results, so it is descriptive, not a clean test.
- No candidate was named, submitted or announced.
