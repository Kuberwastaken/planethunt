# Planethunt

A public, inspectable record of two archival transit searches. **No confirmed planet is claimed.**

- Read the digest in `index.html` (GitHub Pages serves the repository root).
- Read [`planethunt.md`](planethunt.md) first when using this repository with an LLM.
- Scientific synthesis: [`analysis/review.md`](analysis/review.md).
- Original evidence: [`evidence/tess/`](evidence/tess/) and [`evidence/codex/`](evidence/codex/).
- Completeness and file-level checksums: [`inventory.json`](inventory.json) and `SHA256SUMS`.

## Current state: 10 October 2026

TIC 309780779 has a repeated TESS dip and target-consistent difference imaging, but no formal false-positive probability or demonstrated held-out test in the supplied evidence. KIC 5689121 / TIC 120686465 has a Kepler candidate reported with a reserved-quarter test and official-PRF localization, and the measurement files are now received. A fixed-ephemeris recheck reproduces the corrected aperture depth and held-out local SNR, but is not fresh blind validation.

TIC 305054512's corrected pixel analysis is off-target and is not carried as an on-target planet candidate.

The full Codex results, Kepler data and TESS data archives have now been received and integrity-checked. Scientific scripts, measurements, reports and modest tables are mirrored in `evidence/codex/`; bulky source data remain in checksummed release archives. Read [`analysis/full-archive-review.md`](analysis/full-archive-review.md) for the new audit and exact corrected SAP recheck. Historical declarations about "no publication" describe the state before this repository.

## Reproducibility

Historical TESS scripts retain their original scratch paths and are not a one-command rerun. Read the limitations in `planethunt.md`. Codex's requirements and scripts are now included. Merge all three release archives and follow their reproduction instructions; a full end-to-end rerun has not been performed here. Do not silently overwrite original results or claim successful reproduction.

Third-party code licenses are retained under `third_party/`; original data/product attribution is in `SOURCES.md`. No blanket license is applied to third-party artifacts.

## Complete source downloads
- [planet-search-kepler-data.zip](https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-kepler-data.zip)
- [planet-search-results.zip](https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-results.zip)
- [planet-search-tess-data.zip](https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-tess-data.zip)

Download all three and merge their `planet-search/` folders. All are audited, source-preserving release assets. Exact hashes are in `analysis/full-archive-review.md`.

## Extension 2026-10-11
Codex's Kepler Bonus search was extended to 497 more stars with a matched inverted control: no second candidate, and the real run passed the first screen no more often than the null (10 signals each). See `analysis/kbonus-extension-20261011/README.md`.
