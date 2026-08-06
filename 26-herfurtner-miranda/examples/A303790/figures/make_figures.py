"""Generate the exact figures for the A303790 cubic note.

All critical points, levels, and factorizations are exact. Floating point is
used only to sample the exact algebraic level curves for raster/vector output.
No numerical critical-point solver and no image-generation tool is used.
"""
from pathlib import Path

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

OUT = Path(__file__).parent

u, v, y = sp.symbols("u v y", real=True)
sqrt2 = sp.sqrt(2)

K = u**2 + v**2 + u*(u**2 + 3*v**2)/sqrt2
K_wick = u**2 - y**2 + u*(u**2 - 3*y**2)/sqrt2

E_sep = sp.Rational(4, 27)
u_divider = -sqrt2/3
v_saddle = sqrt2/3
u_max = -2*sqrt2/3

right_levels = [sp.Rational(1,27), sp.Rational(2,27), sp.Rational(3,27)]
left_levels = [sp.Rational(5,27), sp.Rational(6,27), sp.Rational(7,27)]

f_real = sp.lambdify((u, v), K, "numpy")
f_wick = sp.lambdify((u, y), K_wick, "numpy")

def save_all(fig, stem):
    fig.savefig(OUT / f"{stem}.png", dpi=240, bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")

# Main real picture: closed curves from both disks.
ugrid = np.linspace(-1.48, 0.55, 1250)
vgrid = np.linspace(-0.74, 0.74, 900)
U, V = np.meshgrid(ugrid, vgrid)
Z = np.asarray(f_real(U, V), dtype=float)

u0 = float(u_divider)
vs = float(v_saddle)
um = float(u_max)

inside_ellipse = (U-u0)**2 + 3*V**2 <= 2/3 + 1e-10
right_disk = inside_ellipse & (U >= u0 - 1e-10)
left_disk = inside_ellipse & (U <= u0 + 1e-10)

Z_right = np.ma.masked_where(~right_disk, Z)
Z_left = np.ma.masked_where(~left_disk, Z)

fig = plt.figure(figsize=(9.4, 7.3))
ax = fig.add_subplot(111)

right = ax.contour(
    U, V, Z_right,
    levels=[float(level) for level in right_levels],
    linewidths=1.5,
)
left = ax.contour(
    U, V, Z_left,
    levels=[float(level) for level in left_levels],
    linewidths=1.5,
)

right_fmt = {float(level): f"E={level}" for level in right_levels}
left_fmt = {float(level): f"E={level}" for level in left_levels}
ax.clabel(
    right, inline=True, fontsize=9,
    fmt=lambda value: right_fmt[min(
        right_fmt, key=lambda candidate: abs(candidate-value)
    )],
)
ax.clabel(
    left, inline=True, fontsize=9,
    fmt=lambda value: left_fmt[min(
        left_fmt, key=lambda candidate: abs(candidate-value)
    )],
)

theta = np.linspace(0, 2*np.pi, 1600)
ellipse_u = u0 + np.sqrt(2/3)*np.cos(theta)
ellipse_v = np.sqrt(2/9)*np.sin(theta)
ax.plot(ellipse_u, ellipse_v, linewidth=3.0)
ax.plot([u0, u0], [-vs, vs], linewidth=3.0)

ax.scatter([0], [0], marker="o", s=62)
ax.scatter([um], [0], marker="s", s=62)
ax.scatter([u0, u0], [-vs, vs], marker="x", s=82)

ax.annotate("minimum  E=0", (0,0), xytext=(8,8),
            textcoords="offset points", fontsize=10)
ax.annotate("maximum  E=8/27", (um,0), xytext=(-112,8),
            textcoords="offset points", fontsize=10)
ax.annotate("saddles  E=4/27", (u0,vs), xytext=(8,8),
            textcoords="offset points", fontsize=10)

ax.axhline(0, linewidth=0.55)
ax.axvline(0, linewidth=0.55)
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(ugrid.min(), ugrid.max())
ax.set_ylim(vgrid.min(), vgrid.max())
ax.set_xlabel("u")
ax.set_ylabel("v")
ax.set_title(
    "Two period disks for E = u^2+v^2+u(u^2+3v^2)/sqrt(2)\n"
    "right disk: 0<E<4/27; left disk: 4/27<E<8/27"
)
fig.tight_layout()
save_all(fig, "figure_real_two_disks")
plt.close(fig)

def wick_figure(levels, stem, title):
    ugrid = np.linspace(-1.75, 0.95, 1500)
    ygrid = np.linspace(-2.1, 2.1, 1500)
    U, Y = np.meshgrid(ugrid, ygrid)
    Z = np.asarray(f_wick(U, Y), dtype=float)

    fig = plt.figure(figsize=(8.6, 8.0))
    ax = fig.add_subplot(111)

    contours = ax.contour(
        U, Y, Z,
        levels=[float(level) for level in levels],
        linewidths=1.5,
    )
    labels = {float(level): f"E={level}" for level in levels}
    ax.clabel(
        contours, inline=True, fontsize=9,
        fmt=lambda value: labels[min(
            labels, key=lambda candidate: abs(candidate-value)
        )],
    )

    yp = np.linspace(ygrid.min(), ygrid.max(), 2200)
    root = np.sqrt(2/3 + 3*yp**2)
    ax.plot(u0+root, yp, linewidth=3.0)
    ax.plot(u0-root, yp, linewidth=3.0)
    ax.plot([u0,u0], [ygrid.min(),ygrid.max()], linewidth=1.2)

    ax.scatter([0], [0], marker="o", s=62)
    ax.axhline(0, linewidth=0.55)
    ax.axvline(0, linewidth=0.55)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(ugrid.min(), ugrid.max())
    ax.set_ylim(ygrid.min(), ygrid.max())
    ax.set_xlabel("u")
    ax.set_ylabel("y")
    ax.set_title(title)
    fig.tight_layout()
    save_all(fig, stem)
    plt.close(fig)

wick_figure(
    right_levels,
    "figure_wick_from_minimum_disk",
    "Abel-Wick traces v -> i y from the E=0 disk",
)
wick_figure(
    left_levels,
    "figure_wick_from_maximum_disk",
    "Abel-Wick traces v -> i y from the E=8/27 disk",
)

print("Figures written to", OUT)
