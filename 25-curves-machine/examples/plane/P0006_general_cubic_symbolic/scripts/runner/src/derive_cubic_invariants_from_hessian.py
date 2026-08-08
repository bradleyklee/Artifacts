from pathlib import Path
import json
import time
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
x, y, z = sp.symbols('x y z')
a, b, c, d, alpha = sp.symbols('a b c d alpha')
mu = sp.symbols('mu')
U = a*x**3 + b*x**2*y + c*x*y**2 + d*y**3 + x**2*z + y**2*z - alpha*z**3


def hessian_covariant(form):
    return sp.expand(-sp.det(sp.hessian(form, (x, y, z))) / 2)


start = time.time()
HU = sp.factor(hessian_covariant(U))
print('Hessian seconds', time.time() - start, 'terms', len(sp.Poly(HU, x, y, z).terms()))
start = time.time()
pencil = sp.Poly(hessian_covariant(U + mu*HU), mu)
print('pencil seconds', time.time() - start, 'degree', pencil.degree())
coefficient_1 = sp.expand(pencil.coeff_monomial(mu))
q4, r4 = sp.div(coefficient_1, 3*U, x, y, z,
                domain=sp.QQ.frac_field(a, b, c, d, alpha))
if sp.simplify(r4) != 0:
    raise RuntimeError('nonzero c4 division remainder')
c4 = sp.factor(q4)
coefficient_2 = sp.expand(pencil.coeff_monomial(mu**2))
q6, r6 = sp.div(sp.expand(coefficient_2 + 3*c4*HU), 6*U, x, y, z,
                domain=sp.QQ.frac_field(a, b, c, d, alpha))
if sp.simplify(r6) != 0:
    raise RuntimeError('nonzero c6 division remainder')
c6 = sp.factor(q6)
delta = sp.factor((c4**3 - c6**2) / 1728)
record = {
    'c4': str(c4),
    'c6': str(c6),
    'Delta_normalized': str(delta),
    'Hessian': str(HU),
}
(ROOT / 'data/general_cubic_invariants.json').write_text(json.dumps(record, indent=2) + '\n')
print('c4 =', c4)
print('c6 =', c6)
print('Delta degree in alpha =', sp.degree(delta, alpha))
