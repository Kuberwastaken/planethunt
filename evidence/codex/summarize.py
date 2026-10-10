"""Build auditable summary. Refuses stale results as current evidence."""
import json,hashlib
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
CONTROL={410153553}

def main():
 rows=[];invalid=[];seen=set()
 targets=set(pd.read_csv(ROOT/'targets.csv').TIC.astype(int))
 for f in sorted((ROOT/'results').glob('*.json')):
  d=json.loads(f.read_text());tic=d.get('tic');lc=ROOT/'lightcurves'/f'{tic}.npz'
  if d.get('pipeline_version')!=3:invalid.append({'file':f.name,'reason':'superseded_pipeline_version'});continue
  if not lc.exists() or d.get('input_sha256')!=hashlib.sha256(lc.read_bytes()).hexdigest():invalid.append({'file':f.name,'reason':'input_hash_mismatch'});continue
  if d['status']!='ok':invalid.append({'file':f.name,'reason':d.get('error','failed')});continue
  seen.add((tic,d['mode'],d['inverted']))
  for s in d.get('signals',[]):
   st=s['discovery'];ht=s['holdout']
   row={'tic':tic,'mode':d['mode'],'inverted':d['inverted'],'positive_control':tic in CONTROL,'rank':s['rank'],'period_d':s['period'],'epoch_btjd':s['t0'],'duration_hr':s['duration_hr'],'depth_ppm':s['depth_ppm'],'rp_earth_approx':s['rp_earth_approx'],'discovery_bls_snr':s['bls_snr'],'holdout_search_snr':ht.get('snr'),'discovery_good_events':st.get('n_good_events'),'holdout_good_events':ht.get('n_good_events'),'odd_even_sigma':st.get('odd_even_sigma'),'secondary_snr':st['secondary']/st['secondary_err'] if st.get('secondary_err') else None,'screen_pass':s['screen_pass'],'input_sha256':d['input_sha256']}
   vet=ROOT/'improvements/vetting'/f"{tic}_{d['mode']}_rank{s['rank']}_v3.json"
   if vet.exists():
    v=json.loads(vet.read_text());row['independent_local_snr']=v.get('primary',{}).get('local_snr');row['independent_holdout_snr']=v.get('holdout',{}).get('measurement',{}).get('local_snr');row['vet_flags']=';'.join(v.get('flags',[]))
   row['disposition']='known_positive_control' if tic in CONTROL else ('inverted_negative_control' if d['inverted'] else ('requires_followup_not_a_planet_claim' if s['screen_pass'] else 'failed_initial_screen'))
   if row.get('vet_flags') and tic not in CONTROL:row['disposition']='failed_or_inconclusive_independent_vet'
   if tic==94753488 and s['rank']==1 and d['mode']=='usp' and not d['inverted']:row['disposition']='unresolved_broad_periodic_dimming_not_planet_candidate'
   rows.append(row)
 df=pd.DataFrame(rows);df.to_csv(ROOT/'search_summary.csv',index=False)
 (ROOT/'stale_or_failed_results.json').write_text(json.dumps(invalid,indent=2))
 complete=[t for t in targets if all((t,m,False) in seen for m in ['usp','regular'])]
 incomplete=sorted(targets-set(complete))
 noncontrol=df[(~df.positive_control)&(~df.inverted)] if len(df) else df
 null=df[(~df.positive_control)&df.inverted] if len(df) else df
 stat={'selected_stars':len(targets),'complete_two_band_stars':len(complete),'incomplete_tics':incomplete,'valid_real_search_runs':sum(not i and t in targets for t,m,i in seen),'valid_inverted_search_runs':sum(i and t in targets for t,m,i in seen),'real_signal_records':len(noncontrol),'real_screen_survivors':int(noncontrol.screen_pass.sum()) if len(noncontrol) else 0,'inverted_signal_records':len(null),'inverted_screen_survivors':int(null.screen_pass.sum()) if len(null) else 0,'positive_control':'LHS3844 b; known; never count as novel','discovery_claim':'NONE; no confirmed new planet','invalid_or_superseded_files':len(invalid)}
 (ROOT/'run_status.json').write_text(json.dumps(stat,indent=2));print(json.dumps(stat,indent=2))
if __name__=='__main__':main()
