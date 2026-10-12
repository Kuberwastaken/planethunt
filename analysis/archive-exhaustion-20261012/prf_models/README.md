# PRF inputs and interpolation

The FITS files are TESS sector-4-and-later PRFs from MAST. `downloads.json` records their URLs, dates and successful transfer status; `sectors.json` lists the four surrounding models used for each sector. They are interpolated at the cutout centre before shifting to the proper-motion-adjusted star positions.

`prf.py` is from Keaton Bell's MIT-licensed TESS_PRF repository. `UPSTREAM.json` identifies the upstream revision; `LICENSE` retains the licence. Only the imports for the unused online-download branch were moved inside that branch so offline reproduction does not require requests or BeautifulSoup. The interpolation code is unchanged. Always use the bundled local models when reproducing this analysis.

See the parent report for assumptions: the PRF is static within each sector, source fluxes are estimated from catalogue magnitudes, and this is an extraction-response experiment rather than a complete scene fit or calibrated blind-search completeness test.
