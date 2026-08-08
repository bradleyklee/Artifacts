#!/usr/bin/env python3
"""Regenerate the two-panel triangle-rectangle period figure from code.

Left: midpoint action-quantized real contours and Abel-Wick contours at the
same matched energies, tangent at their common turning points, in the same
(q,p) / (q,U) plotting frame.  Right: the two normalized Picard-Fuchs
solutions on 0 < alpha < 1 and the Abel constant sqrt(5)/pi.
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


def f_real(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    return p**2 + q**2 + 0.5*(q**3 - 3*p**2*q) + 0.0625*(q**2 - 3*p**2)**2


def f_wick(U: np.ndarray, q: np.ndarray) -> np.ndarray:
    return -U**2 + q**2 + 0.5*(q**3 + 3*U**2*q) + 0.0625*(q**2 + 3*U**2)**2


def polygon_area(seg: np.ndarray) -> float:
    xx, yy = seg[:, 0], seg[:, 1]
    return 0.5 * abs(np.dot(xx, np.roll(yy, 1)) - np.dot(yy, np.roll(xx, 1)))


def component_containing(
    generator, level: float, point: tuple[float, float], *, prefer_smallest: bool = False
) -> np.ndarray:
    lines = [s for s in generator.lines(float(level)) if len(s) >= 40]
    closed = [s for s in lines if np.linalg.norm(s[0] - s[-1]) < 2e-5]
    candidates = closed or lines
    if not candidates:
        raise RuntimeError(f"no contour component at alpha={level}")
    inside = [s for s in candidates if MplPath(s).contains_point(point)]
    if inside:
        chooser = min if prefer_smallest else max
        return chooser(inside, key=polygon_area)
    target = np.asarray(point)
    return min(candidates, key=lambda s: np.sum((np.mean(s, axis=0) - target)**2))


def read_levels() -> tuple[np.ndarray, np.ndarray]:
    real, wick = [], []
    with LEVELS_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            real.append(float(row["real_alpha"]))
            wick.append(float(row["wick_alpha"]))
    return np.asarray(real), np.asarray(wick)


def plot_all_segments(ax, generator, level: float, **kwargs) -> None:
    for seg in generator.lines(float(level)):
        if len(seg) >= 20:
            ax.plot(seg[:, 0], seg[:, 1], **kwargs)


def make_left(real_levels: np.ndarray, wick_levels: np.ndarray) -> Path:
    # Match the previous certificate: horizontal coordinate q, vertical p or U.
    qgrid = np.linspace(-5.52, 1.52, 1500)
    rgrid = np.linspace(-2.36, 2.36, 1100)
    Q, R = np.meshgrid(qgrid, rgrid)
    cg_real = contourpy.contour_generator(x=qgrid, y=rgrid, z=f_real(R, Q), name="serial")
    cg_wick = contourpy.contour_generator(x=qgrid, y=rgrid, z=f_wick(R, Q), name="serial")

    wells = [(-4.0, 0.0), (0.0, 0.0)]
    center = (-2.0, 0.0)
    blues, greens = plt.get_cmap("Blues"), plt.get_cmap("Greens")
    n = max(1, len(real_levels)-1)

    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    for i, alpha in enumerate(real_levels):
        color = blues(0.32 + 0.58*i/n)
        for target in wells:
            seg = component_containing(cg_real, alpha, target)
            ax.plot(seg[:, 0], seg[:, 1], color=color, lw=1.25)
    for i, alpha in enumerate(wick_levels):
        color = greens(0.28 + 0.62*i/n)
        # Around the Wick saddle there are both an inner oval and a much larger
        # component containing the same point.  Select the inner oval so the
        # green family occupies the interior, matching the geometric cycle.
        seg = component_containing(cg_wick, alpha, center, prefer_smallest=True)
        ax.plot(seg[:, 0], seg[:, 1], color=color, lw=1.25)

    # Exact separatrices: real alpha=1 and Wick alpha=0.
    plot_all_segments(ax, cg_real, 1.0, color="#d00000", lw=1.9)
    # The Wick zero level has more than one component.  Keep only the
    # inner separatrix bounding the selected green oval family.
    wick_sep = component_containing(cg_wick, 0.0, center, prefer_smallest=True)
    ax.plot(wick_sep[:, 0], wick_sep[:, 1], color="#f472b6", lw=1.9)

    ax.scatter([-4.0, 0.0], [0.0, 0.0], s=18, c="#2563a6", edgecolors="white", linewidths=0.5, zorder=6)
    ax.scatter([-2.0], [0.0], s=18, c="#d00000", edgecolors="white", linewidths=0.5, zorder=6)
    ax.scatter([-2.0], [-2*math.sqrt(5)/3], s=0)  # fixes deterministic bounds

    ax.axhline(0, color="#888888", lw=0.45, alpha=0.35)
    ax.axvline(-2, color="#888888", lw=0.45, alpha=0.25)
    ax.set(xlim=(-5.36, 1.36), ylim=(-1.16, 1.16))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=0.1)
    path = ASSETS / "geometry_left.png"
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def t1_initial(alpha: float) -> tuple[float, float]:
    # T1(alpha)=T1_scaled(alpha/16), where T1_scaled(x)=sum A_n x^n.
    A = [1.0, 0.0]
    for n in range(1, 18):
        g = lambda k: A[k] if k >= 0 else 0.0
        num = (n*(13*n+1)*g(n)
               + 6*(17*n*n+14*n-15)*g(n-1)
               - 216*(2*n-3)**2*g(n-2))
        A.append(num/(n+1)**2)
    x = alpha/16.0
    val = sum(A[n]*x**n for n in range(len(A)))
    der = sum(n*A[n]*x**(n-1)/16.0 for n in range(1, len(A)))
    return val, der


def t2_local_coeffs(N: int = 24) -> list[float]:
    # beta=alpha-1.  Polynomial coefficients of P2,P1,P0 in beta.
    p2 = [0.0, -125.0, -95.0, 57.0, 27.0]
    p1 = [-125.0, -340.0, -33.0, 54.0]
    p0 = [-165/4, -69/2, 27/4]
    c = [0.0]*N
    c[0] = 1.0
    for n in range(N-1):
        den = p2[1]*(n+1)*n + p1[0]*(n+1)
        rhs = 0.0
        for j, coef in enumerate(p2):
            k = n-j+2
            if 0 <= k <= n:
                rhs += coef*k*(k-1)*c[k]
        for j, coef in enumerate(p1):
            k = n-j+1
            if 0 <= k <= n:
                rhs += coef*k*c[k]
        for j, coef in enumerate(p0):
            k = n-j
            if 0 <= k <= n:
                rhs += coef*c[k]
        c[n+1] = -rhs/den
    return c


def t2_initial(alpha: float) -> tuple[float, float]:
    c = t2_local_coeffs()
    beta = alpha-1.0
    val = sum(c[n]*beta**n for n in range(len(c)))
    der = sum(n*c[n]*beta**(n-1) for n in range(1, len(c)))
    return val, der


def ode(_alpha: float, yy: np.ndarray) -> tuple[float, float]:
    alpha = _alpha
    P2 = alpha*(alpha-1)*(3*alpha-8)*(9*alpha+16)
    P1 = 54*alpha**3-195*alpha**2-112*alpha+128
    P0 = 0.75*alpha*(9*alpha-64)
    return yy[1], -(P1*yy[1]+P0*yy[0])/P2


def make_right() -> Path:
    eps = 1.0e-4
    xeval = np.linspace(eps, 1.0-eps, 600)
    y10 = t1_initial(eps)
    sol1 = solve_ivp(ode, (eps, 1.0-eps), y10, t_eval=xeval,
                     rtol=2e-10, atol=2e-12, max_step=0.004)
    y20 = t2_initial(1.0-eps)
    sol2 = solve_ivp(ode, (1.0-eps, eps), y20, t_eval=xeval[::-1],
                     rtol=2e-10, atol=2e-12, max_step=0.004)
    x2 = sol2.t[::-1]
    t2 = sol2.y[0][::-1]

    blues, greens = plt.get_cmap("Blues"), plt.get_cmap("Greens")
    const = math.sqrt(5)/math.pi
    fig, ax = plt.subplots(figsize=(6.9, 5.0))
    ax.plot(sol1.t, sol1.y[0], color=blues(0.72), lw=1.95)
    ax.plot(x2, t2, color=greens(0.72), lw=1.95)
    ax.axvline(0, color="#f472b6", lw=1.45)
    ax.axvline(1.0, color="#d00000", lw=1.45)
    ax.plot([0, 1.0], [const, const], color="black", lw=1.35, ls="-.")
    ax.text(0.74, const+0.055, r"$\sqrt{5}/\pi$", fontsize=10.8, ha="center", va="bottom")
    ax.set(xlim=(0, 1.0), ylim=(0.50, 3.0))
    ax.set_xticks([0, 1.0], [r"$0$", r"$1$"], fontsize=8.5)
    ax.set_yticks([0.7, 1, 2, 3])
    ax.tick_params(axis="y", labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout(pad=0.1)
    path = ASSETS / "geometry_right.png"
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def compose(left_path: Path, right_path: Path) -> None:
    left = Image.open(left_path).convert("RGB")
    right = Image.open(right_path).convert("RGB")

    # The contour panel has a deliberately wide coordinate range, so its
    # equal-aspect render is about half as tall as the period panel.  Stretch
    # only the vertical display scale to give both certificate panels the same
    # visible height; this removes the blank lower half without changing the
    # right-hand plot.
    target_w, target_h = right.width, right.height
    left = left.resize((target_w, target_h), Image.Resampling.LANCZOS)
    if right.size != (target_w, target_h):
        right = right.resize((target_w, target_h), Image.Resampling.LANCZOS)

    gap, top, bottom = 26, 8, 6
    canvas = Image.new("RGB", (2*target_w+gap, target_h+top+bottom), "white")
    canvas.paste(left, (0, top))
    canvas.paste(right, (target_w+gap, top))
    canvas.save(ASSETS / "geometry_period.png", quality=95)
    canvas.save(ASSETS / "geometry_period.pdf", "PDF", resolution=240)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    real_levels, wick_levels = read_levels()
    compose(make_left(real_levels, wick_levels), make_right())
    print("wrote assets/geometry_period.png and assets/geometry_period.pdf")


if __name__ == "__main__":
    main()
