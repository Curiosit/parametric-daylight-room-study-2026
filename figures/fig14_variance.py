#!/usr/bin/env python3
# Manuscript Figure 14: Variance decomposition.
# Run from the repository root:  python figures/fig14_variance.py
"""
Figure 14 — share of variance in sDA300/50% and ASE1000,250 explained by each
variable and two-way interaction (Batch A, n = 4,320).

Batch A is a balanced full factorial (one case per combination of six factors),
so the sums of squares for main effects and interactions are orthogonal and add
exactly to the total. Each term's share is its sum of squares divided by the
total sum of squares. Orientation is treated as a categorical factor, which a
rank correlation cannot do.

(a) Individual terms, sDA and ASE side by side.
(b) Terms grouped: context (street aspect ratio, orientation, location and their
    interactions), room geometry (width, depth, clear height and their
    interactions), context-by-geometry interactions, and higher-order residual.

Usage:
    python fig_14_variance.py --baseline study/A-baseline.xlsx
"""

from __future__ import annotations

import argparse
import itertools

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HW_MAP = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}
FACTORS = {"Street aspect ratio": "HW", "Orientation": "orient", "Room width": "width",
           "Room depth": "depth", "Clear height": "win_height", "Location": "Location"}
CONTEXT = {"Street aspect ratio", "Orientation", "Location"}
GEOMETRY = {"Room width", "Room depth", "Clear height"}
C_SDA, C_ASE = "#2171b5", "#b2182b"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 10.5,
    "axes.titlesize": 11,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
})


def decompose(d, y):
    g = d[y].mean()
    total = ((d[y] - g) ** 2).sum()
    main, shares = {}, {}
    for name, col in FACTORS.items():
        m = d.groupby(col)[y].transform("mean")
        main[col] = m
        shares[(name,)] = ((m - g) ** 2).sum() / total * 100
    for (n1, c1), (n2, c2) in itertools.combinations(FACTORS.items(), 2):
        cm = d.groupby([c1, c2])[y].transform("mean")
        shares[(n1, n2)] = ((cm - main[c1] - main[c2] + g) ** 2).sum() / total * 100
    residual = 100 - sum(shares.values())
    return shares, residual


def group(shares, residual):
    out = {"Context": 0.0, "Room geometry": 0.0, "Context × geometry": 0.0,
           "Higher-order": residual}
    for key, v in shares.items():
        s = set(key)
        if s <= CONTEXT:
            out["Context"] += v
        elif s <= GEOMETRY:
            out["Room geometry"] += v
        else:
            out["Context × geometry"] += v
    return out


def label(key):
    return key[0] if len(key) == 1 else f"{key[0]} × {key[1]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="study/A-baseline.xlsx")
    ap.add_argument("--out", default="figures/output/Figure_14")
    args = ap.parse_args()

    d = pd.read_excel(args.baseline)
    d["HW"] = d["urban canyon toggle"].map(HW_MAP)
    d["orient"] = d["rotation"].map({0: "S", 1: "E", 2: "N", 3: "W"})
    d["ase"] = d["ASE_results"] * 100 if d["ASE_results"].max() <= 1.01 else d["ASE_results"]

    s_sda, r_sda = decompose(d, "sDA")
    s_ase, r_ase = decompose(d, "ase")

    terms = [("Street aspect ratio",), ("Orientation",), ("Street aspect ratio", "Orientation"),
             ("Clear height",), ("Room depth",), ("Room width",), ("Location",),
             ("Orientation", "Room depth")]
    fig = plt.figure(figsize=(7.6, 4.1))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.15], wspace=0.5)
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(terms))[::-1]
    h = 0.38
    a = [s_sda[t] for t in terms]
    b = [s_ase[t] for t in terms]
    ax.barh(y + h / 2, a, h, color=C_SDA, label="sDA$_{300/50\\%}$")
    ax.barh(y - h / 2, b, h, color=C_ASE, label="ASE$_{1000,250}$")
    for yy, va, vb in zip(y, a, b):
        ax.text(va + 0.8, yy + h / 2, f"{va:.1f}" if va >= 1 else f"{va:.2f}",
                va="center", fontsize=8, color=C_SDA)
        ax.text(vb + 0.8, yy - h / 2, f"{vb:.1f}" if vb >= 1 else f"{vb:.2f}",
                va="center", fontsize=8, color=C_ASE)
    ax.set_yticks(y)
    ax.set_yticklabels([label(t) for t in terms])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of variance (%)")
    ax.set_title("(a) By variable", loc="left")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", lw=0.4, alpha=0.3)
    ax.set_axisbelow(True)

    ax = fig.add_subplot(gs[0, 1])
    gsda, gase = group(s_sda, r_sda), group(s_ase, r_ase)
    cats = ["Context", "Room geometry", "Context × geometry", "Higher-order"]
    cols = ["#08306b", "#bdbdbd", "#fdae6b", "#f0f0f0"]
    for i, (gv, lab) in enumerate(((gsda, "sDA"), (gase, "ASE"))):
        left = 0
        for cat, col in zip(cats, cols):
            ax.barh(i, gv[cat], left=left, height=0.42, color=col, edgecolor="white", lw=0.6)
            left += gv[cat]
        ax.text(gv["Context"] / 2, i, f"context\n{gv['Context']:.1f}%", ha="center",
                va="center", fontsize=8.5, color="white", linespacing=1.2)
        ax.text(0, i + 0.36,
                f"room geometry {gv['Room geometry']:.2f}  ·  "
                f"context × geometry {gv['Context × geometry']:.2f}  ·  "
                f"higher-order {gv['Higher-order']:.2f}",
                fontsize=7.6, color="#555555", va="center")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["sDA$_{300/50\\%}$", "ASE$_{1000,250}$"])
    ax.set_ylim(1.7, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of variance (%)")
    ax.set_title("(b) Grouped", loc="left")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for ext in ("png", "pdf"):
        fig.savefig(f"{args.out}.{ext}")

    for lab, s, r, gv in (("sDA", s_sda, r_sda, gsda), ("ASE", s_ase, r_ase, gase)):
        print(f"\n{lab}:")
        for k, v in sorted(s.items(), key=lambda kv: -kv[1])[:8]:
            print(f"  {label(k):<40s} {v:6.2f}")
        print("  grouped: " + ", ".join(f"{k} {v:.2f}" for k, v in gv.items()))
    print(f"\nwritten: {args.out}.png, {args.out}.pdf")


if __name__ == "__main__":
    main()
