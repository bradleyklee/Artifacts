#!/usr/bin/env python3
"""Autonomous exact / high-precision checks for the circle-triangle-square period certificate."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import sympy as sp
import mpmath as mp


HERE=Path(__file__).resolve().parent
level_generator=HERE/'generate_quantized_levels.py'
if not level_generator.is_file():
    level_generator=HERE.parent/'scripts'/'generate_quantized_levels.py'
subprocess.run([sys.executable,str(level_generator),'--check'],cwd=level_generator.parent.parent if level_generator.parent.name=='scripts' else HERE,check=True,stdout=subprocess.PIPE,text=True)

# Symbols and curve data.
a, p, q, x, beta = sp.symbols("a p q x beta")
K = p**2 + q**2 + q**3 - 3*p**2*q + (p**4 - 6*p**2*q**2 + q**4)/4
rho = sp.diff(K, p)

P0 = 27 - 261*a + 645*a**2 + 408*a**3
P1 = -18 + 426*a - 2827*a**2 + 5736*a**3 + 1632*a**4
P2 = a*(a+6)*(4*a-1)*(8*a-1)*(17*a-3)

u = [
    -6*a*(136*a**3 + 411*a**2 - 211*a + 14),
    -2*(1224*a**4 - 6765*a**3 + 3412*a**2 - 381*a + 18),
    -2448*a**4 + 4410*a**3 + 6337*a**2 - 2811*a + 210,
    -816*a**4 - 31170*a**3 + 7331*a**2 + 1719*a - 66,
    -2*(12240*a**3 + 9535*a**2 - 5142*a + 363),
    -2*(2448*a**3 - 6185*a**2 + 2256*a + 39),
    14*(3842*a**2 - 1473*a + 60),
    2*(20162*a**2 - 7665*a + 348),
    36*(340*a**2 - 129*a + 6),
    4*(340*a**2 - 129*a + 6),
]
v = [
    -816*a**4 - 650*a**3 + 3475*a**2 - 1089*a + 102,
    -3*(272*a**4 - 2322*a**3 + 8515*a**2 - 2733*a + 258),
    -2*(816*a**3 - 16195*a**2 + 5646*a - 543),
    -2*(11152*a**3 - 37113*a**2 + 11910*a - 1125),
    -10*(1632*a**3 + 6286*a**2 - 2343*a + 228),
    -2*(1632*a**3 + 61502*a**2 - 21579*a + 2076),
    -28*(1972*a**2 - 687*a + 66),
    -4*(1972*a**2 - 687*a + 66),
]
V = sum(u[j]*q**j for j in range(10)) + p**2*sum(v[j]*q**j for j in range(8))

# Exact curve/certificate checks.
assert sp.factor(rho - p*(p**2 + 2 - 6*q - 3*q**2)) == 0
assert sp.factor(P1 - (sp.diff(P2, a) - 34*P2/(17*a-3))) == 0
Dalpha = lambda f: sp.diff(f, p)/rho
omega = 2/rho
Aomega = P0*omega + P1*Dalpha(omega) + P2*Dalpha(Dalpha(omega))
Xi = V/rho**3
dXi_curve = sp.diff(Xi, q) - sp.diff(K, q)/rho * sp.diff(Xi, p)
assert sp.factor(sp.together(Aomega.subs(a, K) - dXi_curve.subs(a, K))) == 0

# Exact critical-point and Wick-center checks.
s_plus = {p: sp.Rational(1,2), q: -1 + sp.sqrt(7)/2}
c_tunnel = {p: 0, q: -1}
assert sp.simplify(sp.diff(K,p).subs(s_plus)) == 0 and sp.simplify(sp.diff(K,q).subs(s_plus)) == 0
assert sp.simplify(K.subs(s_plus)) == sp.Rational(1,8)
assert sp.simplify(sp.diff(K,p).subs(c_tunnel)) == 0 and sp.simplify(sp.diff(K,q).subs(c_tunnel)) == 0
assert sp.simplify(K.subs(c_tunnel)) == sp.Rational(1,4)
assert sp.factor(sp.hessian(K,(p,q)).subs(c_tunnel).det()) == -5
assert sp.factor(sp.hessian(K,(p,q)).subs(s_plus).det()) == -14

# Exact p-Wick expansion about the center between the reflected wells.
U, Q = sp.symbols("U Q", real=True)
K_wick_center = sp.expand(K.subs({p: sp.I*U, q: -1+Q}))
expected_wick_center = sp.Rational(1,4) + (U**4 + 6*U**2*Q**2 - 10*U**2 + Q**4 - 2*Q**2)/4
assert sp.expand(K_wick_center - expected_wick_center) == 0
# Tangent-matched display convention: the Wick substitution preserves energy.
P,Q0 = sp.symbols("P Q0", real=True)
Hreal_fig = P**2-Q0**2+P**4/sp.Integer(25)-sp.Rational(6,5)*P**2*Q0**2+Q0**4
Hip_fig = -P**2-Q0**2+P**4/sp.Integer(25)+sp.Rational(6,5)*P**2*Q0**2+Q0**4
assert sp.expand(Hreal_fig.subs(P,sp.I*P)-Hip_fig)==0
assert sp.expand(Hreal_fig.subs(P,0)-Hip_fig.subs(P,0))==0
assert sp.diff(Hreal_fig,P).subs(P,0)==0
assert sp.diff(Hip_fig,P).subs(P,0)==0

# Integer recurrences for the real branch and the auxiliary saddle-normalized complex branch.
def real_terms(N: int) -> list[int]:
    out = [0]*N
    out[0] = 1
    for n in range(1,N):
        g = lambda k: out[k] if k >= 0 else 0
        num = (12*(105*n*n-173*n+77)*g(n-1)
               -32*(1747*n*n-5908*n+5089)*g(n-2)
               +768*(2*n-5)*(494*n-1267)*g(n-3)
               +278528*(2*n-7)*(2*n-5)*g(n-4))
        out[n], rem = divmod(num, 9*n*n)
        assert rem == 0
    return out

def complex_terms(N: int) -> list[int]:
    out = [0]*N
    out[0] = 1
    for n in range(1,N):
        g = lambda k: out[k] if k >= 0 else 0
        num = (-16*(59*n*n-178*n+113)*g(n-1)
               +112*(1440*n*n-3016*n+917)*g(n-2)
               +614656*(2*n-5)*(118*n-297)*g(n-3)
               -292576256*(2*n-7)*(2*n-5)*g(n-4))
        out[n], rem = divmod(num, n*n)
        assert rem == 0
    return out

A = real_terms(1000)
B = complex_terms(1000)
assert A[:6] == [1,12,372,15120,706020,35692272]
assert B[:6] == [1,96,20748,5604480,1675054500,530471120256]
assert all(t > 0 for t in A) and all(t > 0 for t in B)

# Scaled ODE checks.
Atr = sum(sp.Integer(A[n])*x**n for n in range(40))
Btr = sum(sp.Integer(B[n])*x**n for n in range(40))
R2 = x*(4*x+3)*(32*x-1)*(64*x-1)*(136*x-3)
R1 = 3342336*x**4 + 1468416*x**3 - 90464*x**2 + 1704*x - 9
R0 = 12*(69632*x**3 + 13760*x**2 - 696*x + 9)
assert all(sp.expand(R2*sp.diff(Atr,x,2)+R1*sp.diff(Atr,x)+R0*Atr).coeff(x,n)==0 for n in range(36))
C2 = x*(8*x-1)*(392*x-1)*(392*x+1)*(952*x+1)
C1 = 3510915072*x**4 - 287659008*x**3 - 468608*x**2 - 16*x + 1
C0 = 48*(18286016*x**3 - 729904*x**2 - 1505*x - 2)
assert all(sp.expand(C2*sp.diff(Btr,x,2)+C1*sp.diff(Btr,x)+C0*Btr).coeff(x,n)==0 for n in range(36))

# Page-normalized Abel identity at common interior points.  The page's T2 is
# the full green-cycle branch T2=sqrt(10/7)*T2_saddle.
mp.mp.dps = 80
for ztxt in ["0.06","0.07","0.08","0.09","0.10"]:
    z = mp.mpf(ztxt)
    xr = z/8
    xc = (mp.mpf(1)/8-z)/49
    T1 = mp.fsum(mp.mpf(A[n])*xr**n for n in range(500))
    T1p = mp.fsum(mp.mpf(A[n])*n*xr**(n-1)/8 for n in range(1,500))
    scale = mp.sqrt(mp.mpf(10)/7)
    T2 = scale*mp.fsum(mp.mpf(B[n])*xc**n for n in range(500))
    T2p = scale*mp.fsum(mp.mpf(B[n])*n*xc**(n-1)*(-1/mp.mpf(49)) for n in range(1,500))
    factor = z*(z+6)*(4*z-1)*(8*z-1)/(17*z-3)
    assert abs(factor*(T1*T2p-T2*T1p)-mp.sqrt(5)/mp.pi) < mp.mpf("1e-38")

# Analytic local solution Y at z=1/4, Y(1/4)=1.
Nloc = 45
cs = sp.symbols(f"c0:{Nloc}")
y = sum(cs[n]*beta**n for n in range(Nloc))
expr = sp.expand(P2.subs(a,beta+sp.Rational(1,4))*sp.diff(y,beta,2)
                 +P1.subs(a,beta+sp.Rational(1,4))*sp.diff(y,beta)
                 +P0.subs(a,beta+sp.Rational(1,4))*y)
sol = {cs[0]:sp.Integer(1)}
for k in range(Nloc-2):
    eq = sp.expand(expr.subs(sol)).coeff(beta,k)
    unknown = [c for c in cs if c in eq.free_symbols]
    if unknown:
        nxt = min(unknown,key=lambda c:int(str(c)[1:]))
        sol[nxt] = sp.simplify(sp.solve(eq,nxt)[0])
local_coeffs = [sol[cs[n]] for n in range(Nloc-2)]
assert local_coeffs[:6] == [
    1, -sp.Rational(27,25), sp.Rational(1221,500), -sp.Rational(85239,12500),
    sp.Rational(20966001,1000000), -sp.Rational(42578994843,625000000)
]

# Integerized center-normalized series printed on the page:
# T2(1/4-100x)=sum C_n x^n.
C = [sp.simplify(local_coeffs[n]*(-100)**n) for n in range(len(local_coeffs))]
assert all(c.is_Integer for c in C)
assert C[:6] == [1,108,24420,6819120,2096600100,681263917488]
Ctr = sum(C[n]*x**n for n in range(40))
zsub = sp.Rational(1,4)-100*x
center_ode = sp.expand(
    P2.subs(a,zsub)*sp.diff(Ctr,x,2)/10000
    -P1.subs(a,zsub)*sp.diff(Ctr,x)/100
    +P0.subs(a,zsub)*Ctr
)
assert all(center_ode.coeff(x,n)==0 for n in range(36))

# Exact harmonic data at the full p-Wick center for H=K/2.
H_wick_center = K_wick_center/2
Hw_hessian = sp.hessian(H_wick_center,(U,Q)).subs({U:0,Q:0})
assert Hw_hessian == sp.diag(-sp.Rational(5,2),-sp.Rational(1,2))
harmonic_frequency = sp.sqrt(Hw_hessian.det())
assert harmonic_frequency == sp.sqrt(5)/2
harmonic_period = 2*sp.pi/harmonic_frequency
assert sp.simplify(harmonic_period-4*sp.pi/sp.sqrt(5)) == 0

# High-precision Taylor continuation of T2 from z=1/8 to z=0.24,
# bypassing the apparent singularity z=3/17 in the upper half-plane.
def poly_local_coeffs(poly: sp.Expr, z0: mp.mpc) -> list[mp.mpc]:
    degree = int(sp.degree(poly,a))
    monomial = [sp.expand(poly).coeff(a,k) for k in range(degree+1)]
    out=[]
    for j in range(degree+1):
        val=mp.mpc(0)
        for k in range(j,degree+1):
            ck=mp.mpf(str(monomial[k]))
            val += ck*mp.binomial(k,j)*z0**(k-j)
        out.append(val)
    return out

def taylor_step(z0: mp.mpc, y0: mp.mpc, yp0: mp.mpc, h: mp.mpc, order: int=60):
    p2 = poly_local_coeffs(P2,z0)
    p1 = poly_local_coeffs(P1,z0)
    p0 = poly_local_coeffs(P0,z0)
    c=[mp.mpc(y0),mp.mpc(yp0)]
    for n in range(order-2):
        rhs=mp.mpc(0)
        for j in range(1,min(len(p2)-1,n)+1):
            k=n-j+2
            rhs += p2[j]*k*(k-1)*c[k]
        for j in range(0,min(len(p1)-1,n)+1):
            k=n-j+1
            rhs += p1[j]*k*c[k]
        for j in range(0,min(len(p0)-1,n)+1):
            k=n-j
            rhs += p0[j]*c[k]
        c.append(-rhs/(p2[0]*(n+2)*(n+1)))
    yh=mp.fsum(c[n]*h**n for n in range(len(c)))
    yph=mp.fsum(n*c[n]*h**(n-1) for n in range(1,len(c)))
    return yh,yph

def continue_segment(z0, z1, y0, yp0, max_step=mp.mpf("0.004")):
    delta=z1-z0
    steps=max(1,int(mp.ceil(abs(delta)/max_step)))
    h=delta/steps
    zcur=z0; ycur=y0; ypcur=yp0
    for _ in range(steps):
        ycur,ypcur=taylor_step(zcur,ycur,ypcur,h)
        zcur += h
    return ycur,ypcur

z0=mp.mpc("0.14")
xc=(mp.mpf(1)/8-z0)/49
y0=mp.fsum(mp.mpf(B[n])*xc**n for n in range(500))
yp0=mp.fsum(mp.mpf(B[n])*n*xc**(n-1)*(-1/mp.mpf(49)) for n in range(1,500))
path=[z0,z0+mp.mpc(0,"0.025"),mp.mpc("0.24","0.025"),mp.mpc("0.24")]
yc,ypc=y0,yp0
for za,zb in zip(path,path[1:]):
    yc,ypc=continue_segment(za,zb,yc,ypc)

bval=mp.mpf("-0.01")
yloc=mp.fsum(mp.mpf(str(sp.N(local_coeffs[n],90)))*bval**n for n in range(len(local_coeffs)))
yploc=mp.fsum(n*mp.mpf(str(sp.N(local_coeffs[n],90)))*bval**(n-1) for n in range(1,len(local_coeffs)))
ratio1=yc/yloc
ratio2=ypc/yploc
expected=mp.sqrt(mp.mpf(7)/10)
assert abs(ratio1-expected) < mp.mpf("1e-35")
assert abs(ratio2-expected) < mp.mpf("1e-35")
# The page branch rescales the saddle-normalized branch to value 1 at z=1/4.
assert abs(mp.sqrt(mp.mpf(10)/7)*ratio1-1) < mp.mpf("1e-35")
assert abs(mp.sqrt(mp.mpf(10)/7)*ratio2-1) < mp.mpf("1e-35")

# Direct full-green-oval quadrature.  With p=iU and q=-1+Q,
# i*omega=2 dQ/[U(5-U^2-3Q^2)].  The full oval contains both U sheets.
def full_green_period(z):
    z=mp.mpf(z)
    qmax=mp.sqrt(1-2*mp.sqrt(z))
    def integrand(theta):
        ct=mp.cos(theta)
        if abs(ct) < mp.mpf("1e-35"):
            theta=mp.pi/2-mp.mpf("1e-35")
            ct=mp.cos(theta)
        Qv=qmax*mp.sin(theta)
        Bv=Qv**4-2*Qv**2+1-4*z
        disc=(6*Qv**2-10)**2-4*Bv
        # stable expression for the small root U^2
        yv=2*Bv/(10-6*Qv**2+mp.sqrt(disc))
        Uv=mp.sqrt(yv)
        Dv=5-yv-3*Qv**2
        return qmax*ct/(Uv*Dv)
    return 8*mp.quad(integrand,[0,mp.pi/2])

def center_series_value(z):
    s=mp.mpf(1)/4-mp.mpf(z)
    return mp.fsum(mp.mpf(str(sp.N(C[n],90)))*(s/100)**n for n in range(len(C)))

for ztxt in ["0.249","0.24","0.23"]:
    z=mp.mpf(ztxt)
    normalized=mp.sqrt(5)/(4*mp.pi)*full_green_period(z)
    assert abs(normalized-center_series_value(z)) < mp.mpf("1e-20")

checks = [
    {"id": "figure_midpoint_action_quantization", "status": "pass", "kind": "numeric_replay"},
    {"id": "curve_and_rho", "status": "pass", "kind": "exact_symbolic"},
    {"id": "annihilator_factorization", "status": "pass", "kind": "exact_symbolic"},
    {"id": "exact_differential_certificate", "status": "pass", "kind": "exact_symbolic"},
    {"id": "critical_points_and_energies", "status": "pass", "kind": "exact_symbolic"},
    {"id": "wick_center_transform", "status": "pass", "kind": "exact_symbolic"},
    {"id": "real_and_complex_integer_series", "status": "pass", "kind": "exact_recurrence"},
    {"id": "scaled_ode_series_checks", "status": "pass", "kind": "exact_symbolic"},
    {"id": "abel_identity", "status": "pass", "kind": "high_precision"},
    {"id": "center_normalized_local_solution", "status": "pass", "kind": "exact_symbolic"},
    {"id": "harmonic_frequency_and_period", "status": "pass", "kind": "exact_symbolic"},
    {"id": "connection_across_apparent_singularity", "status": "pass", "kind": "high_precision"},
    {"id": "full_green_cycle_quadrature", "status": "pass", "kind": "high_precision"},
]
results = {
    "certificate": "circle_triangle_square_periods_v19_source_standardized",
    "status": "pass",
    "proof_level_check_count": len(checks),
    "checks": checks,
}
(HERE / "verification_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print("PASS: exact certificate, centers, harmonic frequency/period, printed series, Abel identity, and full green-cycle quadrature.")
print("Full green harmonic period = 4*pi/sqrt(5); page T2(1/4)=1.")
print(f"{len(checks)} proof-level checks passed; see verification_results.json and claim_index.json for row-by-row coverage.")
