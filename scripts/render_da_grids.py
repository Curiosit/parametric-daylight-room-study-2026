#!/usr/bin/env python3
"""Render a daylight autonomy image for every simulated configuration.

    Batch A  4,320 images   plan of DA300 on the work plane
    Batch B    720 images   plan of DA300 on the work plane
    Batch C  2,160 images   plan of DA300 on the work plane, plus sDA of the two
                            vertical planes at eye height (as values)
    --------------------
    total    7,200 images   ->  study/da-grids/<batch>/<case_id>.png

Each image shows the room in plan with north up: walls, the window as an opening,
the opposing building when the street is obstructed, the DA300 = 50% line (the
boundary of the area counted in sDA300/50%), and the case parameters and metrics.
Metrics are recomputed from the per-sensor arrays on the full grid.

The vertical sensor planes of Batch C are reported as plane-level values only.
Their per-sensor order has not been verified against the horizontal grid, so
they are not drawn as maps; the plane-level metrics do not depend on the order.

The run is resumable: images that already exist are skipped unless --overwrite
is given. Work is processed in chunks with several processes.

Examples (run from the repository root)
    python scripts/render_da_grids.py                       # everything
    python scripts/render_da_grids.py --batches A --chunk 500
    python scripts/render_da_grids.py --batches C --start 0 --stop 100
    python scripts/render_da_grids.py --cases A-00076 A-01156
    python scripts/render_da_grids.py --workers 4 --dpi 100
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ASE_COL, DA_COL, ROOT, ase, load, parse, sda  # noqa: E402

OUT = ROOT / "study" / "da-grids"
WALL = 0.20
INK, SOFT = "#1c2230", "#6b7280"
FIELDS = ["case_id", "batch", "city", "orientation", "rotation", "HW", "width", "depth",
          "win_height", "sill_h", "window_area", "VT", "WFR"]


# --------------------------------------------------------------------------- drawing
def _rot(x, y, cx, cy, deg):
    r = math.radians(deg)
    return (cx + (x - cx) * math.cos(r) - (y - cy) * math.sin(r),
            cy + (x - cx) * math.sin(r) + (y - cy) * math.cos(r))


def draw_plan(ax, g, c, cmap, norm, pad=1.5, contour=True):
    """Room plan, north up. Local frame: x = depth (window wall at x = 0), y = width."""
    import numpy as np
    from matplotlib.patches import FancyArrowPatch, Polygon
    from matplotlib.transforms import Affine2D

    width, depth = c["width"], c["depth"]
    win_w = c["window_area"] / c["win_height"]
    angle = 90 + 90 * int(c["rotation"])        # window wall faces S, E, N, W
    cx, cy = depth / 2, width / 2
    T = Affine2D().rotate_deg_around(cx, cy, angle) + ax.transData

    ax.imshow(g, origin="lower", extent=[0, depth, 0, width], cmap=cmap, norm=norm,
              interpolation="nearest", transform=T, zorder=1)
    if contour and g.min() < 50 < g.max():
        nw, nd = g.shape
        ax.contour((np.arange(nd) + 0.5) * 0.25, (np.arange(nw) + 0.5) * 0.25, g,
                   levels=[50], colors="white", linewidths=1.3, transform=T, zorder=3)
    y0, y1 = cy - win_w / 2, cy + win_w / 2
    for w in ([(-WALL, width), (depth + WALL, width), (depth + WALL, width + WALL), (-WALL, width + WALL)],
              [(depth, -WALL), (depth + WALL, -WALL), (depth + WALL, width + WALL), (depth, width + WALL)],
              [(-WALL, -WALL), (depth + WALL, -WALL), (depth + WALL, 0), (-WALL, 0)],
              [(-WALL, 0), (0, 0), (0, y0), (-WALL, y0)],
              [(-WALL, y1), (0, y1), (0, width), (-WALL, width)]):
        ax.add_patch(Polygon(w, closed=True, fc=INK, ec="none", transform=T, zorder=4))
    ax.add_patch(Polygon([(-WALL, y0), (0, y0), (0, y1), (-WALL, y1)], closed=True,
                         fc="#bcd9ee", ec=INK, lw=0.5, transform=T, zorder=4))
    if c["HW"] > 0:                              # opposing building, not to scale
        ax.add_patch(Polygon([(-1.25, -0.3), (-0.95, -0.3), (-0.95, width + 0.3), (-1.25, width + 0.3)],
                             closed=True, fc="#d9dce1", ec=SOFT, lw=0.5, hatch="////",
                             transform=T, zorder=2))
    # fixed view box (7 x 7 m room plus padding), so all images share one scale
    half = 3.5 + pad
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyArrowPatch((0.95, 0.83), (0.95, 0.97), transform=ax.transAxes,
                                 arrowstyle="-|>", mutation_scale=10, color=INK, lw=1.0))
    ax.text(0.95, 0.79, "N", transform=ax.transAxes, ha="center", va="top", fontsize=8, color=INK)


def render(task):
    """Render one case. task = (fields, da, ase_hours, vert_s, vert_n, out_path, dpi)."""
    c, da, hours, vs, vn, out, dpi = task
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    cmap = matplotlib.colormaps["viridis"]
    norm = matplotlib.colors.Normalize(0, 100)
    shape = (round(c["width"] / 0.25), round(c["depth"] / 0.25))
    g = np.asarray(da).reshape(shape)

    fig, ax = plt.subplots(figsize=(5.6, 6.2))
    draw_plan(ax, g, c, cmap, norm, pad=0.9)

    street = "unobstructed" if c["HW"] == 0 else f"street H/W = {c['HW']:.1f}"
    win_w = c["window_area"] / c["win_height"]
    fig.text(0.04, 0.975, f"{c['case_id']}  ·  {c['city']}", fontsize=12, weight="bold", color=INK, va="top")
    fig.text(0.04, 0.935, f"{c['orientation']}-facing  ·  {street}", fontsize=10.5, color=INK, va="top")
    fig.text(0.04, 0.9, f"Room {c['width']:g} × {c['depth']:g} m  ·  window {win_w:.2f} × {c['win_height']:.2f} m, "
             f"sill {c['sill_h']:.2f} m", fontsize=9, color=SOFT, va="top")
    fig.text(0.04, 0.87, f"WFR 1/{round(1 / c['WFR'])}  ·  VT {c['VT']:.2f}", fontsize=9, color=SOFT, va="top")

    fig.text(0.04, 0.115, f"sDA {sda(g):.1f}%", fontsize=13, weight="bold", color=INK)
    fig.text(0.30, 0.117, f"mean DA {g.mean():.1f}%  ·  ASE {ase(np.asarray(hours)):.1f}%",
             fontsize=10, color=INK)
    if vs is not None:
        fig.text(0.04, 0.075, f"Eye height 1.2 m:  sDA facing south {sda(np.asarray(vs)):.1f}%  ·  "
                 f"facing north {sda(np.asarray(vn)):.1f}%", fontsize=9, color=INK)
    fig.text(0.04, 0.03, "Work plane 0.8 m.  White line: DA300 = 50%.  Hatched: opposing building, not to scale.",
             fontsize=7.3, color=SOFT)

    fig.subplots_adjust(left=0.0, right=0.84, top=0.85, bottom=0.14)
    cax = fig.add_axes([0.87, 0.28, 0.025, 0.42])
    cb = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
    cb.set_label("DA$_{300}$ (%)", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    cb.outline.set_visible(False)

    tmp = Path(str(out) + ".tmp.png")
    fig.savefig(tmp, dpi=dpi)
    plt.close(fig)
    os.replace(tmp, out)                         # atomic: no half-written files on interrupt
    return c["case_id"]


# --------------------------------------------------------------------------- driver
def tasks_for(batch, frame, out_dir, dpi, overwrite):
    vertical = batch == "C"
    for _, r in frame.iterrows():
        out = out_dir / f"{r['case_id']}.png"
        if out.exists() and not overwrite:
            continue
        c = {k: (r[k] if k in r else None) for k in FIELDS}
        c["sill_h"] = float(c["sill_h"])
        c["VT"] = float(c["VT"]) if c["VT"] is not None else 0.64
        c["WFR"] = float(c["WFR"]) if c["WFR"] is not None else 0.125
        yield (c, parse(r[DA_COL[batch]]), parse(r[ASE_COL[batch]]),
               parse(r["raw_DA_vert_south_facing"]) if vertical else None,
               parse(r["raw_DA_vert_north_facing"]) if vertical else None,
               out, dpi)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batches", nargs="+", default=["A", "B", "C"], choices=["A", "B", "C"])
    ap.add_argument("--cases", nargs="+", help="render only these case IDs, e.g. A-00076")
    ap.add_argument("--start", type=int, default=0, help="first row within each batch")
    ap.add_argument("--stop", type=int, default=None, help="row after the last one within each batch")
    ap.add_argument("--chunk", type=int, default=250, help="images per chunk (progress is reported per chunk)")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    ctx = get_context("spawn")
    grand = 0
    t_all = time.time()
    for batch in a.batches:
        d = load(batch)
        if a.cases:
            d = d[d["case_id"].isin(a.cases)]
        d = d.iloc[a.start:a.stop]
        if d.empty:
            continue
        out_dir = OUT / batch
        out_dir.mkdir(parents=True, exist_ok=True)
        todo = list(tasks_for(batch, d, out_dir, a.dpi, a.overwrite))
        print(f"Batch {batch}: {len(d)} cases in range, {len(todo)} to render, "
              f"{len(d) - len(todo)} already present")
        done = 0
        with ctx.Pool(a.workers) as pool:
            for i in range(0, len(todo), a.chunk):
                t = time.time()
                chunk = todo[i:i + a.chunk]
                for _ in pool.imap_unordered(render, chunk, chunksize=4):
                    done += 1
                rate = len(chunk) / max(time.time() - t, 1e-6)
                left = (len(todo) - done) / rate if rate else 0
                print(f"  {batch}: {done}/{len(todo)}  ({rate:.1f} img/s, ~{left / 60:.1f} min left)",
                      flush=True)
        grand += done
    print(f"Done: {grand} images in {(time.time() - t_all) / 60:.1f} min -> {OUT}")


if __name__ == "__main__":
    main()
