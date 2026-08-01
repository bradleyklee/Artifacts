# Human-facing explainer

## The geometry

A nonempty typogeometry is written over the alphabet

```text
{  }  ,  0  1
```

and has one of three forms.

```text
1
{W}
{W1,W2,W3,W4}
```

Here `0` is an empty closed slot and is used only as a child entry. The local rules are:

- `1` is terminal and costs one unit;
- `{W}` is unary growth and costs one additional unit;
- `{W1,W2,W3,W4}` is an ordered four-slot junction and costs no additional units;
- a four-slot junction must have at least two nonzero entries.

Therefore unary growth is not the same operation as a one-active-slot four-way branch. The latter is forbidden.

## The first members

At size 0:

```text
0
```

At size 1:

```text
1
```

At size 2 there are seven members:

```text
{1}
{1,1,0,0}
{1,0,1,0}
{1,0,0,1}
{0,1,1,0}
{0,1,0,1}
{0,0,1,1}
```

Thus the first counts are

```text
1, 1, 7, 95, 1614, ...
```

A complete literal list through size 4 is in `data/members_n0_n4.txt`.

## Why the generating equation follows

Let `T(x)` count nonempty geometries by total cost.

- terminal `1`: `x`;
- unary growth `{W}`: `x*T`;
- two nonzero children among four ordered slots: `binomial(4,2)*T^2 = 6*T^2`;
- three nonzero children: `4*T^3`;
- four nonzero children: `T^4`.

Hence

```text
T = x + x*T + 6*T^2 + 4*T^3 + T^4.
```

With `A=1+T`, this rearranges to

```text
A = (4 + A^4)/(5-x),
```

which is the defining equation of A244856.

## Certificate warning

The size is not the number of braces or vertices. It counts terminals plus unary growth events. Four-slot branching junctions are free. Every checker and explanatory table must preserve that weighting convention.
