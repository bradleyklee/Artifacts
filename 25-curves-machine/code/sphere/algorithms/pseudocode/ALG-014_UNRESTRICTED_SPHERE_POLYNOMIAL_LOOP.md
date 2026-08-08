# ALG-014 — Unrestricted sphere-polynomial example loop

**Input:** any polynomial `H(Jx,Jy,Jz)` and a chosen axis `lambda=Jz`.

1. Substitute `Jx=sqrt(1-lambda^2)*cos(phi)` and `Jy=sqrt(1-lambda^2)*sin(phi)`.
2. Collect the finite sine/cosine harmonics. Do not reject odd powers.
3. Generate local period coefficients numerically or by series reversion and guess the smallest operator order and coefficient degrees.
4. If there is one harmonic, phase-shift it to
   `H=h1(lambda)+h2(lambda)*cos(m*phi)` and eliminate the angle:
   `z^2=-m^2*((alpha-h1)^2-h2^2)`.
5. Differentiate the period numerator successively in `alpha`.
6. At each derivative, use polynomial division to reduce powers of `z`, then subtract exact derivatives until the numerator lies in the fixed polynomial basis.
7. Append its coefficient vector to a matrix and test the nullspace.
8. On first dependence, add the discarded derivative terms to reconstruct `Xi` and verify the residual exactly.
9. Record actual order, coefficient degrees, matrix shape, time, memory, and primitive size.
10. For multiple harmonics, retain the sine/cosine algebraic variables and apply the same consecutive-support discipline; use inductive period data to prioritize order and coefficient shells.

Never report a capped support search as nonexistence. Never count trailing zero operator coefficients as derivative order.
