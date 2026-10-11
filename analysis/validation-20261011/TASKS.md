# Task log, 11 October 2026

Everything below was run on the `evidence-20261010` release archives (SHA-256 verified against
`analysis/full-archive-review.md`), plus files already in the repository.

## Done

| # | Task | Result | Where |
|---|---|---|---|
| 1 | Inventory local data; download and verify release archives | Kepler + TESS archives hashes match | — |
| 2 | Kepler-169 ephemeris-match test (KIC 5689121) | Excluded: no overlap in 70 events (closest 67 h), period 32σ apart, null depth at all 5 Kepler-169 ephemerides | `scripts/kepler/k169_overlap.py`, `kdepth.py` |
| 3 | Full-baseline MCMC ephemeris (KIC 5689121) | P = 13.769448 ± 0.000065 d; ρ* consistent with host | `scripts/kepler/kfit.py` |
| 4 | Empirical false-alarm rate vs 1,736 inverted null searches | ≈ 2 null stars as strong; not unique by detection statistic | `scripts/kepler/null_fap2.py` |
| 5 | PSF vs SAP depth reconciliation | Dilution model fits (p = 0.22); contaminant-hosted rejected (p ≈ 1e−36) | `kcrowd.py`, `kdilution_pooled.py` |
| 6 | Bright-neighbour light curve test | KIC 5689116: 24 ± 41 ppm vs ≈ 1,100 needed | `kdepth.py` |
| 7 | Raw-TPF centroid test, all Gaia sources within 30″ | Target favoured; neighbour Δχ² = 934, others ≥ 4,300 | `kcentroid_tpf.py`, `kcentroid_all.py` |
| 8 | KBonus centroid-column test | Uninformative (columns don't respond); not used | `kcentroid.py`, `kcentroid2.py` |
| 9 | TESS blind BLS: full, inverted, each half separately | Top peak 8.7236 d in both halves; inverted max SDE 7.8 | `scripts/tess/bls.py` |
| 10 | TESS transit fits (free, density prior, each half) | b ≈ 0.95, Rp ≈ 2.0 R⊕ with prior; shape degenerate without | `scripts/tess/tfit.py` |
| 11 | TESS frozen-ephemeris holdout | Late half on schedule within uncertainty; 9–10σ | `scripts/tess/holdout.py` |
| 12 | TESS odd/even, per-era depth, all-phase secondary, phase null | All clean | `scripts/tess/scan.py` |
| 13 | TRICERATOPS FPP, Kepler (offline driver, Gaia-cone background) | FPP ≈ 0.07 (STP-dominated); 0.03 with a hypothetical AO curve | `scripts/triceratops/`, `results/triceratops/` |
| 14 | TRICERATOPS FPP, TESS | FPP ≈ 0.57 (SEB-dominated); 0.45 with a hypothetical speckle curve | same |
| 15 | Diagnostic figures | 2 figures | `figures/` |
| 16 | Independent check by a separate agent with its own code | Key numbers reproduced; caveats folded into README | `independent_check/` |
| 17 | Transit difference images per Kepler season | Missing light peaks on the candidate's pixel in seasons 0–2 | `scripts/post/diffimg.py` |
| 18 | Post graphics + plotted data as CSV | charts + 15 data files | `post/charts/`, `post/data/` |
| 19 | Register user-supplied Pan-STARRS/DSS2 cutouts to Gaia DR3; annotate real-sky images | Offsets < 0.1″ (PS1); 2 more graphics | `scripts/sky/`, `post/` |
| 20 | Clean sky images (pair/stack) and Kepler-pixel vs missing-light images | 6 text-free graphics | `post/sky_images/`, `scripts/sky/clean_*.py` |
| 21 | To-scale model graphic (orbit vs Mercury, size vs Earth/Neptune, star in its sky) | T_eq ≈ 417–430 K, 0.09 AU, star ~6× Sun's width | `post/charts/post_07_model.png`, `scripts/sky/model_fig.py` |
| 24 | Packaging: single ZIP, README, LINKS, checksums | — | `README.md`, `LINKS.md`, `SHA256SUMS` |

## Blocked here (hard obstructions)

- MAST, Gaia archive, VizieR, ExoFOP unreachable: no TESScut/official-PRF redo for TIC 309780779,
  no RUWE for TIC 309780779, no live TOI/CTOI check.
- Telescope work: AO/speckle imaging, reconnaissance spectra, RVs, multi-band transits.

## Next

1. KIC 5689121: AO contrast curve; MOLUSC companion limits using RUWE 0.98; rerun TRICERATOPS with both.
2. TIC 309780779: 2–3 reconnaissance spectra (SB2 / RV trend); official-PRF pixel test via TESScut.
3. Re-check TOI/CTOI and literature on the day of any announcement.
