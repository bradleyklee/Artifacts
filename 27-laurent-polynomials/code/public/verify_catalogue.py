#!/usr/bin/env python3
"""Replay the public eleven-model catalogue and its four exact double certificates.

The script reads only examples/public/. It checks every stored ODE against all
available coefficients, verifies the four Hamiltonian divergence identities,
verifies the Laurent telescopers for models 1, 3, and 9, and runs the independent
A303790 Laurent replay for model 2. It uses explicit expansion and coefficient
comparison; it does not call a generic simplification routine.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "examples" / "public" / "catalogue"

p, q, E, n, x, t = sp.symbols("p q E n x t")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def parse_expr(text: str, symbols: dict[str, sp.Expr]) -> sp.Expr:
    value = sp.sympify(text, locals=symbols)
    forbidden = value.free_symbols - set(symbols.values())
    if forbidden:
        raise ValueError(f"forbidden symbols in expression: {forbidden}")
    return sp.expand(value)


def check_ode(sequence: list[sp.Integer], ode: dict[str, str]) -> int:
    operators = {
        int(order): sp.Poly(parse_expr(text, {"t": t}), t, domain=sp.QQ)
        for order, text in ode.items()
    }
    max_order = max(operators)
    checked = 0
    for power in range(0, len(sequence) - max_order):
        total = sp.S.Zero
        for order, polynomial in operators.items():
            for (shift,), coefficient in polynomial.terms():
                index = power - shift + order
                if index < order or index >= len(sequence):
                    continue
                falling = sp.factorial(index) / sp.factorial(index - order)
                total += coefficient * falling * sequence[index]
        if total != 0:
            raise AssertionError(f"ODE residual at t^{power}: {total}")
        checked += 1
    return checked


def check_hamiltonian_certificate(model: dict, data_root: Path) -> None:
    certificate = model["certificate"]
    H = parse_expr(model["hamiltonian_2H"], {"p": p, "q": q})
    operator = certificate["hamiltonian_operator_E"]
    A2 = parse_expr(operator["A2"], {"E": E})
    A1 = parse_expr(operator["A1"], {"E": E})
    A0 = parse_expr(operator["A0"], {"E": E})
    P = parse_expr(
        (data_root / certificate["hamiltonian_P_file"]).read_text(encoding="utf-8"),
        {"E": E, "alpha": E, "p": p, "q": q},
    )
    Q = parse_expr(
        (data_root / certificate["hamiltonian_Q_file"]).read_text(encoding="utf-8"),
        {"E": E, "alpha": E, "p": p, "q": q},
    )
    denominator = sp.expand(H - E)
    left = sp.expand(2 * A2 + A1 * denominator + A0 * denominator**2)
    right = sp.expand(
        denominator * (sp.diff(P, p) + sp.diff(Q, q))
        - 2 * (P * sp.diff(H, p) + Q * sp.diff(H, q))
    )
    residual = sp.Poly(sp.expand(right - left), p, q, E, domain=sp.QQ)
    if not residual.is_zero:
        raise AssertionError(f"model {model['index']}: Hamiltonian certificate residual is nonzero")


def laurent_dict(expression: sp.Expr, variable: sp.Symbol) -> dict[int, sp.Expr]:
    """Return an exact exponent dictionary without expanding large products."""
    result: dict[int, sp.Expr] = {}
    for term in sp.Add.make_args(expression):
        exponent_value = term.as_powers_dict().get(variable, sp.S.Zero)
        if not exponent_value.is_Integer:
            raise ValueError(f"nonintegral Laurent exponent: {exponent_value}")
        exponent = int(exponent_value)
        coefficient = term / variable**exponent
        if variable in coefficient.free_symbols:
            raise ValueError("failed to separate Laurent variable")
        result[exponent] = result.get(exponent, sp.S.Zero) + coefficient
    return {key: sp.expand(value) for key, value in result.items() if value != 0}


def laurent_add(*values: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for value in values:
        for exponent, coefficient in value.items():
            result[exponent] = result.get(exponent, sp.S.Zero) + coefficient
    return {key: sp.expand(value) for key, value in result.items() if value != 0}


def laurent_scale(value: dict[int, sp.Expr], scalar: sp.Expr) -> dict[int, sp.Expr]:
    return {exponent: sp.expand(scalar * coefficient) for exponent, coefficient in value.items()}


def laurent_mul(left: dict[int, sp.Expr], right: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = left_exponent + right_exponent
            result[exponent] = result.get(exponent, sp.S.Zero) + left_coefficient * right_coefficient
    return {key: sp.expand(value) for key, value in result.items() if value != 0}


def laurent_pow(value: dict[int, sp.Expr], power: int) -> dict[int, sp.Expr]:
    result = {0: sp.S.One}
    for _ in range(power):
        result = laurent_mul(result, value)
    return result


def laurent_x_derivative(value: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    return {
        exponent: sp.expand(exponent * coefficient)
        for exponent, coefficient in value.items()
        if exponent != 0
    }


def check_laurent_certificate(model: dict, data_root: Path) -> None:
    certificate = model["certificate"]
    laurent = model["laurent_model"]
    G_expr = sp.sympify(laurent["factor_G"], locals={"x": x, "I": sp.I})
    R_expr = sp.sympify(
        (data_root / certificate["laurent_R_file"]).read_text(encoding="utf-8"),
        locals={"n": n, "x": x, "I": sp.I},
    )
    G = laurent_dict(G_expr, x)
    R = laurent_dict(R_expr, x)
    recurrence = {
        int(shift): parse_expr(text, {"n": n})
        for shift, text in certificate["angular_recurrence"].items()
    }
    lhs: dict[int, sp.Expr] = {}
    for shift, coefficient in recurrence.items():
        lhs = laurent_add(lhs, laurent_scale(laurent_pow(G, shift), coefficient))
    residual = laurent_add(
        laurent_mul(G, lhs),
        laurent_scale(laurent_mul(G, laurent_x_derivative(R)), -1),
        laurent_scale(laurent_mul(laurent_x_derivative(G), R), -n),
    )
    for exponent, coefficient in residual.items():
        polynomial = sp.Poly(sp.expand(coefficient), n, extension=sp.I)
        if not polynomial.is_zero:
            raise AssertionError(
                f"model {model['index']}: Laurent residual at x^{exponent} is nonzero"
            )


def run_a303790_laurent_replay() -> list[str]:
    scripts = [
        PROJECT_ROOT / "code" / "a303790" / "verify_scalar_certificate.py",
        PROJECT_ROOT / "code" / "a303790" / "derive_and_verify_laurent.py",
    ]
    output: list[str] = []
    for script in scripts:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output.extend(line for line in completed.stdout.splitlines() if line.strip())
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root.is_absolute():
        data_root = PROJECT_ROOT / data_root
    report_path = args.report or (data_root / "VERIFICATION_REPORT.json")
    if not report_path.is_absolute():
        report_path = PROJECT_ROOT / report_path

    dataset = read_json(data_root / "models.json")
    models = dataset["models"]
    results = []
    complete_indices = {1, 2, 3, 9}

    for position, model in enumerate(models, start=1):
        index = int(model["index"])
        print(f"[{position}/{len(models)}] public model {index}", flush=True)
        sequence = [sp.Integer(value) for value in model["first_31_coefficients_at_observed_scale"]]
        if any(not value.is_Integer for value in sequence):
            raise AssertionError(f"model {index}: nonintegral stored coefficient")
        ode_checks = check_ode(sequence, model["ode_t"])
        entry = {
            "index": index,
            "fibres": model["fibres"],
            "coefficient_count": len(sequence),
            "ode_coefficients_checked": ode_checks,
            "laurent_status": "complete" if model.get("laurent_model") else "open",
            "hamiltonian_certificate": False,
            "laurent_certificate": False,
        }
        if index in complete_indices:
            check_hamiltonian_certificate(model, data_root)
            entry["hamiltonian_certificate"] = True
            if index in {1, 3, 9}:
                check_laurent_certificate(model, data_root)
                entry["laurent_certificate"] = True
        results.append(entry)
        print(f"[{position}/{len(models)}] PASS model {index}", flush=True)

    a303790_output = run_a303790_laurent_replay()
    for entry in results:
        if entry["index"] == 2:
            entry["laurent_certificate"] = True
            entry["a303790_replay"] = a303790_output
            break

    report = {
        "schema": "laurent-public-catalogue-verification-v1",
        "model_count": len(models),
        "complete_double_certificate_count": sum(
            1 for item in results
            if item["hamiltonian_certificate"] and item["laurent_certificate"]
        ),
        "models": results,
    }
    write_json(report_path, report)
    print(f"PASS: {len(models)}/11 public period records", flush=True)
    print("PASS: 4/4 complete double certificates", flush=True)
    print(f"report: {report_path}", flush=True)


if __name__ == "__main__":
    main()
