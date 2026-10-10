"""FITS ingestion with explicit QLP flux provenance and strict uncertainty units.

QLP generations expose different corrected-flux columns. Prefer corrected
photometry and its matching error. If that error is absent, use empirical
point scatter in the selected flux's own units, never a differently normalized
column's uncertainty. All such fallbacks are recorded in returned metadata.
"""
import numpy as np

SPOC_BAD_BITS = 17087 | 8192
QLP_BAD_BITS = 1 | 4 | 8 | 16 | 32 | 128 | 1024 | 2048 | 4096 | (1 << 30)


def read_lc_fits(path, provenance):
    from astropy.io import fits
    with fits.open(path, memmap=False) as h:
        d=h[1].data
        names={s.upper():s for s in d.columns.names}
        def col(name):return np.asarray(d[names[name]],float)
        def optional(name):return col(name) if name in names else np.full(len(d),np.nan)
        t=col('TIME')
        q=col('QUALITY').astype(np.int64) if 'QUALITY' in names else np.zeros(len(t),np.int64)
        if provenance in ('SPOC','TESS-SPOC'):
            flux_col='PDCSAP_FLUX';bad=(q&SPOC_BAD_BITS)!=0
            cx,cy,bkg=[optional(n) for n in ('MOM_CENTR1','MOM_CENTR2','SAP_BKG')]
        elif provenance=='QLP':
            choices=('SYS_RM_FLUX','KSPSAP_FLUX','DET_FLUX','SAP_FLUX')
            flux_col=next((x for x in choices if x in names and np.isfinite(col(x)).sum()>=2),None)
            if flux_col is None:raise ValueError('No recognized QLP flux column')
            bad=(q&QLP_BAD_BITS)!=0
            cx,cy,bkg=[optional(n) for n in ('SAP_X','SAP_Y','SAP_BKG')]
        else:raise ValueError(f'Unsupported provenance {provenance}')
        f=col(flux_col)
        valid=~bad & np.isfinite(t) & np.isfinite(f)
        err_col=flux_col+'_ERR'
        matching_error_usable=err_col in names and np.sum(valid & np.isfinite(col(err_col)) & (col(err_col)>0))>=2
        if matching_error_usable:
            e=col(err_col);valid &= np.isfinite(e)&(e>0)
            error_source=err_col
        else:
            # Sorting protects the point-noise estimate if a product is unordered.
            idx=np.flatnonzero(valid);idx=idx[np.argsort(t[idx])]
            diff=np.diff(f[idx]);noise=1.4826*np.median(np.abs(diff-np.median(diff)))/np.sqrt(2) if len(diff)>1 else np.nan
            if not np.isfinite(noise) or noise<=0:raise ValueError('Cannot estimate missing flux uncertainty')
            e=np.full(len(t),noise);error_source='empirical_point_scatter_in_selected_flux_units'
        if valid.sum()<2:raise ValueError('Fewer than two usable points after quality/finite/error filtering')
        med=float(np.median(f[valid]))
        if not np.isfinite(med) or med<=0:raise ValueError('Non-positive or invalid median flux')
        # TIMEDEL is in days. Fall back to time spacing only when headers omit it.
        exptime=float(h[1].header.get('TIMEDEL',h[0].header.get('TIMEDEL',np.nan)))*86400
        exposure_source='TIMEDEL'
        if not np.isfinite(exptime) or exptime<=0:
            spacing=np.diff(np.sort(t[valid]));spacing=spacing[spacing>0]
            exptime=float(np.median(spacing))*86400 if len(spacing) else np.nan
            exposure_source='median_time_spacing'
        if not np.isfinite(exptime) or exptime<=0:raise ValueError('No positive exposure/cadence estimate')
        return {'time':t[valid],'flux':(f[valid]/med).astype(np.float64),
                'flux_err':(e[valid]/med).astype(np.float64),'cx':cx[valid],
                'cy':cy[valid],'bkg':bkg[valid],
                'camera':int(h[0].header.get('CAMERA',-1) or -1),
                'ccd':int(h[0].header.get('CCD',-1) or -1),'exptime':exptime,
                'flux_column':flux_col,'error_source':error_source,
                'exposure_source':exposure_source,'raw_flux_fallback':flux_col=='SAP_FLUX',
                'quality_column_missing':'QUALITY' not in names}
