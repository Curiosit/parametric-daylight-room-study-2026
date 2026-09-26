#!/usr/bin/env python3
# Manuscript Figure 4: Distribution of sDA300/50% across Batch A.
# Run from the repository root:  python figures/fig04_distribution.py
"""
Figure 4 — distribution of sDA300/50% across Batch A (n = 4,320).

Left axis  : histogram, percentage of cases per bin.
Right axis : reverse-cumulative curve, i.e. the share of cases reaching at least
             a given sDA. This is the quantity the compliance argument rests on,
             and reading it off a histogram is otherwise guesswork.

Benchmarks marked: 40% (LEED, 1 point), 50% and 55%.

Usage:
    python fig_4_distribution.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BENCHMARKS = [40, 50, 55]
BIN_WIDTH = 2.5

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
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})

BAR = "#6baed6"
BAR_EDGE = "#2171b5"
CUM = "#08306b"
ACCENT = "#b2182b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_04")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    v = d["sDA"].to_numpy()
    n = v.size

    fig, ax = plt.subplots(figsize=(7.2, 3.8))

    bins = np.arange(0, np.ceil(v.max() / BIN_WIDTH) * BIN_WIDTH + BIN_WIDTH, BIN_WIDTH)
    ax.hist(v, bins=bins, weights=np.full(n, 100 / n),
            color=BAR, edgecolor=BAR_EDGE, lw=0.5)
    ax.set_xlabel("sDA$_{300/50\\%}$ (%)")
    ax.set_ylabel("Share of cases (%)")
    ax.set_xlim(0, 72)
    ax.set_ylim(0, 19.5)
    ax.grid(axis="y", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)

    # reverse cumulative: share of cases at or above x
    xs = np.linspace(0, 72, 400)
    ys = [(v >= x).mean() * 100 for x in xs]
    ax2 = ax.twinx()
    ax2.plot(xs, ys, color=CUM, lw=1.8)
    ax2.set_ylabel("Cases reaching at least this value (%)", color=CUM)
    ax2.tick_params(axis="y", colors=CUM)
    ax2.set_ylim(0, 102)
    ax2.spines["top"].set_visible(False)

    for t in BENCHMARKS:
        share = (v >= t).mean() * 100
        ax.axvline(t, color=ACCENT, lw=0.9, ls="--", alpha=0.8)
        ax2.plot([t], [share], "o", color=ACCENT, ms=5, zorder=5)
        ax.annotate(f"{t}%", xy=(t, ax.get_ylim()[1]), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=9,
                    color=ACCENT)

    # compliance shares as a compact block rather than three colliding callouts
    lines = [f"$\\geq$ {t}%:  {(v >= t).mean()*100:5.2f}%" for t in BENCHMARKS]
    ax.text(0.985, 0.95, "Cases reaching\n" + "\n".join(lines),
            transform=ax.transAxes, ha="right", va="top", fontsize=9.5,
            color=ACCENT, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=ACCENT, lw=0.7))

    mean, med = v.mean(), np.median(v)
    ax.axvline(mean, color="#4d4d4d", lw=1.1)
    ax.annotate(f"mean {mean:.2f}%", xy=(mean, ax.get_ylim()[1] * 0.72),
                xytext=(6, 0), textcoords="offset points",
                fontsize=9.5, color="#4d4d4d", va="top")

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print(f"n = {n}   mean {mean:.2f}   median {med:.2f}   "
          f"sd {v.std(ddof=1):.2f}   min {v.min():.2f}   max {v.max():.2f}")
    for t in BENCHMARKS:
        print(f"  >= {t}%: {(v >= t).sum():5d} cases ({(v >= t).mean()*100:5.2f}%)")
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
