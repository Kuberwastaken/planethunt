"""Deliberate known-system control: Kepler-138. Never count as a discovery."""
import json,requests
from pilot import ROOT,one,dump
name='Gaia DR3 2102053446751282944'
req={'service':'Mast.Caom.Filtered','format':'json','pagesize':20,'page':1,'params':{'columns':'*','filters':[{'paramName':'provenance_name','values':['KBONUS-BKG']},{'paramName':'target_name','values':[name]}]}}
r=requests.post('https://mast.stsci.edu/api/v0/invoke',data={'request':json.dumps(req)},timeout=60);r.raise_for_status();j=r.json();dump(ROOT/'known_control_observations.json',j)
row={'source_id':'2102053446751282944','kic':7603200,'tpforg':7603200,'dataURL':j['data'][0]['dataURL']}
out=one(row);out['positive_control']=True;out['known_host']='Kepler-138';out['not_a_discovery']=True
dump(ROOT/'known_control.json',out)
print(json.dumps({'status':out['status'],'signals':[{'period':s['period'],'snr':s['bls_snr'],'holdout_snr':s['holdout']['snr']} for s in out['signals']]}))
