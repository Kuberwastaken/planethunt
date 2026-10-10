"""Presentation-only charts. No search, period fitting, or validation is performed."""
from pathlib import Path
import json, sys, importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#c0bebf','text.color':'#251f21','axes.labelcolor':'#251f21','xtick.color':'#585254','ytick.color':'#585254','figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':170})
hits=dict(json.loads((ROOT/'evidence/tess/hits/hits_ext_1-1fce4d3a.txt').read_text()))
# Reuse saved cleaning function to present a folded curve at the SAVED search ephemeris.
# An adapter supplies its unused LIGHTCURVES constant, not a substituted algorithm.
import types
sys.modules['env']=types.SimpleNamespace(LIGHTCURVES=ROOT/'evidence/tess/lightcurves')
spec=importlib.util.spec_from_file_location('saved_lcsearch',ROOT/'evidence/tess/scripts/lcsearch_PATCHED.py')
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
for tic in (309780779,305054512):
 d=np.load(ROOT/f'evidence/tess/lightcurves/{tic}.npz');lc={k:d[k] for k in d.files}
 lc,bad,noise=L.reject_bad_sectors(lc);c=L.clean(lc);s=hits[tic]
 ph=((c['time']-s['t0']+s['period']/2)%s['period']-s['period']/2)*24
 width=3 if tic==309780779 else 7
 edges=np.linspace(-width,width,31);x=[];y=[];e=[];n=[]
 for a,b in zip(edges[:-1],edges[1:]):
  m=(ph>=a)&(ph<b);nn=m.sum()
  if nn<2:continue
  vals=(c['flux'][m]-1)*1e6
  x.append((a+b)/2);y.append(float(np.mean(vals)));e.append(float(np.std(vals,ddof=1)/np.sqrt(nn)));n.append(int(nn))
 fig,ax=plt.subplots(figsize=(7,3.8));ax.errorbar(x,y,yerr=e,fmt='o',color='#527d70',ms=4,capsize=2);ax.axhline(0,color='#eae9ea');ax.axvline(0,color='#eae9ea');ax.set(xlabel='Hours from saved search epoch (phase folded)',ylabel='Relative flux (ppm)',title=f'TIC {tic} | fixed period {s["period"]:.5f} d');fig.tight_layout();fig.savefig(OUT/f'{tic}-fold.png');plt.close(fig)
 (ROOT/f'analysis/{tic}-display-bins.json').write_text(json.dumps({'purpose':'presentation at saved ephemeris; not independent validation','detrend_window_days':0.75,'bad_sectors':bad,'bins':list(map(lambda q:dict(zip(['hours','flux_ppm','standard_error_ppm','cadences'],q)),zip(x,y,e,n)))},indent=2)+'\n')
 p=json.loads((ROOT/'evidence/tess/pixels'/f'{tic}_pixels{"_CORRECTED_RERUN" if tic==305054512 else ""}.json').read_text())
 fig,ax=plt.subplots(figsize=(7,3.8));rows=p['sectors'];ax.bar(range(len(rows)),[r['amp_at_target'] for r in rows],color='#73a89a');ax.axhline(0,color='#eae9ea');ax.set_xticks(range(len(rows)),[f'S{r["sector"]}' for r in rows],rotation=45);ax.set(ylabel='Fitted target amplitude (model units)',title=f'TIC {tic} | target amplitudes by pixel sector');fig.tight_layout();fig.savefig(OUT/f'{tic}-amplitudes.png');plt.close(fig)
# Original PDF charts: lossless raster crops at known PDF page positions.
