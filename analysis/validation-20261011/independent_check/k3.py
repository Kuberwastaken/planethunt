import numpy as np, sys
exec(open('k.py').read().split('P=13.769448')[0])
P=13.769448; T0=-1369.7546
# variants: inner core (|dt|<0.7h), different baseline windows, per-event median
for inner in [1.1,0.8,0.6]:
  for win in [6.6,10,15]:
    D=[];W=[]
    for n in range(-60,60):
        tc=T0+n*P; dt=(t-tc)*24
        sel=np.abs(dt)<win; intr=np.abs(dt)<inner; oot=sel&(np.abs(dt)>2.2)
        if intr.sum()<1 or oot.sum()<4: continue
        c=np.polyfit(dt[oot],f[oot],1); r=1-f[intr]/np.polyval(c,dt[intr])
        D.append(np.mean(r)); W.append(intr.sum())
    D=np.array(D)
    print('inner %.1fh win %.1fh: N=%d mean %.0f median %.0f ppm, event-scatter err %.0f -> snr %.1f'%(inner,win,len(D),D.mean()*1e6,np.median(D)*1e6,D.std()/np.sqrt(len(D))*1e6,D.mean()/(D.std()/np.sqrt(len(D)))))
