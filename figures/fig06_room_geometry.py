#!/usr/bin/env python3
# Manuscript Figure 6: sDA300/50% against room width and depth.
# Run from the repository root:  python figures/fig06_room_geometry.py
"""
Figure 6 — room geometry and sDA300/50%, by street aspect ratio (Batch A).

Main axes: mean sDA against room width (a) and room depth (b), one line per
street aspect ratio, on a common absolute scale. The vertical separation between
lines is the street-aspect-ratio effect; the slope along each line is the
room-geometry effect. The comparison between the two is the point of the figure.

Insets: the unobstructed line magnified, since at the scale of the main axes its
shape is invisible. Panel (a)'s inset carries a fitted 1/W curve; the saturating
form is consistent with side-wall exposure, which falls as 2h/W and routes
proportionally less interreflected light through the darker (rho = 0.50) side
surfaces as the room widens.

Usage:
    python fig_6_room_geometry.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})

TIER_COLOUR = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
FIT = "#b2182b"


def tier_lines(ax, d, col):
    ranges = {}
    for hw in sorted(d.HW.unique()):
        q = d[d.HW == hw]
        x = sorted(q[col].unique())
        y = [q.loc[q[col] == v, "sDA"].mean() for v in x]
        ax.plot(x, y, "o-", color=TIER_COLOUR[hw], lw=1.8, ms=4,
                label=f"H/W = {hw:.1f}")
        ax.annotate(f"{max(y)-min(y):.2f}", xy=(x[-1], y[-1]),
                    xytext=(7, -1), textcoords="offset points",
                    fontsize=8.5, color=TIER_COLOUR[hw], va="center")
        ranges[hw] = max(y) - min(y)
    return ranges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_06")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    u = d[d.HW == 0.0]

    fig = plt.figure(figsize=(7.4, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.55, 1.0], hspace=0.45, wspace=0.30)
    top = [fig.add_subplot(gs[0, 0]), None]
    top[1] = fig.add_subplot(gs[0, 1], sharey=top[0])
    bot = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]

    rw = tier_lines(top[0], d, "width")
    top[0].set_xlabel("Room width (m)")
    top[0].set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    top[0].set_title("(a) Room width, all tiers", loc="left")
    top[0].set_xlim(2.7, 8.0)


    rd = tier_lines(top[1], d, "depth")
    top[1].set_xlabel("Room depth (m)")
    top[1].set_title("(b) Room depth, all tiers", loc="left")
    top[1].set_xlim(2.6, 8.2)
    plt.setp(top[1].get_yticklabels(), visible=False)

    for ax in top:
        ax.set_ylim(0, 50)
        ax.grid(axis="y", lw=0.4, alpha=0.3)
        ax.set_axisbelow(True)
    top[0].annotate("", xy=(2.9, 42.58), xytext=(2.9, 7.65),
                    arrowprops=dict(arrowstyle="<->", color="#4d4d4d", lw=1.0))
    top[0].text(3.05, 34, "34.93 pts\nbetween tiers", fontsize=8.5,
                color="#4d4d4d", va="center", linespacing=1.4)
    top[1].legend(ncol=2, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.70),
                  handlelength=1.5, columnspacing=1.2, labelspacing=0.3,
                  borderpad=0.2, fontsize=8.5)

    O_COL = {"South": "#b2182b", "West": "#ef8a62", "East": "#67a9cf", "North": "#2166ac"}
    O_MARK = {"South": "o", "West": "s", "East": "D", "North": "^"}
    u = u.assign(orient=u["rotation"].map({0: "South", 1: "East", 2: "North", 3: "West"}))

    # (c) width, unobstructed mean, with 1/W fit
    ax = bot[0]
    x = np.array(sorted(u.width.unique()), dtype=float)
    y = np.array([u.loc[u.width == v, "sDA"].mean() for v in x])
    ax.plot(x, y, "o-", color=TIER_COLOUR[0.0], lw=1.8, ms=4.5, zorder=3, label="mean")
    a, b = np.polyfit(1 / x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.plot(xs, b + a / xs, ls="--", lw=1.3, color=FIT, zorder=2)
    ax.text(0.97, 0.08, f"${b:.1f} - {abs(a):.1f}/W$\nmax residual {np.abs(y-(b+a/x)).max():.2f} pts",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=FIT, linespacing=1.5)
    ax.set_title("(c) Room width, H/W = 0.0, all orientations", loc="left", fontsize=10)
    ax.set_xlabel("Room width (m)")
    ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    ax.set_ylim(37.5, 46.5)

    # (d) depth, unobstructed, split by orientation — the cancellation
    ax = bot[1]
    for o in ["South", "West", "East", "North"]:
        q = u[u.orient == o].groupby("depth").sDA.mean()
        slope = np.polyfit(q.index, q.values, 1)[0]
        ax.plot(q.index, q.values, marker=O_MARK[o], color=O_COL[o], lw=1.7, ms=4.5,
                label=f"{o} ({slope:+.2f} pts/m)")
    q = u.groupby("depth").sDA.mean()
    ax.plot(q.index, q.values, color="#4d4d4d", lw=1.2, ls=":", label="mean")
    ax.set_title("(d) Room depth, H/W = 0.0, by orientation", loc="left", fontsize=10)
    ax.set_xlabel("Room depth (m)")
    ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    ax.set_ylim(14, 66)
    ax.legend(frameon=False, loc="lower center", fontsize=7.8, handlelength=1.4, ncol=2,
              labelspacing=0.25, columnspacing=0.9, borderpad=0.1)

    for ax in bot:
        ax.grid(lw=0.4, alpha=0.3)
        ax.set_axisbelow(True)
        ax.margins(x=0.07)

    tier = d.groupby("HW").sDA.mean()
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print("range of means within each tier:")
    print(f"{'H/W':>5} {'width':>8} {'depth':>8}")
    for hw in sorted(rw):
        print(f"{hw:>5.1f} {rw[hw]:>8.2f} {rd[hw]:>8.2f}")
    print(f"\nbetween tiers: {tier.max()-tier.min():.2f}")
    for col in ("width", "depth"):
        print(f"{col:>6}: rho {spearmanr(u[col], u['sDA'])[0]:+.3f} unobstructed, "
              f"{spearmanr(d[col], d['sDA'])[0]:+.3f} all tiers")
    x = np.array(sorted(u.width.unique()), dtype=float)
    y = np.array([u.loc[u.width == v, "sDA"].mean() for v in x])
    a, b = np.polyfit(1 / x, y, 1)
    print(f"1/W fit: sDA = {b:.2f} - {abs(a):.2f}/W, "
          f"max residual {np.abs(y - (b + a / x)).max():.2f} pts")
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
