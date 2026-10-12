"""Audit the saved two-source SPHEREx extraction; no stellar/planet model fit.

Read numeric TABLEDATA explicitly: Astropy cannot parse this service's char
arraysize='4x*'/'54x*'. Preserve the original VOTable without rewriting it.
"""

from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.utils import iers
import astropy.units as u

P = Path(__file__).resolve().parent
iers.conf.auto_download = False
NS = {"v": "http://www.ivoa.net/xml/VOTable/v1.3"}
BAD_BITS = [
    0,
    1,
    2,
    6,
    7,
    9,
    10,
    11,
    14,
    15,
    17,
    19,
    20,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    32,
    33,
]
BAD_MASK = sum(1 << b for b in BAD_BITS)


def read_spectra():
    table = ET.parse(P / "spherex_result.vot").find(".//v:TABLE", NS)
    fields = table.findall("v:FIELD", NS)
    out = {}
    for tr in table.findall(".//v:TR", NS):
        row = dict(zip([f.attrib["name"] for f in fields], [c.text or "" for c in tr]))
        n = int(row["n_meas"])
        for f in fields:
            a = f.attrib
            if a.get("arraysize") == "*" and a["datatype"] != "char":
                name = a["name"]
                row[name] = np.fromstring(
                    row[name],
                    sep=" ",
                    dtype=np.int64
                    if a["datatype"] in ("long", "bit", "unsignedByte")
                    else float,
                )
                assert len(row[name]) == n, (name, len(row[name]), n)
        out[row["label"]] = row
    return out


def twomass():
    table = Table.read(P / "twomass_pair.body", format="ascii.ipac")
    results = {}
    for label, designation in [
        ("target", "19033788+4056311"),
        ("neighbour", "19033726+4056316"),
    ]:
        row = table[np.asarray(table["designation"]) == designation][0]
        results[label] = []
        for band, wave, zp, ze in [
            ("j", 1.235, 1594, 27.8),
            ("h", 1.662, 1024, 20),
            ("k", 2.159, 666.7, 12.6),
        ]:
            mag, err = float(row[band + "_m"]), float(row[band + "_msigcom"])
            flux = zp * 10 ** (-0.4 * mag) * 1000
            results[label].append(
                dict(
                    band=band.upper(),
                    wavelength_micron=wave,
                    magnitude=mag,
                    magnitude_error=err,
                    flux_mjy=flux,
                    stat_error_mjy=flux * np.log(10) * 0.4 * err,
                    zeropoint_fractional_uncertainty=ze / zp,
                )
            )
    (P / "twomass_flux_comparison.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )
    return results


spectra = read_spectra()
tm = twomass()
sp = json.loads(
    (P.parent / "archive-followup-20261012/spitzer/results/summary.json").read_text()
)
summary = dict(
    method="Joint fixed-position point-source Tractor extraction. Conservative bad-bit mask; fit_ql <= 2 is an analyst-selected screen, not an official acceptance threshold.",
    bad_bits=BAD_BITS,
    informational_bits_allowed=[12, 21],
    sources={},
    limitations="No bandpass-integrated stellar fit, close-companion exclusion, atmosphere inference or FPP update. Geocentric timing neglects satellite orbit. Cross-survey comparison is illustrative; bandpasses, calibration and epochs differ.",
)
fig, axs = plt.subplots(
    2, 2, figsize=(13, 8), layout="constrained", gridspec_kw={"height_ratios": [2, 1]}
)
for ax, qa, (label, name) in zip(
    axs[0], axs[1], [("KIC5689121", "target"), ("KIC5689116", "neighbour")]
):
    r = spectra[label]
    wave, flux, err, flags, fit = [
        r[c] for c in ["lambda", "flux", "flux_err", "flags", "fit_ql"]
    ]
    finite = np.isfinite(wave + flux + err + fit) & (err > 0)
    clean = finite & ((flags & BAD_MASK) == 0)
    keep = clean & (fit <= 2)
    time = Time(
        r["mjd"],
        format="mjd",
        scale="utc",
        location=EarthLocation.from_geocentric(0, 0, 0, unit="m"),
    )
    bjd = (
        time.tdb
        + time.light_travel_time(
            SkyCoord(float(r["ra"]) * u.deg, float(r["dec"]) * u.deg)
        )
    ).jd
    phase = (
        (bjd - 2455630.245430646 + 13.769448251493595 / 2) % 13.769448251493595
        - 13.769448251493595 / 2
    ) * 24
    data = Table(
        {
            c: r[c]
            for c in [
                "lambda",
                "lambda_width",
                "flux",
                "flux_err",
                "mjd",
                "flags",
                "fit_ql",
                "flux_bkg",
                "det_id",
                "lvf_id",
                "x_image",
                "y_image",
            ]
        }
    )
    data["selected"] = keep
    data["hours_from_predicted_midpoint"] = phase
    data.write(P / f"spherex_{name}.ecsv", format="ascii.ecsv", overwrite=True)
    stats = dict(
        n_returned=len(wave),
        n_clean_flags=int(clean.sum()),
        n_selected=int(keep.sum()),
        fit_ql_median=float(np.median(fit)),
        wavelength_range_um=[float(wave.min()), float(wave.max())],
        date_range_utc=[time.min().isot, time.max().isot],
        in_transit=int((abs(phase) < 1.15).sum()),
        closest_midpoint_hours=float(min(abs(phase))),
        clean_fit_threshold_counts={
            str(q): int((clean & (fit <= q)).sum()) for q in [1.5, 2, 2.5, 3]
        },
        flag_bit_counts={
            str(b): int(((flags & (1 << b)) != 0).sum())
            for b in range(34)
            if ((flags & (1 << b)) != 0).any()
        },
        median_selected_fractional_error=float(np.median(err[keep] / flux[keep])),
    )
    stats["selected_by_detector"] = {
        str(d): dict(
            n=int((keep & (r["det_id"] == d)).sum()),
            median_fit_ql=float(np.median(fit[keep & (r["det_id"] == d)])),
        )
        for d in np.unique(r["det_id"])
        if (keep & (r["det_id"] == d)).any()
    }
    summary["sources"][label] = stats
    ax.scatter(
        wave[~keep],
        flux[~keep] / 1000,
        c="0.75",
        marker="x",
        s=14,
        label="Flagged / fit metric > 2",
    )
    ax.errorbar(
        wave[keep],
        flux[keep] / 1000,
        yerr=err[keep] / 1000,
        fmt=".",
        ms=3,
        color="#286c8d",
        elinewidth=0.6,
        alpha=0.8,
        label="SPHEREx selected",
    )
    a = tm[name]
    ax.errorbar(
        [x["wavelength_micron"] for x in a],
        [x["flux_mjy"] for x in a],
        yerr=[
            np.hypot(
                x["stat_error_mjy"],
                x["flux_mjy"] * x["zeropoint_fractional_uncertainty"],
            )
            for x in a
        ],
        fmt="s",
        mfc="none",
        color="#b96720",
        ms=6,
        label="2MASS (broad bands)",
    )
    ax.scatter(
        [3.6, 4.5],
        [sp[c][name]["mean_prf_mjy"] for c in ["1", "2"]],
        marker="D",
        facecolors="none",
        edgecolors="#8d3c6b",
        s=45,
        label="Spitzer PRF (systematics not shown)",
    )
    ax.set(
        title=f"{label} / {name}",
        ylabel="Flux density (mJy)",
        xlim=(0.65, 5.1),
        ylim=(0, 7),
    )
    ax.legend(fontsize=8, loc="upper right")
    qa.scatter(wave[keep], fit[keep], s=7, color="#286c8d")
    qa.scatter(wave[~keep], fit[~keep], s=10, color="0.65", marker="x")
    qa.axhline(2, color="0.4", ls="--", lw=0.8)
    qa.set(
        xlabel="Wavelength (μm)",
        ylabel="Fit quality metric",
        xlim=(0.65, 5.1),
        ylim=(0, 3),
    )
    for a in (ax, qa):
        a.spines[["top", "right"]].set_visible(False)
        a.grid(alpha=0.15)
fig.suptitle(
    "Joint extraction of the known 7.1″ pair • no in-transit measurements", fontsize=15
)
fig.savefig(P / "spherex_pair_spectra.png", dpi=170)
(P / "spherex_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
