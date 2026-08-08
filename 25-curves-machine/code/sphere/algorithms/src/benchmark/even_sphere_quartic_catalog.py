#!/usr/bin/env python3
"""Deterministic support-stratified even sphere quartic catalog."""
from __future__ import annotations

import json
from pathlib import Path

MODELS = [
    {"name":"linear_asymmetric","coefficients":[0,1,2,5,0,0,0,0,0,0],"stratum":"linear"},
    {"name":"octahedral","coefficients":[0,0,0,0,2,2,2,0,0,0],"stratum":"polyhedral"},
    {"name":"diagonal_quadratic_01","coefficients":[0,1,-1,2,1,2,3,0,0,0],"stratum":"diagonal"},
    {"name":"reflection_xy","coefficients":[1,2,2,-1,3,3,5,7,-2,-2],"stratum":"reflection"},
    {"name":"factored_xy","coefficients":[0,0,0,0,0,0,0,1,0,0],"stratum":"degenerate"},
    {"name":"dense_01","coefficients":[1,2,-3,5,7,-11,13,17,-19,23],"stratum":"dense"},
    {"name":"dense_02","coefficients":[-2,3,5,-7,11,13,-17,19,23,-29],"stratum":"dense"}
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parents[3]/"data/examples/sphere_curves/even_quartic_catalog.json"
    out.write_text(json.dumps({"energy_convention":"alpha=H","models":MODELS},indent=2)+"\n")
    print(out)
