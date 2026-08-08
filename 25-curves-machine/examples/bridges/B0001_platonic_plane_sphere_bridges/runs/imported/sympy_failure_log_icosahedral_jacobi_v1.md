# SymPy failure log — icosahedral Jacobi work

## 1. Nested radical series

Operation:

    series(alpha_of_m.subs(m,m_edge), beta, 0, 5)

Observed behavior:

- entered assumption checking and algebraic root sorting;
- attempted quartic root heuristics and multivariate integer factorization;
- exceeded the 60-second cap.

Mathematical status:

- not an obstruction;
- recursive coefficient solving and numerical continuation both succeed.

Bypass:

- keep `alpha(z)` exact;
- keep `m(beta)` implicit in the exact sextic;
- recurse one series coefficient at a time;
- use `mpmath.findroot` for branch continuation.

## 2. Branch-sensitive radical simplification

Operation:

    simplify((1-3*z(m)/4)^(1/4)*sqrt(1+m)
             -(1-m+m^2)^(1/4))

Observed behavior:

- SymPy did not prove the identity because the fourth-root branch is not fixed.

Bypass:

- compare fourth powers exactly;
- keep the root/cycle convention as separate metadata.

## 3. Simultaneous high-order series at the second locality

Operation:

- generic symbolic solve near `alpha=-4/9`.

Observed behavior:

- expensive algebraic root sorting;
- exceeded the execution cap.

Bypass:

- solve one coefficient per order;
- avoid generic solve over large algebraic expressions.

## 4. Generated verifier used mathematical caret syntax

Operation:

    python verify_icosahedral_branchpoint_tschirnhaus_map_v1.py

Observed behavior:

- the generated Python source contained expressions such as `beta^3`;
- Python interpreted `^` as bitwise XOR and raised `TypeError`.

Bypass/fix:

- replace mathematical caret powers with Python `**`;
- rerun the exact symbolic remainder test.

This was a code-generation defect, not a SymPy algebra defect.
