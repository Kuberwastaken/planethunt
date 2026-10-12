from pathlib import Path
import numpy as np, json
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.utils import iers
import astropy.units as u
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).parent
O = P / "ztf_results"
O.mkdir(exist_ok=True)
iers.conf.auto_download = False
z = Table.read(P / "ztf_dr24_lightcurves.body", format="ascii.csv")
z = z[
    (z["catflags"] == 0)
    & np.isfinite(z["mag"])
    & np.isfinite(z["magerr"])
    & (z["magerr"] > 0)
]
loc = EarthLocation.from_geodetic(-116.8648 * u.deg, 33.3563 * u.deg, 1706 * u.m)
t = Time(np.array(z["mjd"]), format="mjd", scale="utc", location=loc)
coord = SkyCoord(285.907827 * u.deg, 40.941988 * u.deg)
bjd = (t.tdb + t.light_travel_time(coord)).jd
T0 = 2455630.245430646
PER = 13.769448251493595
half = 1.15 / 24
# An independent baseline for each object ID and 100-day segment.
keys = np.array([str(a) + "_" + str(int(b // 100)) for a, b in zip(z["oid"], z["mjd"])])
seasons = np.unique(keys)
base = np.column_stack([keys == k for k in seasons]).astype(float)
mag = np.array(z["mag"])
err = np.array(z["magerr"])
med = np.median(mag)
flux = 10 ** (-0.4 * (mag - med))
ferr = flux * err * np.log(10) * 0.4


# Work in magnitudes so instrumental offsets remain additive.
def fit(offset=0, band=None):
    phase = (bjd - T0 - offset + PER / 2) % PER - PER / 2
    inside = abs(phase) < half
    use = np.ones(len(z), bool) if band is None else np.array(z["filtercode"]) == band
    # Baseline clipping does not remove any possible transit measurements.
    for k in seasons:
        m = (keys == k) & use
        out = m & ~inside
        if out.sum() < 10:
            use[m] = False
            continue
        v = mag[out]
        mu = np.median(v)
        sig = max(1.4826 * np.median(abs(v - mu)), np.median(err[out]))
        use &= inside | ~(m & (abs(mag - mu) > 5 * sig))
    X = np.column_stack([base, inside.astype(float)])[use]
    nonempty = np.any(X != 0, axis=0)
    X = X[:, nonempty]
    y = mag[use]
    e = err[use]
    if inside[use].sum() < 2:
        return None
    A = X / e[:, None]
    coef = np.linalg.lstsq(A, y / e, rcond=None)[0]
    cov = np.linalg.pinv(A.T @ A)
    res = y - X @ coef
    infl = max(1.0, float(np.sqrt(np.sum((res / e) ** 2) / (len(y) - X.shape[1]))))
    dm = float(coef[-1])
    dmerr = float(np.sqrt(cov[-1, -1]) * infl)
    return dict(
        depth_ppm=float((1 - 10 ** (-0.4 * dm)) * 1e6),
        error_ppm=float(np.log(10) * 0.4 * 10 ** (-0.4 * dm) * dmerr * 1e6),
        n_in=int(inside[use].sum()),
        n_used=int(use.sum()),
        noise_inflation=infl,
        delta_mag=dm,
    )


summary = {}
for band in [None, "zg", "zr"]:
    key = band or "combined"
    s = fit(band=band)
    cs = [
        dict(offset_days=float(off), **r)
        for off in np.linspace(0.35, PER - 0.35, 80)
        if (r := fit(float(off), band)) is not None
    ]
    s["control_depth_std_ppm"] = float(np.std([r["depth_ppm"] for r in cs], ddof=1))
    s["controls"] = cs
    summary[key] = s
(O / "summary.json").write_text(json.dumps(summary, indent=2))
z["bjd_tdb"] = bjd
z.write(O / "quality0_photometry.csv", format="ascii.csv", overwrite=True)
fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
phase = ((bjd - T0 + PER / 2) % PER - PER / 2) * 24
res = mag.copy()
for k in seasons:
    m = keys == k
    res[m] -= np.median(mag[m])
ax.scatter(phase, res * 1000, s=5, alpha=0.4, color="gray")
ax.axvspan(-1.15, 1.15, color="lightblue")
ax.set(
    xlim=(-6, 6),
    ylim=(-100, 100),
    xlabel="Hours from Kepler-predicted transit",
    ylabel="Magnitude residual (mmag)",
    title="ZTF DR24 · target · per-source / 100-day baseline",
)
ax.invert_yaxis()
fig.savefig(O / "ztf_fixed_ephemeris.png", dpi=160)
for k, s in summary.items():
    print(k, {a: b for a, b in s.items() if a != "controls"})
