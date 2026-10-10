# Archival planet search - 10 October 2026

## Result

**Credible, potentially unreported transit candidate around KIC 5689121 =
Gaia DR3 2103792461826460288 = TIC 120686465. Not a confirmed or statistically
validated planet. No discovery submission, naming, publication, or contact
with other people was made.**

The Kepler Bonus background-star search recovered a 13.76941357-day signal,
with a BLS box duration of 2.1376 hours. A local raw-PSF measurement found
2165 +/- 98 ppm across 70 usable events; 22 events in reserved quarters give
1929 +/- 159 ppm. Discovery-only exposure-integrated physical transit fits
are compatible with the catalog star and an approximately 3 Earth-radius
object, conditional on an undiluted planetary transit on that star.

The independent aperture check uses the correct SAP uncertainties in
`database_expansion/kbonus_independent_audit/`, superseding the initial
pilot SAP significances: overall local SNR 13.73, holdout 5.84. PSF and SAP
are different extractions of the same photons, not independent telescopes.

Original Kepler target-pixel files at the fixed ephemeris favor the candidate
over the brighter star 7.1 arcsec away in all 13 quarters. Fits use official
Kepler PRF calibration files. Conditional chi-square differences are not a
calibrated false-positive probability. Unresolved companions, background
eclipsing binaries and residual instrumental effects still require formal
validation and follow-up.

No matching reported signal was found in the retrieved Kepler KOI/TCE/EB,
NASA confirmed-planet, TESS TOI/CTOI/RAVEN catalogs, relevant background-star
papers, or indexed alias searches. The star previously appeared as a
possible MELANGE-3 association member. Absence from these searches is not
proof of novelty. See the complete audit in
`catalogs/kbonus2103792461826460288_novelty_report.json`.

## Reproduction

Use Python 3.12. `bash bootstrap.sh` creates `.venv`, installs the core
packages and clones/checks out the two upstream pipelines in sibling folders.
Their commit IDs are pinned in that script. The full local package inventory
is in `requirements-lock.txt`; core direct dependencies are in
`requirements-core.txt`. The runtime and dependencies are not shipped as a
binary environment. Public archive access is required to redownload data.

Extract `planet-search-tess-data.zip` and `planet-search-kepler-data.zip`
beside this project so their `planet-search/` directories merge with this one.
All three archives share that top-level folder. The data were split to stay
below the service's 512 MiB per-file limit.

```
bash bootstrap.sh
.venv/bin/python acquire.py --workers 6
.venv/bin/python run_search.py --workers 6
.venv/bin/python summarize.py
.venv/bin/python database_expansion/kbonus/pilot.py --limit 64 --workers 5
.venv/bin/python database_expansion/kbonus/known_control.py
.venv/bin/python database_expansion/kbonus/crosscheck.py
.venv/bin/python database_expansion/kbonus/candidate_neighbors.py
.venv/bin/python database_expansion/kbonus/pixel_localize.py
```

To recompute instead of using the saved caches, move the relevant `results/`
folder aside first. Do not overwrite provenance or mix old and new input
hashes. The timing-safe reanalysis has its own script and output folder;
use its results instead of interpreting affected original QLP holdouts.

## Scope and controls

Initial TESS selection: 175 stars, 350 two-band searches (0.2-0.5 days and
0.5-25 days), with the latest observing season held out. Nine signals across
eight hosts passed the initial numerical screen. The 100 matched inverted
searches produced five initial screen passes, showing that that screen alone
does not establish a discovery.

An archive documentation audit subsequently identified QLP timing errors in
sectors 99-104. Used files on 44 stars were affected. All 44 were rerun in
both bands with those entire QLP sector products removed, retaining original
results for audit. These revised holdouts are retrospective. TIC 358559650's
earlier holdout rejection was withdrawn: its signal repeats but has broad
shape, depth variability and an astrometric-binary/blend concern. TIC
94753488 remains unresolved broad dimming, not a defensible planet claim.

Kepler Bonus pilot: 64 stars selected from 1,800 eligible background M dwarfs
after excluding official Kepler primary targets. Criteria: catalog minimum
PSF fraction >0.5, aperture crowding metric >0.7, at least eight available
quarters, then brightness order. The last ceil(25%) usable quarters, at
least two, were reserved before search. The search spans 0.5-25 days and
assumes 5-solar stellar density for candidate generation, not validation.
Two signals passed the first screen. The other, Gaia2129404966720268672 /
KIC10794841 at 1.4102 days, has secondary dimming and weak aperture support.

Known positive controls are explicitly labeled and excluded from discovery
claims: LHS3844 b in TESS, and Kepler-138 c/d in Kepler Bonus. Strong synthetic
injections and a holdout-randomization check verified basic recovery and
absence of direct holdout-flux leakage. They do not measure survey completeness.
Inverted and phase controls are diagnostics, not calibrated survey-wide FAPs.
The completed Kepler pilot includes 64 matched inverted runs, with zero
initial-screen survivors. A latent SAP inversion issue was repaired for
future runs; the existing inverted outputs never reached the SAP-vetting
branch, so their recorded search results and conclusions are unaffected.

## Files that matter

- `database_expansion/kbonus/pilot_summary.csv`: real/inverted pilot results.
- `database_expansion/kbonus/results/2103792461826460288.json`: initial search
  and fixed-ephemeris measurements, with input hash.
- `database_expansion/kbonus_independent_audit/`: independent physical shape
  fits and corrected SAP uncertainty checks.
- `database_expansion/kbonus/pixels/localization.json`: quarter-by-quarter
  source localization, with images and original-pixel download manifest.
- `catalogs/kbonus2103792461826460288_novelty_report.json`: novelty/identity audit.
- `database_expansion/TIMING_REANALYSIS.md`: QLP timing warning and repairs.
- `improvements/`: independent vetting and ingestion fixes plus synthetic tests.
- `manifests/`: public source URLs, download hashes, parser provenance and splits.
- `results_v1/`, `results_pre_final/`: superseded outputs retained only for audit.

## Other archives identified

Kepler Bonus is the implemented expansion. EVEREST/K2SFF offer complementary
K2 observations; TGLC offers Gaia-informed TESS extraction; CDIPS and PATHOS
offer young/cluster-star photometry. These are useful follow-up search pools,
but they were not all scanned in this run. More archives do not by themselves
imply a high probability of a *new* planet. Existing known multi-planet hosts
can be searched for additional periods only after masking all known signals.
Seed lists are saved under `database_expansion/` without being represented as
completed searches.

## Attribution and primary sources

Search functions import Paras Chopra's MIT-licensed `tess-planet-candidates`
and Eumemic's MIT-licensed `exoplanets`; upstream repositories are retrieved
by `bootstrap.sh`, not bundled. Preserve their licenses when redistributing.

- https://github.com/paraschopra/tess-planet-candidates
- https://github.com/eumemic/exoplanets
- Kepler Bonus: Martinez-Palomera, Hedges & Dotson (2023),
  https://arxiv.org/abs/2310.17733 ; https://archive.stsci.edu/hlsp/kbonus-bkg
- Kepler Bonus data DOI: https://doi.org/10.17909/7jbr-w430 (CC BY 4.0).
- QLP data and timing warnings: https://archive.stsci.edu/hlsp/qlp
- NASA Exoplanet Archive TAP: https://exoplanetarchive.ipac.caltech.edu/TAP/
- MAST data archive: https://mast.stsci.edu/
- Gaia archive: https://gea.esac.esa.int/archive/
- EVEREST: https://archive.stsci.edu/hlsp/everest
- TGLC: https://archive.stsci.edu/hlsp/tglc
- CDIPS: https://archive.stsci.edu/hlsp/cdips
- PATHOS: https://archive.stsci.edu/hlsp/pathos

This work uses public NASA Kepler/TESS observations from MAST, Gaia DR3
catalog data, and cited third-party high-level science products. No claim of
exclusive priority or statistical validation is made.
