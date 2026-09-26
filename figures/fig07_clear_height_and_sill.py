#!/usr/bin/env python3
# Manuscript Figure 7: Window clear height and sill position (Batches A and B).
# Run from the repository root:  python figures/fig07_clear_height_and_sill.py
"""
Figure 7 — window clear height and window position (Batches A and B).

(a) Mean sDA300/50% by window clear height at a uniform 0.67 m sill, one line
    per street aspect ratio (Batch B, Berlin, room widths 3.0, 5.0 and 7.0 m).
(b) The same room (5.0 x 6.0 m, Berlin, 1.7 m clear height, unobstructed),
    facing south and north: change in DA300 at each sensor when the sill is
    lowered from 0.80 m (Batch A) to 0.67 m (Batch B) at constant clear height
    and glazing area. Solid and dashed white lines mark DA300 = 50% at the
    0.80 m and 0.67 m sill respectively.
"""
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon, FancyArrowPatch
from matplotlib.transforms import Affine2D
from matplotlib.lines import Line2D

A_PATH = "study/A-baseline.xlsx"
B_PATH = "study/B-sill-control.xlsx"
HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
ORIENT = {0: "South", 1: "East", 2: "North", 3: "West"}
TIER = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
INK, SOFT = "#1c2230", "#6b7280"
SPACING, WALL = 0.25, 0.20
HEIGHTS = [1.4, 1.7, 2.0]
DCMAP = mpl.colormaps["RdBu"]          # red = loss, blue = gain
DNORM = mpl.colors.TwoSlopeNorm(vmin=-16, vcenter=0, vmax=16)

mpl.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.labelsize": 11,
                     "axes.titlesize": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 600, "savefig.bbox": "tight"})


def parse(c):
    return np.fromstring(str(c).replace(",", "."), sep=";")


def rot(x, y, cx, cy, deg):
    r = math.radians(deg)
    return (cx + (x - cx) * math.cos(r) - (y - cy) * math.sin(r),
            cy + (x - cx) * math.sin(r) + (y - cy) * math.cos(r))


def panel_a(ax, B):
    B = B.assign(HW=B["urban canyon toggle"].map(HW_MAP))
    for hw in sorted(B.HW.unique(), reverse=True):
        q = B[B.HW == hw]
        y = [q[q.win_height == h].sDA.mean() for h in HEIGHTS]
        ax.plot(HEIGHTS, y, "o-", color=TIER[hw], lw=1.9, ms=5, label=f"H/W = {hw:.1f}")
        ax.annotate(f"{y[-1]:.1f}", (HEIGHTS[-1], y[-1]), textcoords="offset points",
                    xytext=(7, -3), fontsize=9, color=TIER[hw])
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.78), fontsize=9)
    ax.set_xticks(HEIGHTS)
    ax.set_xlim(1.3, 2.18); ax.set_ylim(0, 46)
    ax.set_xlabel("Window clear height (m)")
    ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
    ax.set_title("(a) Clear height, uniform 0.67 m sill", loc="left", pad=8)
    ax.grid(axis="y", lw=0.4, alpha=0.35); ax.set_axisbelow(True)


def plan_delta(ax, a, b, pad=1.1):
    width, depth = float(a["width"]), float(a["depth"])
    nw, nd = round(width / SPACING), round(depth / SPACING)
    g80, g67 = parse(a["raw_DA"]).reshape(nw, nd), parse(b["raw_DA"]).reshape(nw, nd)
    delta = g67 - g80
    r = int(a["rotation"])
    win_w = float(a["window_area"]) / float(a["win_height"])
    angle = 90 + 90 * r
    cx, cy = depth / 2, width / 2
    T = Affine2D().rotate_deg_around(cx, cy, angle) + ax.transData

    ax.imshow(delta, origin="lower", extent=[0, depth, 0, width], cmap=DCMAP, norm=DNORM,
              interpolation="nearest", transform=T, zorder=1)
    xs, ys = (np.arange(nd) + 0.5) * SPACING, (np.arange(nw) + 0.5) * SPACING
    for g, ls in ((g80, "-"), (g67, "--")):
        if g.min() < 50 < g.max():
            ax.contour(xs, ys, g, levels=[50], colors=INK, linewidths=1.3, linestyles=ls,
                       transform=T, zorder=3)
    y0, y1 = cy - win_w / 2, cy + win_w / 2
    for w in ([(-WALL, width), (depth + WALL, width), (depth + WALL, width + WALL), (-WALL, width + WALL)],
              [(depth, -WALL), (depth + WALL, -WALL), (depth + WALL, width + WALL), (depth, width + WALL)],
              [(-WALL, -WALL), (depth + WALL, -WALL), (depth + WALL, 0), (-WALL, 0)],
              [(-WALL, 0), (0, 0), (0, y0), (-WALL, y0)],
              [(-WALL, y1), (0, y1), (0, width), (-WALL, width)]):
        ax.add_patch(Polygon(w, closed=True, fc=INK, ec="none", transform=T, zorder=4))
    ax.add_patch(Polygon([(-WALL, y0), (0, y0), (0, y1), (-WALL, y1)], closed=True,
                         fc="#bcd9ee", ec=INK, lw=0.6, transform=T, zorder=4))
    corners = [(-pad, -pad), (depth + pad, -pad), (depth + pad, width + pad), (-pad, width + pad)]
    pts = [rot(x, y, cx, cy, angle) for x, y in corners]
    ax.set_xlim(min(p[0] for p in pts), max(p[0] for p in pts))
    ax.set_ylim(min(p[1] for p in pts), max(p[1] for p in pts))
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyArrowPatch((0.94, 0.80), (0.94, 0.96), transform=ax.transAxes,
                                 arrowstyle="-|>", mutation_scale=11, color=INK, lw=1.1))
    ax.text(0.94, 0.75, "N", transform=ax.transAxes, ha="center", va="top", fontsize=9, color=INK)
    s80, s67 = 100 * np.mean(g80 >= 50), 100 * np.mean(g67 >= 50)
    ax.set_title(f"{ORIENT[r]}-facing", loc="left", fontsize=10.5, weight="bold", color=INK, pad=3)
    ax.text(0.0, -0.03, f"sDA {s80:.1f}% → {s67:.1f}% ({s67 - s80:+.1f})", transform=ax.transAxes,
            va="top", fontsize=10, color=INK, weight="bold")
    ax.text(0.0, -0.115, f"mean DA change {delta.mean():+.1f} pts, largest {delta.min():+.1f}",
            transform=ax.transAxes, va="top", fontsize=9, color=SOFT)
    return s80, s67, delta


def main():
    A = pd.read_excel(A_PATH)
    B = pd.read_excel(B_PATH)
    A = A[A.Location == "Berlin"]
    sel = dict(width=5.0, depth=6, win_height=1.7)

    fig = plt.figure(figsize=(11.2, 4.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 0.95, 0.95], wspace=0.28,
                          left=0.06, right=0.9, top=0.86, bottom=0.2)
    panel_a(fig.add_subplot(gs[0, 0]), B)

    axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])]
    for ax, r in zip(axes, (0, 2)):
        pick = lambda d: d[(d.width == sel["width"]) & (d.depth == sel["depth"]) &
                           (d.win_height == sel["win_height"]) & (d.rotation == r) &
                           (d["urban canyon toggle"] == 0)].iloc[0]
        s80, s67, delta = plan_delta(ax, pick(A), pick(B))
        print(f"{ORIENT[r]}: sDA {s80:.2f} -> {s67:.2f} | mean dDA {delta.mean():.2f} | min {delta.min():.1f}")
    fig.text(0.40, 0.92, "(b) Sill lowered from 0.80 m to 0.67 m, same window, same room",
             fontsize=11, color=INK)

    cax = fig.add_axes([0.915, 0.28, 0.012, 0.52])
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=DNORM, cmap=DCMAP), cax=cax)
    cb.set_label("Change in DA$_{300}$ (percentage points)")
    cb.outline.set_visible(False)
    handles = [Line2D([], [], color=INK, lw=1.3, ls="-", label="DA 50%, sill 0.80 m"),
               Line2D([], [], color=INK, lw=1.3, ls="--", label="DA 50%, sill 0.67 m")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.66, -0.02), ncol=2,
               frameon=False, fontsize=9.5, handlelength=2.2)

    for ext in ("png", "pdf"):
        fig.savefig(f"figures/output/Figure_07.{ext}")
    print("written Figure_07")


if __name__ == "__main__":
    main()
