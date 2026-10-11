"""Additional presentation diagnostics from saved measurements. No refitting or new vetting.
Run from the repository root. Outputs CSV sidecars for every numerical transformation.
"""
import csv, json, math, bisect
from pathlib import Path
from collections import defaultdict
from charts import Plot, save, ebar, TXT, MUT, LINE, OR, BL, FONT
V=Path('analysis/validation-20261011')
D=V/'post/data'
OUT=Path('docs/derived');OUT.mkdir(exist_ok=True)
def rows(name):return list(csv.DictReader((D/name).open()))
def dump(name,keys,data):
    with (OUT/name).open('w') as f:
        w=csv.writer(f);w.writerow(keys);w.writerows(data)

def residuals():
    model=rows('kic5689121_transit_model.csv');mx=[float(r['hours_from_mid']) for r in model];my=[float(r['model_ppm']) for r in model]
    result=[]
    for r in rows('kic5689121_folded_15min_bins.csv'):
        x,y,e=[float(r[k]) for k in ['hours_from_mid','flux_ppm','err_ppm']]
        j=max(1,min(len(mx)-1,bisect.bisect_left(mx,x)))
        m=my[j-1]+(my[j]-my[j-1])*(x-mx[j-1])/(mx[j]-mx[j-1])
        result.append([x,y-m,e,m])
    p=Plot(720,310,l=64,t=30,xr=(-8.5,8.5),yr=(-2300,2300))
    p.xaxis([-8,-4,0,4,8],'Hours from mid-transit');p.yaxis([-2000,-1000,0,1000,2000],'Residual (ppm)')
    for x,y,e,m in result:
        ebar(p,x,y,e,MUT);p.circ(p.X(x),p.Y(y),3,TXT)
    save('transit-residuals',p.svg('Fold minus saved transit model','Residuals of the 67 exported 15-minute bins after linear interpolation of the saved median model. This is a display diagnostic, not a refit or independent goodness-of-fit test.'))
    dump('transit-residuals.csv',['hours_from_mid','residual_ppm','bin_error_ppm','interpolated_model_ppm'],result)

def baseline():
    light=rows('kic5689121_lightcurve_psf.csv');events=rows('kic5689121_per_transit_depths.csv');quarters=defaultdict(list)
    for r in light:quarters[int(r['quarter'])].append(float(r['time_btjd']))
    p=Plot(1100,350,l=52,r=86,t=16,b=52,xr=(-2050,-570),yr=(0,14))
    p.xaxis([-2000,-1750,-1500,-1250,-1000,-750],'BTJD = BJD TDB − 2,457,000')
    out=[]
    for i,(q,ts) in enumerate(sorted(quarters.items())):
        y=13-i;ev=[r for r in events if int(r['quarter'])==q];held=any(r['held_out']=='True' for r in ev)
        p.text(34,p.Y(y)+4,f'Q{q}',11,TXT,'end');p.line(p.X(min(ts)),p.Y(y),p.X(max(ts)),p.Y(y),TXT if held else '#666666',7)
        for e in ev:
            x=p.X(float(e['predicted_mid_btjd']));p.line(x,p.Y(y)-6,x,p.Y(y)+6,TXT,1)
        p.text(1020,p.Y(y)+4,f'{len(ts):,} / {len(ev)}',11,TXT)
        out.append([q,len(ts),len(ev),min(ts),max(ts),held])
    p.text(1070,15,'samples / events',10,MUT,'end')
    save('quarter-baseline',p.svg('Kepler observation baseline','Each horizontal interval spans the first to last available sample in a quarter; small internal gaps are not shown. Vertical marks are exported event times. Bright intervals are reserved quarters. Right column lists cadence and event counts.'))
    dump('quarter-coverage.csv',['quarter','cadences','exported_events','first_btjd','last_btjd','reserved_quarter'],out)

def source_depth():
    d=json.loads((V/'results/kepler/kdepth.json').read_text())
    entries=[('Host / candidate period','target_psf_at_candidate'),('Neighbour / candidate period','neighbor5689116_psf_at_candidate')]+[(f'Host / Kepler-169 {k}',f'target_psf_at_K169{k}') for k in 'bcdef']
    p=Plot(720,390,l=230,r=30,t=35,b=60,xr=(-400,2900),yr=(-.5,6.5))
    p.xaxis([0,1000,2000],'Measured PSF depth (ppm)',grid=True)
    for i,(label,key) in enumerate(entries):
        n,depth,error=d[key];y=6-i;p.text(214,p.Y(y)+4,label,11,TXT,'end');p.line(p.X(depth-error),p.Y(y),p.X(depth+error),p.Y(y),TXT,1.5);p.circ(p.X(depth),p.Y(y),4,TXT if i==0 else '#888888')
    save('source-depth-comparison',p.svg('The signal is specific to this star and period','Depths and one-sigma errors from the same saved kdepth test: the candidate target is about 2348 ppm, the bright neighbour 24 ppm; folds at all five Kepler-169 ephemerides are consistent with zero. Measurement choice differs from other depth estimates.'))

def centroid_vectors():
    d=json.loads((V/'results/kepler/kcentroid_tpf.json').read_text())
    p=Plot(720,420,l=62,r=24,t=30,b=56,xr=(-1,4.5),yr=(-1.2,1.5))
    p.xaxis([-1,0,1,2,3,4],'Column shift (millipixels)',grid=True);p.yaxis([-1,-.5,0,.5,1,1.5],'Row shift (millipixels)')
    for r in d['per_quarter']:
        x,y=r['meas_mpix'];ex,ey=r['err_mpix'];tx,ty=r['pred_target'];nx,ny=r['pred_neighbour']
        p.line(p.X(x),p.Y(y-ey),p.X(x),p.Y(y+ey),'#666666');p.line(p.X(x-ex),p.Y(y),p.X(x+ex),p.Y(y),'#666666')
        p.line(p.X(x),p.Y(y),p.X(tx),p.Y(ty),'#888888',1,'3 4');p.circ(p.X(x),p.Y(y),3.7,TXT)
        p.circ(p.X(tx),p.Y(ty),4,'none',TXT,1.2)
        p.rect(p.X(nx)-3,p.Y(ny)-3,6,6,'#777777',0)
    p.text(75,48,'● measured   ○ target prediction   ▪ neighbour prediction',11,TXT)
    save('centroid-vectors',p.svg('Raw pixel shifts versus source predictions','Measured column and row centroid shifts for 12 quarters, with error bars, connected to target predictions. Squares show predictions if the bright neighbour hosted the signal. This uses the same photons as other localization checks.'))

def noise_histogram():
    ev=rows('kic5689121_per_transit_depths.csv');hist=[[x,0,0] for x in range(-2000,9000,500)]
    for r in ev:
        idx=int((float(r['depth_ppm'])+2000)//500)
        if 0<=idx<len(hist):hist[idx][2 if r['held_out']=='True' else 1]+=1
    p=Plot(720,320,l=56,t=25,b=54,xr=(-2000,9000),yr=(0,max(sum(r[1:]) for r in hist)+2))
    p.xaxis([-2000,0,2000,4000,6000,8000],'Event depth (ppm)');p.yaxis([0,5,10,15,20],'Number of events')
    for x,a,b in hist:
        w=p.X(x+500)-p.X(x)-2
        p.rect(p.X(x)+1,p.Y(a),w,p.Y(0)-p.Y(a),'#666666',0)
        p.rect(p.X(x)+1,p.Y(a+b),w,p.Y(a)-p.Y(a+b),TXT,0)
    p.text(72,44,'Grey: search quarters / white: reserved quarters',11,TXT)
    save('event-depth-distribution',p.svg('Distribution of all exported event depths','Event counts in 500 ppm intervals, stacked by discovery and reserved quarter selections. Scatter is visible even though the stacked transit is precise; this histogram is not an independent significance test.'))
    dump('event-depth-histogram.csv',['bin_left_ppm','search_count','reserved_count'],hist)

if __name__=='__main__':
    for fn in [residuals,baseline,source_depth,centroid_vectors,noise_histogram]:fn()
