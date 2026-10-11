import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, ConnectionPatch
src=open('/root/ph/sky/sky_figs.py').read()
exec(src.split('# ======================= HERO: real sky')[0])
def panels(fig,a,b,vertical):
    show(a,'ps1_10arcmin.png',600,1200); show(b,'ps1_2arcmin.png',120,1200)
    a.add_patch(Rectangle((-60,-60),120,120,fill=False,ec=ORANGE,lw=2))
    scalebar(a,-200,-270,60,'1 arcminute'); compass(a,250,-280,40)
    b.add_patch(Circle((0,0),3.2,fill=False,ec=ORANGE,lw=2.4)); b.add_patch(Circle((nbx,nby),3.2,fill=False,ec=BLUE,lw=1.8,ls='--'))
    scalebar(b,-40,-52,10,'10″'); compass(b,50,-54,7)
    corners=[((60,-60),(60,60)),((-60,-60),(-60,60))] if vertical else [((-60,60),(60,60)),((-60,-60),(60,-60))]
    for (pa,pb) in corners:
        fig.add_artist(ConnectionPatch(xyA=pa,coordsA=a.transData,xyB=pb,coordsB=b.transData,color=ORANGE,lw=1,alpha=0.7))
# vertical stack
fig=plt.figure(figsize=(7,14.4)); fig.patch.set_facecolor(SURF)
a=fig.add_axes([0.03,0.515,0.94,0.47]); b=fig.add_axes([0.03,0.015,0.94,0.47])
panels(fig,a,b,True); fig.savefig(OUT+'post_00_real_sky_stack.png',dpi=170); plt.close(fig)
# side-by-side
fig=plt.figure(figsize=(14,7.15)); fig.patch.set_facecolor(SURF)
a=fig.add_axes([0.015,0.03,0.475,0.94]); b=fig.add_axes([0.51,0.03,0.475,0.94])
panels(fig,a,b,False); fig.savefig(OUT+'post_00_real_sky_pair.png',dpi=170); plt.close(fig); print('ok')
