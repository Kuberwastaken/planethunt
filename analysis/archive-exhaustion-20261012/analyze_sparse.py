"""Timing and precision screen for sparse PTF / blended NEOWISE photometry."""

from pathlib import Path
import json
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.utils import iers
import astropy.units as u

iers.conf.auto_download = False
P = Path(__file__).parent
C = SkyCoord(285.907827 * u.deg, 40.941988 * u.deg)
PER = 13.769448251493595
T0 = 2455630.245430646


def phase(mjd, location):
    t = Time(np.array(mjd, float), format="mjd", scale="utc", location=location)
    b = (t.tdb + t.light_travel_time(C)).jd
    return ((b - T0 + PER / 2) % PER - PER / 2) * 24


t = Table.read(P / "ptf_lightcurves.body", format="votable")
h = phase(
    t["obsmjd"],
    EarthLocation.from_geodetic(-116.8648 * u.deg, 33.3563 * u.deg, 1706 * u.m),
)
r = dict(
    n_measurements=len(t),
    n_inside_2p3h=int((abs(h) < 1.15).sum()),
    nearest_midtransit_hours=float(min(abs(h))),
    median_magnitude_error=float(np.median(np.array(t["magerr_auto"]))),
    mjd_span=[float(min(t["obsmjd"])), float(max(t["obsmjd"]))],
)
(P / "ptf_summary.json").write_text(json.dumps(r, indent=2))
z = Table.read(P / "neowiser_p1bs_psd.body", format="votable")
h = phase(z["mjd"], EarthLocation.from_geocentric(0, 0, 0, u.m))
r = dict(
    n_total=len(z),
    note="Geocentric barycentric correction; satellite position unavailable (<0.03 s impact). Broad WISE PSF: nearby-star blending remains.",
)
for band in ["w1", "w2"]:
    m = np.ma.filled(z[band + "mpro"], np.nan)
    e = np.ma.filled(z[band + "sigmpro"], np.nan)
    ok = (
        np.isfinite(m)
        & np.isfinite(e)
        & (e > 0)
        & (np.array(z["qual_frame"]) >= 5)
        & np.array([str(c)[int(band[-1]) - 1] == "0" for c in z["cc_flags"]])
    )
    inside = abs(h) < 1.15
    v = m[ok]
    r[band] = dict(
        n_quality=int(ok.sum()),
        n_inside=int((ok & inside).sum()),
        median_magnitude=float(np.median(v)),
        median_error_mag=float(np.median(e[ok])),
        robust_scatter_mag=float(1.4826 * np.median(abs(v - np.median(v)))),
    )
    if np.sum(ok & inside):
        r[band].update(
            global_baseline_delta_mag=float(
                np.average(m[ok & inside], weights=1 / e[ok & inside] ** 2)
                - np.average(m[ok & ~inside], weights=1 / e[ok & ~inside] ** 2)
            ),
            formal_error_mag=float(
                np.sqrt(
                    1 / np.sum(1 / e[ok & inside] ** 2)
                    + 1 / np.sum(1 / e[ok & ~inside] ** 2)
                )
            ),
        )
(P / "neowise_summary.json").write_text(json.dumps(r, indent=2))
