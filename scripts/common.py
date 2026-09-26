"""Shared constants, loaders and metric functions.

All scripts in this repository are run from the repository root, for example
    python scripts/render_da_grids.py
    python figures/make_all_figures.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "study"

FILES = {
    "A": STUDY / "A-baseline.xlsx",
    "B": STUDY / "B-sill-control.xlsx",
    "C": STUDY / "C-wfr-x-vt.xlsx",
    "D": STUDY / "D-ab-sweep.xlsx",
}

SPACING = 0.25                         # sensor spacing (m)
HW = {0: 0.0, 1: 0.5, 2: 1.0, 3: 1.5}  # 'urban canyon toggle' -> street aspect ratio H/W
# The model rotates counter-clockwise: 0 = South, 1 = East, 2 = North, 3 = West.
ORIENTATION = {0: "South", 1: "East", 2: "North", 3: "West"}
CITY_FROM_EPW = {"Berlin": "Berlin", "Warsz": "Warsaw"}

# Horizontal per-sensor columns differ between batches; everything else is shared.
DA_COL = {"A": "raw_DA", "B": "raw_DA", "C": "raw_DA-horizontal", "D": "raw_DA"}
ASE_COL = {"A": "raw_ASE_hours", "B": "raw_ASE_hours", "C": "raw_ASE_hours-horizontal", "D": "raw_ASE_hours"}


def parse(cell) -> np.ndarray:
    """Per-sensor values stored as a ';'-delimited string."""
    return np.fromstring(str(cell).replace(",", "."), sep=";")


def grid(cell, width: float, depth: float) -> np.ndarray:
    """Reshape a per-sensor array to (n_width, n_depth).

    Ordering is width-major: index k = i * n_depth + j, with i along the window
    wall and j from the window wall (j = 0) to the back wall.
    """
    return parse(cell).reshape(round(width / SPACING), round(depth / SPACING))


def sda(da: np.ndarray) -> float:
    """sDA300/50%: share of sensors with DA300 >= 50%, in percent."""
    return 100.0 * float(np.mean(da >= 50))


def ase(hours: np.ndarray) -> float:
    """ASE1000,250: share of sensors above 1000 lux direct sun for > 250 h, in percent."""
    return 100.0 * float(np.mean(hours > 250))


def city(row) -> str:
    if "Location" in row and isinstance(row["Location"], str):
        return row["Location"]
    epw = str(row.get("epw_file", ""))
    return next((v for k, v in CITY_FROM_EPW.items() if k in epw), "")


def load(batch: str) -> pd.DataFrame:
    """Load one batch with a few convenience columns added."""
    d = pd.read_excel(FILES[batch])
    d["batch"] = batch
    d["HW"] = d["urban canyon toggle"].map(HW)
    d["orientation"] = d["rotation"].map(ORIENTATION)
    d["city"] = [city(r) for _, r in d.iterrows()]
    return d
