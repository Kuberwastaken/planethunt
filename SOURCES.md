# Sources and attribution

## Received artifacts
- TESS evidence tarball, SHA-256 `d43383ffc2d1b896cf0e1a8e41ba32e1821b9d1c77bf76b39bf320dc3825d443`, 10 October 2026. Original checksums retained; public wording edits documented.
- Codex summary PDF and readable partial code/catalog pack, supplied by Kuber on 10 October 2026. The full results and separate Kepler/TESS data archives were later received through the supplied ChatGPT share on the same date. The corrected aperture local measurements were reproduced at the saved ephemeris; other reports are inspected saved outputs, not a claim of end-to-end independent reproduction.

## Primary public references checked on 10 October 2026
- Kepler Bonus background products, authors and CC BY 4.0 attribution: https://archive.stsci.edu/hlsp/kbonus-bkg
- Martinez-Palomera, Hedges & Dotson (2023), Kepler Bonus: https://arxiv.org/abs/2310.17733
- QLP products and the barycentric timing correction warning for sectors 99-104: https://archive.stsci.edu/hlsp/qlp
- NASA Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu/
- Gaia Archive: https://gea.esac.esa.int/archive/
- Paras Chopra's upstream transit-search repository: https://github.com/paraschopra/tess-planet-candidates
- Eumemic's upstream exoplanet-search repository: https://github.com/eumemic/exoplanets

The QLP warning is independently visible on the archive documentation. The candidate-specific catalog assertions are from dated audit snapshots, not a fresh independent query of all catalogs by this publication.

## Licenses
Third-party code license notices are retained in `third_party/`. Paras's repository distinguishes MIT source code from CC BY 4.0 text, figures and videos. Kepler Bonus high-level data products are CC BY 4.0. Attribute NASA/MAST, the named product authors, Gaia/ESA, and the upstream search authors when reusing their material. No blanket license here overrides third-party rights. Repository synthesis and source reports are separate from upstream code.

## Website typography

Self-hosted [Barlow Condensed Light and ExtraBold](https://github.com/google/fonts/tree/main/ofl/barlowcondensed)
and [IBM Plex Mono Regular](https://github.com/google/fonts/tree/main/ofl/ibmplexmono),
obtained from the official Google Fonts repository on 12 October 2026. Both use the
SIL Open Font License 1.1; the complete notices are retained in `docs/fonts/`.

## Planet illustrations and derived comparisons

The four planet scenes and share card were generated with the built-in OpenAI image tool on
12 October 2026. They are artist interpretations, not observations or physical simulations.
Prompts, assumptions and source inputs are retained in `docs/planet/PROVENANCE.json`; the
share prompt is in `docs/planet/SHARE-PROMPT.txt`. Atmospheric colour and cloud structure are
not measured. The cutaway shows one possible interior; layer dimensions are schematic.

The saved on-target transit and stellar model supplies radius, period, separation, irradiation
and equilibrium temperature. `planet_facts.py` derives diameter, spherical volume, circular
orbital speed, light-travel time and years-per-Earth-year with explicit constants in its output.
No mass, density, gravity, rotation, atmosphere composition or companion count is inferred.

Context references checked on 12 October 2026:
- [NASA: Neptunian planets](https://science.nasa.gov/exoplanets/neptune-like/)
- [Bean, Raymond & Owen: The nature and origins of sub-Neptune size planets](https://arxiv.org/abs/2010.11867)
- [NASA: sub-Neptune atmosphere observations](https://science.nasa.gov/missions/webb/nasas-james-webb-space-telescope-primed-to-lift-the-haze-surrounding-sub-neptunes/)

Social metadata follows the [Open Graph protocol](https://ogp.me/); search metadata follows
[Google Search Central guidance](https://developers.google.com/search/docs/appearance/site-names).
The favicon is an original code-rendered planetary mark, not a measured phase.

## Website icon

The navigation GitHub mark comes from [Primer Octicons](https://github.com/primer/octicons), under the MIT license retained in `docs/icons/octicons-LICENSE.txt`.

## Archival extension — 12 October 2026

[Archive follow-up provenance and methods](analysis/archive-followup-20261012/README.md) records NASA Exoplanet Archive/SpiKeS, IRSA Spitzer CBCD/CBUNC/mask products and official warm IRAC PRFs, ESA Gaia DR3, public Keck/Gemini metadata, and STScI/MAST TESScut images from NASA TESS/SPOC. Input URLs, query failures, retrieval dates and hashes are preserved within the pack. Generated photometry, residual figures and TESS diagnostics are analysis products, not new telescope observations. No third-party data license is replaced by this repository.

## Second archive pass (12 October 2026)

See [the reproducible pack](analysis/archive-exhaustion-20261012/README.md): Chrome inspection of NASA Inventory, and exports from IRSA Data Discovery and current MAST HST/JWST searches; TGLC DOI 10.17909/610m-9474; ZTF DR24 and NEOWISE-R through IRSA; PTF through IRSA; CFHT MegaCam through CADC; ESA HST/JWST ObsCore footprint services; Barber et al. 2022 (AJ 164, 88), CDS J/AJ/164/88/table5. Exact requests and timestamps are saved in the pack. No new validation probability is claimed.

The extension also retains official IRSA SPHEREx joint forced spectrophotometry, the 288-image inventory, 2MASS PSC photometry, early WISE single exposures and AllWISE catalogue photometry. [SPHEREx methods and flags](https://irsa.ipac.caltech.edu/onlinehelp/spherex/spherex/sp.html) and [2MASS flux zero points](https://www.ipac.caltech.edu/2mass/releases/allsky/faq.html) govern the spectral audit. The conditional TESS pixel-injection analysis uses official mission PRFs and [Keaton Bell's MIT-licensed interpolation code](https://github.com/keatonb/TESS_PRF); upstream revision and license are retained in the analysis pack. Derived spectra plots are exploratory analysis products, not planet spectra or close-companion contrast limits.
