from pathlib import Path
import json
import math
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
A, B, C, D, t = sp.symbols('a b c d alpha')
U = json.loads((ROOT / 'data/general_cubic_order2_operator.json').read_text())
Ps = [sp.sympify(s, locals={'a': A, 'b': B, 'c': C, 'd': D, 'alpha': t})
      for s in U['operator_expanded']]


def primitive_tuple(polys):
    polys = [sp.expand(poly) for poly in polys]
    denominator = sp.lcm([sp.denom(poly) for poly in polys])
    polys = [sp.expand(poly * denominator) for poly in polys]
    common = sp.gcd(sp.gcd(polys[0], polys[1]), polys[2])
    if common != 0:
        polys = [sp.cancel(poly / common) for poly in polys]
    return [sp.Poly(poly, t, domain=sp.QQ) for poly in polys]


def proportional(left, right):
    ratio = None
    for p, q in zip(left, right):
        if p.is_zero and q.is_zero:
            continue
        if p.is_zero or q.is_zero:
            return False, None
        candidate = sp.cancel(p.as_expr() / q.as_expr())
        if t in candidate.free_symbols:
            return False, None
        if ratio is None:
            ratio = candidate
        elif sp.simplify(candidate - ratio) != 0:
            return False, None
    return True, ratio


results = []
for operator_path in sorted((ROOT / 'reference/data').glob('*_operator_exact.json')):
    name = operator_path.name.replace('_operator_exact.json', '')
    model_path = ROOT / f'reference/models/{name}.json'
    if not model_path.exists():
        continue
    model = json.loads(model_path.read_text())
    monomials = model.get('monomials', {})
    if monomials.get('4') or any(k not in ('3', '4') and v for k, v in monomials.items()):
        continue
    coeff = {(3, 0): 0, (2, 1): 0, (1, 2): 0, (0, 3): 0}
    for p_exp, q_exp, value in monomials.get('3', []):
        coeff[(int(p_exp), int(q_exp))] += sp.Rational(value)
    values = {
        A: coeff[(3, 0)], B: coeff[(2, 1)],
        C: coeff[(1, 2)], D: coeff[(0, 3)],
    }
    specialization = primitive_tuple([poly.subs(values) for poly in Ps])
    archived_record = json.loads(operator_path.read_text())
    if (
        'coefficients' in archived_record
        and isinstance(archived_record['coefficients'], list)
        and archived_record['coefficients']
        and isinstance(archived_record['coefficients'][0], dict)
    ):
        archived = [
            sum(sp.Rational(value) * t ** int(power) for power, value in row.items())
            for row in archived_record['coefficients']
        ]
    elif 'operator_coefficients' in archived_record:
        archived = [
            sp.sympify(expr, locals={'alpha': t})
            for expr in archived_record['operator_coefficients']
        ]
    else:
        continue
    archived = primitive_tuple(archived)
    ok, ratio = proportional(specialization, archived)
    record = {
        'example': name,
        'match': bool(ok),
        'ratio': str(ratio),
        'universal_degrees': [int(poly.degree()) for poly in specialization],
        'archive_degrees': [int(poly.degree()) for poly in archived],
    }
    results.append(record)
    print(record)

out = ROOT / 'checks/general_cubic_specialization_checks.json'
out.write_text(json.dumps(results, indent=2) + '\n')
if not results or not all(record['match'] for record in results):
    raise SystemExit('exact specialization verification failed')
