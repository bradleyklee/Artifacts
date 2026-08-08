from pathlib import Path
import json
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
A, B, C, D, x = sp.symbols('a b c d alpha')
U = json.loads((ROOT / 'data/general_cubic_order2_operator.json').read_text())
Ps = [sp.sympify(s, locals={'a': A, 'b': B, 'c': C, 'd': D, 'alpha': x})
      for s in U['operator_expanded']]


def inv(n, p):
    return pow(n % p, -1, p)


def ratmod(r, p):
    r = sp.Rational(r)
    return int(r.p) % p * inv(int(r.q), p) % p


def apply_operator(polys, seq, p):
    n_terms = len(seq)
    residual = [0] * n_terms
    for j, poly_expr in enumerate(polys):
        poly = sp.Poly(poly_expr, x)
        for (k,), coeff in poly.terms():
            cmod = ratmod(coeff, p)
            for m in range(n_terms - j - k):
                falling = 1
                for h in range(1, j + 1):
                    falling = falling * (m + h) % p
                residual[m + k] = (
                    residual[m + k] + cmod * falling * int(seq[m + j])
                ) % p
    return residual


checks = []
name = 'generic_cubic_all_B'
model = json.loads((ROOT / f'reference/models/{name}.json').read_text())
coeff = {(3, 0): 0, (2, 1): 0, (1, 2): 0, (0, 3): 0}
for p_exp, q_exp, value in model['monomials']['3']:
    coeff[(int(p_exp), int(q_exp))] += sp.Rational(value)

for prime in (65497, 65521):
    seq = json.loads(
        (ROOT / f'reference/data/{name}_series_{prime}.json').read_text()
    )['terms']
    vals = {
        A: coeff[(3, 0)], B: coeff[(2, 1)],
        C: coeff[(1, 2)], D: coeff[(0, 3)],
    }
    specialized = [
        sp.Poly(sp.expand(poly.subs(vals)), x, domain=sp.QQ).as_expr()
        for poly in Ps
    ]
    residual = apply_operator(specialized, seq, prime)
    max_degree = max(int(sp.degree(poly, x)) for poly in specialized)
    valid = int(len(seq) - 2 - max_degree)
    bad = [(int(i), int(residual[i])) for i in range(valid) if residual[i] % prime]
    record = {
        'example': name,
        'prime': int(prime),
        'checked_coefficients': valid,
        'bad_count': int(len(bad)),
        'first_bad': bad[:3],
    }
    checks.append(record)
    print(record)

out = ROOT / 'checks/general_cubic_modular_series_checks.json'
out.write_text(json.dumps(checks, indent=2) + '\n')
if any(record['bad_count'] for record in checks):
    raise SystemExit('modular series verification failed')
