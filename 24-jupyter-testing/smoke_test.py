from pathlib import Path
import sys

import numpy as np
import pandas as pd
import sympy as sp

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "original_scripts"))

from artifact24.geometry import VERTICES, COMMON_IMAGE, polynomial_map
from artifact24.plots import build_interactive_figure
from compute_mesh_area_series import compute as compute_red_area
from abel_wick_period_series import SCALES, period_coefficients
from validate_mapped_area_periods import (
    red_direct_quadrature,
    aw_direct_quadrature,
)

# Original Artifact 24 geometry.
mapped = polynomial_map(VERTICES)
assert np.max(np.linalg.norm(mapped - COMMON_IMAGE, axis=1)) < 1e-10
fig = build_interactive_figure(
    red_count=8,
    auxiliary_count=4,
    samples=240,
    show_background=False,
)
assert len(fig.data) > 0


# Binder rational-backend guard.
from sympy.polys.domains import QQ
from abel_wick_period_series import rationalized_gram_parts
for family_index in range(3):
    parts, _ = rationalized_gram_parts(family_index)
    assert all(type(c) is type(QQ.one) for row in parts.values() for c in row)

# Live exact prefixes for the new notebook.
red_area = compute_red_area(4)["coeffs"]
red_period = [sp.factor((k + 1) * red_area[k + 1]) for k in range(4)]
red_scale = sp.Integer(235_651_734)
assert all(sp.denom(c * red_scale**k) == 1 for k, c in enumerate(red_period))

for family in ("green", "yellow", "blue"):
    coefficients, _ = period_coefficients(family, 4)
    assert all(
        sp.denom(coefficient * SCALES[family]**k) == 1
        for k, coefficient in enumerate(coefficients)
    )

# Long cache is external, transparent data rather than notebook state.
cache = pd.read_csv(DATA := ROOT / "data" / "mapped_area_period_scaled_integers.csv")
assert cache.groupby("family").size().to_dict() == {
    "blue": 100,
    "green": 100,
    "red": 90,
    "yellow": 100,
}
assert cache["is_integer"].all()

# Warning-free direct integrations at small resolution.
old = np.seterr(divide="raise", invalid="raise", over="raise", under="ignore")
try:
    assert red_direct_quadrature(0.1, 48, 18) > 0
    assert aw_direct_quadrature(0, 0.02, 48, 18) > 0
    assert aw_direct_quadrature(1, 0.002, 48, 18) > 0
    assert aw_direct_quadrature(2, 0.002, 48, 18) > 0
finally:
    np.seterr(**old)

print("PASS")
