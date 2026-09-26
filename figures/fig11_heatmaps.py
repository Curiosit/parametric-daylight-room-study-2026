#!/usr/bin/env python3
# Manuscript Figure 11: sDA300/50% by room width and depth, per street aspect ratio.
# Run from the repository root:  python figures/fig11_heatmaps.py
"""
Figure 10 — mean sDA300/50% by room width and room depth, one heatmap per street
aspect ratio, on a shared colour scale (Batch A, n = 4,320; 24 cases per cell).

The shared scale is deliberate. Within each panel the grid is close to uniform,
because room proportions have little effect; between panels the colour shifts
wholesale, because street aspect ratio has a large one. Separate colour scales
per panel would hide exactly that contrast.

Usage:
    python fig_10_heatmaps.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
TIERS = [0.0, 0.5, 1.0, 1.5]

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9.5,
    "axes.labelsize": 10.5,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 9,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_11")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    grids = {hw: d[d.HW == hw].groupby(["depth", "width"]).sDA.mean().unstack()
             for hw in TIERS}
    vmin, vmax = 0, max(g.values.max() for g in grids.values())
    widths = grids[0.0].columns.to_numpy()
    depths = grids[0.0].index.to_numpy()

    # cell edges at real metric positions, so both axes share one scale
    def edges(c):
        c = np.asarray(c, dtype=float)
        mid = (c[:-1] + c[1:]) / 2
        return np.concatenate([[c[0] - (mid[0] - c[0])], mid, [c[-1] + (c[-1] - mid[-1])]])
    xe, ye = edges(widths), edges(depths)

    fig, axes = plt.subplots(1, 4, figsize=(10.4, 3.7), sharey=True)
    cmap = mpl.colormaps["viridis"]
    for ax, hw in zip(axes, TIERS):
        g = grids[hw]
        im = ax.pcolormesh(xe, ye, g.values, cmap=cmap, vmin=vmin, vmax=vmax,
                           edgecolors="white", linewidth=0.4)
        ax.set_aspect("equal")                     # one metre is the same length on both axes
        ax.set_xlim(xe[0], xe[-1]); ax.set_ylim(ye[-1], ye[0])   # depth increases downward
        ax.set_xticks([3, 4, 5, 6, 7])
        ax.set_yticks(depths)
        ax.set_xlabel("Room width (m)")
        rng = g.values.max() - g.values.min()
        ax.set_title(f"H/W = {hw:.1f}\nmean {g.values.mean():.1f}%, range {rng:.2f}",
                     loc="left", linespacing=1.35)
        for fn in (np.argmax, np.argmin):
            i, j = np.unravel_index(fn(g.values), g.shape)
            v = g.values[i, j]
            ax.text(widths[j], depths[i], f"{v:.1f}", ha="center", va="center",
                    fontsize=6.8, rotation=90,
                    color="white" if v < vmax * 0.55 else "black")
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axes[0].set_ylabel("Room depth (m)")

    cbar = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.015, shrink=0.8)
    cbar.set_label("Mean sDA$_{300/50\\%}$ (%)")
    cbar.outline.set_visible(False)

    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    q = d.groupby(["HW", "depth", "width"]).sDA.mean().reset_index()
    between = ((q.groupby("HW").sDA.transform("mean") - q.sDA.mean()) ** 2).sum()
    total = ((q.sDA - q.sDA.mean()) ** 2).sum()
    for hw in TIERS:
        g = grids[hw]
        print(f"H/W {hw:.1f}: cells {g.values.min():6.2f} – {g.values.max():6.2f}  "
              f"(range {g.values.max()-g.values.min():5.2f})")
    print(f"share of variance in the 180 cell means explained by H/W: {100*between/total:.1f}%")
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
