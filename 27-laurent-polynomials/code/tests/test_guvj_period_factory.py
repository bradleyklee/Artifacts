from __future__ import annotations

import io
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "guvj"))

from guvj_period_factory import Progress, t, theta, theta_operator_lines  # noqa: E402


def test_theta_operator_is_sorted_and_factored() -> None:
    operator = (
        23328*t**2*theta**2 + 46656*t**2*theta + 12960*t**2
        - 324*t*theta**2 - 324*t*theta - 60*t + theta**2
    )
    assert theta_operator_lines(operator) == [
        "theta**2",
        "- 12*t*(27*theta**2 + 27*theta + 5)",
        "+ 2592*t**2*(3*theta + 1)*(3*theta + 5)",
    ]


def test_progress_separates_A_theta_and_stays_within_80_columns() -> None:
    stream = io.StringIO()
    progress = Progress(total=8, enabled=True, stream=stream, width=80)
    with progress.stage("derive A and verify the Xi certificate") as details:
        details["description"] = "x" * 100
        details["A_theta"] = theta**2 - 81*t**2*theta**2 - 162*t**2*theta - 72*t**2

    lines = stream.getvalue().splitlines()
    assert max(map(len, lines)) <= 80
    done_line = next(line for line in lines if "done in" in line)
    assert "A_theta" not in done_line
    assert "      A_theta =" in lines
    assert "          theta**2" in lines
    assert "          - 9*t**2*(3*theta + 2)*(3*theta + 4)" in lines
