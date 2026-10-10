# Broad-signal follow-up — pipeline v3

Two screened signals had no usable windows in the default local vetter because its half-window is capped at 0.23 periods, almost the same as their fitted transit duration. **That limitation does not reject those signals.** The separate exploratory diagnostic `broad_signal_vet.py` explicitly widens each half-window to 0.35P and 0.40P and compares linear and quadratic local baselines. The period, epoch, duration, discovery sectors, and holdout sectors remain fixed to the search outputs. Exposure integration, per-event fits, empirical noise floors, event-cluster scatter, and leave-one-event-out checks are retained.

These new diagnostic choices followed inspection of the candidates. The results are robustness/consistency checks, not a new blind validation or a calibrated discovery probability. JSON reports include search/input SHA256 hashes and all per-event and per-sector measurements.

## TIC 94753488 — retain as unresolved periodic dimming

P = 0.4297023627 days, box duration = 2.36 hours, duty fraction = 22.9%.

| Baseline | Half-window | Combined depth (ppm) | Combined local SNR | Fixed holdout depth (ppm) | Holdout local SNR |
|---|---:|---:|---:|---:|---:|
| Linear | 0.35P | 127.8 ± 18.4 | 6.93 | 139.8 ± 36.8 | 3.80 |
| Linear | 0.40P | 126.2 ± 18.6 | 6.80 | 147.6 ± 37.1 | 3.98 |
| Quadratic | 0.35P | 103.5 ± 18.3 | 5.66 | 134.9 ± 36.4 | 3.71 |
| Quadratic | 0.40P | 118.1 ± 18.5 | 6.38 | 133.3 ± 36.1 | 3.69 |

150 usable event windows include 46 in the fixed holdout sector 93. No single event dominates. The signal survives the reasonable alternative baseline models tested here. A phase-0.5 depression is marginal: roughly 30–46 ppm, with local ratios 2.4–3.1; it should not be described as a robust secondary eclipse or as definitely absent.

The catalog star has R = 0.763526 R_sun and M = 0.73 M_sun, implying density 1.640 solar and a/R_star = 2.826 at this period. For a circular central transit and a radius ratio inferred from the search depth, the maximum contact duration is approximately **1.20 hours**, about half the fitted 2.36-hour box. Interpreting the box width as contact duration would instead imply circular central density approximately 0.263 solar. That large disagreement challenges a small planet on a circular orbit around the catalogued star.

It is **not** a mathematical impossibility for every planetary orbit: an idealized central transit at apastron could attain this duration at e ≈ 0.589, placing periastron at only 1.16 stellar radii. This is a geometric illustration, not a fitted eccentric orbit or evidence favoring that scenario. Stellar-parameter error, an alternative period, dilution by a different host/background binary, stellar variability, and instrumental origins remain to be resolved. A properly constrained physical transit/EB fit and pixel/source localization are the useful next tests.

Disposition: **reproducible broad periodic dimming; astrophysical source and nature unresolved; not a validated planet or a novelty claim.**

## TIC 456716455 — baseline-sensitive broad modulation

P = 0.4066725895 days, box duration = 2.16 hours, duty fraction = 22.1%.

| Baseline | Half-window | Combined depth (ppm) | Combined local SNR | Fixed holdout depth (ppm) | Holdout local SNR |
|---|---:|---:|---:|---:|---:|
| Linear | 0.35P | 68.3 ± 10.7 | 6.35 | 59.0 ± 13.0 | 4.54 |
| Linear | 0.40P | 73.6 ± 10.4 | 7.07 | 63.3 ± 12.6 | 5.03 |
| Quadratic | 0.35P | 28.9 ± 14.9 | 1.94 | 26.0 ± 17.9 | 1.45 |
| Quadratic | 0.40P | 33.4 ± 13.6 | 2.45 | 27.4 ± 16.4 | 1.67 |

There are 172 event windows, including 114 in holdout sectors 81/82. Most of the apparent dip is absorbed by local curvature; primary and holdout support both become weak with quadratic baselines. Linear fits also show an opposite-phase **brightening** at approximately -42 to -47 ppm, consistent with broad modulation. This brightening also weakens when fitting curvature. These patterns favor broad variability or detrending/baseline sensitivity over a robust box-shaped transit, without uniquely identifying the cause.

Catalog R = 0.719906 R_sun and M = 0.77 M_sun imply central circular contact duration approximately 1.09 hours, versus a 2.16-hour box. The same conditional geometry caveats apply as for TIC 94753488.

Disposition: **deprioritize as a planet candidate because transit-like significance is strongly baseline-dependent; origin still unclassified.**

## Control-phase limitations

Only 18–22 phase-control measurements meet the local side-coverage requirements. Their boxes avoid the primary but overlap one another extensively, and viable phases are concentrated around the opposite half of the orbit. The phase-0.5 feature can be included in those controls. Consequently, depth divided by their scatter is only a sensitivity diagnostic; it is not an independent-sample significance, tail probability, or survey false-alarm rate. The table's event-cluster errors also do not capture every possible inter-event/season correlation.

## TIC 113710966, rank 2 — residual modulation/alias concern

This final screened signal exceeds the default vetter's quarter-period duration limit, so it received the same separate broad diagnostic: P = 0.3428908563 days, duration = 2.28 hours, duty fraction = 27.7%.

| Baseline | Half-window | Combined depth (ppm) | Combined local SNR | Holdout local SNR | Opposite-phase depth (ppm) | Opposite-phase local SNR |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 0.35P | 10.41 ± 1.28 | 8.13 | 2.57 | 8.46 ± 1.21 | 6.97 |
| Linear | 0.40P | 9.39 ± 1.27 | 7.37 | 2.45 | 8.24 ± 1.21 | 6.80 |
| Quadratic | 0.35P | 9.27 ± 1.58 | 5.86 | 2.12 | 7.52 ± 1.51 | 4.97 |
| Quadratic | 0.40P | 11.45 ± 1.49 | 7.69 | 2.13 | 8.04 ± 1.52 | 5.29 |

There are 414 primary-event windows, including 58 in the fixed holdout. Comparable opposite-phase dimming, weak holdout support, and extreme width prevent a clean planet interpretation. The first search signal already had a near-identical period of 0.3425718602 days (0.093% different) before iterative masking; the second signal can therefore be a residual nearby-period alias of the same underlying variability rather than an additional body.

Catalog R = 0.832935 R_sun and M = 0.88 M_sun give circular central contact duration approximately **1.144 hours**, versus the 2.28-hour box. Only eight heavily overlapping phase controls have adequate coverage; their scatter ratios of 1.38–2.55 do not provide discovery significance.

Disposition: **deprioritize as a planet candidate; residual modulation/alias or other non-planet explanations remain plausible.**

Two synthetic checks verify that the broader diagnostic preserves a real injected broad box under both baseline choices, while a smooth sinusoid's apparent box depth falls substantially with a quadratic baseline. These checks validate the intended diagnostic behavior, not survey completeness or planet classification.
