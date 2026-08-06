"""Derive and verify the Laurent-polynomial side exactly.

The computation uses explicit Laurent-polynomial coefficient extraction,
rational differentiation, and named recurrence transformations. It does not
call sympy.simplify.
"""
from pathlib import Path
import json
import sympy as sp

OUT = Path(__file__).parent

n, w, y, t, E = sp.symbols("n w y t E")

B = sp.expand((1+w)**3 / w**2)
C = sp.expand((1+y)**2 * (y**2 - 4*y + 1)**2 / y**3)
Phi = sp.factor(B*C)

# One-variable Laurent certificate for c_n=[C(y)^n]_0.
P0 = sp.Rational(128,3)*(n+1)*(2*n+1)*(2*n+3)*(3*n+5)
P1 = -sp.Rational(8,27)*(2*n+3)*(3*n+2)*(27*n**2+81*n+59)
P2 = sp.Rational(1,27)*(n+2)*(3*n+2)*(3*n+4)*(3*n+5)

certificate_poly = (
    27*n**3*y**8 - 270*n**3*y**7 + 540*n**3*y**6
    + 486*n**3*y**5 + 1026*n**3*y**4 + 486*n**3*y**3
    + 540*n**3*y**2 - 270*n**3*y + 27*n**3
    + 99*n**2*y**8 - 1008*n**2*y**7 + 2052*n**2*y**6
    + 1800*n**2*y**5 + 4482*n**2*y**4 + 1800*n**2*y**3
    + 2052*n**2*y**2 - 1008*n**2*y + 99*n**2
    + 114*n*y**8 - 1176*n*y**7 + 2412*n*y**6
    + 2112*n*y**5 + 6612*n*y**4 + 2112*n*y**3
    + 2412*n*y**2 - 1176*n*y + 114*n
    + 40*y**8 - 416*y**7 + 856*y**6 + 752*y**5
    + 3200*y**4 + 752*y**3 + 856*y**2 - 416*y + 40
)

R = sp.factor(
    (y-1)*(y+1)*(y**2-4*y+1)*certificate_poly
    / (81*y**6)
)

residual = sp.cancel(
    P0 + P1*C + P2*C**2
    - y*sp.diff(R,y)
    - n*y*sp.diff(C,y)*R/C
)
assert sp.fraction(residual)[0] == 0

# Multiplication by C^n and constant-term extraction yields:
# P0*c_n + P1*c_(n+1) + P2*c_(n+2) = 0.

# The binomial factor b_n=[B(w)^n]_0=binomial(3n,2n).
b_ratio_1 = sp.factor(
    sp.Rational(3,2)*(3*n+1)*(3*n+2)
    / ((n+1)*(2*n+1))
)
b_ratio_2 = sp.factor(
    b_ratio_1
    * sp.Rational(3,2)*(3*n+4)*(3*n+5)
    / ((n+2)*(2*n+3))
)

# Substitute c_n=A_n/b_n and clear the common factor.
coeff_A_n = sp.factor(P0)
coeff_A_n1 = sp.factor(P1/b_ratio_1)
coeff_A_n2 = sp.factor(P2/b_ratio_2)

common = sp.factor(
    4*(n+1)*(2*n+1)*(2*n+3)
    / (243*(3*n+1))
)

reduced = [
    sp.factor(coeff_A_n/common),
    sp.factor(coeff_A_n1/common),
    sp.factor(coeff_A_n2/common),
]

expected_reduced = [
    2592*(3*n+1)*(3*n+5),
    -12*(27*n**2+81*n+59),
    (n+2)**2,
]
assert all(
    sp.expand(left-right) == 0
    for left, right in zip(reduced, expected_reduced)
)

# Shift n -> n-1 to obtain the paper recurrence.
recurrence = (
    (n+1)**2,
    -12*(27*n**2+27*n+5),
    2592*(3*n-2)*(3*n+2),
)

# Generate exact coefficients.
A = [sp.Integer(1), sp.Integer(60)]
for k in range(1, 25):
    next_value = sp.cancel(
        (
            12*(27*k**2+27*k+5)*A[k]
            - 2592*(3*k-2)*(3*k+2)*A[k-1]
        ) / (k+1)**2
    )
    assert sp.denom(next_value) == 1
    A.append(sp.Integer(next_value))

# Verify direct constant terms for the first ten coefficients.
def laurent_constant_term(expr, variables):
    result = sp.expand(expr)
    for variable in variables:
        terms = sp.Add.make_args(result)
        result = sp.Add(*[
            term for term in terms
            if term.as_powers_dict().get(variable, 0) == 0
        ])
        result = sp.expand(result)
    return result

direct = []
power = sp.Integer(1)
for k in range(10):
    direct.append(sp.Integer(laurent_constant_term(power, (w,y))))
    power = sp.expand(power*Phi)
assert direct == A[:10]

# Recurrence-to-ODE translation.
Y = sum(A[k]*t**k for k in range(len(A)))
L_t_Y = sp.expand(
    t*(108*t-1)*(216*t-1)*sp.diff(Y,t,2)
    + (69984*t**2-648*t+1)*sp.diff(Y,t)
    + 60*(216*t-1)*Y
)
for k in range(len(A)-2):
    assert L_t_Y.coeff(t,k) == 0

# Verify exact change from Hamiltonian energy E to t=E/32.
A2E = E*(27*E-8)*(27*E-4)
A1E = 2187*E**2-648*E+32
A0E = 15*(27*E-4)

assert sp.expand(
    A2E.subs(E,32*t)/32**2
    - t*(108*t-1)*(216*t-1)
) == 0
assert sp.expand(
    A1E.subs(E,32*t)/32
    - (69984*t**2-648*t+1)
) == 0
assert sp.expand(
    A0E.subs(E,32*t)
    - 60*(216*t-1)
) == 0

data = {
    "B": sp.sstr(B),
    "C": sp.sstr(C),
    "Phi": sp.sstr(Phi),
    "certificate_R": sp.sstr(R),
    "certificate_residual": "0",
    "recurrence": (
        "(n+1)^2*A[n+1] - 12*(27*n^2+27*n+5)*A[n] "
        "+ 2592*(3*n-2)*(3*n+2)*A[n-1] = 0"
    ),
    "first_coefficients": [str(value) for value in A],
    "operator_t": {
        "A2": "t*(108*t-1)*(216*t-1)",
        "A1": "69984*t^2-648*t+1",
        "A0": "60*(216*t-1)",
    },
}
(OUT / "laurent_data.json").write_text(
    json.dumps(data, indent=2),
    encoding="utf-8",
)
(OUT / "coefficients.txt").write_text(
    ", ".join(str(value) for value in A) + "\n",
    encoding="utf-8",
)
(OUT / "certificate_R.txt").write_text(
    sp.sstr(R) + "\n",
    encoding="utf-8",
)

print("Laurent certificate residual: 0")
print("First coefficients:", A[:10])
print("Same t-operator obtained exactly")
