import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Circle
exec(open('/root/ph/post/post_figs.py').read().split('# ------------------------------------------------------------------ data')[0])
# --- numbers (TIC host parameters; same as the analysis)
P=13.769448; M=0.5054; R=0.50748; T=3633.
a=(M*(P/365.25)**2)**(1/3)                     # AU
L=R**2*(T/5772)**4; S=L/a**2; Teq=278.6*S**0.25
ang=np.degrees(2*R*0.0046505/a); sun=0.533
print('a %.4f AU  L %.4f Lsun  S %.2f  Teq %.0f K  star %.2f deg (%.1fx Sun)'%(a,L,S,Teq,ang,ang/sun))
json.dump(dict(a_AU=a,L_Lsun=L,insolation_earth=S,Teq_K_zero_albedo=Teq,star_angular_diam_deg=ang,sun_angular_diam_deg=sun,radius_earth=[2.5,3.0]),open(OUT+'data/kic5689121_model_numbers.json','w'),indent=1)
fig=plt.figure(figsize=(14,6.2)); fig.patch.set_facecolor(SURF)
def ax_(x,w,ttl):
    a_=fig.add_axes([x,0.12,w,0.70]); a_.set_aspect('equal'); a_.axis('off'); fig.text(x,0.84,ttl,color=INK2,fontsize=13); return a_
# 1 orbit to scale
A=ax_(0.03,0.30,'Its orbit, to scale with Mercury\'s')
th=np.linspace(0,2*np.pi,400)
A.plot(0.387*np.cos(th),0.387*np.sin(th),color=INK3,lw=1.4,ls=(0,(4,3)))
A.plot(a*np.cos(th),a*np.sin(th),color=ORANGE,lw=2.4)
A.add_patch(Circle((0,0),0.012,color='#e8603c')); A.add_patch(Circle((a*np.cos(0.8),a*np.sin(0.8)),0.008,color=ORANGE))
A.text(-0.30,0.33,'Mercury\n0.39 AU · 88 days',color=INK3,fontsize=11,ha='center')
A.annotate('this planet\n%.2f AU · 13.8 days'%a,xy=(a*np.cos(0.8),a*np.sin(0.8)),xytext=(0.20,0.24),color=ORANGE,fontsize=11,arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1))
A.set_xlim(-0.43,0.43); A.set_ylim(-0.43,0.43)
# 2 size comparison
B=ax_(0.37,0.30,'Its size')
xs=[0,2.8,9.3]; rs=[1.0,2.75,3.88]; cols=[BLUE,ORANGE,'#7f9cc4']; labs=['Earth','This planet\n2.5–3× Earth','Neptune\n3.9× Earth']
for x,r,c,l in zip(xs,rs,cols,labs):
    B.add_patch(Circle((x+r,0),r,color=c,alpha=0.95 if c!=ORANGE else 1))
    B.text(x+r,-max(rs)-0.6,l,color=c if c!=BLUE else INK,fontsize=11,ha='center',va='top')
B.set_xlim(-0.5,17.4); B.set_ylim(-7.4,6.0)
# 3 star in the sky
C=ax_(0.70,0.28,'Its star in the sky')
C.add_patch(Circle((-1.9,0),sun/2,color='#f4e7c8')); C.add_patch(Circle((1.1,0),ang/2,color='#e8603c'))
C.text(-1.9,-1.85,'our Sun,\nfrom Earth\n%.1f° wide'%sun,color=INK2,fontsize=11,ha='center',va='top')
C.text(1.1,-1.85,'its star,\nfrom the planet\n%.1f° wide (~%.0f×)'%(ang,ang/sun),color='#e8603c',fontsize=11,ha='center',va='top')
C.set_xlim(-2.9,2.9); C.set_ylim(-3.4,2.2)
fig.text(0.03,0.93,'Modelled from the measured orbit, transit depth and star size  ·  ~5× Earth\'s sunlight  ·  ≈ %d K  ·  light left the star ~1050 AD'%(round(Teq/10)*10),color=INK2,fontsize=11.5)
fig.text(0.03,0.035,'Model, not a photograph. Host: 0.51 R☉, 0.51 M☉, 3,633 K (TIC 8). Temperature assumes zero albedo. KIC 5689121 · planet candidate.',color=INK3,fontsize=9)
fig.savefig(OUT+'post_07_model.png',dpi=170); plt.close(fig); print('ok')
