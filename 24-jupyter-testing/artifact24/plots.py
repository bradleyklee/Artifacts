
"""Plotly figures for notebooks, Binder, and Voila."""

from __future__ import annotations
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .geometry import (
    COLORS, FAMILY_KEYS, CENTROID, COMMON_IMAGE, VERTICES, NORMAL,
    polynomial_map, c3_loop, aw_closed_cycle, embed_red, embed_aw,
    source_axis, matched_point,
)

POINT_LEVELS = np.array([0.10, 0.22, 0.34, 0.46, 0.58, 0.70, 0.82, 0.92])


def merge_levels(base, extras=POINT_LEVELS):
    return np.array(sorted(set(map(float, base)) | set(map(float, extras))))


def source_basis():
    e1 = VERTICES[1] - VERTICES[2]
    e1 = e1 / np.linalg.norm(e1)
    e3 = NORMAL
    e2 = np.cross(e3, e1)
    e2 = e2 / np.linalg.norm(e2)
    return np.column_stack((e1, e2, e3))


_SOURCE_BASIS = source_basis()


def source_display(points):
    return (np.asarray(points) - CENTROID) @ _SOURCE_BASIS


def _xyz(points):
    points = np.asarray(points)
    return dict(x=points[:,0], y=points[:,1], z=points[:,2])


def build_interactive_figure(
    red_count=14,
    auxiliary_count=8,
    samples=520,
    show_background=True,
):
    red_levels = merge_levels(np.linspace(0.05, 0.98, red_count))
    aw_levels = merge_levels(np.linspace(0.08, 0.96, auxiliary_count))

    red_source = [embed_red(c3_loop(a, samples)) for a in red_levels]
    red_range = [polynomial_map(c) for c in red_source]
    aw_source = [
        [embed_aw(aw_closed_cycle(a, samples), family) for a in aw_levels]
        for family in range(3)
    ]
    aw_range = [[polynomial_map(c) for c in family] for family in aw_source]

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type":"scene"}, {"type":"scene"}]],
        subplot_titles=("Domain", "Range"),
        horizontal_spacing=0.02,
    )

    for family, key in enumerate(FAMILY_KEYS):
        for alpha, s_curve, r_curve in zip(aw_levels, aw_source[family], aw_range[family]):
            matched = np.any(np.isclose(alpha, POINT_LEVELS))
            if not matched and not show_background:
                continue
            for col, curve in ((1, source_display(s_curve)), (2, r_curve)):
                fig.add_trace(go.Scatter3d(
                    **_xyz(curve),
                    mode="lines",
                    line=dict(color=COLORS[key], width=5 if matched else 2),
                    opacity=0.92 if matched else 0.18,
                    name=f"{key} closed cycles",
                    legendgroup=key,
                    showlegend=bool(col == 1 and alpha == aw_levels[-1]),
                    text=[f"{key} closed cycle, alpha={alpha:.3f}"] * len(curve),
                    hoverinfo="text",
                ), row=1, col=col)

    for alpha, s_curve, r_curve in zip(red_levels, red_source, red_range):
        matched = np.any(np.isclose(alpha, POINT_LEVELS))
        if not matched and not show_background:
            continue
        for col, curve in ((1, source_display(s_curve)), (2, r_curve)):
            fig.add_trace(go.Scatter3d(
                **_xyz(curve),
                mode="lines",
                line=dict(color=COLORS["R"], width=6 if matched else 3),
                opacity=0.98 if matched else 0.28,
                name="red family",
                legendgroup="R",
                showlegend=bool(col == 1 and alpha == red_levels[-1]),
                text=[f"red level, alpha={alpha:.3f}"] * len(curve),
                hoverinfo="text",
            ), row=1, col=col)

    symbols = ["circle", "diamond", "square"]
    for family, key in enumerate(FAMILY_KEYS):
        s_axis = source_axis(family, 600)
        r_axis = polynomial_map(s_axis)
        for col, curve in ((1, source_display(s_axis)), (2, r_axis)):
            fig.add_trace(go.Scatter3d(
                **_xyz(curve), mode="lines",
                line=dict(color=COLORS[key], width=7),
                name=f"{key} principal axis",
                showlegend=(col == 1),
                hoverinfo="skip",
            ), row=1, col=col)

        s_points = np.array([matched_point(a, family) for a in POINT_LEVELS])
        r_points = polynomial_map(s_points)
        for col, points in ((1, source_display(s_points)), (2, r_points)):
            fig.add_trace(go.Scatter3d(
                **_xyz(points), mode="markers",
                marker=dict(
                    size=6, color=COLORS[key], symbol=symbols[family],
                    line=dict(color="black", width=1),
                ),
                name=f"exact {key}/red points",
                showlegend=(col == 1),
                text=[
                    f"{key}/red exact point<br>alpha={a:.2f}<br>"
                    + ", ".join(f"{v:.6g}" for v in p)
                    for a, p in zip(POINT_LEVELS, points)
                ],
                hoverinfo="text",
            ), row=1, col=col)

    fig.update_layout(
        title="Artifact 24: closed cycles and exact matched levels",
        height=760,
        width=1450,
        margin=dict(l=0, r=0, t=60, b=0),
        scene=dict(aspectmode="data", dragmode="orbit"),
        scene2=dict(aspectmode="data", dragmode="orbit"),
        uirevision="keep-camera",
    )
    return fig
