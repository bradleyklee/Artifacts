#!/usr/bin/env python3
"""Regenerate the two-panel showcase figure from code.

The quantized energy levels are read from the checked CSV in payload/.  The
left panel extracts only the selected connected closed components.  The right
panel computes the two period curves by Hamiltonian return times and draws the
page-normalized Abel level sqrt(5)/pi.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import contourpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
import numpy as np
from PIL import Image
from scipy.integrate import solve_ivp

SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == "scripts":
    ROOT = SCRIPT_DIR.parent
    ASSETS = ROOT / "assets"
    LEVELS_CSV = ROOT / "payload" / "quantized_levels_for_figure.csv"
else:
    ROOT = SCRIPT_DIR
    ASSETS = ROOT / "assets"
    LEVELS_CSV = ROOT / "quantized_levels_for_figure.csv"


def h_real(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    return p**2 - q**2 + p**4 / 25 - (6 / 5) * p**2 * q**2 + q**4


def h_ip(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    return -p**2 - q**2 + p**4 / 25 + (6 / 5) * p**2 * q**2 + q**4


def polygon_area(seg: np.ndarray) -> float:
    xx, yy = seg[:, 0], seg[:, 1]
    return 0.5 * abs(np.dot(xx, np.roll(yy, 1)) - np.dot(yy, np.roll(xx, 1)))


def component_containing(generator, level: float, point: tuple[float, float]) -> np.ndarray:
    lines = [s for s in generator.lines(float(level)) if len(s) >= 40]
    closed = [s for s in lines if np.linalg.norm(s[0] - s[-1]) < 1e-6]
    candidates = closed or lines
    if not candidates:
        raise RuntimeError(f"no contour component at E={level}")
    inside = [s for s in candidates if MplPath(s).contains_point(point)]
    if inside:
        return max(inside, key=polygon_area)
    target = np.asarray(point)
    return min(candidates, key=lambda s: np.sum((np.mean(s, axis=0) - target) ** 2))


def read_levels() -> tuple[np.ndarray, np.ndarray]:
    real, comp = [], []
    with LEVELS_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            real.append(float(row["real_E"]))
            comp.append(float(row["ip_E"]))
    return np.asarray(real), np.asarray(comp)


def flow_real(_t: float, state: np.ndarray) -> tuple[float, float]:
    p, q = state
    hp = 2 * p + 4 * p**3 / 25 - 12 * p * q * q / 5
    hq = -2 * q - 12 * p * p * q / 5 + 4 * q**3
    return -hq, hp


def flow_ip(_t: float, state: np.ndarray) -> tuple[float, float]:
    p, q = state
    hp = -2 * p + 4 * p**3 / 25 + 12 * p * q * q / 5
    hq = -2 * q + 12 * p * p * q / 5 + 4 * q**3
    return -hq, hp


def period_from_turning_point(flow, energy: float) -> float:
    q0 = math.sqrt((1 - math.sqrt(1 + 4 * energy)) / 2)
    warm = solve_ivp(
        flow, (0.0, 1e-5), (0.0, q0),
        rtol=2e-10, atol=2e-12, max_step=1e-6,
    )
    state = warm.y[:, -1]

    def event_p_up(_t: float, yy: np.ndarray) -> float:
        return float(yy[0])

    event_p_up.direction = 1
    event_p_up.terminal = True
    sol = solve_ivp(
        flow, (1e-5, 120.0), state, events=event_p_up,
        rtol=2e-9, atol=2e-11, max_step=0.015,
    )
    if not len(sol.t_events[0]):
        raise RuntimeError(f"no return event for E={energy}")
    return float(sol.t_events[0][0])


def make_left(real_levels: np.ndarray, ip_levels: np.ndarray) -> Path:
    x = np.linspace(-1.12, 1.12, 1200)  # horizontal q
    y = np.linspace(-0.96, 0.96, 1050)  # vertical p
    X, Y = np.meshgrid(x, y)
    cg_real = contourpy.contour_generator(x=x, y=y, z=h_real(Y, X), name="serial")
    cg_ip = contourpy.contour_generator(x=x, y=y, z=h_ip(Y, X), name="serial")

    left_well = (-1 / math.sqrt(2), 0.0)
    right_well = (1 / math.sqrt(2), 0.0)
    origin = (0.0, 0.0)
    blues, greens = plt.get_cmap("Blues"), plt.get_cmap("Greens")
    n = len(real_levels) - 1

    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    for i, energy in enumerate(real_levels):
        color = blues(0.34 + 0.56 * i / max(1, n))
        ax.plot(*component_containing(cg_real, energy, left_well).T, color=color, lw=1.35)
        ax.plot(*component_containing(cg_real, energy, right_well).T, color=color, lw=1.35)
    for i, energy in enumerate(ip_levels):
        color = greens(0.30 + 0.60 * i / max(1, n))
        ax.plot(*component_containing(cg_ip, energy, origin).T, color=color, lw=1.35)

    for target in (left_well, right_well):
        ax.plot(*component_containing(cg_real, -1 / 8, target).T, color="#d00000", lw=2.0)
    ax.plot(*component_containing(cg_ip, -1 / 4 + 1e-5, origin).T, color="#f472b6", lw=2.1)

    real_critical = [
        (-math.sqrt(14) / 4, -math.sqrt(10) / 4),
        (-math.sqrt(14) / 4, math.sqrt(10) / 4),
        (math.sqrt(14) / 4, -math.sqrt(10) / 4),
        (math.sqrt(14) / 4, math.sqrt(10) / 4),
    ]
    ax.scatter(*zip(*real_critical), s=20, c="#d00000", edgecolors="white", linewidths=0.5, zorder=6)
    ip_critical = [(-1 / math.sqrt(2), 0.0), (1 / math.sqrt(2), 0.0)]
    ax.scatter(*zip(*ip_critical), s=20, c="#f472b6", edgecolors="white", linewidths=0.5, zorder=6)
    ax.axhline(0, color="#888888", lw=0.45, alpha=0.35)
    ax.axvline(0, color="#888888", lw=0.45, alpha=0.35)
    ax.set(xlim=(-1.04, 1.04), ylim=(-0.88, 0.88))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=0.1)
    path = ASSETS / "geometry_left.png"
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_right() -> Path:
    # T1 is normalized at z=0.  T2 is the full p-Wick oval normalized at z=1/4.
    d1 = np.geomspace(1e-7, 0.1245, 58)
    e1 = np.sort(-1 / 8 - d1)
    z1 = e1 + 1 / 4
    t1 = np.array([period_from_turning_point(flow_real, float(e)) for e in e1])
    t1 /= math.pi * math.sqrt(5) / 2

    d2 = np.geomspace(1e-6, 0.1240, 58)
    e2 = np.sort(-1 / 4 + d2)
    e2 = e2[e2 <= -1 / 8 + 1e-9]
    z2 = e2 + 1 / 4
    raw2 = np.array([period_from_turning_point(flow_ip, float(e)) for e in e2])
    # Earlier saddle-normalized numerical curve had endpoint one at z=1/8.
    # The page's center normalization multiplies that curve by sqrt(10/7).
    t2 = math.sqrt(10 / 7) * raw2 / raw2[-1]

    blues, greens = plt.get_cmap("Blues"), plt.get_cmap("Greens")
    const = math.sqrt(5) / math.pi
    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    ax.plot(z1, t1, color=blues(0.72), lw=1.95)
    ax.plot(z2, t2, color=greens(0.72), lw=1.95)
    ax.axvline(0, color="#f472b6", lw=1.45)
    ax.axvline(1 / 8, color="#d00000", lw=1.45)
    ax.plot([0, 1 / 8], [const, const], color="black", lw=1.45, ls="-.")
    ax.text(0.094, const + 0.055, r"$\sqrt{5}/\pi$", fontsize=10.8, ha="center", va="bottom")
    ax.set(xlim=(0, 1 / 8), ylim=(0.50, 3.0))
    ax.set_xticks([0, 1 / 8], [r"$0$", r"$1/8$"], fontsize=8.5)
    ax.set_yticks([0.7, 1, 2, 3])
    ax.tick_params(axis="y", labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout(pad=0.1)
    path = ASSETS / "geometry_right.png"
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def compose(left_path: Path, right_path: Path) -> None:
    left, right = Image.open(left_path).convert("RGB"), Image.open(right_path).convert("RGB")
    cell_w, cell_h = max(left.width, right.width), max(left.height, right.height)
    gap, top, bottom = 26, 8, 6
    canvas = Image.new("RGB", (2 * cell_w + gap, cell_h + top + bottom), "white")
    canvas.paste(left, (0, top))
    canvas.paste(right, (cell_w + gap, top))
    canvas.save(ASSETS / "geometry_period.png", quality=95)
    canvas.save(ASSETS / "geometry_period.pdf", "PDF", resolution=220)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    real_levels, ip_levels = read_levels()
    compose(make_left(real_levels, ip_levels), make_right())
    print("wrote assets/geometry_period.png and assets/geometry_period.pdf")


if __name__ == "__main__":
    main()
