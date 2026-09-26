#!/usr/bin/env python3
"""Regenerate every manuscript figure into figures/output/ (PNG at 600 dpi and PDF).

Run from the repository root:
    python figures/make_all_figures.py
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = sorted(p for p in (ROOT / "figures").glob("fig*.py")) + [ROOT / "figures" / "graphical_abstract.py"]

(ROOT / "figures" / "output").mkdir(parents=True, exist_ok=True)
failed = []
for s in SCRIPTS:
    t = time.time()
    r = subprocess.run([sys.executable, str(s)], cwd=ROOT, capture_output=True, text=True)
    status = "ok" if r.returncode == 0 else "FAILED"
    print(f"{status:>6}  {s.name:<42} {time.time() - t:5.1f} s")
    if r.returncode:
        failed.append(s.name)
        print(r.stderr[-1500:])
print(f"\n{len(SCRIPTS) - len(failed)}/{len(SCRIPTS)} scripts ok -> figures/output/")
sys.exit(1 if failed else 0)
