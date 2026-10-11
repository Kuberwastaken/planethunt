"""Builds index.html. Run from repo root after charts.py and sky.py:  python3 scripts/site/build_site.py
Reuses the deep-dive sections of the previous page (kept verbatim as data) from scripts/site/legacy_sections.html."""
import re, os
CH = 'docs/charts/'
V = 'analysis/validation-20261011/'

def svg(name, label):
    s = open(CH + name + '.svg').read()
    s = s.replace('aria-labelledby="t d"', f'aria-labelledby="{name}-t {name}-d"').replace('id="t"', f'id="{name}-t"').replace('id="d"', f'id="{name}-d"')
    return s

def fig(inner, cap, wide=False):
    return f'<figure class="{"wide" if wide else ""}">{inner}<figcaption>{cap}</figcaption></figure>'

def img(src, alt, w=None, h=None):
    d = f' width="{w}" height="{h}"' if w else ''
    return f'<img src="{src}" alt="{alt}" loading="lazy"{d}>'

def a(href, t): return f'<a href="{href}">{t}</a>'

legacy = open('scripts/site/legacy_sections.html').read()
def leg(i):
    m = re.search(rf'<section class="section" id="{i}">(.*?)</section>', legacy, re.S)
    return m.group(1)

tess_old = leg('tess').replace('No formal FPP, completed independent holdout, or complete negative-control results are included.',
    'Update, 11 October: a TRICERATOPS run later gave a false-positive probability of about 0.57 and a frozen-ephemeris holdout was added (both in the TESS section above). This original text describes the 10 October evidence.')
kep_old = leg('kepler').replace('No formal FPP, high-resolution imaging, reconnaissance spectra or new ground-based transit is reported.',
    'A TRICERATOPS false-positive probability of about 0.07 was added on 11 October (see above); no high-resolution imaging, reconnaissance spectra or new ground-based transit exists yet.')
assert 'Update, 11 October' in tess_old and 'about 0.07 was added' in kep_old

def deep(i, inner, title):
    return f'<details class="deep" id="deep-{i}"><summary><span>{title}</span></summary><div class="deepbody">{inner}</div></details>'

explore = leg('explore').replace('style="display:block;width:100%;font:inherit;padding:12px;margin:10px 0 18px;border:1px solid #c0bebf;border-radius:4px"', 'class="search"')
explore = explore.replace('<button id="file-more" style="font:inherit;padding:12px 20px;background:white;border:1px solid #c0bebf;border-radius:4px;cursor:pointer">', '<button id="file-more" class="btn">')
extension = leg('extension')
files_sec = leg('files')

script = re.search(r'<script>.*?</script>', legacy, re.S).group(0).replace('#eae9ea', '#2a3552')

CSS = open('scripts/site/site.css').read()
SITEJS = open('scripts/site/site.js').read()
CHAPS = [('summary','Verdict','what we know'),('sky','The sky','six real images'),('kepler','The signal','Kepler transit'),('vetting','Vetting','8 checks'),('fpp','False positives','FPP 0.07'),('planet','The planet','if it is real'),('tess','TESS lead','probably binary'),('search','Searches','null controls'),('verify','Independent check','integrity'),('next','Next steps','what is blocked'),('deep','Deep dive','original evidence'),('explore','File explorer','every path'),('links','Links','data and credits')]
SHEET = ''.join(f'<a class="press" href="#{i}"><b>{n:02d}</b>{t}<small>{d}</small></a>' for n,(i,t,d) in enumerate(CHAPS,1))
METER = ('<figure class="meter wide"><svg viewBox="0 0 720 170" role="img" aria-labelledby="mt md"><title id="mt">False-positive probability against the validation line</title><desc id="md">Scale from 0 to 0.10. Kepler candidate at about 0.07, TESS lead at 0.57 off the scale, validation line at 0.015.</desc>'
 '<rect x="20" y="62" width="680" height="16" rx="8" fill="rgba(255,255,255,.1)"/><rect x="20" y="62" width="476" height="16" rx="8" fill="#ff9f5a"/>'
 '<line x1="122" y1="44" x2="122" y2="96" stroke="#62d8a6" stroke-width="3"/><text x="122" y="32" fill="#62d8a6" font-size="21" font-weight="600" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif">0.015 validation line</text>'
 '<text x="496" y="32" fill="#ff9f5a" font-size="21" font-weight="600" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif">0.07 KIC 5689121</text><line x1="496" y1="40" x2="496" y2="58" stroke="#ff9f5a" stroke-width="2"/>'
 '<g fill="rgba(235,238,248,.5)" font-size="18" font-family="system-ui,-apple-system,sans-serif" text-anchor="middle"><text x="20" y="128">0</text><text x="360" y="128">0.05</text><text x="700" y="128">0.10</text></g>'
 '<text x="700" y="160" fill="#ff7b7b" font-size="18" text-anchor="end" font-family="system-ui,-apple-system,sans-serif">TESS lead TIC 309780779: 0.57, off this scale</text></svg>'
 '<figcaption>Where the Kepler candidate sits against the bar for statistical validation. Both numbers are TRICERATOPS outputs from the 11 October validation pass.</figcaption></figure>')
SHEET_IDS = {i:t for i,t,d in CHAPS}

PS1 = 'https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FPanSTARRS%2FDR1%2Fcolor-z-zg-g&width=1200&height=1200&fov=0.0333&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png'
PS1_10 = PS1.replace('fov=0.0333', 'fov=0.1667')
STSCI = 'https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=285.907827+40.941988&filter=color&filetypes=stack&size=480'
DSS2 = 'https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FDSS2%2Fcolor&width=1200&height=1200&fov=0.25&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png'
TMASS = 'https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2F2MASS%2Fcolor&width=1200&height=1200&fov=0.1667&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png'
WISE = 'https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS%2FP%2FallWISE%2Fcolor&width=1200&height=1200&fov=0.1667&projection=TAN&coordsys=icrs&ra=285.907827&dec=40.941988&format=png'
ALADIN = 'https://aladin.cds.unistra.fr/AladinLite/?target=285.907827%20%2B40.941988&fov=0.03&survey=CDS%2FP%2FPanSTARRS%2FDR1%2Fcolor-z-zg-g'
REL = 'https://github.com/Kuberwastaken/planethunt/releases/download/evidence-20261010/'

def metric(b, s): return f'<div class="metric"><b>{b}</b><small>{s}</small></div>'
def fact(k, v): return f'<div class="fact"><span>{k}</span><strong>{v}</strong></div>'

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Two archival transit searches: one well-vetted Kepler planet candidate (KIC 5689121), one TESS signal that is probably an eclipsing binary. Every test, chart, image and link.">
<meta name="theme-color" content="#0b1020"><title>Planethunt | A planet candidate, and everything we checked</title>
<style>{CSS}</style></head><body>
<div class="edge" aria-hidden="true"></div>
<header class="top"><a class="brand press" href="#top">Planethunt</a><span class="now" aria-live="off"></span><button class="menu press" type="button" aria-expanded="false" aria-controls="sheet"><i></i>Sections</button><span class="prog" aria-hidden="true"></span></header>
<div class="scrim" aria-hidden="true"></div>
<nav class="sheet" id="sheet" aria-label="Sections"><div class="grab"></div><h2>Jump to</h2>
{SHEET}</nav>
<main id="top">

<section class="hero">
<div><span class="eyebrow">Archival research · updated 11 October 2026</span>
<h1>One planet candidate. <span>Everything we checked.</span></h1>
<p class="lead">A faint red dwarf in Lyra dims by 0.24% every 13.77 days. After 24 tasks of checks it still looks like a planet. It is not confirmed, and the main open question is a hidden companion star.</p>
<div class="pills"><span class="pill ok">Candidate, not a discovery</span><span class="pill warn">False-positive probability about 0.07</span><span class="pill">Validation needs below 0.015</span></div></div>
<figure class="lensfig"><div class="lens"><div class="ph">{img('docs/sky/ps1-2arcmin.jpg','Pan-STARRS colour image 2 arcminutes wide centred on KIC 5689121, the target ringed in orange and the brighter neighbour KIC 5689116 in blue dashed',1000,1000)}</div></div>
<figcaption>KIC 5689121 (orange ring) and its brighter neighbour KIC 5689116 (blue dashed, 7.1″ west). Real Pan-STARRS DR1 image, 2′ wide, north up, east left. Credit: Pan-STARRS1 / STScI via CDS hips2fits.</figcaption></figure>
</section>

<div class="stats rv"><div><b>13.769<em> d</em></b><span>orbital period, ±0.000065</span></div><div><b>0.24<em>%</em></b><span>transit depth, 70 transits</span></div><div><b>6<em>/8</em></b><span>vetting checks passed, 2 open</span></div><div><b>0.07</b><span>false-positive probability. Validation needs 0.015</span></div></div>
<div class="path rv"><a class="press" href="#summary"><b>Verdict</b><span>What we know, see and don't</span></a><a class="press" href="#sky"><b>See it</b><span>Six real sky images</span></a><a class="press" href="#vetting"><b>Test it</b><span>Eight checks, 14 charts</span></a><a class="press" href="#links"><b>Get the data</b><span>Every link and file</span></a></div>

<div class="notice"><strong>An unconfirmed signal is not a discovery.</strong> Neither lead is validated. "New" means absent from the catalogue snapshots we checked, not proven first. No candidate has been named, submitted or announced. Null-control results and failed leads are on this page on purpose.</div>

<section class="section" id="summary"><div class="eyebrow">The short version</div><h2>Two leads, two very different outcomes</h2>
<div class="grid">
<article class="card lead-card"><span class="tag good">Kepler · well vetted candidate</span><h3>KIC 5689121 <small>/ TIC 120686465</small></h3>
<p>A repeating 0.24% dip on a faint M dwarf 298 pc (about 970 light-years) away. It survives a held-out test, a raw-pixel centroid test, a Kepler-169 exclusion and a false-positive model.</p>
<div class="metrics">{metric('13.769 d','period, ±0.000065')}{metric('0.24%','depth, 70 transits')}{metric('2.5-3 R⊕','if on target and planetary')}</div>
<div class="facts">{fact('False-positive probability','about 0.07 (4 runs: 0.058-0.089)')}{fact('Main loophole','a planet around an unseen bound companion star')}{fact('Next step','adaptive-optics imaging plus a companion limit from Gaia RUWE')}</div></article>
<article class="card"><span class="tag bad">TESS · probably an eclipsing binary</span><h3>TIC 309780779</h3>
<p>A real, repeating 8.7236-day dip, recovered blind in each half of the data and on schedule 89 cycles later. But it is shallow, short and grazing-shaped, and the false-positive model puts about 57% on a false positive, mostly a bound eclipsing binary.</p>
<div class="metrics">{metric('8.7236 d','period')}{metric('~400 ppm','depth, 46 events')}{metric('0.57','false-positive probability')}</div>
<div class="facts">{fact('Dominant scenario','eclipsing binary bound to the target (about 42%)')}{fact('Imaging helps?','not much: 0.57 falls only to about 0.45')}{fact('Next step','2-3 reconnaissance spectra, then a multi-colour transit')}</div></article>
</div>
<div class="triptych">
<div><h3>What we know</h3><ul><li>The Kepler dip repeats on a fixed schedule and shows in quarters held out of the search (5.8σ).</li><li>It is not Kepler-169 e, which has almost the same period 4′ away.</li><li>The missing light is on KIC 5689121, not the brighter neighbour or any other Gaia star within 30″.</li><li>No odd/even difference or secondary eclipse in either lead.</li></ul></div>
<div><h3>What we see</h3><ul><li>A dip about 2,400 ppm deep and 2.1-2.4 h long, repeated 70 times over four years.</li><li>A red dwarf (0.51 R☉, 3,630 K) with a brighter blue star 7.1″ west.</li><li>Shallower aperture depths where more neighbour light is in the aperture, as dilution predicts.</li></ul></div>
<div><h3>What we do not know</h3><ul><li>Whether a hidden companion star hosts the planet or the signal (the 0.07).</li><li>The planet's mass. The star is too faint for a realistic radial-velocity measurement.</li><li>Whether anyone has independent claim to the signal. Novelty is provisional.</li></ul></div>
</div></section>

<section class="section" id="sky"><div class="eyebrow">What the target looks like</div><h2>The sky around KIC 5689121</h2>
<p>Centre: RA 285.907827°, Dec +40.941988° (ICRS), constellation Lyra. All images are registered to Gaia DR3 (Pan-STARRS offset under 0.1″, see <a href="{V}post/source_images/registration.json">registration.json</a>). North is up and east is left. The orange ring is the candidate host; the blue dashed ring is KIC 5689116, a star about 2.1 times brighter in Gaia G that sits 7.1″ west.</p>
<div class="gallery">
{fig(img('docs/sky/ps1-2arcmin.jpg','Pan-STARRS 2 arcminute view',1000,1000),'<b>Pan-STARRS colour, 2′</b> (best view). <a href="'+PS1+'">Source render</a> · <a href="'+STSCI+'">STScI cutout page</a>')}
{fig(img('docs/sky/ps1-10arcmin.jpg','Pan-STARRS 10 arcminute view',1000,1000),'<b>Pan-STARRS colour, 10′</b> for context. <a href="'+PS1_10+'">Source render</a>')}
{fig(img('docs/sky/dss2-15arcmin.jpg','DSS2 15 arcminute view',1000,1000),'<b>DSS2 colour, 15′</b>: older photographic plates. <a href="'+DSS2+'">Source render</a>')}
{fig(img('docs/sky/2mass-10arcmin.jpg','2MASS near-infrared 10 arcminute view',1000,1000),'<b>2MASS near-infrared, 10′</b>: cool stars like the host brighten at these wavelengths. <a href="'+TMASS+'">Source render</a>')}
{fig(img('docs/sky/allwise-10arcmin.jpg','AllWISE infrared 10 arcminute view',1000,1000),'<b>AllWISE mid-infrared, 10′</b>: coarse resolution, the pair is blended. <a href="'+WISE+'">Source render</a>')}
{fig(img(V+'post/sky_images/post_00_real_sky_pair.jpg','Pan-STARRS field with a zoom panel',2380,1215),'<b>Field and zoom together</b>: a 10′ field with the 2′ view boxed. Registered to Gaia, host orange, neighbour blue dashed.',True)}
</div>
<p class="small">Pan-STARRS and DSS2 views use the cutouts saved in the validation pack; 2MASS and AllWISE were fetched fresh from the same CDS hips2fits service on 11 October (parameters in <a href="docs/sky/SOURCES.json">docs/sky/SOURCES.json</a>). Interactive zoom from the whole sky down to the star: <a href="{ALADIN}">Aladin Lite</a>. Credits: Pan-STARRS1 Surveys (STScI), DSS2 (STScI/AURA, Palomar/UK Schmidt), 2MASS (UMass/IPAC-Caltech), AllWISE (NASA/JPL-Caltech/UCLA), CDS Strasbourg.</p>

<h3 class="sub">What Kepler actually sees: a few big pixels</h3>
<p>Kepler pixels are 4″ wide, so the target and its neighbour fall on the same handful of pixels. The right panel overlays the pixels that lost light during transit on the Pan-STARRS image; the strongest (14σ and 12σ) sit on the host.</p>
{fig(img(V+'post/sky_images/post_06_kepler_pixels_pair.jpg','Kepler pixels at true footprint beside the pixels that lost light in transit overlaid on Pan-STARRS',2380,1215),'Left: Kepler pixels at true sky footprint (average brightness). Right: pixels that lost light during transit, with their significance, over Pan-STARRS.',True)}
<div class="figures">
{fig(img(V+'post/charts/post_05_three_views.png','Same patch in DSS2, Pan-STARRS, Kepler pixels and missing-light map'),'The same 34″ patch four ways: DSS2, Pan-STARRS, Kepler pixels, missing-light map.')}
{fig(img(V+'post/charts/post_01_where.png','Lyra locator, Gaia finder chart, Kepler stamp and difference image'),'Where it is: Lyra locator, Gaia finder chart, Kepler stamp and difference image.')}
{fig(svg('kepler-diffimage',''),'Missing light per Kepler pixel in four seasons. In seasons 0-2 the peak falls on the candidate pixel. Data: <a href="'+V+'post/data/kic5689121_diffimage_season0_snr.csv">CSV per season</a>.')}
{fig(svg('gaia-field',''),'All 114 Gaia DR3 stars within 2′. Within 30″ there are only the neighbour and a handful of faint stars, each tested. Data: <a href="'+V+'post/data/kic5689121_gaia_neighbours_120arcsec.csv">CSV</a>.')}
</div></section>

<section class="section" id="kepler"><div class="eyebrow">KIC 5689121 · Kepler Bonus PSF photometry</div><h2>The signal</h2>
<p>Kepler watched this field for four years. The target is too faint to have been a planet-search target, so its light comes from the Kepler Bonus background-star photometry. Folding the light curve at 13.769448 days stacks 70 transits into one clear dip.</p>
<div class="figures">
{fig(svg('kepler-fold',''),'All usable transits folded at P = 13.769448 ± 0.000065 d, 15-minute bins, with the MCMC transit model. Data: <a href="'+V+'post/data/kic5689121_folded_15min_bins.csv">bins</a>, <a href="'+V+'post/data/kic5689121_transit_model.csv">model</a>.')}
{fig(svg('kepler-event-depths',''),'Depth of each event (74 measured, 70 pass the stricter cut). Blue: discovery quarters. Yellow: quarters reserved before the search. The held-out events sit on the same level. Data: <a href="'+V+'post/data/kic5689121_per_transit_depths.csv">CSV</a>.')}
</div>
<div class="metrics four">{metric('13.769448 d','period (full-baseline MCMC)')}{metric('1,830-2,430 ppm','depth, by method (PSF)')}{metric('2.1-2.4 h','duration')}{metric('5.8σ','in the last 4 held-out quarters')}</div>
<div class="figures">
{fig(img(V+'post/charts/post_03_folded_dip.png','Folded transit with model and key numbers'),'Presentation chart: all 70 transits folded, with the MCMC model.')}
{fig(img(V+'post/charts/post_02_lightcurve.png','Four years of Kepler photometry with predicted transits and six single transits'),'Four years of photometry with predicted transits marked, and six single transits. Full light curve: <a href="'+V+'post/data/kic5689121_lightcurve_psf.csv">CSV</a>.')}
</div>
<details><summary>How depth depends on the method</summary><p>The PSF depth is 1,830-2,430 ppm across box widths and baseline windows in the independent check (1,958 ± 46 ppm for a plain 2.2 h box). Against measured event-to-event and random-phase scatter that is 11-22σ; the formal error gives about 43σ and should not be quoted. The aperture (SAP) depth is shallower, 1,438 ± 105 ppm, because the aperture holds neighbour light. The original report quoted 2,165 ± 98 ppm raw PSF depth.</p></details>
</section>

<section class="section" id="vetting"><div class="eyebrow">Is it real, and is it on this star?</div><h2>Eight checks: six passed, two stay open</h2>
<div class="scoreboard">
<div class="test pass"><b>Repeats on schedule</b><p>70 transits in 13 quarters. The last four quarters, held out of the search, still show it at 5.8σ.</p></div>
<div class="test pass"><b>Not Kepler-169 e</b><p>That planet has P = 13.767 d, 4.4′ away. No transit ever overlaps (closest 67 h); periods differ by 32σ; the target shows no dip at any of five Kepler-169 ephemerides.</p></div>
<div class="test pass"><b>On this star</b><p>Raw-pixel centroids reject the bright neighbour at Δχ² = 934 and every other Gaia star within 30″ at 4,300 or more.</p></div>
<div class="test pass"><b>Not the bright neighbour</b><p>KIC 5689116's own light curve shows 24 ± 41 ppm at the candidate times. It would need about 1,100 ppm to host the dip.</p></div>
<div class="test pass"><b>Dilution fits</b><p>Per-quarter aperture depths track the target's share of aperture light (p = 0.22). A signal on the contaminating light is rejected (p about 1e-36).</p></div>
<div class="test pass"><b>No eclipsing-binary signs</b><p>Odd and even depths agree (0.6σ). No secondary eclipse (17 ± 59 ppm). The shape fits the star's density.</p></div>
<div class="test open"><b>Not unique by detection strength</b><p>About 2 of 1,736 inverted null searches score as high. The case rests on the vetting, not on how loud the dip is.</p></div>
<div class="test open"><b>Hidden companion</b><p>A planet around an unresolved bound companion (STP about 0.07) is still allowed. Imaging and a RUWE-based limit are needed.</p></div>
</div>
<div class="figures">
{fig(svg('kepler-ephemeris-null',''),'Depth measured at the candidate ephemeris and at each Kepler-169 planet ephemeris. Only the candidate ephemeris shows a dip. The neighbour (green) shows none. Data: <code>results/kepler/kdepth.json</code>.')}
{fig(svg('kepler-centroid',''),'A raw target-pixel centroid test using only stamp geometry and Gaia positions. Lower Δχ² is a better match to where the missing light is. Data: <a href="'+V+'results/kepler/kcentroid_all_sources.csv">CSV</a>.')}
{fig(svg('kepler-dilution',''),'Aperture depth is shallow in quarters with the most neighbour light (7-pixel apertures: Q2, Q6, Q14), the opposite of what a signal on a contaminating star would do. Data: <a href="'+V+'results/kepler/kcrowd.json">kcrowd.json</a>.')}
{fig(img(V+'figures/kic5689121_dilution_centroid.png','Dilution and centroid figure from the validation pass'),'Original validation figure: dilution model (left) and centroid test (right).')}
</div>
<details><summary>The honest negative: null searches</summary><p>Ranked against all 1,736 matched inverted Kepler Bonus searches, two inverted stars pass the first screen at P &gt; 1.5 d with BLS SNR at least 26.7 and holdout SNR at least 15.5: KIC 8701308 (4.25 d) and KIC 5283912 (8.78 d). That is an empirical false-alarm rate near 1e-3 per star, so about two null-level signals are expected in a survey this size. Detection strength alone cannot single KIC 5689121 out. Script: <a href="{V}scripts/kepler/null_fap2.py">null_fap2.py</a>.</p></details>
<details><summary>A test that did not work</summary><p>The Kepler Bonus <code>CENTROID_COLUMN/ROW</code> series show no in-transit response at all (χ² 25.5/26 for zero), so they appear model-derived and were not used. Only the raw target-pixel centroid test is quoted.</p></details>
</section>

<section class="section" id="fpp"><div class="eyebrow">Statistical validation</div><h2>How likely is a false positive?</h2>
<p>TRICERATOPS (Giacalone et al. 2021) weighs planet and false-positive scenarios against the folded light curve, the star and the nearby field. We ran it offline with a field population built from the Gaia DR3 stars already in the evidence pack. A candidate is "statistically validated" when the false-positive probability is below 0.015. Neither lead is there.</p>
<div class="figures">
{fig(svg('fpp-runs',''),'Every run (1,000,000 draws each). Kepler candidate: 0.058, 0.089, 0.058, 0.069 (mean 0.069); with a G = 22.5 background 0.058 and 0.088. TESS lead: 0.556, 0.579, 0.568. The AO and speckle rows use <b>hypothetical</b> contrast curves for what-if only, not observations. Data: <a href="'+V+'results/triceratops/fpp_summary.json">fpp_summary.json</a>.')}
{fig(svg('fpp-scenarios',''),'What the false-positive probability is made of. The Kepler candidate is almost all "planet", and its remaining risk is a planet around a bound companion. The TESS lead is dominated by an eclipsing binary bound to the star (best fit: a 0.18 M☉ pair, grazing, diluted by the K dwarf).')}
</div>
<p>Why imaging cannot fully rescue either one: companions inside about 0.1″ (about 30 AU at 298 pc) stay allowed even after a typical AO contrast curve. Gaia RUWE 0.98 already disfavours some of them, but TRICERATOPS 1.1 does not use it. A MOLUSC companion file would. Resolved neighbours were not passed to TRICERATOPS (that needs a Kepler PRF model), so NFPP is reported as 0; those scenarios were excluded with the direct light-curve and centroid tests above instead.</p>
<p class="small">Run logs and per-run JSON: <a href="{V}results/triceratops/">results/triceratops/</a>. Driver code: <a href="{V}scripts/triceratops/">scripts/triceratops/</a>.</p>
</section>

<section class="section" id="planet"><div class="eyebrow">If it is a planet</div><h2>What it would be</h2>
<p>These numbers are modelled from the fitted orbit and the TIC star, and only apply if the dip is a planet on this star.</p>
<div class="facts wide">{fact('Host star','M dwarf, 0.51 R☉, 0.51 M☉, 3,630 K, Gaia G 16.3, about 298 pc')}{fact('Orbit','0.09 AU, 13.77 days')}{fact('Size','about 2.5 R⊕ (TIC radius) to 2.8 R⊕ (Gaia radius); fixed-density fits 3.0-3.1 R⊕')}{fact('Starlight','about 5 times Earth’s sunlight; its sun would look about 6 times wider than ours')}{fact('Identifiers','KIC 5689121 · TIC 120686465 · Gaia DR3 2103792461826460288')}{fact('Position','RA 19h 03m 37.9s, Dec +40° 56′ 31″ (Lyra)')}</div>
{fig(img(V+'post/charts/post_07_model.png','To-scale model of orbit, size and the star in its sky'),'To-scale model, not a photograph: orbit against Mercury, size against Earth and Neptune, and the host star as it would appear in the planet’s sky. Zero-albedo equilibrium temperature of about 420 K is a model. Data: <a href="'+V+'post/data/kic5689121_model_numbers.json">model_numbers.json</a>.')}
</section>

<section class="section" id="tess"><div class="eyebrow">TIC 309780779 · TESS</div><h2>The other lead: real signal, probably the wrong cause</h2>
<p>Host: K dwarf, 5,013 K, 0.685 R☉, 74.9 pc, TESS magnitude 10.03. Light curves are TESS-SPOC FFI products plus two QLP sectors, 92,860 cadences.</p>
<div class="figures">
{fig(svg('tess-fold',''),'Presentation fold at the saved ephemeris: a dip of about 400 ppm lasting about 1 hour. This is not an independent test. Data: <a href="analysis/309780779-display-bins.json">display bins</a>.')}
{fig(svg('tess-bls',''),'Blind period search on the real and inverted light curves, in the full data and in each half. The real signal shows up at 8.7236 d in each half; the inverted curve does not come close. Data: <code>results/tess/bls_full.json</code>, <code>bls_disc.json</code>.')}
{fig(svg('tess-depth-consistency',''),'Depth is consistent across odd/even transits (1.3σ), across three cadence eras, and in the held-out late sectors, where the ephemeris from sectors 1-38 predicts the transit 89 cycles later within 0.12σ (−0.95 min, prediction ±7.5 min). 22 of 22 late events are positive.')}
{fig(img(V+'figures/tic309780779_holdout_phase_scan.png','Holdout and all-phase secondary scan'),'Original validation figure: frozen-ephemeris holdout and an all-phase secondary-eclipse scan. Phase 0.5 depth is −20 ± 26 ppm; the largest off-transit dip in 377 phase trials is 3.2σ.')}
</div>
<div class="grid"><div><h3>What passes</h3><ul><li>Recovered blind in each half of the data (SDE 12.6 and 12.9 versus 7.8 best inverted).</li><li>Depth flat at 401 ± 30 ppm across eras, odd/even clean, no secondary.</li><li>No catalogue match within 5′ or at 1° harmonics.</li><li>Gaussian-PSF difference imaging is target-consistent in 16 of 16 sectors (old, approximate test).</li></ul></div>
<div><h3>Why it is weak</h3><ul><li>With a density prior: impact parameter b = 0.95 ± 0.015, Rp ≈ 2.05 R⊕, T14 = 1.07 h, 14% of the posterior grazing. Without it, 85% grazing and a large radius: the data cannot tell a small planet at high b from a larger grazing body.</li><li>TRICERATOPS FPP about 0.57, mostly a bound eclipsing binary (SEB about 0.42).</li><li>Not re-tested with the official TESS PRF (MAST was unreachable here).</li></ul></div></div>
<div class="note-strip">What would move it: two or three reconnaissance spectra (the star is T = 10) for a double-lined binary or a large velocity trend, and a multi-colour or CHEOPS transit for colour dependence. A 2 R⊕ planet would only produce about 2 m/s, so a true mass needs a precision spectrograph.</div>
</section>

<section class="section" id="search"><div class="eyebrow">What was searched, and the controls</div><h2>Searches and null controls</h2>
<p>A search is only worth something if it also finds nothing where nothing should be. Every Kepler search was paired with an inverted light curve of the same star, which cannot contain real transits.</p>
<div class="figures">
{fig(svg('null-control',''),'Real Kepler Bonus searches versus matched inverted nulls on the same stars: no excess in either stage (ranks 65-576 and 577-1800). Source tables: <a href="analysis/kbonus-extension-20261011/README.md">extension README</a>.')}
{fig(svg('coverage',''),'Stars per search on a shared scale. These are different kinds of count and are not added into one survey size.')}
</div>
<div class="grid"><div><h3>Rest of the Kepler run</h3><p>In ranks 577-1800 the strict-screen survivors are known false-positive neighbours (the KIC 4544570 field, KOI K06244.01) or deep 0.3-1% dips on G about 18.5 background stars, likely blends. Three real hits also appear inverted, so they are variability. Nothing approaches KIC 5689121. One faint 2.64 d signal (KIC 6629201) is unresolved and unlocalised.</p></div>
<div><h3>Earlier controls</h3><p>Codex reported 5 first-screen passes in 100 inverted TESS searches and none in 64 inverted Kepler searches. Known planets (LHS 3844 b, Kepler-138 c/d) were recovered as positive controls. These are diagnostics, not planet probabilities.</p></div></div>
<h3 class="sub">What failed</h3>
<div class="fails">
<div class="fail"><b>TIC 305054512</b><p>Missing light lands 37.3″ away at 54σ nominal; nearby sources fit better. Blend-like, rejected as on-target.</p></div>
<div class="fail"><b>KIC 10794841 (1.41 d)</b><p>Secondary dimming and weak aperture support. Not carried forward.</p></div>
<div class="fail"><b>Short-period hits (1.0-1.5 d)</b><p>Contact binaries every time. SDE of 9 or more alone lets noise through.</p></div>
<div class="fail"><b>TIC 358559650, 94753488</b><p>Persistent but broad or variable dimming with unresolved source; no defensible planet.</p></div>
</div></section>

<section class="section" id="verify"><div class="eyebrow">Checking the checkers</div><h2>Independent check and integrity</h2>
<p>A separate agent rewrote the key measurements from scratch without reading the main analysis code. Every claim passed, with caveats folded back into the text.</p>
<div class="table"><table><thead><tr><th>Claim</th><th>Verdict</th><th>Independent numbers</th></tr></thead><tbody>
<tr><td>Kepler depth 2,100-2,400 ppm at more than 15σ</td><td>Pass, with caveat</td><td>1,958 ± 46 ppm plain 2.2 h box; 1,830-2,430 ppm across methods; 11-22σ against measured scatter (43σ formal)</td></tr>
<tr><td>No overlap with Kepler-169 e</td><td>Pass</td><td>Closest 67.3 h; fold on that ephemeris 80 ± 39 / 14 ± 45 ppm</td></tr>
<tr><td>2 of 1,736 inverted nulls as strong</td><td>Pass</td><td>KIC 8701308 (4.254 d) and KIC 5283912 (8.785 d)</td></tr>
<tr><td>TESS late half on frozen ephemeris</td><td>Pass</td><td>Offset +4 min (−12 to +11); late depth 382-444 ppm at 9-10σ</td></tr>
<tr><td>TESS phase-0.5 depth near 0</td><td>Pass</td><td>−44 ± 30 ppm; sectors 61+ alone −94 ± 44 ppm (a 2σ brightening, not an eclipse)</td></tr></tbody></table></div>
<ul><li>Release archives were downloaded and their SHA-256 hashes match <a href="analysis/full-archive-review.md">the archive review</a>.</li><li>Sky images are registered to Gaia DR3 positions; median offset under 0.1″ for Pan-STARRS.</li><li>Every file in this repository has a hash in <a href="SHA256SUMS">SHA256SUMS</a> and <a href="inventory.json">inventory.json</a>.</li></ul>
<p><a href="{V}independent_check/README.md">Independent check</a> · <a href="{V}SCIENCE.md">Full science write-up</a> · <a href="{V}TASKS.md">All 24 tasks</a></p></section>

<section class="section" id="next"><div class="eyebrow">What would change the answer</div><h2>Blocked, and what comes next</h2>
<div class="grid"><div class="card"><span class="tag good">KIC 5689121</span><ol><li>Adaptive-optics imaging (Keck/NIRC2 or similar; Kp 16.3, K 12.97).</li><li>A companion limit using RUWE 0.98 (MOLUSC), then rerun TRICERATOPS with both.</li><li>A multi-band transit: a planet around a companion predicts colour-dependent depth.</li></ol><p class="small">Realistic endpoint: statistically validated, if imaging and RUWE squeeze the companion scenario below about 1%. A radial-velocity mass is not realistic for this faint star.</p></div>
<div class="card"><span class="tag bad">TIC 309780779</span><ol><li>Two or three reconnaissance spectra for an SB2 or velocity trend.</li><li>Official-PRF pixel test via TESScut.</li><li>Multi-colour or space-based transit for chromaticity and shape.</li></ol><p class="small">Until then it is a candidate with a false-positive probability near 50%.</p></div></div>
<div class="note-strip"><b>Hard obstructions in this environment:</b> MAST, the Gaia archive, VizieR and ExoFOP were unreachable, so there was no live TOI/CTOI check, no official-PRF TESS redo and no Gaia RUWE for TIC 309780779. Telescope work (imaging, spectra, multi-band transits) was out of reach. Re-check TOI/CTOI and the literature on the day of any announcement.</div>
<h3 class="sub">How we got here</h3>
<ol class="timeline"><li><b>9 Oct</b> A TESS transit search over about 540 nearby K and M dwarfs begins, with a vetting ladder from odd/even through pixel localisation.</li><li><b>10 Oct</b> A parallel Kepler Bonus search finds KIC 5689121. Raw FITS rechecks reproduce its depth; the repo and this page go public.</li><li><b>11 Oct</b> The Kepler search extends to 1,672 more stars with null controls. A validation pass adds the Kepler-169, centroid, dilution, holdout and TRICERATOPS tests plus an independent check.</li></ol></section>

<h2 class="deep-h" id="deep">Deep dive: the original evidence, unchanged</h2>
<p class="small deep-intro">The sections below are the 10 October evidence pages, kept in full with their original figures. Where later work supersedes a sentence it is marked.</p>
{deep('tess', tess_old, 'TESS evidence: pixel localisation and original figures')}
{deep('kepler', kep_old, 'Kepler evidence: original report figures and aperture recheck')}
{deep('methods', leg('methods'), 'Methods, controls and the work behind the leads')}
{deep('extension', extension, 'Kepler extension: 1,672 more stars')}
<section class="section" id="explore">{explore}</section>

<section class="section" id="links"><div class="eyebrow">Everything linked</div><h2>Data, sources, tools and credits</h2>
<div class="linkcols">
<div><h3>This project</h3><ul><li>{a('https://github.com/Kuberwastaken/planethunt','Repository')}</li><li>{a('planethunt.md','planethunt.md: LLM entry point and file map')}</li><li>{a(V+'README.md','Validation pack README')} · {a(V+'SCIENCE.md','SCIENCE')} · {a(V+'TASKS.md','TASKS')} · {a(V+'LINKS.md','LINKS')}</li><li>{a('analysis/review.md','Scientific review')} · {a('analysis/full-archive-review.md','archive audit')}</li><li>{a('inventory.json','Inventory')} · {a('SHA256SUMS','SHA256SUMS')}</li></ul></div>
<div><h3>Release archives (evidence-20261010)</h3><ul><li>{a(REL+'planet-search-kepler-data.zip','planet-search-kepler-data.zip')}<br><small>SHA-256 4fd59efb…8640dd</small></li><li>{a(REL+'planet-search-tess-data.zip','planet-search-tess-data.zip')}<br><small>SHA-256 98a5dec4…bfac85</small></li><li>{a(REL+'planet-search-results.zip','planet-search-results.zip')}</li></ul></div>
<div><h3>Sky images (centre RA 285.907827, Dec +40.941988)</h3><ul><li>{a(PS1,'Pan-STARRS colour, 2′')} · {a(PS1_10,'10′')}</li><li>{a(STSCI,'STScI Pan-STARRS cutout page')}</li><li>{a(DSS2,'DSS2 colour, 15′')}</li><li>{a(TMASS,'2MASS colour, 10′')} · {a(WISE,'AllWISE colour, 10′')}</li><li>{a(ALADIN,'Aladin Lite interactive zoom')}</li></ul></div>
<div><h3>Datasets</h3><ul><li>{a('https://archive.stsci.edu/hlsp/kbonus-bkg','Kepler Bonus background photometry')} (DOI 10.17909/7jbr-w430)</li><li>{a('https://archive.stsci.edu/kepler/','Kepler target pixel files, MAST')}</li><li>{a('https://archive.stsci.edu/hlsp/qlp','TESS QLP, MAST')}</li><li>{a('https://gea.esac.esa.int/archive/','Gaia DR3')}</li><li>{a('https://exoplanetarchive.ipac.caltech.edu/','NASA Exoplanet Archive')}</li></ul></div>
<div><h3>Kepler-169</h3><ul><li>Rowe et al. 2014, ApJ 784, 45</li><li>{a('https://astro.keele.ac.uk/jkt/tepcat/planets/Kepler-169e.html','TEPCat: Kepler-169 e')}</li><li>{a('https://exoplanet.eu/catalog/kepler_169_e--2195/','exoplanet.eu: Kepler-169 e')}</li></ul></div>
<div><h3>Tools</h3><ul><li>{a('https://github.com/stevengiacalone/triceratops','TRICERATOPS')} (Giacalone et al. 2021)</li><li>batman, emcee, astropy, lightkurve</li><li>Site code: {a('scripts/site/','scripts/site/')}</li></ul></div>
</div>
<p class="small">Credits: NASA Kepler and TESS; Kepler Bonus (Martínez-Palomera et al.); Pan-STARRS1 Surveys and the PS1 archive (STScI); DSS2 (STScI/AURA, Palomar Observatory / UK Schmidt); 2MASS (UMass and IPAC/Caltech); AllWISE (NASA/JPL-Caltech/UCLA); Gaia DR3 (ESA/Gaia/DPAC); CDS Strasbourg hips2fits and Aladin. Attribution detail: <a href="SOURCES.md">SOURCES.md</a>.</p></section>

<section class="section" id="files">{files_sec}</section>
<footer>Planethunt / Kuber Mehta. Public archival research, updated 11 October 2026.<br>Research candidates remain unconfirmed. No candidate submission, naming or outreach is performed.</footer>
</main>{script}
<div class="lb" aria-modal="true" role="dialog" aria-label="Enlarged figure"><div class="bg"></div><div class="stage"></div><div class="cap"></div><button class="x press" type="button" aria-label="Close">×</button></div>
<script>{SITEJS}</script>
</body></html>'''
import re as _re
for cid,ct in SHEET_IDS.items():
    html = html.replace(f'<section class="section" id="{cid}">', f'<section class="section" id="{cid}" data-chap="{ct}">')
html = html.replace('<h2 class="deep-h" id="deep">', '<h2 class="deep-h" id="deep" data-chap="Deep dive">')
html = _re.sub(r'<figure class="(?!lensfig|meter)([^"]*)"', lambda m: f'<figure class="{m.group(1)} rv"', html)
html = html.replace('<article class="card', '<article class="rv card').replace('<div class="card', '<div class="rv card').replace('<div class="test ', '<div class="rv test ').replace('<div class="fail"', '<div class="rv fail"').replace('<div class="note-strip"', '<div class="rv note-strip"').replace('<div class="triptych">', '<div class="triptych rv">')
html = html.replace('<a href="#links">','<a href="#links">')
m = _re.search(r'(id="fpp"[^>]*><div class="eyebrow">Statistical validation</div><h2>How likely is a false positive\?</h2>)', html)
assert m
html = html.replace(m.group(1), m.group(1)+METER, 1)
for c in ('btn','directory'):
    pass
html = html.replace('class="btn"','class="btn press"').replace('<div class="directory">','<div class="directory">').replace('<meta name="theme-color" content="#0b1020">','<meta name="theme-color" content="#05070d">')
open('index.html', 'w').write(html)
print(len(html))
