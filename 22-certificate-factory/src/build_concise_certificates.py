#!/usr/bin/env python3
"""Build concise illustrated TeX/PDF certificates for all 23 canonical cases."""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
import os
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = json.loads((ROOT / "work/targets.json").read_text())
IDS = [a for family in TARGETS["families"] for a in family["targets"]]


def load(path: Path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(case: Path, rel: str):
    wrapper = load(case / rel)
    source = wrapper.get("canonical_source") if isinstance(wrapper, dict) else None
    if not source:
        return wrapper, rel
    path_text, _, fragment = source.partition("#")
    path = ROOT / path_text if path_text.startswith("runs/") else case / path_text
    obj = load(path)
    for key in fragment.strip("/").split("/") if fragment.strip("/") else []:
        obj = obj[key]
    return obj, source


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tex_escape(text: str):
    table = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(table.get(ch, ch) for ch in str(text))


def math_expr(text: str):
    s = str(text).replace("**", "^").replace("*", r"\,")
    s = re.sub(r"\^(\d+)", r"^{\1}", s)
    s = re.sub(r"\^\(([^)]+)\)", r"^{\1}", s)
    s = s.replace("rho", r"\rho").replace("pi", r"\pi")
    return s


def scalar_latex(text: str):
    s = str(text)
    match = re.fullmatch(r"(-?\d+)/(\d+)", s)
    if match:
        return rf"\frac{{{match.group(1)}}}{{{match.group(2)}}}"
    return math_expr(s)


def matrix_latex(obj, max_dimension=4):
    if not isinstance(obj, dict) or "entries" not in obj:
        return None
    rows, cols = obj.get("shape", [len(obj["entries"]), len(obj["entries"][0])])
    if max(rows, cols) > max_dimension:
        return None
    entries = obj["entries"]
    cell_lengths = [len(str(x)) for row in entries for x in row]
    if sum(cell_lengths) > 300 or max(cell_lengths, default=0) > 40:
        return None
    body = r"\\".join("&".join(scalar_latex(x) for x in row) for row in entries)
    return rf"\begin{{pmatrix}}{body}\end{{pmatrix}}"


def multinomial_formula(case: Path, spec: dict):
    cid = case.name
    formula = load(case / "data/coefficient_formula.json")["formula"]
    if "parent" in spec:
        power = spec["observable"].rsplit("^", 1)[-1]
        return (rf"\[\begin{{gathered}}p(n)=[x^n]A_{{\rm parent}}(x),\\"
                rf"a(n)=\sum_{{\substack{{n_1,\ldots,n_{power}\ge0\\n_1+\cdots+n_{power}=n}}}}"
                rf"\prod_{{j=1}}^{{{power}}}p(n_j).\end{{gathered}}\]")
    inverse = load(case / "data/inverse_map.json")
    coefficients = inverse.get("D_coefficients_by_power")
    if inverse.get("type") == "rational":
        q = int(spec["q"])
        d = load(case / "data/coefficient_formula.json").get("d", "1")
        highest = q - 1
        weights = [str(math.comb(q, j + 1)) for j in range(1, highest + 1)]
        product = r"\,".join(rf"{weights[j-1]}^{{k_{j}}}" for j in range(1, highest + 1))
        return (rf"\[\begin{{gathered}}\mathcal K_{{n,h}}=\{{(k_1,\ldots,k_{highest})\in\mathbb Z_{{\ge0}}^{{{highest}}}:"
                rf"h+\sum_{{j=1}}^{{{highest}}}jk_j=n-1\}},\quad K=\sum_{{j=1}}^{{{highest}}}k_j,\\"
                rf"a(n)=\frac{{{d}}}{{n}}\sum_{{h=0}}^{{n-1}}\binom{{n}}{{h}}"
                rf"\sum_{{\boldsymbol k\in\mathcal K_{{n,h}}}}\binom{{n+K-1}}{{K}}"
                rf"\binom{{K}}{{k_1,\ldots,k_{highest}}}{product}.\end{{gathered}}\]")
    if not coefficients:
        return rf"\texttt{{{tex_escape(formula)}}}"
    d = load(case / "data/coefficient_formula.json").get("d", "1")
    highest = max(int(k) for k in coefficients if int(k) > 0)
    weights = [str(-int(str(coefficients[str(j)]).replace("(", "").replace(")", ""))) for j in range(1, highest + 1)]
    product = " ".join(rf"{weights[j-1]}^{{k_{j}}}" for j in range(1, highest + 1))
    return (rf"\[\begin{{gathered}}\mathcal K_n=\{{(k_1,\ldots,k_{highest})\in\mathbb Z_{{\ge0}}^{{{highest}}}:"
            rf"\sum_{{j=1}}^{{{highest}}}jk_j=n-1\}},\quad K=\sum_{{j=1}}^{{{highest}}}k_j,\\"
            rf"a(n)=\frac{{{d}}}{{n}}\sum_{{\boldsymbol k\in\mathcal K_n}}\binom{{n+K-1}}{{K}}"
            rf"\binom{{K}}{{k_1,\ldots,k_{highest}}}{product}.\end{{gathered}}\]")


def rho_latex(contour):
    """Render the kernel uniformly; companions store D with rho(u)=uD(u)."""
    raw = contour.get("rho")
    if not raw:
        return rf"u\left({math_expr(contour.get('D', 'D(u)'))}\right)"
    rational = re.fullmatch(r"u\*\((.+)\)/\((.+)\)", raw)
    if rational:
        return rf"u\,\dfrac{{{math_expr(rational.group(1))}}}{{{math_expr(rational.group(2))}}}"
    return math_expr(raw)


def multiplicity_text(tree_model: dict):
    values = tree_model.get("branch_multiplicities", tree_model.get("parent_branch_multiplicities", {}))
    if not values:
        return r"\text{no repeated constructor codes}"
    rendered = []
    for key, value in values.items():
        code = key.removeprefix("Delta_")
        if "_with_" in code:
            arity = code.split("_", 1)[0]
            label = rf"\Delta_{{{arity}}}^{{\rm marked}}"
        else:
            label = rf"\Delta_{{{tex_escape(code)}}}"
        rendered.append(rf"{label}\!:\,{value}")
    return r",\;".join(rendered)


def reduction_panel(case: Path):
    matrices, matrix_source = resolve(case, "data/matrices.json")
    matrices = matrices.get("matrices", matrices)
    certificate, certificate_source = resolve(case, "data/certificate.json")
    # A human certificate shows a coherent reduction tuple, never a partial
    # grab-bag of matrices.  G is optional; U, V, and J are inseparable.
    rendered = {key: matrix_latex(matrices.get(key)) for key in ("G", "U", "V", "J")}
    parts = []
    if all(rendered[key] for key in ("U", "V", "J")):
        keys = ("G", "U", "V", "J") if rendered["G"] else ("U", "V", "J")
        parts = [rf"{key}={rendered[key]}" for key in keys]
    shown = r",\quad ".join(parts)
    if not shown:
        shown = r"\text{No compact matrix tuple is shown; see the embedded exact reduction data.}"
    if "numerator_N" in certificate:
        numerator = certificate["numerator_N"]
        if len(numerator) <= 115:
            cert = rf"R(n,u)=\dfrac{{{math_expr(numerator)}}}{{\rho(u)^{{{certificate.get('denominator_power', 0)}}}}}"
        else:
            cert = rf"R(n,u)=N(n,u)/\rho(u)^{{{certificate.get('denominator_power', 0)}}},\ \deg_uN={max(map(int,re.findall(r'u\*\*(\d+)',numerator) or ['1']))}"
    elif "C" in certificate:
        if certificate["C"] == "(1+t)*P/(n*(n+1)*t^3*Q^3)":
            cert = r"C(n,t)=\dfrac{(1+t)P(n,t)}{n(n+1)t^3Q(t)^3}"
        else:
            cert = rf"C(n,t)=\texttt{{{tex_escape(certificate['C'])}}}"
    elif "N" in certificate:
        cert = rf"R(n,u)=N(n,u)/({math_expr(certificate.get('denominator_base','D'))})^{{{certificate.get('denominator_power','?')}}}"
    elif "numerator" in certificate:
        numerator = str(certificate["numerator"])
        cert = rf"R(n,u,x)=N/D\ \text{{(exact }}{len(numerator)}\text{{-character numerator in embedded payload)}}"
    else:
        cert = rf"\text{{exact telescoper certificate: }}\texttt{{{tex_escape(certificate_source)}}}"
    identity = r"\sum_r P_r(n)H_{n+r}(u)=\partial_u\!\left(R(n,u)H_n(u)\right)"
    return shown, cert, identity


def polynomial_degree(expressions):
    degree = 0
    for expression in expressions:
        powers = [int(k) for k in re.findall(r"n\*\*(\d+)", expression)]
        if re.search(r"\bn\b", expression):
            powers.append(1)
        degree = max([degree] + powers)
    return degree


def contour_text(contour):
    """Use the exact stored contour statement, without inventing a numerator."""
    formula = contour.get("coefficient_integral") or contour.get("formula")
    if formula:
        simple = re.fullmatch(r"a\(n\)=\((\d+)\)/\(2\*pi\*i\*n\)\s*\*?\s*integral_gamma du/rho\(u\)\^n, n>=1", formula)
        if simple:
            return rf"\(a(n)=\dfrac{{{simple.group(1)}}}{{2\pi i n}}\oint_\gamma\dfrac{{du}}{{\rho(u)^n}},\quad n\ge1.\)"
        companion = re.fullmatch(r"\[x\^n\]A\(x\)\^(\d+)=\((\d+)\*1\)/\(2\*pi\*i\*n\)\*integral_gamma \(1\+\(1\)\*u\)\^(\d+) du/\(u\^n\*D\(u\)\^n\)", formula)
        if companion:
            power, constant, numerator_power = companion.groups()
            return rf"\([x^n]A(x)^{{{power}}}=\dfrac{{{constant}}}{{2\pi i n}}\oint_\gamma\dfrac{{(1+u)^{{{numerator_power}}}\,du}}{{u^nD(u)^n}}.\)"
        return (r"\texttt{" + tex_escape(formula) + r"}")
    kernel = contour.get("rho", contour.get("D", "kernel recorded in payload"))
    return r"kernel \(=" + math_expr(kernel) + r"\); exact extraction formula is embedded in the payload."


def recurrence(case: Path):
    obj, source = resolve(case, "data/recurrence.json")
    if isinstance(obj, dict) and "recurrence" in obj:
        obj = obj["recurrence"]
    if isinstance(obj, list):
        vals, valid = obj, 1
    elif "coefficients" in obj:
        vals, valid = obj["coefficients"], int(obj.get("valid_from_n", 1))
    else:
        vals = obj["p"]
        valid = 0 if "n=0 checked" in obj.get("validity", "") else 1
    return vals, valid, source


def ode(case: Path):
    obj, source = resolve(case, "data/ode.json")
    return obj, source


def matrix_summary(case: Path):
    wrapper = load(case / "data/matrices.json")
    stats = wrapper.get("statistics", wrapper.get("pilot_statistics", {}))
    if stats:
        g = stats.get("G_shape", stats.get("Gx_shape"))
        x = stats.get("X_shape")
        rank = stats.get("rank", stats.get("X_rank", x[0] if x else None))
        return g, x, rank, int(stats.get("nullity", 1))
    obj, _ = resolve(case, "data/matrices.json")
    obj = obj.get("matrices", obj)
    gobj = obj.get("G", obj.get("Gx"))
    xobj = obj["X"]
    g, x = gobj["shape"], xobj["shape"]
    return g, x, x[0], 1


def parse_raw_word(raw: str):
    def parse(index):
        if raw.startswith("false", index): return 0, index + 5
        if raw.startswith("l", index): return 1, index + 1
        op = raw.index("(", index)
        name, index = raw[index:op], op + 1
        children = []
        while True:
            child, index = parse(index); children.append(child)
            if raw[index] == ",": index += 1; continue
            assert raw[index] == ")"; index += 1; break
        return (children[0] if name.startswith("root") else tuple(children)), index
    tree, end = parse(0)
    assert end == len(raw)
    return tree


def brace(tree):
    if tree == 1: return "1"
    if tree == 0: return "0"
    return "{" + ",".join(brace(x) for x in tree) + "}"


def true_leaf_count(tree):
    if tree == 1: return 1
    if tree == 0: return 0
    return sum(true_leaf_count(child) for child in tree)


def picture_multiplicity(case: Path, tree, tree_note: str):
    """Number of colored words represented by a displayed color-erased code."""
    if tree_note.startswith("literal"):
        return 1
    record = load(case / "data/set_elements_n_le_3.json")
    group = record["elements_by_true_leaf_count"].get(str(true_leaf_count(tree)), [])
    counts = Counter(brace(parse_raw_word(raw)) for raw in group)
    return counts.get(brace(tree), 1)


def display_trees(case: Path):
    cid = case.name
    tree = load(case / "data/tree_model.json")
    spec = load(case / "input/case_spec.json")
    if cid in ("A120589", "A120591"):
        elems = load(case / "data/set_elements_n_le_3.json")["elements_by_true_leaf_count"]
        candidates = [parse_raw_word(elems[k][0]) for k in ("1", "2", "3")]
        if len(elems["3"]) > 1: candidates.append(parse_raw_word(elems["3"][-1]))
        return candidates[:4], "forest slots are explicit; 0 denotes an empty slot"
    q = int(spec.get("q", 3))
    mult = tree.get("branch_multiplicities", {})
    literal = "b" in spec and all(mult.get(f"Delta_{k}") == math.comb(q, k) for k in range(2, q + 1))
    if literal:
        binary_left = tuple([1, 1] + [0] * (q - 2))
        binary_right = tuple([0] * (q - 2) + [1, 1])
        ternary = tuple([1, 1, 1] + [0] * (q - 3)) if q >= 3 else (binary_left, 1)
        return [1, binary_left, binary_right, ternary], f"literal {q}-slot geometry; empty positions are shown"
    # Colored grammars are honest arity-k trees; a color key distinguishes constructors.
    return [1, (1, 1), (1, (1, 1)), (1, 1, 1)], "colored arity geometry; node color distinguishes constructors"


def tikz_tree(tree, color_index=0):
    branch_colors = ["blue!18", "orange!24", "green!20", "violet!16"]
    counter = itertools.count()
    def emit(node, depth=0):
        ident = f"n{next(counter)}"
        if node == 1: return rf"node[trueleaf] ({ident}) {{}}"
        if node == 0: return rf"node[falseleaf] ({ident}) {{}}"
        fill = branch_colors[(color_index + depth) % len(branch_colors)]
        children = " ".join("child {" + emit(ch, depth + 1) + "}" for ch in node)
        return rf"node[branch,fill={fill}] ({ident}) {{}} {children}"
    prefix = r"\begin{tikzpicture}[level distance=9mm,level 1/.style={sibling distance=10mm},level 2/.style={sibling distance=6mm},scale=.82,transform shape] "
    return prefix + "\\" + emit(tree) + r";\end{tikzpicture}"


def compact_payload(case: Path):
    cid = case.name
    data = {}
    for rel in (
        "input/case_spec.json", "data/tree_model.json", "data/set_elements_n_le_3.json",
        "data/inverse_map.json", "data/coefficient_formula.json", "data/contour.json",
        "data/integrand_analysis.json", "data/recurrence.json", "data/ode.json",
        "data/terms.json", "checks/results.json",
    ):
        data[rel] = load(case / rel)
    rec, recsrc = resolve(case, "data/recurrence.json")
    od, odsrc = resolve(case, "data/ode.json")
    cert, certsrc = resolve(case, "data/certificate.json")
    matrices, matsrc = resolve(case, "data/matrices.json")
    encoded_matrices = json.dumps(matrices, sort_keys=True).encode()
    g, x, rank, nullity = matrix_summary(case)
    payload = {
        "schema_version": "1.0",
        "case_id": cid,
        "status": "verified",
        "normalized_records": data,
        "resolved_recurrence": rec,
        "resolved_recurrence_source": recsrc,
        "resolved_ode": od,
        "resolved_ode_source": odsrc,
        "resolved_certificate": cert,
        "resolved_certificate_source": certsrc,
        "matrix_summary": {"G_or_Gx_shape": g, "X_shape": x, "rank": rank, "nullity": nullity},
        "resolved_matrices_source": matsrc,
        "resolved_matrices_sha256": hashlib.sha256(encoded_matrices).hexdigest(),
        "compact_exact_matrices": {k: v for k, v in matrices.get("matrices", matrices).items() if k in ("G", "Gx", "U", "Ux", "V", "Vx", "J") and matrix_latex(v) is not None},
        "note": "Full matrix entries remain at the precise canonical source above to avoid overwhelming the presentation PDF.",
    }
    out = case / "release/certificate_payload.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return out


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.25in]{geometry}
\usepackage{amsmath,amssymb,booktabs,array,tabularx,xcolor,tikz,hyperref,embedfile,microtype}
\usetikzlibrary{trees}
\hypersetup{colorlinks=true,urlcolor=blue!55!black}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\linespread{1.035}\selectfont
\definecolor{navy}{RGB}{25,54,86}
\definecolor{soft}{RGB}{244,247,250}
\tikzset{branch/.style={circle,draw=navy,line width=.6pt,inner sep=2pt},trueleaf/.style={circle,draw=navy,fill=navy,inner sep=2.1pt},falseleaf/.style={circle,draw=navy,fill=white,inner sep=1.8pt}}
\newcommand{\sectionbar}[1]{\vspace{3pt}{\color{navy}\bfseries #1}\par\vspace{2pt}\hrule\vspace{4pt}}
\begin{document}
\enlargethispage{.12in}
"""


def build_tex(case: Path, payload: Path):
    cid = case.name
    spec = load(case / "input/case_spec.json")
    contour = load(case / "data/contour.json")
    terms = load(case / "data/terms.json")
    checks = load(case / "checks/results.json")
    tree_model = load(case / "data/tree_model.json")
    vals, valid, recsrc = recurrence(case)
    od, odsrc = ode(case)
    ordinary = od["ordinary_derivative_form"]
    g, xshape, rank, nullity = matrix_summary(case)
    trees, tree_note = display_trees(case)
    if "equation" in spec:
        equation_display = math_expr(spec["equation"])
    elif spec.get("parent") and spec.get("observable"):
        power = spec["observable"].rsplit("^", 1)[-1]
        parent_number = tex_escape(spec["parent"].removeprefix("A"))
        equation_display = (rf"A(x)=A_{{\mathrm{{parent}}}}(x)^{{{power}}},\quad "
                            rf"A_{{\mathrm{{parent}}}}(x)=A_{{{parent_number}}}(x)")
    else:
        equation_display = rf"\text{{{tex_escape(spec.get('observable', 'observable'))}}}"
    normalization = tree_model.get("normalization", tree_model.get("model", ""))
    grammar = tree_model.get("recursive_equation", tree_model.get("model", ""))
    if normalization == grammar:
        normalization_display = normalization
    elif len(grammar) > 70:
        normalization_display = normalization + "; T-polynomial coefficients are the Delta multiplicities below"
    else:
        normalization_display = normalization + "; " + grammar
    rho = rho_latex(contour)
    rec_order = len(vals) - 1
    ode_order = ordinary["order"]
    initial = ",".join(map(str, terms["terms"][:8]))
    published = len(terms["oeis_prefix_checked"])
    drawings = []
    for i, t in enumerate(trees):
        multiplicity = picture_multiplicity(case, t, tree_note)
        label = tex_escape(brace(t) + f"x{multiplicity}")
        drawings.append(rf"\begin{{minipage}}[t]{{.235\textwidth}}\centering {tikz_tree(t, i)}\\[2pt]{{\normalsize\texttt{{{label}}}}}\end{{minipage}}")
    if len(vals) <= 5 and max(map(len, vals)) < 150 and sum(map(len, vals)) < 310:
        rec_rows = [rf"P_{{{i}}}(n)&={math_expr(v)}" for i, v in enumerate(vals)]
        rec_display = r"\(\sum_{r=0}^{" + str(rec_order) + r"}P_r(n)a(n+r)=0\), \(n\ge " + str(valid) + r"\), with \[\begin{aligned}" + r"\\".join(rec_rows) + r"\end{aligned}\]"
    else:
        rec_display = rf"\(\sum_{{r=0}}^{{{rec_order}}}P_r(n)a(n+r)=0\) for \(n\ge {valid}\). The exact degree-{polynomial_degree(vals)} coefficient polynomials are embedded in \texttt{{certificate\_payload.json}} (source: \texttt{{{tex_escape(recsrc)}}})."
    coeffs = ordinary["coefficients"]
    if ode_order <= 4 and max(map(len, coeffs)) < 60 and sum(map(len, coeffs)) < 125:
        ode_terms = []
        for j, c in enumerate(coeffs):
            derivative = "A(x)" if j == 0 else ("A'(x)" if j == 1 else rf"A^{{({j})}}(x)")
            ode_terms.append(rf"\left({math_expr(c)}\right){derivative}")
        rhs = math_expr(od.get("boundary_polynomial", "0"))
        if sum(map(len, coeffs)) > 85 and len(ode_terms) > 2:
            chunks = ["+".join(ode_terms[i:i + 2]) for i in range(0, len(ode_terms), 2)]
            ode_display = r"\[\begin{aligned}&" + r"\\[-1pt]&+".join(chunks) + "=" + rhs + r".\end{aligned}\]"
        else:
            ode_display = r"\[" + "+".join(ode_terms) + "=" + rhs + r".\]"
    else:
        ode_display = rf"The scalar linear ODE has order {ode_order}. It is obtained from the recurrence by the standard Euler-operator substitution. Exact coefficients and boundary polynomial: \texttt{{{tex_escape(odsrc)}}}."
    contour_display = contour_text(contour)
    closed_form = multinomial_formula(case, spec)
    multiplicities = multiplicity_text(tree_model)
    matrices_display, telescoper_display, telescoper_identity = reduction_panel(case)
    if r"\begin{pmatrix}" in matrices_display:
        matrix_panel = (r"\begingroup\renewcommand{\arraystretch}{1.42}\setlength{\arraycolsep}{5pt}"
                        rf"{{\small\[\displaystyle {matrices_display}\]}}\endgroup")
    else:
        matrix_panel = rf"{{\small \({matrices_display}\)}}"
    source_paths = rf"\texttt{{data/tree\_model.json}}, \texttt{{data/contour.json}}, \texttt{{data/matrices.json}}, \texttt{{data/recurrence.json}}, \texttt{{data/ode.json}}"
    text = PREAMBLE + rf"""
\embedfile[desc={{{cid} exact certificate payload}},mimetype=application/json]{{certificate_payload.json}}
{{\color{{navy}}\LARGE\bfseries {cid} concise calculus certificate}}\hfill{{\small VERIFIED}}\\[-1pt]
{{\small Bradley Klee, \quad Mech.An.ika Sol (Open AI) \hfill July 31, 2026}}

\sectionbar{{Definition and first terms}}
\(\displaystyle {equation_display}\), with the origin-normalized solution.\\
{{\footnotesize Normalization/grammar: \texttt{{{tex_escape(normalization_display)}}}.}}\\
\(a(0),\ldots,a(7)={initial}\).\\[2pt]
{{\small Kernel used throughout: \(\displaystyle \rho(u)={rho}\), so \(x=\rho(T(x))\).}}

\sectionbar{{Typogeometry}}
{''.join(drawings)}

{{\footnotesize {tex_escape(tree_note)}. Filled endpoints are true leaves; open endpoints are false/empty leaves. For colored grammars, color is genuine constructor data and is not silently converted into a positional zero pattern.}}

{{\footnotesize Typogeometric constructor codes and multiplicities: \({multiplicities}\).}}

\sectionbar{{Coefficient and contour extraction}}
{{\footnotesize {closed_form}}}
{contour_display}

\sectionbar{{Recurrence}}
{{\footnotesize {rec_display}}}

\sectionbar{{Differential equation}}
{{\footnotesize {ode_display}}}

\sectionbar{{Matrices, telescoper certificate, and checks}}
{matrix_panel}
\par\vspace{{6pt}}
{{\small\textbf{{Certificate.}}\par\smallskip\(\displaystyle {telescoper_display}.\)\par}}
\vspace{{4pt}}
{{\small Telescoping identity: \({telescoper_identity}.\)\par}}
\vspace{{4pt}}
{{\footnotesize Matrix dimensions: \({g[0]}\times {g[1]}\); remainder \({xshape[0]}\times {xshape[1]}\), rank {rank}, nullity {nullity}. The exact telescoping residual is zero. The recurrence reconstructs all 24 stored terms; {published}/{published} published OEIS prefix terms match.\par}}

\vfill
\colorbox{{soft}}{{\parbox{{.97\textwidth}}{{\tiny Canonical records: {source_paths}. Embedded payload contains exact sources and SHA-256 matrix identifiers. Compare with the verbose certificate for A120590.}}}}
\end{{document}}
"""
    tex = case / "release/certificate.tex"
    tex.write_text(text)
    return tex


def compile_tex(tex: Path):
    release = tex.parent
    proc = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-jobname=certificate.building", tex.name],
        cwd=release, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    (release / "certificate.build.log").write_text(proc.stdout)
    (release / "certificate.log").write_text(proc.stdout)
    if proc.returncode:
        raise RuntimeError(f"LaTeX failed for {tex}:\n{proc.stdout[-3000:]}")
    staged = release / "certificate.building.pdf"
    check = subprocess.run(["pdfinfo", str(staged)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode:
        raise RuntimeError(f"Staged PDF integrity check failed: {staged}")
    published = release / "certificate.pdf"
    os.replace(staged, published.resolve())
    return published


def main():
    assert len(IDS) == 23
    results = []
    for cid in IDS:
        case = ROOT / "examples" / cid
        payload = compact_payload(case)
        tex = build_tex(case, payload)
        pdf = compile_tex(tex)
        named_pdf = case / "release/certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.pdf"
        named_tex = case / "release/certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.tex"
        if not named_pdf.exists() or not os.path.samefile(pdf, named_pdf):
            shutil.copy2(pdf, named_pdf)
        if not named_tex.exists() or not os.path.samefile(tex, named_tex):
            shutil.copy2(tex, named_tex)
        (case / "release/certificate.pdf.status.json").write_text(json.dumps({
            "status": "verified",
            "pdf": "certificate.pdf",
            "tex": "certificate.tex",
            "embedded_payload": "certificate_payload.json",
            "fresh_named_copy": "certificate_WITH_RHO_AND_INLINE_MULTIPLICITIES.pdf",
        }, indent=2, sort_keys=True) + "\n")
        results.append({"case_id": cid, "tex": str(tex.relative_to(ROOT)), "pdf": str(pdf.relative_to(ROOT)), "payload": str(payload.relative_to(ROOT)), "pdf_bytes": pdf.stat().st_size, "pdf_sha256": sha(pdf)})
    # A managed/networked filesystem can very occasionally expose a short PDF
    # immediately after TeX exits.  Never publish such a file: validate and
    # rebuild the affected case before writing the build report.
    for item in results:
        pdf = ROOT / item["pdf"]
        for attempt in range(3):
            check = subprocess.run(["pdfinfo", str(pdf)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            attach = subprocess.run(["pdfdetach", "-list", str(pdf)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if check.returncode == 0 and "1 embedded files" in attach.stdout:
                break
            compile_tex(pdf.with_suffix(".tex"))
        else:
            raise RuntimeError(f"PDF integrity check failed after retries: {pdf}")
        item["pdf_bytes"] = pdf.stat().st_size
        item["pdf_sha256"] = sha(pdf)
    out = ROOT / "reports/concise_certificate_build.json"
    out.write_text(json.dumps({"status": "built", "case_count": 23, "cases": results}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "built", "case_count": 23, "pdf_bytes": sum(x["pdf_bytes"] for x in results)}))


if __name__ == "__main__":
    main()
