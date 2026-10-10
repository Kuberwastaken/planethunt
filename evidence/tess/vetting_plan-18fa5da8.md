# Vetting plan: TIC 370612437 (P 3.5649 d, ~210 ppm) and HIP 114417 / TIC 252721481 (P 4.9335 d, ~279 ppm)

Uses scripts already in Paras's kit: pipeline/10_pixels.py (FFI difference imaging), vet.py, 12_triceratops.py, 06_inverted.py, 08_holdout.py. Python 3.10 works with unpinned deps. Needs MAST/TESScut access only.

Goal: move each candidate from "BLS peak" to "signal is on the target star, not a systematic, and not an EB blend". Report the tier reached, not "planet".

1. Re-derive ephemeris per candidate: fit P, T0, depth, duration with batman + emcee on the combined sectors. Record epoch count and per-sector depths. Per-sector depth consistency check: a real planet gives the same depth in every sector within ~1.5 sigma; a depth that varies with sector points to a systematic or contamination changing with the aperture.
2. Odd/even depth and secondary eclipse at phase 0.5, and at the 2x period (EB check). Fail if odd/even differs >2 sigma or a secondary exceeds ~25% of the primary depth.
3. Systematics: check the period and its harmonics against scattered-light and momentum-dump times per sector (the sectors' quality flags, "bkg" flux). Check the same period in the background flux. Run the inverted-light-curve test (06_inverted.py) to get the false-alarm rate of an SDE this high: if inverted dips of similar SDE are common in this star's data, the signal is not special.
4. Detrending sensitivity: re-run with 3 different wotan windows (0.5, 0.75, 1.5 d) and a different method (biweight vs spline), and one pass with the transit masked. A real signal survives all.
5. Pixel level (10_pixels.py): TESScut 15x15 per sector, difference images over all transits, joint Gaussian-spot fit across sectors, then source comparison for each Gaia neighbour. Pass if the fitted centroid is within ~1 pixel (21") of the target AND neighbours are disfavoured at delta-chi2 > ~10. Check the depth in growing apertures: flat for an on-target source, growing for a neighbour. For SNR ~7 signals the spot fit may be inconclusive; report that as "inconclusive", not as a pass.
6. Contamination: list Gaia neighbours within 60" and the minimum eclipse depth each would need (10_pixels.py prints this). If a neighbour 5+ mag fainter can't produce the dip, it is excluded. Check for binarity of the target itself (Gaia RUWE, Gaia DR3 non-single-star flag, wide companions). RUWE > 1.4 lowers confidence.
7. Statistical validation: 12_triceratops.py (TRICERATOPS) with the best ephemeris and the contrast limits if any ExoFOP imaging exists. Report FPP and NFPP, and which scenario dominates.
8. Holdout test (08_holdout.py): detect the signal in half the sectors and predict the transits in the other half. Report the hit count.
9. Check non-TESS data: is there K2 / Kepler / ground photometry of either star? Do a MAST/Exoplanet Archive/ExoFOP cone search (60") for TOI/CTOI/ground-based follow-up notes. Re-check TOI/CTOI tables the day we report.
10. Output per candidate: table of tests with pass / fail / inconclusive, plots, final tier: (a) BLS recovery only, (b) passes systematics + odd/even + secondary, (c) also passes pixel-level on-target test, (d) FPP < 1% in TRICERATOPS. Honest ceiling at this SNR is (c); validation to "planet" needs ground follow-up or more sectors.

Caveats: signals of 200-280 ppm, SNR ~7-8, are marginal. Expect most pixel tests to be inconclusive. This is an original planned-test checklist, not evidence that each test was completed.
