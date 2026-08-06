"""Exact release checks for promoted models 5 and 7.

The checks use explicit expansion, exact polynomial division, exact sparse
Laurent arithmetic, coefficient matching, and ODE-recurrence compatibility.
No black-box simplification routine is used.
"""
from pathlib import Path
import json
import math
import time
import sympy as sp

HERE = Path(__file__).resolve().parent
RELEASE_ROOT = HERE.parents[1]
DATA = RELEASE_ROOT / 'examples' / 'data'
CERT = RELEASE_ROOT / 'examples' / 'certificates' / 'models_05_07'

models = json.loads((DATA / 'models_11_release.json').read_text())
form = json.loads((CERT / 'exact_formulas.json').read_text())
p, q, E, n, w, z, x, y, t = sp.symbols('p q E n w z x y t')

START = time.monotonic()


def progress(message: str) -> None:
    elapsed = time.monotonic() - START
    print(f"[promoted] {elapsed:7.2f}s  {message}", flush=True)



def scalar_check(item: dict[str, str], filename: str) -> None:
    loc = {'p': p, 'q': q, 'E': E}
    K = sp.sympify(item['K'], locals=loc)
    A2 = sp.sympify(item['A2E'], locals=loc)
    A1 = sp.sympify(item['A1E'], locals=loc)
    A0 = sp.sympify(item['A0E'], locals=loc)
    V = sp.sympify((CERT / filename).read_text(), locals=loc)
    Kp = sp.diff(K, p)
    Kq = sp.diff(K, q)

    def DE(value: sp.Expr) -> sp.Expr:
        return sp.cancel(sp.diff(value, p) / Kp)

    left = sp.cancel(A2*DE(DE(2/Kp)) + A1*DE(2/Kp) + A0*(2/Kp))
    Xi = sp.cancel(V / Kp**3)
    right = sp.cancel(sp.diff(Xi, q) - Kq*sp.diff(Xi, p)/Kp)
    numerator, _ = sp.fraction(sp.cancel(left-right))
    remainder = sp.Poly(sp.expand(numerator), p).rem(sp.Poly(K-E, p)).as_expr()
    if remainder != 0:
        raise AssertionError('nonzero scalar-certificate residual')


def sparse_expr(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> dict[tuple[int, ...], sp.Expr]:
    out: dict[tuple[int, ...], sp.Expr] = {}
    for term in sp.Add.make_args(sp.expand(expr)):
        powers = term.as_powers_dict()
        exponent = tuple(int(powers.get(var, 0)) for var in vars_)
        monomial = sp.prod(var**power for var, power in zip(vars_, exponent, strict=True))
        coefficient = sp.expand(term / monomial)
        out[exponent] = sp.expand(out.get(exponent, 0) + coefficient)
    return {key: value for key, value in out.items() if value != 0}


def sparse_add(a, b):
    out = dict(a)
    for key, value in b.items():
        out[key] = sp.expand(out.get(key, 0) + value)
        if out[key] == 0:
            del out[key]
    return out


def sparse_mul(a, b):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            key = tuple(x+y for x, y in zip(ka, kb, strict=True))
            out[key] = sp.expand(out.get(key, 0) + va*vb)
    return {key: value for key, value in out.items() if value != 0}


def sparse_scale(a, factor):
    return {key: sp.expand(factor*value) for key, value in a.items()}


def sparse_log_derivative(a, position):
    return {
        key: sp.expand(key[position]*value)
        for key, value in a.items()
        if key[position] != 0
    }


def constant_terms(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], count: int) -> list[sp.Integer]:
    poly = sparse_expr(expr, vars_)
    power = {(0,)*len(vars_): sp.Integer(1)}
    values = []
    for _ in range(count):
        values.append(sp.Integer(power.get((0,)*len(vars_), 0)))
        power = sparse_mul(power, poly)
    return values


def ode_recurrence(model: dict) -> dict[int, sp.Expr]:
    ode = model['ode_t']
    A0 = sp.sympify(ode['0'], locals={'t': t})
    A1 = sp.sympify(ode['1'], locals={'t': t})
    A2 = sp.sympify(ode['2'], locals={'t': t})
    recurrence: dict[int, sp.Expr] = {}
    for (degree,), coefficient in sp.Poly(A2, t).terms():
        shift = 2-degree
        recurrence[shift] = sp.expand(recurrence.get(shift, 0) + coefficient*(n-degree+2)*(n-degree+1))
    for (degree,), coefficient in sp.Poly(A1, t).terms():
        shift = 1-degree
        recurrence[shift] = sp.expand(recurrence.get(shift, 0) + coefficient*(n-degree+1))
    for (degree,), coefficient in sp.Poly(A0, t).terms():
        shift = -degree
        recurrence[shift] = sp.expand(recurrence.get(shift, 0) + coefficient)
    return recurrence


# Exact Hamiltonian scalar certificates.
progress("model 5: scalar certificate started")
scalar_check(form['model5'], 'model5_scalar_V.txt')
progress("model 5: scalar certificate passed")
progress("model 7: scalar certificate started")
scalar_check(form['model7'], 'model7_scalar_V.txt')
progress("model 7: scalar certificate passed")

# Model 5 Laurent certificate.
progress("model 5: Laurent certificate started")
G5 = sp.expand(390 + 320*(z+z**-1) + 125*(z**2+z**-2))
Q5 = {int(key): sp.sympify(value, locals={'n': n}) for key, value in form['model5']['Q'].items()}
R5 = sp.sympify((CERT / 'model5_laurent_R.txt').read_text(), locals={'z': z, 'n': n})
residual5 = sp.expand(G5*sum(Q5[s]*G5**s for s in Q5) - G5*z*sp.diff(R5, z) - n*z*sp.diff(G5, z)*R5)
if residual5 != 0:
    raise AssertionError('model 5 Laurent residual is nonzero')
progress("model 5: Laurent certificate passed")

# Model 7 two-variable Laurent certificate.
progress("model 7: Laurent certificate started")
def read_sparse(filename: str):
    raw = json.loads((CERT / filename).read_text())
    return {tuple(map(int, key.split(','))): sp.sympify(value, locals={'n': n}) for key, value in raw.items()}

P7 = sp.sympify(form['model7']['P'], locals={'x': x, 'y': y})
Q7 = {int(key): sp.sympify(value, locals={'n': n}) for key, value in form['model7']['Q_scaled'].items()}
Rx = read_sparse('model7_laurent_Rx.json')
Ry = read_sparse('model7_laurent_Ry.json')
F7 = sparse_expr(P7, (x, y))
powers = {0: {(0, 0): sp.Integer(1)}}
for exponent in range(1, 5):
    powers[exponent] = sparse_mul(powers[exponent-1], F7)
lhs = {}
for shift, coefficient in Q7.items():
    lhs = sparse_add(lhs, sparse_scale(powers[shift+1], coefficient))
rhs = sparse_add(
    sparse_mul(F7, sparse_add(sparse_log_derivative(Rx, 0), sparse_log_derivative(Ry, 1))),
    sparse_scale(
        sparse_add(sparse_mul(sparse_log_derivative(F7, 0), Rx), sparse_mul(sparse_log_derivative(F7, 1), Ry)),
        n,
    ),
)
for key in set(lhs) | set(rhs):
    if sp.expand(lhs.get(key, 0)-rhs.get(key, 0)) != 0:
        raise AssertionError(f'model 7 Laurent residual is nonzero at {key}')
progress("model 7: Laurent certificate passed")

# Coefficient matching through 12 terms.
progress("models 5 and 7: coefficient checks started")
P5 = sp.sympify(form['model5']['P'], locals={'w': w, 'z': z})
for index, expr, vars_ in [(5, P5, (w, z)), (7, P7, (x, y))]:
    expected = [sp.Integer(value) for value in models['models'][index-1]['first_31_coefficients_at_observed_scale'][:12]]
    observed = constant_terms(expr, vars_, 12)
    if observed != expected:
        raise AssertionError(f'constant-term coefficient mismatch for model {index}')
    progress(f"model {index}: 12 coefficients passed")

# Model 7 recurrence is the stored ODE recurrence times one common factor.
progress("model 7: ODE recurrence check started")
rec7 = ode_recurrence(models['models'][6])
expected7 = {shift: sp.factor(rec7[shift-2].subs(n, n+2)) for shift in range(4)}
ratios7 = [sp.factor(Q7[shift]/expected7[shift]) for shift in range(4)]
if any(ratio != ratios7[0] for ratio in ratios7[1:]):
    raise AssertionError('model 7 Laurent recurrence does not match the period ODE')
progress("model 7: ODE recurrence check passed")

# Model 5 certificate is for the z-moments after removing binomial(2n,n).
progress("model 5: ODE recurrence check started")
rec5 = ode_recurrence(models['models'][4])
expected5 = {shift: sp.factor(rec5[shift-2].subs(n, n+2)) for shift in range(4)}
def central_ratio(shift: int) -> sp.Expr:
    value = sp.Integer(1)
    for step in range(shift):
        k = n+step
        value = sp.factor(value * 2*(2*k+1)/(k+1))
    return value
transformed5 = {shift: sp.factor(Q5[shift]/central_ratio(shift)) for shift in range(4)}
ratios5 = [sp.factor(transformed5[shift]/expected5[shift]) for shift in range(4)]
if any(ratio != ratios5[0] for ratio in ratios5[1:]):
    raise AssertionError('model 5 Laurent recurrence does not match the period ODE')
progress("model 5: ODE recurrence check passed")
progress("all promoted certificate checks passed")

print(
    'models 5 and 7: exact certificates, 12 coefficients, and ODE '
    'recurrences all match',
    flush=True,
)
