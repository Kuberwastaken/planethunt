import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
src=open('/root/ph/sky/sky_figs.py').read()
exec(src.split('# ======================= HERO: real sky')[0])
w=kepler_pixels(1); P=pix_polys(w,5,5)
L=17; cx=nbx/2; lim=[cx+L,cx-L,-L,L]
D=json.load(open('/root/ph/post/diffimg.json'))['seasons']['1']
med=np.array(D['median_image'],dtype=float); snr=np.array(D['diff'],dtype=float)/np.array(D['diff_err'],dtype=float)
v=np.log10(np.clip(med,1,None)); lo,hi=np.nanpercentile(v,5),np.nanmax(v); cmg=matplotlib.colormaps['gray']
cmb=matplotlib.colors.LinearSegmentedColormap.from_list('b',['#184f95','#3987e5','#cde2fb'])
def circles(a):
    a.add_patch(Circle((0,0),2.6,fill=False,ec=ORANGE,lw=2.4)); a.add_patch(Circle((nbx,nby),2.6,fill=False,ec=BLUE,lw=1.8,ls='--'))
def kepler(a):
    a.set_facecolor('#000000'); a.set_xlim(lim[0],lim[1]); a.set_ylim(lim[2],lim[3]); a.set_xticks([]); a.set_yticks([]); a.grid(False)
    for s in a.spines.values(): s.set_visible(False)
    for (i,j),poly in P.items():
        if np.isfinite(med[i,j]): a.add_patch(Polygon(poly,closed=True,fc=cmg((v[i,j]-lo)/(hi-lo)),ec='#000000',lw=0.8))
    circles(a); scalebar(a,cx-L+12,-L+2.5,10,'10″'); compass(a,cx+L-9,-L+3,4)
def missing(a):
    show(a,'ps1_2arcmin.png',120,1200,lim)
    for (i,j),poly in P.items():
        z=snr[i,j]
        if np.isfinite(z) and z>3:
            a.add_patch(Polygon(poly,closed=True,fc=cmb(min(1,(z-3)/11)),ec=INK,lw=1.0,alpha=0.55))
            a.text(poly[:,0].mean(),poly[:,1].mean(),'%.0fσ'%z,color=INK,fontsize=12,ha='center',va='center',weight='bold')
    circles(a); scalebar(a,cx-L+12,-L+2.5,10,'10″'); compass(a,cx+L-9,-L+3,4)
fig=plt.figure(figsize=(14,7.15)); fig.patch.set_facecolor(SURF)
a=fig.add_axes([0.015,0.03,0.475,0.94]); b=fig.add_axes([0.51,0.03,0.475,0.94]); kepler(a); missing(b)
fig.savefig(OUT+'post_06_kepler_pixels_pair.png',dpi=170); plt.close(fig)
fig=plt.figure(figsize=(7,14.4)); fig.patch.set_facecolor(SURF)
a=fig.add_axes([0.03,0.515,0.94,0.47]); b=fig.add_axes([0.03,0.015,0.94,0.47]); kepler(a); missing(b)
fig.savefig(OUT+'post_06_kepler_pixels_stack.png',dpi=170); plt.close(fig); print('ok')
