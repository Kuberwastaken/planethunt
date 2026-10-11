# Planethunt validation pass and outreach pack, 11 October 2026

Everything produced on 11 October 2026 to vet the two Planethunt leads and to present the stronger
one publicly: analysis code, results, logs, an independent check, figures, the real sky images,
post graphics, the data behind every plotted number, and the post text.

**Status in one line:** KIC 5689121 is a well-vetted **planet candidate** (false-positive
probability ≈ 0.07; validation needs < 0.015). TIC 309780779 is a real periodic signal but most
likely an eclipsing binary (FPP ≈ 0.57). Nothing here is a confirmed or validated planet.

## How to merge into the repo

Unzip at the repository root. Everything lands in `analysis/validation-20261011/`; no existing
file is overwritten. Then optionally:

1. Link this folder from the repo `README.md` and from `index.html`.
2. Use `post/sky_images/post_00_real_sky_pair.jpg` and `post/charts/post_03_folded_dip.png` on the
   site; `post/README.md` lists every graphic.
3. Check `SHA256SUMS` after copying (`sha256sum -c SHA256SUMS` from this folder).

## Folder map

| Path | What it is |
|---|---|
| `README.md` | This file |
| `SCIENCE.md` | Full write-up: every test, number, caveat and what's still open |
| `TASKS.md` | Task log: what was done, what was blocked, next steps |
| `LINKS.md` | Datasets, archives, survey-image URLs, references, credits |
| `figures/` | Diagnostic figures (dilution + centroid; TESS holdout + phase scan) |
| `results/kepler/` | KIC 5689121 results: ephemeris MCMC, Kepler-169 overlap, depths, crowding, dilution fits, centroid tests, difference images |
| `results/tess/` | TIC 309780779 results: blind BLS, transit fits, holdout, odd/even + secondary scan |
| `results/triceratops/` | FPP runs (JSON per run), logs, summary, background star populations |
| `scripts/kepler/`, `scripts/tess/`, `scripts/triceratops/` | Analysis code, one script per test |
| `scripts/post/`, `scripts/sky/` | Code for every graphic and the sky-image registration |
| `scripts/sky/stack.py` | Code from a parallel session that made the `kic5689121_panstarrs_*` images |
| `independent_check/` | A second agent's from-scratch re-derivation of the key numbers, with its own README |
| `post/` | Sky images, charts and plotted data; see `post/README.md` |

## Key results: KIC 5689121 / TIC 120686465

| Quantity | Value |
|---|---|
| Position | RA 19h 03m 37.9s, Dec +40° 56′ 31″ (Lyra) · Gaia DR3 2103792461826460288 |
| Host | M dwarf, 0.51 R☉, 0.51 M☉, ~3,630 K, G 16.3, ~298 pc (~970 ly), RUWE 0.98 |
| Period | 13.769448 ± 0.000065 d (full-baseline MCMC) |
| Transit | ~0.24% deep (PSF; 1,830–2,430 ppm depending on method), ~2.1–2.4 h, 70 events |
| Size if planetary | ≈ 2.5–3 R⊕ (likely sub-Neptune) |
| Orbit / climate (model) | 0.09 AU · ~5× Earth's insolation · T_eq ≈ 420–430 K (zero albedo) |
| FPP (TRICERATOPS) | ≈ 0.07 (4 runs, 0.058–0.089); ≈ 0.03 with a *hypothetical* AO curve |

What the checks show:
- **Real and periodic.** Still present (5.8σ) in the last 4 quarters, which were held out of the search.
- **Not Kepler-169.** Kepler-169 e (13.767 d, 4′ away) never overlaps a transit (closest 67 h); periods differ by 32σ; the target folded on all 5 Kepler-169 ephemerides gives zero depth.
- **On the right star.** A raw-pixel centroid test rejects the brighter neighbour KIC 5689116 at Δχ² = 934 and every other Gaia star within 30″; the neighbour's own light curve shows no dip; the PSF vs aperture depth gap is explained by dilution (p = 0.22).
- **No eclipsing-binary signature.** Odd/even agree (0.6σ); no secondary eclipse.
- **Honest negative.** About 2 of 1,736 inverted null searches are as strong by search statistics alone, so the case rests on the vetting.
- **Main loophole.** A planet around an unresolved bound companion star (STP ≈ 0.07). Needs high-resolution imaging plus companion limits.

## Key results: TIC 309780779

Real, repeating 8.7236-day signal: recovered blind in each half of the data, lands on schedule
89 cycles later, flat depth, no secondary. But FPP ≈ 0.57, dominated by an eclipsing binary bound
to the star (SEB ≈ 0.42); imaging can't close it. Needs reconnaissance spectroscopy.

## Verification

- Release archives `evidence-20261010` downloaded; SHA-256 hashes match `analysis/full-archive-review.md`.
- A separate agent rebuilt the key numbers with its own code (`independent_check/`): all passed,
  with caveats folded into `SCIENCE.md` (depth is method-dependent; ~15σ against measured scatter, 43σ formal).
- Sky images are registered to Gaia DR3 positions (median offset < 0.1″).

## Not done here (hard obstructions)

MAST, the Gaia archive, VizieR and ExoFOP were unreachable from the sandbox, so there was no
TESScut/official-PRF redo for TIC 309780779 and no live TOI/CTOI check. Telescope work (AO imaging,
spectra, multi-band transits) is the next step. See `TASKS.md`.

## Reproducing

Scripts use the absolute paths of the working session (`/root/ph/...`). Point them at the merged
release archives (Kepler Bonus FITS and light curves under `planet-search/database_expansion/kbonus*`,
the TESS light curve under `evidence/tess/lightcurves`). Environment: Python 3.13, numpy, scipy,
astropy 8.0, batman 2.5, emcee 3.1; TRICERATOPS 1.1.0 with lightkurve 2.6.0 and pytransit 2.2.0 in a
virtualenv. TRICERATOPS is driven offline (no MAST): see `scripts/triceratops/run_*.py`. The
contrast curves `scripts/triceratops/hypo_cc_*.txt` are **hypothetical**, for what-if runs only.

## Wording and credit

- Call it a **planet candidate**. It is not confirmed, validated or named, and "new" means absent
  from the catalogue snapshots checked, not proven first.
- Credit NASA Kepler, Kepler Bonus (Martínez-Palomera et al., DOI 10.17909/7jbr-w430),
  Pan-STARRS1/STScI, DSS2 (STScI/AURA) and Gaia DR3 (ESA/DPAC) wherever their data appear.
