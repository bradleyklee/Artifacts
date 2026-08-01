# Maximality observation: A120589

A120589 is the smallest standout case showing that relation length is governed
by the occupied remainder space, not merely by the degree of the parent
kernel.

For the seed-one degree-q family, every reduced column lies in the
(q-1)-dimensional subspace whose top-degree remainder coefficient is zero.
Therefore q shifted columns suffice.

For A120589, the observable seed is `1+u`, of maximal possible degree q-1 for
q=2. Its unshifted column occupies the missing top-degree direction. The
remainder space is therefore the full q-dimensional space. The first
nullvector requires q+1 columns:

    X is 2 by 3, rank 2, nullity 1.

The nullvector begins with zero:

    (0, -2*(2*n+1), n+2).

Thus the extra shift is maximal in two related senses:

1. the seed fills the last available remainder direction; and
2. one must reach the maximal generic column count `dimension+1` before a
   nullvector is forced.

The resulting recurrence is

    (n+2)*a(n+2)-2*(2*n+1)*a(n+1)=0.

The leading zero is structural, not an error: no relation uses the unshifted
integrand because it alone carries the top-degree remainder component.

A120591 exhibits the analogous full-space behavior for q=3, using a 3 by 4
remainder matrix. A120589 remains the clearest minimal example of the
maximality phenomenon.
