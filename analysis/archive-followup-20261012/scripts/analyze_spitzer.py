"""Exploratory IRAC photometry; no companion contrast curve or FPP inference.
Run with --data pointing to a directory containing fits/, prfs/ and kfit_psf.json.
"""

import argparse, json, csv, warnings
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_area
from scipy.ndimage import map_coordinates, spline_filter
from scipy.optimize import least_squares
from photutils.aperture import CircularAperture
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=fits.verify.VerifyWarning)
a = argparse.ArgumentParser()
a.add_argument(
    "--data", type=Path, default=Path(__file__).resolve().parents[1] / "spitzer"
)
a.add_argument("--out", type=Path)
args = a.parse_args()
P = args.data
O = args.out or P / "results"
O.mkdir(parents=True, exist_ok=True)
coords = np.array([[285.907827, 40.941988], [285.90521895334, 40.94207048408]])
eph = json.loads((P / "kfit_psf.json").read_text())
period = eph["P"][0]
t0 = eph["T0_btjd"][0] + 2457000
cache = {}


def prf_at(ch, x, y):
    grid = np.array([25, 77, 129, 181, 233.0])
    x = np.clip(x + 1, 25, 233)
    y = np.clip(y + 1, 25, 233)
    ix = np.clip(np.searchsorted(grid, x) - 1, 0, 3)
    iy = np.clip(np.searchsorted(grid, y) - 1, 0, 3)
    fx = (x - grid[ix]) / 52
    fy = (y - grid[iy]) / 52
    out = 0
    for i, wx in [(ix, 1 - fx), (ix + 1, fx)]:
        for j, wy in [(iy, 1 - fy), (iy + 1, fy)]:
            name = f"IRACPC{ch}_col{int(grid[i]):03d}_row{int(grid[j]):03d}.fits"
            if name not in cache:
                cache[name] = fits.getdata(P / "prfs" / name).astype(float)
            out = out + wx * wy * cache[name]
    # Renormalize the sampled zero-phase realization to unit flux inside 10 native pixels.
    # The supplied FITS amplitudes do not numerically sum to one when sampled at 5-pixel steps.
    gy, gx = np.mgrid[-10:11, -10:11]
    norm = map_coordinates(
        out, [gy * 5 + 63.5, gx * 5 + 63.5], order=3, mode="constant", cval=0
    )[gx * gx + gy * gy <= 100].sum()
    return out / norm


def solve(d, e, mask, xy, ch, radius=7, strict=False):
    yy, xx = np.indices(d.shape)
    zone = np.min([np.hypot(xx - x, yy - y) for x, y in xy], axis=0) < radius
    valid = (
        zone
        & np.isfinite(d)
        & np.isfinite(e)
        & (e > 0)
        & ((mask == 0) if strict else ((mask & 32520) == 0))
    )
    X, Y = xx[valid], yy[valid]
    D, E = d[valid], e[valid]
    templates = [spline_filter(prf_at(ch, *pos), order=3) for pos in xy]

    # Reference centre is free through the fitted source positions, not fixed astrometry.
    def design(v):
        cols = [
            map_coordinates(
                prf,
                [(Y - v[2 * i + 1]) * 5 + 63.5, (X - v[2 * i]) * 5 + 63.5],
                order=3,
                mode="constant",
                cval=0,
                prefilter=False,
            )
            for i, prf in enumerate(templates)
        ]
        return np.array(
            cols + [np.ones(len(X)), (X - xy[0, 0]) / 10, (Y - xy[0, 1]) / 10]
        ).T

    def res(v):
        A = design(v)
        coef = np.linalg.lstsq(A / E[:, None], D / E, rcond=None)[0]
        return (D - A @ coef) / E

    start = xy.ravel()
    fit = least_squares(
        res, start, bounds=(start - 1.5, start + 1.5), xtol=1e-9, ftol=1e-9, gtol=1e-9
    )
    A = design(fit.x)
    coef = np.linalg.lstsq(A / E[:, None], D / E, rcond=None)[0]
    r = res(fit.x)
    red = np.sum(r * r) / (len(D) - 9)
    cov = np.linalg.inv((A / E[:, None]).T @ (A / E[:, None])) * max(1, red)
    return dict(
        xy=fit.x.reshape(2, 2),
        amps=coef[:2],
        errors=np.sqrt(np.diag(cov)[:2]),
        redchi2=red,
        shift=fit.x - start,
        background=coef[2:],
        valid=valid,
        residual=r,
        X=X,
        Y=Y,
        model=A @ coef,
        success=fit.success,
    )


def aperture(d, e, mask, xy, i, r, ch):
    x, y = xy[i]
    other = xy[1 - i]
    yy, xx = np.indices(d.shape)
    rr = np.hypot(xx - x, yy - y)
    background = (
        (rr >= 12)
        & (rr < 20)
        & (np.hypot(xx - other[0], yy - other[1]) > 5)
        & np.isfinite(d)
        & ((mask & 32520) == 0)
    )
    vals = d[background]
    med = np.median(vals)
    sig = 1.4826 * np.median(abs(vals - med))
    vals = vals[abs(vals - med) < 3 * sig]
    bg = np.mean(vals)
    bge = np.std(vals) / np.sqrt(len(vals))
    weights = CircularAperture((x, y), r).to_mask(method="exact").to_image(d.shape)
    inside = weights > 0
    bad = ((mask & 32520) != 0) | ~np.isfinite(d) | ~np.isfinite(e)
    if np.any(bad & inside):
        return None
    corr = {1: {2: 1.2026, 3: 1.1132}, 2: {2: 1.2228, 3: 1.1126}}[ch][r]
    return {
        "amp": float(np.sum(weights[inside] * (d[inside] - bg)) * corr),
        "err": float(
            np.sqrt(
                np.sum((weights[inside] * e[inside]) ** 2) + (weights.sum() * bge) ** 2
            )
            * corr
        ),
    }


results = []
fig, axs = plt.subplots(2, 4, figsize=(14, 7), layout="constrained")
resfig, resaxs = plt.subplots(2, 4, figsize=(14, 7), layout="constrained")
for fi, f in enumerate(sorted((P / "fits").glob("*cbcd.fits"))):
    d, h = fits.getdata(f, header=True)
    d = d.astype(float)
    e = fits.getdata(str(f).replace("cbcd", "cbunc")).astype(float)
    mask = fits.getdata(str(f).replace("cbcd", "bimsk")).astype(np.int64)
    br = fits.getdata(str(f).replace("cbcd", "brmsk"))
    mask[br != 0] |= 16384
    w = WCS(h)
    xy = w.all_world2pix(coords, 0)
    ch = int(h["CHNLNUM"])
    fac = float(abs(proj_plane_pixel_area(w)) * (np.pi / 180) ** 2 * 1e9)
    fit = solve(d, e, mask, xy, ch)
    assert fit["success"], f"Fit failed: {f}"
    strict = solve(d, e, mask, xy, ch, strict=True)
    small = solve(d, e, mask, xy, ch, radius=5)
    # Handbook BMJD_OBS is UTC-like: convert ET-UTC seconds to days, add midpoint.
    bjd = (
        h["BMJD_OBS"]
        + 2400000.5
        + (h["ET_OBS"] - h["UTCS_OBS"] + h["FRAMTIME"] / 2) / 86400
    )
    dt = ((bjd - t0 + period / 2) % period - period / 2) * 24
    row = {
        "file": f.name,
        "channel": ch,
        "exptime_s": h["EXPTIME"],
        "bjd_tdb_mid_approx": bjd,
        "hours_from_predicted_transit": dt,
        "pixel_mjy_per_mjysr": fac,
        "redchi2": float(fit["redchi2"]),
        "separation_arcsec": float(
            np.linalg.norm(fit["xy"][1] - fit["xy"][0])
            * np.sqrt(abs(h["PXSCAL1"] * h["PXSCAL2"]))
        ),
        "success": bool(fit["success"]),
    }
    for i, name in enumerate(["target", "neighbour"]):
        x, y = fit["xy"][i]
        row.update(
            {
                name + "_x": float(x),
                name + "_y": float(y),
                name + "_wcs_offset_pixels": float(
                    np.linalg.norm(fit["xy"][i] - xy[i])
                ),
                name + "_prf_mjy": float(fit["amps"][i] * fac),
                name + "_prf_fit_err_mjy": float(fit["errors"][i] * fac),
                name + "_prf_strict_mask_mjy": float(strict["amps"][i] * fac),
                name + "_prf_radius5_mjy": float(small["amps"][i] * fac),
                name + "_edge_pixels": float(min(x, y, 255 - x, 255 - y)),
            }
        )
        for r in [2, 3]:
            ap = aperture(d, e, mask, fit["xy"], i, r, ch)
            row[name + f"_ap{r}_mjy"] = ap["amp"] * fac if ap else None
            row[name + f"_ap{r}_err_mjy"] = ap["err"] * fac if ap else None
    results.append(row)
    ax = axs.flat[fi]
    rx = resaxs.flat[fi]
    xt, yt = fit["xy"][0]
    xn, yn = fit["xy"][1]
    ax.imshow(
        d, origin="lower", cmap="magma", vmin=np.nanmedian(d), vmax=np.nanmedian(d) + 12
    )
    resim = np.full(d.shape, np.nan)
    resim[fit["Y"], fit["X"]] = fit["residual"]
    rx.imshow(resim, origin="lower", cmap="RdBu_r", vmin=-5, vmax=5)
    for q in [ax, rx]:
        q.set_xlim(xt - 9, xt + 9)
        q.set_ylim(min(yt, yn) - 7, max(yt, yn) + 7)
        q.set_xticks([])
        q.set_yticks([])
        q.set_title(
            f"{3.6 if ch == 1 else 4.5} μm · {h['DATE_OBS'][:10]} · {f.name.split('_')[3]}",
            fontsize=9,
        )
    ax.scatter(
        [xt, xn], [yt, yn], facecolors="none", edgecolors=["cyan", "lime"], s=150
    )
    ax.text(
        0.03,
        0.97,
        f"T {row['target_prf_mjy']:.2f} / N {row['neighbour_prf_mjy']:.2f} mJy",
        transform=ax.transAxes,
        va="top",
        color="white",
        fontsize=9,
    )
fig.suptitle(
    "KIC 5689121 in Spitzer images · cyan: target · green: optical neighbour\nExploratory warm-PRF photometry; detector coordinates; stars, not a resolved planet",
    fontsize=12,
)
fig.savefig(O / "spitzer_frames.png", dpi=170)
plt.close(fig)
resfig.suptitle(
    "Two-source PRF + background-plane fit residuals\nColour scale: −5 to +5 pipeline uncertainty units; masked pixels blank",
    fontsize=12,
)
resfig.savefig(O / "spitzer_residuals.png", dpi=170)
plt.close(resfig)
(O / "per_frame.json").write_text(json.dumps(results, indent=2))
with (O / "per_frame.csv").open("w") as f:
    wr = csv.DictWriter(f, fieldnames=results[0].keys())
    wr.writeheader()
    wr.writerows(results)
summary = {}
for ch in [1, 2]:
    rows = [r for r in results if r["channel"] == ch]
    s = {"n_frames": len(rows), "exposure_total_s": sum(r["exptime_s"] for r in rows)}
    for name in ["target", "neighbour"]:
        v = np.array([r[name + "_prf_mjy"] for r in rows])
        s[name] = {
            "mean_prf_mjy": float(np.mean(v)),
            "frame_scatter_mjy": float(np.std(v, ddof=1)),
            "sem_mjy": float(np.std(v, ddof=1) / np.sqrt(len(v))),
            "mean_ap2_mjy": float(
                np.mean(
                    [
                        r[name + "_ap2_mjy"]
                        for r in rows
                        if r[name + "_ap2_mjy"] is not None
                    ]
                )
            ),
            "mean_ap3_mjy": float(
                np.mean(
                    [
                        r[name + "_ap3_mjy"]
                        for r in rows
                        if r[name + "_ap3_mjy"] is not None
                    ]
                )
            ),
            "mean_strict_mask_mjy": float(
                np.mean([r[name + "_prf_strict_mask_mjy"] for r in rows])
            ),
            "mean_radius5_mjy": float(
                np.mean([r[name + "_prf_radius5_mjy"] for r in rows])
            ),
        }
    s["mean_flux_ratio_target_neighbour"] = float(
        np.mean([r["target_prf_mjy"] / r["neighbour_prf_mjy"] for r in rows])
    )
    summary[str(ch)] = s
summary["limits"] = (
    "Exploratory photometry. Fit amplitude errors condition on fitted positions. No array-location/aperture pixel-phase or colour correction applied; PRF includes subpixel response. Method/mask discrepancies and calibration systematics dominate. Do not use as a contrast curve or transit depth."
)
(O / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
print(
    "Transit offsets (hours)",
    [round(r["hours_from_predicted_transit"], 2) for r in results],
)
