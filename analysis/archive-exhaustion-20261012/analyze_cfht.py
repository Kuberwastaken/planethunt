from pathlib import Path
import numpy as np, csv, json
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import gaussian_filter, maximum_filter
from scipy.spatial import cKDTree
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).parent
h = fits.open(P / "cutout_1098087.body")
d = h[0].data.astype(float)
w = WCS(h[0].header)
stars = list(csv.DictReader((P / "gaia_field.body").open()))
g = np.array([float(s["phot_g_mean_mag"]) for s in stars])
coords = np.array([[float(s["ra"]), float(s["dec"])] for s in stars])
xy = w.all_world2pix(coords, 0)
sm = gaussian_filter(d, 1.5)
bg = np.median(sm)
noise = 1.4826 * np.median(abs(sm - bg))
y, x = np.where((sm == maximum_filter(sm, 11)) & (sm > bg + 15 * noise))
peaks = np.array([x, y]).T
bright = xy[
    (g < 18)
    & (xy[:, 0] > 50)
    & (xy[:, 0] < d.shape[1] - 50)
    & (xy[:, 1] > 50)
    & (xy[:, 1] < d.shape[0] - 50)
]
diffs = (peaks[:, None, :] - bright[None, :, :]).reshape(-1, 2)
diffs = diffs[np.all(abs(diffs) < 200, axis=1)]
tree = cKDTree(peaks)
best = []
for delta in diffs:
    dist, idx = tree.query(bright + delta)
    best.append((np.sum(dist < 4), np.median(np.sort(dist)[:10]), delta))
best.sort(key=lambda r: (-r[0], r[1]))
delta = best[0][2]
for _ in range(3):
    dist, idx = tree.query(bright + delta)
    ok = dist < 6
    delta = np.median(peaks[idx[ok]] - bright[ok], axis=0)
print(
    "best",
    best[:2],
    "delta",
    delta,
    "matched",
    ok.sum(),
    "rms",
    np.sqrt(np.mean(dist[ok] ** 2)),
)
from scipy.optimize import least_squares

results = []
fig, axs = plt.subplots(1, 2, figsize=(11, 5), layout="constrained")
for ax, sid in zip(axs, ["2103792461826460288", "2103792427466721792"]):
    i = [s["source_id"] for s in stars].index(sid)
    pos = xy[i] + delta
    ix, iy = np.rint(pos).astype(int)
    cut = d[iy - 18 : iy + 19, ix - 18 : ix + 19]
    yy, xx = np.indices(cut.shape)
    sky = np.median(cut[np.hypot(xx - 18, yy - 18) > 15])
    peak = cut.max()

    def model(p):
        b, a, cx, cy, alpha, beta = p
        return b + a * (1 + ((xx - cx) ** 2 + (yy - cy) ** 2) / alpha**2) ** (-beta)

    def resid(p):
        return (model(p) - cut).ravel()

    fit = least_squares(
        resid,
        [sky, peak - sky, 18, 18, 3, 2.5],
        bounds=([-np.inf, 0, 13, 13, 0.5, 1.01], [np.inf, np.inf, 23, 23, 12, 10]),
        loss="soft_l1",
        f_scale=100,
    )
    b, a, cx, cy, alpha, beta = fit.x
    fwhm = 2 * alpha * np.sqrt(2 ** (1 / beta) - 1) * 0.185
    results.append(
        dict(
            source_id=sid,
            peak_adu=float(peak),
            saturation_adu=68746,
            fwhm_arcsec=float(fwhm),
            fit=fit.x.tolist(),
            centroid_pixels=[float(ix - 18 + cx), float(iy - 18 + cy)],
        )
    )
    ax.imshow(
        np.arcsinh((cut - sky) / max(noise, 1)),
        origin="lower",
        extent=[-18 * 0.185, 18 * 0.185, -18 * 0.185, 18 * 0.185],
        cmap="gray",
    )
    ax.set(
        title=("Target" if ax == axs[0] else "7.1″ neighbour") + f" · FWHM {fwhm:.2f}″",
        xlabel="Arcsec from approximate centroid",
        ylabel="Arcsec",
    )
fig.savefig(P / "cfht_pair.png", dpi=150)
(P / "cfht_quality.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
