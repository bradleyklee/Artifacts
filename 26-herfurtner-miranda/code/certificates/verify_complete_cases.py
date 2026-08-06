#!/usr/bin/env python3
"""Verify every complete Hamiltonian/Laurent model through one interface.

The verifier uses exact polynomial arithmetic, exact sparse Laurent arithmetic,
coefficient extraction, and named recurrence transformations.  It does not use
``sympy.simplify`` as a proof step.
"""
from __future__ import annotations

import argparse
import json
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXAMPLES = ROOT / "examples"
DATA = EXAMPLES / "data"
PUBLIC = EXAMPLES / "public"
OLD_CERT = EXAMPLES / "certificates" / "models_01_02_03_09"
NEW_CERT = EXAMPLES / "certificates" / "models_05_07"
MODEL2 = EXAMPLES / "A303790"

MODELS = json.loads((DATA / "models_11_release.json").read_text())
FORMULAS = json.loads((NEW_CERT / "exact_formulas.json").read_text())
MANIFEST = json.loads((PUBLIC / "complete_cases.json").read_text())
COMPLETE_MODELS = tuple(item["model"] for item in MANIFEST["models"])

p, q, E, n, w, z, x, y, t = sp.symbols("p q E n w z x y t")
START = time.monotonic()

H = {
    1: p**2 + q**2 + p*q**2 + q**3,
    2: p**2 + q**2 + p**3 + q**3,
    3: p**2 + q**2 - p**3 - 3*p**2*q - 2*q**3,
    9: p**2 + q**2 + (q**2 - 4*p**2) ** 2,
}
G = {
    1: -sp.I*x**3 + (2+4*sp.I)*x**2 + (-8-5*sp.I)*x + 12
       + (-8+5*sp.I)/x + (2-4*sp.I)/x**2 + sp.I/x**3,
    3: -sp.I*x**3 + (-6-12*sp.I)*x**2 + (-24-21*sp.I)*x + 92
       + (-24+21*sp.I)/x + (-6+12*sp.I)/x**2 + sp.I/x**3,
    9: -25*x**2 - 60*x - 86 - 60/x - 25/x**2,
}

SparseLaurent = dict[tuple[int, ...], sp.Expr]


def progress(message: str, enabled: bool = True) -> None:
    """Print a flushed progress message with every line at most 80 columns."""
    if not enabled:
        return
    elapsed = time.monotonic() - START
    prefix = f"[complete] {elapsed:7.2f}s  "
    width = 80 - len(prefix)
    lines = textwrap.wrap(
        message,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    print(prefix + lines[0], flush=True)
    indent = " " * len(prefix)
    for line in lines[1:]:
        print(indent + line, flush=True)


def model(index: int) -> dict:
    return MODELS["models"][index - 1]


def poly_pqE(expression: sp.Expr) -> sp.Poly:
    return sp.Poly(expression, p, q, E, domain=sp.QQ)


def sparse_expr(
    expression: sp.Expr,
    variables: tuple[sp.Symbol, ...],
) -> SparseLaurent:
    out: SparseLaurent = {}
    for term in sp.Add.make_args(sp.expand(expression)):
        powers = term.as_powers_dict()
        exponent = tuple(int(powers.get(variable, 0)) for variable in variables)
        monomial = sp.prod(
            variable**power
            for variable, power in zip(variables, exponent, strict=True)
        )
        coefficient = sp.expand(term / monomial)
        out[exponent] = out.get(exponent, 0) + coefficient
    return {key: value for key, value in out.items() if value != 0}


def sparse_add(*items: tuple[SparseLaurent, sp.Expr]) -> SparseLaurent:
    out: SparseLaurent = {}
    for polynomial, scale in items:
        for key, value in polynomial.items():
            out[key] = sp.expand(out.get(key, 0) + scale * value)
            if out[key] == 0:
                del out[key]
    return out


def sparse_mul(left: SparseLaurent, right: SparseLaurent) -> SparseLaurent:
    out: SparseLaurent = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(
                a + b for a, b in zip(left_key, right_key, strict=True)
            )
            out[key] = sp.expand(
                out.get(key, 0) + left_value * right_value
            )
    return {key: value for key, value in out.items() if value != 0}


def sparse_power(base: SparseLaurent, exponent: int) -> SparseLaurent:
    out: SparseLaurent = {(0,) * len(next(iter(base))): sp.Integer(1)}
    for _ in range(exponent):
        out = sparse_mul(out, base)
    return out


def sparse_scale(polynomial: SparseLaurent, factor: sp.Expr) -> SparseLaurent:
    return {
        key: sp.expand(factor * value)
        for key, value in polynomial.items()
        if sp.expand(factor * value) != 0
    }


def sparse_log_derivative(
    polynomial: SparseLaurent,
    position: int,
) -> SparseLaurent:
    return {
        key: sp.expand(key[position] * value)
        for key, value in polynomial.items()
        if key[position] != 0
    }


def constant_terms(
    expression: sp.Expr,
    variables: tuple[sp.Symbol, ...],
    count: int,
) -> list[sp.Expr]:
    polynomial = sparse_expr(expression, variables)
    zero = (0,) * len(variables)
    power: SparseLaurent = {zero: sp.Integer(1)}
    values = []
    for _ in range(count):
        values.append(sp.expand(power.get(zero, 0)))
        power = sparse_mul(power, polynomial)
    return values


def verify_vector_hamiltonian(index: int) -> None:
    item = model(index)
    certificate = item["certificate"]
    operator = certificate["hamiltonian_operator_E"]
    loc = {"E": E, "alpha": E, "p": p, "q": q}
    A2 = sp.sympify(operator["A2"], locals=loc)
    A1 = sp.sympify(operator["A1"], locals=loc)
    A0 = sp.sympify(operator["A0"], locals=loc)
    P = poly_pqE(sp.sympify(
        (OLD_CERT / Path(certificate["hamiltonian_P_file"]).name).read_text(),
        locals=loc,
    ))
    Q = poly_pqE(sp.sympify(
        (OLD_CERT / Path(certificate["hamiltonian_Q_file"]).name).read_text(),
        locals=loc,
    ))
    hamiltonian = poly_pqE(H[index])
    divisor = poly_pqE(H[index] - E)
    left = poly_pqE(2*A2) + poly_pqE(A1)*divisor
    left += poly_pqE(A0)*divisor*divisor
    right = divisor*(P.diff(p) + Q.diff(q))
    right -= 2*(P*hamiltonian.diff(p) + Q*hamiltonian.diff(q))
    if right != left:
        raise AssertionError("exact residual is nonzero")


def verify_scalar_hamiltonian(index: int) -> None:
    item = FORMULAS[f"model{index}"]
    loc = {"p": p, "q": q, "E": E}
    K = sp.sympify(item["K"], locals=loc)
    A2 = sp.sympify(item["A2E"], locals=loc)
    A1 = sp.sympify(item["A1E"], locals=loc)
    A0 = sp.sympify(item["A0E"], locals=loc)
    V = sp.sympify(
        (NEW_CERT / f"model{index}_scalar_V.txt").read_text(),
        locals=loc,
    )
    Kp = sp.diff(K, p)
    Kq = sp.diff(K, q)

    def D_E(value: sp.Expr) -> sp.Expr:
        return sp.cancel(sp.diff(value, p) / Kp)

    base = 2 / Kp
    left = sp.cancel(A2*D_E(D_E(base)) + A1*D_E(base) + A0*base)
    Xi = sp.cancel(V / Kp**3)
    right = sp.cancel(sp.diff(Xi, q) - Kq*sp.diff(Xi, p)/Kp)
    numerator, _ = sp.fraction(sp.cancel(left - right))
    remainder = sp.Poly(sp.expand(numerator), p).rem(sp.Poly(K-E, p))
    if remainder.as_expr() != 0:
        raise AssertionError("exact residual is nonzero modulo 2H-E")


def verify_hamiltonian(index: int) -> None:
    if index in (1, 2, 3, 9):
        verify_vector_hamiltonian(index)
    elif index in (5, 7):
        verify_scalar_hamiltonian(index)
    else:
        raise ValueError(f"model {index} is not complete")


def verify_sparse_angular_laurent(index: int) -> None:
    item = model(index)
    certificate = item["certificate"]
    recurrence = {
        int(key): sp.sympify(value, locals={"n": n})
        for key, value in certificate["angular_recurrence"].items()
    }
    R = sp.sympify(
        (OLD_CERT / Path(certificate["laurent_R_file"]).name).read_text(),
        locals={"n": n, "x": x, "I": sp.I},
    )
    g = sparse_expr(G[index], (x,))
    g_with_n = {(key[0], 0): value for key, value in g.items()}
    r = sparse_expr(R, (x, n))
    recurrence_sum: SparseLaurent = {}
    for exponent, coefficient in recurrence.items():
        term = sparse_mul(
            sparse_expr(coefficient, (x, n)),
            sparse_power(g_with_n, exponent),
        )
        recurrence_sum = sparse_add((recurrence_sum, 1), (term, 1))
    dx_r = sparse_log_derivative(r, 0)
    dx_g = sparse_log_derivative(g_with_n, 0)
    n_dx_g = {
        (key[0], key[1] + 1): value
        for key, value in dx_g.items()
    }
    residual = sparse_add(
        (sparse_mul(g_with_n, recurrence_sum), 1),
        (sparse_mul(g_with_n, dx_r), -1),
        (sparse_mul(n_dx_g, r), -1),
    )
    if residual:
        raise AssertionError("exact sparse residual is nonzero")


def verify_model2_laurent() -> None:
    C = sp.expand(
        (1+y)**2 * (y**2 - 4*y + 1)**2 / y**3
    )
    R = sp.sympify(
        (MODEL2 / "laurent" / "certificate_R.txt").read_text(),
        locals={"n": n, "y": y},
    )
    P0 = sp.Rational(128, 3)*(n+1)*(2*n+1)*(2*n+3)*(3*n+5)
    P1 = -sp.Rational(8, 27)*(2*n+3)*(3*n+2)*(27*n**2+81*n+59)
    P2 = sp.Rational(1, 27)*(n+2)*(3*n+2)*(3*n+4)*(3*n+5)
    residual = sp.cancel(
        P0 + P1*C + P2*C**2
        - y*sp.diff(R, y)
        - n*y*sp.diff(C, y)*R/C
    )
    if sp.fraction(residual)[0] != 0:
        raise AssertionError("exact Laurent residual is nonzero")


def read_sparse_json(filename: str) -> SparseLaurent:
    raw = json.loads((NEW_CERT / filename).read_text())
    return {
        tuple(map(int, key.split(","))): sp.sympify(value, locals={"n": n})
        for key, value in raw.items()
    }


def verify_model5_laurent() -> None:
    G5 = sp.expand(390 + 320*(z+z**-1) + 125*(z**2+z**-2))
    Q5 = {
        int(key): sp.sympify(value, locals={"n": n})
        for key, value in FORMULAS["model5"]["Q"].items()
    }
    R5 = sp.sympify(
        (NEW_CERT / "model5_laurent_R.txt").read_text(),
        locals={"z": z, "n": n},
    )
    residual = sp.expand(
        G5*sum(Q5[shift]*G5**shift for shift in Q5)
        - G5*z*sp.diff(R5, z)
        - n*z*sp.diff(G5, z)*R5
    )
    if residual != 0:
        raise AssertionError("exact Laurent residual is nonzero")


def verify_model7_laurent() -> None:
    F7_expr = sp.sympify(
        FORMULAS["model7"]["P"],
        locals={"x": x, "y": y},
    )
    Q7 = {
        int(key): sp.sympify(value, locals={"n": n})
        for key, value in FORMULAS["model7"]["Q_scaled"].items()
    }
    Rx = read_sparse_json("model7_laurent_Rx.json")
    Ry = read_sparse_json("model7_laurent_Ry.json")
    F7 = sparse_expr(F7_expr, (x, y))
    powers = {0: {(0, 0): sp.Integer(1)}}
    for exponent in range(1, max(Q7) + 2):
        powers[exponent] = sparse_mul(powers[exponent-1], F7)
    left: SparseLaurent = {}
    for shift, coefficient in Q7.items():
        left = sparse_add(
            (left, 1),
            (sparse_scale(powers[shift+1], coefficient), 1),
        )
    right = sparse_add(
        (
            sparse_mul(
                F7,
                sparse_add(
                    (sparse_log_derivative(Rx, 0), 1),
                    (sparse_log_derivative(Ry, 1), 1),
                ),
            ),
            1,
        ),
        (
            sparse_add(
                (sparse_mul(sparse_log_derivative(F7, 0), Rx), n),
                (sparse_mul(sparse_log_derivative(F7, 1), Ry), n),
            ),
            1,
        ),
    )
    residual = sparse_add((left, 1), (right, -1))
    if any(sp.expand(value) != 0 for value in residual.values()):
        raise AssertionError("exact Laurent residual is nonzero")


def verify_laurent(index: int) -> None:
    if index in (1, 3, 9):
        verify_sparse_angular_laurent(index)
    elif index == 2:
        verify_model2_laurent()
    elif index == 5:
        verify_model5_laurent()
    elif index == 7:
        verify_model7_laurent()
    else:
        raise ValueError(f"model {index} is not complete")


def ode_recurrence(index: int) -> dict[int, sp.Expr]:
    ode = model(index)["ode_t"]
    A0 = sp.sympify(ode["0"], locals={"t": t})
    A1 = sp.sympify(ode["1"], locals={"t": t})
    A2 = sp.sympify(ode["2"], locals={"t": t})
    recurrence: dict[int, sp.Expr] = {}
    for (degree,), coefficient in sp.Poly(A2, t).terms():
        shift = 2 - degree
        recurrence[shift] = sp.expand(
            recurrence.get(shift, 0)
            + coefficient*(n-degree+2)*(n-degree+1)
        )
    for (degree,), coefficient in sp.Poly(A1, t).terms():
        shift = 1 - degree
        recurrence[shift] = sp.expand(
            recurrence.get(shift, 0)
            + coefficient*(n-degree+1)
        )
    for (degree,), coefficient in sp.Poly(A0, t).terms():
        shift = -degree
        recurrence[shift] = sp.expand(
            recurrence.get(shift, 0) + coefficient
        )
    return recurrence


def certificate_recurrence(index: int) -> tuple[dict[int, sp.Expr], str]:
    if index in (1, 3, 9):
        source = model(index)["certificate"]["angular_recurrence"]
        kind = "trinomial" if index in (1, 3) else "central"
    elif index == 5:
        source = FORMULAS["model5"]["Q"]
        kind = "central"
    elif index == 7:
        source = FORMULAS["model7"]["Q_scaled"]
        kind = "none"
    elif index == 2:
        return ({
            -1: 2592*(3*n-2)*(3*n+2),
            0: -12*(27*n**2+27*n+5),
            1: (n+1)**2,
        }, "full")
    else:
        raise ValueError(f"model {index} is not complete")
    return (
        {
            int(key): sp.sympify(value, locals={"n": n})
            for key, value in source.items()
        },
        kind,
    )


def binomial_ratio(kind: str, shift: int) -> sp.Expr:
    value = sp.Integer(1)
    for step in range(shift):
        k = n + step
        if kind == "central":
            value = sp.factor(value * 2*(2*k+1)/(k+1))
        elif kind == "trinomial":
            value = sp.factor(
                value * sp.Rational(3, 2)*(3*k+1)*(3*k+2)
                / ((k+1)*(2*k+1))
            )
        elif kind == "none":
            pass
        else:
            raise ValueError(f"unknown coefficient factor: {kind}")
    return value


def verify_annihilator(index: int) -> None:
    certificate, kind = certificate_recurrence(index)
    ode = ode_recurrence(index)
    if kind == "full":
        shifts = sorted(certificate)
        ratios = [
            sp.factor(certificate[shift] / ode[shift])
            for shift in shifts
        ]
    else:
        first_ode_shift = min(ode)
        shifts = sorted(certificate)
        transformed = {
            shift: sp.factor(
                certificate[shift] / binomial_ratio(kind, shift)
            )
            for shift in shifts
        }
        expected = {
            shift: sp.factor(
                ode[first_ode_shift + shift].subs(
                    n,
                    n - first_ode_shift,
                )
            )
            for shift in shifts
        }
        ratios = [
            sp.factor(transformed[shift] / expected[shift])
            for shift in shifts
        ]
    if any(sp.cancel(ratio - ratios[0]) != 0 for ratio in ratios[1:]):
        raise AssertionError("Laurent and period annihilators differ")


def verify_stored_recurrence(index: int) -> None:
    values = [
        sp.Integer(value)
        for value in model(index)[
            "first_31_coefficients_at_observed_scale"
        ]
    ]
    recurrence = ode_recurrence(index)
    low = min(recurrence)
    high = max(recurrence)
    for center in range(-low, len(values)-high):
        residual = sum(
            coefficient.subs(n, center) * values[center+shift]
            for shift, coefficient in recurrence.items()
        )
        if sp.expand(residual) != 0:
            raise AssertionError(f"stored recurrence failed at n={center}")


def laurent_expression(index: int) -> tuple[sp.Expr, tuple[sp.Symbol, ...]]:
    if index == 5:
        expression = sp.sympify(
            FORMULAS["model5"]["P"],
            locals={"w": w, "z": z},
        )
        return expression, (w, z)
    if index == 7:
        expression = sp.sympify(
            FORMULAS["model7"]["P"],
            locals={"x": x, "y": y},
        )
        return expression, (x, y)
    source = model(index)["laurent_model"]["F"]
    expression = sp.sympify(
        source,
        locals={"w": w, "x": x, "y": y, "I": sp.I},
    )
    symbols = tuple(
        symbol for symbol in (w, x, y)
        if expression.has(symbol)
    )
    return expression, symbols


def direct_coefficients(index: int, count: int) -> list[sp.Expr]:
    if index in (1, 3):
        angular = constant_terms(G[index], (x,), count)
        return [sp.binomial(3*k, 2*k)*angular[k] for k in range(count)]
    if index == 9:
        angular = constant_terms(G[index], (x,), count)
        return [sp.binomial(2*k, k)*angular[k] for k in range(count)]
    if index == 2:
        C = sp.expand((1+y)**2*(y**2-4*y+1)**2/y**3)
        angular = constant_terms(C, (y,), count)
        return [sp.binomial(3*k, 2*k)*angular[k] for k in range(count)]
    if index == 5:
        G5 = sp.expand(390 + 320*(z+z**-1) + 125*(z**2+z**-2))
        angular = constant_terms(G5, (z,), count)
        return [sp.binomial(2*k, k)*angular[k] for k in range(count)]
    if index == 7:
        expression, variables = laurent_expression(index)
        return constant_terms(expression, variables, count)
    raise ValueError(f"model {index} is not complete")


def verify_coefficients(index: int, count: int = 12) -> None:
    observed = direct_coefficients(index, count)
    expected = [
        sp.Integer(value)
        for value in model(index)[
            "first_31_coefficients_at_observed_scale"
        ][:count]
    ]
    if observed != expected:
        raise AssertionError(f"first {count} coefficients do not match")


STAGES: tuple[tuple[str, Callable[[int], None]], ...] = (
    ("Hamiltonian certificate", verify_hamiltonian),
    ("Laurent certificate", verify_laurent),
    ("annihilator comparison", verify_annihilator),
    ("recurrence check", verify_stored_recurrence),
    ("coefficient check", verify_coefficients),
)


@dataclass
class VerificationReport:
    requested: tuple[int, ...]
    passed_models: set[int] = field(default_factory=set)
    stage_counts: dict[str, int] = field(
        default_factory=lambda: {name: 0 for name, _ in STAGES}
    )


def print_summary(report: VerificationReport) -> None:
    total = len(report.requested)
    passed = len(report.passed_models)
    print()
    print(f"{passed}/{total} complete cases passed")
    print()
    labels = {
        "Hamiltonian certificate": "Hamiltonian certificates",
        "Laurent certificate": "Laurent certificates",
        "annihilator comparison": "Annihilator comparisons",
        "recurrence check": "Recurrence checks",
        "coefficient check": "Coefficient checks",
    }
    width = max(len(value) for value in labels.values())
    for stage, _ in STAGES:
        print(
            f"{labels[stage]+':':<{width+1}} "
            f"{report.stage_counts[stage]} passed"
        )


def run_verification(
    requested: tuple[int, ...],
    progress_enabled: bool = True,
) -> VerificationReport:
    unknown = sorted(set(requested) - set(COMPLETE_MODELS))
    if unknown:
        raise ValueError(f"not complete: {', '.join(map(str, unknown))}")
    report = VerificationReport(requested=requested)
    for index in requested:
        for stage, check in STAGES:
            progress(
                f"model {index}: {stage} started",
                enabled=progress_enabled,
            )
            try:
                check(index)
            except Exception as exc:
                progress(
                    f"model {index}: {stage} FAILED: {exc}",
                    enabled=progress_enabled,
                )
                print_summary(report)
                raise
            report.stage_counts[stage] += 1
            progress(
                f"model {index}: {stage} passed",
                enabled=progress_enabled,
            )
        report.passed_models.add(index)
    progress("all requested complete cases passed", enabled=progress_enabled)
    print_summary(report)
    return report


def parse_models(text: str) -> tuple[int, ...]:
    try:
        values = tuple(
            int(part.strip())
            for part in text.split(",")
            if part.strip()
        )
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "models must be comma-separated integers"
        ) from exc
    if not values:
        raise argparse.ArgumentTypeError("at least one model is required")
    if len(set(values)) != len(values):
        raise argparse.ArgumentTypeError("model numbers must not repeat")
    return values


def main(default_models: tuple[int, ...] = COMPLETE_MODELS) -> None:
    parser = argparse.ArgumentParser(
        description="Verify complete Hamiltonian and Laurent cases exactly."
    )
    parser.add_argument(
        "--models",
        type=parse_models,
        default=default_models,
        help="comma-separated complete model numbers",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress stage progress; retain the final summary",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="print the selected model numbers without running checks",
    )
    args = parser.parse_args()
    requested = tuple(args.models)
    if args.list_models:
        print(" ".join(map(str, requested)))
        return
    run_verification(requested, progress_enabled=not args.quiet)


if __name__ == "__main__":
    main()
