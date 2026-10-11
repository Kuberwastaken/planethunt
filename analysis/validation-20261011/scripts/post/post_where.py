import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon
from astropy.wcs import WCS
from astropy.io import fits
import glob
exec(open('/root/ph/post/post_figs.py').read().split('# ------------------------------------------------------------------ data')[0])
d=json.load(open('/root/ph/post/diffimg.json')); S=d['seasons']['1']; G=d['gaia']
ra=np.array([g['ra'] for g in G]); de=np.array([g['dec'] for g in G]); gm=np.array([g['phot_g_mean_mag'] for g in G]); sep=np.array([g['sep'] for g in G])
it=np.argmin(sep); ib=np.argmin(np.where(sep<1,999,np.abs(sep-7.1)))
ra0,de0=ra[it],de[it]
f=[x for x in sorted(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')) if fits.getheader(x,0)['SEASON']==1][0]
w=WCS(fits.getheader(f,2))
fig=plt.figure(figsize=(14,8.2)); title(fig,'Where it is: a faint red dwarf in Lyra','RA 19h 03m 37.9s, Dec +40° 56′ 31″ (Gaia DR3 2103792461826460288 · KIC 5689121 · TIC 120686465)')
# --- panel 1: locator
a=fig.add_axes([0.045,0.12,0.27,0.68]); a.set_facecolor(SURF); a.grid(False)
st={'Vega':(279.2347,38.7837,0.03),'ε Lyr':(281.084,39.670,4.7),'ζ Lyr':(281.193,37.605,4.3),'δ² Lyr':(283.626,36.899,4.3),'Sheliak (β)':(282.520,33.363,3.5),'Sulafat (γ)':(284.736,32.690,3.3)}
for p,qq in (('Vega','ζ Lyr'),('Vega','ε Lyr'),('ζ Lyr','δ² Lyr'),('δ² Lyr','Sulafat (γ)'),('Sulafat (γ)','Sheliak (β)'),('Sheliak (β)','ζ Lyr')):
    a.plot([st[p][0],st[qq][0]],[st[p][1],st[qq][1]],color=INK3,lw=0.8)
for nm,(x,y,mg) in st.items():
    a.plot(x,y,'o',ms=max(3,13-2.2*mg),color=INK,mec=SURF,mew=1.5); a.text(x-0.25,y+0.2 if nm!='Sulafat (γ)' else y-0.6,nm,fontsize=9,color=INK2,ha='left')
a.plot(ra0,de0,'o',ms=14,mfc='none',mec=ORANGE,mew=2); a.plot(ra0,de0,'o',ms=3,color=ORANGE)
a.text(ra0-0.3,de0+0.35,'KIC 5689121\n(G 16.3: invisible\nto the naked eye)',fontsize=9.5,color=ORANGE,ha='left')
a.set_xlim(288.2,277.6); a.set_ylim(31.5,42.6); a.set_aspect(1/np.cos(np.radians(37)))
a.set_xlabel('Right ascension (°)',fontsize=9); a.set_ylabel('Declination (°)',fontsize=9); a.tick_params(labelsize=8)
a.set_title('Constellation Lyra (approx. bright-star positions)',fontsize=10.5,color=INK2,loc='left')
# --- panel 2: Gaia finder chart (60" box), Kepler stamp footprint
a=fig.add_axes([0.36,0.12,0.27,0.68]); a.set_facecolor(SURF); a.grid(False)
x=(ra-ra0)*np.cos(np.radians(de0))*3600; y=(de-de0)*3600
m=(np.abs(x)<35)&(np.abs(y)<35)
a.scatter(x[m],y[m],s=np.clip(10**(0.32*(21.5-gm[m])),4,600),color=INK,edgecolors='none',zorder=2)
ny,nx=np.array(S['median_image']).shape
cor=np.array([[-0.5,-0.5],[nx-0.5,-0.5],[nx-0.5,ny-0.5],[-0.5,ny-0.5]]); sk=w.pixel_to_world(cor[:,0],cor[:,1])
px=(sk.ra.deg-ra0)*np.cos(np.radians(de0))*3600; py=(sk.dec.deg-de0)*3600
a.add_patch(Polygon(np.c_[px,py],closed=True,fill=False,ec=BLUE,lw=1.6,ls='--',zorder=3))
a.text(px.max()+0.5,py.min()-3.5,'Kepler pixel stamp (5×5 px, 4″ each)',fontsize=9,color=BLUE)
a.plot(0,0,'o',ms=22,mfc='none',mec=ORANGE,mew=2,zorder=4); a.text(-3,-6.5,'Candidate host\nG 16.3, M dwarf',fontsize=9,color=ORANGE,ha='left')
a.annotate('KIC 5689116\nG 15.5, 7.1″ away\n(the Kepler target whose\npixels contain both stars)',xy=(x[ib],y[ib]),xytext=(x[ib]+3,y[ib]+12),fontsize=9,color=INK2,arrowprops=dict(arrowstyle='-',color=INK3))
a.set_xlim(32,-32); a.set_ylim(-32,32); a.set_aspect('equal'); a.set_xlabel('East ← offset (″)',fontsize=9); a.set_ylabel('North offset (″)',fontsize=9); a.tick_params(labelsize=8)
a.set_title('Gaia DR3 stars within 30″ (dot size ∝ brightness)',fontsize=10.5,color=INK2,loc='left')
# --- panels 3/4: Kepler pixels and difference image
med=np.array(S['median_image'],dtype=float); dif=np.array(S['diff'],dtype=float); dife=np.array(S['diff_err'],dtype=float)
gx,gy=np.array(S['gaia_xy']).T; tx,ty=S['target_xy']; inb=(gx>-0.6)&(gx<nx-0.4)&(gy>-0.6)&(gy<ny-0.4)
gray=LinearSegmentedColormap.from_list('g',[SURF,'#6b6a64',INK]); blue=LinearSegmentedColormap.from_list('b',[SURF,'#184f95','#3987e5','#cde2fb'])
for j,(img,cm,lab,ttl) in enumerate(((np.log10(np.clip(med,1,None)),gray,'log flux','Kepler pixels (median, Q3/7/11/15)'),
                                      (dif/dife,blue,'missing light (σ)','Light lost during transit')) ):
    a=fig.add_axes([0.665,0.47-j*0.37,0.16,0.31]); a.grid(False)
    im=a.imshow(np.ma.masked_invalid(img),origin='lower',cmap=cm,interpolation='nearest')
    a.plot(gx[inb],gy[inb],'+',color=INK3,ms=7,mew=1)
    a.plot(tx,ty,'o',ms=14,mfc='none',mec=ORANGE,mew=2)
    bx,by=gx[ib],gy[ib]; a.plot(bx,by,'s',ms=13,mfc='none',mec=SURF,mew=3.2); a.plot(bx,by,'s',ms=13,mfc='none',mec=BLUE,mew=1.8)
    a.set_xticks([]); a.set_yticks([]); a.set_title(ttl,fontsize=10,color=INK2,loc='left')
    cb=fig.colorbar(im,ax=a,fraction=0.05,pad=0.03); cb.set_label(lab,color=INK2,fontsize=9); cb.ax.tick_params(colors=INK3,labelsize=8); cb.outline.set_edgecolor(INK3)
fig.text(0.885,0.74,'○  candidate host',fontsize=10,color=ORANGE); fig.text(0.885,0.705,'□  KIC 5689116',fontsize=10,color=BLUE); fig.text(0.885,0.67,'+  Gaia star positions',fontsize=10,color=INK3)
fig.text(0.885,0.43,'The pixel that loses\nlight during transit\nsits on the faint\ncandidate, not on\nthe brighter star\nnext to it.',fontsize=10,color=INK2,va='top')
fig.text(0.885,0.19,'Peak: %.1fσ\n%d transits stacked'%(np.nanmax(dif/dife),S['n_events']),fontsize=10.5,color=INK,va='top')
foot(fig,'Gaia DR3 positions · Kepler target pixel files for KIC 5689116 · difference image = out-of-transit minus in-transit, stacked over one Kepler season · planet CANDIDATE')
fig.savefig(OUT+'post_01_where.png',dpi=150); plt.close(fig); print('ok', tx,ty,gx[ib],gy[ib])
