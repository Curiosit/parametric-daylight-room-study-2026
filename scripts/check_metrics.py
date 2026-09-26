#!/usr/bin/env python3
"""Recompute every stored metric from the per-sensor arrays and compare.

For each batch, sDA300/50% (share of sensors with DA300 >= 50%) and ASE1000,250
(share of sensors above 250 h of direct sun > 1000 lux) are recomputed from the
';'-delimited per-sensor columns and compared with the stored values. The script
also prints the headline values reported in the manuscript.

Run from the repository root:
    python scripts/check_metrics.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load, parse, sda, ase  # noqa: E402

CHECKS = {
    "A": [("sDA", "raw_DA", sda), ("culled_sDA", "culled_raw_DA", sda),
          ("ASE_results", "raw_ASE_hours", ase), ("ASE_culled_results", "raw_culled_ASE_hours", ase)],
    "B": [("sDA", "raw_DA", sda), ("culled_sDA", "culled_raw_DA", sda),
          ("ASE_results", "raw_ASE_hours", ase), ("ASE_culled_results", "raw_culled_ASE_hours", ase)],
    "C": [("sDA-horizontal", "raw_DA-horizontal", sda),
          ("sDA_vert_south_facing", "raw_DA_vert_south_facing", sda),
          ("sDA_vert_north_facing", "raw_DA_vert_north_facing", sda),
          ("ASE_results-horizontal", "raw_ASE_hours-horizontal", ase)],
    "D": [("sDA", "raw_DA", sda), ("culled_sDA", "culled_raw_DA", sda),
          ("ASE_results", "raw_ASE_hours", ase), ("ASE_culled_results", "raw_culled_ASE_hours", ase)],
}

ok = True
for batch, checks in CHECKS.items():
    d = load(batch)
    print(f"Batch {batch}: {len(d)} configurations")
    for stored, raw, fn in checks:
        if stored not in d or raw not in d:
            continue
        diff = np.abs(np.array([fn(parse(x)) for x in d[raw]]) - d[stored].to_numpy())
        flag = "ok" if diff.max() < 1e-6 else "MISMATCH"
        ok &= flag == "ok"
        print(f"   {stored:<24} max |stored - recomputed| = {diff.max():.2e}  {flag}")

A = load("A")
print("\nManuscript values (Batch A, full grid)")
print(f"   mean sDA300/50%            {A.sDA.mean():6.2f}%   (22.44)")
for hw, ref in [(0.0, 42.58), (0.5, 26.07), (1.0, 13.47), (1.5, 7.65)]:
    print(f"   mean at H/W = {hw:.1f}          {A[A.HW == hw].sDA.mean():6.2f}%   ({ref})")
print(f"   configurations >= 40%      {100 * (A.sDA >= 40).mean():6.2f}%   (12.43)")
print(f"   obstructed reaching 40%    {int((A[A.HW > 0].sDA >= 40).sum()):6d}    (0 of 3,240)")
sys.exit(0 if ok else 1)
