from pathlib import Path
import pandas as pd,re,json,hashlib,datetime
p=Path(__file__).parent;s=(p/'bienias2025_appendixA.txt').read_text();rows=[]
for gid,ra,dec,alias,kic in re.findall(r'Gaia DR3 (\d{19})\s+([\d.]+)\s+([\d.]+)\s+([^\n]+)\n\s+\(KIC (\d+)\)',s.split('Table 2:')[0]):
 m=re.search(gid+r'\s+BJD0[^\n]*?([\d.]+)\s*\n[^\n]*Period[^\n]*?([\d.]+)\s*\n',s)
 assert m,gid
 rows.append(dict(gaia_dr3_id=gid,ra=float(ra),dec=float(dec),alias=alias,aperture_kic=int(kic),period_days=float(m[2]),epoch_bkjd=float(m[1]),catalog='Bienias_Szabo2025_background_candidate',source='https://doi.org/10.5281/zenodo.14618891',host_kic=''))
assert len(rows)==7,len(rows)
rows.append(dict(gaia_dr3_id='2077240046296834304',ra=295.859489,dec=42.713179,alias='',aperture_kic=7214804,period_days=4.99671123,epoch_bkjd=635.0541,catalog='MartinezPalomera2022_APEXBA_candidate',source='https://arxiv.org/abs/2112.06683',host_kic=''))
s=(p/'apexba2022.txt').read_text()
for gid,per,epoch,dur,dep in re.findall(r'Gaia EDR3 (\d{19})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',s):
 rows.append(dict(gaia_dr3_id=gid,period_days=float(per),epoch_bkjd=float(epoch),duration_days=float(dur),depth_pct=float(dep),catalog='MartinezPalomera2022_APEXBA_EB',source='https://arxiv.org/abs/2112.06683',host_kic=''))
d=pd.DataFrame(rows);d.to_csv(p/'kepler_background_prior_signals.csv',index=False)
prov={'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'notes':['Bienias KIC IDs label aperture primary, NOT planet host. Do not join these to host KIC as same object.','Source Table1 corrects contradictory exampleID in mainpaperintro; quoted period/epochs Table4 finalcolumn.','Gaia IDs must be strings. BKJD=BJD-2454833.0.','All objects are prior reports regardless of validation status.'],'files':{f:hashlib.sha256((p/f).read_bytes()).hexdigest()for f in ['bienias2025_appendixA.pdf','apexba2022.pdf']},'counts':d.catalog.value_counts().to_dict()};(p/'kepler_background_prior_signals.provenance.json').write_text(json.dumps(prov,indent=2));print(d.to_string(index=False))
