from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "guvj"))

import all_orders_solver as solver  # noqa: E402

from all_orders_solver import (  # noqa: E402
    Progress,
    derive,
    find_operator,
    operator_order,
    parse_laurent,
    solve_divergence_certificate,
    support_basis,
    t,
    theta,
    x,
    y,
)


def test_segment_support_includes_interior_lattice_points() -> None:
    assert support_basis(x + 1 / x, 1) == [(-1, 0), (0, 0), (1, 0)]


def test_exact_input_contract() -> None:
    assert parse_laurent("u + 1/u") == x + 1 / x
    assert parse_laurent("I*u + 1/u + v + 1/v").has(sp.I)
    with pytest.raises(ValueError):
        parse_laurent("0.5*x + 1/x")
    with pytest.raises(ValueError):
        parse_laurent("sqrt(x) + 1/x")
    with pytest.raises(ValueError):
        parse_laurent("1/(x + y)")
    with pytest.raises(ValueError):
        parse_laurent("sqrt(2)*x + 1/x")


def test_order_one_certificate() -> None:
    F = x + 1 / x
    operator, _, stats = find_operator(
        F, max_order=2, max_shift_degree=4
    )
    assert stats["order"] == 1
    assert operator_order(operator) == 1
    assert sp.expand(operator - (4*t**2*theta + 4*t**2 - theta)) == 0
    certificate = solve_divergence_certificate(F, operator, max_dilation=2)
    assert certificate["dilation"] == 1


def test_order_two_certificate() -> None:
    F = x + y + 1 / (x * y)
    operator, _, stats = find_operator(
        F, max_order=3, max_shift_degree=6
    )
    assert stats["order"] == 2
    assert operator_order(operator) == 2
    certificate = solve_divergence_certificate(F, operator, max_dilation=2)
    assert certificate["dilation"] == 2



def test_former_order_three_case_is_exactly_order_two() -> None:
    F = x + y + 1 / (x * y) + y**2 / x
    result = derive(
        F, max_order=2, max_support_level=1, progress_enabled=False
    )
    assert result["operator_stats"]["order"] == 2
    assert result["checks"]["operator_from_joint_exact_identity"] is True
    assert result["checks"]["operator_from_finite_term_fit"] is False



def test_production_path_does_not_call_term_fitter(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("finite-term fitter called by production derive")

    monkeypatch.setattr(solver, "find_operator", forbidden)
    result = solver.derive(
        x + 1 / x,
        max_order=1,
        max_support_level=1,
        progress_enabled=False,
    )
    assert result["operator_stats"]["order"] == 1


def test_progress_lines_are_at_most_80_columns() -> None:
    stream = io.StringIO()
    progress = Progress(enabled=True, stream=stream, width=80)
    progress.emit(
        "operator trial with a deliberately long description that must wrap "
        "without producing any physical line wider than eighty columns"
    )
    assert stream.getvalue()
    assert max(map(len, stream.getvalue().splitlines())) <= 80


def test_gaussian_rational_certificate() -> None:
    F = sp.I * x + 1 / x
    operator, _, stats = find_operator(
        F, max_order=2, max_shift_degree=4
    )
    assert stats["order"] == 1
    certificate = solve_divergence_certificate(F, operator, max_dilation=2)
    assert certificate["dilation"] == 1
