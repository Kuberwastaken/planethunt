"""Builds the SVG charts and sky images used by index.html from data saved in this repo.
Run from the repo root: python3 scripts/site/charts.py  (needs numpy-free stdlib + Pillow for images)."""
import csv, json, math, os
V = 'analysis/validation-20261011/'
D = V + 'post/data/'
OUT = 'docs/charts/'
os.makedirs(OUT, exist_ok=True)
BG, PANEL, LINE, TXT, MUT = '#080808', '#080808', '#303030', '#ffffff', '#aaaaaa'
OR, BL, GR, RD, YE = '#ffffff', '#aaaaaa', '#dddddd', '#888888', '#ffffff'
FONT = 'font-family="IBM Plex Mono,monospace"'

def rcsv(p): return list(csv.DictReader(open(p)))
def rjson(p): return json.load(open(p))

class Plot:
    def __init__(s, w=640, h=360, l=62, r=16, t=16, b=46, xr=(0, 1), yr=(0, 1), xlog=False):
        s.w, s.h, s.l, s.r, s.t, s.b, s.xr, s.yr, s.xlog = w, h, l, r, t, b, xr, yr, xlog
        s.o = []
    def X(s, v):
        a, b = s.xr
        if s.xlog: v, a, b = math.log10(max(v, 1e-9)), math.log10(a), math.log10(b)
        return s.l + (v - a) / (b - a) * (s.w - s.l - s.r)
    def Y(s, v):
        a, b = s.yr
        return s.h - s.b - (v - a) / (b - a) * (s.h - s.t - s.b)
    def add(s, x): s.o.append(x)
    def text(s, x, y, t, size=14, fill=MUT, anchor='start', weight='400', rot=None):
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ''
        s.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" {FONT}{tr}>{esc(t)}</text>')
    def line(s, x1, y1, x2, y2, c=LINE, w=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d}/>')
    def circ(s, x, y, r, fill, stroke='none', sw=1, op=1):
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>')
    def rect(s, x, y, w, h, fill, rx=2, op=1):
        s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{h:.1f}" fill="{fill}" rx="{rx}" opacity="{op}"/>')
    def yaxis(s, ticks, label, fmt=lambda v: f'{v:g}'):
        for v in ticks:
            y = s.Y(v); s.line(s.l, y, s.w - s.r, y, LINE if v else MUT, 1)
            s.text(s.l - 8, y + 5, fmt(v), 13, anchor='end')
        s.text(16, (s.t + s.h - s.b) / 2, label, 13, rot=-90, anchor='middle')
    def xaxis(s, ticks, label, fmt=lambda v: f'{v:g}', grid=False):
        for v in ticks:
            x = s.X(v)
            if grid: s.line(x, s.t, x, s.h - s.b, LINE, 1)
            s.text(x, s.h - s.b + 20, fmt(v), 13, anchor='middle')
        s.text((s.l + s.w - s.r) / 2, s.h - 8, label, 13, anchor='middle')
    def svg(s, title, desc):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" role="img" aria-labelledby="t d">'
                f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
                f'<rect width="{s.w}" height="{s.h}" fill="{BG}" rx="0"/>' + ''.join(s.o) + '</svg>')

def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def save(name, svg): open(OUT + name + '.svg', 'w').write(svg)

def ebar(p, x, y, e, c, lo=None, hi=None):
    y1, y2 = y - e, y + e
    if lo is not None: y1 = max(y1, lo)
    if hi is not None: y2 = min(y2, hi)
    p.line(p.X(x), p.Y(y1), p.X(x), p.Y(y2), c, 1.2)

def fold():
    b = rcsv(D + 'kic5689121_folded_15min_bins.csv'); m = rcsv(D + 'kic5689121_transit_model.csv')
    p = Plot(640, 380, xr=(-8.5, 8.5), yr=(-3300, 1100))
    p.yaxis([-3000, -2000, -1000, 0, 1000], 'Flux change (ppm)'); p.xaxis([-8, -4, 0, 4, 8], 'Hours from mid-transit', grid=True)
    for r in b:
        x, y, e = float(r['hours_from_mid']), float(r['flux_ppm']), float(r['err_ppm'])
        ebar(p, x, y, e, '#666666'); p.circ(p.X(x), p.Y(y), 3.4, BL)
    pts = ' '.join(f'{p.X(float(r["hours_from_mid"])):.1f},{p.Y(float(r["model_ppm"])):.1f}' for r in m[::4])
    p.add(f'<polyline points="{pts}" fill="none" stroke="{OR}" stroke-width="2.4"/>')
    p.text(p.l + 10, p.t + 20, 'Kepler PSF flux, saved full-series fold, 15-minute bins', 13, TXT)
    p.text(p.l + 10, p.t + 38, 'white line: MCMC transit model, depth about 2,400 ppm (0.24%)', 13, OR)
    save('kepler-fold', p.svg('KIC 5689121 folded transit', 'Folded Kepler photometry of KIC 5689121 with the fitted transit model, about 0.24 percent deep and 2.2 hours long.'))

def depths():
    r = rcsv(D + 'kic5689121_per_transit_depths.csv')
    p = Plot(640, 380, xr=(-50, 28), yr=(-2500, 8500))
    p.yaxis([0, 2000, 4000, 6000, 8000], 'Depth per event (ppm)', lambda v: f'{v:,.0f}')
    p.xaxis([-48, -36, -24, -12, 0, 12, 24], 'Transit number from epoch 0 (about 13.77 days each)', grid=False)
    p.rect(p.X(-50), p.Y(2400) - 1, p.X(28) - p.X(-50), 2, OR, 0, .7)
    for q in r:
        e = int(q['epoch']); d = float(q['depth_ppm']); s = float(q['err_ppm']); ho = q['held_out'] == 'True'
        c = YE if ho else BL
        ebar(p, e, d, s, c, -2500, 8500); p.circ(p.X(e), p.Y(d), 3.6, c)
    p.text(p.l + 10, p.t + 18, 'every measurable transit, one dot each', 13, TXT)
    p.circ(p.l + 14, p.t + 34, 4, BL); p.text(p.l + 24, p.t + 39, 'discovery events (51)', 13)
    p.circ(p.l + 178, p.t + 34, 4, YE); p.text(p.l + 188, p.t + 39, 'held-out quarters (23)', 13)
    p.line(p.l + 350, p.t + 34, p.l + 372, p.t + 34, OR, 2); p.text(p.l + 378, p.t + 39, 'fit depth', 13)
    save('kepler-event-depths', p.svg('Per-transit depths', 'Depth of each of 74 Kepler transit events with error bars, discovery and held-out quarters, scattered around the fitted depth.'))

def dilution():
    q = rjson(V + 'results/kepler/kcrowd.json')
    p = Plot(640, 400, l=62, xr=(0, len(q) + 1), yr=(-400, 4400))
    p.yaxis([0, 1000, 2000, 3000, 4000], 'Transit depth (ppm)', lambda v: f'{v:,.0f}')
    p.xaxis([], 'Kepler quarter')
    bw = (p.w - p.l - p.r) / (len(q) + 1)
    for i, r in enumerate(q):
        x = p.l + bw * (i + .5)
        for k, (key, c, off) in enumerate([('psf', BL, -7), ('sap', OR, 7)]):
            n, d, e = r[key]
            if n < 2: continue
            ye = min(d + e, 4400); ys = max(d - e, -400)
            p.line(x + off, p.Y(ye), x + off, p.Y(ys), c, 1.2); p.circ(x + off, p.Y(d), 3.6, c)
        p.text(x, p.h - p.b + 18, f"Q{r['q']}", 12, anchor='middle')
    p.circ(p.l + 14, p.t + 14, 4, BL); p.text(p.l + 24, p.t + 19, 'PSF / target', 13)
    p.circ(p.l + 230, p.t + 14, 4, OR); p.text(p.l + 240, p.t + 19, 'SAP / blended aperture', 13)
    save('kepler-dilution', p.svg('Depth per quarter, PSF versus SAP', 'Per quarter transit depth in PSF and aperture photometry; aperture depths are shallower in quarters where the aperture holds more contaminating light.'))

def ephem_null():
    d = rjson(V + 'results/kepler/kdepth.json')
    rows = [('Candidate ephemeris (13.769 d)', d['target_psf_at_candidate'], OR), ('Kepler-169 e (13.767 d)', d['target_psf_at_K169e'], BL),
            ('Kepler-169 c', d['target_psf_at_K169c'], BL), ('Kepler-169 b', d['target_psf_at_K169b'], BL),
            ('Kepler-169 d', d['target_psf_at_K169d'], BL), ('Kepler-169 f', d['target_psf_at_K169f'], BL),
            ('Neighbour KIC 5689116 at candidate ephemeris', d['neighbor5689116_psf_at_candidate'], GR)]
    p = Plot(640, 360, l=16, r=16, t=16, b=40, xr=(-500, 2700), yr=(0, 1))
    for v in [0, 1000, 2000]:
        x = p.X(v); p.line(x, p.t, x, p.h - p.b, LINE if v else MUT)
        p.text(x, p.h - p.b + 18, f'{v:,}', 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 6, 'Box depth in the target PSF light curve (ppm); neighbour row is its own light curve', 12, anchor='middle')
    rh = (p.h - p.t - p.b) / len(rows)
    for i, (lab, (n, dp, e), c) in enumerate(rows):
        y = p.t + rh * (i + .5) + 8
        p.text(p.l, y - 14, f'{lab}  (n={n})', 13, TXT)
        p.line(p.X(dp - e), y, p.X(dp + e), y, c, 2); p.circ(p.X(dp), y, 5, c)
        p.text(p.X(dp - e) - 8 if dp > 1500 else p.X(dp + e) + 8, y + 5, f'{dp:,.0f} ± {e:,.0f}', 12, MUT, 'end' if dp > 1500 else 'start')
    save('kepler-ephemeris-null', p.svg('Depth at candidate and Kepler-169 ephemerides', 'The target shows a 2,350 ppm dip at the candidate ephemeris and no depth at any of the five Kepler-169 planet ephemerides or in the neighbour light curve.'))

def centroid():
    rows = list(csv.DictReader(open(V + 'results/kepler/kcentroid_all_sources.csv')))
    rows = rows[1:]
    p = Plot(640, 330, l=16, r=24, t=16, b=44, xr=(100, 30000), yr=(0, 1), xlog=True)
    for v in [100, 1000, 10000]:
        x = p.X(v); p.line(x, p.t, x, p.h - p.b, LINE); p.text(x, p.h - p.b + 18, f'{v:,}', 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 6, 'Δχ² of centroid fit versus the target (log scale, higher = worse fit)', 12, anchor='middle')
    rh = (p.h - p.t - p.b) / len(rows)
    for i, r in enumerate(rows):
        y = p.t + rh * i + 4; dc = float(r['dchi2_vs_target']); nb = i == 0
        p.rect(p.l, y + 10, p.X(max(dc, 100)) - p.l, rh - 14, GR if nb else BL, 3, .85)
        p.text(p.l + 6, y + 8, f"Gaia {r['source_id'][-6:]} · {float(r['sep']):.1f}\" · G {float(r['phot_g_mean_mag']):.1f}" + ('  (the bright neighbour)' if nb else ''), 12, TXT)
        p.text(p.X(max(dc, 100)) + 5, y + rh - 5, f'{dc:,.0f}', 12, MUT)
    save('kepler-centroid', p.svg('Raw-pixel centroid test', 'Every Gaia source within 30 arcseconds is rejected relative to the target by at least 934 in chi-square; the bright neighbour is the least bad at 934.'))

def gaia_map():
    r = rcsv(D + 'kic5689121_gaia_neighbours_120arcsec.csv')
    ra0, de0 = 285.907827, 40.941988
    p = Plot(520, 520, l=20, r=20, t=20, b=24, xr=(130, -130), yr=(-130, 130))
    for rad in (30, 60, 120):
        cx, cy = p.X(0), p.Y(0); rr = abs(p.X(rad) - cx)
        p.add(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{LINE}" stroke-dasharray="4 4"/>')
        p.text(cx + 4, cy - rr + 14, f'{rad}"', 12)
    for q in r:
        dx = (float(q['ra']) - ra0) * math.cos(math.radians(de0)) * 3600; dy = (float(q['dec']) - de0) * 3600
        g = float(q['phot_g_mean_mag']); rad = max(1.8, 7 - 0.42 * (g - 14))
        nb = abs(float(q['sep']) - 7.1) < .3
        p.circ(p.X(dx), p.Y(dy), rad, GR if nb else '#888888', op=.85)
    p.circ(p.X(0), p.Y(0), 7.5, 'none', OR, 2.5)
    p.text(p.X(0) + 12, p.Y(0) - 10, 'KIC 5689121', 13, OR, weight='600')
    p.text(p.X(-7.1) + 4, p.Y(0) + 24, 'KIC 5689116 (7.1")', 12, GR)
    p.text(p.w - 22, p.h - 6, 'North up, east left · dot size = brightness', 12, anchor='end')
    p.text(24, 18, '114 Gaia DR3 stars within 120"', 13, TXT)
    save('gaia-field', p.svg('Gaia stars around KIC 5689121', 'Map of 114 Gaia DR3 sources within 2 arcminutes of the candidate, the brighter neighbour 7.1 arcseconds west marked.'))

def fpp():
    S = rjson(V + 'results/triceratops/fpp_summary.json')
    p = Plot(640, 360, l=20, r=60, t=18, b=44, xr=(0, 0.7), yr=(0, 1))
    for v in [0, .1, .2, .3, .4, .5, .6, .7]:
        x = p.X(v); p.line(x, p.t + 20, x, p.h - p.b, LINE); p.text(x, p.h - p.b + 18, f'{v:.1f}', 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 6, 'False-positive probability (TRICERATOPS). Each dot is one run of 1,000,000 draws', 12, anchor='middle')
    x = p.X(.015); p.line(x, p.t + 10, x, p.h - p.b, GR, 2); p.text(x + 6, p.t + 18, 'validation threshold 0.015', 12, GR)
    rows = [('KIC 5689121, observed data', 'kepler G21', OR), ('KIC 5689121, with a hypothetical AO curve', 'kepler G21+hypoAO', '#bbbbbb'),
            ('TIC 309780779, observed data', 'tess', RD), ('TIC 309780779, with a hypothetical speckle curve', 'tess+hypoSpeckle', '#888888')]
    rh = (p.h - p.t - p.b - 44) / 4
    for i, (lab, k, c) in enumerate(rows):
        y = p.t + 52 + rh * i + 16
        p.text(p.l, y - 14, lab, 13, TXT)
        for v in S[k]['FPP']: p.circ(p.X(v), y + 4, 5, c, op=.8)
        m = S[k]['FPP_mean']; p.line(p.X(m), y - 6, p.X(m), y + 14, TXT, 2)
        p.text(p.X(max(S[k]['FPP'])) + 12, y + 9, f'mean {m:.3f}', 12, MUT)
    save('fpp-runs', p.svg('TRICERATOPS false-positive probabilities', 'KIC 5689121 has a false positive probability of about 0.07 and TIC 309780779 about 0.57; validation requires below 0.015.'))

def scenarios():
    S = rjson(V + 'results/triceratops/fpp_summary.json')
    def agg(mp, keys): return sum(mp.get(k, 0) for k in keys)
    cats = [('Planet on target (TP / PTP / DTP)', ['TP', 'PTP', 'DTP'], GR), ('Planet on a bound companion (STP)', ['STP'], YE), ('Planet on background star (BTP)', ['BTP'], BL),
            ('Eclipsing binary bound to target (SEB)', ['SEB', 'SEBx2P'], RD), ('Other binary scenarios', ['EB', 'EBx2P', 'PEB', 'PEBx2P', 'DEB', 'DEBx2P', 'BEB', 'BEBx2P'], '#555555')]
    p = Plot(640, 330, l=20, r=20, t=18, b=20, xr=(0, 1), yr=(0, 1))
    for j, (lab, k) in enumerate([('KIC 5689121 (Kepler)', 'kepler G21'), ('TIC 309780779 (TESS)', 'tess')]):
        mp = S[k]['mean_probs']; y = 24 + j * 62; x = p.l
        p.text(p.l, y, lab, 14, TXT, weight='600')
        tot = sum(mp.values())
        for cl, keys, c in cats:
            v = agg(mp, keys) / tot; w = v * (p.w - p.l - p.r)
            p.rect(x, y + 8, w, 26, c, 0)
            if v > .06: p.text(x + w / 2, y + 26, f'{v*100:.0f}%', 13, '#080808', 'middle', '700')
            x += w
    y = 170
    for cl, keys, c in cats:
        p.rect(p.l, y - 11, 13, 13, c, 2); p.text(p.l + 22, y, cl, 13); y += 24
    p.text(p.l, p.h - 22, 'Share of total scenario probability (mean of runs).', 12)
    p.text(p.l, p.h - 6, 'FPP excludes the planet-on-target scenarios (TP, PTP and DTP).', 12)
    save('fpp-scenarios', p.svg('Scenario probabilities', 'For the Kepler candidate most probability is a planet on target; the remaining mass is mostly a planet around an unseen bound companion. For the TESS lead the largest block is an eclipsing binary.'))

def tess_fold():
    d = rjson('analysis/309780779-display-bins.json')['bins']
    p = Plot(640, 360, xr=(-3.1, 3.1), yr=(-800, 500))
    p.yaxis([-600, -400, -200, 0, 200, 400], 'Flux change (ppm)'); p.xaxis([-3, -2, -1, 0, 1, 2, 3], 'Hours from mid-transit', grid=True)
    for r in d:
        x, y, e = r['hours'], r['flux_ppm'], r['standard_error_ppm']
        ebar(p, x, y, e, '#666666'); p.circ(p.X(x), p.Y(y), 3.4, BL)
    p.text(p.l + 10, p.t + 20, 'TESS, P = 8.72361 d, presentation fold of 46 events', 13, TXT)
    p.text(p.l + 10, p.t + 38, 'dip is shallow (about 400 ppm) and short (about 1 h)', 13, OR)
    save('tess-fold', p.svg('TIC 309780779 folded dip', 'Folded TESS photometry of TIC 309780779 showing a shallow dip of about 400 parts per million.'))

def tess_depths():
    rows = [('All 46 events', 401, 30, OR), ('Odd transits (25)', 365, 41, BL), ('Even transits (21)', 444, 42, BL),
            ('Sectors 1-11, 30-min data', 367, 67, GR), ('Sectors 28-38, 10-min data', 423, 55, GR), ('Sectors 61-90, 200-s data', 408, 44, GR),
            ('Held out: sectors 61-90 at frozen ephemeris from 1-38', 450, 47, YE)]
    p = Plot(640, 380, l=16, r=24, t=14, b=40, xr=(150, 600), yr=(0, 1))
    for v in [200, 300, 400, 500, 600]:
        x = p.X(v); p.line(x, p.t, x, p.h - p.b, LINE); p.text(x, p.h - p.b + 18, str(v), 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 6, 'Transit depth (ppm, ±1σ)', 12, anchor='middle')
    rh = (p.h - p.t - p.b) / len(rows)
    for i, (lab, d, e, c) in enumerate(rows):
        y = p.t + rh * (i + .5) + 10
        p.text(p.l, y - 14, lab, 13, TXT)
        p.line(p.X(d - e), y, p.X(d + e), y, c, 2); p.circ(p.X(d), y, 5, c)
    save('tess-depth-consistency', p.svg('TIC 309780779 depth consistency', 'Odd and even depths agree within 1.3 sigma, three cadence eras agree, and the held-out late sectors show a 450 ppm dip at the frozen ephemeris.'))

def bls():
    rows = [('Full data', 19.6, 7.8), ('Sectors 1-38 only', 12.6, 6.0), ('Sectors 61-90 only', 12.9, None)]
    p = Plot(640, 280, l=20, r=20, t=16, b=40, xr=(0, 22), yr=(0, 1))
    for v in [0, 5, 10, 15, 20]:
        x = p.X(v); p.line(x, p.t, x, p.h - p.b, LINE); p.text(x, p.h - p.b + 18, str(v), 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 6, 'Peak strength (SDE): 8.7236 d signal versus inverted-data peak', 12, anchor='middle')
    rh = (p.h - p.t - p.b) / 3
    for i, (lab, a, b) in enumerate(rows):
        y = p.t + rh * i + 6
        p.text(p.l, y + 10, lab, 13, TXT)
        p.rect(p.l, y + 16, p.X(a) - p.l, 14, OR, 2); p.text(p.X(a) + 6, y + 28, f'{a} real', 12, MUT)
        if b: p.rect(p.l, y + 34, p.X(b) - p.l, 14, '#666666', 2); p.text(p.X(b) + 6, y + 46, f'{b} inverted', 12, MUT)
        else: p.text(p.l, y + 46, 'inverted peak not saved for this half', 12, MUT)
    save('tess-bls', p.svg('Blind period search, real versus inverted', 'The real TESS light curve gives a strong 8.72 day peak in the full data and in each half; the inverted light curve gives weaker peaks.'))

def nullc():
    rows = [('Kepler ranks 65-576', 10, 10), ('Kepler ranks 577-1800', 19, 22)]
    p = Plot(640, 220, l=20, r=20, t=14, b=34, xr=(0, 32), yr=(0, 1))
    for v in [0, 5, 10, 15, 20, 25]:
        x = p.X(v); p.line(x, p.t, x, p.h - p.b, LINE); p.text(x, p.h - p.b + 18, str(v), 13, anchor='middle')
    p.text((p.l + p.w) / 2, p.h - 4, 'First-screen signals found', 12, anchor='middle')
    rh = (p.h - p.t - p.b) / 2
    for i, (lab, a, b) in enumerate(rows):
        y = p.t + rh * i + 4
        p.text(p.l, y + 12, lab, 13, TXT)
        p.rect(p.l, y + 18, p.X(a) - p.l, 16, OR, 2); p.text(p.X(a) + 6, y + 31, f'{a} real', 12, MUT)
        p.rect(p.l, y + 38, p.X(b) - p.l, 16, '#666666', 2); p.text(p.X(b) + 6, y + 51, f'{b} inverted (null)', 12, MUT)
    save('null-control', p.svg('Real versus inverted searches', 'Real Kepler searches find no more first-screen signals than matched inverted null searches.'))

def model():
    mp = rjson(D + 'kic5689121_model_numbers.json')
    p = Plot(640, 300, l=0, r=0, t=0, b=0)
    cx, cy = 150, 150; sc = 120 / 0.39
    p.add(f'<circle cx="{cx}" cy="{cy}" r="{0.39*sc:.1f}" fill="none" stroke="{MUT}" stroke-dasharray="5 5"/>')
    p.add(f'<circle cx="{cx}" cy="{cy}" r="{mp["a_AU"]*sc:.1f}" fill="none" stroke="{OR}" stroke-width="2"/>')
    p.circ(cx, cy, 3.5, OR); p.circ(cx + mp['a_AU'] * sc * .7, cy - mp['a_AU'] * sc * .7, 4.5, OR)
    p.text(cx, 24, 'Mercury 0.39 AU · 88 d', 13, MUT, 'middle'); p.text(cx, 284, 'This orbit: 0.09 AU · 13.77 d', 13, OR, 'middle')
    p.text(cx, 14 + 4, '', 1)
    x0 = 330
    for lab, rr, c, dx in [('Earth', 1, BL, 0), ('This planet 2.5-3', 2.75, OR, 70), ('Neptune 3.9', 3.9, '#8fa8d6', 170)]:
        rad = rr * 10; p.circ(x0 + dx + 20, 150, rad, c)
        p.text(x0 + dx + 20, 200 + (0 if lab != 'Earth' else 0), lab if 'planet' not in lab else 'This planet', 13, TXT, 'middle')
        if 'planet' in lab: p.text(x0 + dx + 20, 218, '2.5-3 Earth radii', 12, OR, 'middle')
        if lab.startswith('Neptune'): p.text(x0 + dx + 20, 218, '3.9 Earth radii', 12, MUT, 'middle')
    p.text(330, 24, 'Size, if it is on the target star', 13, MUT)
    p.text(330, 262, f'About {mp["insolation_earth"]:.0f}× Earth\'s sunlight', 13, TXT)
    p.text(330, 282, f'T_eq about {mp["Teq_K_zero_albedo"]:.0f} K (model, zero albedo)', 13, TXT)
    save('model-orbit-size', p.svg('Modelled orbit and size', 'To-scale model: the orbit is much smaller than Mercury\'s, the planet is between two and three Earth radii and smaller than Neptune.'))

def diffimg():
    seas = [rcsv_nohdr(D + f'kic5689121_diffimage_season{i}_snr.csv') for i in range(4)]
    p = Plot(640, 230, l=0, r=0, t=0, b=0)
    cw = 28; x0 = 8
    for i, g in enumerate(seas):
        ox = x0 + i * 158
        p.text(ox, 20, f'Season {i}', 13, TXT, weight='600')
        for r_, row in enumerate(g):
            for c_, v in enumerate(row):
                t = max(0, min(1, v / 7)); col = lerp((24, 24, 24), (255, 255, 255), t) if v > 0 else ('#080808' if v < -8 else '#222222')
                p.rect(ox + c_ * cw, 30 + r_ * cw, cw - 2, cw - 2, col, 2)
                if v >= 2: p.text(ox + c_ * cw + cw / 2 - 1, 30 + r_ * cw + 18, f'{v:.0f}', 11, '#080808' if t > .45 else TXT, 'middle', '700')
    p.text(8, 200, 'Lost-light S/N per Kepler pixel. White ≥ 7; numbers give S/N.', 12)
    p.text(8, 220, 'Stored pixel orientation; see the registered sky overlay below.', 12)
    save('kepler-diffimage', p.svg('Missing-light pixels by season', 'Per-pixel signal to noise of the light lost during transit in four Kepler seasons, peaking on a few pixels.'))

def rcsv_nohdr(p): return [[float(x) if x.strip() else -9 for x in r] for r in csv.reader(open(p)) if r]
def lerp(a, b, t): return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def coverage():
    rows = [('Kepler Bonus: pilot + extension (matched null control)', 1736, OR), ('TESS extension, assigned targets', 540, BL), ('Upstream TESS results inherited (not redone)', 526, '#888888'), ('Codex TESS pilot', 175, GR)]
    p = Plot(640, 250, l=20, r=20, t=10, b=30, xr=(0, 1900), yr=(0, 1))
    rh = (p.h - p.t - p.b) / 4
    for i, (lab, n, c) in enumerate(rows):
        y = p.t + rh * i
        p.text(p.l, y + 14, lab, 13, TXT); p.rect(p.l, y + 22, p.X(n) - p.l, 16, c, 2); p.text(p.X(n) + 6, y + 35, f'{n:,}', 13, MUT)
    p.text(p.l, p.h - 6, 'Stars per search. Not a success-rate chart; counts of different kinds are not added together.', 11)
    save('coverage', p.svg('Search coverage', 'Number of stars in each search, on a shared scale.'))

def lyra_locator():
    # Approximate bright-star coordinates preserved from post_where.py, not new astrometry.
    stars = {'Vega': (279.2347,38.7837,.03), 'ε Lyr': (281.084,39.670,4.7),
             'ζ Lyr': (281.193,37.605,4.3), 'δ² Lyr': (283.626,36.899,4.3),
             'Sheliak': (282.520,33.363,3.5), 'Sulafat': (284.736,32.690,3.3)}
    p=Plot(640,480,l=60,r=24,t=24,b=56,xr=(288.2,277.6),yr=(31.5,42.6))
    p.xaxis([288,286,284,282,280,278], 'Right ascension (degrees, east to the left)')
    p.yaxis([32,34,36,38,40,42], 'Declination (degrees)')
    for a,b in [('Vega','ζ Lyr'),('Vega','ε Lyr'),('ζ Lyr','δ² Lyr'),('δ² Lyr','Sulafat'),('Sulafat','Sheliak'),('Sheliak','ζ Lyr')]:
        p.line(p.X(stars[a][0]),p.Y(stars[a][1]),p.X(stars[b][0]),p.Y(stars[b][1]),MUT)
    for name,(ra,dec,mag) in stars.items():
        p.circ(p.X(ra),p.Y(dec),max(3,8-mag),TXT)
        p.text(p.X(ra)+12,p.Y(dec)+5,name,14,TXT)
    p.circ(p.X(285.907827),p.Y(40.941988),10,'none',OR,2)
    p.text(p.X(285.907827)+18,p.Y(40.941988)-6,'KIC 5689121',16,OR)
    p.text(p.X(285.907827)+18,p.Y(40.941988)+15,'Too faint for the unaided eye',12)
    save('lyra-locator',p.svg('The candidate in constellation Lyra','Schematic sky locator using approximate bright-star coordinates. Vega and five other familiar Lyra stars orient the candidate; this is not a telescope image.'))

if __name__ == '__main__':
    for f in (fold, depths, dilution, ephem_null, centroid, gaia_map, fpp, scenarios, tess_fold, tess_depths, bls, nullc, diffimg, coverage, lyra_locator): f()
    print(sorted(os.listdir(OUT)))
