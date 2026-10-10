# Catalog audit, 2026-10-10 UTC

These downloads support an initial search and novelty check. Catalog absence is not evidence that a periodic dip is planetary, and catalog absence alone cannot establish a first discovery.

## Successfully retrieved

- NASA Exoplanet Archive `toi`: 8,148 rows (archive current release date may precede download date).
- NASA Exoplanet Archive `pscomppars`: 6,445 confirmed-planet rows.
- ExoFOP community TOI export: 5,138 rows.
- RAVEN author data on Zenodo record 19661443: first-stage `nsfp09_table.csv` (14,815 rows), vetted (2,170), validated (143), and radius-above-8-Earth validation table (207).
- Official MAST SPOC TCE bulk index: all 132 linked tables downloaded successfully; 341,351 rows, 68,456 TIC hosts. Many TCEs are false alarms or duplicate detections. A TCE is prior detection, not confirmation of a planet.
- Villanova TESS EB export: 17,605 records / 17,597 TICs including candidates; confirmed-only export has 4,584 records / 4,578 TICs. The server returns HTML containing comma-separated records even when CSV is selected. `villanova_eb.csv` is parsed from that response; raw HTML retained.
- Public candidates in the supplied Paras and Eumemic repositories, including 2,405 distinct hosts in Eumemic's all-sky table, are excluded from claims of our first discovery.

## Files to use

- `known_tics.csv`: conservative host-level union, with source labels. It includes TCE and EB-candidate hosts; it is intended for selecting fresh search targets, not adjudicating an additional planet in a known system.
- `known_tic_sources.csv`: uncollapsed source memberships.
- `known_signals.csv`: source TIC, period, epoch and coordinates where available.
- `selected_prior_matches.csv`: exact TIC matches to the selected 175-star search, including periods and epochs. 271 TCE records match 35 stars; no other exact host overlaps found in these downloaded sources.
- `selected_neighbor_prior_matches.csv`: screening cone of 120 arcsec around selected targets. Empty in this snapshot. TCE coordinates are absent, so this is not a complete TCE contamination test. Proper motion is not propagated.
- `refresh_catalogs.py`: reproducible core downloads and host exclusions; `--tce` refreshes TCE tables.
- `match_selected.py`: rebuilds normalized signal list and selected-target matches.

URLs, timestamps and SHA-256 hashes are in sidecars or `provenance.json`. The initial PS query used an invalid Gaia column and failed; the corrected successful query and hash are in `nasa_pscomppars.provenance.json`.

## Important gaps before a novelty claim

ExoFOP full TOI export timed out twice. NASA's successfully downloaded TOI table serves as the present catalog snapshot; the repo's prior-day ExoFOP copy is not silently relabeled fresh. ExoFOP target JSON attempt returned an HTML page and is retained as HTML, not valid catalog JSON.

For any surviving signal: fetch live target and neighbor ExoFOP records, resolve aliases in SIMBAD, propagate Gaia positions to each observing epoch, compare nearby TCE/TOI/EB periods and epochs including rational period aliases, inspect additional survey tables (e.g. ExoMiner, T16), and search literature/preprints/Zenodo by TIC, Gaia, aliases and sky coordinates. Use transit timing uncertainty accumulated over the baseline, rather than a fixed period tolerance alone. Diluted eclipses can be produced far outside a single TESS pixel.

Independent pixel localization, multiple detrendings, leave-one-sector/transit-out tests, odd/even and secondary eclipses, a variability model comparison, and null/injection calibration are separate requirements from catalog novelty.

## First preliminary survivor

TIC 95431305 is AD Leo / GJ 388, a famous active flare star. The historical 2.23-day planet interpretation has substantial activity-based refutation, including Carmona et al. 2023, arXiv:2303.16712. The preliminary 0.236475713-day signal is a different period; no report of that exact signal was identified in the targeted searches, but that does not establish novelty or a planet. See `tic95431305_literature_check.json` and primary-source SIMBAD text.
