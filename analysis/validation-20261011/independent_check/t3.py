import numpy as np, sys
exec(open('t.py').read().split('early=s<=38')[0].replace("print('sectors'","0 and print('sectors'"))
P,T0=np.load('eph.npy')
tc=T0+198*P; print('pred n=198 %.4f sector'%tc, np.unique(s[np.abs(t-tc)<1]))
win=np.abs(t-tc)<0.5/24*3+0.1
res=[]
for dT in np.arange(-40,40.1,0.5)/1440:
    m=np.abs(t-tc)<0.25
    dp,er,N=depth(m,P,tc+dT,1.0); res.append((dT*1440,dp,er))
res=np.array(res); i=np.argmax(res[:,1]); sn=res[:,1]/res[:,2]
ok=res[(res[:,1]-res[i,1])**2/res[:,2]**2 < 1 ,0]
print('single event best offset %.1f min depth %.0f+-%.0f (snr %.1f); dchi2<1 range %.0f..%.0f'%(res[i,0],res[i,1],res[i,2],sn[i],ok.min(),ok.max()))
