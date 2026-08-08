# Icosahedral to triangle–rectangle native model — v1

## Direct tower, with no Legendre step

The icosahedral edge branch is represented by the exact cubic

    F_ico(beta,z) =
      N(beta)*(4-3*z)^3
      -4*P(beta)^3*z^2*(1-z)
      = 0,

where

    P(beta)=135*beta^3+115*beta^2+5*beta+1,

    N(beta)=beta^2*(1-beta)^5*(27*beta+5)^3.

The triangle–rectangle family has the native signature-4 relation

    G_TR(alpha,z) =
      z*(1+6*alpha)^2
      -4*alpha*(4+9*alpha)
      = 0.

Thus the direct algebraic base-change tower is

    beta  --cubic-->  z  --quadratic-->  alpha.

Over this tower, use the new plane model directly:

    alpha =
      p^2+q^2+(q^3-3*p^2*q)
      +(q^2-3*p^2)^2/4.

No Legendre cubic is introduced.

## Certificate map verified symbolically

Set

    u=x-1,

    A(u)=(3*u^2+6*u+4)/12,

    B(u)=u*(3*u+2)/6,

    v=(y-B(u))/(2*A(u)),

    q=(u+v)/2,

    p=(v-u)/(2*sqrt(3)).

For the quartic

    12*y^2 =
      -x^4+(2+12*alpha)*x^2+4*alpha-1,

symbolic polynomial division gives zero remainder in

    2H(p,q)-alpha.

More precisely,

    2H(p,q)-alpha
      = Q(x,y,alpha) * R(x,y,alpha),

where `Q=0` is the quartic equation and

    R = 1/(4*(3*x**2 + 1)).

This independently verifies that the page-2 birational map sends the quartic
to the new Hamiltonian curve.

## Simple real section

At `x=1`, the quartic gives

    y^2=4*alpha/3.

The inverse map simplifies to

    q=3*y/4,

    p=sqrt(3)*y/4.

Hence

    q^2-3*p^2=0,

    q^3-3*p^2*q=0,

and therefore

    2H=p^2+q^2=alpha.

This provides a particularly simple real point on every small positive-energy
fiber.  It also shows that the new model retains a distinguished harmonic ray
on which all nonlinear triangular and rectangular corrections vanish.

## Numerical edge-branch checks

| beta | z | alpha | p at x=1 | q at x=1 | Hamiltonian error |
|---:|---:|---:|---:|---:|---:|
| 1.0e-5 | 0.000447080132389423615373186 | 0.0000279501232976665406043327 | 0.00264339380804613279458076 | 0.00457849237994887411533127 | 2.7635739e-76 |
| 0.0001 | 0.00445882012554939189015686 | 0.000279435816903934089833101 | 0.00835816691781059864580222 | 0.0144767697597893214326696 | 4.4217183e-75 |
| 0.001 | 0.0434195667791667128365619 | 0.00278777893812795375579983 | 0.0263997108797045055621812 | 0.0457256405487770648556653 | 0.0 |
| 0.005 | 0.194029938895919886598589 | 0.0137886467932406866047042 | 0.0587125344224738066380506 | 0.101693092660861263402191 | 1.4149499e-73 |
| 0.01 | 0.341176371915148921863399 | 0.0271840155348589738098636 | 0.0824378789375050785122715 | 0.142786594787971011257889 | 0.0 |
| 0.02 | 0.544375273222547196749706 | 0.0526896146522586873484229 | 0.114771092453913114423746 | 0.198789363370362488595903 | 1.1319599e-72 |
| 0.04 | 0.758978606583255347712679 | 0.0980239432807919773948575 | 0.156543878258455045689859 | 0.271141950757521074242302 | 1.1319599e-72 |

The icosahedral cubic residual is also below the displayed numerical precision
at every point.

## Interpretation

The useful model hierarchy is now

    icosahedral invariant data
       -> native signature-4 coordinate z
       -> triangle–rectangle energy alpha
       -> new polynomial Hamiltonian H(p,q).

Jacobi remains available as a local D2 chart, but it is not required in the
actual map.  The new model is potentially better because:

1. it is polynomial in the physical plane coordinates;
2. it carries the `1/12,5/12` period directly;
3. it retains a simple harmonic ray;
4. its triangular and rectangular corrections are explicit invariant
   polynomials;
5. the base change from the icosahedral family is only cubic followed by
   quadratic.

## Still missing

This proves the base-changed elliptic family and the certificate birational
map, but not yet a direct formula from the original sphere coordinates to
`p,q`.

The next proof step is to express the signature-4 coordinate `z` and one
quartic coordinate `x` in terms of the paper's icosahedral quotient variables.
Once `x` is available, the certificate gives `p,q` immediately.
