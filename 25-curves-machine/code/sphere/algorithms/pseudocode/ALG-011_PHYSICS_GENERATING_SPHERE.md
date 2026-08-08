# ALG-011: physical fixed-J generating-function sphere curves

## Physics convention

```text
Fix L2=Jx^2+Jy^2+Jz^2.
Use the canonical pair p=Jz, phi, with {phi,p}=1.
Use energy=H, without the plane-curve factor of two.

s^2 = 1+kappa*p^2
G_kappa(p) = 2*(s-1)/kappa
H = epsilon(L2)+b(L2)*G_kappa(p)
    +eta*(L2-p^2)^(m/2)*cos(m*phi),  m even.
```

The article's spectroscopic dictionary is

```text
b^(J) = B_z^(J),
kappa^(J) = 4*Delta_K^(J)/B_z^(J).
```

The square root is not approximated during certification.  Adjoin `s` and work
modulo `s^2-1-kappa*p^2`.  Taylor expansion is used only for comparison with
Watson centrifugal-distortion coefficients.

## Exact angle elimination

```text
h1(p,s) = epsilon+b*G_kappa(p)
h2(p)   = eta*(L2-p^2)^(m/2)

D_p = partial_p + (kappa*p/s)*partial_s
rho = h2*D_p(h1)+(energy-h1)*D_p(h2)
p_dot^2 = -m^2*(energy-h1-h2)*(energy-h1+h2)
p_ddot  = (1/2)*D_p(p_dot^2)
```

All expressions are reduced to degree less than two in `s`.  This is the
algebraic extension of DihedralODE appropriate to the article's nonpolynomial
physical Hamiltonian.

## Testing/refinement loop

```text
FOR m in 2,4,6,...:
  reject odd m in the present even-component branch
  verify D_p(s^2-1-kappa*p^2)=0
  construct rho, p_dot^2, and the energy-derivative tower
  eliminate s from p_dot^2=0 and record resultant degrees
  grow certificate numerators consecutively in p, s, and energy
  reduce every residual modulo s^2-1-kappa*p^2
  compare kappa->0 with the polynomial rigid-rotor/prism certificate
  classify degree observations as proven, empirical, or blocked
```

Octahedral or icosahedral flattening is obtained by adding `b*G_kappa(Jz)` to
the relevant even invariant.  The chosen `z` axis breaks the polyhedral group
to its stabilizer subgroup while preserving the even-power restriction.
