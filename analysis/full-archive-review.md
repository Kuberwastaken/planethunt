# Full archive audit - 10 October 2026

## Receipt and integrity
The shared ChatGPT file controls returned three complete archives. Download succeeded without login. Their temporary signed URLs are deliberately not published.

| Archive | Bytes | SHA-256 |
|---|---:|---|
| planet-search-results.zip | 294813531 | 60e86d7e2fc42f78d6b80b5925d13c38cd07a6117467a23cb7d484e132380f3f |
| planet-search-kepler-data.zip | 163854848 | 4fd59efb1f252116b37d9f6a076c84e67a93249d00c7cb152e373d36c58640dd |
| planet-search-tess-data.zip | 448391783 | 98a5dec45bb2c74fccd7788ace394c698a8d973ee63347a1c0686ad15bbfac85 |

All ZIP CRC tests pass. All 2,401 file records in the supplied manifests match exact byte counts and SHA-256 hashes after merged extraction. Safe extraction checked for absolute paths and parent traversal. Secret-pattern scans found no tokens, keys or bearer strings. This is scientific code/data, not a publication of the shared-chat transcript.

Modest reports, scripts, tables and figures are mirrored under `evidence/codex/`. New raw FITS/NPZ and files over 2 MB remain in the source-preserving release archives. The previously published 36.7 MB known_signals.csv remains in git to avoid rewriting history. `analysis/bulk-files.json` is the map of files intentionally kept in the archive assets instead of git. These are not missing from the received evidence.

## Reproduced corrected aperture measurement
`analysis/kepler-sap-recheck.json` records an independent execution of the supplied fixed-ephemeris local vetter against original KBonus FITS and SAP_FLUX_ERR. It exactly reproduces:
- 70 usable events: 1438.4753706 +/-104.7895544 ppm, local SNR 13.7272782.
- 22 reserved-quarter events: 1264.6166038 +/-216.4155804 ppm, local SNR 5.8434638.
- Original FITS SHA-256: 44980afb7843a4507c898eb1ce5d5733029a0f4658f6b96d6196db49df37c06f.

This is a reproducibility check using the supplied algorithm at a previously inspected ephemeris. It does not grant a new blind holdout, independently validate the search pipeline, or compute FPP. The original data remain unchanged. PSF and SAP are two reductions of the same observations.

## Measurement files now inspected
The independent audit selects discovery quarters 1,2,3,4,6,7,8,10,11 and reserved quarters 12,14,15,16. The search script constructs this split from metadata before searching. Period 13.769413569662944 d, epoch -2030.687110167298 BTJD. Original TIME is BKJD (BJD_TDB -2454833); subtracting 2167 gives BTJD (BJD_TDB -2457000). This agrees with 136.312889832702 BKJD.

Corrected SAP odd/even difference: 0.633 nominal sigma. Phase-0.5 secondary depth 17.508 +/-58.569 ppm, local SNR 0.299. A small opposite-phase secondary not seen at these errors does not exclude every eccentric EB or unresolved blend. Maximum positive-event contribution is 4.20%; minimum leave-one-event-out local SNR is 13.41 overall and 5.47 in reserved data. These diagnostics reduce the single-event concern but do not calibrate global odds.

Fixed catalog-density circular discovery fits give contact duration 2.1355-2.4201 h and conditional radius 2.9588-3.0887 Earth radii. Stellar-parameter uncertainty is not propagated; approximate fixed limb darkening and no dilution are assumed. Do not quote these as a validated size with error bars.

Original official-PRF localization favors the target in all 13 quarters, summed delta-chi-square 799.20. Removing the common shift retains 13/13 preference (797.72). A spatial-plane background still yields 13/13 target preference (579.27 without shift, 581.06 with shift). These stress tests share the root difference images; they are not independent pixel observations. Models can miss other neighbors, PRF errors, covariance and unresolved companions. None of these chi-square sums is FPP.

## Corrected timing-safe TESS outcomes
`database_expansion/timing_safe_all44/disposition_summary.json` records 88 repeats, zero execution errors, and two screen survivors:
- TIC 244869034 rank 2: not robust; local combined 3.89 sigma and reassigned holdout 0.19 sigma.
- TIC 358559650: persistent timing-clean dimming, but too broad for the catalog-density circular model, season-dependent amplitude and reported binary/source concerns. Not a defensible planet detection.

Forty-two targets have no screen survivor in the restricted rerun. These are retrospective and do not establish survey completeness or absence of planets. The older CSV holdout rejection of 358559650 remains historical and is superseded by the actual timing-safe output.

## Method improvements and limits
The archive includes parser corrections, synthetic wrapper tests showing no direct held-out-flux leakage into discovery outputs, broad-signal baseline comparisons, and known controls. SAP errors were originally mismatched to PSF; corrected aperture uncertainties are essential. The inverted pilot's SAP bug was repaired; saved inverted survivors never reached that branch, so no corrected SAP null calibration can be inferred from those outputs. Multiple archive products reuse photons. Source and novelty checks are incomplete, finite snapshots.

## Scientific verdict
The full pack strengthens inspectability and supports a credible target-localized transit candidate. It does not establish a confirmed planet, first-discovery priority or permission to assign a scientific name. Formal blend/FPP analysis, model/calibration checks and suitable independent observations remain needed. No submission, naming or outreach is performed.
