"""
Artifact 24: Q/R coordinate net on the discriminant surface

This project script is called by
`notebooks/artifact24_integer_periods_and_mesh.ipynb`.  It:
- locates the local `artifact24` package;
- loads the original two-panel Hamilton-Abel figure;
- removes marker clutter;
- overlays only TWO coordinate families on the discriminant surface:
    * constant Q curves (black)
    * constant R curves (black)
- overlays their finite inverse images on the left panel;
- overlays the pink missing cubic on the right panel;
- runs built-in algebraic verification before plotting.

It builds on `artifact24.plots.build_interactive_figure` rather than duplicating
the original closed-cycle depiction in notebook state.
"""

from pathlib import Path
import sys
import numpy as np
import plotly.graph_objects as go


def safe_divide(numerator, denominator, *, fill=np.nan, where=None):
    """Broadcasting divide that never evaluates excluded entries."""
    num, den = np.broadcast_arrays(
        np.asarray(numerator, dtype=float), np.asarray(denominator, dtype=float)
    )
    if where is None:
        where = den != 0.0
    else:
        where = np.broadcast_to(np.asarray(where, dtype=bool), den.shape)
    out = np.full(den.shape, fill, dtype=float)
    np.divide(num, den, out=out, where=where)
    return out

# ============================================================
# Bootstrap: locate the artifact24 package
# ============================================================

HERE = Path.cwd().resolve()

candidates = []
for base in (HERE, *HERE.parents):
    candidates.extend([
        base,
        base / "24-jupyter-testing",
        base / "Artifacts" / "24-jupyter-testing",
    ])

PROJECT_ROOT = next(
    (
        candidate
        for candidate in candidates
        if (candidate / "artifact24" / "geometry.py").is_file()
        and (candidate / "artifact24" / "plots.py").is_file()
    ),
    None,
)

if PROJECT_ROOT is None:
    raise RuntimeError(
        "Could not locate the artifact24 package.\n"
        f"Current directory: {HERE}\n\n"
        "The notebook must be inside the Artifacts repository, or beside "
        "the 24-jupyter-testing folder."
    )

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from artifact24.geometry import polynomial_map
from artifact24.plots import build_interactive_figure, source_display

print("Artifact 24 loaded from:", PROJECT_ROOT)

# ============================================================
# User choices
# ============================================================

Q_LEVELS = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]
R_LEVELS = [-1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]

BLACK = "#111111"
PINK = "#ff00aa"

# ============================================================
# Geometry / algebra helpers
# ============================================================

def discriminant(P, Q, R):
    return Q*Q - 16.0*P - Q**3 * R + 18.0*P*Q*R - 27.0*(P**2)*(R**2)

def discriminant_error(P, Q, R):
    """
    Return both absolute and scale-aware residuals.

    The discriminant is a cancellation of five polynomial terms.  Its
    absolute roundoff can be around 1e-9 even when the relative error is near
    machine precision, so verification must use the scaled residual.
    """
    terms = (
        Q*Q,
        -16.0*P,
        -Q**3 * R,
        18.0*P*Q*R,
        -27.0*(P**2)*(R**2),
    )
    residual = abs(sum(terms))
    scale = max(1.0, sum(abs(term) for term in terms))
    return residual, residual / scale

def finite_preimage_from_rho_c(rho, c, pole_tolerance=1.0e-14):
    """Finite preimage parameterization without evaluating its pole."""
    rho, c = np.broadcast_arrays(
        np.asarray(rho, dtype=float), np.asarray(c, dtype=float)
    )
    den = 3.0 * c * rho - 2.0
    valid = np.abs(den) >= pole_tolerance

    x = safe_divide(2.0 * c, den**2, where=valid)
    y = rho * (8.0 - 9.0 * c * rho) / 2.0
    z = (
        -9.0
        * rho**2
        * den**2
        * (9.0 * c**2 * rho**2 - 24.0 * c * rho + 14.0)
        / 8.0
    )
    y = np.where(valid, y, np.nan)
    z = np.where(valid, z, np.nan)
    return x, y, z, den

def _trace_bounds(figure, scene_name, coordinate):
    chunks = []
    for trace in figure.data:
        if getattr(trace, "scene", "scene") != scene_name:
            continue
        values = getattr(trace, coordinate, None)
        if values is None:
            continue
        try:
            values = np.asarray(values, dtype=float).reshape(-1)
        except (TypeError, ValueError):
            continue
        values = values[np.isfinite(values)]
        if values.size:
            chunks.append(values)

    if not chunks:
        raise RuntimeError(f"No finite {coordinate}-values found in {scene_name}")

    values = np.concatenate(chunks)
    lo = float(values.min())
    hi = float(values.max())
    pad = 0.03 * max(hi - lo, 1.0)
    return lo - pad, hi + pad

def _clip3(x, y, z, xr, yr, zr):
    mask = (
        np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        & (x >= xr[0]) & (x <= xr[1])
        & (y >= yr[0]) & (y <= yr[1])
        & (z >= zr[0]) & (z <= zr[1])
    )
    return (
        np.where(mask, x, np.nan),
        np.where(mask, y, np.nan),
        np.where(mask, z, np.nan),
    )

# ============================================================
# Verification
# ============================================================

_OLD_NUMPY_ERRORS = np.seterr(divide="raise", invalid="raise", over="raise", under="ignore")

rho_samples_Q = np.array([-3.0, -1.7, -0.8, -0.3, 0.35, 0.9, 1.8, 3.1], dtype=float)
rho_samples_R = np.array([-3.2, -2.0, -1.2, -0.6, 0.5, 1.1, 2.1, 3.0], dtype=float)

max_inverse_residual = 0.0
max_surface_absolute_residual = 0.0
max_surface_scaled_residual = 0.0
max_fixed_coordinate_residual = 0.0
max_pink_absolute_error = 0.0
max_pink_scaled_error = 0.0
qr_lattice_real = 0
qr_lattice_total = 0

# Constant-Q family verification
for q0 in Q_LEVELS:
    for rho in rho_samples_Q:
        if abs(rho) < 1e-12:
            continue

        P = rho * (q0 - rho) / 3.0
        Q = q0
        R = safe_divide(4.0 * rho - q0, 3.0 * rho**2)

        surface_abs, surface_scaled = discriminant_error(P, Q, R)
        max_surface_absolute_residual = max(
            max_surface_absolute_residual, surface_abs
        )
        max_surface_scaled_residual = max(
            max_surface_scaled_residual, surface_scaled
        )
        max_fixed_coordinate_residual = max(
            max_fixed_coordinate_residual, abs(Q - q0)
        )

        x, y, z, den = finite_preimage_from_rho_c(np.array([rho]), np.array([R]))
        if abs(den[0]) < 1e-7:
            continue
        mapped = polynomial_map(np.array([[x[0], y[0], z[0]]], dtype=float))[0]
        target = np.array([P, Q, R], dtype=float)

        scale = max(1.0, np.max(np.abs(target)))
        max_inverse_residual = max(
            max_inverse_residual,
            np.max(np.abs(mapped - target)) / scale
        )

# Constant-R family verification
for r0 in R_LEVELS:
    for rho in rho_samples_R:
        P = rho**2 - r0 * rho**3
        Q = 4.0 * rho - 3.0 * r0 * rho**2
        R = r0

        surface_abs, surface_scaled = discriminant_error(P, Q, R)
        max_surface_absolute_residual = max(
            max_surface_absolute_residual, surface_abs
        )
        max_surface_scaled_residual = max(
            max_surface_scaled_residual, surface_scaled
        )
        max_fixed_coordinate_residual = max(
            max_fixed_coordinate_residual, abs(R - r0)
        )

        x, y, z, den = finite_preimage_from_rho_c(np.array([rho]), np.array([r0]))
        if abs(den[0]) < 1e-7:
            continue
        mapped = polynomial_map(np.array([[x[0], y[0], z[0]]], dtype=float))[0]
        target = np.array([P, Q, R], dtype=float)

        scale = max(1.0, np.max(np.abs(target)))
        max_inverse_residual = max(
            max_inverse_residual,
            np.max(np.abs(mapped - target)) / scale
        )

# Pink missing curve verification
pink_rho = np.array([-4.0, -2.0, -0.7, 0.5, 1.6, 3.0], dtype=float)
for rho in pink_rho:
    P = rho**2 / 3.0
    Q = 2.0 * rho
    R = safe_divide(2.0, 3.0 * rho)
    pink_abs, pink_scaled = discriminant_error(P, Q, R)
    max_pink_absolute_error = max(max_pink_absolute_error, pink_abs)
    max_pink_scaled_error = max(max_pink_scaled_error, pink_scaled)

# Q/R lattice: each pair (Q,R) should generically meet surface in 0,1,2 real points.
# For our chosen modest lattice this mainly checks that the chosen levels do produce
# intersections around the central visible figure.
for q0 in Q_LEVELS:
    for r0 in R_LEVELS:
        qr_lattice_total += 1
        # Solve 3 r rho^2 - 4 rho + q = 0
        if abs(r0) < 1e-14:
            # Then q = 4 rho, exactly one real rho
            qr_lattice_real += 1
        else:
            disc = 16.0 - 12.0 * r0 * q0
            if disc >= 0.0:
                qr_lattice_real += 1

assert max_inverse_residual < 1e-8, max_inverse_residual
assert max_surface_scaled_residual < 1e-12, max_surface_scaled_residual
assert max_fixed_coordinate_residual < 1e-12, max_fixed_coordinate_residual
assert max_pink_scaled_error < 1e-12, max_pink_scaled_error

print("Verification passed")
print(f"  max inverse scaled residual:     {max_inverse_residual:.3e}")
print(f"  max surface absolute residual:   {max_surface_absolute_residual:.3e}")
print(f"  max surface scaled residual:     {max_surface_scaled_residual:.3e}")
print(f"  max fixed-coordinate residual:   {max_fixed_coordinate_residual:.3e}")
print(f"  max pink absolute error:         {max_pink_absolute_error:.3e}")
print(f"  max pink scaled error:           {max_pink_scaled_error:.3e}")
print(f"  Q/R lattice pairs with real intersections: {qr_lattice_real}/{qr_lattice_total}")

# ============================================================
# Build the original Artifact 24 figure and remove markers
# ============================================================

fig_base = build_interactive_figure(
    red_count=12,
    auxiliary_count=8,
    samples=420,
    show_background=True,
)

filtered = []
for trace in fig_base.data:
    mode = str(getattr(trace, "mode", ""))
    if trace.type == "scatter3d" and mode == "markers":
        continue
    filtered.append(trace)

fig1 = go.Figure(data=filtered, layout=fig_base.layout)

# Slightly strengthen surviving colored line traces
for trace in fig1.data:
    if trace.type == "scatter3d" and "lines" in str(getattr(trace, "mode", "")):
        old_width = getattr(getattr(trace, "line", None), "width", None)
        old_width = 2.0 if old_width is None else float(old_width)
        trace.line.width = max(old_width, 3.0)

# Preserve the original plotting windows
domain_bounds = {
    "x": _trace_bounds(fig1, "scene", "x"),
    "y": _trace_bounds(fig1, "scene", "y"),
    "z": _trace_bounds(fig1, "scene", "z"),
}
range_bounds = {
    "x": _trace_bounds(fig1, "scene2", "x"),  # P
    "y": _trace_bounds(fig1, "scene2", "y"),  # Q
    "z": _trace_bounds(fig1, "scene2", "z"),  # R
}

x_range = domain_bounds["x"]
y_range = domain_bounds["y"]
z_range = domain_bounds["z"]

P_range = range_bounds["x"]
Q_range = range_bounds["y"]
R_range = range_bounds["z"]

rho_line = np.linspace(-4.0, 4.0, 3200)
rho_abs = np.geomspace(0.04, 8.0, 4200)

# ============================================================
# Constant R curves (range + finite preimages)
# ============================================================

first_R_range = True
first_R_domain = True

for R0 in R_LEVELS:
    rho = rho_line
    c = np.full_like(rho, R0, dtype=float)

    # Range curve
    P = rho**2 - c * rho**3
    Q = 4.0 * rho - 3.0 * c * rho**2
    R = c

    P, Q, R = _clip3(P, Q, R, P_range, Q_range, R_range)

    if np.isfinite(P).sum() >= 2:
        fig1.add_trace(
            go.Scatter3d(
                x=P, y=Q, z=R,
                mode="lines",
                line=dict(color=BLACK, width=2),
                name="constant R" if first_R_range else "constant R ",
                legendgroup="const-R-range",
                showlegend=first_R_range,
                hovertemplate=(
                    f"<b>constant R={R0:g}</b>"
                    "<br>P=%{x:.5g}"
                    "<br>Q=%{y:.5g}"
                    "<extra></extra>"
                ),
                scene="scene2",
            )
        )
        first_R_range = False

    # Domain finite preimage
    X, Y, Z, den = finite_preimage_from_rho_c(rho, c)
    away = np.abs(den) >= 0.04
    X = np.where(away, X, np.nan)
    Y = np.where(away, Y, np.nan)
    Z = np.where(away, Z, np.nan)

    raw_pts = np.column_stack([X, Y, Z])
    disp_pts = source_display(raw_pts)

    XD = disp_pts[:, 0]
    YD = disp_pts[:, 1]
    ZD = disp_pts[:, 2]

    XD, YD, ZD = _clip3(XD, YD, ZD, x_range, y_range, z_range)

    if np.isfinite(XD).sum() >= 2:
        fig1.add_trace(
            go.Scatter3d(
                x=XD, y=YD, z=ZD,
                mode="lines",
                line=dict(color=BLACK, width=2),
                name="preimage of constant R" if first_R_domain else "preimage of constant R ",
                legendgroup="const-R-domain",
                showlegend=first_R_domain,
                hovertemplate=(
                    f"<b>preimage of R={R0:g}</b>"
                    "<br>display x=%{x:.5g}"
                    "<br>display y=%{y:.5g}"
                    "<br>display z=%{z:.5g}"
                    "<extra></extra>"
                ),
                scene="scene",
            )
        )
        first_R_domain = False

# ============================================================
# Constant Q curves (range + finite preimages)
# ============================================================

first_Q_range = True
first_Q_domain = True

for Q0 in Q_LEVELS:
    for sign in (+1.0, -1.0):
        rho = sign * rho_abs

        # Range curve
        P = rho * (Q0 - rho) / 3.0
        Q = np.full_like(rho, Q0, dtype=float)
        R = safe_divide(4.0 * rho - Q0, 3.0 * rho**2)

        P, Q, R = _clip3(P, Q, R, P_range, Q_range, R_range)

        if np.isfinite(P).sum() >= 2:
            fig1.add_trace(
                go.Scatter3d(
                    x=P, y=Q, z=R,
                    mode="lines",
                    line=dict(color=BLACK, width=3),
                    name="constant Q" if first_Q_range else "constant Q ",
                    legendgroup="const-Q-range",
                    showlegend=first_Q_range,
                    hovertemplate=(
                        f"<b>constant Q={Q0:g}</b>"
                        "<br>P=%{x:.5g}"
                        "<br>R=%{z:.5g}"
                        "<extra></extra>"
                    ),
                    scene="scene2",
                )
            )
            first_Q_range = False

        # Domain finite preimage
        c = safe_divide(4.0 * rho - Q0, 3.0 * rho**2)
        X, Y, Z, den = finite_preimage_from_rho_c(rho, c)

        away = np.abs(den) >= 0.04
        X = np.where(away, X, np.nan)
        Y = np.where(away, Y, np.nan)
        Z = np.where(away, Z, np.nan)

        raw_pts = np.column_stack([X, Y, Z])
        disp_pts = source_display(raw_pts)

        XD = disp_pts[:, 0]
        YD = disp_pts[:, 1]
        ZD = disp_pts[:, 2]

        XD, YD, ZD = _clip3(XD, YD, ZD, x_range, y_range, z_range)

        if np.isfinite(XD).sum() >= 2:
            fig1.add_trace(
                go.Scatter3d(
                    x=XD, y=YD, z=ZD,
                    mode="lines",
                    line=dict(color=BLACK, width=3),
                    name="preimage of constant Q" if first_Q_domain else "preimage of constant Q ",
                    legendgroup="const-Q-domain",
                    showlegend=first_Q_domain,
                    hovertemplate=(
                        f"<b>preimage of Q={Q0:g}</b>"
                        "<br>display x=%{x:.5g}"
                        "<br>display y=%{y:.5g}"
                        "<br>display z=%{z:.5g}"
                        "<extra></extra>"
                    ),
                    scene="scene",
                )
            )
            first_Q_domain = False

# ============================================================
# Pink missing cubic in the range only
#
# Draw it twice:
#   1. a broad white under-stroke separating it from black lines;
#   2. a narrower saturated pink stroke.
#
# Both traces are appended AFTER every black and colored curve.
# ============================================================

rho_missing_abs = np.geomspace(1.0e-5, 1.0e5, 50000)
pink_branch_data = []

for sign in (+1.0, -1.0):
    rho = sign * rho_missing_abs

    P = rho**2 / 3.0
    Q = 2.0 * rho
    R = safe_divide(2.0, 3.0 * rho)

    P, Q, R = _clip3(P, Q, R, P_range, Q_range, R_range)

    visible = np.isfinite(P) & np.isfinite(Q) & np.isfinite(R)
    if np.count_nonzero(visible) >= 2:
        pink_branch_data.append((P, Q, R))

if len(pink_branch_data) != 2:
    raise RuntimeError(
        "Expected two visible pink branches, but found "
        f"{len(pink_branch_data)}. "
        "The current range-panel bounds may exclude a branch."
    )

# White halo first.
for branch_index, (P, Q, R) in enumerate(pink_branch_data):
    fig1.add_trace(
        go.Scatter3d(
            x=P,
            y=Q,
            z=R,
            mode="lines",
            line=dict(color="#ffffff", width=18),
            opacity=1.0,
            name="missing cubic halo",
            legendgroup="missing-cubic",
            showlegend=False,
            hoverinfo="skip",
            scene="scene2",
        )
    )

# Pink curve second, so it is the final geometry added to the figure.
for branch_index, (P, Q, R) in enumerate(pink_branch_data):
    fig1.add_trace(
        go.Scatter3d(
            x=P,
            y=Q,
            z=R,
            mode="lines",
            line=dict(color=PINK, width=12),
            opacity=1.0,
            name="missing cubic" if branch_index == 0 else "missing cubic ",
            legendgroup="missing-cubic",
            legendrank=1,
            showlegend=(branch_index == 0),
            hovertemplate=(
                "<b>missing triple-root curve</b>"
                "<br>P=%{x:.5g}"
                "<br>Q=%{y:.5g}"
                "<br>R=%{z:.5g}"
                "<extra></extra>"
            ),
            scene="scene2",
        )
    )

pink_visible_points = sum(
    int(np.count_nonzero(np.isfinite(P)))
    for P, Q, R in pink_branch_data
)
print(
    "Pink missing cubic added:",
    f"{len(pink_branch_data)} branches,",
    f"{pink_visible_points} visible sampled points",
)

# ============================================================
# Freeze panel windows and display
# ============================================================

fig1.layout.scene.xaxis.range = list(x_range)
fig1.layout.scene.yaxis.range = list(y_range)
fig1.layout.scene.zaxis.range = list(z_range)
fig1.layout.scene.xaxis.autorange = False
fig1.layout.scene.yaxis.autorange = False
fig1.layout.scene.zaxis.autorange = False

fig1.layout.scene2.xaxis.range = list(P_range)
fig1.layout.scene2.yaxis.range = list(Q_range)
fig1.layout.scene2.zaxis.range = list(R_range)
fig1.layout.scene2.xaxis.autorange = False
fig1.layout.scene2.yaxis.autorange = False
fig1.layout.scene2.zaxis.autorange = False

fig1.update_layout(
    title="Hamilton-Abel families with constant Q and constant R coordinate curves",
)

pink_traces = [
    trace for trace in fig1.data
    if str(getattr(trace, "name", "")).startswith("missing cubic")
    and str(getattr(trace, "name", "")) != "missing cubic halo"
]
assert len(pink_traces) == 2, len(pink_traces)

fig1.show(config={"scrollZoom": True, "displaylogo": False})
np.seterr(**_OLD_NUMPY_ERRORS)
