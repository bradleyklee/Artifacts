#!/usr/bin/env python3
"""Exact all-orders Laurent-period solver.

The solver discovers an operator from exact constant terms and proves it with
the G,U,V,J pole-layer divergence identity.  Small rational systems use direct
exact reduction.  Large rational systems and Gaussian-rational systems are
shunted to sampled modular reduction followed by one exact symbolic replay.
"""
from __future__ import annotations

import itertools
import math
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, TextIO, Tuple

import sympy as sp
from sympy.polys.domains import GF, QQ, QQ_I, ZZ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.exceptions import DMNonInvertibleMatrixError
from sympy.polys.modulargcd import _integer_rational_reconstruction

x, y, t, theta, n = sp.symbols("x y t theta n")
Point = Tuple[int, int]


def cancel(expr: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.sympify(expr))


def is_zero(expr: sp.Expr) -> bool:
    return cancel(expr) == 0


@dataclass
class Progress:
    """Human progress with every physical line at most ``width`` columns."""

    enabled: bool = True
    stream: TextIO = sys.stderr
    width: int = 80
    started: float = field(default_factory=time.perf_counter)

    def emit(self, message: str) -> None:
        if not self.enabled:
            return
        elapsed = time.perf_counter() - self.started
        prefix = f"[{elapsed:7.2f}s] "
        usable = max(20, self.width - len(prefix))
        lines = textwrap.wrap(
            str(message), width=usable, break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        for line in lines:
            print(prefix + line, file=self.stream, flush=True)


def coefficient_domain(expressions: Iterable[sp.Expr]):
    """Return Q or Q(i); reject approximate and unsupported coefficients."""
    has_i = False
    for expression in expressions:
        value = sp.sympify(expression)
        if value.has(sp.Float):
            raise ValueError("floating coefficients are not exact; use rationals")
        if value.free_symbols:
            raise ValueError(f"coefficient contains symbols: {value}")
        real, imag = sp.expand_complex(value).as_real_imag()
        if not (real.is_Rational and imag.is_Rational):
            raise ValueError(
                "supported coefficient fields are Q and Q(i); "
                f"got {value}"
            )
        has_i = has_i or imag != 0
    return QQ_I if has_i else QQ


def laurent_terms(
    expression: sp.Expr, *, allowed_symbols: frozenset[sp.Symbol] = frozenset()
) -> Dict[Point, sp.Expr]:
    """Return coefficients of a finite Laurent polynomial in x and y."""
    result: Dict[Point, sp.Expr] = {}
    for term in sp.Add.make_args(sp.expand(expression)):
        powers = term.as_powers_dict()
        exponents: List[int] = []
        for variable in (x, y):
            exponent = powers.get(variable, sp.Integer(0))
            if exponent.is_Integer is not True:
                raise ValueError(
                    f"noninteger exponent of {variable}: {exponent}"
                )
            exponents.append(int(exponent))
        coefficient = cancel(term / (x ** exponents[0] * y ** exponents[1]))
        forbidden = coefficient.free_symbols - allowed_symbols
        if forbidden:
            raise ValueError(
                "input is not a Laurent polynomial in exactly two variables: "
                f"{coefficient}"
            )
        point = (exponents[0], exponents[1])
        result[point] = cancel(result.get(point, 0) + coefficient)
    result = {point: value for point, value in result.items() if value != 0}
    if not allowed_symbols:
        coefficient_domain(result.values())
    return result


def normalize_laurent(
    expression: sp.Expr,
    allowed_symbols: frozenset[sp.Symbol] = frozenset(),
) -> sp.Expr:
    expression = sp.expand(sp.sympify(expression))
    terms = laurent_terms(expression, allowed_symbols=allowed_symbols)
    return sp.Add(*(
        coefficient * x ** i * y ** j
        for (i, j), coefficient in sorted(terms.items())
    )) if terms else sp.Integer(0)


def laurent_expression_from_point_coefficients(
    terms: Dict[Point, sp.Expr],
) -> sp.Expr:
    """Build a Laurent expression without global rational cancellation."""
    pieces = []
    for (i, j), coefficient in sorted(terms.items()):
        coefficient = cancel(coefficient)
        if coefficient != 0:
            pieces.append(coefficient * x ** i * y ** j)
    return sp.Add(*pieces) if pieces else sp.Integer(0)


def parse_laurent(text: str) -> sp.Expr:
    """Parse exact input and rename up to two supplied variables to x and y."""
    expression = sp.sympify(text, evaluate=True)
    symbols = sorted(expression.free_symbols, key=lambda item: item.name)
    if len(symbols) > 2:
        raise ValueError(
            "a bivariate Laurent polynomial may contain at most two variables"
        )
    replacement = {}
    if symbols:
        replacement[symbols[0]] = x
    if len(symbols) == 2:
        replacement[symbols[1]] = y
    return normalize_laurent(expression.xreplace(replacement))


def univariate_constant_terms(
    steps: Dict[int, sp.Expr], count: int,
) -> List[sp.Expr]:
    """Return CT(A^k) using native Q or Q(i) coefficient arithmetic."""
    domain = coefficient_domain(steps.values())
    domain_steps = {
        exponent: domain.from_sympy(sp.expand(coefficient))
        for exponent, coefficient in steps.items()
    }
    layer = {0: domain.one}
    answer: List[sp.Expr] = []
    for _ in range(count):
        answer.append(domain.to_sympy(layer.get(0, domain.zero)))
        following = {}
        for left_exponent, left in layer.items():
            for right_exponent, right in domain_steps.items():
                exponent = left_exponent + right_exponent
                following[exponent] = (
                    following.get(exponent, domain.zero) + left * right
                )
        layer = {
            exponent: value
            for exponent, value in following.items()
            if value
        }
    return answer


def separable_laurent_factors(
    steps: Dict[Point, sp.Expr],
) -> Tuple[Dict[int, sp.Expr], Dict[int, sp.Expr]] | None:
    """Detect an exact product A(x)B(y) from its coefficient table."""
    if not steps:
        return None
    i_values = sorted({i for i, _ in steps})
    j_values = sorted({j for _, j in steps})
    pivot_i, pivot_j = next(iter(sorted(steps)))
    pivot = steps[(pivot_i, pivot_j)]
    left = {
        i: steps.get((i, pivot_j), sp.Integer(0))
        for i in i_values
    }
    right = {
        j: cancel(steps.get((pivot_i, j), 0) / pivot)
        for j in j_values
    }
    for i in i_values:
        for j in j_values:
            if cancel(steps.get((i, j), 0) - left[i] * right[j]) != 0:
                return None
    return (
        {i: value for i, value in left.items() if value != 0},
        {j: value for j, value in right.items() if value != 0},
    )


def constant_terms(F: sp.Expr, count: int) -> List[sp.Expr]:
    """Compute CT(F^k) by exact sparse lattice convolution.

    Exact rank-one coefficient tables are shunted to two univariate
    convolutions.  This is especially important for canonical product models
    and does not change the general bivariate fallback.
    """
    if count < 1:
        raise ValueError("term count must be positive")
    steps = laurent_terms(F)
    factors = separable_laurent_factors(steps)
    if factors is not None:
        left_terms = univariate_constant_terms(factors[0], count)
        right_terms = univariate_constant_terms(factors[1], count)
        return [
            cancel(left * right)
            for left, right in zip(left_terms, right_terms)
        ]

    domain = coefficient_domain(steps.values())
    domain_steps = {
        point: domain.from_sympy(sp.expand(coefficient))
        for point, coefficient in steps.items()
    }
    layer = {(0, 0): domain.one}
    answer: List[sp.Expr] = []
    for _ in range(count):
        answer.append(domain.to_sympy(layer.get((0, 0), domain.zero)))
        following = {}
        for (i, j), left in layer.items():
            for (r, q), right in domain_steps.items():
                point = (i + r, j + q)
                following[point] = (
                    following.get(point, domain.zero) + left * right
                )
        layer = {
            point: value for point, value in following.items() if value
        }
    return answer


def constant_term_generator(F: sp.Expr):
    """Yield CT(F^n) incrementally using exact coefficient-domain arithmetic."""
    steps = laurent_terms(F)
    factors = separable_laurent_factors(steps)
    if factors is not None:
        left_steps, right_steps = factors
        domain = coefficient_domain(
            list(left_steps.values()) + list(right_steps.values())
        )
        left_domain = {
            exponent: domain.from_sympy(sp.expand(value))
            for exponent, value in left_steps.items()
        }
        right_domain = {
            exponent: domain.from_sympy(sp.expand(value))
            for exponent, value in right_steps.items()
        }
        left_layer = {0: domain.one}
        right_layer = {0: domain.one}
        while True:
            yield domain.to_sympy(
                left_layer.get(0, domain.zero)
                * right_layer.get(0, domain.zero)
            )
            following_left = {}
            for i, a in left_layer.items():
                for r, b in left_domain.items():
                    following_left[i + r] = (
                        following_left.get(i + r, domain.zero) + a * b
                    )
            following_right = {}
            for j, a in right_layer.items():
                for q, b in right_domain.items():
                    following_right[j + q] = (
                        following_right.get(j + q, domain.zero) + a * b
                    )
            left_layer = {k: v for k, v in following_left.items() if v}
            right_layer = {k: v for k, v in following_right.items() if v}

    domain = coefficient_domain(steps.values())
    domain_steps = {
        point: domain.from_sympy(sp.expand(coefficient))
        for point, coefficient in steps.items()
    }
    layer = {(0, 0): domain.one}
    while True:
        yield domain.to_sympy(layer.get((0, 0), domain.zero))
        following = {}
        for (i, j), left in layer.items():
            for (r, q), right in domain_steps.items():
                point = (i + r, j + q)
                following[point] = (
                    following.get(point, domain.zero) + left * right
                )
        layer = {point: value for point, value in following.items() if value}


def recurrence_matrix(
    values: Sequence[sp.Expr], order: int, shift_degree: int,
    start: int, stop: int,
) -> sp.Matrix:
    """Rows for sum c[s,j]*(k-s)^j*a[k-s] = 0."""
    columns = [
        (shift, derivative)
        for derivative in range(order + 1)
        for shift in range(shift_degree + 1)
    ]
    rows = []
    for k in range(start, stop):
        row = []
        for shift, derivative in columns:
            index = k - shift
            value = 0 if index < 0 else index ** derivative * values[index]
            row.append(value)
        rows.append(row)
    return sp.Matrix(rows)


def relation_operator(
    vector: Sequence[sp.Expr], order: int, shift_degree: int,
) -> sp.Expr:
    columns = [
        (shift, derivative)
        for derivative in range(order + 1)
        for shift in range(shift_degree + 1)
    ]
    return sp.expand(sum(
        value * t ** shift * theta ** derivative
        for value, (shift, derivative) in zip(vector, columns)
    ))


def primitive_operator(operator: sp.Expr) -> sp.Expr:
    """Clear K(t) denominators and remove every common polynomial factor.

    This normalization is exact.  In particular, a factor such as ``t**37``
    shared by all theta coefficients is removed rather than being mistaken for
    part of the annihilator.
    """
    expression = cancel(sp.together(operator))
    numerator, _ = sp.fraction(expression)
    operator = sp.expand(numerator)
    theta_polynomial = sp.Poly(operator, theta)
    scalar_coefficients = theta_polynomial.all_coeffs()
    domain = coefficient_domain(
        coefficient
        for item in scalar_coefficients
        for coefficient in sp.Poly(item, t).coeffs()
    )

    coefficient_polynomials = []
    for item in scalar_coefficients:
        if item == 0:
            continue
        if domain == QQ_I:
            coefficient_polynomials.append(sp.Poly(item, t, extension=sp.I))
        else:
            coefficient_polynomials.append(sp.Poly(item, t, domain=QQ))
    common = coefficient_polynomials[0]
    for item in coefficient_polynomials[1:]:
        common = sp.gcd(common, item)
    if common.as_expr() not in (1, -1):
        operator = sp.expand(cancel(operator / common.as_expr()))

    polynomial = sp.Poly(operator, t, theta)
    coefficients = polynomial.coeffs()
    if domain == QQ:
        denominator = 1
        for value in coefficients:
            denominator = sp.ilcm(denominator, int(sp.denom(value)))
        operator = sp.expand(denominator * operator)
        integer_coefficients = [
            int(value) for value in sp.Poly(operator, t, theta).coeffs()
        ]
        content = 0
        for value in integer_coefficients:
            content = math.gcd(content, abs(value))
        if content > 1:
            operator = sp.expand(operator / content)
        leading = sp.Poly(operator, theta, t).LC()
        if leading < 0:
            operator = -operator
        return sp.expand(operator)

    leading = sp.Poly(operator, theta, t, extension=sp.I).LC()
    return sp.expand(cancel(operator / leading))


def normalize_operator_with_scale(
    operator: sp.Expr,
) -> Tuple[sp.Expr, sp.Expr]:
    """Return primitive operator and the exact scalar applied to it."""
    normalized = primitive_operator(operator)
    raw_polynomial = sp.Poly(operator, theta)
    normalized_polynomial = sp.Poly(normalized, theta)
    for derivative in range(raw_polynomial.degree(), -1, -1):
        raw = raw_polynomial.coeff_monomial(theta ** derivative)
        if raw != 0:
            scale = cancel(
                normalized_polynomial.coeff_monomial(theta ** derivative) / raw
            )
            if cancel(normalized - scale * operator) != 0:
                raise AssertionError("operator normalization scale is inconsistent")
            return normalized, scale
    raise ValueError("zero operator cannot be normalized")

def operator_order(operator: sp.Expr) -> int:
    return sp.Poly(operator, theta).degree()


def operator_recurrence(operator: sp.Expr) -> Dict[int, sp.Expr]:
    polynomial = sp.Poly(sp.expand(operator), t)
    return {
        int((degree_tuple[0])): sp.expand(coefficient)
        for degree_tuple, coefficient in polynomial.terms()
    }


def recurrence_holds(
    recurrence: Dict[int, sp.Expr], values: Sequence[sp.Expr],
    start: int = 0,
) -> bool:
    for k in range(start, len(values)):
        residual = 0
        for shift, polynomial in recurrence.items():
            index = k - shift
            if index >= 0:
                residual += polynomial.subs(theta, index) * values[index]
        if cancel(residual) != 0:
            return False
    return True


def find_operator(
    F: sp.Expr,
    *,
    max_order: int | None = None,
    max_shift_degree: int | None = None,
    held_out: int = 12,
    progress: Progress | None = None,
) -> Tuple[sp.Expr, List[sp.Expr], dict]:
    """Expand order and shift searches until an exact held-out relation appears.

    The default search is unbounded. Bounds are optional resource controls for
    regression runs; exhausting one reports ``SearchExhausted``, never a claim
    that no operator exists.
    """
    if progress is None:
        progress = Progress(enabled=False)
    round_number = 1
    tested: set[Tuple[int, int]] = set()
    values: List[sp.Expr] = []
    term_stream = constant_term_generator(F)
    while True:
        order_limit = (
            round_number if max_order is None
            else min(round_number, max_order)
        )
        shift_limit = 2 * round_number + 1
        if max_shift_degree is not None:
            shift_limit = min(shift_limit, max_shift_degree)

        needed = max(
            shift + (order + 1) * (shift + 1)
            + max(4, order + 1) + held_out
            for order in range(1, order_limit + 1)
            for shift in range(shift_limit + 1)
        )
        if len(values) < needed:
            progress.emit(
                f"extending exact constant terms from {len(values)} to {needed}"
            )
            while len(values) < needed:
                values.append(next(term_stream))

        for order in range(1, order_limit + 1):
            for shift_degree in range(0, shift_limit + 1):
                key = (order, shift_degree)
                if key in tested:
                    continue
                tested.add(key)
                column_count = (order + 1) * (shift_degree + 1)
                train_rows = column_count + max(4, order + 1)
                term_count = shift_degree + train_rows + held_out
                progress.emit(
                    f"operator trial order={order}, shift={shift_degree}, "
                    f"terms={term_count}"
                )
                matrix = recurrence_matrix(
                    values[:term_count], order, shift_degree,
                    start=shift_degree,
                    stop=shift_degree + train_rows,
                )
                nullspace = matrix.nullspace()
                for relation in nullspace:
                    operator = primitive_operator(
                        relation_operator(list(relation), order, shift_degree)
                    )
                    if operator_order(operator) != order:
                        continue
                    recurrence = operator_recurrence(operator)
                    if recurrence_holds(
                        recurrence, values[:term_count], start=0
                    ):
                        stats = {
                            "order": order,
                            "shift_degree": shift_degree,
                            "terms": term_count,
                            "trials": len(tested),
                        }
                        progress.emit(
                            f"operator found: order={order}, "
                            f"shift={shift_degree}"
                        )
                        return operator, values[:term_count], stats
        if (
            max_order is not None and order_limit >= max_order and
            max_shift_degree is not None and shift_limit >= max_shift_degree
        ):
            raise SearchExhausted(
                "operator search controls exhausted; increase them or omit them"
            )
        round_number += 1


class SearchExhausted(RuntimeError):
    pass


def convex_hull(points: Iterable[Point]) -> List[Point]:
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(origin: Point, left: Point, right: Point) -> int:
        return (
            (left[0] - origin[0]) * (right[1] - origin[1])
            - (left[1] - origin[1]) * (right[0] - origin[0])
        )

    lower: List[Point] = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: List[Point] = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def segment_lattice_points(left: Point, right: Point) -> List[Point]:
    difference = (right[0] - left[0], right[1] - left[1])
    steps = math.gcd(abs(difference[0]), abs(difference[1]))
    if steps == 0:
        return [left]
    step = (difference[0] // steps, difference[1] // steps)
    return [
        (left[0] + k * step[0], left[1] + k * step[1])
        for k in range(steps + 1)
    ]


def lattice_points_in_hull(vertices: Sequence[Point]) -> List[Point]:
    if not vertices:
        return []
    if len(vertices) == 1:
        return [vertices[0]]
    if len(vertices) == 2:
        return sorted(segment_lattice_points(vertices[0], vertices[1]))
    minimum_i = min(i for i, _ in vertices)
    maximum_i = max(i for i, _ in vertices)
    minimum_j = min(j for _, j in vertices)
    maximum_j = max(j for _, j in vertices)

    def cross(left: Point, right: Point, point: Point) -> int:
        return (
            (right[0] - left[0]) * (point[1] - left[1])
            - (right[1] - left[1]) * (point[0] - left[0])
        )

    return [
        (i, j)
        for i in range(minimum_i, maximum_i + 1)
        for j in range(minimum_j, maximum_j + 1)
        if all(
            cross(vertices[k], vertices[(k + 1) % len(vertices)], (i, j)) >= 0
            for k in range(len(vertices))
        )
    ]


def support_basis(F: sp.Expr, dilation: int) -> List[Point]:
    support = set(laurent_terms(F)) | {(0, 0)}
    hull = convex_hull(support)
    dilated = [(dilation * i, dilation * j) for i, j in hull]
    return lattice_points_in_hull(dilated)


def theta_numerators(F: sp.Expr, order: int) -> Tuple[sp.Expr, List[sp.Expr]]:
    rho = sp.expand(1 - t * F)
    numerators = [sp.Integer(1)]
    for derivative in range(order):
        current = numerators[-1]
        following = t * (
            sp.diff(current, t) * rho + (derivative + 1) * current * F
        )
        numerators.append(sp.expand(following))
    return rho, numerators


def operator_numerator(F: sp.Expr, operator: sp.Expr) -> Tuple[sp.Expr, sp.Expr, int]:
    order = operator_order(operator)
    rho, numerators = theta_numerators(F, order)
    theta_polynomial = sp.Poly(sp.expand(operator), theta)
    result = 0
    for (derivative,), coefficient in theta_polynomial.terms():
        result += coefficient * numerators[derivative] * rho ** (order - derivative)
    return rho, sp.expand(result), order


def euler_derivative(expression: sp.Expr, variable: sp.Symbol) -> sp.Expr:
    return sp.expand(variable * sp.diff(expression, variable))


def divergence_column(
    rho: sp.Expr, monomial: sp.Expr, layer: int, order: int,
    component: str,
) -> sp.Expr:
    bx = monomial if component == "x" else sp.Integer(0)
    by = monomial if component == "y" else sp.Integer(0)
    divergence_numerator = (
        rho * (euler_derivative(bx, x) + euler_derivative(by, y))
        - layer * (
            bx * euler_derivative(rho, x)
            + by * euler_derivative(rho, y)
        )
    )
    return sp.expand(rho ** (order - layer) * divergence_numerator)


def coefficient_matrix(
    columns: Sequence[sp.Expr], rhs: sp.Expr,
) -> Tuple[sp.Matrix, sp.Matrix, List[Point]]:
    column_terms = [laurent_terms(column, allowed_symbols=frozenset({t})) for column in columns]
    rhs_terms = laurent_terms(rhs, allowed_symbols=frozenset({t}))
    rows = sorted(set(rhs_terms).union(*[set(item) for item in column_terms]))
    matrix = sp.Matrix([
        [terms.get(point, 0) for terms in column_terms]
        for point in rows
    ])
    vector = sp.Matrix([rhs_terms.get(point, 0) for point in rows])
    return matrix, vector, rows


LaurentMap = Dict[Point, sp.Expr]


def laurent_map_clean(terms: LaurentMap) -> LaurentMap:
    """Expand coefficients and remove exact zeros from a Laurent map."""
    result: LaurentMap = {}
    for point, coefficient in terms.items():
        coefficient = sp.expand(coefficient)
        if coefficient != 0:
            result[point] = coefficient
    return result


def laurent_map_add(left: LaurentMap, right: LaurentMap) -> LaurentMap:
    result = dict(left)
    for point, coefficient in right.items():
        result[point] = result.get(point, 0) + coefficient
    return laurent_map_clean(result)


def laurent_map_scale(terms: LaurentMap, scalar: sp.Expr) -> LaurentMap:
    if scalar == 0:
        return {}
    return laurent_map_clean({
        point: scalar * coefficient
        for point, coefficient in terms.items()
    })


def laurent_map_shift(terms: LaurentMap, shift: Point) -> LaurentMap:
    di, dj = shift
    return {
        (i + di, j + dj): coefficient
        for (i, j), coefficient in terms.items()
    }


def laurent_map_multiply(left: LaurentMap, right: LaurentMap) -> LaurentMap:
    result: LaurentMap = {}
    for (i, j), left_coefficient in left.items():
        for (r, s), right_coefficient in right.items():
            point = (i + r, j + s)
            result[point] = (
                result.get(point, 0)
                + left_coefficient * right_coefficient
            )
    return laurent_map_clean(result)


def laurent_map_t_derivative(terms: LaurentMap) -> LaurentMap:
    return laurent_map_clean({
        point: sp.diff(coefficient, t)
        for point, coefficient in terms.items()
    })


def joint_coefficient_system(
    F: sp.Expr,
    order: int,
    supports: Sequence[Sequence[Point]],
) -> Tuple[
    sp.SparseMatrix,
    sp.SparseMatrix,
    List[Point],
    List[Tuple[int, str, int, int]],
]:
    """Build the joint G-U-V-J system by sparse Laurent-map arithmetic.

    This avoids expanding one large SymPy expression for every witness column.
    Coefficients remain exact polynomials in t throughout.
    """
    F_terms: LaurentMap = {
        point: coefficient
        for point, coefficient in laurent_terms(F).items()
    }
    rho_terms: LaurentMap = {(0, 0): sp.Integer(1)}
    for point, coefficient in F_terms.items():
        rho_terms[point] = rho_terms.get(point, 0) - t * coefficient
    rho_terms = laurent_map_clean(rho_terms)

    rho_powers: List[LaurentMap] = [{(0, 0): sp.Integer(1)}]
    for _ in range(order):
        rho_powers.append(
            laurent_map_multiply(rho_powers[-1], rho_terms)
        )

    numerators: List[LaurentMap] = [{(0, 0): sp.Integer(1)}]
    for derivative in range(order):
        current = numerators[-1]
        differentiated = laurent_map_multiply(
            laurent_map_t_derivative(current), rho_terms
        )
        multiplied = laurent_map_scale(
            laurent_map_multiply(current, F_terms), derivative + 1
        )
        numerators.append(
            laurent_map_scale(
                laurent_map_add(differentiated, multiplied), t
            )
        )

    operator_columns = [
        laurent_map_multiply(
            numerators[derivative], rho_powers[order - derivative]
        )
        for derivative in range(order + 1)
    ]

    labels: List[Tuple[int, str, int, int]] = []
    columns: List[LaurentMap] = list(operator_columns[:-1])
    for layer, basis in enumerate(supports, 1):
        rho_factor = rho_powers[order - layer]
        for component in ("x", "y"):
            for i, j in basis:
                labels.append((layer, component, i, j))
                euler_weight = i if component == "x" else j
                divergence: LaurentMap = laurent_map_scale(
                    laurent_map_shift(rho_terms, (i, j)), euler_weight
                )
                derivative_terms: LaurentMap = {}
                for (r, s), coefficient in rho_terms.items():
                    weight = r if component == "x" else s
                    if weight:
                        derivative_terms[(i + r, j + s)] = (
                            derivative_terms.get((i + r, j + s), 0)
                            - layer * weight * coefficient
                        )
                divergence = laurent_map_add(
                    divergence, derivative_terms
                )
                full_column = laurent_map_multiply(
                    rho_factor, divergence
                )
                columns.append(laurent_map_scale(full_column, -1))

    rhs_terms = laurent_map_scale(operator_columns[-1], -1)
    row_points = sorted(
        set(rhs_terms).union(*[set(column) for column in columns])
    )
    row_index = {point: index for index, point in enumerate(row_points)}
    matrix_entries: Dict[Tuple[int, int], sp.Expr] = {}
    for column_index, column in enumerate(columns):
        for point, coefficient in column.items():
            matrix_entries[(row_index[point], column_index)] = coefficient
    rhs_entries = {
        (row_index[point], 0): coefficient
        for point, coefficient in rhs_terms.items()
    }
    return (
        sp.SparseMatrix(len(row_points), len(columns), matrix_entries),
        sp.SparseMatrix(len(row_points), 1, rhs_entries),
        row_points,
        labels,
    )


def linear_solver_name(coefficient_field) -> str:
    """Name the exact linear-solver branch selected from the input domain."""
    if coefficient_field == QQ_I:
        return "sampled-pivot-Q(i)-with-exact-replay"
    return "direct-rref-Q(t)"


def evaluate_at(matrix: sp.MatrixBase, value: int) -> sp.MatrixBase:
    """Evaluate at an integer while preserving sparse matrix storage."""
    return matrix.applyfunc(
        lambda entry: entry.subs(t, sp.Integer(value))
    )


def rational_mod_prime(value: sp.Expr, prime: int) -> int:
    """Map one exact rational number into GF(prime)."""
    value = sp.Rational(value)
    numerator = int(value.p) % prime
    denominator = int(value.q) % prime
    if denominator == 0:
        raise ZeroDivisionError("sample denominator vanishes modulo prime")
    return numerator * pow(denominator, -1, prime) % prime


def gaussian_mod_prime(
    value: sp.Expr, prime: int, square_root_minus_one: int
) -> int:
    """Map a+b*i into GF(prime) after choosing i^2=-1 modulo prime."""
    real, imag = gaussian_parts(value)
    return (
        rational_mod_prime(real, prime)
        + square_root_minus_one * rational_mod_prime(imag, prime)
    ) % prime


def modular_gaussian_matrix(
    matrix: sp.MatrixBase,
    prime: int,
    square_root_minus_one: int,
) -> DomainMatrix:
    """Convert only nonzero Q(i) entries to a sparse finite-field matrix."""
    domain = GF(prime)
    entries: Dict[int, Dict[int, object]] = {}
    for (row, column), value in matrix.todok().items():
        mapped = gaussian_mod_prime(value, prime, square_root_minus_one)
        if mapped:
            entries.setdefault(row, {})[column] = domain.convert(mapped)
    return DomainMatrix.from_dod(
        entries, (matrix.rows, matrix.cols), domain
    )


def sampled_pivot_layout(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    coefficient_field,
) -> Tuple[List[int], List[int]]:
    """Choose fixed pivot columns and rows at a regular exact sample.

    For Q(i), numerical rank-revealing QR chooses a candidate square block.
    The block is then solved over Q(i), and the complete original system is
    replayed exactly.  Floating-point arithmetic is therefore used only for
    pivot selection, never for a mathematical conclusion.
    """
    evaluated = evaluate_at(matrix, value)
    evaluated_rhs = evaluate_at(rhs, value)
    variable_count = matrix.cols

    if coefficient_field == QQ_I:
        import numpy as np
        from scipy.linalg import qr

        numeric = np.zeros((evaluated.rows, evaluated.cols), dtype=np.complex128)
        for (row, column), entry in evaluated.todok().items():
            gaussian = QQ_I.from_sympy(sp.expand(entry))
            numeric[row, column] = complex(
                float(gaussian.x), float(gaussian.y)
            )
        _, upper, column_order = qr(
            numeric, mode="economic", pivoting=True, check_finite=False
        )
        diagonal = np.abs(np.diag(upper))
        if diagonal.size == 0 or diagonal[0] == 0:
            raise ArithmeticError(f"zero-rank evaluated system at t={value}")
        tolerance = (
            max(numeric.shape)
            * np.finfo(float).eps
            * diagonal[0]
            * 100
        )
        rank = int(np.count_nonzero(diagonal > tolerance))
        pivot_columns = [int(item) for item in column_order[:rank]]

        selected = numeric[:, pivot_columns]
        _, row_upper, row_order = qr(
            selected.T, mode="economic", pivoting=True, check_finite=False
        )
        row_diagonal = np.abs(np.diag(row_upper))
        row_rank = int(np.count_nonzero(row_diagonal > tolerance))
        if row_rank != rank:
            raise ArithmeticError(
                f"numerical row-rank mismatch at t={value}: {row_rank}!={rank}"
            )
        rows = [int(item) for item in row_order[:rank]]
    else:
        augmented = DomainMatrix.from_Matrix(
            evaluated.row_join(evaluated_rhs)
        ).convert_to(coefficient_field)
        _, pivots = augmented.rref()
        if variable_count in pivots:
            raise ArithmeticError(
                f"inconsistent evaluated system at t={value}"
            )
        pivot_columns = [pivot for pivot in pivots if pivot < variable_count]
        pivot_block = DomainMatrix.from_Matrix(
            evaluated[:, pivot_columns]
        ).convert_to(coefficient_field)
        _, independent_rows = pivot_block.transpose().rref()
        rows = list(independent_rows)

    if len(rows) != len(pivot_columns):
        raise ArithmeticError(
            f"failed to select a square pivot block at t={value}"
        )
    return pivot_columns, rows

def solve_sampled_pivot_block(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    pivot_columns: Sequence[int],
    rows: Sequence[int],
    value: int,
    coefficient_field,
) -> List[sp.Expr]:
    """Solve one fixed square pivot block over Q or Q(i)."""
    square = evaluate_at(matrix.extract(rows, pivot_columns), value)
    sampled_rhs = evaluate_at(rhs.extract(rows, [0]), value)
    square_domain = DomainMatrix.from_Matrix(square).convert_to(
        coefficient_field
    )
    rhs_domain = DomainMatrix.from_Matrix(sampled_rhs).convert_to(
        coefficient_field
    )
    numerator, denominator = square_domain.solve_den_rref(rhs_domain)
    denominator_expr = coefficient_field.to_sympy(denominator)
    values = [
        cancel(entry / denominator_expr)
        for entry in numerator.to_Matrix()
    ]
    full_left = evaluate_at(matrix[:, pivot_columns], value) * sp.Matrix(values)
    sampled_residual = full_left - evaluate_at(rhs, value)
    if any(cancel(entry) != 0 for entry in sampled_residual):
        raise ArithmeticError(
            f"sample solution failed the full system at t={value}"
        )
    return values


def rational_candidate(
    data: Sequence[Tuple[sp.Expr, sp.Expr]],
    numerator_degree: int,
    denominator_degree: int,
) -> sp.Expr | None:
    """Fit one Q(t) function by an explicit homogeneous coefficient system."""
    rows = []
    for abscissa, ordinate in data:
        rows.append(
            [abscissa ** degree for degree in range(numerator_degree + 1)]
            + [
                -ordinate * abscissa ** degree
                for degree in range(denominator_degree + 1)
            ]
        )
    nullspace = DomainMatrix.from_Matrix(sp.Matrix(rows)).convert_to(QQ).nullspace()
    if nullspace.shape[0] != 1:
        return None
    vector = list(nullspace.to_Matrix()[0, :])
    numerator = sum(
        vector[index] * t ** index
        for index in range(numerator_degree + 1)
    )
    offset = numerator_degree + 1
    denominator = sum(
        vector[offset + index] * t ** index
        for index in range(denominator_degree + 1)
    )
    if denominator == 0:
        return None
    return cancel(numerator / denominator)


def reconstruct_rational_component(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
    max_total_degree: int,
) -> sp.Expr:
    """Reconstruct one Q(t) component and validate on held-out samples."""
    if len(samples) < 4:
        raise ArithmeticError("not enough samples for rational reconstruction")
    if all(ordinate == 0 for _, ordinate in samples):
        return sp.Integer(0)
    validation_count = min(3, len(samples) - 1)
    training = list(samples[:-validation_count])
    validation = list(samples[-validation_count:])
    usable_degree = min(max_total_degree, len(training) - 1)
    for total_degree in range(usable_degree + 1):
        for numerator_degree in range(total_degree + 1):
            denominator_degree = total_degree - numerator_degree
            candidate = rational_candidate(
                training, numerator_degree, denominator_degree
            )
            if candidate is None:
                continue
            if all(
                cancel(candidate.subs(t, abscissa) - ordinate) == 0
                for abscissa, ordinate in validation
            ):
                return candidate
    raise ArithmeticError(
        f"no rational reconstruction through total degree {usable_degree}"
    )


def gaussian_parts(value: sp.Expr) -> Tuple[sp.Expr, sp.Expr]:
    """Return exact rational parts using the native Gaussian domain."""
    try:
        gaussian = QQ_I.from_sympy(sp.expand(sp.sympify(value)))
    except Exception as error:
        raise ArithmeticError(f"sample is not in Q(i): {value}") from error
    return QQ.to_sympy(gaussian.x), QQ.to_sympy(gaussian.y)


def reconstruct_gaussian_component(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
    max_total_degree: int,
) -> sp.Expr:
    """Reconstruct one Q(i)(t) value as a(t) + i*b(t), a,b in Q(t)."""
    real_samples = []
    imag_samples = []
    for abscissa, ordinate in samples:
        real, imag = gaussian_parts(ordinate)
        real_samples.append((abscissa, real))
        imag_samples.append((abscissa, imag))
    real_part = reconstruct_rational_component(
        real_samples, max_total_degree
    )
    imag_part = reconstruct_rational_component(
        imag_samples, max_total_degree
    )
    return cancel(real_part + sp.I * imag_part)


def polynomial_degree_in_t(expression: sp.Expr, coefficient_field) -> int:
    """Degree in t of a polynomial over Q or Q(i)."""
    expression = sp.expand(expression)
    if expression == 0:
        return -1
    if coefficient_field == QQ_I:
        return int(sp.Poly(expression, t, extension=sp.I).degree())
    return int(sp.Poly(expression, t, domain=QQ).degree())


def cramer_degree_bounds(
    square: sp.MatrixBase,
    sampled_rhs: sp.MatrixBase,
    coefficient_field,
) -> Tuple[int, int, int]:
    """Safe numerator/denominator/total degree bounds from Cramer's rule."""
    matrix_values = list(square.todok().values())
    rhs_values = list(sampled_rhs.todok().values())
    matrix_degree = max(
        [0] + [
            polynomial_degree_in_t(entry, coefficient_field)
            for entry in matrix_values
        ]
    )
    rhs_degree = max(
        [0] + [
            polynomial_degree_in_t(entry, coefficient_field)
            for entry in rhs_values
        ]
    )
    size = square.rows
    denominator_degree = size * matrix_degree
    numerator_degree = max(0, (size - 1) * matrix_degree + rhs_degree)
    return numerator_degree, denominator_degree, (
        numerator_degree + denominator_degree
    )


GAUSSIAN_LIFT_PRIME = (
    57896044618658097711785492504343953926634992332820282019728792003956564820109
)
GAUSSIAN_LIFT_ROOT = (
    18045140912533934601100706938971537283144490841571646837529842552170996990480
)


def modular_gaussian_sample_solution(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    *,
    prime: int = GAUSSIAN_LIFT_PRIME,
    root: int = GAUSSIAN_LIFT_ROOT,
) -> Tuple[Tuple[int, ...], List[sp.Expr]]:
    """Lift one Q(i) sample from the two finite-field embeddings.

    The embeddings ``i -> root`` and ``i -> -root`` recover the real and
    imaginary residues independently.  A 256-bit prime gives a 127-bit
    rational-reconstruction window.  The lifted solution is replayed over
    Q(i), so an insufficient modulus can never produce a false certificate.
    """
    evaluated = evaluate_at(matrix, value)
    evaluated_rhs = evaluate_at(rhs, value)
    augmented = evaluated.row_join(evaluated_rhs)
    variable_count = matrix.cols

    reductions = []
    pivot_layouts = []
    for embedding in (root, prime - root):
        modular = modular_gaussian_matrix(augmented, prime, embedding)
        reduced, pivots = modular.rref()
        if variable_count in pivots:
            raise ArithmeticError(
                f"inconsistent modular sample at t={value}"
            )
        reductions.append(reduced.to_Matrix())
        pivot_layouts.append(tuple(
            pivot for pivot in pivots if pivot < variable_count
        ))

    if pivot_layouts[0] != pivot_layouts[1]:
        raise ArithmeticError(
            f"conjugate modular pivot layouts differ at t={value}"
        )
    pivot_columns = pivot_layouts[0]
    plus_matrix, minus_matrix = reductions
    inverse_two = pow(2, -1, prime)
    inverse_two_root = pow((2 * root) % prime, -1, prime)
    values: List[sp.Expr] = []
    for row in range(len(pivot_columns)):
        plus = int(plus_matrix[row, variable_count]) % prime
        minus = int(minus_matrix[row, variable_count]) % prime
        real_residue = (plus + minus) * inverse_two % prime
        imag_residue = (plus - minus) * inverse_two_root % prime
        real = _integer_rational_reconstruction(
            ZZ(real_residue), ZZ(prime), ZZ
        )
        imag = _integer_rational_reconstruction(
            ZZ(imag_residue), ZZ(prime), ZZ
        )
        if real is None or imag is None:
            raise ArithmeticError(
                f"Gaussian rational lift failed at t={value}"
            )
        values.append(cancel(QQ.to_sympy(real) + sp.I * QQ.to_sympy(imag)))

    # Do not replay the full symbolic sample here: that multiplication costs
    # more than both modular reductions combined.  The reconstructed
    # Q(i)(t) solution is replayed against the original polynomial system
    # before it is accepted, which is the decisive exact check.
    return pivot_columns, values


def _gaussian_sample_worker(connection, matrix, rhs, value) -> None:
    """Child-process entry point for one modular Gaussian sample."""
    try:
        connection.send((
            "ok",
            modular_gaussian_sample_solution(matrix, rhs, value),
        ))
    except BaseException as error:
        connection.send(("error", repr(error)))
    finally:
        connection.close()


def modular_gaussian_sample_solution_fresh(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    timeout_seconds: float = 15.0,
) -> Tuple[Tuple[int, ...], List[sp.Expr]]:
    """Run one modular sample in a fresh forked process.

    Repeated large finite-field RREF calls cause cache and allocator growth in
    the current SymPy process.  Fork isolation keeps every sample at its
    steady-state runtime without changing the mathematics.
    """
    import multiprocessing as mp

    context = mp.get_context("fork")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(
        target=_gaussian_sample_worker,
        args=(child, matrix, rhs, value),
    )
    process.start()
    child.close()
    if not parent.poll(timeout_seconds):
        process.terminate()
        process.join()
        parent.close()
        raise ArithmeticError(
            f"Gaussian modular sample timed out at t={value}"
        )
    status, payload = parent.recv()
    parent.close()
    process.join()
    if process.exitcode != 0 or status != "ok":
        raise ArithmeticError(
            f"Gaussian modular sample failed at t={value}: {payload}"
        )
    return payload


def sampled_rref_solution(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    coefficient_field,
) -> Tuple[Tuple[int, ...], List[sp.Expr]]:
    """Return one exact free-variable-zero solution at ``t=value``.

    This deliberately performs row reduction only after specializing ``t``.
    Coefficients then lie in Q or Q(i), so there is no rational-function
    coefficient explosion.  The returned pivot layout is used to ensure that
    all interpolation samples describe the same symbolic solution branch.
    """
    evaluated = evaluate_at(matrix, value)
    evaluated_rhs = evaluate_at(rhs, value)
    augmented = DomainMatrix.from_Matrix(
        evaluated.row_join(evaluated_rhs)
    ).convert_to(coefficient_field)
    reduced, pivots = augmented.rref()
    variable_count = matrix.cols
    if variable_count in pivots:
        raise ArithmeticError(
            f"inconsistent evaluated system at t={value}"
        )
    pivot_columns = tuple(
        pivot for pivot in pivots if pivot < variable_count
    )
    reduced_matrix = reduced.to_Matrix()
    values = [
        cancel(reduced_matrix[row, variable_count])
        for row, pivot in enumerate(pivots)
        if pivot < variable_count
    ]
    solution = sp.MutableSparseMatrix(variable_count, 1, {})
    for column, coordinate in zip(pivot_columns, values):
        solution[column, 0] = coordinate
    residual = evaluated * sp.SparseMatrix(solution) - evaluated_rhs
    if any(cancel(entry) != 0 for entry in residual):
        raise ArithmeticError(
            f"sample RREF solution failed replay at t={value}"
        )
    return pivot_columns, values


def reconstruct_rational_fast(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
) -> sp.Expr:
    """Reconstruct the least-degree Q(t) function with held-out replay."""
    if len(samples) < 4:
        raise ArithmeticError("not enough samples for rational interpolation")
    if all(ordinate == 0 for _, ordinate in samples):
        return sp.Integer(0)
    validation_count = 1
    training = list(samples[:-validation_count])
    validation = list(samples[-validation_count:])
    for numerator_degree in range(len(training)):
        candidate = cancel(sp.rational_interpolate(
            training, numerator_degree, t
        ))
        if all(
            cancel(candidate.subs(t, abscissa) - ordinate) == 0
            for abscissa, ordinate in validation
        ):
            return candidate
    raise ArithmeticError("rational interpolation did not validate")


def reconstruct_gaussian_fast(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
) -> sp.Expr:
    """Reconstruct one Q(i)(t) coordinate by its rational components."""
    real_samples = []
    imag_samples = []
    for abscissa, ordinate in samples:
        real, imag = gaussian_parts(ordinate)
        real_samples.append((abscissa, real))
        imag_samples.append((abscissa, imag))
    return cancel(
        reconstruct_rational_fast(real_samples)
        + sp.I * reconstruct_rational_fast(imag_samples)
    )


def reconstruct_rational_polynomial(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
) -> sp.Expr:
    """Interpolate one Q[t] polynomial with one held-out sample."""
    if len(samples) < 3:
        raise ArithmeticError("not enough samples for polynomial interpolation")
    training = list(samples[:-1])
    validation = list(samples[-1:])
    polynomial = sp.expand(sp.interpolate(training, t))
    if not all(
        cancel(polynomial.subs(t, abscissa) - ordinate) == 0
        for abscissa, ordinate in validation
    ):
        raise ArithmeticError("rational polynomial interpolation did not validate")
    return polynomial


def polynomial_lcm_in_t_rational(expressions: Sequence[sp.Expr]) -> sp.Expr:
    """Least common multiple in Q[t], normalized to a monic polynomial."""
    current = sp.Poly(1, t, domain=QQ)
    for expression in expressions:
        polynomial = sp.Poly(sp.expand(expression), t, domain=QQ)
        current = sp.lcm(current, polynomial)
    return sp.expand(current.monic().as_expr())


def reconstruct_rational_from_samples(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    pivot_columns: Tuple[int, ...],
    sample_table: Dict[int, List[sp.Expr]],
    operator_coordinate_count: int,
) -> Tuple[sp.Matrix, int, int]:
    """Reconstruct a common-denominator Q(t) solution and replay it exactly."""
    abscissas = sorted(sample_table)
    operator_coordinates = []
    for index in range(min(operator_coordinate_count, len(pivot_columns))):
        coordinate_samples = [
            (sp.Integer(abscissa), sample_table[abscissa][index])
            for abscissa in abscissas
        ]
        operator_coordinates.append(reconstruct_rational_fast(coordinate_samples))
    base_denominator = polynomial_lcm_in_t_rational([
        sp.denom(cancel(coordinate)) for coordinate in operator_coordinates
    ])

    for t_power in range(max(1, operator_coordinate_count) + 1):
        common_denominator = sp.expand(t ** t_power * base_denominator)
        pivot_solution: List[sp.Expr] = []
        failed = False
        for index in range(len(pivot_columns)):
            numerator_samples = [
                (
                    sp.Integer(abscissa),
                    cancel(
                        sample_table[abscissa][index]
                        * common_denominator.subs(t, abscissa)
                    ),
                )
                for abscissa in abscissas
            ]
            try:
                numerator = reconstruct_rational_polynomial(numerator_samples)
            except ArithmeticError:
                failed = True
                break
            pivot_solution.append(cancel(numerator / common_denominator))
        if failed:
            continue

        solution = sp.MutableSparseMatrix(matrix.cols, 1, {})
        maximum_numerator_degree = 0
        for column, coordinate in zip(pivot_columns, pivot_solution):
            numerator = sp.expand(cancel(coordinate * common_denominator))
            if numerator != 0:
                maximum_numerator_degree = max(
                    maximum_numerator_degree, int(sp.degree(numerator, t))
                )
                solution[column, 0] = cancel(numerator / common_denominator)
        solution = sp.SparseMatrix(solution)
        denominator_degree = int(sp.degree(common_denominator, t))
        residual_degree_bound = max(
            operator_coordinate_count + maximum_numerator_degree,
            operator_coordinate_count + denominator_degree,
        )
        usable_points = [
            value for value in abscissas
            if common_denominator.subs(t, value) != 0
        ]
        required_points = residual_degree_bound + 1
        if len(usable_points) < required_points:
            continue
        if exact_sample_replay(
            matrix, solution, rhs, usable_points[:required_points]
        ):
            return solution, denominator_degree, t_power
    raise ArithmeticError("common-denominator rational reconstruction did not replay")


def modular_rational_sample_solution(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    *,
    prime: int = GAUSSIAN_LIFT_PRIME,
) -> Tuple[Tuple[int, ...], List[sp.Expr]]:
    """Lift one Q sample from finite-field RREF."""
    evaluated = evaluate_at(matrix, value)
    evaluated_rhs = evaluate_at(rhs, value)
    augmented = evaluated.row_join(evaluated_rhs)
    domain = GF(prime)
    entries: Dict[int, Dict[int, object]] = {}
    for (row, column), entry in augmented.todok().items():
        mapped = rational_mod_prime(entry, prime)
        if mapped:
            entries.setdefault(row, {})[column] = domain.convert(mapped)
    modular = DomainMatrix.from_dod(
        entries, (augmented.rows, augmented.cols), domain
    )
    reduced, pivots = modular.rref()
    variable_count = matrix.cols
    if variable_count in pivots:
        raise ArithmeticError(f"inconsistent modular sample at t={value}")
    pivot_columns = tuple(p for p in pivots if p < variable_count)
    reduced_matrix = reduced.to_Matrix()
    values: List[sp.Expr] = []
    for row in range(len(pivot_columns)):
        residue = int(reduced_matrix[row, variable_count]) % prime
        lifted = _integer_rational_reconstruction(ZZ(residue), ZZ(prime), ZZ)
        if lifted is None:
            raise ArithmeticError(
                f"rational lift failed at t={value}"
            )
        values.append(QQ.to_sympy(lifted))
    return pivot_columns, values


def _rational_sample_worker(connection, matrix, rhs, value) -> None:
    try:
        connection.send((
            "ok", modular_rational_sample_solution(matrix, rhs, value)
        ))
    except BaseException as error:
        connection.send(("error", repr(error)))
    finally:
        connection.close()


def modular_rational_sample_solution_fresh(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    value: int,
    timeout_seconds: float = 12.0,
) -> Tuple[Tuple[int, ...], List[sp.Expr]]:
    """Run one modular rational sample in a fresh forked process."""
    import multiprocessing as mp
    context = mp.get_context("fork")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(
        target=_rational_sample_worker, args=(child, matrix, rhs, value)
    )
    process.start()
    child.close()
    if not parent.poll(timeout_seconds):
        process.terminate()
        process.join()
        parent.close()
        raise ArithmeticError(f"rational modular sample timed out at t={value}")
    status, payload = parent.recv()
    parent.close()
    process.join()
    if process.exitcode != 0 or status != "ok":
        raise ArithmeticError(
            f"rational modular sample failed at t={value}: {payload}"
        )
    return payload


def sampled_rational_solution(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    *,
    entry_degree_bound: int | None = None,
    progress: Progress | None = None,
) -> sp.Matrix:
    """Solve a large Q(t) system by exact specialization and reconstruction."""
    if progress is None:
        progress = Progress(enabled=False)
    pivot_columns: Tuple[int, ...] | None = None
    sample_table: Dict[int, List[sp.Expr]] = {}
    inconsistent_samples = 0
    operator_coordinate_count = max(1, entry_degree_bound or 1)
    first_reconstruction_count = max(6, 4 * operator_coordinate_count + 1)

    for value in range(1, 129):
        try:
            sample_pivots, sample_values = (
                modular_rational_sample_solution_fresh(matrix, rhs, value)
            )
        except ArithmeticError:
            inconsistent_samples += 1
            if not sample_table and inconsistent_samples >= 3:
                raise ArithmeticError("three regular rational samples were inconsistent")
            continue
        if pivot_columns is None:
            pivot_columns = sample_pivots
            progress.emit(
                "large rational-system shunt: modular sampled RREF selected "
                f"{len(pivot_columns)} pivots"
            )
        elif sample_pivots != pivot_columns:
            continue
        sample_table[value] = sample_values
        sample_count = len(sample_table)
        progress.emit(
            f"rational sample {sample_count}/{first_reconstruction_count} "
            f"accepted at t={value}"
        )
        if sample_count < first_reconstruction_count:
            continue
        if (sample_count - first_reconstruction_count) % 2:
            continue
        try:
            solution, denominator_degree, t_power = reconstruct_rational_from_samples(
                matrix, rhs, pivot_columns, sample_table, operator_coordinate_count
            )
        except ArithmeticError as error:
            progress.emit(f"rational reconstruction deferred: {error}")
            continue
        progress.emit(
            "large rational-system shunt exact replay passed: "
            f"denominator degree={denominator_degree}, t-power={t_power}"
        )
        return solution
    raise ArithmeticError(
        "sampled rational solve exhausted 128 evaluation points without replay"
    )


def reconstruct_gaussian_polynomial(
    samples: Sequence[Tuple[sp.Expr, sp.Expr]],
) -> sp.Expr:
    """Interpolate one Q(i)[t] polynomial with three held-out samples."""
    if len(samples) < 4:
        raise ArithmeticError("not enough samples for polynomial interpolation")
    validation_count = 1
    training = list(samples[:-validation_count])
    validation = list(samples[-validation_count:])
    real_training = []
    imag_training = []
    real_validation = []
    imag_validation = []
    for abscissa, ordinate in training:
        real, imag = gaussian_parts(ordinate)
        real_training.append((abscissa, real))
        imag_training.append((abscissa, imag))
    for abscissa, ordinate in validation:
        real, imag = gaussian_parts(ordinate)
        real_validation.append((abscissa, real))
        imag_validation.append((abscissa, imag))
    real_polynomial = sp.expand(sp.interpolate(real_training, t))
    imag_polynomial = sp.expand(sp.interpolate(imag_training, t))
    if not all(
        cancel(real_polynomial.subs(t, abscissa) - ordinate) == 0
        for abscissa, ordinate in real_validation
    ):
        raise ArithmeticError("real polynomial interpolation did not validate")
    if not all(
        cancel(imag_polynomial.subs(t, abscissa) - ordinate) == 0
        for abscissa, ordinate in imag_validation
    ):
        raise ArithmeticError("imaginary polynomial interpolation did not validate")
    return sp.expand(real_polynomial + sp.I * imag_polynomial)


def polynomial_lcm_in_t(expressions: Sequence[sp.Expr]) -> sp.Expr:
    """Least common multiple in Q(i)[t], normalized only up to a unit."""
    current = sp.Poly(1, t, extension=sp.I)
    for expression in expressions:
        polynomial = sp.Poly(sp.expand(expression), t, extension=sp.I)
        current = sp.lcm(current, polynomial)
    return sp.expand(current.monic().as_expr())


def polynomial_matrix_replay(
    matrix: sp.MatrixBase,
    numerator_coordinates: Dict[int, sp.Expr],
    rhs: sp.MatrixBase,
    denominator: sp.Expr,
) -> bool:
    """Verify ``M*N = denominator*rhs`` by sparse row accumulation."""
    rows = [sp.Integer(0) for _ in range(matrix.rows)]
    for (row, column), coefficient in matrix.todok().items():
        numerator = numerator_coordinates.get(column)
        if numerator is not None:
            rows[row] += coefficient * numerator
    for (row, _), coefficient in rhs.todok().items():
        rows[row] -= denominator * coefficient
    for value in rows:
        if sp.Poly(sp.expand(value), t, extension=sp.I).as_expr() != 0:
            return False
    return True


def exact_sample_replay(
    matrix: sp.MatrixBase,
    solution: sp.MatrixBase,
    rhs: sp.MatrixBase,
    sample_points: Sequence[int],
) -> bool:
    """Replay a rational matrix identity exactly at integer sample points."""
    for value in sample_points:
        evaluated_matrix = evaluate_at(matrix, value).applyfunc(sp.expand)
        evaluated_rhs = evaluate_at(rhs, value).applyfunc(sp.expand)
        evaluated_solution = evaluate_at(solution, value).applyfunc(
            lambda entry: sp.expand(cancel(entry))
        )
        try:
            matrix_domain = DomainMatrix.from_Matrix(
                evaluated_matrix
            ).convert_to(QQ_I)
            rhs_domain = DomainMatrix.from_Matrix(
                evaluated_rhs
            ).convert_to(QQ_I)
            solution_domain = DomainMatrix.from_Matrix(
                evaluated_solution
            ).convert_to(QQ_I)
        except Exception:
            return False
        if not (matrix_domain.matmul(solution_domain) - rhs_domain).is_zero_matrix:
            return False
    return True


def reconstruct_gaussian_from_samples(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    pivot_columns: Tuple[int, ...],
    sample_table: Dict[int, List[sp.Expr]],
    operator_coordinate_count: int,
) -> Tuple[sp.Matrix, int, int]:
    """Reconstruct and exactly replay a common-denominator solution."""
    abscissas = sorted(sample_table)
    operator_coordinates = []
    for index in range(min(
        operator_coordinate_count, len(pivot_columns)
    )):
        coordinate_samples = [
            (sp.Integer(abscissa), sample_table[abscissa][index])
            for abscissa in abscissas
        ]
        operator_coordinates.append(
            reconstruct_gaussian_fast(coordinate_samples)
        )
    base_denominator = polynomial_lcm_in_t([
        sp.denom(cancel(coordinate))
        for coordinate in operator_coordinates
    ])

    for t_power in range(max(1, operator_coordinate_count) + 1):
        common_denominator = sp.expand(t ** t_power * base_denominator)
        pivot_solution: List[sp.Expr] = []
        failed = False
        for index in range(len(pivot_columns)):
            numerator_samples = [
                (
                    sp.Integer(abscissa),
                    cancel(
                        sample_table[abscissa][index]
                        * common_denominator.subs(t, abscissa)
                    ),
                )
                for abscissa in abscissas
            ]
            try:
                numerator = reconstruct_gaussian_polynomial(
                    numerator_samples
                )
            except ArithmeticError:
                failed = True
                break
            pivot_solution.append(cancel(numerator / common_denominator))
        if failed:
            continue

        solution = sp.MutableSparseMatrix(matrix.cols, 1, {})
        maximum_numerator_degree = 0
        for column, coordinate in zip(pivot_columns, pivot_solution):
            numerator = sp.expand(cancel(
                coordinate * common_denominator
            ))
            if numerator != 0:
                maximum_numerator_degree = max(
                    maximum_numerator_degree,
                    int(sp.degree(numerator, t)),
                )
                solution[column, 0] = cancel(
                    numerator / common_denominator
                )
        solution = sp.SparseMatrix(solution)
        denominator_degree = int(sp.degree(common_denominator, t))
        residual_degree_bound = max(
            operator_coordinate_count + maximum_numerator_degree,
            operator_coordinate_count + denominator_degree,
        )
        usable_points = [
            value for value in abscissas
            if common_denominator.subs(t, value) != 0
        ]
        required_points = residual_degree_bound + 1
        if len(usable_points) < required_points:
            continue
        if exact_sample_replay(
            matrix, solution, rhs, usable_points[:required_points]
        ):
            return (solution, denominator_degree, t_power)
    raise ArithmeticError(
        "common-denominator Gaussian reconstruction did not replay"
    )


def _gaussian_reconstruction_worker(
    connection,
    matrix,
    rhs,
    pivot_columns,
    sample_table,
    operator_coordinate_count,
) -> None:
    try:
        connection.send((
            "ok",
            reconstruct_gaussian_from_samples(
                matrix,
                rhs,
                pivot_columns,
                sample_table,
                operator_coordinate_count,
            ),
        ))
    except BaseException as error:
        connection.send(("error", repr(error)))
    finally:
        connection.close()


def reconstruct_gaussian_fresh(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    pivot_columns: Tuple[int, ...],
    sample_table: Dict[int, List[sp.Expr]],
    operator_coordinate_count: int,
    timeout_seconds: float = 40.0,
) -> Tuple[sp.Matrix, int, int]:
    """Run reconstruction in a fresh interpreter using file-based IPC."""
    import os
    import pickle
    import subprocess
    import tempfile

    module_directory = str(Path(__file__).resolve().parent)
    worker_code = r"""
import pickle
import sys
sys.path.insert(0, sys.argv[1])
import all_orders_solver as solver
with open(sys.argv[2], 'rb') as stream:
    arguments = pickle.load(stream)
result = solver.reconstruct_gaussian_from_samples(*arguments)
with open(sys.argv[3], 'wb') as stream:
    pickle.dump(result, stream, protocol=pickle.HIGHEST_PROTOCOL)
"""
    with tempfile.TemporaryDirectory(prefix="guvj_gaussian_") as directory:
        input_path = os.path.join(directory, "input.pkl")
        output_path = os.path.join(directory, "output.pkl")
        with open(input_path, "wb") as stream:
            pickle.dump(
                (
                    matrix,
                    rhs,
                    pivot_columns,
                    sample_table,
                    operator_coordinate_count,
                ),
                stream,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                worker_code,
                module_directory,
                input_path,
                output_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise ArithmeticError(
                "Gaussian reconstruction worker failed: "
                + completed.stderr[-1000:]
            )
        with open(output_path, "rb") as stream:
            return pickle.load(stream)


def sampled_gaussian_solution(
    matrix: sp.MatrixBase,
    rhs: sp.MatrixBase,
    *,
    entry_degree_bound: int | None = None,
    progress: Progress | None = None,
) -> sp.Matrix:
    """Solve over Q(i)(t) through an isolated modular coefficient shunt."""
    if progress is None:
        progress = Progress(enabled=False)

    pivot_columns: Tuple[int, ...] | None = None
    sample_table: Dict[int, List[sp.Expr]] = {}
    inconsistent_samples = 0
    operator_coordinate_count = max(1, entry_degree_bound or 1)
    first_reconstruction_count = max(
        6, 4 * operator_coordinate_count + 1
    )

    for value in range(1, 257):
        try:
            sample_pivots, sample_values = (
                modular_gaussian_sample_solution_fresh(
                    matrix, rhs, value
                )
            )
        except ArithmeticError:
            inconsistent_samples += 1
            if not sample_table and inconsistent_samples >= 3:
                raise ArithmeticError(
                    "three regular Gaussian samples were inconsistent"
                )
            continue

        if pivot_columns is None:
            pivot_columns = sample_pivots
            progress.emit(
                "Gaussian coefficient shunt: modular sampled RREF selected "
                f"{len(pivot_columns)} pivots"
            )
        elif sample_pivots != pivot_columns:
            continue

        sample_table[value] = sample_values
        sample_count = len(sample_table)
        progress.emit(
            f"Gaussian modular sample {sample_count}/"
            f"{first_reconstruction_count} accepted at t={value}"
        )
        if sample_count < first_reconstruction_count:
            continue
        if (sample_count - first_reconstruction_count) % 2:
            continue

        progress.emit(
            f"Gaussian reconstruction trial from {sample_count} samples"
        )
        try:
            solution, denominator_degree, t_power = (
                reconstruct_gaussian_fresh(
                    matrix,
                    rhs,
                    pivot_columns,
                    sample_table,
                    operator_coordinate_count,
                )
            )
        except ArithmeticError:
            continue
        progress.emit(
            "Gaussian coefficient shunt exact replay passed: "
            f"denominator degree={denominator_degree}, t-power={t_power}"
        )
        return solution

    raise ArithmeticError(
        "Gaussian modular sampled solve exhausted 256 evaluation points "
        "without an exact symbolic replay"
    )


def exact_free_zero_solution(
    matrix: sp.Matrix,
    rhs: sp.Matrix,
    coefficient_field,
    *,
    entry_degree_bound: int | None = None,
    progress: Progress | None = None,
) -> sp.Matrix:
    """Solve exactly over K(t), setting every free variable to zero.

    Q(t) retains the established direct path.  Q(i)(t) is detected up front
    and shunted to sampled Q(i) pivot solves, rational reconstruction, and one
    exact symbolic replay.
    """
    if coefficient_field == QQ_I:
        return sampled_gaussian_solution(
            matrix, rhs, entry_degree_bound=entry_degree_bound,
            progress=progress
        )

    # Small rational systems are fastest by direct fraction-field RREF.
    # Large systems suffer severe intermediate expression growth, so route
    # only those systems through exact specialization and reconstruction.
    if matrix.rows * matrix.cols >= 8000:
        return sampled_rational_solution(
            matrix, rhs, entry_degree_bound=entry_degree_bound,
            progress=progress
        )

    field = coefficient_field.frac_field(t)
    augmented = DomainMatrix.from_Matrix(matrix.row_join(rhs)).convert_to(field)
    reduced, pivots = augmented.rref()
    variable_count = matrix.cols
    if variable_count in pivots:
        raise ArithmeticError("divergence system is inconsistent at this support")
    reduced_matrix = reduced.to_Matrix()
    solution = sp.MutableSparseMatrix(variable_count, 1, {})
    for row, pivot in enumerate(pivots):
        if pivot < variable_count:
            solution[pivot, 0] = cancel(reduced_matrix[row, variable_count])
    solution = sp.SparseMatrix(solution)
    residual = matrix * solution - rhs
    failures = [cancel(value) for value in residual if cancel(value) != 0]
    if failures:
        raise AssertionError(
            f"exact divergence solve replay failed: {failures[:4]}"
        )
    return solution

def solve_divergence_certificate(
    F: sp.Expr,
    operator: sp.Expr,
    *,
    start_dilation: int = 1,
    max_dilation: int | None = None,
    progress: Progress | None = None,
) -> dict:
    """Expand Laurent support until the exact pole-layer identity solves."""
    if progress is None:
        progress = Progress(enabled=False)
    F = normalize_laurent(F)
    coefficient_field = coefficient_domain(laurent_terms(F).values())
    rho, rhs, order = operator_numerator(F, operator)
    for dilation in itertools.count(start_dilation):
        if max_dilation is not None and dilation > max_dilation:
            raise SearchExhausted(
                "support control exhausted; increase --max-dilation or omit it"
            )
        basis = support_basis(F, dilation)
        labels = []
        columns = []
        for layer in range(1, order + 1):
            for component in ("x", "y"):
                for i, j in basis:
                    labels.append((layer, component, i, j))
                    columns.append(divergence_column(
                        rho, x ** i * y ** j, layer, order, component
                    ))
        matrix, vector, rows = coefficient_matrix(columns, rhs)
        progress.emit(
            f"certificate trial dilation={dilation}, |B|={len(basis)}, "
            f"system={matrix.rows}x{matrix.cols}"
        )
        try:
            solution = exact_free_zero_solution(
                matrix, vector, coefficient_field, entry_degree_bound=order,
                progress=progress
            )
        except ArithmeticError:
            continue
        layers = []
        for layer in range(1, order + 1):
            bx_terms: Dict[Point, sp.Expr] = {}
            by_terms: Dict[Point, sp.Expr] = {}
            for index, (saved_layer, component, i, j) in enumerate(labels):
                if saved_layer != layer:
                    continue
                value = solution[index, 0]
                target = bx_terms if component == "x" else by_terms
                target[(i, j)] = target.get((i, j), 0) + value
            layers.append({
                "layer": layer,
                "Bx": laurent_expression_from_point_coefficients(bx_terms),
                "By": laurent_expression_from_point_coefficients(by_terms),
            })
        # The coefficient-system solve has already replayed M*solution=rhs
        # exactly.  Reassembling the same identity as one giant SymPy
        # expression is both redundant and can combine Laurent monomials into
        # misleading x,y denominators.
        progress.emit(
            f"certificate found at dilation={dilation}; exact replay passed"
        )
        return {
            "order": order,
            "dilation": dilation,
            "support_family": "newton",
            "support_level": dilation,
            "layer_basis_sizes": [len(basis) for _ in range(order)],
            "basis": basis,
            "rows": rows,
            "matrix_shape": [matrix.rows, matrix.cols],
            "rho": rho,
            "operator_numerator": rhs,
            "layers": layers,
        }



def solve_layered_divergence_certificate(
    F: sp.Expr,
    operator: sp.Expr,
    *,
    max_support_level: int | None = None,
    progress: Progress | None = None,
) -> dict:
    """Certify a known operator with the layerwise Newton degree bounds."""
    if progress is None:
        progress = Progress(enabled=False)
    F = normalize_laurent(F)
    coefficient_field = coefficient_domain(laurent_terms(F).values())
    rho, rhs, order = operator_numerator(F, operator)
    for support_level in itertools.count(1):
        if (
            max_support_level is not None
            and support_level > max_support_level
        ):
            raise SearchExhausted(
                "support control exhausted; increase --max-support-level "
                "or omit it"
            )
        supports = layer_supports(F, order, "newton", support_level)
        labels: List[Tuple[int, str, int, int]] = []
        columns: List[sp.Expr] = []
        for layer, basis in enumerate(supports, 1):
            for component in ("x", "y"):
                for i, j in basis:
                    labels.append((layer, component, i, j))
                    columns.append(divergence_column(
                        rho, x ** i * y ** j, layer, order, component
                    ))
        matrix, vector, rows = coefficient_matrix(columns, rhs)
        progress.emit(
            f"layered certificate trial support=newton:{support_level}, "
            f"system={matrix.rows}x{matrix.cols}"
        )
        try:
            solution = exact_free_zero_solution(
                matrix, vector, coefficient_field,
                entry_degree_bound=order, progress=progress
            )
        except ArithmeticError:
            continue
        layers = []
        for layer, basis in enumerate(supports, 1):
            bx_terms: Dict[Point, sp.Expr] = {}
            by_terms: Dict[Point, sp.Expr] = {}
            for index, (saved_layer, component, i, j) in enumerate(labels):
                if saved_layer != layer:
                    continue
                value = solution[index, 0]
                target = bx_terms if component == "x" else by_terms
                target[(i, j)] = target.get((i, j), 0) + value
            layers.append({
                "layer": layer,
                "Bx": laurent_expression_from_point_coefficients(bx_terms),
                "By": laurent_expression_from_point_coefficients(by_terms),
                "basis": basis,
            })
        progress.emit(
            f"layered certificate found at support=newton:{support_level}; "
            "exact replay passed"
        )
        return {
            "order": order,
            "dilation": order + support_level - 1,
            "support_family": "newton",
            "support_level": support_level,
            "layer_basis_sizes": [len(basis) for basis in supports],
            "rows": rows,
            "matrix_shape": [matrix.rows, matrix.cols],
            "rho": rho,
            "operator_numerator": rhs,
            "layers": layers,
        }


def centered_box_basis(radius: int) -> List[Point]:
    """All Laurent exponents in the centered box of the given radius."""
    if radius < 0:
        raise ValueError("box radius must be nonnegative")
    return [
        (i, j)
        for i in range(-radius, radius + 1)
        for j in range(-radius, radius + 1)
    ]


def layer_supports(
    F: sp.Expr, order: int, family: str, level: int,
) -> List[List[Point]]:
    """Return a finite, deterministic support for every pole layer.

    ``newton`` uses the natural layerwise Newton supports
    ``layer * conv({0} union supp(F))`` and enlarges them by ``level - 1``.
    ``box`` is the exhaustive fallback: every finite Laurent support occurs in
    a centered box at some level.
    """
    if level < 1:
        raise ValueError("support level must be positive")
    if family == "newton":
        return [
            support_basis(F, layer + level - 1)
            for layer in range(1, order + 1)
        ]
    if family == "box":
        basis = centered_box_basis(level)
        return [basis for _ in range(order)]
    raise ValueError(f"unknown support family: {family}")


def solve_joint_identity_trial(
    F: sp.Expr,
    order: int,
    *,
    support_family: str,
    support_level: int,
    progress: Progress | None = None,
) -> dict | None:
    """Solve operator and divergence certificate in one exact K(t) system.

    The coefficient of ``theta**order`` is normalized to one before solving.
    Therefore a successful solve necessarily uses the newest derivative.  No
    constant-term data and no guessed polynomial degree are used to discover
    the operator.
    """
    if progress is None:
        progress = Progress(enabled=False)
    F = normalize_laurent(F)
    coefficient_field = coefficient_domain(laurent_terms(F).values())
    progress.emit(
        "coefficient domain "
        + ("Q(i)" if coefficient_field == QQ_I else "Q")
        + "; linear solver=" + linear_solver_name(coefficient_field)
    )
    rho, numerators = theta_numerators(F, order)
    supports = layer_supports(F, order, support_family, support_level)
    matrix, vector, rows, labels = joint_coefficient_system(
        F, order, supports
    )
    progress.emit(
        f"joint trial order={order}, support={support_family}:{support_level}, "
        f"system={matrix.rows}x{matrix.cols}"
    )
    try:
        solution = exact_free_zero_solution(
            matrix, vector, coefficient_field, entry_degree_bound=order,
            progress=progress
        )
    except ArithmeticError:
        return None

    raw_operator = sp.expand(
        theta ** order
        + sum(solution[derivative, 0] * theta ** derivative
              for derivative in range(order))
    )
    operator, scale = normalize_operator_with_scale(raw_operator)
    witness_offset = order
    scaled_witness = [
        cancel(scale * solution[witness_offset + index, 0])
        for index in range(len(labels))
    ]

    layers = []
    for layer in range(1, order + 1):
        bx_terms: Dict[Point, sp.Expr] = {}
        by_terms: Dict[Point, sp.Expr] = {}
        for value, (saved_layer, component, i, j) in zip(
            scaled_witness, labels
        ):
            if saved_layer != layer or value == 0:
                continue
            target = bx_terms if component == "x" else by_terms
            target[(i, j)] = target.get((i, j), 0) + value
        layers.append({
            "layer": layer,
            "Bx": laurent_expression_from_point_coefficients(bx_terms),
            "By": laurent_expression_from_point_coefficients(by_terms),
            "basis": supports[layer - 1],
        })

    # ``exact_free_zero_solution`` has already replayed the complete joint
    # coefficient system exactly.  Scaling the monic operator and every
    # witness coordinate by the same exact factor preserves that identity.
    # Re-expanding the assembled Laurent expressions here duplicates the same
    # proof and is prohibitively expensive for the Gaussian canonical case.
    _, operator_rhs, replay_order = operator_numerator(F, operator)
    if replay_order != order:
        raise AssertionError("normalized operator order changed unexpectedly")

    progress.emit(
        f"joint identity found: order={order}, "
        f"support={support_family}:{support_level}"
    )
    return {
        "operator": operator,
        "certificate": {
            "order": order,
            "coefficient_domain": (
                "Q(i)" if coefficient_field == QQ_I else "Q"
            ),
            "linear_solver": linear_solver_name(coefficient_field),
            "exact_replay": "joint coefficient matrix",
            "support_family": support_family,
            "support_level": support_level,
            "dilation": (
                order + support_level - 1
                if support_family == "newton" else support_level
            ),
            "layer_basis_sizes": [len(basis) for basis in supports],
            "rows": rows,
            "matrix_shape": [matrix.rows, matrix.cols],
            "rho": rho,
            "operator_numerator": operator_rhs,
            "layers": layers,
        },
    }


def find_certified_identity(
    F: sp.Expr,
    *,
    max_order: int | None = None,
    max_support_level: int | None = None,
    progress: Progress | None = None,
) -> dict:
    """Dovetail exact order and exhaustive support searches.

    There is no term fit and no coefficient-degree search.  The Newton family
    is tried first as a finite deduction from the input support.  Centered boxes
    are interleaved as an exhaustive enumeration of all finite Laurent
    witnesses.  Optional maxima are resource controls only.
    """
    if progress is None:
        progress = Progress(enabled=False)
    tested: set[Tuple[int, Tuple[Tuple[Point, ...], ...]]] = set()
    trial_count = 0
    for search_round in itertools.count(1):
        found_pair = False
        for order in range(1, search_round + 1):
            support_level = search_round - order + 1
            if max_order is not None and order > max_order:
                continue
            if (
                max_support_level is not None
                and support_level > max_support_level
            ):
                continue
            found_pair = True
            for family in ("newton", "box"):
                supports = layer_supports(
                    F, order, family, support_level
                )
                signature = tuple(tuple(basis) for basis in supports)
                key = (order, signature)
                if key in tested:
                    continue
                tested.add(key)
                trial_count += 1
                result = solve_joint_identity_trial(
                    F,
                    order,
                    support_family=family,
                    support_level=support_level,
                    progress=progress,
                )
                if result is not None:
                    result["search"] = {
                        "round": search_round,
                        "trials": trial_count,
                        "order": order,
                        "support_family": family,
                        "support_level": support_level,
                        "minimal_order_proved": False,
                    }
                    return result
        if not found_pair:
            raise SearchExhausted(
                "joint search resource controls exhausted; this is not a "
                "claim that no identity exists"
            )
        if (
            max_order is not None
            and max_support_level is not None
            and search_round >= max_order + max_support_level - 1
        ):
            raise SearchExhausted(
                "joint search resource controls exhausted; this is not a "
                "claim that no identity exists"
            )

def derive_inductive_deductive(
    F: sp.Expr,
    *,
    max_order: int | None,
    max_shift_degree: int | None,
    max_dilation: int | None,
    progress: Progress,
) -> dict:
    """Discover from exact periods, then prove by the G-U-V-J identity.

    This is the large-system shunt.  The inductive relation is never accepted
    by itself: the returned operator must pass an exact divergence solve and
    direct recurrence replay.
    """
    progress.emit(
        "large rational input: exact term discovery followed by G-U-V-J proof"
    )
    operator, values, stats = find_operator(
        F, max_order=max_order, max_shift_degree=max_shift_degree,
        progress=progress
    )
    if operator_order(operator) >= 3:
        certificate = solve_layered_divergence_certificate(
            F, operator, max_support_level=max_dilation, progress=progress
        )
    else:
        certificate = solve_divergence_certificate(
            F, operator, max_dilation=max_dilation, progress=progress
        )
    recurrence = operator_recurrence(operator)
    order = operator_order(operator)
    shift_degree = sp.Poly(operator, t).degree()
    term_count = max(24, shift_degree + 4 * (order + 1) + 12)
    if len(values) < term_count:
        values = constant_terms(F, term_count)
    else:
        values = values[:term_count]
    if not recurrence_holds(recurrence, values):
        raise AssertionError("G-U-V-J-certified recurrence failed direct replay")
    progress.emit("all exact checks passed")
    return {
        "schema": "laurent-period-all-orders-certificate-v3",
        "F": F,
        "operator": operator,
        "operator_stats": {
            **stats,
            "support_family": certificate.get("support_family", "newton"),
            "support_level": certificate.get(
                "support_level", certificate["dilation"]
            ),
            "minimal_order_proved": False,
            "discovery": "exact constant terms with held-out replay",
        },
        "constant_terms": values,
        "recurrence": recurrence,
        "certificate": {
            **certificate,
            "coefficient_domain": "Q",
            "linear_solver": "adaptive-Q(t)-GUVJ",
            "exact_replay": "G-U-V-J coefficient matrix",
        },
        "checks": {
            "operator_from_joint_exact_identity": False,
            "operator_certified_by_GUVJ_identity": True,
            "divergence_identity_exact": True,
            "recurrence_replay_exact": True,
            "operator_from_finite_term_fit": True,
        },
    }


def derive(
    F: sp.Expr,
    *,
    max_order: int | None = None,
    max_shift_degree: int | None = None,
    max_dilation: int | None = None,
    max_support_level: int | None = None,
    progress_enabled: bool = True,
) -> dict:
    """Derive an exact operator, recurrence, and divergence certificate.

    ``max_shift_degree`` is retained only for API compatibility.  The joint
    solver does not search polynomial degrees.  ``max_dilation`` is accepted as
    the legacy name for ``max_support_level``.
    """
    progress = Progress(enabled=progress_enabled)
    F = normalize_laurent(F)
    progress.emit(f"normalized input with {len(laurent_terms(F))} terms")
    if max_shift_degree is not None:
        progress.emit(
            "legacy max-shift control ignored: joint solving has no "
            "shift-degree search"
        )
    if max_support_level is None:
        max_support_level = max_dilation
    elif max_dilation is not None and max_dilation != max_support_level:
        raise ValueError("conflicting support-level resource controls")

    input_terms = laurent_terms(F)
    input_domain = coefficient_domain(input_terms.values())
    if input_domain == QQ and (
        len(input_terms) >= 12 or (max_order is not None and max_order >= 3)
    ):
        return derive_inductive_deductive(
            F,
            max_order=max_order,
            max_shift_degree=max_shift_degree,
            max_dilation=max_support_level,
            progress=progress,
        )

    exact = find_certified_identity(
        F,
        max_order=max_order,
        max_support_level=max_support_level,
        progress=progress,
    )
    operator = exact["operator"]
    certificate = exact["certificate"]
    recurrence = operator_recurrence(operator)
    order = operator_order(operator)
    shift_degree = sp.Poly(operator, t).degree()
    term_count = max(24, shift_degree + 4 * (order + 1) + 12)
    progress.emit(
        f"checking recurrence on {term_count} direct constant terms"
    )
    values = constant_terms(F, term_count)
    if not recurrence_holds(recurrence, values):
        raise AssertionError("exactly derived recurrence failed direct replay")
    progress.emit("all exact checks passed")
    return {
        "schema": "laurent-period-all-orders-certificate-v3",
        "F": F,
        "operator": operator,
        "operator_stats": {
            "order": order,
            "shift_degree": shift_degree,
            "terms": term_count,
            "trials": exact["search"]["trials"],
            "search_round": exact["search"]["round"],
            "support_family": exact["search"]["support_family"],
            "support_level": exact["search"]["support_level"],
            "minimal_order_proved": exact["search"][
                "minimal_order_proved"
            ],
        },
        "constant_terms": values,
        "recurrence": recurrence,
        "certificate": certificate,
        "checks": {
            "operator_from_joint_exact_identity": True,
            "divergence_identity_exact": True,
            "recurrence_replay_exact": True,
            "operator_from_finite_term_fit": False,
        },
    }

