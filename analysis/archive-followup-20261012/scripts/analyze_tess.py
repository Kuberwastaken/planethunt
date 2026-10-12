"""Exploratory fixed-ephemeris TESS aperture check; no deblending or validation.

Quality=0; three fixed circular apertures; local linear baselines outside transit.
Uncertainties and phase controls are diagnostic, not planet probabilities.
"""

import argparse, json, csv, warnings
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from photutils.aperture import CircularAperture
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument(
    "--data", type=Path, default=Path(__file__).resolve().parents[1] / "tess" / "frames"
)
ap.add_argument("--out", type=Path)
ap.add_argument(
    "--ephemeris",
    type=Path,
    default=Path(__file__).resolve().parents[1] / "spitzer/kfit_psf.json",
)
args = ap.parse_args()
P = args.data
O = args.out or P.parent / "results"
O.mkdir(parents=True, exist_ok=True)
eph = json.loads(args.ephemeris.read_text())
T0 = eph["T0_btjd"][0]
PER = eph["P"][0]
HALF = 1.15 / 24
RADII = [1.0, 1.5, 2.0]
coords = [[285.907827, 40.941988], [285.90521895334, 40.94207048408]]
series = []
meta = []
events = []
sectors = []
nfiles = len(list(P.glob("*astrocut.fits.gz")))
nrows = int(np.ceil(nfiles / 5))
fig, axes = plt.subplots(
    nrows, 5, figsize=(15, 3 * nrows), layout="constrained", squeeze=False
)
for f in sorted(P.glob("*astrocut.fits.gz")):
    with fits.open(f) as hd:
        d = hd[1].data
        t = np.array(d["TIME"], float)
        cube = np.array(d["FLUX"], float)
        err = np.array(d["FLUX_ERR"], float)
        quality = np.array(d["QUALITY"])
        sector = int(hd[0].header["SECTOR"])
        w = WCS(hd[2].header)
    good = (
        (quality == 0)
        & np.isfinite(t)
        & np.all(np.isfinite(cube), axis=(1, 2))
        & np.all(np.isfinite(err), axis=(1, 2))
    )
    t, cube, err = t[good], cube[good], err[good]
    if len(t) == 0:
        raise ValueError(f"No usable data: {f}")
    xy = w.all_world2pix(coords, 0)
    y, x = np.indices(cube.shape[1:])
    rr = np.hypot(x - xy[0, 0], y - xy[0, 1])
    med = np.median(cube, axis=0)
    outer = rr > 3.2
    sky = outer & (med <= np.percentile(med[outer], 60))
    background = np.median(cube[:, sky], axis=1)
    mf = []
    fe = []
    for radius in RADII:
        mask = (
            CircularAperture(xy[0], radius).to_mask(method="exact").to_image(med.shape)
        )
        flux = np.sum((cube - background[:, None, None]) * mask, axis=(1, 2))
        sigma = np.sqrt(np.sum((err * mask) ** 2, axis=(1, 2)))
        mf.append(flux)
        fe.append(sigma)
    mf = np.array(mf)
    fe = np.array(fe)
    np.savez_compressed(
        O / f"sector{sector}_apertures.npz",
        time_btjd=t,
        flux_e_s=mf,
        formal_error_e_s=fe,
        radii_pixels=RADII,
        background_e_s=background,
        median_image=med,
        target_neighbour_xy=xy,
        sky_mask=sky,
    )
    cadence = float(np.median(np.diff(t)))
    row = dict(
        sector=sector,
        n_total=len(quality),
        n_quality0_finite=len(t),
        cadence_minutes=cadence * 1440,
        time_min_btjd=float(t.min()),
        time_max_btjd=float(t.max()),
        target_neighbour_separation_pixels=float(np.linalg.norm(xy[1] - xy[0])),
        median_aperture_flux_e_s=np.median(mf, axis=1).tolist(),
    )
    meta.append(row)
    series.append((sector, t, mf, cadence))
    sectors.append(sector)
    ax = axes.flat[len(meta) - 1]
    ax.imshow(np.arcsinh(med / np.nanmedian(med)), origin="lower", cmap="magma")
    ax.scatter(*xy.T, facecolors="none", edgecolors=["cyan", "lime"], s=75)
    ax.add_patch(plt.Circle(xy[0], 1.5, fill=False, color="white", lw=1))
    ax.set_title(f"Sector {sector} · {cadence * 1440:.1f} min")
    ax.set_xticks([])
    ax.set_yticks([])
for ax in axes.flat[len(meta) :]:
    ax.set_axis_off()
fig.suptitle(
    "TESS median pixel images · cyan: target · green: 7.1″ neighbour\nWhite: fixed 1.5-pixel aperture; the close pair is unresolved",
    fontsize=12,
)
fig.savefig(O / "tess_pixels.png", dpi=160)
plt.close(fig)


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


summary = {}
all_events = []
for i, radius in enumerate(RADII):
    s, rows, fold = measure(radius_idx=i, collect=True)
    all_events += rows
    controls = []
    for off in np.linspace(0.35, PER - 0.35, 80):
        c, _, _ = measure(offset=float(off), radius_idx=i)
        if c:
            controls.append(dict(offset_days=float(off), **c))
    cdepth = np.array([c["depth_ppm"] for c in controls])
    s["control_depth_std_ppm"] = float(np.std(cdepth, ddof=1))
    s["control_median_depth_ppm"] = float(np.median(cdepth))
    s["control_fraction_at_least_as_deep"] = float(np.mean(cdepth >= s["depth_ppm"]))
    s["injection_checks"] = []
    for dep in [500, 1000, 2400]:
        inj, _, _ = measure(radius_idx=i, inject_ppm=dep)
        s["injection_checks"].append(
            dict(
                injected_aperture_ppm=dep,
                increment_recovered_ppm=inj["depth_ppm"] - s["depth_ppm"],
            )
        )
    # Inspect timing sensitivity without optimizing/replacing the ephemeris.
    s["timing_offsets"] = [
        dict(offset_minutes=off, result=measure(offset=off / 1440, radius_idx=i)[0])
        for off in [-60, -30, 0, 30, 60]
    ]
    summary[str(radius)] = s
    (O / f"phase_controls_r{radius}.json").write_text(json.dumps(controls, indent=2))
    if radius == 1.5:
        fold = np.array(fold)
        fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
        bins = np.arange(-8, 8.01, 0.5)
        xx = []
        yy = []
        ee = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            v = fold[(fold[:, 0] >= lo) & (fold[:, 0] < hi), 1]
            if len(v) > 3:
                xx.append((lo + hi) / 2)
                yy.append(np.mean(v))
                ee.append(np.std(v, ddof=1) / np.sqrt(len(v)))
        ax.errorbar(xx, yy, yerr=ee, fmt=".", color="black", capsize=2)
        ax.axhline(0, color=".6", lw=1)
        ax.axvspan(-1.15, 1.15, color=".8", alpha=0.4)
        ax.set(
            xlabel="Hours from the Kepler-predicted transit",
            ylabel="Blended-aperture residual (ppm)",
            title="TESS · 1.5-pixel aperture · fixed Kepler ephemeris\n30-minute bins; local linear baselines; no dilution correction",
            xlim=(-8, 8),
        )
        fig.savefig(O / "tess_folded.png", dpi=170)
        plt.close(fig)
(O / "summary.json").write_text(json.dumps(summary, indent=2))
(O / "sectors.json").write_text(json.dumps(meta, indent=2))
with (O / "events.csv").open("w") as f:
    writer = csv.DictWriter(f, fieldnames=all_events[0].keys())
    writer.writeheader()
    writer.writerows(all_events)
print(json.dumps(summary, indent=2))
