#!/usr/bin/env python3
"""
Room plan visualisation of daylight autonomy, updated for the revised manuscript.

Changes from the original notebook cell
- Orientation corrected: the model rotates counter-clockwise, so rotation
  0 = South, 1 = East, 2 = North, 3 = West (the old map had East and West swapped).
- Metrics recomputed from the per-sensor arrays on the full grid (sDA300/50% with
  DA >= 50%, mean DA, ASE1000,250 with > 250 h). The old culled_sDA column carried
  the normalisation error and is no longer used.
- Plans drawn with north up, a north arrow, the window as an opening, the DA = 50%
  contour (the boundary of the area counted in sDA), and the opposing building
  as a hatched bar when the street is obstructed.
- Column names follow the cleaned dataset (width, depth, win_height, sill_h, ...).

Usage
    python room_viz.py                       # Figure 3, four default cases
    python room_viz.py A-00076 A-01156 ...   # any cases, 2 x 2 or 1 x N
"""
import math
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon, FancyArrowPatch
from matplotlib.transforms import Affine2D

DATA = "/mnt/user-data/uploads/01-baseline.xlsx"
SPACING = 0.25          # sensor spacing (m)
WALL = 0.20             # drawn wall thickness (m)
HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
ORIENT = {0: "South", 1: "East", 2: "North", 3: "West"}   # counter-clockwise model rotation
CMAP = mpl.colormaps["viridis"]
INK, SOFT = "#1c2230", "#6b7280"

mpl.rcParams.update({"font.family": "sans-serif", "font.size": 10,
                     "savefig.dpi": 600, "savefig.bbox": "tight"})


def parse(cell):
    return np.fromstring(str(cell).replace(",", "."), sep=";")


def metrics(row):
    da = parse(row["raw_DA"])
    ase_h = parse(row["raw_ASE_hours"])
    return dict(sda=100 * np.mean(da >= 50), mean_da=da.mean(),
                ase=100 * np.mean(ase_h > 250), n=da.size)


def rot(x, y, cx, cy, deg):
    r = math.radians(deg)
    return (cx + (x - cx) * math.cos(r) - (y - cy) * math.sin(r),
            cy + (x - cx) * math.sin(r) + (y - cy) * math.cos(r))


def plot_room(ax, row, extent_pad=1.6):
    """Draw one room in plan, north up. Local frame: x = depth (window wall at x = 0),
    y = width. The local frame is rotated so the window faces its true orientation."""
    width, depth = float(row["width"]), float(row["depth"])
    h_clear, sill = float(row["win_height"]), float(row["sill_h"])
    win_w = float(row["window_area"]) / h_clear
    r = int(row["rotation"])
    hw = HW_MAP[int(row["urban canyon toggle"])]
    nw, nd = round(width / SPACING), round(depth / SPACING)
    grid = parse(row["raw_DA"]).reshape((nw, nd))      # width-major: rows = width, cols = depth

    angle = 90 + 90 * r            # window wall (x = 0) → S at 90°, E 180°, N 270°, W 360°
    cx, cy = depth / 2, width / 2
    T = Affine2D().rotate_deg_around(cx, cy, angle) + ax.transData

    ax.imshow(grid, origin="lower", extent=[0, depth, 0, width], cmap=CMAP,
              vmin=0, vmax=100, interpolation="nearest", transform=T, zorder=1)
    # boundary of the area counted in sDA300/50%
    xs = (np.arange(nd) + 0.5) * SPACING
    ys = (np.arange(nw) + 0.5) * SPACING
    if grid.min() < 50 < grid.max():
        ax.contour(xs, ys, grid, levels=[50], colors="white", linewidths=1.4,
                   linestyles="-", transform=T, zorder=3)

    # walls, with the window as an opening in the wall at x = 0
    y0, y1 = cy - win_w / 2, cy + win_w / 2
    walls = [
        [(-WALL, width), (depth + WALL, width), (depth + WALL, width + WALL), (-WALL, width + WALL)],
        [(depth, -WALL), (depth + WALL, -WALL), (depth + WALL, width + WALL), (depth, width + WALL)],
        [(-WALL, -WALL), (depth + WALL, -WALL), (depth + WALL, 0), (-WALL, 0)],
        [(-WALL, 0), (0, 0), (0, y0), (-WALL, y0)],
        [(-WALL, y1), (0, y1), (0, width), (-WALL, width)],
    ]
    for w in walls:
        ax.add_patch(Polygon(w, closed=True, fc=INK, ec="none", transform=T, zorder=4))
    ax.add_patch(Polygon([(-WALL, y0), (0, y0), (0, y1), (-WALL, y1)], closed=True,
                         fc="#bcd9ee", ec=INK, lw=0.6, transform=T, zorder=4))

    # opposing building (not to scale), only when obstructed
    if hw > 0:
        ax.add_patch(Polygon([(-1.35, -0.3), (-1.0, -0.3), (-1.0, width + 0.3), (-1.35, width + 0.3)],
                             closed=True, fc="#d9dce1", ec=SOFT, lw=0.6, hatch="////",
                             transform=T, zorder=2))

    # view box: identical for all panels of the same room size
    corners = [(-extent_pad, -extent_pad), (depth + extent_pad, -extent_pad),
               (depth + extent_pad, width + extent_pad), (-extent_pad, width + extent_pad)]
    pts = [rot(x, y, cx, cy, angle) for x, y in corners]
    ax.set_xlim(min(p[0] for p in pts), max(p[0] for p in pts))
    ax.set_ylim(min(p[1] for p in pts), max(p[1] for p in pts))
    ax.set_aspect("equal")
    ax.axis("off")

    # north arrow
    ax.add_patch(FancyArrowPatch((0.93, 0.80), (0.93, 0.95), transform=ax.transAxes,
                                 arrowstyle="-|>", mutation_scale=12, color=INK, lw=1.2))
    ax.text(0.93, 0.74, "N", transform=ax.transAxes, ha="center", va="top", fontsize=9.5, color=INK)

    m = metrics(row)
    street = "unobstructed" if hw == 0 else f"street H/W = {hw:.1f}"
    ax.set_title(f"{ORIENT[r]}-facing · {street}", loc="left", fontsize=11.5,
                 weight="bold", color=INK, pad=4)
    ax.text(0.0, -0.05, f"sDA {m['sda']:.1f}%", transform=ax.transAxes, va="top",
            fontsize=12.5, weight="bold", color=INK)
    ax.text(0.37, -0.058, f"mean DA {m['mean_da']:.1f}%  ·  ASE {m['ase']:.1f}%",
            transform=ax.transAxes, va="top", fontsize=10, color=INK)
    ax.text(0.0, -0.14, f"{width:g} × {depth:g} m room · window {win_w:.2f} × {h_clear:.2f} m · sill {sill:.2f} m",
            transform=ax.transAxes, va="top", fontsize=8.8, color=SOFT)
    ax.text(0.0, -0.205, f"{row['Location']} · case {row['case_id']}",
            transform=ax.transAxes, va="top", fontsize=8.8, color=SOFT)
    return m


def figure(case_ids, out):
    d = pd.read_excel(DATA).set_index("case_id", drop=False)
    rows = [d.loc[c] for c in case_ids]
    n = len(rows)
    nr, nc = (2, 2) if n == 4 else (1, n)
    fig, axes = plt.subplots(nr, nc, figsize=(4.8 * nc, 5.3 * nr))
    axes = np.atleast_1d(axes).ravel()
    for ax, row in zip(axes, rows):
        m = plot_room(ax, row)
        print(f"{row['case_id']}: {ORIENT[int(row['rotation'])]:>5}, H/W {HW_MAP[int(row['urban canyon toggle'])]:.1f}"
              f" | sDA {m['sda']:.2f} (file {row['sDA']:.2f}) | mean DA {m['mean_da']:.2f} | ASE {m['ase']:.2f}")
    fig.subplots_adjust(wspace=0.22, hspace=0.50, right=0.86)
    cax = fig.add_axes([0.90, 0.30, 0.014, 0.45])
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(0, 100), cmap=CMAP), cax=cax)
    cb.set_label("Daylight autonomy DA$_{300}$ (% of occupied hours)")
    cb.outline.set_visible(False)
    cax.text(0.5, -0.09, "white line:\nDA = 50%\n\nhatched bar:\nopposing\nbuilding,\nnot to scale", transform=cax.transAxes, ha="center",
             va="top", fontsize=8.8, color=SOFT, linespacing=1.3)
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}")
    print("written", out)


if __name__ == "__main__":
    cases = sys.argv[1:] or ["A-00076", "A-01156", "A-00346", "A-01426"]
    figure(cases, "/mnt/user-data/outputs/Figure_03")
