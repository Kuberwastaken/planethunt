"""Render the self-contained three-page research report (requires reportlab)."""
from pathlib import Path
import json,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
P=Path(__file__).resolve().parent
OUT=P/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=595.28,841.89;M=42;CW=W-2*M
c=canvas.Canvas(str(OUT/'planet-search-report.pdf'),pagesize=(W,H));c.setTitle('KIC 5689121 - Archival planet candidate research report');c.setAuthor('Archival search prepared for Kuber')
navy=HexColor('#102B46');teal=HexColor('#087E8B');muted=HexColor('#526477');pale=HexColor('#EDF4F7')
def txt(s,x,y,size=10,bold=False,color=navy):
 c.setFillColor(color);c.setFont('DejaVuBold' if bold else 'DejaVu',size);c.drawString(x,y,s)
def para(s,y,size=9.2,leading=13,width=CW,color=navy):
 words=s.split();lines=[];line=''
 for w in words:
  test=(line+' '+w).strip()
  if pdfmetrics.stringWidth(test,'DejaVu',size)>width:lines.append(line);line=w
  else:line=test
 if line:lines.append(line)
 for line in lines:txt(line,M,y,size,color=color);y-=leading
 return y
def header(n,eyebrow,title):
 c.setFillColor(navy);c.rect(0,H-12,W,12,fill=1,stroke=0)
 txt(eyebrow.upper(),M,H-43,8.4,True,teal);txt(title,M,H-72,23,True)
 txt('10 October 2026  |  Public archival research  |  Unconfirmed candidate',M,25,7.5,color=muted)
 txt(f'{n} / 3',W-67,25,7.5,color=muted)
def table(rows,y,widths=(150,361),rowh=30):
 for i,row in enumerate(rows):
  if i%2==0:c.setFillColor(pale);c.rect(M,y-rowh+6,CW,rowh,fill=1,stroke=0)
  xx=M+10
  for j,s in enumerate(row):txt(str(s),xx,y-12,9,j==0);xx+=widths[j]
  y-=rowh
 return y

header(1,'Search breakthrough','A credible transit candidate')
y=H-101
y=para('KIC 5689121 / TIC 120686465 / Gaia DR3 2103792461826460288',y,10.2,15)
y=para('Potentially unreported. The evidence supports a planet candidate, not a confirmed or statistically validated planet. Nothing has been submitted, named, or published.',y-7,10,15)
y=table([('Period','13.7694 days (search ephemeris; uncertainty not estimated)'),('Transit duration','About 2.1-2.4 hours'),('Conditional size','About 3 Earth radii, if on-target and undiluted'),('Repeated events','70 usable local events; 22 in reserved quarters')],y-12,rowh=29)
img=P/'database_expansion/kbonus_independent_audit/2103792461826460288_shape.png'
c.drawImage(str(img),M,y-346,width=CW,height=341,preserveAspectRatio=True,anchor='c')
y-=368
y=para('The discovery-only shape predicts the timing and shape in four reserved quarters. Both PSF and aperture photometry show the dip. These are two extractions of the same observations, not two independent telescopes.',y,9,13)
y=para('Raw PSF local fit: 2165 +/- 98 ppm overall; 1929 +/- 159 ppm in reserved data. Corrected aperture uncertainties give local SNR 13.73 overall and 5.84 held out. These conditional scores are not global discovery probabilities.',y-7,9,13)
c.showPage()

header(2,'Source and novelty checks','The signal follows the target star')
y=H-105
y=para('Original Kepler pixel data favor the candidate over the brighter star 7.1 arcseconds away in all 13 observed quarters. Official Kepler PRF templates fit the difference images at the frozen 13.7694-day ephemeris.',y,10,15)
compact=P/'database_expansion/kbonus/pixels/localization_compact.png'
if compact.exists():c.drawImage(str(compact),M,y-173,width=CW,height=160,preserveAspectRatio=True,anchor='c');y-=183
y=para('Green marker: candidate. Orange marker: brighter aperture primary. The difference-image fits remain consistent with the candidate when the common positional correction is removed and a spatial background gradient is added. The primary star independently has no dip at this ephemeris.',y,9,13)
y=table([('Identity','KIC 5689121 = TIC 120686465 = Gaia ID above'),('Catalog star','Radius ~0.54-0.56 solar; Gaia RUWE 0.984; NSS flag 0'),('Kepler catalogs','No same-host KOI, TCE, confirmed planet, or EB match'),('TESS catalogs','No matching signal in the retrieved TOI/CTOI/RAVEN checks'),('Literature','Prior possible MELANGE-3 member; no transit report found'),('Nearby coincidences','Kepler-169 e: similar period, but 2.80 days out of phase')],y-18,rowh=29)
y=para('Novelty is provisional: catalog and indexed-search absence cannot establish that nobody has reported the signal. Exact aliases, nearby sources, published background-star candidates, and the association paper were checked. Full query results and source URLs are preserved in the research bundle.',y-15,9,13)
y=para('What remains unresolved',y-12,11,15)
y=para('An unresolved eclipsing companion or more distant blended source is not ruled out by these tests. PRF systematics and correlated noise are not fully calibrated. No formal false-positive probability, high-resolution imaging, reconnaissance spectroscopy, or new ground-based transit observation was obtained.',y-3,9.3,14)
y=para('Scientific next step: independent astronomer review, proper-motion-aware multi-source localization, formal blend validation, and targeted follow-up. A candidate designation or a planet name has not been assigned.',y-6,9.3,14)
c.showPage()

header(3,'Archives, method and reproducibility','A more promising search pool')
y=H-107
y=para('Kepler Bonus supplied this lead. Its long light curves include hundreds of thousands of background sources outside the original Kepler target list. Our catalog cuts left 1,800 background M dwarfs; the 64 brightest eligible stars were actually searched in this pilot.',y,10,15)
y=table([('Kepler Bonus','Implemented: 64-star pilot, 0.5-25 day periods'),('TESS SPOC / QLP','Implemented: 175 stars, two period bands'),('EVEREST / K2SFF','Identified: complementary K2 observations; not scanned'),('TGLC','Identified: Gaia-informed TESS extraction; not scanned'),('CDIPS / PATHOS','Identified: young/cluster stars; not scanned')],y-15,rowh=28)
y=para('Archive ranking is a scientific judgment, not a quantified probability of discovery. Cluster stars often have stronger variability; alternate TESS extractions reuse the same photons. More data are useful only when quality, contamination and prior searches are accounted for.',y-13,9.2,13)
y=para('Validation of the workflow',y-13,11,15)
y=para('Known controls recovered LHS 3844 b and Kepler-138 c/d, explicitly excluded from discovery claims. Synthetic tests checked transit recovery and holdout separation. The initial TESS screen yielded nine signals and five false-screen passes in 100 inverted runs, so screen scores alone were never treated as planets.',y-3,9.2,13)
y=para('The archive review found QLP timing errors in sectors 99-104 affecting 44 selected stars. All 88 affected two-band runs were repeated with those QLP products removed. Original results are retained as superseded evidence. Revised holdouts are retrospective; earlier conclusions were corrected.',y-6,9.2,13)
y=para('The Kepler pilot reserved the last 25% of usable quarters, rounded up, before searching. Its second initial survivor has secondary dimming and weak aperture support. None of 64 inverted controls passed the first screen. These counts do not provide a formal false-alarm probability.',y-6,9.2,13)
y=para('Reproduction and provenance',y-13,11,15)
y=para('The code/results archive includes pinned upstream commits, bootstrap.sh, package versions, catalog snapshots, per-file hashes, complete measurements, rejected hypotheses and the independent audit. The two data archives include normalized light curves and the candidate pixel/calibration data. Read README.md before rerunning.',y-3,9.2,13)
y=para('Primary references and data services',y-13,11,15)
for label,url in [('Kepler Bonus: Martinez-Palomera et al. (2023)','https://arxiv.org/abs/2310.17733'),('Kepler Bonus data (CC BY 4.0)','https://archive.stsci.edu/hlsp/kbonus-bkg'),('QLP documentation and timing warnings','https://archive.stsci.edu/hlsp/qlp'),('NASA Exoplanet Archive','https://exoplanetarchive.ipac.caltech.edu/'),('Gaia archive','https://gea.esac.esa.int/archive/')]:
 txt(label,M,y,8.1,True);y-=11;txt(url,M,y,7.8,color=teal);c.linkURL(url,(M,y-2,M+CW,y+9),relative=0);y-=17
c.save();print(OUT/'planet-search-report.pdf')
