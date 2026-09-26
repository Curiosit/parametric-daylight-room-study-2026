#!/usr/bin/env python3
# Manuscript Figure 15: Window-to-floor ratio and glazing transmittance (Batch C).
# Run from the repository root:  python figures/fig15_wfr_vt.py
"""
Figure 15 — mean sDA300/50% by window-to-floor ratio (x axis) and visible
transmittance (lines), one panel per street aspect ratio (Batch C, n = 2,160;
60 configurations per point: 3 widths x 5 depths x 4 orientations).

This shows the two variables separately, before Figure 16 combines them into a
single effective aperture. Shared y axis so the 40% benchmark and the gap between
tiers are read on one scale.

Usage:
    python fig_15_wfr_vt.py --sweep study/C-wfr-x-vt.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
RATIOS = [8, 6, 5]
VT_STYLE = {0.64: ("#bdbdbd", "o", "-"), 0.70: ("#737373", "s", "-"),
            0.76: ("#252525", "D", "-")}

mpl.rcParams.update({
    "font.family": "sans-serif", "font.size": 10, "axes.labelsize": 10.5,
    "axes.titlesize": 10.5, "xtick.labelsize": 9.5, "ytick.labelsize": 10,
    "legend.fontsize": 8.8, "axes.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "figure.dpi": 120, "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", default="study/C-wfr-x-vt.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_15")
    args = ap.parse_args()

    c = pd.read_excel(args.sweep)
    c["HW"] = c["urban canyon toggle"].map(HW_MAP)
    c["sda"] = c["sDA-horizontal"]
    x = [1 / r for r in RATIOS]                     # glazing fraction of floor area

    fig, axes = plt.subplots(1, 4, figsize=(10.2, 3.4), sharey=True)
    for ax, hw in zip(axes, [0.0, 0.5, 1.0, 1.5]):
        q = c[c.HW == hw]
        ax.axhline(40, color="#b2182b", lw=0.9, ls="--", alpha=0.8)
        for vt, (col, mk, ls) in VT_STYLE.items():
            y = [q[(q.ratio == r) & (q.VT == vt)].sda.mean() for r in RATIOS]
            ax.plot(x, y, marker=mk, ls=ls, color=col, lw=1.8, ms=5, label=f"VT {vt:.2f}")
        # spread due to VT at 1/8 and 1/5, annotated at the right
        lo = q[(q.ratio == 5) & (q.VT == 0.64)].sda.mean()
        hi = q[(q.ratio == 5) & (q.VT == 0.76)].sda.mean()
        ax.plot([0.207, 0.207], [lo, hi], color="#555555", lw=0.9)
        for yy in (lo, hi):
            ax.plot([0.2055, 0.2085], [yy, yy], color="#555555", lw=0.9)
        ax.text(0.209, (lo + hi) / 2, f"{hi - lo:.1f}", fontsize=8, color="#555555",
                va="center")
        star = q[(q.ratio == 6) & (q.VT == 0.70)].sda.mean()
        ax.plot([1 / 6], [star], "*", ms=11, color="#b2182b", mec="white", mew=0.5, zorder=5)
        ax.set_xticks(x)
        ax.set_xticklabels(["1/8", "1/6", "1/5"])
        ax.set_xlim(0.115, 0.222)
        ax.set_title(f"H/W = {hw:.1f}", loc="left")
        ax.set_xlabel("Window-to-floor ratio")
        ax.grid(lw=0.4, alpha=0.3)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    axes[0].set_ylim(0, 90)
    axes[0].text(0.170, 36.0, "40% benchmark", fontsize=8, color="#b2182b", ha="center")
    axes[0].legend(frameon=False, loc="upper left", handlelength=1.8, labelspacing=0.3)
    axes[3].text(0.118, 86, "★  1/6 at VT 0.70", fontsize=8.5, color="#b2182b", va="top")

    fig.tight_layout(w_pad=0.8)
    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    print("mean sDA, rows = VT, cols = ratio")
    for hw in [0.0, 0.5, 1.0, 1.5]:
        q = c[c.HW == hw]
        print(f"H/W {hw:.1f}")
        for vt in VT_STYLE:
            print(f"   VT {vt:.2f}: " + "  ".join(
                f"1/{r} {q[(q.ratio == r) & (q.VT == vt)].sda.mean():6.2f}" for r in RATIOS))
    print(f"written: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
