import json, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
from PIL import Image
from astropy.io import fits
from astropy.wcs import WCS
exec(open('/root/ph/post/post_figs.py').read().split('# ------------------------------------------------------------------ data')[0])
OUT='/root/ph/post/out/'
ra0,de0=285.90782692874626,40.94198844296448
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
gx=(g.ra-ra0)*np.cos(np.radians(de0))*3600; gy=(g.dec-de0)*3600
ib=int(np.argmin(np.abs(np.hypot(gx,gy)-7.1))); nbx,nby=gx[ib],gy[ib]
def show(ax,fn,fov,N,lim=None):
    im=np.asarray(Image.open('/root/ph/sky/'+fn).convert('RGB')); sc=fov/N; h=fov/2
    ax.imshow(im,extent=[h,-h,-h,h],interpolation='lanczos')   # east (+x) on the left
    if lim: ax.set_xlim(lim[0],lim[1]); ax.set_ylim(lim[2],lim[3])
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values(): s.set_visible(False)
def kepler_pixels(season):
    f=[x for x in sorted(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')) if fits.getheader(x,0)['SEASON']==season][0]
    return WCS(fits.getheader(f,2))
def pix_polys(w,ny,nx):
    P={}
    for i in range(ny):
        for j in range(nx):
            c=np.array([[j-0.5,i-0.5],[j+0.5,i-0.5],[j+0.5,i+0.5],[j-0.5,i+0.5]]); sk=w.pixel_to_world(c[:,0],c[:,1])
            P[(i,j)]=np.c_[(sk.ra.deg-ra0)*np.cos(np.radians(de0))*3600,(sk.dec.deg-de0)*3600]
    return P
def compass(ax,x,y,L,col=INK):
    ax.annotate('',xy=(x,y+L),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color=col,lw=1.4)); ax.text(x,y+L*1.15,'N',color=col,ha='center',va='bottom',fontsize=10)
    ax.annotate('',xy=(x+L,y),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color=col,lw=1.4)); ax.text(x+L*1.18,y,'E',color=col,ha='right',va='center',fontsize=10)
def scalebar(ax,x,y,L,lab,col=INK):
    ax.plot([x,x-L],[y,y],color=col,lw=2.5,solid_capstyle='butt'); ax.text(x-L/2,y+L*0.12,lab,color=col,ha='center',va='bottom',fontsize=10)
# ======================= HERO: real sky
fig=plt.figure(figsize=(14,8.2)); title(fig,'The real star: KIC 5689121, photographed by Pan-STARRS','The orange dot at the centre is the faint red dwarf. The planet candidate is far too small and close to its star to see in any image.')
a=fig.add_axes([0.03,0.09,0.40,0.73]); show(a,'ps1_10arcmin.png',600,1200)
a.add_patch(Rectangle((-60,-60),120,120,fill=False,ec=ORANGE,lw=1.6))
a.annotate('zoom →',xy=(-60,30),xytext=(-150,190),color=ORANGE,fontsize=11,arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1))
scalebar(a,-200,-270,60,'1 arcminute'); compass(a,250,-280,40)
a.text(295,285,'10′ × 10′ field in Lyra',color=INK,fontsize=11,va='top')
b=fig.add_axes([0.445,0.09,0.40,0.73]); show(b,'ps1_2arcmin.png',120,1200)
b.add_patch(Circle((0,0),3.2,fill=False,ec=ORANGE,lw=2.2)); b.add_patch(Circle((nbx,nby),3.2,fill=False,ec=BLUE,lw=1.6,ls='--'))
b.annotate('Candidate host\nKIC 5689121\nM dwarf · G 16.3 · ~300 pc',xy=(-1.5,2.7),xytext=(14,30),color=ORANGE,fontsize=11,ha='center',arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1.2))
b.annotate('KIC 5689116\nbrighter, hotter star\n7.1″ west',xy=(nbx+1.5,nby-2.7),xytext=(nbx-12,-27),color=BLUE,fontsize=11,ha='center',arrowprops=dict(arrowstyle='-',color=BLUE,lw=1.2))
w=kepler_pixels(1); P=pix_polys(w,5,5)
one=P[(1,2)]
b.add_patch(Polygon(one,closed=True,fill=False,ec=INK,lw=1.5,ls=(0,(4,3))))
b.annotate('one Kepler pixel (4″):\nthe telescope that found\nthe dip saw both stars\nblurred together',xy=(one[:,0].mean(),one[:,1].min()),xytext=(52,-28),color=INK,fontsize=10,ha='left',va='center',arrowprops=dict(arrowstyle='-',color=INK2,lw=1))
scalebar(b,-40,-52,10,'10″'); compass(b,50,-54,7)
b.text(58,57,'2′ × 2′ zoom',color=INK,fontsize=11,va='top')
fig.text(0.865,0.70,'Position',fontsize=9,color=INK3,weight='bold'); fig.text(0.865,0.665,'RA 19h 03m 37.9s\nDec +40° 56′ 31″',fontsize=11,color=INK,va='top')
fig.text(0.865,0.56,'Signal',fontsize=9,color=INK3,weight='bold'); fig.text(0.865,0.525,'0.2% dip every\n13.77 days,\n~2 hours long',fontsize=11,color=INK,va='top')
fig.text(0.865,0.39,'Size if real',fontsize=9,color=INK3,weight='bold'); fig.text(0.865,0.355,'≈ 2.5–3 Earth radii',fontsize=11,color=INK,va='top')
fig.text(0.865,0.28,'Status',fontsize=9,color=INK3,weight='bold'); fig.text(0.865,0.245,'candidate,\nnot confirmed',fontsize=11,color=ORANGE,va='top')
fig.text(0.035,0.035,'Images: Pan-STARRS1 DR1 colour (via CDS hips2fits). Positions registered to Gaia DR3 (median offset < 0.1″).',fontsize=9,color=INK3)
foot(fig,'Kepler pixel outline from the KIC 5689116 target pixel file WCS (Q3/7/11/15) · planet CANDIDATE, not confirmed')
fig.savefig(OUT+'post_00_real_sky.png',dpi=150); plt.close(fig)
# ======================= THREE VIEWS of the same 34" patch
L=17; cx=nbx/2; lim=[cx+L,cx-L,-L,L]
D=json.load(open('/root/ph/post/diffimg.json'))['seasons']['1']
med=np.array(D['median_image'],dtype=float); snr=np.array(D['diff'],dtype=float)/np.array(D['diff_err'],dtype=float)
fig=plt.figure(figsize=(14,6.6)); title(fig,'Same patch of sky, three ways of seeing it','A 34″ square. Kepler found the dip; sharper surveys show which of the two stars is losing light.')
W=0.215; X0=[0.035,0.275,0.515,0.755]
panels=[('DSS2 photographic plates','dss2_15arcmin.png',900,1200),('Pan-STARRS (2010–2014)','ps1_2arcmin.png',120,1200)]
for k,(ttl,fn,fov,N) in enumerate(panels):
    a=fig.add_axes([X0[k],0.21,W,W*14/6.6]); show(a,fn,fov,N,lim); a.set_title(ttl,fontsize=11,color=INK2,loc='left')
    a.add_patch(Circle((0,0),2.6,fill=False,ec=ORANGE,lw=1.8)); a.add_patch(Circle((nbx,nby),2.6,fill=False,ec=BLUE,lw=1.4,ls='--'))
    if k==0: scalebar(a,lim[0]-2,-L+2.5,10,'10″')
# Kepler pixels as true sky polygons
a=fig.add_axes([X0[2],0.21,W,W*14/6.6]); a.set_facecolor('#000000'); a.set_xlim(lim[0],lim[1]); a.set_ylim(lim[2],lim[3]); a.set_xticks([]); a.set_yticks([]); a.grid(False)
for s in a.spines.values(): s.set_visible(False)
v=np.log10(np.clip(med,1,None)); lo,hi=np.nanpercentile(v,5),np.nanmax(v)
cmg=matplotlib.colormaps['gray']
for (i,j),poly in P.items():
    if np.isfinite(med[i,j]): a.add_patch(Polygon(poly,closed=True,fc=cmg((v[i,j]-lo)/(hi-lo)),ec='#000000',lw=0.6))
a.add_patch(Circle((0,0),2.6,fill=False,ec=ORANGE,lw=1.8)); a.add_patch(Circle((nbx,nby),2.6,fill=False,ec=BLUE,lw=1.4,ls='--'))
a.set_title('Kepler (2009–2013), 4″ pixels',fontsize=11,color=INK2,loc='left')
# Pan-STARRS + missing light overlay
a=fig.add_axes([X0[3],0.21,W,W*14/6.6]); show(a,'ps1_2arcmin.png',120,1200,lim); a.set_title('Where the light went missing',fontsize=11,color=INK2,loc='left')
cmb=matplotlib.colors.LinearSegmentedColormap.from_list('b',['#184f95','#3987e5','#cde2fb'])
for (i,j),poly in P.items():
    z=snr[i,j]
    if np.isfinite(z) and z>3: a.add_patch(Polygon(poly,closed=True,fc=cmb(min(1,(z-3)/11)),ec=INK,lw=0.8,alpha=0.55))
    if np.isfinite(z) and z>3: a.text(poly[:,0].mean(),poly[:,1].mean(),'%.0fσ'%z,color=INK,fontsize=9,ha='center',va='center',weight='bold')
a.add_patch(Circle((0,0),2.6,fill=False,ec=ORANGE,lw=1.8)); a.add_patch(Circle((nbx,nby),2.6,fill=False,ec=BLUE,lw=1.4,ls='--'))
fig.text(0.035,0.135,'○ candidate host KIC 5689121 (orange)      ◌ KIC 5689116, 7.1″ away (blue, dashed)',fontsize=10.5,color=INK2)
fig.text(0.755,0.15,'Kepler pixels that lost light during\ntransit (> 3σ), drawn on the real sky',fontsize=10,color=INK2,va='top')
fig.text(0.035,0.045,'Images: DSS2 (STScI/AURA, Palomar/UK Schmidt) and Pan-STARRS1 DR1 via CDS hips2fits. Kepler: KIC 5689116 target pixel files, season Q3/7/11/15, 25 transits stacked.',fontsize=9,color=INK3)
foot(fig,'All panels north up, east left, registered to Gaia DR3 · planet CANDIDATE, not confirmed')
fig.savefig(OUT+'post_05_three_views.png',dpi=150); plt.close(fig); print('ok')
