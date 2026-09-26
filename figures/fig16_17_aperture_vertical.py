#!/usr/bin/env python3
# Manuscript Figure 16, 17: Effective aperture; eye-height against work-plane daylight.
# Run from the repository root:  python figures/fig16_17_aperture_vertical.py
"""
Figures for the Batch C sections (Warsaw, H_win 1.7 m, sill 0.80 m, n = 2,160).

Figure 15 — response of mean sDA300/50% to effective aperture, by street aspect
ratio. Effective aperture = WFR x VT, normalised to the prescribed 1/8 at 0.64.
Dashed lines extend a linear fit to the 40% benchmark; because the response is
concave, the extrapolated aperture is a lower bound on what would be required.
The shaded region marks apertures that cannot be built as a single window in the
deepest (7 m) room at a 1.7 m clear height, where the required width exceeds the
available facade.

Figure 16 — horizontal work-plane sDA300/50% against the equivalent criterion on
the window-facing vertical plane at 1.2 m, for south- and north-facing rooms
(1,080 cases). The vertical quantity is the share of vertical sensors whose
daylight autonomy at 300 lux reaches 50% of occupied hours: photopic, not mEDI.

Usage:
    python fig_batch_c.py --sweep study/C-wfr-x-vt.xlsx
"""

from __future__ import annotations

import argparse

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
TIER_COLOUR = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
CLEAR_H, BASE = 1.7, (1 / 8) * 0.64

mpl.rcParams.update({
    "font.family": "sans-serif", "font.size": 10, "axes.labelsize": 10.5,
    "axes.titlesize": 11, "xtick.labelsize": 9.5, "ytick.labelsize": 10,
    "legend.fontsize": 8.8, "axes.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "figure.dpi": 120, "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def load(path):
    c = pd.read_excel(path)
    c["HW"] = c["urban canyon toggle"].map(HW_MAP)
    c["or"] = c["rotation"].map({0: "S", 1: "E", 2: "N", 3: "W"})
    c["sda"] = c["sDA-horizontal"]
    c["eff"] = (1 / c["ratio"]) * c["VT"] / BASE
    return c


def figure_15(c, out):
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    lim7 = (CLEAR_H / 7) / (1 / 8)      # effective aperture at VT 0.64 filling a 7 m-deep room's wall
    ax.axvspan(lim7, 3.3, color="#f0f0f0", zorder=0)
    ax.text(lim7 + 0.05, 3, "aperture exceeds\nthe facade of a\n7 m-deep room",
            fontsize=8, color="#777777", va="bottom", linespacing=1.3)
    ax.axhline(40, color="#4d4d4d", lw=0.9, ls="--")
    ax.text(2.35, 41.2, "sDA benchmark 40%", ha="center", fontsize=8.5, color="#4d4d4d")

    for hw in sorted(c.HW.unique()):
        g = c[c.HW == hw].groupby("eff").sda.mean()
        ax.plot(g.index, g.values, "o-", color=TIER_COLOUR[hw], lw=1.8, ms=4,
                label=f"H/W = {hw:.1f}", zorder=3)
        k = np.polyfit(g.index, g.values, 1)
        need = (40 - k[1]) / k[0]
        if 1.9 < need <= 3.3:
            xs = np.linspace(g.index.max(), need, 20)
            ax.plot(xs, np.polyval(k, xs), ls="--", lw=1.2, color=TIER_COLOUR[hw], zorder=2)
            ax.plot([need], [40], "o", mfc="white", mec=TIER_COLOUR[hw], ms=6, zorder=4)
            ax.annotate(f"≥ {need:.2f}", (need, 40), xytext=(0, -15),
                        textcoords="offset points", ha="center", fontsize=8.5,
                        color=TIER_COLOUR[hw])
        elif need > 3.3:
            ax.annotate(f"H/W 1.5 requires ≥ {need:.1f}  →", (3.25, np.polyval(k, 3.25)),
                        ha="right", fontsize=8.3, color=TIER_COLOUR[hw],
                        xytext=(0, 7), textcoords="offset points")

    r = c[(c.ratio == 6) & (c.VT == 0.70)]
    for hw in (1.0, 1.5):
        y = r[r.HW == hw].sda.mean()
        ax.plot([r.eff.iloc[0]], [y], marker="*", ms=12, color="#b2182b", zorder=5,
                mec="white", mew=0.6)
    ax.annotate("1/6 at VT 0.70", (r.eff.iloc[0], r[r.HW == 1.0].sda.mean()),
                xytext=(-6, 13), textcoords="offset points", fontsize=8.5,
                color="#b2182b", ha="right")

    ax.set_xlim(0.92, 3.3)
    ax.set_ylim(0, 88)
    ax.set_xlabel("Relative effective aperture (WFR × VT; 1/8 at 0.64 = 1)")
    ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    ax.grid(lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left")

    top = ax.secondary_xaxis("top", functions=(lambda e: e, lambda e: e))
    wfr = [8, 6, 5, 4, 3]
    top.set_xticks([(1 / w) / (1 / 8) for w in wfr])
    top.set_xticklabels([f"1/{w}" for w in wfr])
    top.set_xlabel("Equivalent WFR at VT 0.64", fontsize=9.5)
    top.tick_params(labelsize=9)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")
    plt.close(fig)


def figure_16(c, out):
    a = c[c["or"].isin(["S", "N"])].copy()
    a["toward"] = np.where(a["or"] == "S", a.sDA_vert_south_facing, a.sDA_vert_north_facing)
    b = a[(a.ratio == 8) & (a.VT == 0.64)]
    tiers = [0.0, 0.5, 1.0, 1.5]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6))
    for ax, o, name in ((axes[0], "S", "South-facing"), (axes[1], "N", "North-facing")):
        q = b[b["or"] == o]
        h = [q[q.HW == t].sda.mean() for t in tiers]
        v = [q[q.HW == t].toward.mean() for t in tiers]
        ax.plot(tiers, h, "o-", color="#4d4d4d", lw=1.8, ms=5, label="horizontal, 0.8 m")
        ax.plot(tiers, v, "s-", color="#d95f02", lw=1.8, ms=5,
                label="vertical, 1.2 m, window-facing")
        for t, hh, vv in zip(tiers, h, v):
            ax.text(t, max(hh, vv) + 3, f"×{vv / hh:.2f}", ha="center", fontsize=8,
                    color="#d95f02")
        ax.set_xticks(tiers)
        ax.set_xticklabels([f"{t:.1f}" for t in tiers])
        ax.set_xlabel("Street aspect ratio H/W")
        ax.set_title(f"({'a' if o == 'S' else 'b'}) {name}", loc="left")
        ax.set_ylim(0, 100)
        ax.set_xlim(-0.15, 1.65)
        ax.grid(lw=0.4, alpha=0.3)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Share of sensors with DA$_{300}$ ≥ 50% (%)")
    axes[1].legend(frameon=False, loc="upper right")
    fig.tight_layout(w_pad=2.0)
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", default="study/C-wfr-x-vt.xlsx")
    args = ap.parse_args()
    c = load(args.sweep)
    figure_15(c, "figures/output/Figure_16")
    figure_16(c, "figures/output/Figure_17")
    print("written: figure_15_response_surface.png/.pdf, figure_16_vertical.png/.pdf")


if __name__ == "__main__":
    main()
