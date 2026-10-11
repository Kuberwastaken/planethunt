# Links, datasets and references

## This project
- Site: https://kuber.studio/planethunt/
- Repository: https://github.com/Kuberwastaken/planethunt
- Source archives used (release `evidence-20261010`):
  - https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-kepler-data.zip
    (SHA-256 4fd59efb1f252116b37d9f6a076c84e67a93249d00c7cb152e373d36c58640dd)
  - https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-tess-data.zip
    (SHA-256 98a5dec45bb2c74fccd7788ace394c698a8d973ee63347a1c0686ad15bbfac85)
  - https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/planet-search-results.zip
    (not re-downloaded; its contents are mirrored in `evidence/codex/`)

## Target identifiers
- KIC 5689121 · TIC 120686465 · Gaia DR3 2103792461826460288
- RA 285.907827°, Dec +40.941988° (ICRS, epoch 2016)
- Neighbour: KIC 5689116 · Gaia DR3 2103792427466721792 (7.1″ west)
- Nearby known system: Kepler-169 (KIC 5689351, KOI-505), ~4.4′ away

## Datasets
- Kepler Bonus background-star photometry (KBONUS-BKG), Martínez-Palomera et al.:
  https://archive.stsci.edu/hlsp/kbonus-bkg · DOI 10.17909/7jbr-w430
- Kepler target pixel files (KIC 5689116, quarters 1–16): MAST, https://archive.stsci.edu/kepler/
- TESS SPOC FFI and QLP light curves (TIC 309780779): MAST, https://archive.stsci.edu/hlsp/qlp
- Gaia DR3: https://gea.esac.esa.int/archive/
- NASA Exoplanet Archive KOI/TCE/confirmed tables (snapshots in `evidence/codex/database_expansion/`):
  https://exoplanetarchive.ipac.caltech.edu/

## Sky images (centred on the candidate; north up, east left)
- Pan-STARRS colour, 2′:
  https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FPanSTARRS%2FDR1%2Fcolor-z-zg-g&width=1200&height=1200&fov=0.0333&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png
- Pan-STARRS colour, 10′: same URL with `fov=0.1667`
- STScI Pan-STARRS cutout: https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=285.907827+40.941988&filter=color&filetypes=stack&size=480
- DSS2 colour, 15′:
  https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FDSS2%2Fcolor&width=1200&height=1200&fov=0.25&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png
- Interactive: https://aladin.cds.unistra.fr/AladinLite/?target=285.907827%20%2B40.941988&fov=0.03&survey=CDS%2FP%2FPanSTARRS%2FDR1%2Fcolor-z-zg-g

## Kepler-169 references
- Rowe et al. 2014, ApJ 784, 45 (discovery; Kepler-169 e P = 13.767102 d)
- TEPCat: https://astro.keele.ac.uk/jkt/tepcat/planets/Kepler-169e.html
- exoplanet.eu: https://exoplanet.eu/catalog/kepler_169_e--2195/

## Tools
- TRICERATOPS (Giacalone et al. 2021): https://github.com/stevengiacalone/triceratops
- batman (Kreidberg 2015), emcee (Foreman-Mackey et al. 2013), astropy, lightkurve

## Credits for images
- Pan-STARRS1 Surveys (PS1) and the PS1 public science archive (STScI), via CDS hips2fits
- DSS2: STScI/AURA, Palomar Observatory / UK Schmidt Telescope
- Gaia DR3: ESA/Gaia/DPAC
- Kepler: NASA; Kepler Bonus: Martínez-Palomera et al.
