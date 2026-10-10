"""Conservative exact-TIC and 120 arcsec matches; no novelty certification.

Epochs normalized to BJD_TDB where source uses BTJD. Gaia proper-motion correction
is not applied here; targeted survivor vetting must do it at observation epochs.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

R=Path(__file__).resolve().parent
W=R.parents[1]
parts=[]
def add(file, mapping, label, epoch_offset=0):
    if not file.exists(): return
    d=pd.read_csv(file,comment='#',low_memory=False)
    o=pd.DataFrame(index=d.index)
    for col,source in mapping.items(): o[col]=d[source]
    if 'TIC' in o: o['TIC']=pd.to_numeric(o.TIC.astype(str).str.replace('TIC ','',regex=False),errors='coerce')
    if 'epoch_BJD' in o: o['epoch_BJD']=pd.to_numeric(o.epoch_BJD,errors='coerce')+epoch_offset
    o['catalog']=label
    o['source_file']=file.name
    parts.append(o)

add(R/'nasa_toi.csv',dict(TIC='tid',period='pl_orbper',epoch_BJD='pl_tranmid',ra='ra',dec='dec',status='tfopwg_disp'),'NASA TOI')
add(R/'nasa_pscomppars.csv',dict(TIC='tic_id',period='pl_orbper',epoch_BJD='pl_tranmid',ra='ra',dec='dec',name='pl_name'),'NASA confirmed')
add(R/'exofop_ctoi.csv',dict(TIC='TIC ID',period='Period (days)',epoch_BJD='Transit Epoch (BJD)',ra='RA',dec='Dec',status='User Disposition'),'ExoFOP CTOI')
add(R/'villanova_eb.csv',dict(TIC='tic',period='period',epoch_BJD='t0_btjd',ra='ra',dec='dec'),'Villanova EB',2457000)
for p in (R/'raven').glob('*.csv'):
    add(p,dict(TIC='ticid',period='bls_per',epoch_BJD='bls_t0',ra='ra',dec='dec'),'RAVEN',2457000)
for p in (W/'upstream-eumemic/results_public').glob('candidates*.csv'):
    add(p,dict(TIC='TIC',period='P_d',epoch_BJD='T0_BJD'),'Eumemic public')
for p in (R/'tce').glob('*.csv'):
    add(p,dict(TIC='ticid',period='tce_period',epoch_BJD='tce_time0bt'),'SPOC TCE',2457000)
allrows=pd.concat(parts,ignore_index=True)
for col in ['TIC','period','epoch_BJD','ra','dec']: allrows[col]=pd.to_numeric(allrows[col],errors='coerce')
allrows.to_csv(R/'known_signals.csv',index=False)
selected=pd.read_csv(R.parent/'targets.csv')
matches=selected[['TIC','branch']].merge(allrows,on='TIC')
matches.to_csv(R/'selected_prior_matches.csv',index=False)
neighbors=[]
pos=allrows.dropna(subset=['ra','dec'])
for star in selected.itertuples():
    # Great-circle haversine; target positions approximate epoch, screen generously.
    ra1,dec1,ra2,dec2=map(np.deg2rad,[star.ra,star.dec,pos.ra.to_numpy(),pos.dec.to_numpy()])
    h=np.sin((dec2-dec1)/2)**2+np.cos(dec1)*np.cos(dec2)*np.sin((ra2-ra1)/2)**2
    sep=2*np.arcsin(np.sqrt(np.clip(h,0,1)))*180/np.pi*3600
    keep=(sep<120)&(pos.TIC.to_numpy()!=star.TIC)
    if keep.any():
        n=pos[keep].copy().rename(columns={'TIC':'neighbor_TIC'})
        n['TIC']=star.TIC;n['separation_arcsec']=sep[keep]
        neighbors.append(n)
pd.concat(neighbors,ignore_index=True).to_csv(R/'selected_neighbor_prior_matches.csv',index=False) if neighbors else pd.DataFrame().to_csv(R/'selected_neighbor_prior_matches.csv',index=False)
print('Exact match counts (catalog,TIC,period rounding may vary across sectors):')
print(matches.groupby('catalog').agg(rows=('TIC','size'),hosts=('TIC','nunique')).to_string())
print(matches[['TIC','period','catalog']].drop_duplicates().to_string(index=False))
print('Neighbor records',sum(len(x) for x in neighbors))
