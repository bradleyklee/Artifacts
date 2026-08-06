#!/usr/bin/env python3
"""Regenerate, validate, and compare every publication reference certificate.

Each model is derived in a fresh Python subprocess.  This releases exact-linear-
algebra memory between models and prevents one difficult solve from contaminating
the timing or state of the next model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp

THETA = sp.Symbol("theta")
T = sp.Symbol("t")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_sparse_record(name: str, record: dict, *, vector: bool) -> None:
    """Check dimensions, uniqueness, ordering, and declared nonzero count."""
    rows, columns = record["shape"]
    entries = record["entries"]
    if record["nonzero_count"] != len(entries):
        raise AssertionError(f"{name}: nonzero_count does not match entries")
    if vector:
        if columns != 1 or len(record["labels"]) != rows:
            raise AssertionError(f"{name}: vector dimensions or labels are inconsistent")
        coordinates = [entry[0] for entry in entries]
        if any(not 0 <= index < rows for index in coordinates):
            raise AssertionError(f"{name}: vector index outside declared shape")
    else:
        if len(record["rows"]) != rows or len(record["columns"]) != columns:
            raise AssertionError(f"{name}: matrix labels do not match shape")
        coordinates = [(entry[0], entry[1]) for entry in entries]
        if any(not (0 <= i < rows and 0 <= j < columns) for i, j in coordinates):
            raise AssertionError(f"{name}: matrix coordinate outside declared shape")
    if coordinates != sorted(coordinates):
        raise AssertionError(f"{name}: sparse entries are not in canonical order")
    if len(coordinates) != len(set(coordinates)):
        raise AssertionError(f"{name}: duplicate sparse coordinates")


def validate_certificate(certificate: dict, schema: dict) -> None:
    jsonschema.Draft202012Validator(schema).validate(certificate)
    assert_sparse_record("G", certificate["matrices"]["G"], vector=False)
    assert_sparse_record("J", certificate["matrices"]["J"], vector=False)
    for key in ("U", "Vx", "Vy"):
        assert_sparse_record(key, certificate["reduction"][key], vector=True)
    for key in ("Xi_x", "Xi_y"):
        assert_sparse_record(key, certificate["certificate_Xi"][key], vector=True)


def compare_reference(model: dict, certificate: dict, term_count: int) -> None:
    got = sp.Poly(
        sp.expand(sp.sympify(certificate["annihilator_A"]["theta_form"], locals={"t": T, "theta": THETA})),
        T,
        THETA,
        domain=sp.QQ,
    )
    expected = sp.Poly(
        sp.expand(sp.sympify(model["expected_theta_operator"], locals={"t": T, "theta": THETA})),
        T,
        THETA,
        domain=sp.QQ,
    )
    if got != expected:
        raise AssertionError(f"operator mismatch for {model['model']}: {got.as_expr()} != {expected.as_expr()}")
    wanted_terms = [str(value) for value in model["expected_terms"][:term_count]]
    if certificate["constant_terms"][: len(wanted_terms)] != wanted_terms:
        raise AssertionError(f"constant-term mismatch for {model['model']}")


def derive_one(
    root: Path,
    model: dict,
    output_path: Path,
    term_count: int,
    direct_check_count: int,
    timeout: float,
) -> dict:
    command = [
        sys.executable,
        str(root / "guvj_period_factory.py"),
        "--model",
        model["model"],
        "--F",
        model["F"],
        "--terms",
        str(term_count),
        "--direct-check-count",
        str(direct_check_count),
        "--output",
        str(output_path),
    ]
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    result = subprocess.run(
        command,
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=None,
        timeout=timeout,
        env=environment,
    )
    summary = json.loads(result.stdout)
    if not all(summary["checks"].values()):
        raise AssertionError(f"reported check failure for {model['model']}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", type=Path, required=True)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--terms", type=int, default=12)
    parser.add_argument("--direct-check-count", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    project_root = Path(__file__).resolve().parents[2]
    models_path = args.models
    schema_path = args.schema or root / "certificate_schema.json"
    output_dir = args.output_dir
    if not models_path.is_absolute():
        models_path = project_root / models_path
    if not schema_path.is_absolute():
        schema_path = project_root / schema_path
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    models = read_json(models_path)["models"]
    schema = read_json(schema_path)
    report_models = []
    started = time.perf_counter()

    for index, model in enumerate(models, start=1):
        name = model["model"]
        output_path = output_dir / f"{name}.json"
        print(f"[model {index}/{len(models)}] {name}", flush=True)
        model_started = time.perf_counter()
        summary = derive_one(
            root,
            model,
            output_path,
            args.terms,
            args.direct_check_count,
            args.timeout,
        )
        certificate = read_json(output_path)
        validate_certificate(certificate, schema)
        compare_reference(model, certificate, args.terms)
        elapsed = time.perf_counter() - model_started
        entry = {
            "model": name,
            "seconds": elapsed,
            "certificate": str(output_path.relative_to(project_root)),
            "sha256": sha256_file(output_path),
            "G_shape": certificate["matrices"]["G"]["shape"],
            "G_nonzero_count": certificate["matrices"]["G"]["nonzero_count"],
            "checks": certificate["checks"],
            "summary": summary,
        }
        report_models.append(entry)
        print(f"[model {index}/{len(models)}] PASS in {elapsed:.3f} s", flush=True)

    total = time.perf_counter() - started
    report = {
        "schema": "laurent-period-guvj-verification-report-v1",
        "python": sys.version.split()[0],
        "sympy": sp.__version__,
        "terms": args.terms,
        "direct_check_count": min(args.direct_check_count, args.terms),
        "total_seconds": total,
        "models": report_models,
    }
    report_path = args.report or (output_dir.parent / "VERIFICATION_REPORT.json")
    if not report_path.is_absolute():
        report_path = project_root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(report_path, report)
    print(f"[all] PASS: {len(models)} models in {total:.3f} s", flush=True)
    print(f"[all] report: {report_path}", flush=True)


if __name__ == "__main__":
    main()
