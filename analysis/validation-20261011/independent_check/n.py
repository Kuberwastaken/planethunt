import pandas as pd
fs=['/root/ph/planethunt/evidence/codex/database_expansion/kbonus/pilot_summary.csv','/root/ph/planethunt/analysis/kbonus-extension-20261011/signals_real_and_inverted.csv','/root/ph/planethunt/analysis/kbonus-extension-20261011/ranks577-1800/signals_real_and_inverted.csv']
L=[]
for f in fs:
    d=pd.read_csv(f,dtype={'source_id':str})
    d=d.rename(columns={'first_screen_pass':'screen_pass'})
    for c in ['inverted','screen_pass']:
        d[c]=d[c].astype(str).str.strip().str.lower().map({'true':True,'false':False,'1':True,'0':False})
    print(f.split('/')[-2:], len(d), d.inverted.value_counts(dropna=False).to_dict(), 'uniq src inv',d[d.inverted].source_id.nunique(),'uniq src all',d.source_id.nunique())
    d['file']=f.split('/')[-2]; L.append(d)
D=pd.concat(L)
inv=D[D.inverted==True]
print('total unique inverted source_id',inv.source_id.nunique(),'unique kic',inv.kic.nunique(),'unique real src',D[D.inverted==False].source_id.nunique())
print('overlap real-only vs inv-only:', len(set(D[D.inverted==False].source_id)-set(inv.source_id)), len(set(inv.source_id)-set(D[D.inverted==False].source_id)))
s=inv[(inv.screen_pass==True)&(inv.period_d>1.5)&(inv.bls_snr>=26.67)&(inv.holdout_snr>=15.47)]
print(s[['file','source_id','kic','period_d','bls_snr','holdout_snr']].to_string())
print('unique stars:',s.kic.nunique(), sorted(s.kic.unique()))
# sensitivity
s2=inv[(inv.period_d>1.5)&(inv.bls_snr>=26.67)&(inv.holdout_snr>=15.47)]
print('without screen flag:',s2.kic.nunique(), sorted(s2.kic.unique()))
print('screen_pass NaN count', D.screen_pass.isna().sum())
g=inv.groupby('source_id').kic.first()
print('kic NaN among inv sources',g.isna().sum(), 'dup kic', g.dropna().duplicated().sum())
