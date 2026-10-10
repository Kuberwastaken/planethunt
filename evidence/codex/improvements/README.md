# Independent transit robustness checks

This module does not discover, confirm, validate, or establish the novelty of a planet. It measures a **fixed** period/epoch/duration in normalized raw TESS flux with an independent local-baseline fit.

## Run

```bash
python independent_vet.py /path/to/TIC.npz \
  --period 3.5 --epoch 1500.2 --duration-hours 2.4 \
  --output /path/to/report.json
python -m unittest -v test_independent_vet.py
```

Input arrays: `time` in BTJD, `flux` normalized to approximately one per sector, `flux_err`, `sector`, and `exptime` in seconds. Do not substitute search-detrended flux. For a genuinely reserved holdout, add `--holdout-sectors 90,91 --holdout-was-unseen`; the code cannot verify that the caller kept those data hidden. Absent that declaration, results explicitly say retrospective.

Each event is fit with an exposure-integrated box, intercept, and linear slope; events without adequate observations on both sides are discarded. Reported measurements include cluster scatter across events, strongest event contribution, minimum leave-one-event-out significance, odd/even depths, phase-0.5 depth, sector depths, and matched local-processing off-phase controls. The controls are correlated and condition on the chosen period; their rank is not a survey false-alarm probability. Stellar variability, remaining instrumental artifacts, eccentric-binary secondaries away from phase 0.5, and unresolved blends are not excluded. Event-level noise estimates do not capture all season correlations.

Three meaningful synthetic tests check recovery of a repeating transit in held-out data, alternating-depth eclipses, and rejection of a single-event glitch.

## Concrete upstream findings and improvements

Source review: `upstream-tess/pipeline/lcsearch.py`, `vet.py`, `01_targets.py`, `02_download.py`, `results/review/REVIEW_CODEX.md`, and `RESPONSE_TO_CODEX.md`.

1. The upstream ranked catalog contains **15,332 stars**; **14,806** are absent from its 526-star download/search list, and **8,076** of those have reference SNR >= 10. The `has_2min == False` restriction throws away substantial search space. Include SPOC when downloading targets with two-minute products. Existing searches of those stars mean these are new to this run, not newly unsearched stars.
2. Prefer recent sectors and reserve the newest observing season **before** choosing periods. Freeze the candidate ephemeris using only discovery data, then evaluate held-out flux once. A holdout selected after full-data discovery is a retrospective consistency test.
3. Start with per-season BLS candidates, merge peaks and aliases, and refine frequencies over the entire discovery baseline. This can reduce the cost of searching million-frequency grids for every long-baseline star. Retain a full-grid comparison on a sample to measure missed weak coherent signals before treating the shortcut as equivalent.
4. Upstream detrending uses asymmetric clipping and a fixed 0.75-day window. Check symmetric clipping and multiple transit-safe windows on finalists; report whether a signal survives. Apply the same transformations to null data. Detrending with candidate transits masked is useful for depth measurement but is not independent evidence.
5. Require multiple actual well-covered events, modest event dominance, and persistence across seasons. A three-transit count that merely finds any cadence in each window is insufficient.
6. Treat SDE and local depth/error as ranking diagnostics. Upstream audit found 10 clean real versus 17 clean inverted survivors; the advertised numerical survey false-alarm estimates were withdrawn. Calibrate the entire frozen search/selection pipeline using repeated block-preserving null surveys; do not extrapolate unobserved Gaussian tails.
7. Independent products from the same TESS exposures are reductions of shared data, not independent observations. Finalists need pixel localization, neighboring-source checks, and external follow-up to exclude blends/eclipsing binaries.
8. Broadening beyond this catalog should include nearby/bright stars with fewer prior sectors and known hosts after masking known ephemerides. Catalog absence is not novelty: crossmatch current NASA confirmed planets/TOIs, ExoFOP CTOIs, TCE/DV products, eclipsing-binary and variable catalogs, literature, and coordinate aliases.

`expanded_targets_recent_top100.csv` prioritizes `has_recent` then reference SNR, excludes all 526 upstream downloaded targets, and retains original catalog metadata. Its pre-existing catalog exclusions are stale until live novelty checks; it is a workload shortlist, not a list of unknown planet hosts.
