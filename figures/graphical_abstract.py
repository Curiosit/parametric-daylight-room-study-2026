#!/usr/bin/env python3
# Graphical abstract.
# Run from the repository root:  python figures/graphical_abstract.py
"""Graphical abstract sketch for the revised LEUKOS manuscript.

Zones, left to right:
  1. Street section: room with window, street W, opposing building H.
  2. Result 1: share of Batch A configurations reaching a given sDA, by H/W.
  3. Result 2: Batch C, mean sDA against effective aperture, by H/W.
  4. Message.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
TIER = {0.0: "#9ecae1", 0.5: "#4292c6", 1.0: "#2171b5", 1.5: "#08306b"}
INK, SOFT, ACCENT = "#1c2230", "#6b7280", "#b2182b"

mpl.rcParams.update({"font.family": "sans-serif", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.9, "savefig.dpi": 300})

A = pd.read_excel("study/A-baseline.xlsx")
A["HW"] = A["urban canyon toggle"].map(HW_MAP)
C = pd.read_excel("study/C-wfr-x-vt.xlsx")
C["HW"] = C["urban canyon toggle"].map(HW_MAP)
C["eff"] = (1 / C["ratio"]) * C["VT"] / ((1 / 8) * 0.64)

fig = plt.figure(figsize=(14, 5.6))
gs = fig.add_gridspec(1, 4, width_ratios=[1.3, 1.0, 1.0, 1.0], wspace=0.42,
                      left=0.015, right=0.985, top=0.80, bottom=0.17)

# ---------------------------------------------------------------- 1. section
ax = fig.add_subplot(gs[0, 0])
ax.set_xlim(-0.5, 12.2); ax.set_ylim(-1.6, 10.4); ax.set_aspect("equal"); ax.axis("off")
ground = -0.05
ax.plot([-0.4, 12.1], [ground, ground], color=INK, lw=1.2)
# building with the room on ground floor
ax.add_patch(Rectangle((0, 0), 3.2, 8.2, fc="#eef0f3", ec=INK, lw=1.2))
ax.add_patch(Rectangle((0.25, 0.25), 2.7, 2.7, fc="#f7e9c8", ec=INK, lw=1.0))    # room
ax.add_patch(Rectangle((2.95, 0.95), 0.25, 1.6, fc="#bcd9ee", ec=INK, lw=1.0))   # window
for y in (3.2, 5.7):
    ax.plot([0, 3.2], [y, y], color=SOFT, lw=0.6)
ax.text(1.6, 1.55, "room", ha="center", va="center", fontsize=10, color=INK)
# opposing building
x0, H, W = 3.2 + 5.2, 5.2, 5.2
ax.add_patch(Rectangle((x0, 0), 3.3, H, fc="#d9dce1", ec=INK, lw=1.2))
# sky angle from window head
ax.plot([3.2, x0], [2.55, H], color=ACCENT, lw=1.1, ls="--")
ax.add_patch(Polygon([[3.2, 2.55], [x0, H], [x0 + 0.01, 10.3], [3.2, 10.3]],
                     closed=True, fc="#fff4c2", ec="none", alpha=0.55, zorder=0))
ax.text(4.55, 7.3, "visible sky", fontsize=9.5, color="#8a6d00", rotation=0)
# dimension arrows
ax.add_patch(FancyArrowPatch((3.2, -0.75), (x0, -0.75), arrowstyle="<->", mutation_scale=11, lw=1.0, color=INK))
ax.text((3.2 + x0) / 2, -1.35, "W", ha="center", fontsize=13, weight="bold", color=INK)
ax.add_patch(FancyArrowPatch((x0 + 3.75, 0), (x0 + 3.75, H), arrowstyle="<->", mutation_scale=11, lw=1.0, color=INK))
ax.text(x0 + 4.05, H / 2, "H", va="center", fontsize=13, weight="bold", color=INK)
ax.text(8.4, 7.2, "H/W = 0.0, 0.5,\n1.0, 1.5", ha="left", fontsize=10, color=INK, linespacing=1.3)
ax.set_title("7,200 annual daylight simulations", loc="left", fontsize=12.5, weight="bold", color=INK, pad=10)
ax.text(0.0, -0.09, "Room width and depth · window height and sill\norientation · window-to-floor ratio 1/8–1/5\nglazing VT 0.64–0.76 · Warsaw and Berlin",
        fontsize=9.3, color=SOFT, va="top", linespacing=1.4, transform=ax.transAxes)

# ---------------------------------------------------------------- 2. collapse
ax = fig.add_subplot(gs[0, 1])
xs = np.linspace(0, 70, 300)
for hw in (0.0, 0.5, 1.0, 1.5):
    v = A.loc[A.HW == hw, "sDA"].to_numpy()
    ax.plot(xs, [(v >= x).mean() * 100 for x in xs], color=TIER[hw], lw=2.4,
            label=f"H/W {hw:.1f}")
ax.axvline(40, color=ACCENT, lw=1.1, ls="--")
ax.text(41.5, 94, "40% benchmark", color=ACCENT, fontsize=9.5, va="top")
ax.set_xlim(0, 70); ax.set_ylim(0, 102)
ax.set_xlabel("sDA$_{300/50\\%}$ (%)")
ax.set_ylabel("Rooms reaching this value (%)")
ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.02, 0.82), fontsize=9.5, handlelength=1.5)
ax.set_title("0 of 3,240 obstructed rooms\nreach 40% sDA", loc="left", fontsize=12.5, weight="bold", color=INK, pad=24, linespacing=1.25)
ax.text(0, 1.035, "all comply with the 1/8 ratio", transform=ax.transAxes, fontsize=10, color=SOFT)

# ---------------------------------------------------------------- 3. failed fix
ax = fig.add_subplot(gs[0, 2])
for hw in (0.0, 0.5, 1.0, 1.5):
    g = C[C.HW == hw].groupby("eff")["sDA-horizontal"].mean()
    ax.plot(g.index, g.values, "o-", color=TIER[hw], lw=2.2, ms=3.8)
ax.axhline(40, color=ACCENT, lw=1.1, ls="--")
ax.set_xlim(0.95, 1.97); ax.set_ylim(0, 90)
ax.set_xticks([1.0, 1.4583, 1.9])
ax.set_xticklabels(["1/8\n0.64", "1/6\n0.70", "1/5\n0.76"])
ax.set_xlabel("Window-to-floor ratio and glazing VT", labelpad=4)
ax.set_ylabel("Mean sDA$_{300/50\\%}$ (%)")
for hw, y in ((1.0, 29), (1.5, 17.5)):
    ax.text(1.93, y, f"H/W {hw:.1f}", ha="right", fontsize=9.5, color=TIER[hw])
ax.set_title("No tested ratio reaches 40%\nat H/W ≥ 1.0", loc="left", fontsize=12.5, weight="bold", color=INK, pad=24, linespacing=1.25)
ax.text(0, 1.035, "larger windows, clearer glass", transform=ax.transAxes, fontsize=10, color=SOFT)

# ---------------------------------------------------------------- 4. message
ax = fig.add_subplot(gs[0, 3]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0.0, 1.0, "The 1/8 window-to-floor\nratio regulates room size.", fontsize=13.5,
        color=INK, va="top", linespacing=1.35, style="italic")
ax.text(0.0, 0.77, "0.4%", fontsize=32, color=SOFT, weight="bold", va="top")
ax.text(0.0, 0.58, "of daylight variance is explained\nby room width, depth and\nwindow height.", fontsize=10.5, color=SOFT, va="top", linespacing=1.3)
ax.text(0.0, 0.36, "98%", fontsize=32, color=ACCENT, weight="bold", va="top")
ax.text(0.0, 0.17, "is explained by street geometry\nand orientation, which the ratio\ndoes not contain.", fontsize=10.5, color=INK, va="top", linespacing=1.3)

fig.savefig("figures/output/graphical_abstract.png")
fig.savefig("figures/output/graphical_abstract.pdf")
print("saved")
