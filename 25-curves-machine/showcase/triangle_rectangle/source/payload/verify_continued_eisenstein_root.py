#!/usr/bin/env python3
"""Verify the continued X-based Eisenstein fourth root on 0 <= alpha < 1."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import mpmath as mp

PRECISION_DIGITS = 80
SAMPLE_TEXT = [
    "0", "0.20", "0.40", "0.56", "0.60", "0.64", "0.72",
    "0.80", "0.88", "0.96", "0.996",
]


def alpha_star() -> mp.mpf:
    return 4 * (mp.sqrt(6) - 2) / 3


def X_of_alpha(alpha: mp.mpf) -> mp.mpf:
    return (
        -108 * alpha**2 * (alpha - 1) * (9 * alpha + 16) ** 2
        / (9 * alpha**2 + 16) ** 3
    )


def z4_of_alpha(alpha: mp.mpf) -> mp.mpf:
    return alpha * (9 * alpha + 16) / (3 * alpha + 2) ** 2


def m_of_alpha(alpha: mp.mpf) -> mp.mpf:
    root = mp.sqrt(1 - alpha)
    return (3 * alpha + 2 - 2 * root) / (3 * alpha + 2 + 2 * root)


def direct_period(alpha: mp.mpf) -> mp.mpf:
    return (
        mp.hyp2f1(mp.mpf(1) / 4, mp.mpf(3) / 4, 1, z4_of_alpha(alpha))
        * mp.sqrt(2 / (2 + 3 * alpha))
    )


def principal_X_period(alpha: mp.mpf) -> mp.mpf:
    return (
        mp.hyp2f1(mp.mpf(1) / 12, mp.mpf(5) / 12, 1, X_of_alpha(alpha))
        / (1 + 9 * alpha**2 / 16) ** (mp.mpf(1) / 4)
    )


def connection_A(X: mp.mpf) -> mp.mpf:
    return (
        mp.sqrt(mp.pi)
        / (mp.gamma(mp.mpf(11) / 12) * mp.gamma(mp.mpf(7) / 12))
        * mp.hyp2f1(
            mp.mpf(1) / 12,
            mp.mpf(5) / 12,
            mp.mpf(1) / 2,
            1 - X,
        )
    )


def connection_B(X: mp.mpf) -> mp.mpf:
    return (
        -2
        * mp.sqrt(mp.pi)
        / (mp.gamma(mp.mpf(1) / 12) * mp.gamma(mp.mpf(5) / 12))
        * mp.hyp2f1(
            mp.mpf(11) / 12,
            mp.mpf(7) / 12,
            mp.mpf(3) / 2,
            1 - X,
        )
    )


def signed_sqrt_one_minus_X(alpha: mp.mpf) -> mp.mpf:
    return (
        (3 * alpha + 2) * (32 - 48 * alpha - 9 * alpha**2)
        / (9 * alpha**2 + 16) ** (mp.mpf(3) / 2)
    )


def continued_eisenstein_root(alpha: mp.mpf) -> mp.mpf:
    X = X_of_alpha(alpha)
    return connection_A(X) + signed_sqrt_one_minus_X(alpha) * connection_B(X)


def continued_X_period(alpha: mp.mpf) -> mp.mpf:
    return continued_eisenstein_root(alpha) / (1 + 9 * alpha**2 / 16) ** (mp.mpf(1) / 4)


def _text(value: mp.mpf, digits: int = 40) -> str:
    return mp.nstr(value, digits)


def build_report() -> dict[str, Any]:
    mp.mp.dps = PRECISION_DIGITS
    astar = alpha_star()
    near = mp.mpf("4e-8")
    samples = [mp.mpf(value) for value in SAMPLE_TEXT]
    samples[4:4] = [astar - near, astar, astar + near]

    rows: list[dict[str, str]] = []
    max_continued_error = mp.mpf("0")
    for alpha in samples:
        direct = direct_period(alpha)
        principal = principal_X_period(alpha)
        continued = continued_X_period(alpha)
        principal_error = abs(principal - direct)
        continued_error = abs(continued - direct)
        max_continued_error = max(max_continued_error, continued_error)
        rows.append(
            {
                "alpha": _text(alpha),
                "X": _text(X_of_alpha(alpha)),
                "m": _text(m_of_alpha(alpha)),
                "direct_period": _text(direct),
                "principal_X_period": _text(principal),
                "continued_X_period": _text(continued),
                "principal_abs_error": _text(principal_error, 22),
                "continued_abs_error": _text(continued_error, 22),
            }
        )

    h = mp.mpf("4e-7")
    value_at_fold = continued_X_period(astar)
    left_slope = (value_at_fold - continued_X_period(astar - h)) / h
    right_slope = (continued_X_period(astar + h) - value_at_fold) / h
    direct_slope = mp.diff(direct_period, astar)

    return {
        "schema": "triangle-rectangle-continued-eisenstein-root-check/1.1",
        "precision_digits": PRECISION_DIGITS,
        "normalization": "alpha_new=4*alpha_old; p_new=2*p_old; q_new=2*q_old",
        "alpha_star": _text(astar, 60),
        "X_alpha_star": _text(X_of_alpha(astar), 60),
        "m_alpha_star": _text(m_of_alpha(astar), 60),
        "direct_period_alpha_star": _text(direct_period(astar), 60),
        "direct_period_derivative_alpha_star": _text(direct_slope, 60),
        "continued_left_difference_quotient": _text(left_slope, 40),
        "continued_right_difference_quotient": _text(right_slope, 40),
        "maximum_continued_abs_error_on_samples": _text(max_continued_error, 22),
        "principal_abs_error_alpha_0_60": _text(
            abs(principal_X_period(mp.mpf("0.60")) - direct_period(mp.mpf("0.60"))), 22
        ),
        "principal_abs_error_alpha_0_80": _text(
            abs(principal_X_period(mp.mpf("0.80")) - direct_period(mp.mpf("0.80"))), 22
        ),
        "principal_abs_error_alpha_0_96": _text(
            abs(principal_X_period(mp.mpf("0.96")) - direct_period(mp.mpf("0.96"))), 22
        ),
        "rows": rows,
        "conclusion": (
            "The exact signed algebraic square root sigma(alpha), with sigma^2=1-X, "
            "continues the Eisenstein fourth root through alpha_star in the rescaled "
            "0 <= alpha < 1 normalization."
        ),
    }


def assert_report(report: dict[str, Any]) -> None:
    mp.mp.dps = PRECISION_DIGITS
    assert abs(mp.mpf(report["X_alpha_star"]) - 1) < mp.mpf("1e-70")
    assert abs(mp.mpf(report["m_alpha_star"]) - mp.mpf("0.5")) < mp.mpf("1e-70")
    assert mp.mpf(report["maximum_continued_abs_error_on_samples"]) < mp.mpf("1e-48")

    direct_slope = mp.mpf(report["direct_period_derivative_alpha_star"])
    left_slope = mp.mpf(report["continued_left_difference_quotient"])
    right_slope = mp.mpf(report["continued_right_difference_quotient"])
    assert abs(left_slope - direct_slope) < mp.mpf("3e-6")
    assert abs(right_slope - direct_slope) < mp.mpf("3e-6")
    assert abs(left_slope - right_slope) < mp.mpf("6e-6")

    assert mp.mpf(report["principal_abs_error_alpha_0_60"]) > mp.mpf("1e-4")
    assert mp.mpf(report["principal_abs_error_alpha_0_80"]) > mp.mpf("0.1")
    assert mp.mpf(report["principal_abs_error_alpha_0_96"]) > mp.mpf("0.4")


def write_report(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "continued_eisenstein_root_check.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    rows = report["rows"]
    with (output_dir / "continued_eisenstein_root_check.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    report = build_report()
    assert_report(report)
    write_report(report, Path(__file__).resolve().parent)
    summary = {key: value for key, value in report.items() if key != "rows"}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
