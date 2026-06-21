# Exact certificates used in the triomino–tetromino–pentomino figure

All membership decisions use exact rational arithmetic. Floating point is used only to sample the already-certified curves for drawing.

| shape | circle result | circle certificate | axis-aligned ellipse certificate |
|---|---|---|---|
| I3 | FAIL; admits 2 immediate exterior site(s) | C=(0,1), r²=1, fence gap=0 | `2x² + y² - 2y ≤ 0` |
| L3 | PASS | C=(1/6,1/6), r²=13/18, fence gap=2/3 | `3x² + 3y² - x - y - 2 ≤ 0` |
| I4 | FAIL; admits 4 immediate exterior site(s) | C=(0,3/2), r²=9/4, fence gap=-1 | `3x² + y² - 3y ≤ 0` |
| T4 | PASS | C=(1/4,1), r²=17/16, fence gap=1/2 | `3x² + 2y² - x - 4y ≤ 0` |
| O4 | PASS | C=(1/2,1/2), r²=1/2, fence gap=2 | `x² + y² - x - y ≤ 0` |
| I5 | FAIL; admits 6 immediate exterior site(s) | C=(0,2), r²=4, fence gap=-3 | `5x² + y² - 4y ≤ 0` |
| Y5 | FAIL; admits 3 immediate exterior site(s) | C=(0,3/2), r²=9/4, fence gap=-1 | `20x² + 5y² - 2x - 11y - 12 ≤ 0` |
| P5 | PASS | C=(3/10,9/10), r²=13/10, fence gap=2/5 | `7x² + 4y² - 3x - 6y - 4 ≤ 0` |
| X5 | PASS | C=(1,1), r²=1, fence gap=1 | `x² + y² - 2x - 2y + 1 ≤ 0` |

Every green ellipse satisfies `Q(p) <= 0` for every occupied lattice site `p` and `Q(e) > 0` for every immediate exterior lattice site `e`.
For red circles, the marked red hollow sites are immediate-exterior sites that the plotted circle includes or touches.
