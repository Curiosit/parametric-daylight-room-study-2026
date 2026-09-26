#!/usr/bin/env python3
# Manuscript Figure 13: sDA against ASE; Batch C trade-off.
# Run from the repository root:  python figures/fig13_ase.py
"""
Figure 13 — daylight sufficiency and direct-sun exposure.

(a) Batch A, prescribed ratio: sDA300/50% against ASE1000,250 for all 4,320
    configurations, coloured by street aspect ratio. The shaded quadrant
    (sDA > 40%, ASE < 20%) is the high-performance zone.
(b) Batch C, raised ratios: as effective transmitted aperture increases, the
    direct-sun exposure of unobstructed south-facing rooms and the best
    daylight autonomy achievable at H/W = 1.0 both rise. The glare line crosses
    its limit well before the canyon line approaches its target.

Effective aperture = WFR x VT, normalised to the prescribed case (1/8 at 0.64).

Usage:
    python fig_13_ase.py --baseline study/A-baseline.xlsx --sweep study/C-wfr-x-vt.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
ORIENT = {0: "S", 1: "E", 2: "N", 3: "W"}
TIER_COLOUR = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
GLARE = "#b2182b"
CANYON = "#2171b5"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 8.8,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def pct(s):
    return s * 100 if s.max() <= 1.01 else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--sweep", default="study/C-wfr-x-vt.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_13")
    args = ap.parse_args()

    A = pd.read_excel(args.baseline)
    A["HW"] = A["urban canyon toggle"].map(HW_MAP)
    A["ase"] = pct(A["ASE_results"])

    C = pd.read_excel(args.sweep)
    C["HW"] = C["urban canyon toggle"].map(HW_MAP)
    C["or"] = C["rotation"].map(ORIENT)
    C["ase"] = pct(C["ASE_results-horizontal"])
    C["sda"] = C["sDA-horizontal"]
    C["eff"] = (1 / C["ratio"]) * C["VT"] / ((1 / 8) * 0.64)

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.9))

    # ---- (a) Batch A scatter with the high-performance quadrant
    ax = axes[0]
    ax.add_patch(plt.Rectangle((40, 0), 40, 20, color="#e5f5e0", zorder=0))
    ax.axvline(40, color="#4d4d4d", lw=0.9, ls="--", zorder=1)
    ax.axhline(20, color=GLARE, lw=0.9, ls="--", zorder=1)
    for hw in sorted(A.HW.unique(), reverse=True):
        q = A[A.HW == hw]
        ax.scatter(q.sDA, q.ase, s=5, lw=0, alpha=0.55, color=TIER_COLOUR[hw],
                   label=f"H/W = {hw:.1f}", zorder=2)
    hp = ((A.sDA > 40) & (A.ase < 20)).mean() * 100
    ax.text(69, 9.5, f"high-\nperformance\nzone\n{hp:.1f}%", ha="center", va="center",
            fontsize=8.5, color="#31a354", linespacing=1.25)
    over = (A.ase > 20).sum()
    ax.text(3, 21.2, f"{over} cases above 20% ASE", fontsize=8.5, color=GLARE)
    ax.set_xlim(0, 72)
    ax.set_ylim(0, 24)
    ax.set_xlabel("sDA$_{300/50\\%}$ (%)")
    ax.set_ylabel("ASE$_{1000,250}$ (%)")
    ax.set_title("(a) Prescribed ratio, Batch A", loc="left")
    h_, l_ = ax.get_legend_handles_labels()
    leg = ax.legend(h_[::-1], l_[::-1], frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.86),
                    markerscale=3, handletextpad=0.3, labelspacing=0.3)
    for h in leg.legend_handles:
        h.set_alpha(1)

    # ---- (b) Batch C trade-off against effective aperture
    ax = axes[1]
    g = C.groupby(["ratio", "VT"])
    rows = []
    for (r, v), q in g:
        rows.append(dict(
            eff=q.eff.iloc[0], label=f"1/{r}, {v:.2f}",
            glare=q[(q.HW == 0) & (q["or"] == "S")].ase.mean(),
            best=q[q.HW == 1.0].sda.max(),
            mean=q[q.HW == 1.0].sda.mean(),
        ))
    t = pd.DataFrame(rows).sort_values("eff")
    ax.axhline(20, color=GLARE, lw=0.9, ls="--", alpha=0.8)
    ax.axhline(40, color="#4d4d4d", lw=0.9, ls="--", alpha=0.8)
    ax.text(1.92, 20.6, "ASE limit 20%", ha="right", fontsize=8.3, color=GLARE)
    ax.text(1.92, 40.6, "sDA benchmark 40%", ha="right", fontsize=8.3, color="#4d4d4d")
    ax.plot(t.eff, t.glare, "o-", color=GLARE, lw=1.8, ms=4.5,
            label="ASE, unobstructed south-facing (mean)")
    ax.plot(t.eff, t.best, "s-", color=CANYON, lw=1.8, ms=4.5,
            label="sDA at H/W = 1.0, best case")
    ax.plot(t.eff, t["mean"], "s:", color=CANYON, lw=1.3, ms=3.5, alpha=0.8,
            label="sDA at H/W = 1.0, mean")
    ax.set_xlabel("Relative effective aperture (WFR × VT)")
    ax.set_ylabel("Percent")
    ax.set_title("(b) Raised ratios, Batch C", loc="left")
    ax.set_xlim(0.94, 1.96)
    ax.set_ylim(0, 46)
    ax.set_xticks([1.0, 1.2, 1.4, 1.6, 1.8])
    ax.legend(frameon=False, loc="lower right", handlelength=1.8, labelspacing=0.3)
    for ax_ in axes:
        ax_.grid(lw=0.4, alpha=0.3)
        ax_.set_axisbelow(True)

    fig.tight_layout(w_pad=2.2)
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print("Batch A: HP zone %.2f%%, cases ASE>20: %d, max ASE %.2f" % (hp, over, A.ase.max()))
    print(t.round(2).to_string(index=False))
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
