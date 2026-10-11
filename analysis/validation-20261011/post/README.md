# Post assets: KIC 5689121

Graphics and plotted data. Charts are PNG; photo-heavy images are high-quality JPEG (q93) to keep
the pack small. Scripts that make each one are in `../scripts/post/` and `../scripts/sky/`.

## `sky_images/`: real telescope images (Pan-STARRS, registered to Gaia DR3)
| File | What it shows |
|---|---|
| `post_00_real_sky_pair.jpg` / `_stack.jpg` | 10′ field + 2′ zoom; host (orange), KIC 5689116 (blue dashed), scale bars, N/E. No other text. **Best lead image.** |
| `kic5689121_panstarrs_side.jpg` / `_vertical.jpg` | Same idea at native Pan-STARRS resolution (made in a parallel session) |
| `post_06_kepler_pixels_pair.jpg` / `_stack.jpg` | Kepler's real 4″ pixels at true sky footprint, beside the pixels that lost light during transit overlaid on Pan-STARRS (14σ and 12σ on the host) |
| `post_00_real_sky.jpg` | Annotated version with labels, position and status |

## `charts/`
| File | What it shows |
|---|---|
| `post_03_folded_dip.png` | All 70 transits folded, 15-min bins, MCMC model, key numbers |
| `post_02_lightcurve.png` | 4 years of Kepler photometry with predicted transits, six single transits |
| `post_05_three_views.png` | The same 34″ patch: DSS2, Pan-STARRS, Kepler pixels, missing-light map |
| `post_01_where.png` | Lyra locator, Gaia finder chart, Kepler stamp, difference image |
| `post_04_status.png` | What's ruled out vs still open (FPP ≈ 0.07) |
| `post_07_model.png` | To-scale model: orbit vs Mercury, size vs Earth/Neptune, star size in its sky |

## `source_images/`
Survey images as supplied (Pan-STARRS 2′ and 10′ via CDS hips2fits, STScI PS1 2′ cutout, DSS2 15′),
`registration.json` (offsets vs Gaia DR3).

## `data/`: every plotted number
| File | Contents |
|---|---|
| `kic5689121_lightcurve_psf.csv` | Full Kepler Bonus PSF light curve: time (BTJD and BJD_TDB), flux, error, display-detrended flux, quarter, in-transit flag |
| `kic5689121_folded_15min_bins.csv` | Folded 15-minute bins (hours from mid-transit, ppm, error, n) |
| `kic5689121_transit_model.csv` | MCMC median transit model |
| `kic5689121_per_transit_depths.csv` | Depth of each of 74 events (vetter's stricter cut: 70), with predicted mid-times and held-out flag |
| `kic5689121_diffimage_season*_{electrons_per_s,snr}.csv` | Transit difference images per Kepler season |
| `kic5689121_gaia_neighbours_120arcsec.csv` | Gaia DR3 stars within 120″ |
| `kic5689121_key_numbers.json` | Target, ephemeris, transit parameters, FPP summary |
| `kic5689121_model_numbers.json` | Orbit, insolation, equilibrium temperature, star's apparent size |

Times are BTJD (BJD_TDB − 2,457,000) unless a column says BJD.
