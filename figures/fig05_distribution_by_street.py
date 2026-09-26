#!/usr/bin/env python3
# Manuscript Figure 5: Distribution of sDA300/50% by street aspect ratio.
# Run from the repository root:  python figures/fig05_distribution_by_street.py
"""
Figure 5 — distribution of sDA300/50% by street aspect ratio (Batch A, n = 4,320).

Panel (a): overlaid distributions, one per H/W tier, on a shared axis. Resolves the
           bimodality visible in Figure 4 into four separate populations.
Panel (b): reverse-cumulative curves per tier, so the share of cases reaching each
           compliance benchmark can be read directly rather than estimated.

Usage:
    python fig_5_distribution_by_canyon.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
BENCHMARKS = [40, 50]
BIN_WIDTH = 2.0

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

# darker = more obstructed, matching the direction of the effect
TIER_COLOUR = {0.0: "#bdd7e7", 0.5: "#6baed6", 1.0: "#2171b5", 1.5: "#08306b"}
ACCENT = "#b2182b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_05")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    tiers = sorted(d.HW.unique())

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.5))
    bins = np.arange(0, 72 + BIN_WIDTH, BIN_WIDTH)

    # ---- panel (a): overlaid distributions
    ax = axes[0]
    for hw in tiers:
        v = d.loc[d.HW == hw, "sDA"].to_numpy()
        w = np.full(v.size, 100 / v.size)
        ax.hist(v, bins=bins, weights=w, color=TIER_COLOUR[hw], alpha=0.75,
                label=f"H/W = {hw:.1f}   (mean {v.mean():.1f}%)")
    lo = d.loc[d.HW == 1.5, "sDA"].max()
    hi = d.loc[d.HW == 0.0, "sDA"].min()
    ax.axvspan(lo, hi, color="#f0f0f0", zorder=0)
    ax.annotate(f"no overlap\nbetween H/W 1.5\nand H/W 0.0",
                xy=((lo + hi) / 2, 36), ha="center", va="center",
                fontsize=8.5, color="#666666", linespacing=1.4)
    ax.set_xlabel("sDA$_{300/50\\%}$ (%)")
    ax.set_ylabel("Share of cases within tier (%)")
    ax.set_title("(a) Distribution by street aspect ratio", loc="left")
    ax.set_xlim(0, 72)
    ax.grid(axis="y", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right", handlelength=1.4, borderpad=0.2)

    # ---- panel (b): reverse cumulative
    ax = axes[1]
    xs = np.linspace(0, 72, 400)
    for hw in tiers:
        v = d.loc[d.HW == hw, "sDA"].to_numpy()
        ax.plot(xs, [(v >= x).mean() * 100 for x in xs],
                color=TIER_COLOUR[hw], lw=2.0, label=f"H/W = {hw:.1f}")
    for t in BENCHMARKS:
        ax.axvline(t, color=ACCENT, lw=0.9, ls="--", alpha=0.8)
        ax.text(t, 92, f"{t}%", ha="center", va="center", fontsize=9, color=ACCENT,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
    ax.set_xlabel("sDA$_{300/50\\%}$ (%)")
    ax.set_ylabel("Cases reaching at least this value (%)")
    ax.set_title("(b) Share meeting a given threshold", loc="left")
    ax.set_xlim(0, 72)
    ax.set_ylim(0, 100)
    ax.grid(lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout(w_pad=2.0)
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print(f"{'H/W':>5} {'n':>6} {'mean':>7} {'median':>7} {'max':>7} "
          + "  ".join(f"{'>=%d%%' % t:>8}" for t in BENCHMARKS))
    for hw in tiers:
        v = d.loc[d.HW == hw, "sDA"].to_numpy()
        shares = "  ".join(f"{(v >= t).mean()*100:7.2f}%" for t in BENCHMARKS)
        print(f"{hw:>5.1f} {v.size:>6} {v.mean():>7.2f} {np.median(v):>7.2f} "
              f"{v.max():>7.2f} {shares}")
    a, c = d.loc[d.HW == 0.0, "sDA"], d.loc[d.HW == 1.5, "sDA"]
    print(f"\nratio of means, H/W 0.0 to 1.5: {a.mean()/c.mean():.2f}")
    print(f"overlap: max at H/W 1.5 = {c.max():.2f}%, min at H/W 0.0 = {a.min():.2f}%")
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
