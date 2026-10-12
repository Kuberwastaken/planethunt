"""Time coverage of browser-exported SPHEREx image footprints (not detections)."""

from pathlib import Path
import json
import numpy as np
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.utils import iers
import astropy.units as u

P = Path(__file__).resolve().parent
iers.conf.auto_download = False
t = Table.read(P / "planethunt-spherex-288-images.tbl", format="ascii.ipac")
time = Time(
    np.asarray(t["t_min"]),
    format="mjd",
    scale="utc",
    location=EarthLocation.from_geocentric(0, 0, 0, unit="m"),
)
bjd = (
    time.tdb + time.light_travel_time(SkyCoord(285.907827 * u.deg, 40.941988 * u.deg))
).jd
phase = (
    (bjd - 2455630.245430646 + 13.769448251493595 / 2) % 13.769448251493595
    - 13.769448251493595 / 2
) * 24
out = dict(
    n_images=len(t),
    date_min=Time(min(t["t_min"]), format="mjd").isot,
    date_max=Time(max(t["t_max"]), format="mjd").isot,
    in_nominal_window=int(sum(abs(phase) < 1.15)),
    closest_midpoint_hours=float(min(abs(phase))),
    timing="Approximate geocentric correction; SPHEREx orbit not included. Image footprint intersecting cone is not guaranteed target coverage.",
)
(P / "spherex_inventory_summary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
