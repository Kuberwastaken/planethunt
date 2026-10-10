import json,sys
h=json.load(open(sys.argv[1]))
for t,s in h:
    if s['n_transits']<3 or s['period']<=1: continue
    oe=abs(s['depth_odd_ppm']-s['depth_even_ppm'])/max((s['depth_odd_err_ppm']**2+s['depth_even_err_ppm']**2)**.5,1)
    al=12.5<s['period']<14.8 or (s['period']>5 and abs(s['period']/13.7-round(s['period']/13.7*2)/2)<0.015*s['period']/13.7)
    dfrac=s['duration_hr']/24/s['period']
    ok=(not al) and oe<2 and s['depth_ppm']<10000 and dfrac<0.1 and s['snr']>=8
    if ok: print('*',t,round(s['period'],4),round(s['t0'],3),round(s['duration_hr'],2),'dep',round(s['depth_ppm']),'snr',round(s['snr'],1),'sde',round(s['sde'],1),'n',s['n_transits'],'oe',round(oe,1))
