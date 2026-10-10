# Timing-warning audit and separate reanalysis

Source: [MAST QLP release documentation](https://archive.stsci.edu/hlsp/qlp), checked 2026-10-10. Its S99–104 availability entries remain starred as awaiting redelivery after barycentric-timestamp errors. The warning starts in the second half of S99; we conservatively flag or remove the entire affected sector product. S74–79 require corrected v02 products.

Among actual successful final-run acquisition records, **91 of 203 QLP products** fall within S99–104. They affect **44 of 175 survey stars**, with 90 flagged products appearing in holdouts. One affected discovery product is TIC 201726620 S101. No used S74–79 QLP v01 cases were found. Thus the survey is not a uniformly timing-clean null result. This audit identifies a data-quality risk; it does not prove that the timing bug caused any specific signal or failed test.

Two screened finalists used flagged QLP holdouts: TIC 358559650 S99 and TIC 241606913 S102. Their original weak-holdout conclusions cannot be used as robust astrophysical vetoes. The underlying measured numbers are preserved with this qualification. Priority signal TIC 94753488 uses S39/66/93 and is unaffected by this particular warning.

## Separate timing-safe repeats

`timing_safe_repeat.py` copies original NPZ arrays into an isolated branch after removing the entire affected QLP products. It runs the existing root search with the latest remaining season assigned as holdout **before the new period fit**. Earlier work already inspected these stars, so these are retrospective consistency tests, not fresh blind validation. Original survey data and outputs are untouched; manifests preserve both original and filtered hashes.

### TIC 358559650

After removing S99, discovery sectors are 9/36/62/63 and the reassigned holdout is 89/90. The search finds P = **0.2846614176 days**, box duration **1.56 hours**, discovery BLS statistic **16.0**, and holdout depth/error **27.8**. It passes the original screening rules.

The box spans 22.8% of its period, making the default local window insufficient. A separately recorded broad diagnostic therefore uses the same explicit +/-0.35P and +/-0.40P windows and linear/quadratic models used for other broad finalists.

| Baseline | Half-window | Combined depth (ppm) | Combined local SNR | Clean fixed-holdout depth (ppm) | Holdout local SNR |
|---|---:|---:|---:|---:|---:|
| Linear | 0.35P | 329 ± 15 | 21.7 | 468 ± 24 | 19.7 |
| Linear | 0.40P | 342 ± 15 | 23.1 | 487 ± 23 | 21.3 |
| Quadratic | 0.35P | 279 ± 21 | 13.1 | 335 ± 33 | 10.0 |
| Quadratic | 0.40P | 282 ± 19 | 14.6 | 362 ± 30 | 11.9 |

Quadratic fits give opposite-phase depths consistent with zero. Amplitude varies with sector and baseline model, but the signal is clearly recoverable without the flagged QLP sector. The catalog star R = 0.618739 R_sun and M = 0.603115 M_sun give circular central contact duration **0.914 hours**, appreciably shorter than the fitted 1.56-hour box. Broad shape, source localization, dilution, activity, and prior reports remain unresolved.

**Disposition: reopen as strong periodic dimming requiring source/shape/novelty checks; no planet classification.** The new result does not prove that timestamp errors alone explain the old failed S99 test; ephemeris and baseline changes also matter.

### TIC 241606913

After removing S102, discovery sectors are 11/38 and holdout sectors 64/65. The new searches return P = 24.86697 days and 1.864180 days; their holdout depth/error ratios are 1.39 and -0.23. Neither passes screening. This does not prove the old 0.92507-day signal absent: it states the independent fresh candidate generation did not select a screen-passing signal in this smaller timing-safe data subset.

## Outputs

- `qlp_timing_audit.csv` and `qlp_timing_audit_summary.json`
- `timing_safe_repeat/summary.json`
- `timing_safe_repeat/manifests/*_filter.json`
- `timing_safe_repeat/results/*.json`
- `timing_safe_repeat/vetting/358559650_broad_diagnostic.json`

Original finalist dispositions in `../improvements/vetting/final_dispositions.*` now carry the timing qualification. A robust whole-survey null statement would require correcting/replacing/removing all flagged products and rerunning the affected targets, with the resulting tests acknowledged as retrospective.
