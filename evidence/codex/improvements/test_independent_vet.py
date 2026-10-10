"""Synthetic behavior tests: true repeating transit, EB, and one-event glitch."""
import unittest
import numpy as np
from independent_vet import vet


def synthetic(mode='planet', seed=812):
    rng=np.random.default_rng(seed)
    t=np.arange(0,54,1/144); period=3.;epoch=1.;duration=.1
    cycle=np.rint((t-epoch)/period).astype(int)
    phase=(t-epoch+period/2)%period-period/2
    hit=np.abs(phase)<duration/2
    depth=np.full(len(t),.002)
    if mode=='binary':depth=np.where(cycle%2,.001,.004)
    if mode=='glitch':depth=np.where(cycle==3,.02,0.)
    f=1+0.0004*np.sin(t*2*np.pi/8)+rng.normal(0,.0005,len(t))-depth*hit
    lc={'time':t,'flux':f,'flux_err':np.full(len(t),.0005),
        'sector':np.where(t<27,1,2),'exptime':np.full(len(t),600.)}
    return vet(lc,period,epoch,duration,holdout=(2,),controls=12,holdout_was_unseen=True)


class VetTests(unittest.TestCase):
    def test_transit_recovery_and_fixed_holdout(self):
        r=synthetic()
        self.assertGreater(r['primary']['local_snr'],10)
        self.assertAlmostEqual(r['primary']['depth_ppm'],2000,delta=250)
        self.assertGreater(r['holdout']['measurement']['local_snr'],8)
        self.assertLess(r['odd_even_sigma'],3)
    def test_alternating_binary(self):
        self.assertIn('odd_even_discrepancy',synthetic('binary')['flags'])
    def test_single_event_glitch(self):
        r=synthetic('glitch')
        self.assertIn('single_event_dominance',r['flags'])
        self.assertLess(r['primary']['min_leave_one_event_out_snr'],3)


if __name__=='__main__':unittest.main()
