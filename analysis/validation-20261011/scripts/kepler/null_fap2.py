import pandas as pd, numpy as np
R='/root/ph/planethunt/'
p=pd.read_csv(R+'evidence/codex/database_expansion/kbonus/pilot_summary.csv').rename(columns={'rank':'signal_rank','screen_pass':'first_screen_pass'})
e1=pd.read_csv(R+'analysis/kbonus-extension-20261011/signals_real_and_inverted.csv')
e2=pd.read_csv(R+'analysis/kbonus-extension-20261011/ranks577-1800/signals_real_and_inverted.csv')
for d,n in ((p,'pilot'),(e1,'ext1'),(e2,'ext2')): d['stage']=n
cols=['stage','source_id','kic','inverted','period_d','duration_hr','depth_ppm','bls_snr','holdout_snr','first_screen_pass']
a=pd.concat([d[cols] for d in (p,e1,e2)],ignore_index=True)
for c in ('inverted','first_screen_pass'): a[c]=a[c].astype(str).str.lower().eq('true')
print('unique source_ids real/inv:',a[~a.inverted].source_id.nunique(),a[a.inverted].source_id.nunique())
sp=a[a.first_screen_pass]
print(sp.sort_values('bls_snr',ascending=False)[['stage','kic','inverted','period_d','depth_ppm','bls_snr','holdout_snr']].to_string())
inv=sp[sp.inverted]
print('\nInverted screen passes:',len(inv),'max BLS SNR %.2f max holdout %.2f'%(inv.bls_snr.max(),inv.holdout_snr.max()))
print('Inverted screen passes with P>1.5d:',(inv.period_d>1.5).sum(), ' max SNR %.2f max hold %.2f'%(inv[inv.period_d>1.5].bls_snr.max(),inv[inv.period_d>1.5].holdout_snr.max()))
