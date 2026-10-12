"""Early WISE photometry/timing screen; no transit or multiplicity inference."""

from pathlib import Path
import json
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.utils import iers
import astropy.units as u

P = Path(__file__).parent
iers.conf.auto_download = False
out = {}
coord = SkyCoord(285.907827 * u.deg, 40.941988 * u.deg)
for n in ["allsky_4band_p1bs_psd", "allsky_2band_p1bs_psd"]:
    z = Table.read(P / f"wise_{n}.body", format="ascii.ipac")
    t = Time(
        np.asarray(z["mjd"]),
        format="mjd",
        scale="utc",
        location=EarthLocation.from_geocentric(0, 0, 0, unit="m"),
    )
    b = (t.tdb + t.light_travel_time(coord)).jd
    phase = (
        (b - 2455630.245430646 + 13.769448251493595 / 2) % 13.769448251493595
        - 13.769448251493595 / 2
    ) * 24
    result = {
        "n_all": len(z),
        "mjd_min": float(min(z["mjd"])),
        "mjd_max": float(max(z["mjd"])),
        "bands": {},
    }
    for band in [1, 2]:
        m = np.asarray(np.ma.filled(z[f"w{band}mpro"], np.nan), float)
        e = np.asarray(np.ma.filled(z[f"w{band}sigmpro"], np.nan), float)
        good = (
            np.isfinite(m)
            & np.isfinite(e)
            & (e > 0)
            & np.array([str(f)[band - 1] == "0" for f in z["cc_flags"]])
            & np.array([str(f)[band - 1] in "AB" for f in z["ph_qual"]])
        )
        result["bands"][f"W{band}"] = {
            "n_good": int(good.sum()),
            "n_in": int(sum(good & (abs(phase) < 1.15))),
            "median_mag": float(np.median(m[good])),
            "median_error_mag": float(np.median(e[good])),
            "closest_midpoint_hours": float(min(abs(phase[good]))),
        }
    out[n] = result
z = Table.read(P / "wise_allwise_p3as_psd.body", format="ascii.ipac")[0]
out["allwise_source"] = {
    k: (
        None
        if np.ma.is_masked(z[k])
        else str(z[k])
        if k in ["designation", "cc_flags", "ph_qual"]
        else float(z[k])
    )
    for k in [
        "designation",
        "ra",
        "dec",
        "dist",
        "w1mpro",
        "w1sigmpro",
        "w2mpro",
        "w2sigmpro",
        "w3mpro",
        "w3sigmpro",
        "w4mpro",
        "w4sigmpro",
        "cc_flags",
        "ph_qual",
    ]
}
(P / "early_wise_summary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
