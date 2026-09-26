#!/usr/bin/env python3
# Manuscript Figure 10: Orientation, radial charts.
# Run from the repository root:  python figures/fig10_orientation_radial.py
"""
Radial orientation figure, normalised: each tier's polygon divided by its own mean
across orientations, so every tier is drawn at the same scale and only its shape
varies. A circle of radius 1 means orientation makes no difference.

Usage: python fig_8_radial_norm.py --baseline study/A-baseline.xlsx
"""
import argparse
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
ROT_TO_AZ = {0: 180, 1: 90, 2: 0, 3: 270}
AZ_LABEL = {0: "N", 90: "E", 180: "S", 270: "W"}
TIERS = [0.0, 0.5, 1.0, 1.5]
TIER_COLOUR = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
mpl.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.titlesize": 11,
                     "xtick.labelsize": 10.5, "ytick.labelsize": 8.5, "legend.fontsize": 9,
                     "savefig.dpi": 600, "savefig.bbox": "tight"})

ap = argparse.ArgumentParser()
ap.add_argument("--baseline", default="study/A-baseline.xlsx")
ap.add_argument("--out", default="figures/output/Figure_10")
a = ap.parse_args()
d = pd.read_excel(a.baseline)
d["HW"] = d["urban canyon toggle"].map(HW_MAP); d["az"] = d["rotation"].map(ROT_TO_AZ)
d["ase"] = d["ASE_results"] * 100 if d["ASE_results"].max() <= 1.01 else d["ASE_results"]
azs = [0, 90, 180, 270]; th = np.deg2rad(azs + [0])

fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.9), subplot_kw={"projection": "polar"})

def setup(ax, rmax, rt, title):
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad(azs)); ax.set_xticklabels([AZ_LABEL[z] for z in azs], fontweight="bold")
    ax.set_ylim(0, rmax); ax.set_yticks(rt); ax.set_yticklabels([f"{t:g}" for t in rt], color="#666666")
    ax.set_rlabel_position(22.5)
    for lab in ax.get_yticklabels():
        lab.set_bbox(dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ax.grid(lw=0.5, alpha=0.4); ax.spines["polar"].set_linewidth(0.6)
    ax.set_title(title, pad=14, loc="left")

def ring(ax, r, colour, ls="--"):
    c = np.linspace(0, 2 * np.pi, 200); ax.plot(c, np.full_like(c, r), ls=ls, lw=0.9, color=colour, alpha=0.75)

# (a) absolute sDA
ax = axes[0]
for hw in TIERS:
    q = d[d.HW == hw]; r = [q.loc[q.az == z, "sDA"].mean() for z in azs]
    ax.plot(th, r + [r[0]], color=TIER_COLOUR[hw], lw=2, marker="o", ms=4, label=f"H/W = {hw:.1f}")
    ax.fill(th, r + [r[0]], color=TIER_COLOUR[hw], alpha=0.10)
ring(ax, 40, "#b2182b"); ax.text(np.deg2rad(135), 42, "40%", color="#b2182b", fontsize=8.5, ha="center")
setup(ax, 62, [10, 20, 30, 40, 50], "(a) sDA$_{300/50\\%}$, absolute (%)")

# (b) normalised shape
ax = axes[1]
ax.plot(th, [1, 1, 1, 1, 1], ls=":", lw=1.3, color="#4d4d4d", zorder=1)   # uniform = square
for hw in TIERS:
    q = d[d.HW == hw]; r = np.array([q.loc[q.az == z, "sDA"].mean() for z in azs]); r = r / r.mean()
    ax.plot(th, list(r) + [r[0]], color=TIER_COLOUR[hw], lw=2, marker="o", ms=4, zorder=3)
setup(ax, 1.4, [0.8, 1.0, 1.2], "(b) sDA$_{300/50\\%}$, relative to tier mean")
ax.set_ylim(0.6, 1.4)
ax.text(np.deg2rad(315), 1.30, "dotted: no\norientation effect", color="#4d4d4d",
        fontsize=8, ha="center", linespacing=1.2)

# (c) absolute ASE
ax = axes[2]
for hw in TIERS:
    q = d[d.HW == hw]; r = [q.loc[q.az == z, "ase"].mean() for z in azs]
    ax.plot(th, r + [r[0]], color=TIER_COLOUR[hw], lw=2, marker="o", ms=4)
    ax.fill(th, r + [r[0]], color=TIER_COLOUR[hw], alpha=0.10)
ring(ax, 20, "#b2182b"); ax.text(np.deg2rad(135), 20.8, "20%", color="#b2182b", fontsize=8.5, ha="center")
setup(ax, 22, [5, 10, 15, 20], "(c) ASE$_{1000,250}$, absolute (%)")

h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.05),
           handlelength=1.6, columnspacing=1.6)
fig.tight_layout(w_pad=2.4)
for ext in ("png", "pdf"): fig.savefig(f"{a.out}.{ext}")
print("normalised radius (S, W, E, N) per tier:")
for hw in TIERS:
    q = d[d.HW == hw]; r = np.array([q.loc[q.az == z, "sDA"].mean() for z in [180, 270, 90, 0]])
    print(f"  H/W {hw:.1f}: " + "  ".join(f"{v:.3f}" for v in r / r.mean()))
