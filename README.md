# Planethunt

A public, inspectable record of two archival transit searches. **No confirmed planet is claimed.**

- Read the digest in `index.html` (GitHub Pages serves the repository root).
- Read [`planethunt.md`](planethunt.md) first when using this repository with an LLM.
- Scientific synthesis: [`analysis/review.md`](analysis/review.md).
- Original evidence: [`evidence/tess/`](evidence/tess/) and [`evidence/codex/`](evidence/codex/).
- Completeness and file-level checksums: [`inventory.json`](inventory.json) and `SHA256SUMS`.

## Current state: 10 October 2026

TIC 309780779 has a repeated TESS dip and target-consistent difference imaging, but no formal false-positive probability or demonstrated held-out test in the supplied evidence. KIC 5689121 / TIC 120686465 has a Kepler candidate reported with a reserved-quarter test and official-PRF localization, but those measurement files are still awaiting the full Codex archive. The supplied summary and catalog audit can be read now; their scientific claims are not presented as independently reproduced.

TIC 305054512's corrected pixel analysis is off-target and is not carried as an on-target planet candidate.

This first version is an honest partial evidence release, not the full Codex pack. Missing files are listed explicitly; links to absent files are not created. Upstream historical declarations about “no publication” describe the state before this repository, not the current state.

## Reproducibility

Historical TESS scripts retain their original scratch paths and are not a one-command rerun. Read the limitations in `planethunt.md`. Codex's bootstrap needs requirements and pipeline files not yet received. Do not silently overwrite original results or claim successful reproduction.

Third-party code licenses are retained under `third_party/`; original data/product attribution is in `SOURCES.md`. No blanket license is applied to third-party artifacts.
