import sys, pandas as pd, numpy as np
R='/root/ph/planethunt/'
p=pd.read_csv(R+'evidence/codex/database_expansion/kbonus/pilot_summary.csv')
p=p.rename(columns={'rank':'signal_rank','period_d':'period_d'})
p['stage']='pilot'
e1=pd.read_csv(R+'analysis/kbonus-extension-20261011/signals_real_and_inverted.csv'); e1['stage']='ext1'
e2=pd.read_csv(R+'analysis/kbonus-extension-20261011/ranks577-1800/signals_real_and_inverted.csv'); e2['stage']='ext2'
cols=['stage','source_id','kic','inverted','signal_rank','period_d','duration_hr','depth_ppm','bls_snr','holdout_snr']
a=pd.concat([p[cols],e1[cols],e2[cols]],ignore_index=True)
a['inverted']=a.inverted.astype(str).str.lower().eq('true')
print(a.groupby(['stage','inverted']).agg(n_sig=('kic','size'),n_star=('kic','nunique'),max_snr=('bls_snr','max'),max_hold=('holdout_snr','max')))
cand=a[(a.kic==5689121)&(~a.inverted)]
print('\ncandidate rows:\n',cand.to_string())
c_snr=cand.bls_snr.max(); c_h=cand.loc[cand.bls_snr.idxmax(),'holdout_snr']
inv=a[a.inverted]; real=a[~a.inverted]
N=inv.kic.nunique(); print('\ninverted stars:',N,' real stars:',real.kic.nunique())
# per-star max for null
for name,df in (('inverted',inv),('real (excl cand)',real[real.kic!=5689121])):
    s=df.groupby('kic').apply(lambda g: pd.Series({'snr':g.bls_snr.max(),'hold':g.holdout_snr.max(),
        'joint':(g[['bls_snr','holdout_snr']].min(axis=1)).max()}))
    print(f'\n{name}: N={len(s)}')
    print(' top5 BLS SNR:',np.round(np.sort(s.snr.dropna())[-5:],2))
    print(' top5 holdout SNR:',np.round(np.sort(s.hold.dropna())[-5:],2))
    print(' stars with SNR>=%.1f: %d ; holdout>=%.1f: %d ; both: %d'%(c_snr,(s.snr>=c_snr).sum(),c_h,(s.hold>=c_h).sum(),((s.snr>=c_snr)&(s.hold>=c_h)).sum()))
    # restrict to "transit-like" periods >1.5 d
    d2=df[df.period_d>1.5]
    s2=d2.groupby('kic').apply(lambda g: pd.Series({'snr':g.bls_snr.max(),'hold':g.holdout_snr.max()}))
    print(' P>1.5d top5 SNR:',np.round(np.sort(s2.snr.dropna())[-5:],2),' top5 hold:',np.round(np.sort(s2.hold.dropna())[-5:],2))
print('\ncandidate: BLS SNR %.2f holdout SNR %.2f'%(c_snr,c_h))
# 95% upper limit on per-star null exceedance with 0 events in N trials
print('Zero-null-exceedance 95%% upper bound per star: %.2e (=3/N)'%(3/N))
print('Look-elsewhere across %d real stars: expected false exceedances <= %.2f (95%% UL)'%(real.kic.nunique(),3/N*real.kic.nunique()))
