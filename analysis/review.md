# Scientific review - 10 October 2026

## Bottom line
Neither search establishes a confirmed or statistically validated planet. There are two leads worth inspecting: TIC 309780779 in TESS, and KIC 5689121 / TIC 120686465 in Kepler Bonus. Evidence completeness differs: the TESS numeric search and pixel outputs are present; the Kepler quantitative holdout and localization outputs are described in a summary but missing from the partial transfer.

## TESS: TIC 309780779
Source: `evidence/tess/hits/hits_ext_1-1fce4d3a.txt`, `pixels/309780779_pixels.json`.

- Search period 8.723607282476642 d; epoch 1329.1455684886305 in the input TESS time basis. The scripts do not themselves declare its absolute epoch convention; verify FITS provenance before using it for scheduling.
- Box duration 0.864 h; depth 415.809 +/- 30.939 ppm; local depth SNR 13.439; SDE 23.173. These are search statistics, not a global false-alarm probability.
- 46 search events. Pixel test: 45 usable events in 16 sectors. Cached light curve: 17 sector labels, 92,860 cadences. Do not sum or swap these counts.
- Odd depth 458.226 +/-44.459 ppm; even 376.151 +/-42.992 ppm, a 1.33-sigma difference using quadrature errors. This alone cannot exclude an eclipsing binary. `depth_half_ppm` is not a measured phase-0.5 secondary eclipse and must not be relabeled as one.
- Pixel centroid offset 3.610 arcsec, 0.402 nominal sigma; positive fitted target amplitude in 16/16 sectors. Missing-light detection delta-chi-square 67.67. The Gaussian source-model test supports target-consistent localization; it is not a planet probability.
- Original Gaussian PSF method is not an official TESS PRF fit. Aperture depth changes noticeably with radius in some sectors, so “clean aperture stability” is not claimed.
- Duration is unusually short for the rough stellar model assumed in `fit.py`. The earlier grazing-geometry interpretation has no saved fit-result file in this pack, so it is not promoted to a measured impact parameter or planet radius here.

Evidence tier: target-consistent candidate signal, corresponding to the earlier provisional tier c (pixel localization). The full planned ladder was not documented as completed. Formal FPP, independent held-out recovery, source identity/proper-motion review, and a current exact-ephemeris catalog audit remain needed. No submission or follow-up is performed by this repository.

## TESS: TIC 305054512
Source: `pixels/305054512_pixels_CORRECTED_RERUN.json` and matching image/log.

Search period 15.827600363408258 d; box duration 2.736 h; search depth 645.345 +/-48.523 ppm; seven search events. Corrected pixel rerun uses four events in two sectors and a depth input of 771.442 ppm. Its missing-light source is 37.330 arcsec from the target, at 54.285 nominal sigma under that model. Free-position chi-square improves by 850.514 over target-pinned placement. Several neighbors fit better than the target. Verdict: off-target/blend-like signal, rejected as an on-target candidate pending source-model reassessment, not “another planet”.

The first pixel run used a float-damaged Gaia ID and is invalid; its log was overwritten. Only CORRECTED_RERUN artifacts are used. The corrected table gives exact Gaia IDs as strings; do not read the original GAIA float column as an identifier.

## Coverage and controls
`manifest.json` lists 540 unique assigned targets, no overlap with 526 inherited upstream results. This is not proof of 540 completed, independently audited searches: only 54 newly written local per-star results are counted in the reconciliation, remote completion counts are reports, and complete per-star outputs are not shipped. First-600 slice membership was reconstructed after two extra rows and is approximate. Avoid advertising 1,500 stars as searched or counting inherited 526 as new work.

Speed changes: 1-25 d, one signal, 1.5 oversampling, 1,200-second bins (20 minutes, despite a stale “10 min” code comment), five duration-grid values. Earlier results may use original settings. Partial injection log contains baseline lines and an empty quiet-host list, not a completed recovery calibration. Negative-control outputs and phase-null results are not stored. Planned tests are not completed tests.

## Codex: KIC 5689121 / TIC 120686465
Sources: `evidence/codex/README.md`, `FINAL_STATUS.json`, `summary.pdf`, and catalog novelty report. These are source-reported measurements until full underlying artifacts arrive.

- P = 13.769413569662944 d; catalog audit epoch = 136.312889832702 BKJD. Period uncertainty not estimated.
- Box duration 2.1376 h; summary physical duration approximately 2.1-2.4 h, not 3 h.
- Raw PSF local depth 2165 +/-98 ppm overall; 1929 +/-159 ppm reserved; 70 usable local events, 22 held out.
- Corrected SAP local SNR 13.73 overall, 5.84 held out. Two extractions use the same observations; they are not independent telescope confirmations.
- Source reports official Kepler PRF localization consistent with target in 13 quarters, against brighter primary KIC 5689116 at 7.1 arcsec. Full quarter measurements and calibration manifests are missing from this partial pack.
- Conditional size about 3 Earth radii assumes on-target, undiluted planetary transit; this is not a validated radius.
- Target Gaia RUWE 0.98412067 and NSS 0 in the audit. Catalog radius estimates differ: TIC 0.50748, Gaia GSP-Phot 0.5553, Gaia FLAME 0.5420065 solar radii.
- No same-host prior signal was found in the retrieved catalogs. Kepler-169 e is a near-period coincidence 263.33 arcsec away but 2.80356 d out of phase. Novelty remains provisional; absence from a finite snapshot/index is not proof of first discovery.
- Unresolved eclipsing companion, other blended sources, PRF errors and correlated noise remain unexcluded. Formal FPP and external observations are absent.

Kepler pilot: 64 stars from 1,800 eligible background M dwarfs, 0.5-25 d. Last ceil(25%) usable quarters reserved before searching, minimum two. Two initial screen survivors; Gaia 2129404966720268672 / KIC 10794841 (1.4102 d) has secondary dimming and weak aperture support. 64 inverted searches yielded zero initial-screen passes; that small matched diagnostic is not a calibrated survey-wide FAP.

TESS pilot: 175 stars, 350 two-band searches; nine signals/eight hosts initially passed. Five initial-screen passes among 100 inverted runs. QLP timing error in sectors 99-104 affected 44 stars; 88 reruns removed affected QLP products. Revised holdouts are retrospective. Positive controls LHS 3844 b and Kepler-138 c/d are known planets, not discoveries here.

## A material contradiction preserved
`catalogs/final_survivor_dispositions.csv` still says TIC 358559650 fails holdout. The later top-level README explicitly withdraws that rejection after timing-safe reruns: signal repeats but has broad shape, variable depth and binary/blend concern. Use the newer README for the intended disposition; underlying timing-safe output has not been received, so this review cannot adjudicate the rerun itself. Preserve the CSV as historical, not final truth. TIC 94753488 remains broad unresolved dimming; TIC 456716455 has companion concerns.

## What would change the conclusion
Receive and verify the complete Kepler measurement/PRF/holdout archive; run reproducible locked analyses without retuning to held-out data; use proper-motion-aware multiple-source localization and formal blend/FPP analysis; investigate systematics and noise with calibrated controls; obtain suitable external follow-up. Merely creating this repository does none of these.
