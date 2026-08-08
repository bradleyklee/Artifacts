# ALG-012: Watson physics convention adapter

## Internal versus physical coordinates

```text
Internal normalized sphere: X+Y+Z=1, energy=H.
Physical fixed-J sphere: Ja^2+Jb^2+Jc^2=L2=J(J+1) quantum mechanically.
Canonical classical chart: p=Ja, phi=atan2(Jc,Jb), {phi,p}=1.
Normalize only through Ja=sqrt(L2)*lambda when desired.
```

Never silently set `L2=1` in imported spectroscopic parameters.  Powers of
`L2` carry the physical units and the fixed-J dependence.

## Ladder dictionary

```text
J_plus = Jb+i*Jc
J_plus^m+J_minus^m -> 2*(L2-p^2)^(m/2)*cos(m*phi)
1/2*[Q,J_plus^m+J_minus^m]_+ -> Q*(classical ladder sum)
```

The second line is a principal-symbol rule.  Quantum ordering and lower-order
commutator corrections must remain in a separate quantization layer.

## Algorithm classification

```text
Watson A reduction through sextic:
  harmonic support {0,2}; use DihedralODE after combining coefficients.

Watson S reduction through quartic:
  harmonic support {0,2,4}; use general implicit-angle reduction.

Watson S reduction through sextic:
  harmonic support {0,2,4,6}; use general implicit-angle reduction.
```

Always record reduction (`A` or `S`) and axis representation.  Parameters with
the same informal name do not necessarily multiply the same operator.

## Validation

```text
reconstruct A*Ja^2+B*Jb^2+C*Jc^2 from the ladder form exactly
check expected harmonic support at every centrifugal order
check all classical monomials remain even in component variables
retain L2 symbolically until the final normalized-sphere conversion
```
