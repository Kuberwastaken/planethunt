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
        p.point(p.X(x),p.Y(y),'Fold residual',[('Time',f'{x:.3f} hours'),('Residual',f'{y:,.2f} ppm'),('Bin uncertainty',f'±{e:,.2f} ppm'),('Saved model',f'{m:,.2f} ppm')])
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
        p.hit(p.l,p.Y(y)-9,p.w-p.l-8,18,f'Quarter {q}', [('Cadences',f'{len(ts):,}'),('Measured events',str(len(ev))),('First / last BTJD',f'{min(ts):.5f} / {max(ts):.5f}'),('Selection','Reserved' if held else 'Search')])
        for e in ev:
            x=p.X(float(e['predicted_mid_btjd']));p.line(x,p.Y(y)-6,x,p.Y(y)+6,TXT,1)
            p.hit(x-4,p.Y(y)-9,8,18,f"Event {e['epoch']} / Q{q}", [('Mid-transit BTJD',e['predicted_mid_btjd']),('Depth',f"{float(e['depth_ppm']):,.2f} ± {float(e['err_ppm']):,.2f} ppm"),('In-transit samples',e['n_in']),('Selection','Reserved' if held else 'Search')])
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
        p.hit(12,p.Y(y)-15,p.w-24,30,label,[('Depth',f'{depth:,.2f} ppm'),('Uncertainty',f'±{error:,.2f} ppm'),('Count',str(n))])
    save('source-depth-comparison',p.svg('The signal is specific to this star and period','Depths and one-sigma errors from the same saved kdepth test: the candidate target is about 2348 ppm, the bright neighbour 24 ppm; folds at all five Kepler-169 ephemerides are consistent with zero. Measurement choice differs from other depth estimates.'))

def centroid_vectors():
    d=json.loads((V/'results/kepler/kcentroid_tpf.json').read_text())
    p=Plot(1080,690,l=0,r=0,t=0,b=0)
    p.text(22,24,'QUARTER',12,MUT)
    for left,right,ticks,label in [(130,560,[-.5,0,1,2,3,4],'Column shift (millipixels)'),(660,1050,[-1,-.5,0,.5,1],'Row shift (millipixels)')]:
        low,high=(-.6,4.5) if left==130 else (-1.2,1.3)
        scale=lambda v:left+(v-low)/(high-low)*(right-left)
        for tick in ticks:
            xx=scale(tick);p.line(xx,62,xx,615,LINE if tick else MUT,.7);p.text(xx,646,str(tick),12,MUT,'middle')
        p.text((left+right)/2,677,label,14,TXT,'middle')
    p.text(130,24,'● measured ±1σ   ○ target prediction   ▪ neighbour prediction',13,TXT)
    for i,r in enumerate(d['per_quarter']):
        y=80+i*46;p.text(22,y+4,f"Q{r['q']}",15,TXT)
        p.line(22,y+23,1055,y+23,LINE,.5)
        detail=[]
        for component,(left,right,low,high,label) in enumerate([(130,560,-.6,4.5,'Column'),(660,1050,-1.2,1.3,'Row')]):
            X=lambda v:left+(v-low)/(high-low)*(right-left)
            value=r['meas_mpix'][component];error=r['err_mpix'][component];target=r['pred_target'][component];neighbour=r['pred_neighbour'][component]
            p.line(X(value-error),y,X(value+error),y,TXT,1.5);p.circ(X(value),y,4,TXT)
            p.circ(X(target),y-10,4,'none',TXT,1.3);p.rect(X(neighbour)-3,y+7,6,6,MUT,0)
            detail.extend([(label+' measured',f'{value:.4f} ± {error:.4f} mpix'),(label+' target',f'{target:.4f} mpix'),(label+' neighbour',f'{neighbour:.4f} mpix')])
        p.hit(20,y-20,1035,42,f"Quarter {r['q']} / centroid",detail+[('Count',str(r['n']))])
    save('centroid-vectors',p.svg('Centroid predictions by quarter','Twelve separate quarter rows compare measured column and row shifts, with one-sigma errors, to target and neighbour predictions. Filled circles are measurements, open circles target predictions, squares neighbour predictions. Column and row axes use different labelled scales.'))

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
        p.hit(p.X(x)+1,p.t,w,p.h-p.b-p.t,f'{x:,} ≤ depth < {x+500:,} ppm',[('Search events',str(a)),('Reserved events',str(b)),('Total',str(a+b))])
    p.text(72,44,'Grey: search quarters / white: reserved quarters',11,TXT)
    save('event-depth-distribution',p.svg('Distribution of all exported event depths','Event counts in 500 ppm intervals, stacked by discovery and reserved quarter selections. Scatter is visible even though the stacked transit is precise; this histogram is not an independent significance test.'))
    dump('event-depth-histogram.csv',['bin_left_ppm','search_count','reserved_count'],hist)

if __name__=='__main__':
    for fn in [residuals,baseline,source_depth,centroid_vectors,noise_histogram]:fn()
