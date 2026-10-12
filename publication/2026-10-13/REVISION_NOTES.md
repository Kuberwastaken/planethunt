# Revision 2 — author-requested corrections, 13 October 2026

Search history and normalization were checked against `evidence/codex/database_expansion/kbonus/pilot.py`, the 64-row `pilot_targets.csv`, and the saved holdout manifest (Q12/Q14/Q15/Q16). The retained input flux is median-normalized per quarter; the BLS branch calls a separate cleaning step after splitting discovery/holdout data. The all-baseline fit profiles local event baselines separately.

The dated catalogue statement reports the scope and outcome of checks completed by 12 October, rather than asserting universal absence. Saved target/neighbor crossmatches, 12 October exact-ID queries, ExoFOP target export and the follow-up audit are indexed in `claim-sources.json`. ExoFOP non-uploads are not a guarantee that no observations exist.

Bibliography verified against primary archive/publication metadata:
- Kepler Bonus journal version: AJ 166, 265, DOI https://doi.org/10.3847/1538-3881/ad0727 (publisher-deposited Crossref metadata saved in `kbonus-journal-crossref.json`).
- MAST data DOI and citation request: https://archive.stsci.edu/hlsp/kbonus-bkg — https://doi.org/10.17909/7jbr-w430.
- Gaia DR3: https://doi.org/10.1051/0004-6361/202243940.
- TIC: https://ntrs.nasa.gov/citations/99611215072524 — https://doi.org/10.3847/1538-3881/ab3467.
- Kepler-169 discovery/validation: https://www.ipac.caltech.edu/publication/2014ApJ...784...45R — https://doi.org/10.1088/0004-637X/784/1/45.

Author supplied ORCID 0009-0003-1379-7856 and email kuberhob@gmail.com and authorized the independent-researcher affiliation and split MIT / CC BY 4.0 licensing. No institution was inferred. Human review of the final revision remains required before journal submission.

The initial release stays frozen. The second release is the evidence version intended for Zenodo ingestion; once verified, its DOI replaces the temporary GitHub citation in the working journal manuscript.
