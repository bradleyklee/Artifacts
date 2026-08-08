# Transfer: triangle–rectangle / Platonic elliptic bridges

Date: 2026-08-03

## Executive result

The triangle–rectangle Hamiltonian

    alpha = p^2+q^2+(q^3-3*p^2*q)+(q^2-3*p^2)^2/4

has now been connected exactly to both the octahedral and icosahedral
rotation quotients, but in different ways.

### Octahedral

The clean structure is a level-two isogeny square.  Both physical period
forms descend exactly to canonical elliptic differentials.  The
triangle–rectangle family and the octahedral quotient are pullbacks of the
same X_0(2) family after an explicit algebraic energy correspondence.

The octahedral extraction is geometrically cleaner: the tetrahedral
intermediate quotient is already genus one and gives the even quartic with
low-degree invariant coordinates.

### Icosahedral

The natural A4 intermediate quotient is genus three, not genus one.  The
physical polyhedral period nevertheless descends to the full A5 elliptic
quotient 235II.

At the quotient level the edge-first map is now closed exactly:

    icosahedral cubic (R,S)
      -> edge-first D2 even quartic (x,y)
      -> triangle–rectangle model (p,q).

The exact pieces are:

1. a cubic base relation beta -> z;
2. a quadratic relation z -> alpha;
3. an exact quadratic Tschirnhaus map sending the three z-branches to the
   three finite branch points of the icosahedral cubic;
4. an exact generic D2 cross-ratio map from the cubic to

       12*y^2 = -x^4+(2+12*alpha)*x^2+4*alpha-1;

5. the known certificate map from this quartic to (p,q).

The generic cubic-to-quartic residual reduces symbolically to zero.

## Exact identities to preserve

### Certificate quartic to new Hamiltonian

With the page-2 certificate inverse map,

    2H(p,q)-alpha
      = [12*y^2+x^4-(2+12*alpha)*x^2-4*alpha+1]
        / [4*(3*x^2+1)].

### Icosahedral native base tower

Put

    P(beta)=135*beta^3+115*beta^2+5*beta+1,
    N(beta)=beta^2*(1-beta)^5*(27*beta+5)^3.

Then

    N(beta)*(4-3*z)^3 - 4*P(beta)^3*z^2*(1-z)=0,

and

    z*(1+6*alpha)^2 - 4*alpha*(4+9*alpha)=0.

### Branch-point Tschirnhaus map

The exact map has

    R=A(beta)*z^2+B(beta)*z+C(beta).

The full coefficients and zero-remainder verifier are in
`notes/icosahedral_branchpoint_tschirnhaus_map_v1.md` and
`code/verify_icosahedral_branchpoint_tschirnhaus_map_v1.py`.

### Generic quotient cubic to even quartic

For

    S^2=-(R-e1)(R-e2)(R-e3),
    k^2=(e3-e1)/(e3-e2),
    a=b*(1+k)/(1-k),

set

    D=(1-k)*R-(e1-k*e2),

    x=b*((1+k)*R-(e1+k*e2))/D,

    y=b*(a-b)*(e2-e1)/(sqrt(3)*sqrt(e3-e2))*S/D^2.

Then exactly

    12*y^2=-(x^2-a^2)*(x^2-b^2).

For

    a^2+b^2=2+12*alpha,
    a^2*b^2=1-4*alpha,

this is the triangle–rectangle quartic.

## What we learned

1. Do not use Weierstrass form as the main presentation.  It erases the
   local D2 branch pairing and physical oval geometry.
2. Legendre is only an optional period-checking coordinate.  The natural
   symmetry chart is the even Jacobi quartic, and the preferred final model
   is the new polynomial triangle–rectangle Hamiltonian.
3. The new model may be better than Jacobi for the Platonic program because
   its period is native in the (1/12,5/12;1) hypergeometric space while it
   still admits the D2 quartic chart.
4. Icosahedral and octahedral extractions should not be forced into the same
   subgroup pattern.  Octahedral/A4 collapses to genus one; icosahedral/A4
   is generically genus three.
5. The full A5 quotient is the correct elliptic factor for the physical
   icosahedral period.
6. Equal j or equal hypergeometric argument alone is insufficient.  The
   differential, branch choice, real cycle and monodromy must be tracked.

## Hypergeometric warning

The identities involving

    2F1(1/12,5/12;1;X)

are branch-sensitive.  Existing exact algebraic curve identities do not by
themselves prove a global single-valued period identity.

For triangle–rectangle, octahedral and icosahedral examples, separately audit:

1. exact algebraic curve substitution;
2. exact differential pullback;
3. exact Picard–Fuchs operator pullback including algebraic prefactor;
4. numerical continuation of period and derivative from a normalized
   basepoint;
5. monodromy around every singular value;
6. fourth-root and cycle conventions.

Until this audit is complete, state the hypergeometric result as an exact
local identity on the selected branch, not an unqualified global identity.

## What remains open

### Icosahedral

1. Eliminate individual branch roots and find the cleanest direct extraction
   for x^2 in terms of R, beta and alpha.
2. Substitute the paper's explicit sphere invariants R(J),S(J) and simplify.
3. Compare the quotient differential with physical Lie–Poisson time exactly.
4. Prove global continuation of the edge-first real cycle.
5. Determine how face-first and vertex-first localities appear as other
   branches of the same new model.
6. Decide whether the native (1/12,5/12) model gives a simpler invariant
   extraction than the Jacobi quartic.

### Octahedral

1. Preserve the existing direct invariant/intermediate-quotient extraction.
2. Re-run the same differential/Picard–Fuchs/monodromy audit.
3. Compare the clean octahedral map and the new icosahedral map side by side,
   minimizing algebraic extensions and coordinate degree.
4. Test whether there is an even cleaner native (1/12,5/12) extraction than
   the present X_0(2) description.

### Factory integration

1. Add this directory under `examples/triangle_rectangle_platonic_bridge/`.
2. Keep exact proof scripts as acceptance tests.
3. Keep numerical data clearly labeled provisional.
4. Keep Python/SymPy failures in `failures/` for later upstream reporting.
5. Add a generated certificate only after the hypergeometric branch audit.

## Immediate next run

Do not create more modular transforms.  Work on exactly two deliverables:

A. `clean_extraction.py`

   Eliminate e1,e2,e3,k from the exact branch-field formulas and search for
   the lowest-degree direct relation for x^2(R,beta,alpha).

B. `hypergeometric_branch_audit.py`

   Verify operator pullbacks and numerically continue periods, derivatives and
   monodromy for triangle–rectangle, octahedral and icosahedral localities.

A success or failure report should include exact identities, finite numerical
records, branch conventions and all software failures.
