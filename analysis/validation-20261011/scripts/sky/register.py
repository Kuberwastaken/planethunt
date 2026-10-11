import numpy as np, pandas as pd, json
from PIL import Image
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
ra0,de0=285.90782692874626,40.94198844296448
x=(g.ra-ra0)*np.cos(np.radians(de0))*3600; y=(g.dec-de0)*3600   # arcsec, +x = east
imgs={'ps1_2arcmin':(1200,120.0),'ps1_10arcmin':(1200,600.0),'ps1_stsci_2arcmin':(480,120.0),'dss2_15arcmin':(1200,900.0)}
out={}
for nm,(N,fov) in imgs.items():
    a=np.asarray(Image.open('/root/ph/sky/%s.png'%nm).convert('L'),float); sc=fov/N
    px=N/2-0.5 - x/sc; py=N/2-0.5 - y/sc   # east left, north up (row 0 = top)
    sel=(g.phot_g_mean_mag<19.5)&(px>15)&(px<N-15)&(py>15)&(py<N-15)
    off=[]
    for X,Y,G in zip(px[sel],py[sel],g.phot_g_mean_mag[sel]):
        r=max(4,int(2.5/sc)); xi,yi=int(round(X)),int(round(Y))
        w=a[yi-r:yi+r+1,xi-r:xi+r+1]; w=w-np.median(a); w[w<0]=0
        if w.sum()<=0: continue
        yy,xx=np.mgrid[-r:r+1,-r:r+1]; cx=(w*xx).sum()/w.sum(); cy=(w*yy).sum()/w.sum()
        peak=a[yi-r:yi+r+1,xi-r:xi+r+1].max()
        off.append((G,(xi+cx-X)*sc,(yi+cy-Y)*sc,peak))
    o=np.array(off)
    if len(o): print('%-18s scale %.3f"/px  n=%d  median offset dx %.2f" dy %.2f"  mad %.2f"'%(nm,sc,len(o),np.median(o[:,1]),np.median(o[:,2]),np.median(np.hypot(o[:,1]-np.median(o[:,1]),o[:,2]-np.median(o[:,2])))))
    out[nm]=dict(scale=sc,n=int(len(o)),dx=float(np.median(o[:,1])) if len(o) else None,dy=float(np.median(o[:,2])) if len(o) else None)
    # target & neighbour pixel positions and their colour
    for lab,i in (('target',int(np.argmin(np.hypot(x,y)))),('KIC5689116',int(np.argmin(np.abs(np.hypot(x,y)-7.1))))):
        X,Y=px[i],py[i]; im=np.asarray(Image.open('/root/ph/sky/%s.png'%nm).convert('RGB'),float)
        r=max(2,int(1.0/sc)); c=im[int(Y)-r:int(Y)+r+1,int(X)-r:int(X)+r+1].reshape(-1,3).mean(0)
        print('   %-11s at px (%.1f, %.1f)  mean RGB %s'%(lab,X,Y,np.round(c).astype(int)))
json.dump(out,open('/root/ph/sky/registration.json','w'),indent=1)
