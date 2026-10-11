# Planethunt

A public, inspectable record of two archival transit searches. **No confirmed planet is claimed.**

- Read the digest in `index.html` (GitHub Pages serves the repository root).
- Read [`planethunt.md`](planethunt.md) first when using this repository with an LLM.
- Scientific synthesis: [`analysis/review.md`](analysis/review.md).
- Original evidence: [`evidence/tess/`](evidence/tess/) and [`evidence/codex/`](evidence/codex/).
- Completeness and file-level checksums: [`inventory.json`](inventory.json) and `SHA256SUMS`.

## Current state: 11 October 2026

KIC 5689121 / TIC 120686465 is a well-vetted **planet candidate**: it passes held-out, Kepler-169, raw-pixel centroid and dilution tests, with a TRICERATOPS false-positive probability of about 0.07 (validation needs below 0.015; the open loophole is a planet around an unresolved bound companion). TIC 309780779 is a real repeating signal that is probably an eclipsing binary (false-positive probability about 0.57). Nothing is confirmed or validated, and novelty is provisional. The public site (`index.html`) was rebuilt on 12 October as a monochrome evidence atlas. Scientific status remains the 11 October evidence snapshot; no new validation is implied.

## Earlier state: 10 October 2026

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
Codex's Kepler Bonus search was extended to 1,672 more stars with matched inverted controls: no second candidate, and the real run passed the first screen no more often than the null. See `analysis/kbonus-extension-20261011/README.md`.

## Validation pack 2026-10-11
[`analysis/validation-20261011/README.md`](analysis/validation-20261011/README.md): false-positive and holdout vetting of both candidates, an independent re-check, sky images and charts, with its own checksums.

## Public website

The repository root remains deployable as a static GitHub Pages site, including at
`/planethunt/`. No package installation, external JavaScript, analytics, or API keys are required.

```sh
python3 scripts/site/charts.py
python3 scripts/site/build_site.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. The build runs offline from the saved evidence.

- `scripts/site/page.html`: public narrative and accessible HTML template.
- `scripts/site/site.css`, `site.js`: responsive styles and browser interactions.
- `docs/charts/`: 20 reproducible SVG diagnostics, including a Lyra locator.
- `scripts/site/evidence_atlas.py`: five additional diagnostics, run automatically by the
  page build. Derived residuals, event histogram and quarter coverage have CSV sidecars
  in `docs/derived/`. No scientific fitting is rerun.
- `docs/fonts/`: self-hosted Barlow Condensed Light and IBM Plex Mono, with OFL licenses.
- `docs/site-data.json`: compact export of the actual folded bins, transit model,
  74 event measurements, and all 46,523 original detrended cadences.
- Survey switching uses local, unaltered cutouts with separate SVG markers, scale bars,
  and orientation. The presentation defaults to monochrome, with an original-colour toggle. Credits and fetch parameters are in `docs/sky/SOURCES.json`.
- The page preserves the original evidence sections in dated expandable appendices.
  The file explorer reads `inventory.json` and `analysis/bulk-files.json` on demand.

Charts and content remain available without JavaScript. Interactive data are loaded as
needed; failure messages retain links to the source CSVs. Native dialogs support keyboard
focus and Escape. Motion is disabled for reduced-motion preferences.

`sky.py` is the earlier annotation pipeline and is not required for this build.
Do not rerun scientific analyses just to rebuild the website.

After changing tracked presentation files, run `python3 scripts/site/refresh_manifests.py`
to update the root inventory/checksums. Original evidence-pack checksums remain unchanged.
