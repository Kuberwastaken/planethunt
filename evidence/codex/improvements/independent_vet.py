"""Fixed-ephemeris, local-baseline vetting of normalized TESS NPZ flux.

Only NumPy is required. This is a conditional robustness check, NEVER a
discovery significance or a planet validation. Feed raw normalized flux, not
the search detrended flux. All period/epoch/duration choices must be made
outside this program. Reserve holdout sectors BEFORE discovery to justify
--holdout-was-unseen; otherwise their check is explicitly retrospective.
"""
import argparse
import json
from pathlib import Path
import numpy as np


def phase(t, period, epoch):
    return (t - epoch + period / 2) % period - period / 2


def mad(x):
    x = np.asarray(x)
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def load(path):
    with np.load(path, allow_pickle=False) as z:
        t, f = np.asarray(z['time'], float), np.asarray(z['flux'], float)
        s = np.asarray(z['sector'], int) if 'sector' in z else np.zeros(len(t), int)
        ex = np.asarray(z['exptime'], float) if 'exptime' in z else np.full(len(t), 120.)
        er = np.asarray(z['flux_err'], float) if 'flux_err' in z else np.ones(len(t))
    good = np.isfinite(t) & np.isfinite(f) & np.isfinite(ex) & (ex > 0)
    t, f, s, ex, er = [x[good] for x in (t, f, s, ex, er)]
    ix = np.argsort(t)
    return dict(zip(('time', 'flux', 'sector', 'exptime', 'flux_err'), [x[ix] for x in (t, f, s, ex, er)]))


def subset(lc, sel):
    return {k: v[sel] for k, v in lc.items()}


def local_events(lc, period, epoch, duration, exclude_ephemeris=None):
    """Fit exposure-integrated box + intercept + slope independently per event.

    Events require data on both sides; gap-edge or partial events are dropped.
    No clipping is applied, avoiding dip/brightening asymmetry. Empirical noise
    floors and between-event scatter avoid relying on pipeline errors alone.
    """
    t, f, sec, ex, er = [lc[k] for k in ('time', 'flux', 'sector', 'exptime', 'flux_err')]
    if len(t) == 0:
        return []
    window = min(max(3.0 * duration, 0.15), period * 0.23)
    if window <= duration:
        raise ValueError('Transit duration too long relative to period')
    cycle = np.rint((t - epoch) / period).astype(np.int64)
    events = []
    for n in np.unique(cycle):
        center = epoch + n * period
        a, b = np.searchsorted(t, [center - window, center + window])
        if b-a < 12:
            continue
        # Split by sector to prevent fitting an instrumental discontinuity.
        for ss in np.unique(sec[a:b]):
            idx = np.arange(a,b)[sec[a:b] == ss]
            if exclude_ephemeris is not None:
                pp, ee, dd = exclude_ephemeris
                idx = idx[np.abs(phase(t[idx], pp, ee)) > dd]
            x, y, exposure, err = t[idx] - center, f[idx], ex[idx] / 86400, er[idx]
            overlap = np.maximum(0., np.minimum(x + exposure/2, duration/2) - np.maximum(x - exposure/2, -duration/2))
            box = overlap / exposure
            intr, oot = box > 0, box == 0
            if intr.sum() < 2 or (x < -duration).sum() < 4 or (x > duration).sum() < 4:
                continue
            X = np.column_stack((np.ones(len(x)), x/window, -box))
            # Floor measured point noise prevents unrealistically tiny formal errors.
            empirical = mad(np.diff(y[oot])) / np.sqrt(2)
            if empirical <= 0:
                empirical = max(mad(y[oot]), 1e-8)
            gooderr = np.isfinite(err) & (err > 0)
            err = np.where(gooderr, err, empirical)
            # Equal errors in absence of usable uncertainty information.
            if np.all(err == 1.):
                err = np.full_like(err, empirical)
            err = np.maximum(err, empirical)
            w = 1 / err**2
            normal = X.T @ (w[:,None] * X)
            try:
                cov = np.linalg.inv(normal)
            except np.linalg.LinAlgError:
                continue
            beta = cov @ (X.T @ (w*y))
            residual = y - X @ beta
            inflate = max(1., np.sum(w * residual**2) / max(1, len(y)-3))
            sigma = float(np.sqrt(cov[2,2] * inflate))
            events.append({'cycle': int(n), 'sector': int(ss), 'center': float(center),
                           'depth': float(beta[2]), 'error': sigma, 'n_in': int(intr.sum()),
                           'n_out': int(oot.sum()), 'snr': float(beta[2]/sigma)})
    return events


def combine(events):
    if not events:
        return {'n_events': 0}
    d = np.array([r['depth'] for r in events]); e = np.array([r['error'] for r in events])
    w = 1/e**2; a = w / w.sum(); depth = float(a@d)
    white = float(1/np.sqrt(w.sum()))
    # Cluster-robust error treating event windows as independent clusters.
    # Correlations between events/seasons can still invalidate this assumption.
    robust = float(np.sqrt(np.sum((a*(d-depth))**2) * len(d)/(len(d)-1))) if len(d)>1 else white
    err = max(white, robust)
    positive = np.maximum(d,0)*w
    dominance = float(positive.max()/positive.sum()) if positive.sum() else 0.
    # Reject a periodic signal sustained by a single anomalous event.
    leave = []
    if len(d)>1:
        for j in range(len(d)):
            keep = np.arange(len(d)) != j
            ww = w[keep]; aa = ww/ww.sum(); dd = d[keep]
            mu = float(aa@dd)
            se = max(float(1/np.sqrt(ww.sum())), float(np.sqrt(np.sum((aa*(dd-mu))**2)*len(dd)/(len(dd)-1))) if len(dd)>1 else 0.)
            leave.append(mu/se)
    return {'n_events': len(d), 'depth_ppm': depth*1e6, 'error_ppm': err*1e6,
            'white_error_ppm': white*1e6, 'local_snr': depth/err,
            'positive_event_fraction': float(np.mean(d>0)),
            'max_positive_depth_contribution': dominance,
            'min_leave_one_event_out_snr': float(min(leave)) if leave else None}


def vet(lc, period, epoch, duration, holdout=(), controls=64, holdout_was_unseen=False):
    if period <= 0 or duration <= 0 or duration >= period/4:
        raise ValueError('Require period>0 and 0<duration<period/4')
    ev = local_events(lc, period, epoch, duration)
    primary = combine(ev)
    odd, even = [combine([r for r in ev if r['cycle']%2 == parity]) for parity in (1,0)]
    discrepancy = None
    if odd['n_events'] and even['n_events']:
        discrepancy = abs(odd['depth_ppm']-even['depth_ppm']) / np.hypot(odd['error_ppm'],even['error_ppm'])
    secondary = combine(local_events(lc, period, epoch+period/2, duration))
    null = []
    if controls:
        offsets = (np.arange(controls)+0.5)/controls
        # Keep comparison windows away from the real primary and phase-0.5 secondary.
        offsets = offsets[(np.minimum(offsets, 1-offsets) > max(0.06,2*duration/period)) & (np.abs(offsets-.5) > max(.06,2*duration/period))]
        for o in offsets:
            c = combine(local_events(lc,period,epoch+o*period,duration,
                                     exclude_ephemeris=(period,epoch,duration)))
            if c['n_events']>=3:
                null.append({'phase':float(o),**c})
    null_depth = np.array([r['depth_ppm'] for r in null])
    control = {'n_controls': len(null), 'note':'Correlated conditional phase controls; rank is not a survey false-alarm probability.'}
    if len(null)>=10 and primary['n_events']:
        noise = mad(null_depth)
        control.update({'depth_scatter_ppm':noise,
                        'depth_over_control_scatter':primary['depth_ppm']/noise if noise>0 else None,
                        'add_one_depth_rank':float((1+np.sum(null_depth>=primary['depth_ppm']))/(1+len(null_depth)))})
    by_sector = {str(ss): combine([r for r in ev if r['sector']==ss]) for ss in sorted({r['sector'] for r in ev})}
    held = combine([r for r in ev if r['sector'] in holdout])
    train = combine([r for r in ev if r['sector'] not in holdout])
    flags = []
    if primary['n_events'] < 3: flags.append('fewer_than_three_usable_events')
    if primary.get('max_positive_depth_contribution',0) > .5: flags.append('single_event_dominance')
    if not primary['n_events']:flags.append('local_fit_unavailable')
    elif primary.get('local_snr',0) < 5: flags.append('weak_local_depth')
    if discrepancy is not None and discrepancy>3: flags.append('odd_even_discrepancy')
    if secondary.get('local_snr',0)>3: flags.append('secondary_dimming')
    if holdout and not held['n_events']:flags.append('holdout_local_fit_unavailable')
    elif holdout and held.get('local_snr',0)<3: flags.append('weak_fixed_ephemeris_holdout')
    return {'ephemeris':{'period_days':period,'epoch_btjd':epoch,'duration_hours':duration*24},
            'assessment':'Transit-like signal vetting only; no claim of planet confirmation or novelty.',
            'primary':primary,'odd':odd,'even':even,'odd_even_sigma':discrepancy,
            'secondary':secondary,'controls':control,'phase_control_measurements':null,
            'per_sector':by_sector,'events':ev,'flags':flags,
            'holdout':{'sectors':list(holdout),'status':'unseen only as declared by caller' if holdout_was_unseen else 'retrospective; not independent validation',
                       'measurement':held,'discovery_subset_measurement':train}}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('npz',type=Path);p.add_argument('--period',required=True,type=float)
    p.add_argument('--epoch',required=True,type=float);p.add_argument('--duration-hours',required=True,type=float)
    p.add_argument('--holdout-sectors',default='');p.add_argument('--holdout-was-unseen',action='store_true')
    p.add_argument('--controls',type=int,default=64);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();hold=tuple(int(x) for x in a.holdout_sectors.split(',') if x)
    result=vet(load(a.npz),a.period,a.epoch,a.duration_hours/24,hold,a.controls,a.holdout_was_unseen)
    result['source_npz']=str(a.npz.resolve())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('primary','odd_even_sigma','secondary','controls','flags','holdout')},indent=2))


if __name__=='__main__':main()
