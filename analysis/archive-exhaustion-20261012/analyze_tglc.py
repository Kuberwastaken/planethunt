from pathlib import Path
import json
import numpy as np
from astropy.io import fits

P = Path(__file__).resolve().parent
O = P / "tglc_results"
O.mkdir(exist_ok=True)
T0 = -1369.7545693539214
PER = 13.769448251493595
HALF = 1.15 / 24
COLS = ["psf_flux", "aperture_flux", "cal_psf_flux", "cal_aper_flux"]
RADII = COLS
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


summary = {}
for source in ["2103792461826460288", "2103792427466721792"]:
    series = []
    for f in sorted(P.glob(f"tglc_correct_*_{source}.body")):
        with fits.open(f) as hd:
            d = hd[1].data
            good = (
                (d["TESS_flags"] == 0) & (d["TGLC_flags"] == 0) & np.isfinite(d["time"])
            )
            for c in COLS:
                good &= np.isfinite(d[c])
            t = np.array(d["time"][good], float)
            flux = np.array([d[c][good] for c in COLS], float)
            series.append(
                (int(f.name.split("_")[2]), t, flux, float(np.median(np.diff(t))))
            )
    for i, col in enumerate(COLS):
        s, events, fold = measure(radius_idx=i, collect=True)
        controls = [
            dict(offset_days=float(off), **measure(offset=float(off), radius_idx=i)[0])
            for off in np.linspace(0.35, PER - 0.35, 80)
        ]
        s["control_depth_std_ppm"] = float(
            np.std([x["depth_ppm"] for x in controls], ddof=1)
        )
        s["phase_control_fraction_at_least_as_deep"] = float(
            np.mean([x["depth_ppm"] >= s["depth_ppm"] for x in controls])
        )
        s["timing_offsets"] = [
            dict(offset_minutes=off, result=measure(offset=off / 1440, radius_idx=i)[0])
            for off in [-60, -30, 0, 30, 60]
        ]
        key = f"{source}_{col}"
        summary[key] = s
        (O / f"{key}.json").write_text(
            json.dumps(
                dict(summary=s, events=events, phase_controls=controls), indent=2
            )
        )
        np.save(O / f"{key}_fold.npy", np.array(fold))
(O / "summary.json").write_text(json.dumps(summary, indent=2))
for k, s in summary.items():
    print(
        k,
        round(s["depth_ppm"]),
        round(s["error_ppm"]),
        s["n_events"],
        round(s["control_depth_std_ppm"]),
    )
