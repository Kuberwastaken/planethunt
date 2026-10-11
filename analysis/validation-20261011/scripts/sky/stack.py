"""Clean composite: Pan-STARRS 10' and 2' side by side (and stacked vertically), native pixels,
only the candidate (orange) / KIC 5689116 (blue dashed) circles, zoom box, scale bars and N/E arrows."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, ConnectionPatch
from PIL import Image
ORANGE,BLUE,INK,BG='#d95926','#3987e5','#f0efec','#1a1a19'
ra0,de0=285.90782692874626,40.94198844296448
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
gx=(g.ra-ra0)*np.cos(np.radians(de0))*3600; gy=(g.dec-de0)*3600
ib=int(np.argmin(np.abs(np.hypot(gx,gy)-7.1))); nbx,nby=float(gx[ib]),float(gy[ib])
wide=np.asarray(Image.open('/root/ph/sky/ps1_10arcmin.png').convert('RGB')); zoom=np.asarray(Image.open('/root/ph/sky/ps1_2arcmin.png').convert('RGB'))
def panel(ax,im,fov):
    h=fov/2; ax.imshow(im,extent=[h,-h,-h,h],interpolation='none'); ax.set_xlim(h,-h); ax.set_ylim(-h,h); ax.axis('off')
def scalebar(ax,x,y,L,lab,fs):
    ax.plot([x,x-L],[y,y],color=INK,lw=3,solid_capstyle='butt'); ax.text(x-L/2,y+L*0.10,lab,color=INK,ha='center',va='bottom',fontsize=fs)
def compass(ax,x,y,L,fs):
    k=dict(arrowstyle='-|>,head_width=0.35,head_length=0.6',color=INK,lw=2)
    ax.annotate('',xy=(x,y+L),xytext=(x,y),arrowprops=k); ax.text(x,y+L*1.12,'N',color=INK,ha='center',va='bottom',fontsize=fs,weight='bold')
    ax.annotate('',xy=(x+L,y),xytext=(x,y),arrowprops=k); ax.text(x+L*1.12,y,'E',color=INK,ha='right',va='center',fontsize=fs,weight='bold')
def draw(layout):
    if layout=='side': fig=plt.figure(figsize=(24,12),dpi=100); A=fig.add_axes([0,0,0.5,1]); B=fig.add_axes([0.5,0,0.5,1])
    else: fig=plt.figure(figsize=(12,24),dpi=100); A=fig.add_axes([0,0.5,1,0.5]); B=fig.add_axes([0,0,1,0.5])
    fig.patch.set_facecolor(BG)
    panel(A,wide,600); panel(B,zoom,120)
    A.add_patch(Rectangle((-60,-60),120,120,fill=False,ec=ORANGE,lw=2.5))
    scalebar(A,-205,-275,60,'1′',26); compass(A,235,-280,42,24)
    for ax,r,lw in ((B,3.3,4),):
        ax.add_patch(Circle((0,0),r,fill=False,ec=ORANGE,lw=lw)); ax.add_patch(Circle((nbx,nby),r,fill=False,ec=BLUE,lw=lw*0.8,ls=(0,(4,3))))
    scalebar(B,-41,-55,10,'10″',26); compass(B,46,-56,8.4,24)
    # thin divider and zoom guides
    if layout=='side':
        fig.add_artist(matplotlib.lines.Line2D([0.5,0.5],[0,1],color=BG,lw=6))
        for yy in (60,-60):
            fig.add_artist(ConnectionPatch(xyA=(-60,yy),coordsA=A.transData,xyB=(60,yy),coordsB=B.transData,color=ORANGE,lw=1.5,alpha=0.7,ls='--'))
    else:
        fig.add_artist(matplotlib.lines.Line2D([0,1],[0.5,0.5],color=BG,lw=6))
        for xx in (60,-60):
            fig.add_artist(ConnectionPatch(xyA=(xx,-60),coordsA=A.transData,xyB=(xx,60),coordsB=B.transData,color=ORANGE,lw=1.5,alpha=0.7,ls='--'))
    fn='/root/ph/post/out/kic5689121_panstarrs_%s.png'%layout; fig.savefig(fn,dpi=100,facecolor=BG); plt.close(fig); return fn
for l in ('side','vertical'): print(draw(l))
