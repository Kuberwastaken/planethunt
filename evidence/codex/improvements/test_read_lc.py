import io
import unittest
import numpy as np
from astropy.io import fits
from read_lc import read_lc_fits


def make_product(fluxes, timedel=True):
    n=200
    cols=[fits.Column(name='TIME',array=np.arange(n)/720,format='D'),
          fits.Column(name='QUALITY',array=np.zeros(n,dtype=int),format='J')]
    cols += [fits.Column(name=k,array=np.asarray(v),format='D') for k,v in fluxes.items()]
    table=fits.BinTableHDU.from_columns(cols)
    if timedel:table.header['TIMEDEL']=1/720
    buf=io.BytesIO();fits.HDUList([fits.PrimaryHDU(),table]).writeto(buf);buf.seek(0)
    return buf


class ParserTests(unittest.TestCase):
    def test_legacy_corrected_flux_and_matching_error(self):
        phase=np.arange(200)
        z=read_lc_fits(make_product({'SAP_FLUX':1000+phase,'KSPSAP_FLUX':1000+np.sin(phase),
                                    'KSPSAP_FLUX_ERR':np.full(200,2.)}),'QLP')
        self.assertEqual(z['flux_column'],'KSPSAP_FLUX')
        self.assertLess(np.std(z['flux']),.001)
        self.assertEqual(z['error_source'],'KSPSAP_FLUX_ERR')
    def test_modern_corrected_flux_no_mismatched_error(self):
        z=read_lc_fits(make_product({'SYS_RM_FLUX':1+.001*np.sin(np.arange(200)),
                                    'DET_FLUX_ERR':np.full(200,1000.)}),'QLP')
        self.assertEqual(z['flux_column'],'SYS_RM_FLUX')
        self.assertTrue(z['error_source'].startswith('empirical'))
        self.assertLess(np.max(z['flux_err']),.01)
    def test_cadence_fallback_and_missing_centroid(self):
        z=read_lc_fits(make_product({'DET_FLUX':100+np.sin(np.arange(200)),
                                    'DET_FLUX_ERR':np.ones(200)},False),'QLP')
        self.assertAlmostEqual(z['exptime'],120)
        self.assertTrue(np.isnan(z['cx']).all())
    def test_raw_fallback_is_explicit(self):
        z=read_lc_fits(make_product({'SAP_FLUX':100+np.sin(np.arange(200)),
                                    'SAP_FLUX_ERR':np.ones(200)}),'QLP')
        self.assertTrue(z['raw_flux_fallback'])
    def test_entire_error_column_missing_values(self):
        z=read_lc_fits(make_product({'DET_FLUX':1+.001*np.sin(np.arange(200)),
                                    'DET_FLUX_ERR':np.full(200,np.nan)}),'QLP')
        self.assertEqual(len(z['time']),200)
        self.assertTrue(z['error_source'].startswith('empirical'))


if __name__=='__main__':unittest.main()
