# A120590: PDF extraction and OEIS editing guide

Prepared from **Ternatrees and OEIS A120590**, final-draft PDF dated
July 30, 2026 (16 pages).

## What the OEIS entry already contains

As checked on July 30, 2026, A120590 already contains:

- the algebraic generating-function equation `4*A(x) = 3 + x + A(x)^3`;
- the initial terms and offset 0;
- a series-reversion formula and a Lagrange-inversion formula;
- the recurrence in backward-shift form;
- an asymptotic formula and a trigonometric form;
- the finite binomial sum added in March 2026.

Do not submit these again as new formulas. The recurrence in the PDF is the
same recurrence with the index shifted.

## Highest-value additions from the PDF

### 1. Combinatorial interpretation — PDF pages 2–3

Add the ternatree model as a `%C` comment. The essential definition is:

> `a(n)` counts rooted ordered ternatrees with `n` true leaves, three ordered
> child positions at every internal vertex, and no unary branching. After empty
> child positions are deleted, each internal vertex has two or three children;
> each two-child vertex has three choices for the location of its deleted empty
> child.

The cycle-lemma argument and the resulting multinomial count are on pages 2–3.

### 2. Compact coefficient and contour formulas — PDF pages 3–4

With

```
D(u) = 1 - 3*u - u^2,
rho(u) = u*D(u),
```

the compact formulas are

```
a(0) = 1,
a(n) = (1/n)*[u^(n-1)] D(u)^(-n),                         n >= 1,
a(n) = (1/(2*Pi*i*n))*Integral_gamma du/rho(u)^n,          n >= 1,
```

where `gamma` is a sufficiently small positively oriented circle around 0.
The coefficient formula is equivalent to the finite sum already on OEIS, but
is substantially more compact and leads directly to the contour integral.

### 3. Integral form of the ordinary generating function — PDF page 4

```
A(x) = 1 - (1/(2*Pi*i))*Integral_gamma
                    log(1 - x/rho(u)) du.
```

This is a useful bridge between the coefficient formula and the differential
equation.

### 4. Differential equation — PDF pages 6–7

```
(27*x^2 + 162*x - 13)*A''(x)
    + 27*(x + 3)*A'(x)
    - 3*A(x) = 0,
A(0) = 1, A'(0) = 1.
```

This appears to be the most important formula not currently displayed on the
OEIS page.

### 5. Exact certificate for the ODE — PDF page 7 (optional)

Put

```
Phi(x,u) = 1/(rho(u)-x),
Delta(x) = 27*x^2 + 162*x - 13,
N(x,u) = 12*u^4 + 48*u^3 + 3*u*x - 87*u + 3*x + 13.
```

Then

```
24*Phi + (81*x+243)*d(Phi)/dx + Delta(x)*d^2(Phi)/dx^2
    = d/du ( N(x,u)*Phi^2 ).
```

Contour integration kills the right-hand side and produces the third-order
equation for `A'`, which integrates once to the second-order ODE above. This is
probably better kept in the linked PDF than placed directly in the main OEIS
formula field.

### 6. Exact shift certificate — PDF pages 4–5 (optional)

The PDF also gives fixed matrices `U,V,J`, the lowering map

```
Lower(w,m) = (U - J*V/m)*w,
```

and an exact derivative certificate for the recurrence. These are valuable
reproducibility data, but are too detailed for the main sequence entry. Link the
paper and code instead.

## Ready-to-paste OEIS proposal

```text
%C a(n) counts rooted ordered ternatrees with n true leaves, three ordered
%C child positions at every internal vertex, and no unary branching. After
%C empty child positions are deleted, every internal vertex has two or three
%C children; each two-child vertex has three choices for the position of its
%C deleted empty child. - Bradley Klee, Jul 30 2026

%F Put D(u)=1-3*u-u^2 and rho(u)=u*D(u). For n>=1,
%F a(n)=(1/n)*[u^(n-1)]D(u)^(-n)
%F     =(1/(2*Pi*i*n))*Integral_gamma du/rho(u)^n,
%F where gamma is a sufficiently small positively oriented circle around 0.
%F - Bradley Klee, Jul 30 2026

%F A(x)=1-(1/(2*Pi*i))*Integral_gamma log(1-x/rho(u)) du.
%F - Bradley Klee, Jul 30 2026

%F (27*x^2+162*x-13)*A''(x)+27*(x+3)*A'(x)-3*A(x)=0,
%F with A(0)=1 and A'(0)=1. - Bradley Klee, Jul 30 2026

%H Bradley Klee and Harm.On.ica S-O-L 5.6 (OpenAI), Ternatrees and OEIS
%H A120590: All the must-have identities, herein derived or re-proven,
%H [insert stable PDF URL].

%H Bradley Klee, reproducibility packet and exact SymPy implementation,
%H https://github.com/bradleyklee/Artifacts/tree/main/22-certificate-factory/examples/q3
```

## Editorial checks before submission

1. Replace the PDF placeholder with a stable direct link.
2. Verify that the GitHub path matches the eventual public release location.
3. Keep the offset at 0 and state the contour formulas only for `n >= 1`.
4. Do not re-submit the finite binomial sum or the existing backward recurrence.
5. Use `Pi` and `i` in OEIS plain-text notation; avoid TeX-only commands in `%F`.
6. Consider submitting the combinatorial interpretation and ODE first; the two
   contour formulas can be a second edit if the first change is already large.
