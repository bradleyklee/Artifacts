# Complete calculus digest: 23 Hanna-family examples

This file is generated from the canonical machine payloads. It audits the complete path
`typogeometry -> contour integral -> exact reduction matrices -> recurrence -> ODE`.
All comparisons are exact integer or rational identities; no numerical fitting is used.

## Family-wide result

All 23 specified cases are `ANALYTIC_COMPLETE`. Every case has verified geometric and
contour data, matrix reduction data, a recurrence, a rational certificate, a linear ODE,
24 exact stored terms, and a matching published OEIS prefix.

## Dimension and term-generation summary

| Case | G or Gx | X | P_x | recurrence order | linear ODE order | terms generated from recurrence |
|---|---:|---:|---:|---:|---:|---:|
| A120588 | 4×4 | 1×2 | 2×2 | 1 | 1 | 22 |
| A120589 | 4×4 | 2×3 | 3×2 | 2 | 1 | 21 |
| A120590 | 6×6 | 2×3 | 3×3 | 2 | 2 | 21 |
| A120591 | 6×6 | 3×4 | 4×3 | 3 | 2 | 20 |
| A120592 | 6×6 | 2×3 | 3×3 | 2 | 2 | 21 |
| A120593 | 8×8 | 3×4 | 4×4 | 3 | 3 | 20 |
| A120594 | 8×8 | 3×4 | 4×4 | 3 | 3 | 20 |
| A120595 | 8×8 | 3×4 | 4×4 | 3 | 3 | 20 |
| A120596 | 10×10 | 4×5 | 5×5 | 4 | 4 | 19 |
| A120597 | 10×10 | 4×5 | 5×5 | 4 | 4 | 19 |
| A120598 | 10×10 | 4×5 | 5×5 | 4 | 4 | 19 |
| A120599 | 10×10 | 4×5 | 5×5 | 4 | 4 | 19 |
| A120600 | 12×12 | 5×6 | 6×6 | 5 | 5 | 18 |
| A120601 | 12×12 | 5×6 | 6×6 | 5 | 5 | 18 |
| A120602 | 12×12 | 5×6 | 6×6 | 5 | 5 | 18 |
| A120603 | 14×14 | 6×7 | 7×7 | 6 | 6 | 17 |
| A120604 | 16×16 | 7×8 | 8×8 | 7 | 7 | 16 |
| A120605 | 18×18 | 8×9 | 9×9 | 8 | 8 | 15 |
| A120606 | 18×18 | 8×9 | 9×9 | 8 | 8 | 15 |
| A120607 | 20×20 | 9×10 | 10×10 | 9 | 9 | 14 |
| A244594 | 6×6 | 2×3 | 5×4 | 4 | 3 | 19 |
| A244627 | 6×6 | 2×3 | 5×4 | 4 | 3 | 19 |
| A244856 | 8×8 | 3×4 | 5×4 | 4 | 3 | 20 |

## Reading `P_x`

For a recurrence `sum_r P_r(n) a(n+r)=0`, `P_x` stores `P_r` by rows:
row `x^r` is shift `r`, and column `n^k` is the coefficient of `n^k`.
Thus the number of rows is the number of recurrence polynomials, while the number
of columns is one plus their maximum degree in `n`. This matrix is distinct from
the Hermite-reduction matrices `G`, `U`, `V`, `J`, and remainder matrix `X`.

The term audit retains only the necessary initial seeds, solves the recurrence exactly
for every remaining stored coefficient, requires integer output at every division, and
then compares the reconstructed list with both the 24-term algebraic expansion and the
published OEIS prefix.

## A120588

- Defining data: `3*A(x)=2+1*x+A(x)^2`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-1*u^1)`
- Recurrence: order 1, valid from n=1.
- Verified scalar linear ODE order: 1.
- Term seeds retained: 2; recurrence-generated suffix terms: 22.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 4 × 4 |
| U | 2 × 2 |
| V | 2 × 2 |
| J | 2 × 2 |
| X | 1 × 2 |

`P_x` dimensions: 2 × 2. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` |
|---|---:|---:|
| `x^0` | 2 | -4 |
| `x^1` | 1 | 1 |

Canonical recurrence:

```text
P_0(n) = -2*(2*n - 1)
P_1(n) = n + 1
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796`.

## A120589

- Defining data: `A_parent(x)^2`
- Reduction route: full-remainder dynamic term-shift.
- Contour/kernel record: `[x^n]A(x)^2=(2*1)/(2*pi*i*n)*integral_gamma (1+(1)*u)^1 du/(u^n*D(u)^n)`
- Recurrence: order 2, valid from n=1.
- Verified scalar linear ODE order: 1.
- Term seeds retained: 3; recurrence-generated suffix terms: 21.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 4 × 4 |
| U | 2 × 2 |
| V | 2 × 2 |
| J | 2 × 2 |
| X | 2 × 3 |

`P_x` dimensions: 3 × 2. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` |
|---|---:|---:|
| `x^0` | 0 | 0 |
| `x^1` | -2 | -4 |
| `x^2` | 2 | 1 |

Canonical recurrence:

```text
P_0(n) = 0
P_1(n) = -2*(2*n + 1)
P_2(n) = n + 2
```

First terms reconstructed from `P_n` after the stated seeds: `1, 2, 3, 6, 15, 42, 126, 396, 1287, 4290, 14586, 50388`.

Maximality note: the degree-one seed fills the full two-dimensional remainder space. A third column is required; the primitive vector starts with `P_0=0`.

## A120590

- Defining data: `4*A(x)=3+1*x+A(x)^3`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-3*u^1-1*u^2)`
- Recurrence: order 2, valid from n=1.
- Verified scalar linear ODE order: 2.
- Term seeds retained: 3; recurrence-generated suffix terms: 21.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 6 × 6 |
| U | 3 × 3 |
| V | 3 × 3 |
| J | 3 × 3 |
| X | 2 × 3 |

`P_x` dimensions: 3 × 3. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` |
|---|---:|---:|---:|
| `x^0` | 3 | 0 | -27 |
| `x^1` | -81 | -243 | -162 |
| `x^2` | 26 | 39 | 13 |

Canonical recurrence:

```text
P_0(n) = -3*(3*n - 1)*(3*n + 1)
P_1(n) = -81*(n + 1)*(2*n + 1)
P_2(n) = 13*(n + 1)*(n + 2)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 3, 19, 150, 1326, 12558, 124590, 1278189, 13449205, 144342627, 1573990275`.

## A120591

- Defining data: `A_parent(x)^3`
- Reduction route: full-remainder dynamic term-shift.
- Contour/kernel record: `[x^n]A(x)^3=(3*1)/(2*pi*i*n)*integral_gamma (1+(1)*u)^2 du/(u^n*D(u)^n)`
- Recurrence: order 3, valid from n=1.
- Verified scalar linear ODE order: 2.
- Term seeds retained: 4; recurrence-generated suffix terms: 20.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 6 × 6 |
| U | 3 × 3 |
| V | 3 × 3 |
| J | 3 × 3 |
| X | 3 × 4 |

`P_x` dimensions: 4 × 3. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` |
|---|---:|---:|---:|
| `x^0` | 0 | 0 | 0 |
| `x^1` | -24 | -54 | -27 |
| `x^2` | -486 | -567 | -162 |
| `x^3` | 78 | 65 | 13 |

Canonical recurrence:

```text
P_0(n) = 0
P_1(n) = -3*(3*n + 2)*(3*n + 4)
P_2(n) = -81*(n + 2)*(2*n + 3)
P_3(n) = 13*(n + 2)*(n + 3)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 12, 76, 600, 5304, 50232, 498360, 5112756, 53796820, 577370508, 6295961100`.

## A120592

- Defining data: `5*A(x)=4+4*x+A(x)^3`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-3*u^1-2*u^2)`
- Recurrence: order 2, valid from n=1.
- Verified scalar linear ODE order: 2.
- Term seeds retained: 3; recurrence-generated suffix terms: 21.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 6 × 6 |
| U | 3 × 3 |
| V | 3 × 3 |
| J | 3 × 3 |
| X | 2 × 3 |

`P_x` dimensions: 3 × 3. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` |
|---|---:|---:|---:|
| `x^0` | 12 | 0 | -108 |
| `x^1` | -108 | -324 | -216 |
| `x^2` | 34 | 51 | 17 |

Canonical recurrence:

```text
P_0(n) = -12*(3*n - 1)*(3*n + 1)
P_1(n) = -108*(n + 1)*(2*n + 1)
P_2(n) = 17*(n + 1)*(n + 2)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 2, 6, 40, 330, 3048, 30156, 312528, 3349170, 36809960, 412651668, 4700098416`.

## A120593

- Defining data: `5*A(x)=4+1*x+A(x)^4`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-6*u^1-4*u^2-1*u^3)`
- Recurrence: order 3, valid from n=1.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 4; recurrence-generated suffix terms: 20.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 8 × 8 |
| U | 4 × 4 |
| V | 4 × 4 |
| J | 4 × 4 |
| X | 3 × 4 |

`P_x` dimensions: 4 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | 40 | -48 | -384 | -256 |
| `x^1` | -2752 | -8896 | -9216 | -3072 |
| `x^2` | -36864 | -79872 | -55296 | -12288 |
| `x^3` | 2946 | 5401 | 2946 | 491 |

Canonical recurrence:

```text
P_0(n) = -8*(2*n + 1)*(4*n - 1)*(4*n + 5)
P_1(n) = -64*(n + 1)*(48*n**2 + 96*n + 43)
P_2(n) = -6144*(n + 1)*(n + 2)*(2*n + 3)
P_3(n) = 491*(n + 1)*(n + 2)*(n + 3)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 6, 76, 1201, 21252, 402892, 8001412, 164321982, 3461110532, 74358814838, 1623152780808`.

## A120594

- Defining data: `8*A(x)=7+8*x+A(x)^4`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-3*u^1-4*u^2-2*u^3)`
- Recurrence: order 3, valid from n=1.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 4; recurrence-generated suffix terms: 20.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 8 × 8 |
| U | 4 × 4 |
| V | 4 × 4 |
| J | 4 × 4 |
| X | 3 × 4 |

`P_x` dimensions: 4 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | 80 | -96 | -768 | -512 |
| `x^1` | -1204 | -3892 | -4032 | -1344 |
| `x^2` | -3528 | -7644 | -5292 | -1176 |
| `x^3` | 534 | 979 | 534 | 89 |

Canonical recurrence:

```text
P_0(n) = -16*(2*n + 1)*(4*n - 1)*(4*n + 5)
P_1(n) = -28*(n + 1)*(48*n**2 + 96*n + 43)
P_2(n) = -588*(n + 1)*(n + 2)*(2*n + 3)
P_3(n) = 89*(n + 1)*(n + 2)*(n + 3)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 2, 6, 44, 394, 3948, 42364, 476120, 5532714, 65935804, 801461012, 9897836520`.

## A120595

- Defining data: `13*A(x)=12+27*x+A(x)^4`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-2*u^1-4*u^2-3*u^3)`
- Recurrence: order 3, valid from n=1.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 4; recurrence-generated suffix terms: 20.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 8 × 8 |
| U | 4 × 4 |
| V | 4 × 4 |
| J | 4 × 4 |
| X | 3 × 4 |

`P_x` dimensions: 4 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | 1080 | -1296 | -10368 | -6912 |
| `x^1` | -8256 | -26688 | -27648 | -9216 |
| `x^2` | -12288 | -26624 | -18432 | -4096 |
| `x^3` | 2706 | 4961 | 2706 | 451 |

Canonical recurrence:

```text
P_0(n) = -216*(2*n + 1)*(4*n - 1)*(4*n + 5)
P_1(n) = -192*(n + 1)*(48*n**2 + 96*n + 43)
P_2(n) = -2048*(n + 1)*(n + 2)*(2*n + 3)
P_3(n) = 451*(n + 1)*(n + 2)*(n + 3)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 6, 36, 249, 1932, 16044, 139500, 1253934, 11558316, 108658902, 1037800920`.

## A120596

- Defining data: `6*A(x)=5+1*x+A(x)^5`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-10*u^1-10*u^2-5*u^3-1*u^4)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 4.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 10 × 10 |
| U | 5 × 5 |
| V | 5 × 5 |
| J | 5 × 5 |
| X | 4 × 5 |

`P_x` dimensions: 5 × 5. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` |
|---|---:|---:|---:|---:|---:|
| `x^0` | 1155 | -2500 | -13750 | -12500 | -3125 |
| `x^1` | -159375 | -546875 | -668750 | -343750 | -62500 |
| `x^2` | -3656250 | -9234375 | -8390625 | -3281250 | -468750 |
| `x^3` | -23437500 | -52343750 | -40625000 | -13281250 | -1562500 |
| `x^4` | 900744 | 1876550 | 1313585 | 375310 | 37531 |

Canonical recurrence:

```text
P_0(n) = -5*(5*n - 1)*(5*n + 3)*(5*n + 7)*(5*n + 11)
P_1(n) = -3125*(n + 1)*(2*n + 3)*(10*n**2 + 30*n + 17)
P_2(n) = -46875*(n + 1)*(n + 2)*(10*n**2 + 40*n + 39)
P_3(n) = -781250*(n + 1)*(n + 2)*(n + 3)*(2*n + 5)
P_4(n) = 37531*(n + 1)*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 10, 210, 5505, 161601, 5082420, 167451780, 5705082795, 199354509755, 7105393162010, 257312347583330`.

## A120597

- Defining data: `9*A(x)=8+8*x+A(x)^5`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-5*u^1-10*u^2-10*u^3-4*u^4)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 4.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 10 × 10 |
| U | 5 × 5 |
| V | 5 × 5 |
| J | 5 × 5 |
| X | 4 × 5 |

`P_x` dimensions: 5 × 5. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` |
|---|---:|---:|---:|---:|---:|
| `x^0` | 18480 | -40000 | -220000 | -200000 | -50000 |
| `x^1` | -510000 | -1750000 | -2140000 | -1100000 | -200000 |
| `x^2` | -2340000 | -5910000 | -5370000 | -2100000 | -300000 |
| `x^3` | -3000000 | -6700000 | -5200000 | -1700000 | -200000 |
| `x^4` | 217176 | 452450 | 316715 | 90490 | 9049 |

Canonical recurrence:

```text
P_0(n) = -80*(5*n - 1)*(5*n + 3)*(5*n + 7)*(5*n + 11)
P_1(n) = -10000*(n + 1)*(2*n + 3)*(10*n**2 + 30*n + 17)
P_2(n) = -30000*(n + 1)*(n + 2)*(10*n**2 + 40*n + 39)
P_3(n) = -100000*(n + 1)*(n + 2)*(n + 3)*(2*n + 5)
P_4(n) = 9049*(n + 1)*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 2, 10, 120, 1770, 29208, 516180, 9554640, 182867970, 3589443160, 71861735660, 1461730482160`.

## A120598

- Defining data: `30*A(x)=29+125*x+A(x)^5`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-2*u^1-10*u^2-25*u^3-25*u^4)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 4.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 10 × 10 |
| U | 5 × 5 |
| V | 5 × 5 |
| J | 5 × 5 |
| X | 4 × 5 |

`P_x` dimensions: 5 × 5. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` |
|---|---:|---:|---:|---:|---:|
| `x^0` | 721875 | -1562500 | -8593750 | -7812500 | -1953125 |
| `x^1` | -4621875 | -15859375 | -19393750 | -9968750 | -1812500 |
| `x^2` | -4919850 | -12425775 | -11290425 | -4415250 | -630750 |
| `x^3` | -1463340 | -3268126 | -2536456 | -829226 | -97556 |
| `x^4` | 246408 | 513350 | 359345 | 102670 | 10267 |

Canonical recurrence:

```text
P_0(n) = -3125*(5*n - 1)*(5*n + 3)*(5*n + 7)*(5*n + 11)
P_1(n) = -90625*(n + 1)*(2*n + 3)*(10*n**2 + 30*n + 17)
P_2(n) = -63075*(n + 1)*(n + 2)*(10*n**2 + 40*n + 39)
P_3(n) = -48778*(n + 1)*(n + 2)*(n + 3)*(2*n + 5)
P_4(n) = 10267*(n + 1)*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 5, 10, 90, 825, 8445, 92820, 1066740, 12670635, 154308775, 1916370170, 24177471370`.

## A120599

- Defining data: `13*A(x)=12+32*x+A(x)^5`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-5*u^1-20*u^2-40*u^3-32*u^4)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 4.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 10 × 10 |
| U | 5 × 5 |
| V | 5 × 5 |
| J | 5 × 5 |
| X | 4 × 5 |

`P_x` dimensions: 5 × 5. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` |
|---|---:|---:|---:|---:|---:|
| `x^0` | 591360 | -1280000 | -7040000 | -6400000 | -1600000 |
| `x^1` | -6120000 | -21000000 | -25680000 | -13200000 | -2400000 |
| `x^2` | -10530000 | -26595000 | -24165000 | -9450000 | -1350000 |
| `x^3` | -5062500 | -11306250 | -8775000 | -2868750 | -337500 |
| `x^4` | 354504 | 738550 | 516985 | 147710 | 14771 |

Canonical recurrence:

```text
P_0(n) = -2560*(5*n - 1)*(5*n + 3)*(5*n + 7)*(5*n + 11)
P_1(n) = -120000*(n + 1)*(2*n + 3)*(10*n**2 + 30*n + 17)
P_2(n) = -135000*(n + 1)*(n + 2)*(10*n**2 + 40*n + 39)
P_3(n) = -168750*(n + 1)*(n + 2)*(n + 3)*(2*n + 5)
P_4(n) = 14771*(n + 1)*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 4, 20, 280, 4660, 86728, 1727880, 36047280, 777470580, 17195957480, 387906427480, 8890184148560`.

## A120600

- Defining data: `7*A(x)=6+1*x+A(x)^6`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-15*u^1-20*u^2-15*u^3-6*u^4-1*u^5)`
- Recurrence: order 5, valid from n=1.
- Verified scalar linear ODE order: 5.
- Term seeds retained: 6; recurrence-generated suffix terms: 18.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 12 × 12 |
| U | 6 × 6 |
| V | 6 × 6 |
| J | 6 × 6 |
| X | 5 × 6 |

`P_x` dimensions: 6 × 6. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` |
|---|---:|---:|---:|---:|---:|---:|
| `x^0` | 57456 | -177480 | -845640 | -887760 | -349920 | -46656 |
| `x^1` | -13844736 | -49769856 | -67301280 | -42573600 | -12597120 | -1399680 |
| `x^2` | -479390400 | -1330745760 | -1409127840 | -717336000 | -176359680 | -16796160 |
| `x^3` | -5383169280 | -13497114240 | -12639110400 | -5633712000 | -1209323520 | -100776960 |
| `x^4` | -25395793920 | -60163845120 | -52152076800 | -21163161600 | -4081466880 | -302330880 |
| `x^5` | 582728280 | 1330562906 | 1092615525 | 412765865 | 72841035 | 4856069 |

Canonical recurrence:

```text
P_0(n) = -72*(2*n + 3)*(3*n + 2)*(3*n + 7)*(6*n - 1)*(6*n + 19)
P_1(n) = -864*(n + 1)*(1620*n**4 + 12960*n**3 + 36315*n**2 + 41580*n + 16024)
P_2(n) = -349920*(n + 1)*(n + 2)*(2*n + 5)*(24*n**2 + 120*n + 137)
P_3(n) = -1399680*(n + 1)*(n + 2)*(n + 3)*(72*n**2 + 432*n + 641)
P_4(n) = -151165440*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(2*n + 7)
P_5(n) = 4856069*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 15, 470, 18390, 805806, 37828981, 1860433080, 94614523740, 4935081398830, 262560448214031, 14193030016877406`.

## A120601

- Defining data: `15*A(x)=14+27*x+A(x)^6`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-5*u^1-20*u^2-45*u^3-54*u^4-27*u^5)`
- Recurrence: order 5, valid from n=1.
- Verified scalar linear ODE order: 5.
- Term seeds retained: 6; recurrence-generated suffix terms: 18.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 12 × 12 |
| U | 6 × 6 |
| V | 6 × 6 |
| J | 6 × 6 |
| X | 5 × 6 |

`P_x` dimensions: 6 × 6. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` |
|---|---:|---:|---:|---:|---:|---:|
| `x^0` | 41885424 | -129382920 | -616471560 | -647177040 | -255091680 | -34012224 |
| `x^1` | -872218368 | -3135500928 | -4239980640 | -2682136800 | -793618560 | -88179840 |
| `x^2` | -2610014400 | -7245171360 | -7671918240 | -3905496000 | -960180480 | -91445760 |
| `x^3` | -2532821760 | -6350494080 | -5946796800 | -2650704000 | -568995840 | -47416320 |
| `x^4` | -1032622080 | -2446330880 | -2120563200 | -860518400 | -165957120 | -12293120 |
| `x^5` | 64032840 | 146208318 | 120061575 | 45356595 | 8004105 | 533607 |

Canonical recurrence:

```text
P_0(n) = -52488*(2*n + 3)*(3*n + 2)*(3*n + 7)*(6*n - 1)*(6*n + 19)
P_1(n) = -54432*(n + 1)*(1620*n**4 + 12960*n**3 + 36315*n**2 + 41580*n + 16024)
P_2(n) = -1905120*(n + 1)*(n + 2)*(2*n + 5)*(24*n**2 + 120*n + 137)
P_3(n) = -658560*(n + 1)*(n + 2)*(n + 3)*(72*n**2 + 432*n + 641)
P_4(n) = -6146560*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(2*n + 7)
P_5(n) = 533607*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 15, 210, 3510, 65562, 1310901, 27446760, 594104940, 13187589690, 298555767279, 6867021319722`.

## A120602

- Defining data: `31*A(x)=30+125*x+A(x)^6`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-3*u^1-20*u^2-75*u^3-150*u^4-125*u^5)`
- Recurrence: order 5, valid from n=1.
- Verified scalar linear ODE order: 5.
- Term seeds retained: 6; recurrence-generated suffix terms: 18.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 12 × 12 |
| U | 6 × 6 |
| V | 6 × 6 |
| J | 6 × 6 |
| X | 5 × 6 |

`P_x` dimensions: 6 × 6. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` |
|---|---:|---:|---:|---:|---:|---:|
| `x^0` | 4488750000 | -13865625000 | -66065625000 | -69356250000 | -27337500000 | -3645000000 |
| `x^1` | -43264800000 | -155530800000 | -210316500000 | -133042500000 | -39366000000 | -4374000000 |
| `x^2` | -59923800000 | -166343220000 | -176140980000 | -89667000000 | -22044960000 | -2099520000 |
| `x^3` | -26915846400 | -67485571200 | -63195552000 | -28168560000 | -6046617600 | -503884800 |
| `x^4` | -5079158784 | -12032769024 | -10430415360 | -4232632320 | -816293376 | -60466176 |
| `x^5` | 503718360 | 1150156922 | 944471925 | 356800505 | 62964795 | 4197653 |

Canonical recurrence:

```text
P_0(n) = -5625000*(2*n + 3)*(3*n + 2)*(3*n + 7)*(6*n - 1)*(6*n + 19)
P_1(n) = -2700000*(n + 1)*(1620*n**4 + 12960*n**3 + 36315*n**2 + 41580*n + 16024)
P_2(n) = -43740000*(n + 1)*(n + 2)*(2*n + 5)*(24*n**2 + 120*n + 137)
P_3(n) = -6998400*(n + 1)*(n + 2)*(n + 3)*(72*n**2 + 432*n + 641)
P_4(n) = -30233088*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(2*n + 7)
P_5(n) = 4197653*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 5, 15, 190, 2550, 38070, 609205, 10199640, 176483340, 3130904150, 56641633455, 1040985874470`.

## A120603

- Defining data: `16*A(x)=15+27*x+A(x)^7`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-7*u^1-35*u^2-105*u^3-189*u^4-189*u^5-81*u^6)`
- Recurrence: order 6, valid from n=1.
- Verified scalar linear ODE order: 6.
- Term seeds retained: 7; recurrence-generated suffix terms: 17.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 14 × 14 |
| U | 7 × 7 |
| V | 7 × 7 |
| J | 7 × 7 |
| X | 6 × 7 |

`P_x` dimensions: 7 × 7. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` | `n^6` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `x^0` | 85926431745 | -344233703772 | -1531046032551 | -1759920802920 | -868381975125 | -194517562428 | -16209796869 |
| `x^1` | -2619061040925 | -9777521578545 | -14202003224745 | -10234042388325 | -3865907904075 | -729440859105 | -54032656230 |
| `x^2` | -10067746547250 | -29896275693375 | -35094898684125 | -21001978879875 | -6786244324125 | -1125680338125 | -75045355875 |
| `x^3` | -13674931515000 | -37149436485000 | -39321384086250 | -21111965988750 | -6126718736250 | -917221016250 | -55589152500 |
| `x^4` | -8841322350000 | -22866553762500 | -22714345368750 | -11327392781250 | -3032035321875 | -416918643750 | -23162146875 |
| `x^5` | -2779457625000 | -6964085493750 | -6621800434375 | -3126889828125 | -784939421875 | -100369303125 | -5147143750 |
| `x^6` | 114986928240 | 281717974188 | 259359404808 | 117382489245 | 27948211725 | 3353785407 | 159704067 |

Canonical recurrence:

```text
P_0(n) = -137781*(7*n - 1)*(7*n + 5)*(7*n + 11)*(7*n + 17)*(7*n + 23)*(7*n + 29)
P_1(n) = -26254935*(n + 1)*(2*n + 5)*(1029*n**4 + 10290*n**3 + 35035*n**2 + 46550*n + 19951)
P_2(n) = -72930375*(n + 1)*(n + 2)*(1029*n**4 + 12348*n**3 + 53949*n**2 + 101430*n + 69023)
P_3(n) = -3970653750*(n + 1)*(n + 2)*(n + 3)*(2*n + 7)*(7*n**2 + 49*n + 82)
P_4(n) = -1102959375*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(21*n**2 + 168*n + 334)
P_5(n) = -2573571875*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(2*n + 9)
P_6(n) = 159704067*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 21, 399, 9135, 233709, 6400947, 183585897, 5443737390, 165536020650, 5133935821014, 161768728483362`.

## A120604

- Defining data: `24*A(x)=23+64*x+A(x)^8`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-7*u^1-56*u^2-280*u^3-896*u^4-1792*u^5-2048*u^6-1024*u^7)`
- Recurrence: order 7, valid from n=1.
- Verified scalar linear ODE order: 7.
- Term seeds retained: 8; recurrence-generated suffix terms: 16.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 16 × 16 |
| U | 8 × 8 |
| V | 8 × 8 |
| J | 8 × 8 |
| X | 7 × 8 |

`P_x` dimensions: 8 × 8. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` | `n^6` | `n^7` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `x^0` | 7695929180160 | -37899139547136 | -162562331115520 | -199558206324736 | -113494510796800 | -33131377721344 | -4810363371520 | -274877906944 |
| `x^1` | -198278258688000 | -764013764739072 | -1172677959090176 | -927188636401664 | -409167441428480 | -101368073289728 | -13138304958464 | -691489734656 |
| `x^2` | -573197269155840 | -1792981912608768 | -2271837831094272 | -1522308412391424 | -585110724280320 | -129392990748672 | -15283003588608 | -745512370176 |
| `x^3` | -619474554800640 | -1788084917525760 | -2068522968762880 | -1262356112684800 | -443014416302080 | -89948057436160 | -9823678627840 | -446530846720 |
| `x^4` | -341745232066560 | -943891424770560 | -1033542630767360 | -592783653109760 | -194720263082240 | -36943668554240 | -3771092541440 | -160472023040 |
| `x^5` | -103416069879360 | -277655495519472 | -292866221732280 | -160587942137112 | -50123922200520 | -8993218874808 | -865044499200 | -34601779968 |
| `x^6` | -16414219372320 | -43199240984424 | -44334972324832 | -23487670220518 | -7036145804170 | -1204123921126 | -109842629638 | -4145004892 |
| `x^7` | 629508655440 | 1632226013748 | 1640219774452 | 845465096959 | 244808921560 | 40218608542 | 3497270308 | 124902511 |

Canonical recurrence:

```text
P_0(n) = -2097152*(2*n + 5)*(4*n + 3)*(4*n + 17)*(8*n - 1)*(8*n + 13)*(8*n + 27)*(8*n + 41)
P_1(n) = -1507328*(n + 1)*(458752*n**6 + 8257536*n**5 + 58992640*n**4 + 212459520*n**3 + 402661168*n**2 + 375323424*n + 131542875)
P_2(n) = -91004928*(n + 1)*(n + 2)*(2*n + 7)*(4096*n**4 + 57344*n**3 + 286976*n**2 + 603904*n + 449895)
P_3(n) = -109016320*(n + 1)*(n + 2)*(n + 3)*(4096*n**4 + 65536*n**3 + 386816*n**2 + 997376*n + 947067)
P_4(n) = -2507375360*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(2*n + 9)*(32*n**2 + 288*n + 631)
P_5(n) = -1081305624*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(32*n**2 + 320*n + 797)
P_6(n) = -2072502446*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(2*n + 11)
P_7(n) = 124902511*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 4, 28, 616, 15820, 453208, 13894552, 445970128, 14796844588, 503423385080, 17467725995720, 615756709476272`.

## A120605

- Defining data: `25*A(x)=24+64*x+A(x)^9`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-9*u^1-84*u^2-504*u^3-2016*u^4-5376*u^5-9216*u^6-9216*u^7-4096*u^8)`
- Recurrence: order 8, valid from n=1.
- Verified scalar linear ODE order: 8.
- Term seeds retained: 9; recurrence-generated suffix terms: 15.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 18 × 18 |
| U | 9 × 9 |
| V | 9 × 9 |
| J | 9 × 9 |
| X | 8 × 9 |

`P_x` dimensions: 9 × 9. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` | `n^6` | `n^7` | `n^8` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `x^0` | 71227287561830400 | -416449128604631040 | -1751568737221214208 | -2263677536456146944 | -1424692173997080576 | -492904323030712320 | -95631864382881792 | -9749755840167936 | -406239826673664 |
| `x^1` | -2420654909759815680 | -9584186081289043968 | -15383091085476102144 | -13058724950941630464 | -6439919220683440128 | -1901236242151636992 | -330340685723467776 | -31077346740535296 | -1218719480020992 |
| `x^2` | -8307963641761136640 | -27105592249843236864 | -36469569495083139072 | -26614874026099408896 | -11574224666431193088 | -3081748020140998656 | -492045295063891968 | -43188371573243904 | -1599569317527552 |
| `x^3` | -11095864301253795840 | -33616055494337089536 | -41657190152355864576 | -27970822381405188096 | -11227623338293641216 | -2774786224859357184 | -413977425872338944 | -34190794162151424 | -1199676988145664 |
| `x^4` | -7913273679798036480 | -23024226418306444800 | -27164983822812622080 | -17275933605538137600 | -6551544516428701440 | -1528963328121062400 | -215629441983889920 | -16870457645798400 | -562348588193280 |
| `x^5` | -3309421441517452800 | -9383020505916624000 | -10709727353896915008 | -6551834362513441344 | -2379995126142774336 | -530458737004486080 | -71315173459377792 | -5314194158426496 | -168704576457984 |
| `x^6` | -817795434380077440 | -2276900228093123808 | -2536946617107518784 | -1507078400303947464 | -529135460482893768 | -113529393259532712 | -14642737144861896 | -1043859566833776 | -31632108085872 |
| `x^7` | -111028699381410720 | -304962894619600104 | -333580914692146872 | -193624087607133246 | -66119013926493948 | -13736242936289916 | -1708133836637088 | -116925828103134 | -3389154437772 |
| `x^8` | 3207535221985920 | 8717622514040304 | 9396996293697044 | 5352574401689004 | 1785862058491119 | 360847712473416 | 43435372797726 | 2863870733916 | 79551964831 |

Canonical recurrence:

```text
P_0(n) = -84934656*(3*n + 5)*(3*n + 13)*(9*n - 1)*(9*n + 7)*(9*n + 23)*(9*n + 31)*(9*n + 47)*(9*n + 55)
P_1(n) = -286654464*(n + 1)*(2*n + 7)*(2125764*n**6 + 44641044*n**5 + 367875270*n**4 + 1504568520*n**3 + 3174773616*n**2 + 3225344346*n + 1206357785)
P_2(n) = -752467968*(n + 1)*(n + 2)*(2125764*n**6 + 51018336*n**5 + 496602090*n**4 + 2503677600*n**3 + 6877447236*n**2 + 9730412064*n + 5520476615)
P_3(n) = -137137287168*(n + 1)*(n + 2)*(n + 3)*(2*n + 9)*(4374*n**4 + 78732*n**3 + 516456*n**2 + 1459458*n + 1498345)
P_4(n) = -128566206720*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(4374*n**4 + 87480*n**3 + 649296*n**2 + 2118960*n + 2564591)
P_5(n) = -4686238234944*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(2*n + 11)*(18*n**2 + 198*n + 535)
P_6(n) = -585779779368*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(54*n**2 + 648*n + 1939)
P_7(n) = -1694577218886*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(2*n + 13)
P_8(n) = 79551964831*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(n + 8)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 4, 36, 984, 31716, 1140552, 43895208, 1768717872, 73674176868, 3146885203432, 137085166193976, 6066992348458704`.

## A120606

- Defining data: `36*A(x)=35+81*x+A(x)^9`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-4*u^1-28*u^2-126*u^3-378*u^4-756*u^5-972*u^6-729*u^7-243*u^8)`
- Recurrence: order 8, valid from n=1.
- Verified scalar linear ODE order: 8.
- Term seeds retained: 9; recurrence-generated suffix terms: 15.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 18 × 18 |
| U | 9 × 9 |
| V | 9 × 9 |
| J | 9 × 9 |
| X | 8 × 9 |

`P_x` dimensions: 9 × 9. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` | `n^6` | `n^7` | `n^8` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `x^0` | 4011058905828975 | -23451714129423960 | -98636991848159292 | -127475638246726056 | -80229423696855174 | -27757174845352680 | -5385366401619708 | -549043018919064 | -22876792454961 |
| `x^1` | -157071456966455325 | -621898671122461845 | -998178021865648260 | -847354550993031060 | -417873481536198870 | -123367418209073430 | -21435146576523540 | -2016546890474340 | -79080270214680 |
| `x^2` | -621170377267907250 | -2026632721317014475 | -2726759193815725425 | -1989942668577378900 | -865382398460584200 | -230416340617231650 | -36789275296219950 | -3229111033766100 | -119596704954300 |
| `x^3` | -955936499156572500 | -2896107372282710250 | -3588871262101051500 | -2409756401111487750 | -967287870188199000 | -239054782726588500 | -35665192045791000 | -2945622547948500 | -103355177121000 |
| `x^4` | -785553650076825000 | -2285623603448718750 | -2696678146083403125 | -1714988417115093750 | -650374284622584375 | -151780763795062500 | -21405615686831250 | -1674736666312500 | -55824555543750 |
| `x^5` | -378550216563750000 | -1073282598576562500 | -1225038781188731250 | -749435622101381250 | -272237213163431250 | -60676850416218750 | -8157430183612500 | -607867382587500 | -19297377225000 |
| `x^6` | -107787366697500000 | -300100819228875000 | -334375546517250000 | -198636487006781250 | -69741301447781250 | -14963441745656250 | -1929947284781250 | -137583152437500 | -4169186437500 |
| `x^7` | -16862042925000000 | -46315028891250000 | -50661277073750000 | -29405889600937500 | -10041562741875000 | -2086137361875000 | -259416045000000 | -17757645937500 | -514714375000 |
| `x^8` | 1068316291082880 | 2903531062550256 | 3129806388092116 | 1782752810744556 | 594807351649791 | 120185582746824 | 14466783108414 | 953853831324 | 26495939759 |

Canonical recurrence:

```text
P_0(n) = -4782969*(3*n + 5)*(3*n + 13)*(9*n - 1)*(9*n + 7)*(9*n + 23)*(9*n + 31)*(9*n + 47)*(9*n + 55)
P_1(n) = -18600435*(n + 1)*(2*n + 7)*(2125764*n**6 + 44641044*n**5 + 367875270*n**4 + 1504568520*n**3 + 3174773616*n**2 + 3225344346*n + 1206357785)
P_2(n) = -56260575*(n + 1)*(n + 2)*(2125764*n**6 + 51018336*n**5 + 496602090*n**4 + 2503677600*n**3 + 6877447236*n**2 + 9730412064*n + 5520476615)
P_3(n) = -11814720750*(n + 1)*(n + 2)*(n + 3)*(2*n + 9)*(4374*n**4 + 78732*n**3 + 516456*n**2 + 1459458*n + 1498345)
P_4(n) = -12762815625*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(4374*n**4 + 87480*n**3 + 649296*n**2 + 2118960*n + 2564591)
P_5(n) = -536038256250*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(2*n + 11)*(18*n**2 + 198*n + 535)
P_6(n) = -77207156250*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(54*n**2 + 648*n + 1939)
P_7(n) = -257357187500*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(2*n + 13)
P_8(n) = 26495939759*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(n + 8)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 12, 180, 3018, 56238, 1121484, 23406804, 504914175, 11167352013, 251879507880, 5771456609880`.

## A120607

- Defining data: `37*A(x)=36+81*x+A(x)^10`
- Reduction route: term-shift polynomial G/U/V.
- Contour/kernel record: `u*(1-5*u^1-40*u^2-210*u^3-756*u^4-1890*u^5-3240*u^6-3645*u^7-2430*u^8-729*u^9)`
- Recurrence: order 9, valid from n=1.
- Verified scalar linear ODE order: 9.
- Term seeds retained: 10; recurrence-generated suffix terms: 14.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| G | 20 × 20 |
| U | 10 × 10 |
| V | 10 × 10 |
| J | 10 × 10 |
| X | 9 × 10 |

`P_x` dimensions: 10 × 10. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` | `n^4` | `n^5` | `n^6` | `n^7` | `n^8` | `n^9` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `x^0` | 60765412591845561600 | -411585265795186382400 | -1713370388457968100000 | -2309791335910747200000 | -1571056697695747500000 | -613933066696257000000 | -143783222593500000000 | -19930631823000000000 | -1506635235000000000 | -47829690000000000 |
| `x^1` | -3015557810621069414400 | -12226537462320826214400 | -20372865928799666400000 | -18310856628451269600000 | -9831404481830820000000 | -3292052227343460000000 | -692159387220000000000 | -88663490676000000000 | -6313519080000000000 | -191318760000000000 |
| `x^2` | -13734552585302438400000 | -46418781904152652800000 | -65597034406576752000000 | -51226851223679097600000 | -24476155577632080000000 | -7447206055655520000000 | -1447530492744000000000 | -173827973808000000000 | -11734217280000000000 | -340122240000000000 |
| `x^3` | -25085978785653811200000 | -79107568422219187200000 | -103634639243015731200000 | -75015844564847155200000 | -33339535474129920000000 | -9487162552533120000000 | -1735467431040000000000 | -197390571840000000000 | -12697896960000000000 | -352719360000000000 |
| `x^4` | -25252524724331520000000 | -76690890743120640000000 | -96067552211164800000000 | -66226976396582400000000 | -27986631106654080000000 | -7573537052847360000000 | -1319336968320000000000 | -143223655680000000000 | -8817984000000000000 | -235146240000000000 |
| `x^5` | -15556186877091840000000 | -46122233705146368000000 | -56065821201331200000000 | -37340117559198720000000 | -15196973535636480000000 | -3952929861522432000000 | -661246903296000000000 | -68918750208000000000 | -4075868160000000000 | -104509440000000000 |
| `x^6` | -6046776852480000000000 | -17628833488896000000000 | -20968464384000000000000 | -13607859492864000000000 | -5377809991680000000000 | -1354483759104000000000 | -218910504960000000000 | -22008139776000000000 | -1254113280000000000 | -30965760000000000 |
| `x^7` | -1453904363520000000000 | -4185946128384000000000 | -4897050525696000000000 | -3114132160512000000000 | -1201815552000000000000 | -294661226496000000000 | -46227062784000000000 | -4499816448000000000 | -247726080000000000 | -5898240000000000 |
| `x^8` | -198180864000000000000 | -565051392000000000000 | -652420055040000000000 | -408128061440000000000 | -154436567040000000000 | -37007523840000000000 | -5656412160000000000 | -534773760000000000 | -28508160000000000 | -655360000000000 |
| `x^9` | 9798406788431963520 | 27719381743941058704 | 31664990191782858300 | 19540649869522826720 | 7272255038289347925 | 1708483776246846417 | 255166843448749050 | 23491550666710230 | 1215080206898805 | 27001782375529 |

Canonical recurrence:

```text
P_0(n) = -3826375200*(2*n + 7)*(5*n + 4)*(5*n + 13)*(5*n + 22)*(5*n + 31)*(10*n - 1)*(10*n + 17)*(10*n + 53)*(10*n + 71)
P_1(n) = -3401222400*(n + 1)*(56250000*n**8 + 1800000000*n**7 + 24268125000*n**6 + 179235000000*n**5 + 788667665625*n**4 + 2101882650000*n**3 + 3281727850875*n**2 + 2708138007000*n + 886610005456)
P_2(n) = -566870400000*(n + 1)*(n + 2)*(2*n + 9)*(300000*n**6 + 8100000*n**5 + 87922500*n**4 + 489105000*n**3 + 1464716275*n**2 + 2231043975*n + 1346040822)
P_3(n) = -1175731200000*(n + 1)*(n + 2)*(n + 3)*(300000*n**6 + 9000000*n**5 + 110587500*n**4 + 711750000*n**3 + 2528196975*n**2 + 4694469750*n + 3556081921)
P_4(n) = -9797760000000*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(2*n + 11)*(12000*n**4 + 264000*n**3 + 2137000*n**2 + 7535000*n + 9762793)
P_5(n) = -1741824000000*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(60000*n**4 + 1440000*n**3 + 12867000*n**2 + 50724000*n + 74424793)
P_6(n) = -387072000000000*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(2*n + 13)*(40*n**2 + 520*n + 1669)
P_7(n) = -49152000000000*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(120*n**2 + 1680*n + 5869)
P_8(n) = -327680000000000*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(n + 8)*(2*n + 15)
P_9(n) = 27001782375529*(n + 1)*(n + 2)*(n + 3)*(n + 4)*(n + 5)*(n + 6)*(n + 7)*(n + 8)*(n + 9)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 3, 15, 270, 5505, 124818, 3028200, 76896180, 2018211930, 54311811330, 1490518569747, 41556060361920`.

## A244594

- Defining data: `(4-1*x)*A(x)=3+A(x)^3`
- Reduction route: numerator-aware direct-x Gx/Ux/Vx.
- Contour/kernel record: `u*(1-3*u^1-1*u^2)/(1+1*u)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| Gx | 6 × 6 |
| Ux | 3 × 3 |
| Vx | 3 × 3 |
| J | 3 × 3 |
| X | 2 × 3 |

`P_x` dimensions: 5 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | 0 | -2 | 2 | 4 |
| `x^1` | -32 | -136 | -168 | -64 |
| `x^2` | 1472 | 2848 | 1824 | 384 |
| `x^3` | -11520 | -14286 | -5825 | -781 |
| `x^4` | 1248 | 1352 | 468 | 52 |

Canonical recurrence:

```text
P_0(n) = 2*n*(n + 1)*(2*n - 1)
P_1(n) = -8*(n + 1)*(8*n**2 + 13*n + 4)
P_2(n) = 32*(n + 2)*(12*n**2 + 33*n + 23)
P_3(n) = -(n + 2)*(n + 3)*(781*n + 1920)
P_4(n) = 52*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 4, 29, 263, 2672, 29088, 331749, 3912660, 47329811, 583983656, 7321173872`.

## A244627

- Defining data: `(5-4*x)*A(x)=4+A(x)^3`
- Reduction route: numerator-aware direct-x Gx/Ux/Vx.
- Contour/kernel record: `u*(1-3*u^1-2*u^2)/(1+2*u)`
- Recurrence: order 4, valid from n=1.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 5; recurrence-generated suffix terms: 19.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| Gx | 6 × 6 |
| Ux | 3 × 3 |
| Vx | 3 × 3 |
| J | 3 × 3 |
| X | 2 × 3 |

`P_x` dimensions: 5 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | 0 | -128 | 128 | 256 |
| `x^1` | -640 | -2720 | -3360 | -1280 |
| `x^2` | 9200 | 17800 | 11400 | 2400 |
| `x^3` | -22500 | -28158 | -11590 | -1568 |
| `x^4` | 2040 | 2210 | 765 | 85 |

Canonical recurrence:

```text
P_0(n) = 128*n*(n + 1)*(2*n - 1)
P_1(n) = -160*(n + 1)*(8*n**2 + 13*n + 4)
P_2(n) = 200*(n + 2)*(12*n**2 + 33*n + 23)
P_3(n) = -2*(n + 2)*(n + 3)*(784*n + 1875)
P_4(n) = 85*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 2, 10, 84, 882, 10380, 130916, 1729960, 23640770, 331357276, 4737405356, 68818101400`.

## A244856

- Defining data: `(5-1*x)*A(x)=4+A(x)^4`
- Reduction route: numerator-aware direct-x Gx/Ux/Vx; attached order-4 term-shift certificate is canonical.
- Contour/kernel record: `u*(1-6*u^1-4*u^2-1*u^3)/(1+1*u)`
- Recurrence: order 4, valid from n=0.
- Verified scalar linear ODE order: 3.
- Term seeds retained: 4; recurrence-generated suffix terms: 20.
- Checks: generated 24/24 stored terms exactly; published prefix 6/6 matched; maximum recurrence residual 0.

Standard matrix dimensions:

| Matrix | Dimensions |
|---|---:|
| Gx | 8 × 8 |
| Ux | 4 × 4 |
| Vx | 4 × 4 |
| J | 4 × 4 |
| X | 3 × 4 |

`P_x` dimensions: 5 × 4. Rows are shifts `x^r`; columns are powers `n^k`.

| row | `n^0` | `n^1` | `n^2` | `n^3` |
|---|---:|---:|---:|---:|
| `x^0` | -21 | 33 | 81 | 27 |
| `x^1` | -1305 | -3300 | -2430 | -540 |
| `x^2` | 31350 | 48075 | 24300 | 4050 |
| `x^3` | -202500 | -249750 | -101250 | -13500 |
| `x^4` | 11784 | 12766 | 4419 | 491 |

Canonical recurrence:

```text
P_0(n) = 3*(n + 1)*(3*n - 1)*(3*n + 7)
P_1(n) = -15*(2*n + 3)*(18*n**2 + 54*n + 29)
P_2(n) = 75*(n + 2)*(54*n**2 + 216*n + 209)
P_3(n) = -6750*(n + 2)*(n + 3)*(2*n + 5)
P_4(n) = 491*(n + 2)*(n + 3)*(n + 4)
```

First terms reconstructed from `P_n` after the stated seeds: `1, 1, 7, 95, 1614, 30718, 626434, 13383650, 295692145, 6700461777, 154871912815, 3637093846055`.

Quality note: the attached order-4 recurrence/certificate and the independent matrix-derived order-5 recurrence both pass. The shorter attached result is canonical; minimality is not claimed.

