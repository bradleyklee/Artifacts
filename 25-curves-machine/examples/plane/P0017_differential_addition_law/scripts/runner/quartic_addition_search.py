#!/usr/bin/env python3
"""Core symbolic tests for a candidate rational addition law on H(p,q)=alpha.

The Hamiltonian time differential is omega = dq/H_p.  For a candidate map
M(P1,P2)=(P,Q), invariance is equivalent to the two polynomial/rational PDEs

 H_p(P_i) * dQ/dq_i - H_q(P_i) * dQ/dp_i = H_p(M),  i=1,2,

where the derivatives on the left are ordinary partial derivatives of the
candidate rational function Q(p1,q1,p2,q2).
"""
from __future__ import annotations

import sympy as sp


def candidate_residuals(H, p, q, alpha, P, Q, p1, q1, p2, q2):
    """Return curve and invariant-differential residuals for a candidate map.

    H must be a SymPy expression in symbols p,q,alpha. P,Q are candidate sum
    coordinates in p1,q1,p2,q2 and alpha.
    """
    Hp = sp.diff(H, p)
    Hq = sp.diff(H, q)

    def at(expr, pp, qq):
        return sp.expand(expr.subs({p: pp, q: qq}))

    Hp1, Hq1 = at(Hp,p1,q1), at(Hq,p1,q1)
    Hp2, Hq2 = at(Hp,p2,q2), at(Hq,p2,q2)
    HpM = at(Hp,P,Q)

    curve = sp.together(at(H,P,Q) - alpha)
    diff1 = sp.together(Hp1*sp.diff(Q,q1) - Hq1*sp.diff(Q,p1) - HpM)
    diff2 = sp.together(Hp2*sp.diff(Q,q2) - Hq2*sp.diff(Q,p2) - HpM)
    return curve, diff1, diff2


PSEUDOCODE = r"""
INPUT: quartic Hamiltonian H(p,q; parameters), energy alpha.

1. Determine whether the normalized level curve has genus one, or whether the
   time differential descends to a genus-one quotient.
2. Search for a rational section O(alpha).  Without O there is no binary group
   law over the coefficient field; continue instead with a ternary torsor law.
3. Choose pole bounds from L(2O), L(3O), or from observed denominator divisors.
4. Set rational ansatz M(P1,P2)=(P,Q).
5. Impose:
      H(P,Q)=alpha,
      M(P,O)=P, M(O,Q)=Q,
      H_p(P_i) Q_{q_i} - H_q(P_i) Q_{p_i} = H_p(M), i=1,2.
6. Solve coefficient equations modularly, reconstruct over Q(parameters), and
   verify exactly modulo the two input curve ideals.
7. If binary search fails because no rational section exists, search ternary
   tau(P,Q,R) with
      tau^*omega = omega_P - omega_Q + omega_R.
8. Once a rational point P0 is found after specialization, recover a binary law
   by P (+) Q = tau(P,P0,Q), then generate/extrapolate rational points.
"""


if __name__ == "__main__":
    print(PSEUDOCODE)
