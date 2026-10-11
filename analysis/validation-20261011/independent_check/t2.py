import numpy as np, sys
exec(open('t.py').read().split('early=s<=38')[0].replace("print('sectors'","0 and print('sectors'"))
early=s<=38; late=s>=61; ones=np.ones_like(early)
P,T0=np.load('eph.npy')
# reference epoch near 2280.02
nref=np.round((2280.02-T0)/P); Tref=T0+nref*P; print('ref epoch n=%d T=%.4f'%(nref,Tref))
# uncertainty map over (P,Tref) on early: chi2-ish via snr^2 drop of 1
G=[]
for PP in np.arange(P-0.0004,P+0.0004,0.00001):
  for TT in np.arange(Tref-0.02,Tref+0.0201,0.001):
    dp,er,N=depth(early,PP,TT-nref*PP,1.0); G.append((PP,TT,(dp/er)**2))
G=np.array(G); mx=G[:,2].max(); ok=G[G[:,2]>mx-1]
pred=ok[:,1]+89*ok[:,0]
print('P 1sig range %.5f..%.5f  Tref range %.4f..%.4f  pred(n+89) %.4f..%.4f (span %.0f min)'%(ok[:,0].min(),ok[:,0].max(),ok[:,1].min(),ok[:,1].max(),pred.min(),pred.max(),(pred.max()-pred.min())*1440))
print('nominal pred n+89: %.4f'%(Tref+89*P))
for win in [2.0,3.0,4.0,6.0]:
  for dur in [0.9,1.0,1.2]:
    a=depth(late,P,T0,dur,win*dur); b=depth(late,P,T0+P/2,dur,win*dur); c=depth(ones,P,T0+P/2,dur,win*dur)
    print('win %.0fxdur dur %.1f: late depth %.0f+-%.0f (%.1fs) | late ph0.5 %.0f+-%.0f | all ph0.5 %.0f+-%.0f'%(win,dur,a[0],a[1],a[0]/a[1],b[0],b[1],c[0],c[1]))
# late timing with each late sector group separately
for grp,name in [((s>=61)&(s<=68),'61-68'),(s>=89,'89-90')]:
    res=[]
    for dT in np.arange(-60,60.1,1)/1440:
        dp,er,N=depth(grp,P,T0+dT,1.0); res.append((dT*1440,dp,er))
    res=np.array(res); i=np.argmax(res[:,1]/res[:,2]); print(name,'best offset %.0f min depth %.0f+-%.0f; at 0: %.0f+-%.0f'%(res[i,0],res[i,1],res[i,2],res[60,1],res[60,2]))
