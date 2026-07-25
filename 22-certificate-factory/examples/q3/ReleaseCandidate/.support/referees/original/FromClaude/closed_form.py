"""
Closed form for a(n) via Lagrange inversion.

Derivation:
  Functional equation:      4*A = 3 + x + A^3
  Substitute A = 1 + t:     t = x + 3*t^2 + t^3
  Rearrange for x:          x = t*(1 - 3*t - t^2) = t / f(t),  f(t) = 1/(1-3t-t^2)

  This is the Lagrange-inversion shape t = x*f(t), so
      [x^n] t = (1/n) * [t^(n-1)] f(t)^n

  Expand f(t)^n = (1-(3t+t^2))^(-n) via the negative-binomial theorem, then
  the ordinary binomial theorem on (3t+t^2)^k; extracting [t^(n-1)] forces
  k+j = n-1 and collapses the double sum to a single sum over k.

Result:
  a(0) = 1
  a(n) = (1/n) * sum_{k=ceil((n-1)/2)}^{n-1} C(n+k-1,k) * C(k, n-1-k) * 3^(2k-n+1),  n >= 1

This is verified below against the 16 terms produced independently by the
matrix/recurrence route in literal_translation.py (Q3), and separately checked
against Seiichi Manyama's binomial-sum formula listed on OEIS A120590 -- the
two agree on all computed terms, though algebraic identity of the two sums for
general n has not been proven here, only checked numerically.
"""

from sympy import Rational, binomial, Integer, simplify

REFERENCE_TERMS = [1, 1, 3, 19, 150, 1326, 12558, 124590, 1278189, 13449205,
                   144342627, 1573990275, 17389407984, 194228357568,
                   2189610888840, 24881753664840]


def a_closed(n):
    if n == 0:
        return Integer(1)
    total = 0
    for k in range((n - 1 + 1) // 2, n):      # k = ceil((n-1)/2) .. n-1
        j = n - 1 - k
        if j < 0 or j > k:
            continue
        total += binomial(n + k - 1, k) * binomial(k, j) * 3**(2 * k - n + 1)
    return simplify(Rational(1, n) * total)


def a_manyama(n):
    """Formula credited to Seiichi Manyama on OEIS A120590, for comparison only."""
    if n == 0:
        return Integer(1)
    total = 0
    for k in range(0, (n - 1) // 2 + 1):
        total += 3**(n - 1 - 2 * k) * binomial(2 * n - 2 - k, n - 1) * binomial(n - 1 - k, k)
    return simplify(Rational(1, n) * total)


if __name__ == "__main__":
    print(f"{'n':>3} {'a_closed(n)':>18} {'matches recurrence?':>20} {'matches Manyama?':>18}")
    for n, ref in enumerate(REFERENCE_TERMS):
        mine = a_closed(n)
        many = a_manyama(n)
        print(f"{n:>3} {mine!s:>18} {str(mine == ref):>20} {str(mine == many):>18}")
