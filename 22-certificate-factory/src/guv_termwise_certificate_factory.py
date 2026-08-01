#!/usr/bin/env python3
"""G,U,V termwise creative-telescoping certificate factory for q=2..9.

For each q >= 2, define

    D_q(u)   = 1 - sum_{k=2}^q binomial(q,k) u^(k-1),
    rho_q(u) = u D_q(u),
    H_{q,n}(u) = 1 / (n rho_q(u)^n).

The program constructs a dissertation-inspired Hermite--Ostrogradsky
matrix reduction from

    w = rho*a - rho'*b.

With deg(a),deg(b)<q this gives a square 2q x 2q matrix G.  From G^-1
we extract U and V, and lower a pole by

    w/rho^(m+1)
      = (U - J V/m)w / rho^m
        + d/du ((Vw)/(m rho^m)),

where J is coefficient-vector differentiation.  Reducing the q shifted
terms to denominator rho^n yields a (q-1) x q remainder matrix X.  Its
one-dimensional exact nullspace gives P_0(n),...,P_{q-1}(n), and the
stored V-parts give the rational certificate

    R_q(n,u) = N_q(n,u) / rho_q(u)^(q-2).

No algebraic A-equation is used in the construction.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import itertools
import json
import math
import resource
import shutil
import time

from progress_output import emit_progress
from fractions import Fraction
from functools import lru_cache, reduce
from pathlib import Path

import sympy as sp

n, u = sp.symbols("n u")
TRUE, FALSE, LEFT, RIGHT = "▪", "□", "⟨", "⟩"


def D_q(q: int) -> sp.Expr:
    return sp.expand(
        1 - sum(sp.binomial(q, k) * u ** (k - 1) for k in range(2, q + 1))
    )


def expr_text(expr: sp.Expr, *, factor: bool = False) -> str:
    value = sp.factor(expr) if factor else sp.expand(expr)
    return sp.sstr(value, order="lex")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primitive_n_vector(values: list[sp.Expr]) -> sp.Matrix:
    """Normalize a rational vector over Q(n) to a primitive vector in Z[n]."""
    expressions = [sp.cancel(value) for value in values]

    denominators = [sp.Poly(sp.denom(value), n, domain=sp.QQ) for value in expressions]
    common_denominator = denominators[0]
    for denominator in denominators[1:]:
        common_denominator = sp.lcm(common_denominator, denominator)

    polynomials = [
        sp.Poly(
            sp.cancel(value * common_denominator.as_expr()),
            n,
            domain=sp.QQ,
        )
        for value in expressions
    ]

    common_polynomial = polynomials[0]
    for polynomial in polynomials[1:]:
        common_polynomial = sp.gcd(common_polynomial, polynomial)
    polynomials = [sp.exquo(polynomial, common_polynomial) for polynomial in polynomials]

    coefficient_lcm = 1
    for polynomial in polynomials:
        for coefficient in polynomial.all_coeffs():
            coefficient_lcm = sp.ilcm(coefficient_lcm, int(sp.denom(coefficient)))
    polynomials = [
        sp.Poly(sp.expand(polynomial.as_expr() * coefficient_lcm), n, domain=sp.ZZ)
        for polynomial in polynomials
    ]

    content = 0
    for polynomial in polynomials:
        content = math.gcd(content, abs(int(polynomial.content())))
    if content > 1:
        polynomials = [
            sp.Poly(polynomial.as_expr() / content, n, domain=sp.ZZ)
            for polynomial in polynomials
        ]

    if polynomials[-1].LC() < 0:
        polynomials = [-polynomial for polynomial in polynomials]

    return sp.Matrix([polynomial.as_expr() for polynomial in polynomials])


def profile_count(q: int, leaves: int) -> int:
    """Independent multinomial arity-profile count."""
    if leaves == 0:
        return 1
    if leaves < 0:
        return 0

    target = leaves - 1
    arity_weights = list(range(1, q))
    positional_weights = [math.comb(q, k) for k in range(2, q + 1)]
    profile = [0] * (q - 1)
    total = Fraction(0, 1)

    def visit(index: int, remaining: int) -> None:
        nonlocal total
        if index == len(arity_weights) - 1:
            weight = arity_weights[index]
            if remaining % weight:
                return
            profile[index] = remaining // weight
            internal = sum(profile)
            numerator = math.factorial(leaves + internal - 1)
            denominator = math.factorial(leaves)
            position_product = 1
            for count, positional_weight in zip(profile, positional_weights):
                denominator *= math.factorial(count)
                position_product *= positional_weight**count
            total += Fraction(numerator * position_product, denominator)
            return

        weight = arity_weights[index]
        for count in range(remaining // weight + 1):
            profile[index] = count
            visit(index + 1, remaining - count * weight)
        profile[index] = 0

    visit(0, target)
    if total.denominator != 1:
        raise AssertionError(f"nonintegral profile count q={q}, leaves={leaves}: {total}")
    return total.numerator


@lru_cache(maxsize=None)
def plaintext_trees(q: int, leaves: int) -> tuple[str, ...]:
    """Enumerate normalized positional q-slot strings for small leaf counts."""
    if leaves == 1:
        return (TRUE,)
    if leaves < 1:
        return ()

    output: list[str] = []
    counts = [0] * q

    def distribute(slot: int, remaining: int, occupied: int) -> None:
        if slot == q:
            if remaining != 0 or occupied < 2:
                return
            choices: list[tuple[str, ...]] = []
            for count in counts:
                if count == 0:
                    choices.append((FALSE,))
                elif count == 1:
                    choices.append((TRUE,))
                else:
                    choices.append(plaintext_trees(q, count))
            for slots in itertools.product(*choices):
                output.append(LEFT + "".join(slots) + RIGHT)
            return

        for count in range(remaining + 1):
            counts[slot] = count
            distribute(slot + 1, remaining - count, occupied + int(count > 0))
        counts[slot] = 0

    distribute(0, leaves, 0)
    if len(output) != len(set(output)):
        raise AssertionError(f"duplicate plaintext trees q={q}, leaves={leaves}")
    return tuple(output)


def wrap_items(items: tuple[str, ...], width: int = 80) -> str:
    separator = " × "
    lines: list[str] = []
    current = ""
    for item in items:
        candidate = item if not current else current + separator + item
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = item
    if current:
        lines.append(current)
    if any(len(line) > width for line in lines):
        raise AssertionError("80-column wrapping failed")
    return "\n".join(lines) + "\n"


def matrix_dense_tsv(matrix: sp.Matrix) -> str:
    return "\n".join(
        "\t".join(expr_text(matrix[row, column]) for column in range(matrix.cols))
        for row in range(matrix.rows)
    ) + "\n"


def matrix_sparse_tsv(matrix: sp.Matrix, row_label: str, column_label: str) -> str:
    lines = [f"{row_label}\t{column_label}\tentry"]
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            entry = sp.cancel(matrix[row, column])
            if entry != 0:
                lines.append(f"{row}\t{column}\t{expr_text(entry)}")
    return "\n".join(lines) + "\n"


def vector_to_polynomial(vector: sp.Matrix, degree: int) -> sp.Expr:
    return sp.expand(sum(vector[index] * u**index for index in range(degree)))



def matrix_json(matrix: sp.Matrix) -> list[list[str]]:
    """Exact dense matrix encoding for the audit JSON."""
    return [
        [expr_text(sp.cancel(matrix[r, c])) for c in range(matrix.cols)]
        for r in range(matrix.rows)
    ]


def display_path(path: Path) -> str:
    """Show useful output locations without exposing a local home/user path."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        parent = resolved.parent.name
        return str(Path("<external>") / parent / resolved.name)


def progress(stage: str, message: str) -> None:
    emit_progress(stage, message)


def build_case(
    q: int,
    case_dir: Path,
    term_limit: int,
    *,
    D_override: sp.Expr | None = None,
    terms_override: list[int] | None = None,
    check_normalized_plaintext: bool = True,
    initial_vector_override: sp.Matrix | None = None,
) -> dict:
    started = time.perf_counter()
    cpu_started = time.process_time()
    stage_started = started
    stage_seconds: dict[str, float] = {}

    def mark(stage: str, message: str) -> None:
        nonlocal stage_started
        now = time.perf_counter()
        if stage_seconds:
            pass
        progress(stage, message)
        stage_started = now

    def finish_stage(name: str) -> None:
        nonlocal stage_started
        now = time.perf_counter()
        stage_seconds[name] = now - stage_started
        stage_started = now

    case_dir.mkdir(parents=True, exist_ok=True)

    mark("INPUT", f"q={q}; term_limit={term_limit}; output={display_path(case_dir)}")
    D = D_q(q) if D_override is None else sp.expand(D_override)
    rho = sp.expand(u * D)
    degree = sp.degree(rho, u)
    if degree != q:
        raise AssertionError(f"unexpected degree rho for q={q}: {degree}")

    finish_stage("input_polynomials")
    mark("G ASSEMBLY", f"building exact {2*q}x{2*q} matrix for w=rho*a-rho_prime*b")

    # G encodes w = rho*a - rho'*b with deg(a),deg(b)<q.
    a_symbols = sp.symbols(f"a0:{q}")
    b_symbols = sp.symbols(f"b0:{q}")
    a_polynomial = sum(a_symbols[index] * u**index for index in range(q))
    b_polynomial = sum(b_symbols[index] * u**index for index in range(q))
    w_polynomial = sp.expand(rho * a_polynomial - sp.diff(rho, u) * b_polynomial)

    G = sp.zeros(2 * q, 2 * q)
    unknowns = list(a_symbols) + list(b_symbols)
    for row in range(2 * q):
        coefficient = w_polynomial.coeff(u, row)
        for column, symbol in enumerate(unknowns):
            G[row, column] = sp.diff(coefficient, symbol)

    finish_stage("G_assembly")
    mark("G DETERMINANT", f"computing det(G) for {2*q}x{2*q} exact matrix")
    determinant_G = sp.Integer(G.det())
    if determinant_G == 0:
        raise AssertionError(f"singular G for q={q}")

    finish_stage("G_determinant")
    progress("G DETERMINANT", f"det(G)={determinant_G}")
    mark("G INVERSION", f"inverting exact {2*q}x{2*q} matrix; this is usually the main linear-algebra stage")
    G_inverse = G.inv()
    finish_stage("G_inversion")
    progress("G INVERSION", "complete")
    mark("U/V/J", "extracting reduction operators and derivative matrix")
    embedding = sp.zeros(2 * q, q)
    for index in range(q):
        embedding[index, index] = 1

    U = G_inverse[:q, :] * embedding
    V = G_inverse[q:, :] * embedding

    derivative_matrix = sp.zeros(q, q)
    for column in range(1, q):
        derivative_matrix[column - 1, column] = column

    exact_split_check = G * sp.Matrix.vstack(U, V) - embedding
    if any(entry != 0 for entry in exact_split_check):
        raise AssertionError(f"G/U/V split failed q={q}")

    finish_stage("UVJ")
    progress("U/V/J", "exact split G*[U;V]=E verified")
    mark("POLE LOWERING", f"reducing {q} shifts one at a time")
    initial_vector = sp.zeros(q, 1) if initial_vector_override is None else initial_vector_override
    if initial_vector.shape != (q, 1):
        raise AssertionError("initial_vector_override must have shape (q,1)")
    if initial_vector_override is None:
        initial_vector[0] = 1

    reduced_columns: list[sp.Matrix] = []
    shift_records: list[list[dict]] = []

    for shift in range(q):
        progress("POLE LOWERING", f"shift {shift}/{q-1}: {shift} lowering step(s)")
        current = initial_vector
        records: list[dict] = []
        for lowering_index in range(shift, 0, -1):
            pole_parameter = n + lowering_index - 1
            certificate_vector = V * current
            reduced = U * current - derivative_matrix * certificate_vector / pole_parameter
            reduced = reduced.applyfunc(sp.cancel)
            records.append(
                {
                    "lowering_index": lowering_index,
                    "pole_parameter": pole_parameter,
                    "input_vector": current,
                    "certificate_vector": certificate_vector,
                    "output_vector": reduced,
                }
            )
            current = reduced

        scale = sp.Integer(1) if shift == 0 else sp.cancel(n / (n + shift))
        reduced_columns.append((scale * current).applyfunc(sp.cancel))
        shift_records.append(records)

    finish_stage("pole_lowering")
    mark("REMAINDER MATRIX", f"assembling X_full ({q}x{q}) and X ({q-1}x{q})")
    X_full = sp.Matrix.hstack(*reduced_columns)
    if any(sp.cancel(X_full[q - 1, column]) != 0 for column in range(q)):
        raise AssertionError(f"expected zero top-degree remainder row q={q}")
    X = X_full[: q - 1, :]

    finish_stage("remainder_assembly")
    mark("KERNEL SOLVE", f"computing exact rank/nullspace of {q-1}x{q} X over Q(n)")
    domain_X = X.to_DM(field=True)
    rank_X = int(domain_X.rank())
    nullspace = domain_X.nullspace().to_Matrix()
    if rank_X != q - 1 or nullspace.shape != (1, q):
        raise AssertionError(
            f"unexpected remainder rank/nullspace q={q}: rank={rank_X}, shape={nullspace.shape}"
        )

    recurrence = primitive_n_vector(list(nullspace[0, :]))
    null_residual = X * recurrence
    if any(sp.cancel(entry) != 0 for entry in null_residual):
        raise AssertionError(f"X*P != 0 q={q}")

    finish_stage("kernel_solve")
    progress("KERNEL SOLVE", f"rank={rank_X}; nullity=1; primitive recurrence extracted")
    mark("RANK WITNESS", f"computing determinant of leading {q-1}x{q-1} minor")
    leading_minor = X[:, : q - 1]
    leading_minor_dm = leading_minor.to_DM(field=True)
    leading_minor_determinant = leading_minor_dm.domain.to_sympy(leading_minor_dm.det())
    if leading_minor_determinant == 0:
        raise AssertionError(f"zero rank-witness minor q={q}")

    finish_stage("rank_witness")
    progress("RANK WITNESS", "nonzero minor confirmed")
    mark("CERTIFICATE", f"assembling {q*(q-1)//2} partial V-contributions into N/rho^{q-2}")

    # Accumulate the stored partial certificates into the common R denominator.
    N = sp.Integer(0)
    partial_rows: list[str] = [
        "shift\tlowering_index\tpole_parameter\tscale\tcertificate_polynomial\tN_contribution"
    ]

    for shift in range(1, q):
        progress(
            "CERTIFICATE",
            f"shift {shift}/{q-1}: adding {len(shift_records[shift])} contribution(s)",
        )
        scale = sp.cancel(recurrence[shift] * n / (n + shift))
        if sp.denom(scale) != 1:
            raise AssertionError(f"nonpolynomial shifted recurrence scale q={q}, r={shift}")

        for record in shift_records[shift]:
            lowering_index = int(record["lowering_index"])
            pole_parameter = record["pole_parameter"]
            certificate_polynomial = vector_to_polynomial(
                record["certificate_vector"], q
            )
            contribution = sp.cancel(
                scale
                * certificate_polynomial
                * rho ** (q - 1 - lowering_index)
                / pole_parameter
            )
            N += contribution
            # Keep the audit trail compact; the executable script deterministically
            # reconstructs the exact vectors and contributions.
            partial_rows.append(
                "\t".join(
                    [
                        str(shift),
                        str(lowering_index),
                        expr_text(pole_parameter),
                        "stored-in-generator",
                        "stored-in-generator",
                        "stored-in-generator",
                    ]
                )
            )

    progress("CERTIFICATE", "all contributions added; canonicalizing numerator")
    N = sp.cancel(N)
    if sp.denom(N) != 1:
        raise AssertionError(f"certificate numerator not polynomial q={q}")
    N_poly = sp.Poly(N, n, u, domain=sp.QQ)
    N = N_poly.as_expr()

    finish_stage("certificate_assembly")
    progress("CERTIFICATE", f"polynomial numerator degrees: deg_n={N_poly.degree(n)}, deg_u={N_poly.degree(u)}")
    mark("TELESCOPING CHECK", "checking cleared polynomial identity exactly")

    # Exact original identity after multiplication by rho^(q-1).
    recurrence_scales: list[sp.Expr] = []
    for shift in range(q):
        scale = sp.cancel(recurrence[shift] * n / (n + shift))
        if sp.denom(scale) != 1:
            raise AssertionError(f"nonpolynomial scale q={q}, shift={shift}")
        recurrence_scales.append(scale)

    rho_poly = sp.Poly(rho, n, u, domain=sp.QQ)
    rho_derivative_poly = sp.Poly(sp.diff(rho, u), n, u, domain=sp.QQ)
    cleared_residual = (
        rho_poly * N_poly.diff(u)
        - sp.Poly(n + q - 2, n, u, domain=sp.QQ)
        * rho_derivative_poly
        * N_poly
    )
    for shift, scale in enumerate(recurrence_scales):
        cleared_residual -= (
            sp.Poly(scale, n, u, domain=sp.QQ)
            * rho_poly ** (q - 1 - shift)
        )
    if not cleared_residual.is_zero:
        raise AssertionError(f"nonzero cleared telescoping residual q={q}")

    finish_stage("telescoping_check")
    progress("TELESCOPING CHECK", "exact residual is zero")
    mark("TERM CHECKS", f"computing independent terms through n={term_limit}")

    # Independent term checks from the multinomial profile formula.
    terms = (
        [profile_count(q, index) for index in range(term_limit + 1)]
        if terms_override is None
        else terms_override[: term_limit + 1]
    )
    if len(terms) != term_limit + 1:
        raise AssertionError("terms_override is shorter than term_limit+1")
    recurrence_checks: list[tuple[int, int]] = []
    for start in range(1, term_limit - q + 2):
        residual = sum(
            int(recurrence[shift].subs(n, start)) * terms[start + shift]
            for shift in range(q)
        )
        recurrence_checks.append((start, residual))
        if residual != 0:
            raise AssertionError(f"recurrence term check failed q={q}, n={start}")

    n0_residual = sum(
        int(recurrence[shift].subs(n, 0)) * terms[shift]
        for shift in range(q)
    )

    finish_stage("term_checks")
    progress("TERM CHECKS", "all recurrence residuals are zero")
    mark("STRING CHECKS", "checking normalized positional strings through three leaves")

    # Literal normalized string grammar checks through three true leaves.
    plaintext_counts = {0: 1}
    plaintext_hashes: dict[int, str] = {}
    plaintext_sections: list[str] = [
        f"q={q} normalized positional strings",
        f"symbols: {TRUE}=true leaf, {FALSE}=empty/false slot, {LEFT}{RIGHT}=layer",
        "every retained layer has at least two occupied slots",
        "",
        "n=0",
        "empty object (count 1)",
        "",
    ]
    for leaves in range(1, 4) if check_normalized_plaintext else ():
        trees = plaintext_trees(q, leaves)
        expected = terms[leaves]
        if len(trees) != expected:
            raise AssertionError(
                f"plaintext/profile mismatch q={q}, n={leaves}: {len(trees)} != {expected}"
            )
        plaintext_counts[leaves] = len(trees)
        encoded = ("\n".join(trees) + "\n").encode("utf-8")
        plaintext_hashes[leaves] = hashlib.sha256(encoded).hexdigest()
        plaintext_sections.extend(
            [
                f"n={leaves} count={len(trees)} sha256(one-per-line)={plaintext_hashes[leaves]}",
                wrap_items(trees).rstrip("\n"),
                "",
            ]
        )

    # q=4 must reproduce the worked recurrence exactly.
    q4_match = None
    if q == 4 and D_override is None:
        expected_q4 = sp.Matrix(
            [
                -8 * (4 * n + 5) * (2 * n + 1) * (4 * n - 1),
                -64 * (n + 1) * (48 * n**2 + 96 * n + 43),
                -6144 * (2 * n + 3) * (n + 2) * (n + 1),
                491 * (n + 3) * (n + 2) * (n + 1),
            ]
        )
        q4_match = all(
            sp.expand(recurrence[index] - expected_q4[index]) == 0
            for index in range(4)
        )
        if not q4_match:
            raise AssertionError("q=4 recurrence failed worked-example comparison")

    finish_stage("string_checks")
    progress("STRING CHECKS", "counts agree with multinomial formula")
    mark("SERIALIZATION", "writing exact JSON object graph and audit sidecars")

    # Write case artifacts.
    (case_dir / "G.tsv").write_text(matrix_dense_tsv(G), encoding="utf-8")
    (case_dir / "U.tsv").write_text(matrix_dense_tsv(U), encoding="utf-8")
    (case_dir / "V.tsv").write_text(matrix_dense_tsv(V), encoding="utf-8")
    (case_dir / "J.tsv").write_text(matrix_dense_tsv(derivative_matrix), encoding="utf-8")
    (case_dir / "X_remainders_sparse.tsv").write_text(
        matrix_sparse_tsv(X, "remainder_degree", "shift"), encoding="utf-8"
    )
    (case_dir / "partial_certificates.tsv").write_text(
        "\n".join(partial_rows) + "\n", encoding="utf-8"
    )
    (case_dir / "plaintext_n0_n3.txt").write_text(
        "\n".join(plaintext_sections).rstrip() + "\n", encoding="utf-8"
    )

    recurrence_lines = [
        f"q = {q}",
        f"D_q(u) = {expr_text(D)}",
        f"rho_q(u) = {expr_text(rho)}",
        "",
        "P-recurrence (valid from n>=1):",
    ]
    for shift, polynomial in enumerate(recurrence):
        recurrence_lines.append(f"P_{shift}(n) = {expr_text(polynomial, factor=True)}")
    recurrence_lines.extend(
        [
            "",
            "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
            f"n=0 separate residual = {n0_residual}",
            "",
            f"certificate R(n,u) = N(n,u) / rho(u)^{q-2}",
            f"deg_n N = {N_poly.degree(n)}",
            f"deg_u N = {N_poly.degree(u)}",
            "",
            "N(n,u) =",
            expr_text(N),
            "",
            "rank witness: determinant of leading (q-1)x(q-1) X minor =",
            sp.sstr(sp.cancel(leading_minor_determinant), order="lex"),
        ]
    )
    (case_dir / "recurrence_and_certificate.txt").write_text(
        "\n".join(recurrence_lines) + "\n", encoding="utf-8"
    )

    terms_lines = [
        "n\ta_q(n)",
        *[f"{index}\t{value}" for index, value in enumerate(terms)],
        "",
        "recurrence_start_n\tresidual",
        *[f"{start}\t{residual}" for start, residual in recurrence_checks],
        f"0\t{n0_residual}\t(separate check)",
    ]
    (case_dir / "terms_and_recurrence_checks.tsv").write_text(
        "\n".join(terms_lines) + "\n", encoding="utf-8"
    )

    elapsed = time.perf_counter() - started
    cpu_elapsed = time.process_time() - cpu_started
    peak_rss_kb = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    finish_stage("serialization_sidecars")
    result = {
        "format": "RELAY-CT-annotated-case-v0.1",
        "objects": {
            "input_polynomials": {"D_q": expr_text(D), "rho_q": expr_text(rho)},
            "matrices": {
                "G": {"shape": [G.rows, G.cols], "entries": matrix_json(G)},
                "G_inverse": {"shape": [G_inverse.rows, G_inverse.cols], "entries": matrix_json(G_inverse)},
                "embedding_E": {"shape": [embedding.rows, embedding.cols], "entries": matrix_json(embedding)},
                "U": {"shape": [U.rows, U.cols], "entries": matrix_json(U)},
                "V": {"shape": [V.rows, V.cols], "entries": matrix_json(V)},
                "J": {"shape": [derivative_matrix.rows, derivative_matrix.cols], "entries": matrix_json(derivative_matrix)},
                "X_full": {"shape": [X_full.rows, X_full.cols], "entries": matrix_json(X_full)},
                "X": {"shape": [X.rows, X.cols], "entries": matrix_json(X)},
            },
            "p_recurrence": {
                "order": q - 1,
                "coefficients": [expr_text(polynomial) for polynomial in recurrence],
                "identity": "sum_{r=0}^{q-1} P_r(n) a(n+r) = 0",
                "valid_from_n": 1,
            },
            "rational_certificate": {
                "numerator_N": expr_text(N),
                "denominator_base": expr_text(rho),
                "denominator_power": q - 2,
                "formula": "R(n,u)=N(n,u)/rho(u)^(q-2)",
            },
        },
        "identities": {
            "G_definition": "coeff(w)=G*[coeff(a);coeff(b)] for w=rho*a-rho_prime*b",
            "G_inverse": "G*G_inverse=I",
            "GUV_split": "G*[U;V]=E",
            "pole_lowering": "w/rho^(m+1)=(U-JV/m)w/rho^m+d((Vw)/(m rho^m))/du",
            "kernel": "X*P=0",
            "certificate": "sum_r P_r(n)H_{n+r}=d(R H_n)/du",
        },
        "statistics": {
            "q": q,
            "polynomial_space_dimension": q,
            "G_domain_dimension": 2*q,
            "G_codomain_dimension": 2*q,
            "remainder_space_dimension": q-1,
            "shift_count": q,
            "partial_certificate_count": q*(q-1)//2,
            "term_limit": term_limit,
            "wall_seconds": elapsed,
            "cpu_seconds": cpu_elapsed,
            "peak_rss_kb": peak_rss_kb,
            "stage_seconds": stage_seconds,
        },
        "q": q,
        "D": expr_text(D),
        "rho": expr_text(rho),
        "G": {
            "rows": 2 * q,
            "columns": 2 * q,
            "determinant": int(determinant_G),
            "invertible": True,
        },
        "remainder_matrix": {
            "rows": q - 1,
            "columns": q,
            "rank": rank_X,
            "nullity": q - rank_X,
            "leading_minor_determinant": expr_text(
                leading_minor_determinant, factor=True
            ),
        },
        "recurrence": [expr_text(polynomial) for polynomial in recurrence],
        "recurrence_degree": max(int(sp.degree(polynomial, n)) for polynomial in recurrence),
        "recurrence_valid_from": 1,
        "n0_residual": int(n0_residual),
        "certificate": {
            "denominator_power_of_rho": q - 2,
            "degree_n_N": int(N_poly.degree(n)),
            "degree_u_N": int(N_poly.degree(u)),
            "N": expr_text(N),
        },
        "terms": terms,
        "plaintext_counts": {str(key): value for key, value in plaintext_counts.items()},
        "plaintext_hashes": {str(key): value for key, value in plaintext_hashes.items()},
        "worked_q4_recurrence_match": q4_match,
        "checks": {
            "G_invertible": True,
            "GUV_split_exact": True,
            "last_remainder_row_zero": True,
            "remainder_rank_q_minus_1": True,
            "nullspace_dimension_one": True,
            "rank_witness_minor_nonzero": True,
            "X_times_P_zero": True,
            "certificate_numerator_polynomial": True,
            "cleared_telescoping_identity_zero": True,
            "multinomial_recurrence_checks_zero": True,
            "plaintext_counts_match_multinomial_n0_n3": check_normalized_plaintext,
        },
        "elapsed_seconds": elapsed,
    }
    (case_dir / "case.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    finish_stage("json_write")
    progress("FAST CORE", f"q={q}; wall={elapsed:.3f}s; peak_rss={peak_rss_kb} KB; base blob written")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate one exact RELAY G,U,V certificate data blob."
    )
    parser.add_argument("q", type=int, help="single arity q >= 2")
    parser.add_argument("--term-limit", type=int, default=24)
    parser.add_argument("--output", type=Path, default=Path("runs"))
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="skip the separate post-generation checker (generation assertions remain active)",
    )
    args = parser.parse_args()
    if args.q < 2:
        raise SystemExit("require q >= 2")

    case_dir = args.output.resolve() / f"q{args.q}"
    if case_dir.exists():
        shutil.rmtree(case_dir)

    result = build_case(args.q, case_dir, args.term_limit)

    if args.skip_validate:
        progress("VALIDATION", "SKIPPED by --skip-validate")
    else:
        progress("VALIDATION", "running independent checker from emitted JSON")
        from check_case import validate_case
        report = validate_case(case_dir / "case.json")
        (case_dir / "validation.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        progress("VALIDATION", f"PASS: {report['passed_checks']}/{report['total_checks']} checks")

    checksum_lines = []
    for path in sorted(case_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            checksum_lines.append(f"{sha256(path)}  {path.relative_to(case_dir)}")
    (case_dir / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    progress("OUTPUT", display_path(case_dir))


if __name__ == "__main__":
    main()
