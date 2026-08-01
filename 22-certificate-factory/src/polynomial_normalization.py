"""Exact univariate common-factor removal for displayed equations."""
from __future__ import annotations

import ast
import math
from fractions import Fraction
from functools import reduce


def _trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def _add(a, b, sign=1):
    out = [Fraction(0)] * max(len(a), len(b))
    for i, value in enumerate(a): out[i] += value
    for i, value in enumerate(b): out[i] += sign * value
    return _trim(out)


def _mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): out[i + j] += x * y
    return _trim(out)


def _pow(a, exponent):
    out = [Fraction(1)]
    for _ in range(exponent): out = _mul(out, a)
    return out


def _parse(expression, variable):
    def visit(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return [Fraction(node.value)]
        if isinstance(node, ast.Name) and node.id == variable:
            return [Fraction(0), Fraction(1)]
        if isinstance(node, ast.UnaryOp):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else [-x for x in value]
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return _add(left, right)
            if isinstance(node.op, ast.Sub): return _add(left, right, -1)
            if isinstance(node.op, ast.Mult): return _mul(left, right)
            if isinstance(node.op, ast.Pow):
                exponent = ast.literal_eval(node.right)
                if not isinstance(exponent, int) or exponent < 0: raise ValueError(expression)
                return _pow(left, exponent)
        raise ValueError(f"unsupported polynomial expression: {expression}")
    source = str(expression).replace("^", "**")
    return _trim(visit(ast.parse(source, mode="eval").body))


def _divmod(a, b):
    a, b = _trim(a), _trim(b)
    if b == [0]: raise ZeroDivisionError
    quotient = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        shift, coefficient = len(a) - len(b), a[-1] / b[-1]
        quotient[shift] += coefficient
        subtract = [Fraction(0)] * shift + [coefficient * x for x in b]
        a = _add(a, subtract, -1)
    return _trim(quotient), _trim(a)


def _monic(p):
    p = _trim(p)
    if p == [0]: return p
    return [x / p[-1] for x in p]


def _gcd(a, b):
    a, b = _trim(a), _trim(b)
    while b != [0]:
        _, remainder = _divmod(a, b)
        a, b = b, remainder
    return _monic(a)


def _format(p, variable):
    terms = []
    for degree in range(len(p) - 1, -1, -1):
        coefficient = p[degree]
        if not coefficient: continue
        if coefficient.denominator != 1:
            raise ValueError(f"nonintegral normalized coefficient: {coefficient}")
        value = abs(coefficient.numerator)
        power = "" if degree == 0 else (variable if degree == 1 else f"{variable}**{degree}")
        body = str(value) if not power else (power if value == 1 else f"{value}*{power}")
        if not terms:
            terms.append(("-" if coefficient < 0 else "") + body)
        else:
            terms.append((" - " if coefficient < 0 else " + ") + body)
    return "".join(terms) or "0"


def divide_common_polynomial_factor(expressions, variable):
    """Return primitive displayed coefficients and the exact removed factor."""
    polynomials = [_parse(item, variable) for item in expressions]
    nonzero = [p for p in polynomials if p != [0]]
    if not nonzero:
        return list(map(str, expressions)), "1"
    polynomial_gcd = reduce(_gcd, nonzero)
    integer_content = reduce(math.gcd, (abs(x.numerator) for p in nonzero for x in p))
    factor = [integer_content * x for x in polynomial_gcd]
    if factor[-1] < 0: factor = [-x for x in factor]
    if factor == [1]:
        return list(map(str, expressions)), "1"
    quotients = []
    for polynomial in polynomials:
        quotient, remainder = _divmod(polynomial, factor)
        if remainder != [0]: raise ValueError((expressions, factor, remainder))
        quotients.append(_format(quotient, variable))
    return quotients, _format(factor, variable)
