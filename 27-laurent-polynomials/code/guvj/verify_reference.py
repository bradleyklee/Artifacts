#!/usr/bin/env python3
"""Replay and validate the stored publication certificates without re-solving.

This script reconstructs every sparse object, rebuilds G and J from the stated
Laurent polynomial, replays the reduction and Xi identities coefficient by
coefficient, regenerates the reference terms independently, and compares the
published operators and terms with models.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp

from guvj_period_factory import (
    assert_zero_matrix,
    build_matrices,
    cancel_rational,
    constant_terms,
    constant_terms_by_direct_expansion,
    derive_operator,
    expression_vector,
    parse_laurent,
    laurent_terms,
    x,
    y,
    rational_is_zero,
    recurrence_holds,
    t,
    theta,
    n,
    theta_recurrence,
    vector_expression,
)

CODE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_qt(text: str) -> sp.Expr:
    value = sp.sympify(text, locals={"t": t, "theta": theta})
    forbidden = value.free_symbols - {t, theta}
    if forbidden:
        raise ValueError(f"forbidden symbols in stored expression: {forbidden}")
    return cancel_rational(value)




def parse_qn(text: str) -> sp.Expr:
    value = sp.sympify(text, locals={"n": n})
    forbidden = value.free_symbols - {n}
    if forbidden:
        raise ValueError(f"forbidden symbols in stored recurrence: {forbidden}")
    return sp.expand(value)

def parse_qxyt(text: str) -> sp.Expr:
    value = sp.sympify(text, locals={"x": x, "y": y, "t": t})
    forbidden = value.free_symbols - {x, y, t}
    if forbidden:
        raise ValueError(f"forbidden symbols in stored Laurent expression: {forbidden}")
    return sp.expand(value)


def assert_laurent_zero(name: str, expression: sp.Expr) -> None:
    numerator, _ = sp.fraction(sp.cancel(expression))
    polynomial = sp.Poly(sp.expand(numerator), x, y, t, domain=sp.QQ)
    if not polynomial.is_zero:
        raise AssertionError(f"{name}: nonzero rational Laurent expression")

def sparse_matrix(record: dict) -> sp.SparseMatrix:
    rows, columns = record["shape"]
    data = {(i, j): parse_qt(value) for i, j, value in record["entries"]}
    return sp.SparseMatrix(rows, columns, data)


def sparse_vector(record: dict) -> sp.SparseMatrix:
    rows, columns = record["shape"]
    if columns != 1:
        raise AssertionError("stored vector does not have one column")
    data = {(i, 0): parse_qt(value) for i, value in record["entries"]}
    return sp.SparseMatrix(rows, 1, data)


def assert_sparse_record(name: str, record: dict, *, vector: bool) -> None:
    rows, columns = record["shape"]
    entries = record["entries"]
    if record["nonzero_count"] != len(entries):
        raise AssertionError(f"{name}: nonzero_count mismatch")
    if vector:
        if columns != 1 or len(record["labels"]) != rows:
            raise AssertionError(f"{name}: vector shape/labels mismatch")
        coordinates = [entry[0] for entry in entries]
        if any(not 0 <= index < rows for index in coordinates):
            raise AssertionError(f"{name}: vector coordinate out of range")
    else:
        if len(record["rows"]) != rows or len(record["columns"]) != columns:
            raise AssertionError(f"{name}: matrix shape/labels mismatch")
        coordinates = [(entry[0], entry[1]) for entry in entries]
        if any(not (0 <= i < rows and 0 <= j < columns) for i, j in coordinates):
            raise AssertionError(f"{name}: matrix coordinate out of range")
    if coordinates != sorted(coordinates):
        raise AssertionError(f"{name}: sparse coordinates are not sorted")
    if len(coordinates) != len(set(coordinates)):
        raise AssertionError(f"{name}: duplicate sparse coordinates")


def assert_same_expr(name: str, left: sp.Expr, right: sp.Expr) -> None:
    if not rational_is_zero(left - right):
        raise AssertionError(f"{name}: expressions differ")


def assert_same_vector(name: str, left: sp.MatrixBase, right: sp.MatrixBase) -> None:
    assert_zero_matrix(name, left - right)


def replay_one(model: dict, certificate: dict, schema: dict, data_root: Path) -> dict:
    jsonschema.Draft202012Validator(schema).validate(certificate)
    assert_sparse_record("G", certificate["matrices"]["G"], vector=False)
    assert_sparse_record("J", certificate["matrices"]["J"], vector=False)
    for key in ("U", "Vx", "Vy"):
        assert_sparse_record(key, certificate["reduction"][key], vector=True)
    for key in ("Xi_x", "Xi_y"):
        assert_sparse_record(key, certificate["certificate_Xi"][key], vector=True)

    F = parse_laurent(certificate["input"]["F"])
    expected_F = parse_laurent(model["F"])
    assert_laurent_zero("input F", F - expected_F)
    rho = sp.expand(1 - t * F)
    assert_laurent_zero("stored rho", parse_qxyt(certificate["input"]["rho"]) - rho)

    dilation = int(certificate["input"]["dilation"])
    basis, ambient, G, E, J, RHO = build_matrices(F, dilation)
    if certificate["basis"]["B"] != [[i, j] for i, j in basis]:
        raise AssertionError("stored B basis differs from rebuilt basis")
    if certificate["basis"]["C"] != [[i, j] for i, j in ambient]:
        raise AssertionError("stored C basis differs from rebuilt basis")
    assert_same_vector("stored G", sparse_matrix(certificate["matrices"]["G"]), G)
    assert_same_vector("stored J", sparse_matrix(certificate["matrices"]["J"]), J)

    U = sparse_vector(certificate["reduction"]["U"])
    Vx = sparse_vector(certificate["reduction"]["Vx"])
    Vy = sparse_vector(certificate["reduction"]["Vy"])
    V = sp.SparseMatrix.vstack(Vx, Vy)
    alpha = parse_qt(certificate["reduction"]["alpha"])
    beta = parse_qt(certificate["reduction"]["beta"])
    F_vector = expression_vector(F, basis)
    F2_vector = expression_vector(sp.expand(F**2), basis)
    rho_vector = expression_vector(rho, basis)

    assert_same_vector("G[U;V]-E*F^2", G * sp.Matrix.vstack(U, V), E * F2_vector)
    lower2 = U - J * V / 2
    assert_same_vector("Lower_2 closure", lower2, alpha * rho_vector + beta * F_vector)
    assert_laurent_zero(
        "stored Lower2 expression",
        parse_qxyt(certificate["reduction"]["Lower2_expression"])
        - vector_expression(lower2, basis),
    )

    X, p0, p1, p2, A_theta = derive_operator(alpha, beta)
    stored_X = sp.Matrix([[parse_qt(value) for value in row] for row in certificate["reduced_columns_X"]])
    assert_same_vector("stored reduced-column matrix X", stored_X, X)
    standard = certificate["annihilator_A"]["standard_form"]
    for name, got in (("p0", p0), ("p1", p1), ("p2", p2)):
        assert_same_expr(name, parse_qt(standard[name]), got)
    assert_same_expr("theta operator", parse_qt(certificate["annihilator_A"]["theta_form"]), A_theta)
    assert_same_expr("expected theta operator", A_theta, parse_qt(model["expected_theta_operator"]))

    Xi_x = sparse_vector(certificate["certificate_Xi"]["Xi_x"])
    Xi_y = sparse_vector(certificate["certificate_Xi"]["Xi_y"])
    Xi = sp.SparseMatrix.vstack(Xi_x, Xi_y)
    assert_same_vector("Xi=p2*V", Xi, p2 * V)
    Bblock = G[:, len(basis) : 3 * len(basis)]
    left_source = sp.expand(p0 * rho**2 + p1 * F * rho + 2 * p2 * F**2)
    left = E * expression_vector(left_source, basis)
    right = RHO * J * Xi + 2 * Bblock * Xi
    assert_same_vector("exact Xi identity", left, right)

    term_count = int(certificate["input"]["term_count"])
    direct_count = int(certificate["input"]["direct_check_count"])
    terms = constant_terms(F, term_count)
    stored_terms = [sp.Integer(value) for value in certificate["constant_terms"]]
    if terms != stored_terms:
        raise AssertionError("stored constant terms differ from lattice convolution")
    if constant_terms_by_direct_expansion(F, direct_count) != terms[:direct_count]:
        raise AssertionError("direct-power terms differ from lattice convolution")
    wanted = [sp.Integer(value) for value in model["expected_terms"][:term_count]]
    if terms[: len(wanted)] != wanted:
        raise AssertionError("constant terms differ from models.json")

    recurrence = theta_recurrence(A_theta)
    stored_recurrence = {
        int(key): parse_qn(value)
        for key, value in certificate["recurrence"]["shift_polynomials"].items()
    }
    if set(recurrence) != set(stored_recurrence):
        raise AssertionError("stored recurrence shifts differ")
    for key in recurrence:
        difference = sp.Poly(sp.expand(recurrence[key] - stored_recurrence[key]), n, domain=sp.QQ)
        if not difference.is_zero:
            raise AssertionError(f"recurrence shift {key}: expressions differ")
    if not recurrence_holds(recurrence, terms):
        raise AssertionError("recurrence fails on stored terms")
    if not all(certificate["checks"].values()):
        raise AssertionError("stored check field contains false")

    return {
        "model": model["model"],
        "sha256": sha256_file(data_root / "reference" / f"{model['model']}.json"),
        "G_shape": [G.rows, G.cols],
        "G_nonzero_count": certificate["matrices"]["G"]["nonzero_count"],
        "terms": term_count,
        "direct_powers": direct_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", action="append", default=[],
        help="replay only this model; may be repeated",
    )
    parser.add_argument(
        "--data-root", type=Path, required=True,
        help="dataset directory containing models.json and reference/",
    )
    parser.add_argument(
        "--report", type=Path,
        help="JSON report path; defaults to DATA_ROOT/REPLAY_REPORT.json",
    )
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root.is_absolute():
        data_root = PROJECT_ROOT / data_root
    report_path = args.report or (data_root / "REPLAY_REPORT.json")
    if not report_path.is_absolute():
        report_path = PROJECT_ROOT / report_path

    schema = read_json(CODE_ROOT / "certificate_schema.json")
    models = read_json(data_root / "models.json")["models"]
    if args.model:
        requested = set(args.model)
        known = {model["model"] for model in models}
        missing = sorted(requested - known)
        if missing:
            raise SystemExit(f"unknown model names: {', '.join(missing)}")
        models = [model for model in models if model["model"] in requested]
    report = []
    for index, model in enumerate(models, 1):
        path = data_root / "reference" / f"{model['model']}.json"
        print(f"[{index}/{len(models)}] replay {model['model']} ...", flush=True)
        report.append(replay_one(model, read_json(path), schema, data_root))
        print(f"[{index}/{len(models)}] PASS {model['model']}", flush=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({
        "schema": "laurent-period-guvj-replay-report-v1",
        "data_root": str(data_root.relative_to(PROJECT_ROOT)),
        "models": report,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(report)}/{len(models)} publication certificates", flush=True)
    print(f"report: {report_path}", flush=True)


if __name__ == "__main__":
    main()
