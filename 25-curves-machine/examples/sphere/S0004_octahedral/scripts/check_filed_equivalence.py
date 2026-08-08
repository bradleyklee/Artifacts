#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
direct = json.loads((ROOT/'results/octahedral_direct_degree7_certificate.json').read_text())
invariant = json.loads((ROOT/'results/octahedral_exact_invariant_certificate.json').read_text())
transform = json.loads((ROOT/'transforms/T01_direct_to_invariant/transform.json').read_text())
alpha = sp.symbols('alpha')
local = {'alpha': alpha}
d = [sp.sympify(x, locals=local) for x in direct['operator_coefficients_low_to_high']]
q = [sp.sympify(x, locals=local) for x in invariant['operator_coefficients_low_to_high']]
scale = sp.sympify(transform['operator_common_scale'])
assert all(sp.cancel(a-scale*b)==0 for a,b in zip(d,q))
assert direct['exact_quotient_residual']=='0'
assert invariant['exact_quotient_residual']=='0'
assert transform['forward_map']=={'t':'v*(1-v)','w':'y*(1-2*v)'}
print('OCTAHEDRAL_FILED_EQUIVALENCE_PASS scale=8 residuals=0')
