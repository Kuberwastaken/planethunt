import unittest
import numpy as np
from broad_signal_vet import events
from independent_vet import combine


def data(kind):
    t=np.arange(0,30,5/1440);P=.43;t0=.123;D=.095
    ph=(t-t0+P/2)%P-P/2;ex=5/1440
    box=np.maximum(0,np.minimum(ph+ex/2,D/2)-np.maximum(ph-ex/2,-D/2))/ex
    signal=-.0003*box if kind=='box' else -.00015*np.cos(2*np.pi*ph/P)
    f=1+.0004*np.sin(t/5)+signal+np.random.default_rng(300).normal(0,.0002,len(t))
    lc={'time':t,'flux':f,'flux_err':np.full(len(t),.0002),'sector':np.ones(len(t),int),'exptime':np.full(len(t),300.)}
    return lc,P,t0,D


class BroadTests(unittest.TestCase):
    def test_true_broad_box_survives_quadratic_baseline(self):
        lc,P,t0,D=data('box')
        for hf in (.35,.4):
            for degree in (1,2):
                r=combine(events(lc,P,t0,D,hf,degree))
                self.assertAlmostEqual(r['depth_ppm'],300,delta=45)
                self.assertGreater(r['local_snr'],8)
    def test_smooth_modulation_is_baseline_sensitive(self):
        lc,P,t0,D=data('sinusoid')
        linear=combine(events(lc,P,t0,D,.4,1))
        quadratic=combine(events(lc,P,t0,D,.4,2))
        self.assertLess(abs(quadratic['depth_ppm']),.5*linear['depth_ppm'])


if __name__=='__main__':unittest.main()
