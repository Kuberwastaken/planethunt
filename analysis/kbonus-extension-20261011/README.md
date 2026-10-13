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

The real run did not produce more first-screen passes than the null. Six of the nine real passing stars have no inverted pass, but two (KIC 7436275 at 0.614 d, KIC 6206697 at 0.567 d) pass in both polarities, and KIC 5790842 (4.87 d) passes in both. Passing both polarities is a warning for variability or systematics; it does not by itself classify the source or exclude a transit in the same light curve.

This first extension did not establish an additional planet candidate. Across the later combined search, two inverted signals reach BLS and holdout scores at least as high as KIC 5689121; scores alone do not establish its nature (see the [13 October audit](../editorial-audit-20261013/README.md)).

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

## Second stage: ranks 577-1800 (added 2026-10-11)
Same code, same frozen ranking (`batch2.py --lo 576 --hi 1800`, inverted with `ranks577-1800/inv3.py`). Tables in `ranks577-1800/`.

- 1224 stars selected: 1175 searched, 49 not searched (48 with fewer than 6 usable quarters, 1 MAST read timeout, not retried).
- Matched inverted run on the same 1175 stars.
- First-screen passes: real 19 signals on 18 stars, inverted null 22 signals on 19 stars. No excess over the null.
- With a stricter screen (P > 1.5 d, outside 12.5-14.5 d, holdout SNR >= 5): real 6 signals on 5 stars, inverted 7 signals on 6 stars. This screen was chosen after seeing the earlier batch, so it is descriptive, not a clean test.

Real strict passes and what checks say (NASA Exoplanet Archive TCE/KOI cone, ~108 arcsec, same period or 2x/0.5x):
| KIC | P (d) | depth ppm | result |
|---|---|---|---|
| 4544570 | 2.189 | ~5200-6950 | Rejected: four KOI false positives at the same 2.189 d within 85 arcsec |
| 11724208 | 5.746 | ~5600 | Rejected: KOI K06244.01 (KIC 11724210, 5.746 d, false positive, 9.6 arcsec away) |
| 12164160 | 19.42 | 5398 | Unresolved: no catalogue match; G 18.4 and ~0.54% depth. No source localization or stellar-radius assessment sufficient to classify it |
| 8743279 | 21.96 | 9917 | Unresolved: G 18.6, ~0.99% depth; no source localization. Depth alone does not establish an eclipsing binary |
| 8803342 | 5.010 | 2928 | Unresolved: G 18.8, ~0.29% depth; no source localization. Depth alone does not establish an eclipsing binary |

No pixel/PRF localization was done on these. None was promoted to an additional planet candidate or submitted. This is a disposition decision, not a demonstration that each signal is nonplanetary.

## Combined picture
Across ranks 65-1800 (1,672 stars searched, plus Codex's 64) the real search never produced more first-screen passes than the matched inverted null. KIC 5689121 received the detailed follow-up analysis; other high-scoring real and inverted signals mean that detection strength alone does not uniquely distinguish it.
Totals: ranks 65-576: 497 searched; ranks 577-1800: 1175 searched; sum 1,672. One unresolved weak item from the first stage: KIC 6629201 (2.638 d, faint, unlocalized).

Editorial audit, 13 October 2026: the unlocalized depth-based classifications above have been corrected. The total search produced no validated planet, including KIC 5689121. See the linked audit for exact signal-versus-star counts and limits.
