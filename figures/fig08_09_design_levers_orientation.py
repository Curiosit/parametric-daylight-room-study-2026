#!/usr/bin/env python3
# Manuscript Figure 8, 9: Design levers by street aspect ratio; orientation.
# Run from the repository root:  python figures/fig08_09_design_levers_orientation.py
"""
Figures for Section 3.3 (Batch A, n = 4,320).

Figure 7 — design levers under obstruction.
    The range of mean sDA300/50% attributable to each design variable, at each
    street aspect ratio. Orientation, the largest lever in open conditions,
    collapses; room width and depth were never large. Window clear height is
    omitted because its Batch A values are confounded with sill position and
    are treated separately in Section 3.2.3.

Figure 8 — orientation.
    (a) mean sDA300/50% by orientation across street aspect ratios;
    (b) mean ASE1000,250 by orientation across street aspect ratios.
    Read together: south-facing rooms lose their daylight advantage under
    obstruction but retain their direct-sun exposure.

Rotation is counter-clockwise from south: 0 = S, 1 = E, 2 = N, 3 = W.

Usage:
    python fig_3_3.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
ORIENT = {0: "South", 1: "East", 2: "North", 3: "West"}
TIERS = [0.0, 0.5, 1.0, 1.5]

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

# orientation palette: warm to cool, south to north
O_COL = {"South": "#b2182b", "West": "#ef8a62", "East": "#67a9cf", "North": "#2166ac"}
O_MARK = {"South": "o", "West": "s", "East": "D", "North": "^"}
V_COL = {"orientation": "#b2182b", "width": "#4d4d4d", "depth": "#878787"}
ACCENT = "#b2182b"


def load(path):
    d = pd.read_excel(path)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    d["orient"] = d["rotation"].map(ORIENT)
    d["ase"] = d["ASE_results"] * 100 if d["ASE_results"].max() <= 1.01 else d["ASE_results"]
    return d


def rng(q, col):
    m = q.groupby(col).sDA.mean()
    return m.max() - m.min()


def figure_7(d, out):
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    series = {"orientation": "orient", "width": "width", "depth": "depth"}
    labels = {"orientation": "Facade orientation", "width": "Room width",
              "depth": "Room depth"}
    ends = {}
    for key, col in series.items():
        y = [rng(d[d.HW == hw], col) for hw in TIERS]
        ax.plot(TIERS, y, marker="o", lw=2.0 if key == "orientation" else 1.5,
                ms=5, color=V_COL[key], label=labels[key],
                ls="-" if key != "depth" else "--")
        ax.annotate(f"{y[0]:.2f}", (TIERS[0], y[0]), xytext=(-6, 0),
                    textcoords="offset points", ha="right", va="center",
                    fontsize=8.5, color=V_COL[key])
        ends[key] = y[-1]
    # stacked end labels at H/W 1.5, ordered to avoid collision
    for i, key in enumerate(sorted(ends, key=lambda k: -ends[k])):
        ypos = 4.2 - i * 1.25
        ax.annotate(f"{ends[key]:.2f}", xy=(TIERS[-1], ends[key]), xytext=(1.64, ypos),
                    fontsize=8.5, color=V_COL[key], va="center",
                    arrowprops=dict(arrowstyle="-", color=V_COL[key], lw=0.6,
                                    shrinkA=0, shrinkB=3))
    ax.set_xticks(TIERS)
    ax.set_xticklabels([f"{t:.1f}" for t in TIERS])
    ax.set_xlabel("Street aspect ratio H/W")
    ax.set_ylabel("Range of mean sDA$_{300/50\\%}$\nacross the variable (pts)")
    ax.set_xlim(-0.3, 1.9)
    ax.set_ylim(0, 26)
    ax.grid(axis="y", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")
    plt.close(fig)


def figure_8(d, out):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7))
    order = ["South", "West", "East", "North"]

    ax = axes[0]
    for o in order:
        y = [d[(d.HW == hw) & (d.orient == o)].sDA.mean() for hw in TIERS]
        ax.plot(TIERS, y, marker=O_MARK[o], color=O_COL[o], lw=1.8, ms=5, label=o)
    spread0 = rng(d[d.HW == 0.0], "orient")
    spread3 = rng(d[d.HW == 1.5], "orient")
    ax.text(0.30, 55.5, f"orientation spread\n{spread0:.1f} pts  \u2192  {spread3:.2f} pts",
            fontsize=8.5, color="#4d4d4d", va="center", linespacing=1.4)
    ax.set_xticks(TIERS)
    ax.set_xticklabels([f"{t:.1f}" for t in TIERS])
    ax.set_xlabel("Street aspect ratio H/W")
    ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    ax.set_title("(a) Daylight autonomy", loc="left")
    ax.set_ylim(0, 62)
    ax.set_xlim(-0.15, 1.65)
    ax.grid(axis="y", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", handlelength=1.8)

    ax = axes[1]
    for o in order:
        y = [d[(d.HW == hw) & (d.orient == o)].ase.mean() for hw in TIERS]
        ax.plot(TIERS, y, marker=O_MARK[o], color=O_COL[o], lw=1.8, ms=5, label=o)
    ax.axhline(20, color=ACCENT, lw=0.9, ls="--", alpha=0.7)
    ax.text(1.62, 20.6, "20% limit", ha="right", fontsize=8.5, color=ACCENT)
    s3 = d[(d.HW == 1.5) & (d.orient == "South")].ase.mean()
    w3 = d[(d.HW == 1.5) & (d.orient == "West")].ase.mean()
    ax.annotate(f"South retains\n{s3:.1f}% at H/W 1.5\n(West {w3:.1f}%)",
                xy=(1.5, s3), xytext=(0.93, 13.5), fontsize=8.5, color=O_COL["South"],
                arrowprops=dict(arrowstyle="-", color=O_COL["South"], lw=0.7))
    ax.set_xticks(TIERS)
    ax.set_xticklabels([f"{t:.1f}" for t in TIERS])
    ax.set_xlabel("Street aspect ratio H/W")
    ax.set_ylabel("Mean ASE$_{1000,250}$ (%)")
    ax.set_title("(b) Annual sunlight exposure", loc="left")
    ax.set_ylim(0, 22.5)
    ax.set_xlim(-0.15, 1.65)
    ax.grid(axis="y", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout(w_pad=2.0)
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    args = ap.parse_args()
    d = load(args.baseline)
    figure_7(d, "figures/output/Figure_08")
    figure_8(d, "figures/output/Figure_09")

    print("range of means by variable and tier:")
    for hw in TIERS:
        q = d[d.HW == hw]
        print(f"  H/W {hw:.1f}: orientation {rng(q,'orient'):6.2f}  width {rng(q,'width'):5.2f}"
              f"  depth {rng(q,'depth'):5.2f}")
    print("\norientation, relative spread and CV:")
    for hw in TIERS:
        m = d[d.HW == hw].groupby("orient").sDA.mean()
        print(f"  H/W {hw:.1f}: {100*(m.max()-m.min())/m.max():5.1f}%   CV {100*m.std()/m.mean():5.1f}%")
    print("\nwritten: figure_7_design_levers.png/.pdf, figure_8_orientation.png/.pdf")


if __name__ == "__main__":
    main()
