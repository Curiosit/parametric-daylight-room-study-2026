#!/usr/bin/env python3
# Manuscript Figure 12: Warsaw against Berlin, paired configurations.
# Run from the repository root:  python figures/fig12_cities.py
"""
Figure 12 — geographic stability: every Batch A configuration simulated in Warsaw
plotted against its identical twin simulated in Berlin (2,160 pairs).

Points on the 1:1 line would indicate identical performance in both climates.
Colour encodes street aspect ratio, so the figure also shows that the canyon
effect is reproduced in each city, not merely the aggregate means.

Usage:
    python fig_12_cities.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
TIER_COLOUR = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
KEYS = ["win_height", "depth", "width", "rotation", "urban canyon toggle"]

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_12")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    d["ase"] = d["ASE_results"] * 100 if d["ASE_results"].max() <= 1.01 else d["ASE_results"]
    w = d[d.Location == "Warsaw"].set_index(KEYS)
    b = d[d.Location == "Berlin"].set_index(KEYS)
    m = w[["sDA", "ase", "HW"]].join(b[["sDA", "ase"]], lsuffix="_W", rsuffix="_B").dropna()

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7))
    for ax, col, lim, title, lab in (
        (axes[0], "sDA", 72, "(a) sDA$_{300/50\\%}$", "sDA$_{300/50\\%}$"),
        (axes[1], "ase", 23, "(b) ASE$_{1000,250}$", "ASE$_{1000,250}$"),
    ):
        ax.plot([0, lim], [0, lim], color="#999999", lw=0.9, ls="--", zorder=1)
        for hw in sorted(m.HW.unique()):
            q = m[m.HW == hw]
            ax.scatter(q[f"{col}_B"], q[f"{col}_W"], s=6, alpha=0.55, lw=0,
                       color=TIER_COLOUR[hw], label=f"H/W = {hw:.1f}", zorder=2)
        r = pearsonr(m[f"{col}_W"], m[f"{col}_B"])[0]
        diff = (m[f"{col}_W"] - m[f"{col}_B"]).mean()
        ax.text(0.04, 0.95, f"r = {r:.3f}\nmean difference {diff:+.2f} pts",
                transform=ax.transAxes, va="top", fontsize=9, color="#4d4d4d",
                linespacing=1.4)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_aspect("equal")
        ax.set_xlabel(f"Berlin {lab} (%)")
        ax.set_ylabel(f"Warsaw {lab} (%)")
        ax.set_title(title, loc="left")
        ax.grid(lw=0.4, alpha=0.3)
        ax.set_axisbelow(True)

    leg = axes[0].legend(frameon=False, loc="lower right", markerscale=3,
                         handletextpad=0.3, labelspacing=0.3)
    for h in leg.legend_handles:
        h.set_alpha(1)
    fig.tight_layout(w_pad=2.2)
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print(f"pairs: {len(m)}")
    for col in ("sDA", "ase"):
        dd = m[f"{col}_W"] - m[f"{col}_B"]
        print(f"{col}: Warsaw {m[f'{col}_W'].mean():.2f}  Berlin {m[f'{col}_B'].mean():.2f}  "
              f"mean diff {dd.mean():+.2f}  mean |diff| {dd.abs().mean():.2f}  "
              f"max |diff| {dd.abs().max():.2f}  r {pearsonr(m[f'{col}_W'], m[f'{col}_B'])[0]:.4f}")
    print(f"spearman (sDA ranks) {spearmanr(m.sDA_W, m.sDA_B)[0]:.4f}")
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
