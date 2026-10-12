"""Render one two-panel RNAAS figure from preserved numeric inputs; no fitting."""

from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
R = P.parent.parent
files = [
    R / "analysis/validation-20261011/post/data/kic5689121_folded_15min_bins.csv",
    R / "analysis/validation-20261011/post/data/kic5689121_transit_model.csv",
    R / "analysis/validation-20261011/results/kepler/kcentroid_all_sources.csv",
]
b = np.genfromtxt(files[0], delimiter=",", names=True)
m = np.genfromtxt(files[1], delimiter=",", names=True)
with files[2].open() as f:
    rows = list(csv.DictReader(f))[1:]
fig, (a, c) = plt.subplots(
    1, 2, figsize=(10, 4), layout="constrained", gridspec_kw={"width_ratios": [1.2, 1]}
)
a.errorbar(
    b["hours_from_mid"],
    b["flux_ppm"],
    yerr=b["err_ppm"],
    fmt=".",
    ms=4,
    color="black",
    elinewidth=0.65,
)
a.plot(
    m["hours_from_mid"],
    m["model_ppm"],
    color="#b3472c",
    lw=1.5,
    label="Saved transit model",
)
a.axhline(0, color=".7", ls=":", lw=0.6)
a.set(
    xlabel="Hours from mid-transit",
    ylabel="Relative flux (ppm)",
    title="Kepler PSF photometry",
    xlim=(-8.6, 8.6),
)
a.legend(fontsize=8, frameon=False, loc="lower right")
y = np.arange(len(rows))
c.scatter([float(r["dchi2_vs_target"]) for r in rows], y, color="black", s=22)
c.set_yticks(
    y, [r["source_id"][-6:] + f"  ({float(r['sep']):.1f}″)" for r in rows], fontsize=8
)
c.set(
    xscale="log",
    xlim=(600, 25000),
    xlabel="Δχ² relative to target",
    title="Resolved-neighbour alternatives",
)
c.invert_yaxis()
c.grid(axis="x", alpha=0.2)
for ax in (a, c):
    ax.spines[["top", "right"]].set_visible(False)
fig.savefig(P / "figure1.pdf")
fig.savefig(P / "figure1.png", dpi=180)
(P / "figure_sources.json").write_text(
    json.dumps(
        [
            {
                "path": str(f.relative_to(R)),
                "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            }
            for f in files
        ],
        indent=2,
    )
    + "\n"
)
