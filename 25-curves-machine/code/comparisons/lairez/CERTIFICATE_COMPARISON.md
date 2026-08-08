# Certificate validity and equivalence

Date: 2026-08-02. Research owner: Bradley Klee. Unpublished; NO POACHING.

## Pierre-side exact object

The port optionally transports the projective Griffiths--Dwork homotopy into
an affine rational one-form `beta=beta_p dp+beta_q dq`. At a pole-lowering step
write

```text
P = R + Gp*F_p + Gq*F_q + Gz*F_z,
A = (Gp-p*Gz)|z=1,
B = (Gq-q*Gz)|z=1.
```

Then, for `f=2H-alpha`, the exact step is

```text
P/f^k - R/f^k - div(G)/((k-1)f^(k-1))
    = d[(B dp-A dq)/((k-1)f^(k-1))].
```

The certificate is differentiated with every parameter derivative and summed
with the final normalized operator coefficients. The implementation verifies
directly that

```text
d beta = sum_j P_j(alpha) * d_alpha^j(2 dp dq/f).
```

This validation does not depend on the Klee primitive or stored operator.

## Triangle--square equivalence result

Pierre's port finds the same primitive normalized order-two operator and its
ambient one-form passes the exact residual check. A separate bridge then gives
that operator to Klee's support-driven exact-image solver, without a candidate
primitive. The reconstructed 71-term numerator is exactly equal
coefficient-for-coefficient to the stored Klee numerator over `rho^3`, where
`rho=(2H)_p=2H_p`.

Thus the two routes certify the same differential identity. In the canonical
Klee curve gauge, their triangle--square certificate is literally identical,
not merely equivalent up to a locally constant term.

## Timing interfaces

Keep these separately measurable:

```text
L0  Lairez-style operator only
L1  Lairez-style operator plus affine homotopy certificate
K0  Klee full support-driven operator plus curve primitive
H0  Lairez operator followed by Klee curve-primitive reconstruction
```

For triangle--square, `L1` takes about 5.11 seconds in the first certificate
run (2.70 reduction + 2.41 assembly), while `K0` has a 9.97-second median.
The initially unoptimized `H0` total is about 10.7--11.1 seconds because both
sides rebuild related exact-image matrices. The clean optimization target is a
data bridge that reuses Pierre's image/profile data while leaving both
algorithms independently callable.

## Square--hexagon scaling result

Certificate tracking through the reductions reaches order four without a
material change to the reduction profile (about 158 seconds in the bounded
run). Canonically combining the homotopy pieces into one rational one-form and
verifying one globally expanded residual did not finish within a 360-second
total bound. The run was stopped after more than 190 seconds in certificate
assembly/verification.

This is not a failed mathematical certificate: the seven pole-lowering
homotopies are retained and each is defined by the displayed exact identity.
It is a failure of the expanded representation. The next implementation should
serialize a structured sum of homotopy terms and verify each local step
fraction-free, avoiding global rational canonicalization.
