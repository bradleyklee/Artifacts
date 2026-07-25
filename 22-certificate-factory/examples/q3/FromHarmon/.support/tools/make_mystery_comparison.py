#!/usr/bin/env python3
"""Create aligned, shallow dependency trees for the q=3 pseudocode and code."""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import re
from collections import OrderedDict
from pathlib import Path

import cairosvg

FUNCTION_RE = re.compile(r"^\s*Function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)")
CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
LINE_RE = re.compile(r"^\s*\d+\s*:\s*(.*)$")
OF_OPERATOR_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s+of\b")
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
CONTROL_WORDS = {"Assert", "Else", "For", "Function", "If", "Require", "Return", "Write"}

LOCAL_MAP = OrderedDict([
    ("Lower", "lower"),
    ("Normalize3", "normalize3"),
    ("Cancel3", "cancel3"),
    ("Apply2", "apply2"),
    ("MakeODE", "make_ode"),
    ("Q3", "run_q3"),
])

# Human-facing labels and source evidence.  Every named pseudocode operation
# appears exactly once in the tree and is resolved by the q=3 implementation.
RESOLUTIONS = OrderedDict([
    ("LCM", ("lcm_expr / sp.lcm", ("def lcm_expr", "sp.lcm"))),
    ("Denom", ("fraction denominator", ("sp.fraction", "[1]"))),
    ("Together", ("sp.together", ("sp.together",))),
    ("Expand", ("sp.expand", ("sp.expand",))),
    ("PolynomialGCD", ("sp.gcd", ("sp.gcd",))),
    ("GCD", ("math.gcd", ("math.gcd",))),
    ("LeadingCoefficient", ("Poly.LC", (".LC()",))),
    ("Factor", ("sp.factor", ("sp.factor",))),
    ("Collect", ("coefficients of A'', A', A", (".coeff(App)", ".coeff(Ap)", ".coeff(A)"))),
    ("MatrixFromColumns", ("Matrix.hstack", ("sp.Matrix.hstack",))),
    ("Simplify", ("sp.simplify", ("sp.simplify",))),
    ("ExactQuotient", ("exact_integer_quotient", ("def exact_integer_quotient",))),
    ("Sum", ("Python sum", ("S = sum(",))),
    ("Coeffs", ("Poly.nth", (".nth(k)",))),
    ("Substitute", ("ODE residual at A=S", ("ode[0] * sp.diff(S, x, 2)", "ode[1] * sp.diff(S, x)", "ode[2] * S"))),
])

GROUPS = [
    ("reduction", [
        ("defined", "Lower", "lower"),
        ("mystery", "MatrixFromColumns", "Matrix.hstack"),
        ("mystery", "Simplify", "sp.simplify"),
        ("mystery", "ExactQuotient", "exact_integer_quotient"),
    ]),
    ("recurrence normalization", [
        ("defined", "Cancel3 → Normalize3", "cancel3 → normalize3"),
        ("mystery", "LCM", "lcm_expr / sp.lcm"),
        ("mystery", "Denom", "fraction denominator"),
        ("mystery", "Together", "sp.together"),
        ("mystery", "Expand", "sp.expand"),
        ("mystery", "PolynomialGCD", "sp.gcd"),
        ("mystery", "GCD", "math.gcd"),
        ("mystery", "LeadingCoefficient", "Poly.LC"),
        ("mystery", "Factor", "sp.factor"),
    ]),
    ("coefficient checks", [
        ("mystery", "Sum", "Python sum"),
        ("mystery", "Coeffs", "Poly.nth"),
    ]),
    ("differential equation", [
        ("defined", "MakeODE → Apply2", "make_ode → apply2"),
        ("mystery", "Collect", "coefficients of A'', A', A"),
        ("mystery", "Substitute", "ODE residual at A=S"),
    ]),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def body(line: str) -> str | None:
    match = LINE_RE.match(line)
    if not match:
        return None
    return re.split(r"\s{2,}\(", match.group(1), maxsplit=1)[0].strip()


def extract_defined_and_mysteries(text: str) -> tuple[list[str], list[str]]:
    blocks: list[tuple[str, tuple[str, ...], list[str]]] = []
    name: str | None = None
    params: tuple[str, ...] = ()
    lines: list[str] = []
    for line in text.splitlines():
        match = FUNCTION_RE.match(line)
        if match:
            if name is not None:
                blocks.append((name, params, lines))
            name = match.group(1)
            params = tuple(x.strip() for x in match.group(2).split(",") if x.strip())
            lines = []
        elif name is not None:
            lines.append(line)
    if name is not None:
        blocks.append((name, params, lines))

    defined = [block[0] for block in blocks]
    defined_set = set(defined)
    mysteries: OrderedDict[str, None] = OrderedDict()
    for block_name, block_params, block_lines in blocks:
        local = set(block_params)
        for line in block_lines:
            text_line = body(line)
            if text_line and "<-" in text_line:
                local.update(IDENT_RE.findall(text_line.split("<-", 1)[0]))
        for line in block_lines:
            text_line = body(line)
            if text_line is None:
                continue
            for callee in CALL_RE.findall(text_line) + OF_OPERATOR_RE.findall(text_line):
                if callee in local or callee in CONTROL_WORDS or callee in defined_set:
                    continue
                mysteries.setdefault(callee, None)
    return defined, list(mysteries)


def verify_python(text: str) -> None:
    tree = ast.parse(text)
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    missing = [name for name in LOCAL_MAP.values() if name not in functions]
    if missing:
        raise RuntimeError(f"missing Python functions: {missing}")
    for mystery, (_, evidence) in RESOLUTIONS.items():
        absent = [needle for needle in evidence if needle not in text]
        if absent:
            raise RuntimeError(f"resolution evidence missing for {mystery}: {absent}")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def svg_tree(side: str) -> str:
    if side not in {"pseudo", "python"}:
        raise ValueError(side)

    width = 350
    line = 25
    top = 27
    y = top
    layout: list[tuple[str, float, object]] = [("root", y, None)]
    y += 39
    for group_name, items in GROUPS:
        layout.append(("group", y, group_name))
        y += line
        for item in items:
            layout.append(("item", y, item))
            y += line
        y += 8
    height = int(y + 12)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        '<style>',
        'text { font-family: "TeX Gyre Pagella", "Liberation Serif", serif; fill: #111; }',
        '.root { font-size: 15px; font-weight: 700; }',
        '.group { font-size: 13px; font-weight: 700; }',
        '.item { font-size: 12.5px; }',
        '.defined { font-weight: 600; }',
        '.tree { stroke: #555; stroke-width: 0.8; fill: none; }',
        '.mystery { stroke: #333; stroke-width: 0.9; stroke-dasharray: 4 3; fill: white; }',
        '.resolved { stroke: #777; stroke-width: 0.7; fill: white; }',
        '</style>',
    ]

    # Root
    root_label = "Q3" if side == "pseudo" else "run_q3"
    out.append('<rect x="18" y="12" width="78" height="25" rx="2" fill="white" stroke="#111" stroke-width="0.9"/>')
    out.append(f'<text class="root" x="57" y="30" text-anchor="middle">{esc(root_label)}</text>')

    group_rows = [entry for entry in layout if entry[0] == "group"]
    if group_rows:
        first_gy = group_rows[0][1]
        last_gy = group_rows[-1][1]
        out.append(f'<path class="tree" d="M30 37 V{last_gy}"/>')

    for index, (kind, row_y, payload) in enumerate(layout):
        if kind != "group":
            continue
        group_name = str(payload)
        out.append(f'<path class="tree" d="M30 {row_y} H49"/>')
        out.append(f'<circle cx="49" cy="{row_y}" r="2.2" fill="#111"/>')
        out.append(f'<text class="group" x="58" y="{row_y + 4}">{esc(group_name)}</text>')

        # Find this group's items and draw its child trunk.
        group_def = next(g for g in GROUPS if g[0] == group_name)
        item_count = len(group_def[1])
        first_item_y = row_y + line
        last_item_y = row_y + line * item_count
        out.append(f'<path class="tree" d="M49 {row_y + 3} H62 V{last_item_y}"/>')

        for item_index, item in enumerate(group_def[1], start=1):
            status, pseudo_label, python_label = item
            iy = row_y + line * item_index
            out.append(f'<path class="tree" d="M62 {iy} H77"/>')
            label = pseudo_label if side == "pseudo" else python_label
            if status == "defined":
                out.append(f'<circle cx="80" cy="{iy}" r="2.1" fill="#111"/>')
                out.append(f'<text class="item defined" x="89" y="{iy + 4}">{esc(label)}</text>')
            else:
                display = f"? {label}" if side == "pseudo" else label
                char_width = 6.25
                box_width = min(250, max(58, 16 + char_width * len(display)))
                box_x = 78
                box_y = iy - 10.5
                css_class = "mystery" if side == "pseudo" else "resolved"
                out.append(f'<rect class="{css_class}" x="{box_x}" y="{box_y}" width="{box_width}" height="20" rx="2"/>')
                out.append(f'<text class="item" x="{box_x + 7}" y="{iy + 4}">{esc(display)}</text>')

    out.append('</svg>')
    return "\n".join(out) + "\n"


def write_outputs(output_dir: Path, side: str, stem_name: str) -> None:
    svg = svg_tree(side)
    stem = output_dir / stem_name
    svg_path = stem.with_suffix(".svg")
    pdf_path = stem.with_suffix(".pdf")
    png_path = stem.with_suffix(".png")
    svg_path.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(pdf_path))
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path), output_width=1050)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pseudocode", type=Path)
    parser.add_argument("python", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    pseudo_bytes = args.pseudocode.read_bytes()
    python_bytes = args.python.read_bytes()
    pseudo_text = pseudo_bytes.decode("utf-8")
    python_text = python_bytes.decode("utf-8")

    defined, mysteries = extract_defined_and_mysteries(pseudo_text)
    if defined != list(LOCAL_MAP):
        raise RuntimeError(f"unexpected pseudocode functions: {defined}")
    if set(mysteries) != set(RESOLUTIONS):
        raise RuntimeError(
            "mystery/resolution mismatch: "
            f"missing={sorted(set(mysteries) - set(RESOLUTIONS))}, "
            f"extra={sorted(set(RESOLUTIONS) - set(mysteries))}"
        )
    verify_python(python_text)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(args.output_dir, "pseudo", "ternatree_pseudocode_mysteries")
    write_outputs(args.output_dir, "python", "ternatree_sympy_resolutions")

    audit = [
        "TERNATREE MYSTERY TREE AUDIT",
        f"pseudocode_sha256 {sha256_bytes(pseudo_bytes)}",
        f"python_sha256 {sha256_bytes(python_bytes)}",
        f"defined_functions {len(defined)} {' '.join(defined)}",
        f"mystery_vertices {len(mysteries)} {' '.join(mysteries)}",
        "tree_depth 3",
        "resolution_coverage PASS",
        "python_evidence PASS",
        "",
        "MYSTERY\tRESOLUTION",
    ]
    audit.extend(f"{name}\t{RESOLUTIONS[name][0]}" for name in mysteries)
    (args.output_dir / "mystery_graph_audit.txt").write_text("\n".join(audit) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
