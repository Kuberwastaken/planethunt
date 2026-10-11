import json, numpy as np
r=json.load(open('/root/ph/planethunt/analysis/kepler-sap-recheck.json'))['report']
ev=np.array([e['center'] for e in r['events']])           # BTJD
P=r['ephemeris']['period_days']; T0=r['ephemeris']['epoch_btjd']; D=r['ephemeris']['duration_hours']/24
k169={'e':(13.767101,174.81089,2.9105),'c':(6.19546,134.71507,2.952),'b':(3.250582,133.69472,2.2537),
      'd':(8.348192,136.84111,2.835),'f':(87.091259,187.31231,7.0)}
print('candidate events: %d, span %.1f d (%.1f cycles)'%(len(ev),np.ptp(ev),np.ptp(ev)/P))
out={}
for n,(p,t0bk,dh) in k169.items():
    t0=t0bk-2167.0
    ph=((ev-t0)/p)
    dt=(ph-np.round(ph))*p                 # days from nearest Kepler-169 transit
    sep=np.abs(dt)
    lim=(D+dh/24)/2                         # any overlap of the two transit windows
    out[n]=dict(min_sep_h=float(sep.min()*24),n_overlap=int((sep<lim).sum()),dt_first=float(dt[0]),dt_last=float(dt[-1]))
    print('Kepler-169 %s P=%.6f: min |dt| %.2f h, overlaps %d/%d, offset first %.3f d, last %.3f d'%(n,p,sep.min()*24,(sep<lim).sum(),len(ev),dt[0],dt[-1]))
json.dump(out,open('/root/ph/work/k169_overlap.json','w'),indent=1)
