"""Conditional pixel-level PRF injection into saved TESS cutouts.

This tests fixed-aperture dilution/response, not calibrated survey completeness.
The local estimator is the same implementation as analyze_tglc.py.
"""

from pathlib import Path
import json, sys
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from photutils.aperture import CircularAperture

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P / "prf_models"))
from prf import TESS_PRF

O = P / "pixel_injection_results"
O.mkdir(exist_ok=True)
INPUT = P.parent / "archive-followup-20261012/tess"
T0 = -1369.7545693539214
PER = 13.769448251493595
HALF = 1.15 / 24
RADII = [1.0, 1.5, 2.0]
series = []


def measure(offset=0.0, radius_idx=1, inject_ppm=0.0, collect=False):
    rows = []
    fold = []
    for sector, t, mf, cadence in series:
        flux = mf[radius_idx].copy()
        if inject_ppm:
            truephase = (t - T0 + PER / 2) % PER - PER / 2
            flux *= 1 - inject_ppm / 1e6 * (abs(truephase) < HALF)
        for epoch in range(
            int(np.floor((t.min() - T0 - offset) / PER)),
            int(np.ceil((t.max() - T0 - offset) / PER)) + 1,
        ):
            mid = T0 + epoch * PER + offset
            dt = t - mid
            inside = abs(dt) < HALF
            local = abs(dt) < 0.5
            out = local & (abs(dt) > 0.12)
            if (
                inside.sum() < max(3, int(0.5 * 2 * HALF / cadence))
                or np.sum(out & (dt < 0)) < 5
                or np.sum(out & (dt > 0)) < 5
            ):
                continue
            # Reject outlying baseline samples only; never clip an in-transit point.
            for _ in range(3):
                X = np.column_stack([np.ones(out.sum()), dt[out]])
                coef = np.linalg.lstsq(X, flux[out], rcond=None)[0]
                res = flux - (coef[0] + coef[1] * dt)
                scatter = 1.4826 * np.median(abs(res[out] - np.median(res[out])))
                out &= abs(res) < 5 * scatter
            X = np.column_stack([np.ones(out.sum()), dt[out]])
            coef = np.linalg.lstsq(X, flux[out], rcond=None)[0]
            base = coef[0] + coef[1] * dt
            res = flux - base
            scatter = float(np.std(res[out], ddof=2))
            if coef[0] <= 0 or not np.isfinite(scatter) or scatter <= 0:
                continue
            depth = -np.mean(res[inside]) / coef[0] * 1e6
            predictor = np.array([1, np.mean(dt[inside])])
            baselinevar = scatter**2 * predictor @ np.linalg.inv(X.T @ X) @ predictor
            # Thirty-minute residual bins estimate correlated noise; use a floor of 1.
            bids = np.floor((dt + 0.5) / (30 / 1440)).astype(int)
            br = []
            bn = []
            for b in np.unique(bids[out]):
                sel = out & (bids == b)
                if sel.sum() >= 2:
                    br.append(np.mean(res[sel]))
                    bn.append(sel.sum())
            beta = (
                max(1.0, float(np.std(br, ddof=1) / (scatter / np.sqrt(np.median(bn)))))
                if len(br) > 3
                else 1.0
            )
            error = (
                np.sqrt(scatter**2 / inside.sum() + baselinevar) / coef[0] * 1e6 * beta
            )
            row = dict(
                sector=sector,
                epoch=epoch,
                mid_btjd=mid,
                aperture_radius=RADII[radius_idx],
                depth_ppm=float(depth),
                error_ppm=float(error),
                n_in=int(inside.sum()),
                n_baseline=int(out.sum()),
                beta_30min=beta,
            )
            rows.append(row)
            if collect:
                for a, b in zip(dt[local] * 24, res[local] / coef[0] * 1e6):
                    fold.append((float(a), float(b)))
    if not rows:
        return None, [], []
    ds = np.array([r["depth_ppm"] for r in rows])
    es = np.array([r["error_ppm"] for r in rows])
    weights = 1 / es**2
    depth = float(np.sum(weights * ds) / weights.sum())
    infl = max(
        1.0, float(np.sqrt(np.sum(weights * (ds - depth) ** 2) / max(1, len(ds) - 1)))
    )
    error = float(1 / np.sqrt(weights.sum()) * infl)
    return (
        dict(
            depth_ppm=depth,
            error_ppm=error,
            depth_over_error=depth / error,
            n_events=len(rows),
            between_event_error_inflation=infl,
        ),
        rows,
        fold,
    )


# TGLC catalogue magnitudes, converted with the TESS 20.44 zero point.
# Treat flux normalisation as an assumption; test 0.5x and 2x as well.
ids = [2103792461826460288, 2103792427466721792]
gaia = Table.read(P / "gaia_field.body", format="ascii.csv")
configs = json.loads((P / "prf_models/sectors.json").read_text())
raw = []
meta = []
for cfg in configs:
    s = cfg["sector"]
    f = next((INPUT / "frames").glob(f"tess-s{s:04d}-*astrocut.fits.gz"))
    with fits.open(f) as h:
        t = np.array(h[1].data["TIME"], float)
        cube = np.array(h[1].data["FLUX"], float)
        er = np.array(h[1].data["FLUX_ERR"], float)
        q = h[1].data["QUALITY"]
        w = WCS(h[2].header)
    good = (
        (q == 0)
        & np.isfinite(t)
        & np.all(np.isfinite(cube), axis=(1, 2))
        & np.all(np.isfinite(er), axis=(1, 2))
    )
    t, cube = t[good], cube[good]
    z = np.load(INPUT / "results" / f"sector{s}_apertures.npz")
    assert np.allclose(t, z["time_btjd"])
    xy = z["target_neighbour_xy"]
    sky = z["sky_mask"]
    baseline = z["flux_e_s"]
    cad = float(np.median(np.diff(t)))
    masks = np.array(
        [
            CircularAperture(xy[0], r).to_mask(method="exact").to_image((9, 9))
            for r in RADII
        ]
    )
    model = TESS_PRF(
        cfg["cam"],
        cfg["ccd"],
        s,
        cfg["col"],
        cfg["row"],
        localdatadir=str(P / "prf_models"),
    )
    # Propagate Gaia DR3 positions from 2016.0 to the approximate sector epoch.
    year = 2000 + (np.median(t) + 2457000 - 2451545) / 365.25
    positions = []
    patterns = []
    for gid in ids:
        g = gaia[np.asarray(gaia["source_id"]) == gid][0]
        ra = float(g["ra"]) + float(g["pmra"]) * (year - 2016) / 3.6e6 / np.cos(
            np.deg2rad(float(g["dec"]))
        )
        dec = float(g["dec"]) + float(g["pmdec"]) * (year - 2016) / 3.6e6
        pos = w.all_world2pix([[ra, dec]], 0)[0]
        positions.append(pos.tolist())
        patterns.append(model.locate(*pos, stampsize=(9, 9)))
    patterns = np.array(patterns)
    # Compare PRF templates after removing their mean: unresolved pair degeneracy.
    corr = float(np.corrcoef(patterns.reshape(2, -1))[0, 1])
    meta.append(
        dict(
            sector=s,
            prf_template_correlation=corr,
            positions_xy=positions,
            stamp_flux_fractions=patterns.sum(axis=(1, 2)).tolist(),
            aperture_flux_fractions=[
                [float(np.sum(p * m)) for m in masks] for p in patterns
            ],
        )
    )
    raw.append((s, t, cube, sky, masks, baseline, cad, patterns))
print("Loaded", len(raw), "sectors", flush=True)


def get_series(offset, source=None, scale=1.0):
    out = []
    for s, t, cube, sky, masks, base, cad, patterns in raw:
        mf = base.copy()
        if source is not None:
            phase = (t - T0 - offset + PER / 2) % PER - PER / 2
            # Integrate a 2.3-hour box over each cadence exposure.
            overlap = (
                np.maximum(
                    0,
                    np.minimum(phase + cad / 2, HALF)
                    - np.maximum(phase - cad / 2, -HALF),
                )
                / cad
            )
            hit = overlap > 0
            flux = (
                10 ** ((20.44 - [15.29787283143992, 14.99963949026414][source]) / 2.5)
                * scale
            )
            altered = (
                cube[hit] - overlap[hit, None, None] * 0.0024 * flux * patterns[source]
            )
            bg = np.median(altered[:, sky], axis=1)
            for i, m in enumerate(masks):
                mf[i, hit] = np.sum((altered - bg[:, None, None]) * m, axis=(1, 2))
        out.append((s, t, mf, cad))
    return out


summary = {
    "assumed_intrinsic_depth_ppm": 2400,
    "assumed_tess_zeropoint": 20.44,
    "sectors": meta,
    "nominal": [],
    "phase_trials": [],
}
series = get_series(0)
base = [measure(radius_idx=i)[0] for i in range(3)]
for source in [0, 1]:
    for scale in [0.5, 1.0, 2.0]:
        series = get_series(0, source, scale)
        for i, r in enumerate(RADII):
            fit = measure(radius_idx=i)[0]
            summary["nominal"].append(
                dict(
                    source=["target", "neighbour"][source],
                    flux_scale=scale,
                    radius=r,
                    baseline=base[i],
                    injected=fit,
                    increment_ppm=fit["depth_ppm"] - base[i]["depth_ppm"],
                )
            )
# Off-phase trials preserve measured noise and rerun background/aperture extraction.
# A 3-sigma count here is descriptive only (not a false-alarm-calibrated recovery rate).
for off in np.linspace(0.4, PER - 0.4, 24):
    series = get_series(float(off))
    b = measure(offset=float(off), radius_idx=1)[0]
    series = get_series(float(off), 0, 1)
    r = measure(offset=float(off), radius_idx=1)[0]
    if b and r:
        summary["phase_trials"].append(
            dict(
                offset_days=float(off),
                baseline=b,
                injected=r,
                increment_ppm=r["depth_ppm"] - b["depth_ppm"],
            )
        )
tr = summary["phase_trials"]
summary["phase_summary"] = dict(
    n=len(tr),
    median_increment_ppm=float(np.median([r["increment_ppm"] for r in tr])),
    std_uninjected_depth_ppm=float(
        np.std([r["baseline"]["depth_ppm"] for r in tr], ddof=1)
    ),
    positive_3sigma_trials=int(sum(r["injected"]["depth_over_error"] >= 3 for r in tr)),
)
(O / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary["phase_summary"], indent=2))
for r in summary["nominal"]:
    if r["source"] == "target" and r["flux_scale"] == 1:
        print("target nominal", r["radius"], r["increment_ppm"])
print(
    "template correlations",
    [(r["sector"], round(r["prf_template_correlation"], 4)) for r in meta],
)

# Plot the measured noise alongside the conditional source injection.
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
x = np.array([r["offset_days"] for r in tr])
b = np.array([r["baseline"]["depth_ppm"] for r in tr])
a = np.array([r["injected"]["depth_ppm"] for r in tr])
axes[0].scatter(x, b, label="Original pixels", color="gray", s=24)
axes[0].scatter(x, a, label="+ 2,400 ppm dip on target", color="tab:blue", s=24)
for xx, yy, zz in zip(x, b, a):
    axes[0].plot([xx, xx], [yy, zz], color="lightgray", lw=1, zorder=0)
axes[0].axhline(0, color="black", lw=0.7)
axes[0].set(
    xlabel="Offset from Kepler ephemeris (days)",
    ylabel="Recovered aperture depth (ppm)",
    title="Real TESS noise remains after injection",
)
axes[0].legend(fontsize=8)
for src, col in [("target", "tab:blue"), ("neighbour", "gray")]:
    rows = [
        r for r in summary["nominal"] if r["source"] == src and r["flux_scale"] == 1
    ]
    axes[1].plot(
        [r["radius"] for r in rows],
        [r["increment_ppm"] for r in rows],
        "o-",
        label=src,
        color=col,
    )
axes[1].axhline(2400, color="black", ls=":", label="Intrinsic injected depth")
axes[1].set(
    xlabel="Aperture radius (pixels)",
    ylabel="Increment in aperture depth (ppm)",
    title="Dilution depends on aperture and assumed host",
)
axes[1].legend(fontsize=8)
fig.savefig(O / "conditional_injection.png", dpi=160)
plt.close(fig)
