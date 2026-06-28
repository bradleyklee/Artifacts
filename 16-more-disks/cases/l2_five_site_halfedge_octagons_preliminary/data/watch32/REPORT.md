# L=2 half-edge hard-octagon restart — exact scan report

Approved geometry: five unit-edge background octagon centers; square side `3 + 2 sqrt(2)`; moving octagons edge `1/2`.

Full-state complexity cap: 32 bits, taking the maximum exact numerator/denominator bit length over all Q(sqrt(2)) position coefficients and rational velocity coefficients.

`LOW_COMPLEXITY_WATCH` is not an event-budget rejection or a proof of aperiodicity. It means valid and unlabeled-nonrepeating through an exact 2,048-event observation checkpoint while still at or below the 32-bit cap.

## N=2

Status counts: `RETURN` = 24

## N=3

Status counts: `COMPLEXITY_CUTOFF` = 7, `LOW_COMPLEXITY_WATCH` = 12, `REJECT` = 6, `RETURN` = 22, `UNKNOWN_CORNER` = 37

| class | status | batches | max state bits | raw representative |
|---:|---|---:|---:|---|
| 3 | UNKNOWN_CORNER | 5 | 3 | `B[+0,+0] +y ; A[+1,-1] -x ; A[+1,+1] -x` |
| 6 | UNKNOWN_CORNER | 25 | 3 | `B[+0,+0] +y ; A[+1,-1] -x ; A[+1,+1] +x` |
| 7 | UNKNOWN_CORNER | 7 | 3 | `B[+0,+0] +y ; A[+1,-1] +x ; A[+1,+1] -x` |
| 8 | UNKNOWN_CORNER | 6 | 3 | `B[+0,+0] -x ; A[+1,-1] -y ; A[+1,+1] -x` |
| 9 | UNKNOWN_CORNER | 7 | 3 | `B[+0,+0] +x ; A[+1,-1] -y ; A[+1,+1] -x` |
| 10 | UNKNOWN_CORNER | 47 | 5 | `B[+0,+0] +y ; A[+1,-1] -x ; A[+1,+1] +y` |
| 11 | UNKNOWN_CORNER | 25 | 3 | `B[+0,+0] +y ; A[+1,-1] -y ; A[+1,+1] -x` |
| 12 | UNKNOWN_CORNER | 14 | 3 | `B[+0,+0] -x ; A[+1,-1] +y ; A[+1,+1] -x` |
| 13 | UNKNOWN_CORNER | 2 | 3 | `B[+0,+0] +x ; A[+1,-1] +y ; A[+1,+1] -x` |
| 14 | UNKNOWN_CORNER | 4 | 3 | `B[+0,+0] +y ; A[+1,-1] -x ; A[+1,+1] -y` |
| 15 | UNKNOWN_CORNER | 12 | 3 | `B[+0,+0] +y ; A[+1,-1] +y ; A[+1,+1] -x` |
| 18 | UNKNOWN_CORNER | 6 | 3 | `B[+0,+0] +y ; A[+1,-1] +x ; A[+1,+1] +x` |
| 19 | UNKNOWN_CORNER | 6 | 3 | `B[+0,+0] -x ; A[+1,-1] -y ; A[+1,+1] +x` |
| 20 | UNKNOWN_CORNER | 6 | 3 | `B[+0,+0] +x ; A[+1,-1] -y ; A[+1,+1] +x` |
| 21 | UNKNOWN_CORNER | 8 | 3 | `B[+0,+0] +y ; A[+1,-1] +x ; A[+1,+1] +y` |
| 22 | UNKNOWN_CORNER | 4 | 3 | `B[+0,+0] +y ; A[+1,-1] -y ; A[+1,+1] +x` |
| 23 | UNKNOWN_CORNER | 28 | 3 | `B[+0,+0] -x ; A[+1,-1] +y ; A[+1,+1] +x` |
| 24 | UNKNOWN_CORNER | 44 | 5 | `B[+0,+0] +x ; A[+1,-1] +y ; A[+1,+1] +x` |
| 25 | UNKNOWN_CORNER | 10 | 3 | `B[+0,+0] +y ; A[+1,-1] +x ; A[+1,+1] -y` |
| 26 | UNKNOWN_CORNER | 3 | 3 | `B[+0,+0] +y ; A[+1,-1] +y ; A[+1,+1] +x` |
| 27 | REJECT | 5 | 3 | `B[+0,+0] -x ; A[+1,-1] +y ; A[+1,+1] +y` |
| 28 | COMPLEXITY_CUTOFF | 562 | 33 | `B[+0,+0] +x ; A[+1,-1] +y ; A[+1,+1] +y` |
| 29 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `B[+0,+0] +y ; A[+1,-1] +y ; A[+1,+1] +y` |
| 30 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `B[+0,+0] +y ; A[+1,-1] -y ; A[+1,+1] -y` |
| 31 | REJECT | 6 | 3 | `B[+0,+0] -x ; A[+1,-1] +y ; A[+1,+1] -y` |
| 32 | REJECT | 0 | 2 | `B[+0,+0] +x ; A[+1,-1] +y ; A[+1,+1] -y` |
| 33 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `B[+0,+0] +y ; A[+1,-1] +y ; A[+1,+1] -y` |
| 34 | REJECT | 3 | 3 | `B[+0,+0] -x ; A[+1,-1] -y ; A[+1,+1] +y` |
| 35 | REJECT | 1 | 3 | `B[+0,+0] +x ; A[+1,-1] -y ; A[+1,+1] +y` |
| 36 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `B[+0,+0] +y ; A[+1,-1] -y ; A[+1,+1] +y` |
| 37 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] -y ; A[+1,-1] -y ; A[+1,+1] -y` |
| 38 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] -y ; A[+1,-1] +y ; A[+1,+1] -y` |
| 39 | UNKNOWN_CORNER | 5 | 3 | `A[-1,+1] -y ; A[+1,-1] -x ; A[+1,+1] -y` |
| 40 | UNKNOWN_CORNER | 98 | 4 | `A[-1,+1] +y ; A[+1,-1] -x ; A[+1,+1] -x` |
| 41 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] +y ; A[+1,-1] -y ; A[+1,+1] -y` |
| 42 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] +y ; A[+1,-1] +y ; A[+1,+1] -y` |
| 43 | UNKNOWN_CORNER | 17 | 3 | `A[-1,+1] +y ; A[+1,-1] -x ; A[+1,+1] -y` |
| 44 | COMPLEXITY_CUTOFF | 539 | 33 | `A[-1,+1] +y ; A[+1,-1] +x ; A[+1,+1] -y` |
| 46 | COMPLEXITY_CUTOFF | 518 | 33 | `A[-1,+1] +x ; A[+1,-1] -y ; A[+1,+1] -x` |
| 49 | UNKNOWN_CORNER | 21 | 3 | `A[-1,+1] +x ; A[+1,-1] -y ; A[+1,+1] -y` |
| 53 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] -y ; A[+1,-1] -y ; A[+1,+1] +y` |
| 54 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] -y ; A[+1,-1] +y ; A[+1,+1] +y` |
| 55 | UNKNOWN_CORNER | 5 | 3 | `A[-1,+1] -y ; A[+1,-1] -x ; A[+1,+1] +y` |
| 56 | UNKNOWN_CORNER | 12 | 3 | `A[-1,+1] +y ; A[+1,-1] -x ; A[+1,+1] +x` |
| 57 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] +y ; A[+1,-1] -y ; A[+1,+1] +y` |
| 58 | LOW_COMPLEXITY_WATCH | 2048 | 9 | `A[-1,+1] +y ; A[+1,-1] +y ; A[+1,+1] +y` |
| 59 | UNKNOWN_CORNER | 93 | 4 | `A[-1,+1] +y ; A[+1,-1] -x ; A[+1,+1] +y` |
| 60 | UNKNOWN_CORNER | 6 | 3 | `A[-1,+1] +y ; A[+1,-1] +x ; A[+1,+1] +y` |
| 62 | UNKNOWN_CORNER | 6 | 3 | `A[-1,+1] +x ; A[+1,-1] -y ; A[+1,+1] +x` |
| 65 | COMPLEXITY_CUTOFF | 552 | 33 | `A[-1,+1] +x ; A[+1,-1] -y ; A[+1,+1] +y` |
| 71 | UNKNOWN_CORNER | 28 | 5 | `A[-1,+1] +y ; B[+0,+0] -x ; A[+1,-1] -x` |
| 72 | UNKNOWN_CORNER | 6 | 3 | `A[-1,+1] -y ; B[+0,+0] -y ; A[+1,-1] -x` |
| 74 | UNKNOWN_CORNER | 14 | 3 | `A[-1,+1] +y ; B[+0,+0] +x ; A[+1,-1] -x` |
| 75 | UNKNOWN_CORNER | 5 | 3 | `A[-1,+1] -y ; B[+0,+0] +y ; A[+1,-1] -x` |
| 76 | UNKNOWN_CORNER | 7 | 4 | `A[-1,+1] +y ; B[+0,+0] -x ; A[+1,-1] +y` |
| 77 | UNKNOWN_CORNER | 10 | 3 | `A[-1,+1] -y ; B[+0,+0] +x ; A[+1,-1] +y` |
| 78 | COMPLEXITY_CUTOFF | 523 | 33 | `A[-1,+1] +y ; B[+0,+0] +y ; A[+1,-1] -x` |
| 79 | UNKNOWN_CORNER | 5 | 3 | `A[-1,+1] +y ; B[+0,+0] +x ; A[+1,-1] +y` |
| 80 | COMPLEXITY_CUTOFF | 492 | 33 | `A[-1,+1] +y ; B[+0,+0] -y ; A[+1,-1] -x` |
| 82 | UNKNOWN_CORNER | 41 | 4 | `A[-1,+1] +y ; B[+0,+0] -y ; A[+1,-1] +x` |
| 83 | REJECT | 20 | 4 | `A[-1,+1] +y ; B[+0,+0] +y ; A[+1,-1] +x` |
| 84 | COMPLEXITY_CUTOFF | 476 | 33 | `A[-1,+1] +y ; B[+0,+0] +x ; A[+1,-1] -y` |

