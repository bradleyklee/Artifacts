# ALG-010: even-sphere testing and degree-bound refinement loop

## Scope

Accept only `H(Jx^2,Jy^2,Jz^2)`.  Reject or defer every monomial with an odd
power of an angular-momentum component.  In particular, do not use an
odd-power symmetry-breaking perturbation to improve a bound in the even
physical branch.

## Loop

```text
FOR each support stratum and parameter sample:
  construct F(u,v,alpha)=H((1-u)v,(1-u)(1-v),u)-alpha
  verify D_alpha and D_v preserve <F,y^2-u*v*(1-v)>
  record deg_u(F), deg_v(F), disc_u(F), and v-reflection symmetry
  PROVE the quotient bound deg_u(P)<deg_u(F)

  obtain a candidate operator inductively or from a comparison method
  FOR every consecutive angular numerator degree d=0,1,2,...:
    create fresh linear-system unknowns
    build the exact certificate matrix
    record rows, columns, rank, nullity, sparsity, runtime
    IF an operator-bearing null vector occurs:
      reconstruct the primitive and verify exact residual zero
      declare d minimal only because every smaller shell was completed
      BREAK
    IF a resource cap is reached:
      return BLOCKED with the next untested shell

  IF DihedralODE also applies:
    repeat every consecutive lambda numerator degree
    translate both primitives to the same quotient field
    solve their common operator normalization
    test literal equality first, then exact/gauge equivalence

AGGREGATE closure degree by fiber degree, angular degree, symmetry stratum,
discriminant degree, and matrix sparsity.
INFER candidate bounds only from completed shells.
PROMOTE an empirical bound to a theorem only after a finite-space proof.
```

## Bound ledger

Maintain three separate labels:

1. `proven`: follows from quotient or pole-reduction algebra;
2. `empirical`: every tested model closed within the stated shell;
3. `blocked`: computation ended before the next shell was tested.

Never convert `blocked` into `no relation`, and never report a sufficient
degree as minimal without replaying all smaller consecutive shells.
