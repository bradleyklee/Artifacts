"""Verify the four legacy completed cases exactly with sparse arithmetic.

The Hamiltonian identities use multivariate ``Poly`` operations over QQ.  The
Laurent identities use an explicit sparse dictionary in powers of x and n over
the Gaussian rationals QQ(i).  No black-box simplification routine is used.
"""
from __future__ import annotations

import json
from pathlib import Path
import time

import sympy as sp

HERE = Path(__file__).resolve().parent
RELEASE_ROOT = HERE.parents[1]
DATA_ROOT = RELEASE_ROOT / "examples"
DATA = json.loads((DATA_ROOT / "data" / "models_11_release.json").read_text())
ROOT = DATA_ROOT / "certificates" / "models_01_02_03_09"

p, q, E, n, x = sp.symbols("p q E n x")

START = time.monotonic()


def progress(message: str) -> None:
    elapsed = time.monotonic() - START
    print(f"[legacy] {elapsed:7.2f}s  {message}", flush=True)


H = {
    1: p**2 + q**2 + p*q**2 + q**3,
    2: p**2 + q**2 + p**3 + q**3,
    3: p**2 + q**2 - p**3 - 3*p**2*q - 2*q**3,
    9: p**2 + q**2 + (q**2 - 4*p**2) ** 2,
}
G = {
    1: -sp.I*x**3 + (2+4*sp.I)*x**2 + (-8-5*sp.I)*x + 12
       + (-8+5*sp.I)/x + (2-4*sp.I)/x**2 + sp.I/x**3,
    3: -sp.I*x**3 + (-6-12*sp.I)*x**2 + (-24-21*sp.I)*x + 92
       + (-24+21*sp.I)/x + (-6+12*sp.I)/x**2 + sp.I/x**3,
    9: -25*x**2 - 60*x - 86 - 60/x - 25/x**2,
}

SparseLaurent = dict[tuple[int, int], object]


def poly_pqE(expression: sp.Expr) -> sp.Poly:
    return sp.Poly(expression, p, q, E, domain=sp.QQ)


def sparse_laurent(expression: sp.Expr) -> SparseLaurent:
    """Convert a Laurent polynomial in x with polynomial coefficients in n."""
    out: SparseLaurent = {}
    for term in sp.Add.make_args(expression):
        powers = term.as_powers_dict()
        x_power = int(powers.get(x, 0))
        coefficient = term / x**x_power
        polynomial = sp.Poly(coefficient, n, domain=sp.QQ_I)
        for (n_power,), value in polynomial.terms():
            key = (x_power, n_power)
            out[key] = out.get(key, sp.QQ_I.zero) + value
    return {key: value for key, value in out.items() if value}


def sparse_add(*items: tuple[SparseLaurent, int]) -> SparseLaurent:
    out: SparseLaurent = {}
    for polynomial, scale in items:
        scalar = sp.QQ_I.convert(scale)
        for key, value in polynomial.items():
            out[key] = out.get(key, sp.QQ_I.zero) + scalar * value
    return {key: value for key, value in out.items() if value}


def sparse_multiply(left: SparseLaurent, right: SparseLaurent) -> SparseLaurent:
    out: SparseLaurent = {}
    for (x_left, n_left), a in left.items():
        for (x_right, n_right), b in right.items():
            key = (x_left + x_right, n_left + n_right)
            out[key] = out.get(key, sp.QQ_I.zero) + a * b
    return {key: value for key, value in out.items() if value}


def sparse_power(base: SparseLaurent, exponent: int) -> SparseLaurent:
    out: SparseLaurent = {(0, 0): sp.QQ_I.one}
    for _ in range(exponent):
        out = sparse_multiply(out, base)
    return out


def x_derivative_times_x(polynomial: SparseLaurent) -> SparseLaurent:
    return {
        (x_power, n_power): x_power * value
        for (x_power, n_power), value in polynomial.items()
        if x_power * value
    }


def multiply_by_n(polynomial: SparseLaurent) -> SparseLaurent:
    return {(x_power, n_power + 1): value for (x_power, n_power), value in polynomial.items()}


def verify_hamiltonian(index: int) -> None:
    model = DATA["models"][index - 1]
    certificate = model["certificate"]
    A2 = sp.sympify(certificate["hamiltonian_operator_E"]["A2"], locals={"E": E})
    A1 = sp.sympify(certificate["hamiltonian_operator_E"]["A1"], locals={"E": E})
    A0 = sp.sympify(certificate["hamiltonian_operator_E"]["A0"], locals={"E": E})
    P = poly_pqE(sp.sympify(
        (ROOT / Path(certificate["hamiltonian_P_file"]).name).read_text(),
        locals={"E": E, "alpha": E, "p": p, "q": q},
    ))
    Q = poly_pqE(sp.sympify(
        (ROOT / Path(certificate["hamiltonian_Q_file"]).name).read_text(),
        locals={"E": E, "alpha": E, "p": p, "q": q},
    ))
    hamiltonian = poly_pqE(H[index])
    D = poly_pqE(H[index] - E)
    left = poly_pqE(2 * A2) + poly_pqE(A1) * D + poly_pqE(A0) * D * D
    right = D * (P.diff(p) + Q.diff(q)) - 2 * (
        P * hamiltonian.diff(p) + Q * hamiltonian.diff(q)
    )
    if right != left:
        raise AssertionError(f"Hamiltonian certificate failed for model {index}")


def verify_laurent(index: int) -> None:
    model = DATA["models"][index - 1]
    certificate = model["certificate"]
    recurrence = {
        int(key): sp.sympify(value, locals={"n": n})
        for key, value in certificate["angular_recurrence"].items()
    }
    R = sp.sympify(
        (ROOT / Path(certificate["laurent_R_file"]).name).read_text(),
        locals={"n": n, "x": x, "I": sp.I},
    )
    g = sparse_laurent(G[index])
    r = sparse_laurent(R)
    recurrence_sum: SparseLaurent = {}
    for exponent, coefficient in recurrence.items():
        term = sparse_multiply(sparse_laurent(coefficient), sparse_power(g, exponent))
        recurrence_sum = sparse_add((recurrence_sum, 1), (term, 1))
    residual = sparse_add(
        (sparse_multiply(g, recurrence_sum), 1),
        (sparse_multiply(g, x_derivative_times_x(r)), -1),
        (sparse_multiply(multiply_by_n(x_derivative_times_x(g)), r), -1),
    )
    if residual:
        raise AssertionError(f"Laurent certificate failed for model {index}")


for model_index in (1, 2, 3, 9):
    progress(f"model {model_index}: Hamiltonian certificate started")
    verify_hamiltonian(model_index)
    progress(f"model {model_index}: Hamiltonian certificate passed")

for model_index in (1, 3, 9):
    progress(f"model {model_index}: Laurent certificate started")
    verify_laurent(model_index)
    progress(f"model {model_index}: Laurent certificate passed")

progress("all legacy certificate checks passed")
print("Four Hamiltonian certificates: exact sparse residual 0", flush=True)
print("Three Laurent certificates: exact sparse residual 0", flush=True)
print("Model 2 Laurent certificate: retained from exact pilot", flush=True)
