# Trefoil Symplectic-Period Certificate

Self-contained extraction of the one-page trefoil certificate, its exact
symbolic verifier, independent numerical audit, and the code used to compute
the knot-family drawings and crossing data.

## Mathematical object

The certificate studies

- `C = {z^2 = w^3} subset C^2`,
- the standard symplectic form
  `omega0 = (i/2)(dz ^ dbar(z) + dw ^ dbar(w))`,
- `H = |z|^2 + |w|^2`, and
- `K_E = C intersect H^{-1}(E)` for `E > 0`.

With `z=s^3`, `w=s^2`, `s=sqrt(u) exp(i theta)`, one has
`E=u^3+u^2`.  Restricting the Liouville and symplectic forms to `C`
gives the time form

`eta = (9u+4)/(2(3u+2)) dtheta`

and hence

`T(E) = pi (9u+4)/(3u+2)`.

For

`Phi(E) = 3 - T(E)/pi = 2/(3u+2)`,

the exact algebraic and differential equations are

`(4-27E) Phi^3 - 12 Phi + 8 = 0`,

`E(27E-4) Phi'' + 2(27E-1) Phi' + 6 Phi = 0`.

With `x=27E/4`, the latter is Gauss hypergeometric.  Only at the final
series step do we use the local uniformizer `q=sqrt(E)/4`; then

`G(q)=Phi(16q^2)=sum (-1)^n a_n q^n`,

`a_n = 4^n binom(3n/2,n)`,

whose unsigned coefficients are OEIS A244038.

## Reproducibility

From the package root:

```bash
./verify.sh
```

runs the independent numerical audit and the exact SymPy checks.

```bash
./build.sh
```

regenerates the computed knot-family figure, crossing audit, numerical audit,
verifies the mathematics, recompiles the one-page LaTeX certificate, and
runs PDF preflight.  The final PDF is written to `dist/`.

Python requirements are listed in `requirements.txt`.  The LaTeX build uses
`pdflatex` with the packages declared in `src/trefoil_certificate.tex`.

## File map

- `dist/trefoil_symplectic_period_certificate.pdf` - final one-page certificate.
- `print/trefoil_symplectic_period_certificate_300dpi.png` - print/render check.
- `src/trefoil_certificate.tex` - complete LaTeX source.
- `src/make_figures.py` - stereographic family, crossing detection, and
  red-over-green segment rendering from computed coordinates.
- `src/verify_trefoil.py` - exact SymPy checks of forms, period, cubic, ODE,
  Gauss pullback, branch sign, integer coefficients, recurrence, and audits.
- `src/numerical_audit.py` - independent numerical period test on the original
  curves in R^4 plus an independent action-derivative test.
- `src/trefoil_period_payload.json` - compact machine-readable exact payload.
- `src/numerical_audit.json` - numerical results at eight energies.
- `src/crossing_family_view2.json` - exact screen crossing/depth audit for the
  eight displayed knot diagrams.
- `src/trefoil_energy_family_view2.pdf/.png` - computed family figure.
- `audit/verify.log` - exact verifier result.
- `audit/preflight.txt` - PDF structural preflight.
- `MANIFEST.sha256` - SHA-256 checksum manifest for the extraction.

## Numerical audit thresholds in the certificate

The constrained-flow quadrature on the original curves in R^4 agrees with the
closed period to about `8.3e-11` relative over the eight tested energies.
The independent polygonal action plus centered energy difference agrees to
about `1.4e-8` relative.

## Crossing convention

Every displayed curve is computed from the exact parametrization, projected
stereographically to R^3, then projected to a fixed screen.  At each screen
crossing, the two computed R^3 depths decide over/under order.  A short green
segment is drawn on the under branch first; a short red segment is drawn on
the over branch last.  Thus red-over-green is a plotting convention backed by
actual depth data, not a hand annotation.
