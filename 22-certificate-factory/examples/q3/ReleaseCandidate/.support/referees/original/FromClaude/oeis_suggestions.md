# OEIS suggestions — sequence from Q3(N)

**Status check first, adversarial-epistemic style:** this sequence is *not new*.
It is already **A120590** (1, 1, 3, 19, 150, 1326, 12558, 124590, 1278189, ...),
attributed to Paul D. Hanna (2006/2008), g.f. satisfying `4*A(x) = 3 + x + A(x)^3`.

Verified independently, not assumed:
- Terms 0..15 from `Q3(15)` match A120590's listed terms exactly.
- The recurrence derived here, `P2(k)*a[k+2] = -P1(k)*a[k+1] - P0(k)*a[k]` with
  `P0(n)=-3(3n-1)(3n+1)`, `P1(n)=-81(n+1)(2n+1)`, `P2(n)=13(n+1)(n+2)`,
  is algebraically identical (confirmed symbolically, not just numerically)
  to the recurrence already on the page, credited to Vaclav Kotesovec (Oct 19 2012):
  `13*(n-1)*n*a(n) = 81*(n-1)*(2*n-3)*a(n-1) + 3*(3*n-7)*(3*n-5)*a(n-2)`.

So: no new sequence to submit. What follows is what's *missing* from the existing
entry, organized under the section headings OEIS actually uses.

---

## FORMULA (addition candidates)

**1. Closed form — checked, likely redundant with an existing formula.**

Derived independently via Lagrange inversion on the same cubic (substitute
A=1+t, rearrange to x = t/f(t) with f(t)=1/(1-3t-t^2), apply the inversion
theorem, expand f(t)^n, extract [t^(n-1)]):

    a(0) = 1
    a(n) = (1/n) * Sum_{k=ceil((n-1)/2)}^{n-1} C(n+k-1,k) * C(k,n-1-k) * 3^(2k-n+1)

Checked against 16 independently-computed terms (0..15): exact match. Also
checked against Manyama's formula already on the page
(`a(n) = (1/n)*Sum_{k=0..floor((n-1)/2)} 3^(n-1-2k)*C(2n-2-k,n-1)*C(n-1-k,k)`):
the two agree on all 16 terms. **Not proven identical for general n** — this
looks like the same binomial identity reached via a different index shift,
but that equivalence hasn't been established algebraically, only numerically.
Given the overlap, this probably isn't worth submitting as a separate FORMULA
line unless/until it's shown to be a genuinely different identity rather than
Manyama's sum in different dress.

**2. ODE — this one still looks like a real gap.**

The page currently lists the g.f. functional equation, a Lagrange-inversion
sum, Kotesovec's linear recurrence, the asymptotics, an arcsin closed form,
and Manyama's binomial-sum formula — but **no differential equation** for
the g.f. Q3's `MakeODE` step produces one, verified against 15
independently-computed terms (not against values copied from the OEIS
listing):

    (27*x^2 + 162*x - 13) * A''(x) + 27*(x+3) * A'(x) - 3*A(x) = 0

Suggested line (OEIS style, unverified by a second party — flag as such if submitted):

> A(x) satisfies (27\*x^2+162\*x-13)\*A''(x) + 27\*(x+3)\*A'(x) - 3\*A(x) = 0.
> — [submitter], [date]

Caveat to carry into any submission: I have not checked whether this ODE is a
trivial consequence of the known cubic g.f. equation via one differentiation
(likely — differentiating `4A=3+x+A^3` gives `4A' = 1+3A^2 A'`, a *first*-order
relation; getting a second-order *linear* ODE from a cubic algebraic function is
the standard holonomic-closure result, so it's real but probably mechanical, not
deep). Framing it as "new" should say *newly stated*, not "surprising."

## COMMENTS (addition candidate — needs care)

Could add a note that a(n) also arises from a rational parametrized matrix
construction: columns `c_0=e`, `c_1,c_2` built by repeated application of a
map `Lower(U,V,J,w,m) = U*w - (J*V*w)/m` to specific 3×3 matrices, with the
recurrence coefficients falling out as the three 2×2 minors of the resulting
2×3 matrix (cleared of denominators/GCD/sign). This is a legitimate alternate
derivation but **I'd hold off recommending it for the actual OEIS entry** —
it's the kind of comment that needs a named reference or clear combinatorial
meaning (what does U, V, J *count*?) before it adds value rather than obscurity.
Worth resolving privately before proposing it publicly.

## CROSSREFS (no changes needed)

The existing crossrefs (A120591, A244594, A120588, A120592, A120593, A001002,
A192945) already cover the natural neighbors in the `r*A = c + b*x + A^n`
family. Nothing to add here from this exercise.

## LINKS (no changes needed)

Table link and the Richardson arXiv reference are already present and sufficient.

---

**Bottom line:** the only concrete, defensible addition is the FORMULA line for
the ODE. Everything else here (the matrix comment) should stay a private note
until it has a real citation or combinatorial interpretation behind it — no
pseudocode-genrated derivation gets submitted to OEIS on its own authority.
