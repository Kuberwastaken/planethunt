"""Annotated sky views for the site. Inputs: survey cutouts saved in analysis/validation-20261011/post/source_images
(Pan-STARRS DR1 and DSS2 via CDS hips2fits, centred on RA 285.907827 Dec +40.941988) and fresh 2MASS / AllWISE
renders from the same service (fetched 2026-10-11, see docs/sky/SOURCES.json). North up, east left."""
import json, os
from PIL import Image, ImageDraw, ImageFont
SRC = 'analysis/validation-20261011/post/source_images/'
OUT = 'docs/sky/'
os.makedirs(OUT, exist_ok=True)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
Fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
OR, BL = (255, 138, 80), (108, 180, 255)

def dashed(d, cx, cy, r, col, w=3):
    for a in range(0, 360, 20): d.arc((cx - r, cy - r, cx + r, cy + r), a, a + 11, fill=col, width=w)

def make(name, src, arcsec_per_px, bar_arcsec, bar_label, label, ring_r_arcsec, neighbour=True):
    im = Image.open(src).convert('RGB'); n = im.size[0]; d = ImageDraw.Draw(im); c = n // 2
    r = ring_r_arcsec / arcsec_per_px
    d.ellipse((c - r, c - r, c + r, c + r), outline=OR, width=4)
    if neighbour:
        nx = c + 7.1 / arcsec_per_px  # 7.1" to the west = right of the target
        dashed(d, nx, c, r, BL, 4)
    L = bar_arcsec / arcsec_per_px; y = n - 60; x = 50
    d.line((x, y, x + L, y), fill='white', width=5); d.text((x, y - 36), bar_label, fill='white', font=F)
    d.text((n - 50, y - 36), 'N', fill='white', font=F, anchor='ra'); d.line((n - 62, y + 30, n - 62, y - 4), fill='white', width=4)
    d.text((n - 50, 24), label, fill='white', font=Fs, anchor='ra')
    d.text((50, 24), 'RA 285.907827  Dec +40.941988', fill='white', font=Fs)
    im = im.resize((1000, 1000), Image.LANCZOS)
    im.save(OUT + name + '.jpg', quality=86, optimize=True, progressive=True)

if __name__ == '__main__':
    make('ps1-2arcmin', SRC + 'ps1_2arcmin.png', 0.1, 20, '20"', 'Pan-STARRS DR1 colour (z, z+g, g) · 2\' wide', 4.5)
    make('ps1-10arcmin', SRC + 'ps1_10arcmin.png', 0.5, 60, '1\'', 'Pan-STARRS DR1 colour · 10\' wide', 9, True)
    make('dss2-15arcmin', SRC + 'dss2_15arcmin.png', 0.75, 120, '2\'', 'DSS2 colour · 15\' wide (photographic plates)', 12, True)
    make('2mass-10arcmin', '/tmp/f/tmass_10.png', 0.5, 60, '1\'', '2MASS J/H/K colour · 10\' wide', 9, True)
    make('allwise-10arcmin', '/tmp/f/wise_10.png', 0.5, 60, '1\'', 'AllWISE colour · 10\' wide', 9, True)
    # unannotated copy of the best image
    Image.open(SRC + 'ps1_2arcmin.png').convert('RGB').resize((1000, 1000), Image.LANCZOS).save(OUT + 'ps1-2arcmin-clean.jpg', quality=88, optimize=True, progressive=True)
    json.dump({'centre': {'ra_deg': 285.907827, 'dec_deg': 40.941988, 'frame': 'ICRS'}, 'orientation': 'north up, east left',
               'fetched': '2026-10-11', 'service': 'CDS hips2fits (alasky.cds.unistra.fr)',
               'images': {'ps1-2arcmin': 'CDS/P/PanSTARRS/DR1/color-z-zg-g, fov 0.0333 deg', 'ps1-10arcmin': 'same, fov 0.1667 deg',
                          'dss2-15arcmin': 'CDS/P/DSS2/color, fov 0.25 deg', '2mass-10arcmin': 'CDS/P/2MASS/color, fov 0.1667 deg', 'allwise-10arcmin': 'CDS/P/allWISE/color, fov 0.1667 deg'},
               'pan-starrs and dss2 inputs': 'analysis/validation-20261011/post/source_images/ (registered to Gaia DR3, offsets in registration.json)',
               'markers': 'orange ring = KIC 5689121, blue dashed ring = KIC 5689116 at 7.1 arcsec west (drawn at catalogue offset)'},
              open(OUT + 'SOURCES.json', 'w'), indent=1)
