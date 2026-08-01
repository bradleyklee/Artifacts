#!/usr/bin/env python3
"""Generate per-sequence OEIS field deltas from the verified certificates."""
from __future__ import annotations

import gzip
import json
import re
import math
import itertools
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = {
    "A120588", "A120590", "A120592", "A120593", "A120594", "A120595",
    "A120596", "A120597", "A120598", "A120599", "A120600", "A120601",
    "A120602", "A120603", "A120604", "A120605", "A120606", "A120607",
}
COMPANIONS = {"A120589", "A120591"}
DESCENDANTS = {"A244594", "A244627", "A244856"}


def load(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(case: Path, relative: str):
    wrapper = load(case / relative)
    source = wrapper.get("canonical_source") if isinstance(wrapper, dict) else None
    if not source:
        return wrapper
    path_text, _, fragment = source.partition("#")
    path = ROOT / path_text if path_text.startswith("runs/") else case / path_text
    obj = load(path)
    for key in fragment.strip("/").split("/") if fragment.strip("/") else []:
        obj = obj[key]
    return obj


def oeis(expr: str) -> str:
    return (
        str(expr)
        .replace("**", "^")
        .replace("pi", "Pi")
        .replace("integral_gamma", "Integral_gamma")
        .replace("du/rho", "du/rho")
    )


def recurrence(case: Path):
    obj = resolve(case, "data/recurrence.json")
    if isinstance(obj, list):
        coeffs, valid = obj, "n>=1"
    elif "coefficients" in obj:
        coeffs = obj["coefficients"]
        valid = f"n>={obj.get('valid_from_n', 1)}"
    elif "p" in obj:
        coeffs = obj["p"]
        valid = "n>=0" if "n=0 checked" in obj.get("validity", "") else "n>=1"
    else:
        raise ValueError((case.name, obj))
    pieces = []
    for r, coefficient in enumerate(coeffs):
        if re.fullmatch(r"\(?0\)?", str(coefficient).strip()):
            continue
        term = f"({oeis(coefficient)})*a(n{f'+{r}' if r else ''})"
        pieces.append(term)
    return " + ".join(pieces) + f" = 0, for {valid}."


def ode(case: Path):
    obj = resolve(case, "data/ode.json")
    ordinary = obj["ordinary_derivative_form"]
    coeffs = ordinary["coefficients"]
    terms = []
    for j, coefficient in enumerate(coeffs):
        if re.fullmatch(r"\(?0\)?", str(coefficient).strip()):
            continue
        derivative = "A(x)" if j == 0 else ("A'(x)" if j == 1 else f"A^({j})(x)")
        terms.append(f"({oeis(coefficient)})*{derivative}")
    rhs = oeis(obj.get("boundary_polynomial", "0"))
    return f"Let A(x)=Sum_{{n>=0}} a(n)*x^n. Then " + " + ".join(terms) + f" = {rhs}."


def contour(case: Path):
    obj = load(case / "data/contour.json")
    formula = obj.get("coefficient_integral", obj.get("formula", ""))
    rho = obj.get("rho")
    parts = ["Integral:"]
    if rho:
        parts.append(f"With rho(u)={oeis(rho)},")
        match = re.search(r"a\(n\)=\((\d+)\)/\(2\*pi\*i\*n\)", formula)
        numerator = match.group(1) if match else "1"
        parts.append(f"a(n)=({numerator}/(2*Pi*i*n))*Integral_gamma 1/(rho(u)^n) du for n>=1.")
    elif obj.get("D"):
        parts.append(f"With D(u)={oeis(obj['D'])},")
        match = re.search(r"=\((\d+)\*1\)/\(2\*pi\*i\*n\).*\(1\+\(1\)\*u\)\^(\d+)", formula)
        numerator, power = match.groups() if match else ("1", "1")
        factor = "(1+u)" if power == "1" else f"(1+u)^{power}"
        parts.append(f"a(n)=({numerator}/(2*Pi*i*n))*Integral_gamma {factor}/(u^n*D(u)^n) du for n>=1.")
    parts.append("Here gamma is a small positively oriented loop around 0.")
    return " ".join(parts)


def tree_comment(case: Path):
    obj = load(case / "data/tree_model.json")
    if "recursive_equation" in obj:
        mult = ", ".join(f"{k}: {v}" for k, v in obj.get("branch_multiplicities", {}).items())
        if case.name == "A120590":
            return (
                "Typogeometry: From A(x)=1+T(x), write T=x+3*T^2+T^3. "
                "Branch constructors have multiplicities {Delta_2: 3, Delta_3: 1}. "
                "Multiplicities distinguish insertions of false leaves that break symmetry."
            )
        return (
            f"Typogeometry: From {obj['normalization']}, write {obj['recursive_equation']}. "
            f"Branch constructors have multiplicities {{{mult}}}."
        )
    return (
        f"Typogeometry: {obj['model']}; "
        f"{obj['top_constructor']}."
    )


def matrix_comment(case: Path):
    wrapper = load(case / "data/matrices.json")
    stats = wrapper.get("statistics", wrapper.get("pilot_statistics", {}))
    if stats:
        g = stats.get("G_shape", stats.get("Gx_shape"))
        x = stats.get("X_shape")
        rank = stats.get("rank", stats.get("X_rank"))
        nullity = stats.get("nullity", 1)
    else:
        obj = resolve(case, "data/matrices.json")
        obj = obj.get("matrices", obj)
        gobj = obj.get("G", obj.get("Gx", {}))
        xobj = obj.get("X", {})
        g = gobj.get("shape")
        x = xobj.get("shape")
        rank = x[0] if x else None
        nullity = 1
    return (
        f"Hermite reduction uses a {g[0]} X {g[1]} reduction matrix and a "
        f"{x[0]} X {x[1]} remainder matrix of rank {rank} and nullity {nullity}. "
        "Relevant data and the rational telescoping certificate are given in the linked proof certificate."
    )


def brace_word(raw: str) -> str:
    """Discard constructor/color labels while preserving ordered brace structure."""
    def parse(index: int):
        if raw.startswith("false", index):
            return "0", index + 5
        if raw.startswith("l", index):
            return "1", index + 1
        open_paren = raw.index("(", index)
        name = raw[index:open_paren]
        index = open_paren + 1
        children = []
        while True:
            child, index = parse(index)
            children.append(child)
            if raw[index] == ",":
                index += 1
                continue
            assert raw[index] == ")", (raw, index)
            index += 1
            break
        if name.startswith("root"):
            assert len(children) == 1
            return children[0], index
        assert name.startswith("Delta_"), name
        return "{" + ",".join(children) + "}", index

    word, end = parse(0)
    assert end == len(raw), (raw, end)
    assert set(word) <= set("{},01"), (raw, word)
    return word


def positional_brace_word(raw: str, q: int) -> str:
    """Expand binomial constructor colors into their literal q child slots."""
    def parse(index: int):
        if raw.startswith("false", index): return "0", index + 5
        if raw.startswith("l", index): return "1", index + 1
        open_paren = raw.index("(", index)
        label, index = raw[index:open_paren], open_paren + 1
        children = []
        while True:
            child, index = parse(index); children.append(child)
            if raw[index] == ",": index += 1; continue
            index += 1; break
        if label.startswith("root"):
            return children[0], index
        match = re.match(r"Delta_(\d+)\[(\d+)\]", label)
        arity, color = map(int, match.groups())
        positions = list(itertools.combinations(range(q), arity))[color]
        slots = ["0"] * q
        for position, child in zip(positions, children): slots[position] = child
        return "{" + ",".join(slots) + "}", index
    word, end = parse(0)
    assert end == len(raw)
    return word


def typogeometric_examples(case: Path):
    obj = load(case / "data/set_elements_n_le_3.json")
    groups = []
    for leaf_count in sorted(obj["elements_by_true_leaf_count"], key=int):
        raw_words = obj["elements_by_true_leaf_count"][leaf_count]
        counts = Counter(brace_word(raw) for raw in raw_words)
        shown = list(counts.items())[:4]
        rendered = ", ".join(f"{word} (*{multiplicity})" for word, multiplicity in shown)
        suffix = f", ... ({len(raw_words)} total)" if len(counts) > len(shown) else ""
        noun = "leaf" if int(leaf_count) == 1 else "leaves"
        groups.append(f"{leaf_count} true {noun}: {rendered}{suffix}")
    return (
        "Typogeometries in the {,},0,1 encoding (1=true leaf, 0=false leaf): "
        + "; ".join(groups) + "."
    )


def coefficient_formula(case: Path):
    record = load(case / "data/coefficient_formula.json")
    contour_record = load(case / "data/contour.json")
    d = record.get("d", "1")
    rho = oeis(contour_record["rho"])
    return f"With rho(u)={rho}, a(n)=({d}/n)*[u^(n-1)](u/rho(u))^n for n>=1."


def raw_coefficient_formula(case: Path):
    return oeis(load(case / "data/coefficient_formula.json")["formula"])


def signed(field: str, case_id: str, body: str) -> str:
    """OEIS requires contributed formulas, comments, and examples to be signed."""
    body = body.strip()
    if not body.endswith("."):
        body += "."
    return f"%{field} {case_id} {body} - ~~~~"


def existing_snapshot(case_id: str, case: Path):
    spec = load(case / "input/case_spec.json")
    if case_id in PRIMARY:
        return [
            f"Defining equation: {oeis(spec['equation'])}.",
            f"Lagrange/reversion coefficient content equivalent to: {raw_coefficient_formula(case)}.",
            "A polynomial-coefficient recurrence is already present; the certificate recurrence is a shifted/scaled equivalent and should not be duplicated.",
        ]
    if case_id in COMPANIONS:
        return [
            f"Definition: {spec['observable']} from {spec['parent']}.",
            f"Coefficient identity: {raw_coefficient_formula(case)}.",
        ]
    return [
        f"Defining equation: {oeis(spec['equation'])}.",
        "Series-reversion and composition identities are already present.",
    ]


def current_comparison(case_id: str):
    if case_id in PRIMARY:
        return {
            "Defining algebraic equation": "already present",
            "Series reversion / Lagrange formula": "already present",
            "Polynomial recurrence": "already present or equivalent normalization",
            "Contour integral": "new",
            "Scalar linear ODE": "new",
            "Typogeometric interpretation": "new",
            "Brace-word examples": "new",
            "Reduction matrices / certificate": "new; concise comment plus certificate link",
        }
    if case_id in COMPANIONS:
        return {
            "Power/convolution definition": "already present",
            "Coefficient formula": "already present or immediate equivalent",
            "Polynomial recurrence": "new",
            "Contour integral": "new",
            "Scalar linear ODE": "new",
            "Typogeometric interpretation": "new",
            "Brace-word examples": "new",
            "Reduction matrices / certificate": "new; concise comment plus certificate link",
        }
    return {
        "Defining algebraic equation": "already present",
        "Series reversion / composition identity": "already present",
        "Coefficient-extraction formula": "new",
        "Polynomial recurrence": "new",
        "Contour integral": "new",
        "Scalar linear ODE": "new",
        "Typogeometric interpretation": "new",
        "Brace-word examples": "new",
        "Reduction matrices / certificate": "new; concise comment plus certificate link",
    }


def main():
    targets = load(ROOT / "work/targets.json")
    ids = [a for family in targets["families"] for a in family["targets"]]
    md = [
        "---",
        'title: "OEIS Field Deltas for 23 Calculus Certificates"',
        'generated_date: "2026-07-31"',
        "case_count: 23",
        'comparison_basis: "current OEIS records checked 2026-07-30"',
        'style_basis: "OEIS Style Sheet checked 2026-07-31"',
        'draft_basis: "A120590 live draft revision 31 checked 2026-07-31"',
        'format: "per-item comparison plus paste-ready OEIS internal fields"',
        "---",
        "",
        "# OEIS field deltas: what exists and what should be added",
        "",
        "The status tables distinguish genuinely new identities from formulas already",
        "present on OEIS in the same or an equivalent normalization. Full reduction",
        "matrices are not pasted into Formula fields; a concise dimensional identity",
        "belongs in Comments and the exact payload belongs in a linked certificate.",
        "",
        "The `%F`, `%C`, and `%H` lines below use OEIS internal-field notation.",
        "Remove the leading field code and A-number when pasting into the corresponding",
        "web form field.",
        "",
    ]
    txt = [
        "# Paste-ready OEIS additions generated from verified exact certificates.",
        "# Existing/equivalent formulas are intentionally omitted.",
        "",
    ]
    summary = {}
    for case_id in ids:
        case = ROOT / "examples" / case_id
        comparison = current_comparison(case_id)
        new_count = sum(value.startswith("new") for value in comparison.values())
        summary[case_id] = {"new_candidates": new_count, "comparison": comparison}
        md += [f"## {case_id}", "", f"Current record: https://oeis.org/{case_id}", ""]
        md += ["| Candidate identity | Status against current OEIS record |", "|---|---|"]
        for candidate, status in comparison.items():
            md.append(f"| {candidate} | {status} |")
        md += ["", "### Already on OEIS in equivalent form", ""]
        md += [f"- {line}" for line in existing_snapshot(case_id, case)]
        md += ["", "### Recommended additions", "", "```text"]
        additions = []
        if case_id in DESCENDANTS:
            additions.append(signed("F", case_id, coefficient_formula(case)))
        if case_id not in PRIMARY:
            additions.append(signed("F", case_id, f"Recurrence: {recurrence(case)}"))
        additions.append(signed("F", case_id, contour(case)))
        additions.append(signed("F", case_id, f"ODE: {ode(case)}"))
        additions.append(signed("C", case_id, tree_comment(case)))
        additions.append(signed("e", case_id, typogeometric_examples(case)))
        additions.append(signed("C", case_id, matrix_comment(case)))
        additions.append(
            f"%H {case_id} Bradley Klee, "
            f'<a href="https://github.com/bradleyklee/Artifacts/blob/main/22-certificate-factory/examples/{case_id}/release/certificate.pdf">'
            "Concise illustrated typogeometric, contour, matrix-reduction, recurrence, and ODE data certificate</a>."
        )
        md += additions + ["```", "", "### Do not resubmit", ""]
        if case_id in PRIMARY:
            md.append(
                "The algebraic equation, reversion/Lagrange formula, and polynomial "
                "recurrence are already represented on the current record."
            )
        elif case_id in COMPANIONS:
            md.append(
                "The defining convolution/power relation and its immediate coefficient "
                "identity are already represented on the current record."
            )
        else:
            md.append(
                "The algebraic equation and reversion/composition identities are already "
                "represented on the current record."
            )
        md.append("")
        txt += [f"# {case_id}"] + additions + [""]

    out_md = ROOT / "work/OEIS_FIELD_DELTAS_23_CASES.md"
    out_txt = ROOT / "work/OEIS_FIELD_ADDITIONS_23_CASES.txt"
    out_md.write_text("\n".join(md), encoding="utf-8")
    out_txt.write_text("\n".join(txt), encoding="utf-8")
    audit = {
        "status": "generated_from_verified_certificates",
        "case_count": 23,
        "comparison_date": "2026-07-30",
        "style_check_date": "2026-07-31",
        "a120590_draft_revision": 31,
        "recommended_addition_lines": sum(
            1 for line in txt if line.startswith(("%F ", "%C ", "%e ", "%H "))
        ),
        "cases": summary,
        "outputs": [
            str(out_md.relative_to(ROOT)),
            str(out_txt.relative_to(ROOT)),
        ],
    }
    (ROOT / "reports/oeis_field_delta_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "cases": 23,
        "markdown_bytes": out_md.stat().st_size,
        "paste_text_bytes": out_txt.stat().st_size,
        "addition_lines": audit["recommended_addition_lines"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
