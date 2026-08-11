#!/usr/bin/env python3
"""Independent numerical audit of the trefoil symplectic period.

No closed-form time form is used in the numerical period computation.
At each point of the parametrized curve in R^4, finite-difference tangent
vectors are formed and the constrained Hamiltonian vector field is solved
from i_X omega_0 = -dH on the tangent plane.  The resulting dt/dtheta is
integrated around the curve.  A second check computes the polygonal line
integral of lambda_0 and differentiates it numerically with respect to E.
"""
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
J = np.array([[0.,1.,0.,0.],[-1.,0.,0.,0.],
              [0.,0.,0.,1.],[0.,0.,-1.,0.]])


def u_of_E(E):
    lo, hi = 0.0, max(1.0, E**(1/3)+1.0)
    while hi**3 + hi**2 < E:
        hi *= 2.0
    for _ in range(100):
        mid = (lo+hi)/2.0
        if mid**3 + mid**2 < E:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2.0


def point(u, th):
    return np.array([
        u**1.5*math.cos(3*th), u**1.5*math.sin(3*th),
        u*math.cos(2*th),       u*math.sin(2*th)])


def curve(u, th):
    th = np.asarray(th)
    return np.column_stack((
        u**1.5*np.cos(3*th), u**1.5*np.sin(3*th),
        u*np.cos(2*th),      u*np.sin(2*th)))


def analytic_period(E):
    u = u_of_E(E)
    return math.pi*(9*u+4)/(3*u+2)


def constrained_period(E, ntheta=720):
    """Numerically solve the constrained Hamiltonian flow on each tangent plane."""
    u = u_of_E(E)
    dth = 1.0e-6
    du = min(max(1.0e-8, 1.0e-6*max(1.0,u)), 0.10*u)
    inv_speed = []
    for th in np.linspace(0.0, 2*math.pi, ntheta, endpoint=False):
        r = point(u, th)
        ru = (point(u+du, th)-point(u-du, th))/(2*du)
        rt = (point(u, th+dth)-point(u, th-dth))/(2*dth)
        B = [ru, rt]
        # Equations omega_0(X,B_j) = -dH(B_j), X=c_0 ru+c_1 rt.
        M = np.array([[B[k] @ J @ B[j] for k in range(2)] for j in range(2)])
        rhs = np.array([-2.0*r @ B[j] for j in range(2)])
        c = np.linalg.solve(M, rhs)
        inv_speed.append(1.0/c[1])  # dt/dtheta
    return 2*math.pi*float(np.mean(inv_speed))


def polygon_action(E, n=60000):
    """Polygonal integral of lambda_0=(1/2)sum(x dy-y dx) on K_E."""
    u = u_of_E(E)
    th = np.linspace(0.0, 2*math.pi, n, endpoint=False)
    P = curve(u, th)
    Q = np.roll(P, -1, axis=0)
    return 0.5*float(np.sum(
        P[:,0]*Q[:,1]-P[:,1]*Q[:,0]
        + P[:,2]*Q[:,3]-P[:,3]*Q[:,2]))


def action_derivative(E):
    de = max(1.0e-8, 2.0e-5*E)
    if E-de <= 0:
        de = 0.2*E
    return (polygon_action(E+de)-polygon_action(E-de))/(2*de)

energies = [1e-4, 1e-3, 1e-2, 0.05, 0.10, 4/27, 0.20, 1.0]
records=[]
for E in energies:
    u=u_of_E(E)
    ta=analytic_period(E)
    tn=constrained_period(E)
    td=action_derivative(E)
    records.append({
        'E':E, 'u':u,
        'T_closed':ta,
        'T_constrained_numeric':tn,
        'relerr_constrained':abs(tn-ta)/abs(ta),
        'dA_dE_polygon_numeric':td,
        'relerr_action_derivative':abs(td-ta)/abs(ta),
    })

out={
    'method_period': 'finite-difference tangent plane + ambient omega_0 constrained Hamiltonian solve + theta quadrature',
    'method_action': 'polygonal integral of lambda_0 on K_E + centered finite difference in E',
    'records': records,
    'max_relerr_constrained': max(r['relerr_constrained'] for r in records),
    'max_relerr_action_derivative': max(r['relerr_action_derivative'] for r in records),
}
(HERE/'numerical_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('max constrained-flow relative error:',out['max_relerr_constrained'])
print('max polygon-action derivative relative error:',out['max_relerr_action_derivative'])
for r in records:
    print(f"E={r['E']:.12g} T={r['T_closed']:.12g} flow={r['T_constrained_numeric']:.12g} dA/dE={r['dA_dE_polygon_numeric']:.12g}")
