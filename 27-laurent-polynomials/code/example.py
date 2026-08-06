#!/usr/bin/env python3
"""One command-line entry point for Laurent-period examples and certificates."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUVJ_ROOT = PROJECT_ROOT / "code" / "guvj"
sys.path.insert(0, str(GUVJ_ROOT))

from all_orders_solver import derive, parse_laurent  # noqa: E402

PUBLIC_MODELS = (
    PROJECT_ROOT / "examples" / "public" / "catalogue" / "models.json"
)
PRIVATE_MODELS = (
    PROJECT_ROOT / "examples" / "private" / "platonic" / "models.json"
)
A295870_DATA = (
    PROJECT_ROOT / "examples" / "public" / "A295870" / "model_data.json"
)

WIDTH = 80


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def baseline(scope: str) -> None:
    if scope in {"public", "all"}:
        run([sys.executable, "code/run_examples.py", "public"])
    if scope in {"private", "all"}:
        if not PRIVATE_MODELS.exists():
            raise SystemExit("private data root is not present")
        run([
            sys.executable,
            "code/run_examples.py",
            "private",
            "--data-root",
            "examples/private/platonic",
        ])


def load_models() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    public = json.loads(PUBLIC_MODELS.read_text(encoding="utf-8"))
    public_by_index = {model["index"]: model for model in public["models"]}

    if A295870_DATA.exists():
        model = json.loads(A295870_DATA.read_text(encoding="utf-8"))
        result.append({
            "id": "A295870",
            "F": model["laurent_polynomial"],
            "visibility": "public",
            "description": "OEIS A295870 primary public example",
        })

    a303790 = public_by_index[2]
    result.append({
        "id": "A303790",
        "F": a303790["laurent_model"]["F"],
        "visibility": "public",
        "description": "OEIS A303790 primary public example",
    })

    for model in public["models"]:
        laurent = model.get("laurent_model")
        if laurent:
            result.append({
                "id": f"public:{model['index']}",
                "F": laurent["F"],
                "visibility": "public",
                "description": "public catalogue Laurent model",
            })

    if PRIVATE_MODELS.exists():
        private = json.loads(PRIVATE_MODELS.read_text(encoding="utf-8"))
        for model in private["models"]:
            result.append({
                "id": f"private:{model['model']}",
                "F": model["F"],
                "visibility": "private",
                "description": "private canonical model",
            })

    result.extend([
        {
            "id": "regression:line",
            "F": "x + 1/x",
            "visibility": "public",
            "description": "small regression",
        },
        {
            "id": "regression:square",
            "F": "x + 1/x + y + 1/y",
            "visibility": "public",
            "description": "small regression",
        },
        {
            "id": "regression:triangle",
            "F": "x + y + 1/(x*y)",
            "visibility": "public",
            "description": "small regression",
        },
        {
            "id": "regression:order3_triangle",
            "F": "x + y + 1/(x*y) + y**2/x",
            "visibility": "public",
            "description": "order-three regression",
        },
        {
            "id": "regression:order4_triangle",
            "F": "x + y + 1/(x*y) + y**2",
            "visibility": "public",
            "description": "order-four regression",
        },
    ])
    return result


def model_by_id(identifier: str) -> dict[str, Any]:
    for model in load_models():
        if model["id"] == identifier:
            return model
    raise SystemExit(f"unknown model id: {identifier}")


def json_ready(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def wrapped(label: str, value: Any, indent: int = 2) -> None:
    prefix = " " * indent + f"{label}: "
    width = max(20, WIDTH - len(prefix))
    lines = textwrap.wrap(
        str(value),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    print(prefix + lines[0])
    continuation = " " * len(prefix)
    for line in lines[1:]:
        print(continuation + line)




def operator_lines(operator: Any) -> list[str]:
    """Format an operator by powers of t with factored theta coefficients."""
    expression = sp.expand(sp.sympify(operator))
    polynomial = sp.Poly(expression, sp.Symbol("t"))
    variable = sp.Symbol("t")
    lines: list[str] = []
    for power in range(polynomial.degree() + 1):
        coefficient = sp.factor(polynomial.coeff_monomial(variable**power))
        if coefficient == 0:
            continue
        negative = coefficient.could_extract_minus_sign()
        body = -coefficient if negative else coefficient
        body_text = str(body)
        if power == 0:
            term_text = body_text
        else:
            t_text = "t" if power == 1 else f"t**{power}"
            numeric, remainder = body.as_coeff_Mul()
            factors: list[str] = []
            if numeric != 1:
                factors.append(str(numeric))
            factors.append(t_text)
            if remainder != 1:
                remainder_text = str(remainder)
                if isinstance(remainder, sp.Add):
                    remainder_text = f"({remainder_text})"
                factors.append(remainder_text)
            term_text = "*".join(factors)
        if not lines:
            lines.append(("- " if negative else "") + term_text)
        else:
            lines.append(("- " if negative else "+ ") + term_text)
    return lines or ["0"]


def print_operator(operator: Any) -> None:
    print("  operator:")
    for line in operator_lines(operator):
        pieces = textwrap.wrap(
            line,
            width=WIDTH - 4,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        for piece in pieces:
            print("    " + piece)

def print_certificate_summary(record: dict[str, Any], output: Path) -> None:
    stats = record["operator_stats"]
    certificate = record["certificate"]
    print("Certificate complete")
    print_operator(record["operator"])
    wrapped("order", stats["order"])
    wrapped("shift degree", stats["shift_degree"])
    if "dilation" in certificate:
        wrapped("dilation", certificate["dilation"])
    wrapped("matrix", " x ".join(map(str, certificate["matrix_shape"])))
    wrapped(
        "coefficient domain",
        certificate.get("coefficient_domain", "unknown"),
    )
    wrapped("linear solver", certificate.get("linear_solver", "unknown"))
    wrapped("output", output)
    print("  checks:")
    method_flags = {
        "operator_from_joint_exact_identity",
        "operator_from_finite_term_fit",
    }
    for name, passed in record["checks"].items():
        if name in method_flags:
            value = "used" if passed else "not used"
        else:
            value = "PASS" if passed else "FAIL"
        wrapped(name.replace("_", " "), value, indent=4)


def command_list(args: argparse.Namespace) -> None:
    for model in load_models():
        if args.scope != "all" and model["visibility"] != args.scope:
            continue
        text = f"{model['id']:<30} {model['visibility']:<7} "
        description = model.get("description", "")
        print(text + description)


def command_show(args: argparse.Namespace) -> None:
    model = model_by_id(args.model)
    print(model["F"])


def derive_record(
    expression: sp.Expr,
    *,
    max_order: int | None,
    max_shift: int | None,
    max_dilation: int | None,
    quiet: bool,
) -> dict[str, Any]:
    return derive(
        expression,
        max_order=max_order,
        max_shift_degree=max_shift,
        max_dilation=max_dilation,
        progress_enabled=not quiet,
    )


def write_record(record: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(json_ready(record), indent=2) + "\n",
        encoding="utf-8",
    )


def command_derive(args: argparse.Namespace) -> None:
    if bool(args.F) == bool(args.model):
        raise SystemExit("choose exactly one of --F or --model")
    expression = (
        parse_laurent(args.F)
        if args.F
        else parse_laurent(model_by_id(args.model)["F"])
    )
    record = derive_record(
        expression,
        max_order=args.max_order,
        max_shift=args.max_shift,
        max_dilation=args.max_dilation,
        quiet=args.quiet,
    )
    write_record(record, args.output)
    print_certificate_summary(record, args.output)


def command_certify(args: argparse.Namespace) -> None:
    model = model_by_id(args.name)
    output = args.output or Path(f"certificate-{args.name}.json")
    record = derive_record(
        parse_laurent(model["F"]),
        max_order=args.max_order,
        max_shift=args.max_shift,
        max_dilation=args.max_dilation,
        quiet=args.quiet,
    )
    write_record(record, output)
    print_certificate_summary(record, output)


def add_solver_controls(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-order", type=int)
    parser.add_argument("--max-shift", type=int)
    parser.add_argument("--max-dilation", type=int)
    parser.add_argument("--quiet", action="store_true")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("scope", choices=("public", "private", "all"))
    baseline_parser.set_defaults(function=lambda args: baseline(args.scope))

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument(
        "--scope", choices=("public", "private", "all"), default="all"
    )
    list_parser.set_defaults(function=command_list)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("model")
    show_parser.set_defaults(function=command_show)

    derive_parser = subparsers.add_parser("derive")
    derive_parser.add_argument("--F")
    derive_parser.add_argument("--model")
    add_solver_controls(derive_parser)
    derive_parser.add_argument(
        "--output", type=Path, default=Path("certificate-v2.json")
    )
    derive_parser.set_defaults(function=command_derive)

    certify_parser = subparsers.add_parser(
        "certify", help="recompute a named public certificate"
    )
    certify_parser.add_argument("name", choices=("A295870", "A303790"))
    add_solver_controls(certify_parser)
    certify_parser.add_argument("--output", type=Path)
    certify_parser.set_defaults(function=command_certify)

    args = parser.parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
