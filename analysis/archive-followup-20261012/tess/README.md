# TESS check of KIC 5689121 / TIC 120686465

**No convincing recovery in this exploratory aperture reduction. No calibrated exclusion of the Kepler signal has been established.** The 7.1″ pair is separated by only 0.34–0.36 TESS pixels; the extracted flux is blended and no target-specific dilution correction has been measured.

The TESScut endpoint succeeded after the general MAST inventory failed. All ten listed sectors were downloaded: **14, 26, 40, 41, 53, 54, 74, 75, 80, 81**, spanning 2019–2024. Both initial failures and successful retries are preserved. This contains **62,082 quality-zero, finite cadences** and **20 adequately sampled predicted event windows**, not 20 detected transits.

| Aperture radius | Fixed-ephemeris box depth (ppm) | Diagnostic uncertainty (ppm) | Scatter of 80 shifted-epoch control depths (ppm) |
|---|---:|---:|---:|
| 1.0 pixel | −483 | 958 | 1,189 |
| 1.5 pixels | −1,221 | 1,236 | 1,490 |
| 2.0 pixels | −2,075 | 1,384 | 1,762 |

Positive depth means dimming. The negative point estimates are consistent with noisy measurements; none is a significant brightening claim. A diluted transit may be smaller than these uncertainties. The different apertures share pixels and must not be counted as independent experiments. The larger control scatter also shows why the formal depth/error ratio is not a calibrated detection statistic.

![Fixed-ephemeris TESS check](results/tess_folded.png)

## Method and limits

- Preserved the complete 9×9-pixel TESScut FITS files as lossless gzip archives, including pipeline flags and WCS. Original and compressed hashes and request URLs are in [provenance.json](provenance.json).
- Kept quality=0 cadences with finite time, flux and errors across the cutout. Used exact pixel-overlap circular apertures at the WCS target position, fixed before looking at the folded signal. Estimated a per-cadence sky level from the median of a fixed mask of faint outer pixels (radius >3.2 pixels, lowest 60% of the median-image outer pixels). This removes a sky pedestal, not contaminating stellar light or PRF wings.
- Used the **unchanged Kepler ephemeris**, a 2.3-hour box and local linear baselines within ±0.5 d, excluding ±0.12 d around each predicted event. Clipped 5σ baseline outliers only. Required both baseline sides and at least half the expected in-event samples (minimum three). No search for a new period or best-fitting epoch was performed.
- Event errors include baseline-fit uncertainty and a 30-minute residual-bin inflation where estimable. Combined events with inverse-variance weights and inflated for between-event dispersion. Noise is still correlated and aperture-dependent; these are diagnostic errors, not a likelihood validated for planet model comparison.
- Examined epoch offsets −60, −30, 0, +30, +60 minutes. No positive depth/error ratio reaches 1 at those offsets in any aperture. These are timing-sensitivity checks, not a posterior ephemeris update.
- Evaluated 80 shifted-epoch controls between +0.35 d and P−0.35 d. They overlap in data and are **not** independent trials or a false-alarm probability. The saved control distribution gives a useful empirical noise scale.
- Injected 500, 1000 and 2400 ppm boxes into the extracted **aperture flux**, before baseline fitting. Recovered increments agree within ~0.3%. This checks depth transfer through this baseline procedure; it is not pixel-level injection, blind recovery, a completeness measurement or evidence that such shallow signals are detectable here. There is no correction for target throughput or crowding.
- The folded figure uses unweighted 30-minute bins with standard errors for display. The numeric summary uses weighted event depths; read the table for inference. Long-cadence integration and detailed transit shape are not modelled in this box diagnostic.

The faint source, unresolved close pair, other field light and imperfect background/systematics removal limit this extraction. A calibrated multi-source TESS PRF model, pixel-level injections and more advanced instrumental detrending remain possible specialist work. They have **not** been completed here. Do not feed this non-detection into an FPP calculation as though it were a calibrated exclusion limit.

[Per-sector coverage](results/sectors.json) · [Event estimates](results/events.csv) · [Summary and timing tests](results/summary.json) · [Pixel panels](results/tess_pixels.png). Compact `.npz` files include all retained aperture fluxes, formal errors, background series and extraction masks.

## Reproduce offline

Use the parent pack's Python 3.12 environment and pinned requirements:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/planethunt-irac-env/bin/python analysis/archive-followup-20261012/scripts/analyze_tess.py --out /tmp/planethunt-tess-check
```

The script defaults to the committed gzip frames and preserved Kepler ephemeris. A fresh run from those compressed files reproduced `summary.json`, `sectors.json` and `events.csv` **byte-for-byte** on 12 October 2026. Images were visually inspected. Inputs need no network access. The live URLs may generate FITS files with changed creation headers on a later request; original hashes identify this exact snapshot.

Data: NASA TESS/SPOC, accessed through STScI/MAST's [TESScut service](https://mast.stsci.edu/tesscut/docs/getting_started.html). These are new checks of KIC 5689121, separate from the repository's historical TESS searches of other TIC targets.

## 13 October 2026 recheck

The ten-sector reduction was rerun from the retained pixel cubes in a fresh environment; `summary.json`, `events.csv` and `sectors.json` reproduced byte-for-byte. Six-sector TGLC summary values also reproduced. This checks reproducibility, not an independent reduction. The point estimates, including negative aperture depths, must remain visible. The conditional PRF injection is not a completeness test; a joint period/epoch uncertainty propagation and calibrated recovery/exclusion analysis remain outstanding. See [the audit](../../editorial-audit-20261013/README.md).
