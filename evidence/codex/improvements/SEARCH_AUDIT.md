# Search wrapper audit and smoke results

Audited `run_search.py` and `acquire.py`, and their imported upstream `search.py`, `fastbls.py`, and `common.py`.

## Verified behavior

The chronological final-season split is selected from time/sector metadata before period searching. Discovery-only sector rejection avoids using heldout noise to decide discovery retention. Per-sector detrending does not mix the two subsets.

`smoke_search.py` invokes the actual wrapper against a temporary replacement ROOT. It exercises cleaning, binning, semi-coherent candidate generation, coherent refinement, event statistics, fixed-ephemeris holdout evaluation, result serialization, and manifest creation. It never writes synthetic discoveries into the real results directory.

| Injection | True period (days) | Recovered period | Discovery statistic | Heldout depth SNR |
|---|---:|---:|---:|---:|
| Regular transit | 2.371 | 2.3710418938 | 50.49 | 34.93 |
| Dense-star USP, 24.48-minute duration | 0.3173 | 0.3173059612 | 66.93 | 49.23 |

Both passed the wrapper's screening. Replacing every heldout flux value with independent noise left discovery period, epoch, duration, depth, and BLS statistic **exactly identical**. Noise holdout SNRs were -0.16 and 1.33. These are strong-signal implementation checks, not a sensitivity/completeness estimate and not evidence of a celestial discovery.

The deliberate real-data positive control, **known LHS 3844 b (TIC 410153553)**, also passed the independent raw-flux vetter under pipeline v3: 291 usable events, depth 4,342 +/- 57 ppm, period 0.462929624 days, and fixed-ephemeris S103/104 depth 4,456 +/- 99 ppm. It is explicitly a rediscovery of a known planet, not a new candidate. The independent check labels the season test retrospective because earlier processing occurred during pipeline development.

Two v3 screened periods on TIC 201293664 failed independent validation: all-data local SNRs 3.64/3.88 and final-season SNRs 1.56/1.91. Their durations occupy about 18%/21% of the period, further motivating caution. The separate v2 TIC 259999047 output is marked superseded and must not be interpreted as a current result.

## Parser correction

The upstream QLP parser selects `SYS_RM_FLUX` when present but otherwise raw `SAP_FLUX`, bypassing older corrected `KSPSAP_FLUX` or `DET_FLUX`. It also selects an error from a different flux column. A live check of TIC 273418879 sector 102 showed valid systematics-corrected flux but **every DET_FLUX_ERR value NaN**; the old reader discards all observations. `read_lc.py` instead uses a matching uncertainty when usable, otherwise measured point scatter in the selected flux's units, and explicitly records this fallback. It recovered **8,447 clean cadences** from that product. Five synthetic FITS tests cover these cases, cadence fallback, absent centroids, and explicit raw-flux fallback.

The acquisition wrapper must persist the returned `flux_column`, `error_source`, `exposure_source`, `raw_flux_fallback`, and `quality_column_missing` metadata. A star downloaded before the correction may omit affected QLP sectors; use manifests to decide selective reacquisition. A previously withheld season should remain withheld when products are refreshed; do not silently reassign it based on newly successful downloads.

## Remaining scientific and implementation limitations

- Coarse and refined USP duration grids have 30-minute and 24-minute lower limits, respectively. Denser/grazing stars can have shorter events; test additional short injections before lowering these bounds, with exposure integration/cadence accounted for.
- Inversion after asymmetric clipping is a conditional residual control, not the same full pipeline run on negated raw flux. Running both provides a sensitivity check; neither alone calibrates a survey false-alarm probability.
- `event_stats`'s discovery/holdout errors assume independent measurements and do not fully propagate baseline or correlated-noise uncertainty. Its depth uses all events even though `n_good_events` separately counts adequate coverage. Independent raw-flux event fits are needed on finalists.
- All stars and both search ranges contribute trial multiplicity. Selecting on heldout SNR makes the holdout part of final screening; it does not turn an individual local SNR into a globally calibrated discovery probability. Subsequent parameter tuning on observed holdout outcomes invalidates the original blind-test interpretation.
- Cache filenames contain only TIC/mode/inversion. Changing parser, clipping, duration grid, input products, or splitting logic requires explicit versioned outputs or invalidation; otherwise old JSON is silently reused.
- A failure in the highest-priority selected product currently has no fallback to a lower-priority product for the same sector. This loses coverage, especially when selected QLP products have unusable errors. Preserve the failure record and retry a valid alternative without changing split definitions after screening.
- No successful smoke test or screening result rules out an eclipsing binary, blending, stellar variability, a spacecraft artifact, or a previously reported candidate.
