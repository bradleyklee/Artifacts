#!/usr/bin/env python3
from __future__ import annotations

import sympy as sp
from compute_mesh_area_series import compute

TERMS = 20
coeffs = compute(TERMS)['coeffs']
prime_exponents: dict[int, int] = {}
for n in range(2, TERMS + 1):
    denominator = sp.denom(sp.factor(n * coeffs[n]))
    for prime, exponent in sp.factorint(denominator).items():
        required = (exponent + n - 2) // (n - 1)
        prime_exponents[prime] = max(prime_exponents.get(prime, 0), required)

C = int(sp.prod(p**e for p, e in prime_exponents.items()))
assert C == 54 * 2089**2
for n in range(2, TERMS + 1):
    assert sp.denom(sp.factor(n * coeffs[n] * C**(n - 1))) == 1

print('terms checked:', TERMS)
print('minimal denominator-clearing C through these terms:', C)
print('factorization:', sp.factorint(C))
print('PASS')
