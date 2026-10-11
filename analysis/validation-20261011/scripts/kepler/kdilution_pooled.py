"""Dilution models for the per-quarter SAP depth of KIC 5689121, with per-quarter errors
from the pooled per-event scatter (sigma_event / sqrt(N_q)). This is the version quoted in
the write-up; kdilution.py uses raw per-quarter scatter, which is unreliable for quarters
with only 2 events."""
import json, numpy as np
from scipy.stats import chi2 as C
rows = json.load(open('/root/ph/work/kcrowd.json'))
D = json.load(open('/root/ph/work/kdepth.json'))
gd = D['target_psf_at_candidate'][1]
sig_ev = D['target_sap_at_candidate'][2] * np.sqrt(D['target_sap_at_candidate'][0])
N = np.array([r['sap'][0] for r in rows]); sap = np.array([r['sap'][1] for r in rows]); se = sig_ev / np.sqrt(N)
x = np.array([r['flfrcsap'] / (r['med_sap'] / r['med_psf']) for r in rows])
crowd = np.array([r['crowdsap'] for r in rows])
def fa(xx):
    w = 1 / se**2; a = np.sum(w * sap * gd * xx) / np.sum(w * (gd * xx)**2)
    return a, np.sum(((sap - a * gd * xx) / se)**2)
res = {}
for nm, xx in (('dilution_fluxratio', x), ('crowdsap', crowd), ('constant', np.ones_like(x)), ('on_contaminant', 1 - x)):
    a, c = fa(xx); res[nm] = dict(alpha=a, chi2=c, p=float(C.sf(c, len(x) - 1)))
    print('%-20s alpha %.3f chi2 %.1f / %d dof  p=%.3g' % (nm, a, c, len(x) - 1, res[nm]['p']))
res['per_event_sigma_ppm'] = sig_ev
json.dump(res, open('/root/ph/work/kdilution_pooled.json', 'w'), indent=1)
