# Science write-up: validation pass, 11 October 2026

This folder adds the next round of checks on the two Planethunt leads, run end to end on the
original data in the `evidence-20261010` release archives (Kepler and TESS archive SHA-256
hashes match `analysis/full-archive-review.md`). **Neither lead is validated by this pass.**
One lead gets materially stronger, and the other turns out to be weaker than it looked.

Short version:

| | KIC 5689121 / TIC 120686465 | TIC 309780779 |
|---|---|---|
| Signal real and periodic | Yes | Yes, recovered blind in each half of the data |
| Signal on the target star | Strong: three independent pixel/photometry tests | Not re-tested (MAST unreachable); prior Gaussian-PSF result only |
| Known-object contamination | Kepler-169 excluded | No catalog match within 5′ or 1° harmonic |
| Formal FPP (TRICERATOPS) | **≈ 0.07** (threshold 0.015) | **≈ 0.57** |
| Dominant false-positive scenario | Planet around an unresolved bound companion (STP) | Eclipsing binary bound to the target (SEB) |
| With hypothetical imaging | ≈ 0.03 | ≈ 0.45 |
| What would move it | AO imaging + RUWE-based companion limits | Reconnaissance spectroscopy / RVs; colour-dependent depth |

## KIC 5689121 / TIC 120686465 (Kepler, P = 13.769 d)

**Ephemeris (full baseline, all 13 quarters, PSF flux).** P = 13.769448 ± 0.000065 d,
T0 = −1369.7546 ± 0.0020 BTJD, ρ* = 4.4 (+2.3 −2.8) ρ☉ from the free-density fit, consistent
with the Gaia/TIC density of the 0.51–0.55 R☉ M dwarf. `scripts/kepler/kfit.py`,
`results/kepler/kfit_psf.json`.

**Kepler-169 is not the source.** No candidate transit overlaps a Kepler-169 e transit in the
whole baseline; the closest pair is 67 h apart, and the offset drifts from 2.80 to 3.04 d. The
period differs from Kepler-169 e (13.767101 d) by 32σ. Box depths in the target's PSF light
curve at all five Kepler-169 ephemerides are null (−65 to +143 ppm, all |d| < 1.1σ). Chance
overlaps with Kepler-169 b and d (5 and 1 events) are at the expected rate for short periods.
`k169_overlap.py`, `kdepth.py`.

**The PSF/SAP depth gap is dilution, and its pattern points to the target.** Per quarter, the
SAP depth tracks the target's share of the SAP-aperture flux (FLFRCSAP × PSF flux / SAP flux):
the dilution model fits (χ² 15.4/12, p = 0.22, scale 0.91); a constant depth does not
(p = 0.005); a signal riding on the extra aperture flux is rejected (p ≈ 1e−36). The seasons
with 7-pixel apertures (Q2, Q6, Q14) have the most contaminating flux and the shallowest SAP
depths, the opposite of what a contaminant-hosted signal would do. `kcrowd.py`,
`kdilution_pooled.py`, figure `kic5689121_dilution_centroid.png` (left).

**The bright neighbour shows no dip.** KIC 5689116's own KBonus PSF light curve at the
candidate ephemeris: 24 ± 41 ppm. If it hosted the signal it would need ≈ 1100 ppm in its own
photometry (it is 2.1× brighter in G). Its SAP light curve shows 137 ± 42 ppm, the expected
leakage of the target into its aperture.

**New, independent raw-pixel centroid test.** Flux-weighted centroids computed directly from the
13 calibrated KIC 5689116 target pixel files (which contain both stars), using only stamp
geometry and Gaia positions, no PRF model. In-transit shifts are detected (zero shift rejected,
χ² 504/24) and match the first-order prediction for a dip on the target (χ² 43.9/24, p = 0.008,
mild tension from the linear approximation and unmodelled faint stars). The bright neighbour is
rejected at Δχ² = 934, and every other Gaia source within 30″ at Δχ² ≥ 4,300.
`kcentroid_tpf.py`, `kcentroid_all.py`, figure (right). This shares photons with the Codex PRF
localization but no modelling choices.

*Caveat:* the KBonus `CENTROID_COLUMN/ROW` columns show no in-transit response at all
(`kcentroid.py`, χ²(zero) = 25.5/26); they appear to be model-derived and are not usable for
this test. Only the raw-TPF version is quoted.

**Search statistics alone do not single it out (new negative result).** Ranked against all
1,736 matched inverted Kepler Bonus searches (pilot + both extension stages), 2 inverted stars
pass the first screen at P > 1.5 d with BLS SNR ≥ 26.7 and holdout SNR ≥ 15.5 (KIC 8701308 at
4.25 d, KIC 5283912 at 8.78 d). The observed inverted-control fraction is 2/1,736 for these retrospectively chosen thresholds. It is a diagnostic count, not a calibrated per-star or survey-wide false-alarm probability: inversion is not established as a representative null for every systematic, and the threshold comparison followed inspection of the candidate. (Interpretation corrected 13 October 2026.) The
case for KIC 5689121 rests on the vetting (shape, density, localization, dilution pattern), not
on detection strength. `null_fap2.py`.

**TRICERATOPS FPP ≈ 0.07, not validated.** Run offline on the target alone (on-target and
unresolved-blend scenarios), Kepler mission settings, 29.4-min exposure, the folded PSF light
curve, and a field population built with TRICERATOPS' own Gaia recipe from the 120″ Gaia DR3
cone already in the evidence pack (resampled to the 0.1 deg² its priors assume).

| Background population | Runs (N = 1e6 each) | FPP |
|---|---|---|
| Gaia G < 21 | 4 | 0.059, 0.089, 0.058, 0.069 (mean 0.069) |
| Gaia G < 21 + extrapolated to G = 22.5 | 2 | 0.058, 0.088 |
| G < 21 + *hypothetical* Keck K-band AO curve | 2 | 0.022, 0.032 (mean 0.027) |

The PSF depth itself depends on the measurement choice: 1830–2430 ppm across box widths and
baseline windows in the independent check. It is 13–22σ against the event-to-event and
random-phase scatter, which is far more conservative than the formal errors (≈ 43σ).

Mean scenario probabilities (G < 21): TP 0.75, PTP 0.17, **STP 0.068**, DTP 0.009, BTP+BEB
< 0.001, every eclipsing-binary scenario ≈ 0. The FPP is almost entirely "a planet transiting an
unresolved bound companion". Even a typical AO contrast curve (hypothetical, not an
observation) only brings it to ≈ 0.02, because companions inside ~0.1″ (~30 au at 298 pc) stay
allowed. Gaia RUWE 0.98 already disfavours some of these, but TRICERATOPS 1.1 does not use it;
a MOLUSC companion file would.

NFPP is reported as 0 only because resolved neighbours were not passed to TRICERATOPS (that
requires a Kepler PRF/aperture model). The resolved-neighbour scenarios are instead excluded by
the neighbour light curve and the centroid test above.

## TIC 309780779 (TESS, P = 8.7236 d)

Host: TIC Teff 5013 K, R 0.685 R☉, M 0.83 M☉, d 74.9 pc, T = 10.03. Light curves are TESS-SPOC
FFI products at 1800/600/200 s plus two QLP sectors (89, 90), outside the documented QLP timing
problem (99–104).

**Blind recovery in each half of the data (new).** An independent BLS (astropy, own
detrending) on the full data returns 8.72363 d (SDE 19.6); on the inverted light curve the best
peak is SDE 7.8. Searching sectors 1–38 alone returns 8.72374 d as the top peak (SDE 12.6;
inverted best 6.0). Searching sectors 61–90 alone returns 8.72348 d as the top peak (SDE 12.9).
`bls.py`.

**Frozen-ephemeris holdout (new).** The ephemeris fitted to sectors 1–38 predicts the
sectors 61–90 mid-transit 89 cycles later, and the late transit lands on the prediction within
its uncertainty: the MCMC fits give −0.95 min (prediction ±7.5 min, 0.12σ). An independent
check with separate code finds +4 min (−12 to +11 min). Depth in the late sectors at the frozen
ephemeris is 380–450 ppm depending on box width (9–10σ), with 22/22 events positive.
Discovery-half and late-half periods agree at 1.2σ. `holdout.py`, figure
`tic309780779_holdout_phase_scan.png`.

**Fixed-ephemeris diagnostics.** Depth 401 ± 30 ppm; odd/even 365 ± 41 vs 444 ± 42 (1.3σ);
depth flat across cadence eras (367 ± 67, 423 ± 55, 408 ± 44 ppm). No secondary at any phase:
phase 0.5 is −20 ± 26 ppm (−23 to −48 ppm in the independent check, consistent with zero), the
largest off-transit dip in 377 phase trials is 3.2σ, and a phase-shift null never approaches
the transit (13.5σ). `scan.py`.

**Shape.** With a 15% Gaussian prior on the TIC density: b = 0.953 ± 0.015, Rp/R* = 0.0274
(+0.0027 −0.0019), Rp ≈ 2.05 (+0.20 −0.14) R⊕, T14 = 1.07 h, 14% of posterior grazing.
Without the prior the fit runs into the grazing branch (85% grazing, large radius ratio): the
data cannot tell a ~2 R⊕ planet at high impact parameter from a grazing larger body. `tfit.py`.

**TRICERATOPS FPP ≈ 0.57, not validated.** Same offline setup, TESS settings, 600-s-equivalent
series (native 600-s cadences + 200-s cadences averaged in 600-s bins, 34 of 46 events), field
population from the 90″ Gaia neighbour list in the pixel output. Three runs: 0.556, 0.579,
0.568. Dominant scenario: **SEB ≈ 0.42**, an eclipsing binary bound to the target (best fit: a
0.18 M☉ pair, grazing at b ≈ 1.0, diluted by the K dwarf), with TP 0.35. This is the textbook
false positive for a short, high-impact, shallow dip on a bright star. With a *hypothetical*
832-nm speckle contrast curve the FPP only falls to 0.44–0.47 (SEB still 0.38), because imaging
cannot resolve a close hierarchical companion.

## What was not possible here, and why

- **TESS pixel re-analysis with the official PRF, Gaia RUWE/NSS for TIC 309780779, live
  ExoFOP/TOI status for either star:** MAST, the Gaia archive, VizieR and ExoFOP are unreachable
  from this environment (network allowlist / robots). These are hard obstructions, not skipped
  steps.
- **High-resolution imaging, reconnaissance spectra, RVs, multi-band transits:** need telescopes.
- **NFPP for KIC 5689121 inside TRICERATOPS:** needs a Kepler PRF + aperture flux model for every
  neighbour; handled with direct tests instead (above).

## What would actually move each lead

**KIC 5689121.** AO imaging (Keck/NIRC2 or similar; the target is Kp 16.3, K 12.97) plus a
companion constraint that uses RUWE 0.98 (MOLUSC). A multi-band transit (STP predicts
colour-dependent depth) would also help. A radial-velocity mass is not realistic for this faint
M dwarf. Realistic endpoint: *statistically validated*, if imaging and RUWE squeeze STP below
~1%.

**TIC 309780779.** The bound-EB scenario dominates, and imaging cannot reach a close
hierarchical companion. Two or three reconnaissance spectra (the star is T = 10) would show
an SB2 or a large RV trend. For a 2 R⊕ planet the expected semi-amplitude is ~2 m/s, so a
true RV mass needs a precision spectrograph. A multi-colour or space-based (e.g. CHEOPS)
transit would test chromaticity and pin down the shape. Until then it is a candidate with an
FPP near 50%.

## Reproducing

Scripts use absolute paths from the working session (`/root/ph/...`). Point them at the merged
release archives: Kepler PSF/SAP light curves and FITS under
`planet-search/database_expansion/kbonus*`, TESS light curve `evidence/tess/lightcurves`. Python
3.13; TRICERATOPS 1.1.0, lightkurve 2.6.0 and pytransit 2.2.0 in a virtualenv; batman 2.5,
emcee 3.1, astropy 8.0. TRICERATOPS is driven without its `target.__init__` (no MAST): see
`scripts/triceratops/run_*.py` for the exact star tables and inputs. Contrast curves in
`scripts/triceratops/hypo_cc_*.txt` are **hypothetical**, for what-if runs only.

No candidate was submitted, named or announced.
