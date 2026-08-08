#!/usr/bin/env python3
"""Quantize the real action, then Abel-Wick match the same energies.

For L displayed real ovals, use midpoint action fractions

    f_n = (n + 1/2) / L,   n = 0, ..., L-1.

Only the real branch is quantized.  Abel-Wick continuation p -> iU preserves
the energy parameter, so the complex contour paired with a real level alpha_n
is drawn at the same alpha_n.  The paired curves share turning points at
p=U=0 and are tangent there.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import contourpy
import numpy as np
from matplotlib.path import Path as MplPath
from scipy.optimize import brentq

SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == "scripts":
    ROOT = SCRIPT_DIR.parent
    PAYLOAD_DIR = ROOT / "payload"
else:
    ROOT = SCRIPT_DIR
    PAYLOAD_DIR = SCRIPT_DIR
OUTPUT = PAYLOAD_DIR / "quantized_levels_for_figure.csv"
LEVEL_COUNT = 11
SEPARATRIX_EPS = 1.0e-6
REAL_LOWER = 4.0e-4
WICK_UPPER = 1.0 - 4.0e-4


def f_real(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    return p**2 + q**2 + 0.5*(q**3 - 3*p**2*q) + 0.0625*(q**2 - 3*p**2)**2


def f_wick(U: np.ndarray, q: np.ndarray) -> np.ndarray:
    return -U**2 + q**2 + 0.5*(q**3 + 3*U**2*q) + 0.0625*(q**2 + 3*U**2)**2


def polygon_area(segment: np.ndarray) -> float:
    x, y = segment[:, 0], segment[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def component_containing(generator, level: float, point: tuple[float, float], *, smallest: bool = False) -> np.ndarray:
    lines = [seg for seg in generator.lines(float(level)) if len(seg) >= 40]
    closed = [seg for seg in lines if np.linalg.norm(seg[0] - seg[-1]) < 2e-5]
    candidates = closed or lines
    if not candidates:
        raise RuntimeError(f"no contour component at level {level}")
    inside = [seg for seg in candidates if MplPath(seg).contains_point(point)]
    if inside:
        return (min if smallest else max)(inside, key=polygon_area)
    target = np.asarray(point)
    return min(candidates, key=lambda seg: np.sum((np.mean(seg, axis=0) - target)**2))


def build_generators():
    qgrid = np.linspace(-5.52, 1.52, 1800)
    rgrid = np.linspace(-2.36, 2.36, 1500)
    Q, R = np.meshgrid(qgrid, rgrid)
    real = contourpy.contour_generator(x=qgrid, y=rgrid, z=f_real(R, Q), name="serial")
    wick = contourpy.contour_generator(x=qgrid, y=rgrid, z=f_wick(R, Q), name="serial")
    return real, wick


def generate_rows(level_count: int = LEVEL_COUNT) -> list[dict[str, float | int]]:
    real_gen, wick_gen = build_generators()
    real_total = polygon_area(component_containing(real_gen, 1.0 - 4*SEPARATRIX_EPS, (-4.0, 0.0)))

    def real_fraction(alpha: float) -> float:
        return polygon_area(component_containing(real_gen, alpha, (-4.0, 0.0))) / real_total


    rows: list[dict[str, float | int]] = []
    for n in range(level_count):
        fraction = (n + 0.5) / level_count
        real_alpha = brentq(lambda value: real_fraction(value) - fraction, REAL_LOWER, 1.0 - 4*SEPARATRIX_EPS, xtol=2e-13, rtol=2e-13)
        wick_alpha = real_alpha
        rows.append({
            "n": n,
            "action_fraction_(n+1/2)/L": fraction,
            "real_alpha": real_alpha,
            "wick_alpha": wick_alpha,
        })
    return rows


def write_rows(rows: list[dict[str, float | int]], output: Path = OUTPUT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "action_fraction_(n+1/2)/L", "real_alpha", "wick_alpha"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "n": row["n"],
                "action_fraction_(n+1/2)/L": f"{float(row['action_fraction_(n+1/2)/L']):.16g}",
                "real_alpha": f"{float(row['real_alpha']):.16g}",
                "wick_alpha": f"{float(row['wick_alpha']):.16g}",
            })


def read_rows(path: Path = OUTPUT) -> list[dict[str, float | int]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "n": int(row["n"]),
                "action_fraction_(n+1/2)/L": float(row["action_fraction_(n+1/2)/L"]),
                "real_alpha": float(row["real_alpha"]),
                "wick_alpha": float(row["wick_alpha"]),
            })
    return rows


def check_rows(saved: list[dict[str, float | int]], regenerated: list[dict[str, float | int]], tolerance: float = 3e-8) -> None:
    if len(saved) != len(regenerated):
        raise SystemExit(f"row-count mismatch: saved={len(saved)} regenerated={len(regenerated)}")
    for left, right in zip(saved, regenerated):
        if int(left["n"]) != int(right["n"]):
            raise SystemExit(f"index mismatch: {left['n']} != {right['n']}")
        for key in ("action_fraction_(n+1/2)/L", "real_alpha", "wick_alpha"):
            error = abs(float(left[key]) - float(right[key]))
            if error > tolerance:
                raise SystemExit(f"{key} mismatch at n={left['n']}: error={error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="regenerate in memory and compare with the checked CSV")
    parser.add_argument("--levels", type=int, default=LEVEL_COUNT)
    args = parser.parse_args()
    regenerated = generate_rows(args.levels)
    if args.check:
        check_rows(read_rows(), regenerated)
        print(f"QUANTIZED LEVELS PASS ({args.levels} real-action levels; Wick energies tangent-matched)")
    else:
        write_rows(regenerated)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
