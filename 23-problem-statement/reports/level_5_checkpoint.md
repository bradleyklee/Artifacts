# Level 5 checkpoint

This is a checkpoint, not a completed exact level.

Coding convention: `0` is empty, integer `k` is the occupied leaf labeled `k`, and `{a,b,c,d}` lists children in `NW,SW,SE,NE` order.

## Current exact record

`{0,4,0,{0,0,{0,3,0,5},{1,0,0,2}}}`

- manifest lookup ID: 14974
- first feasible inflation: 1
- width: 8
- exact shortest length: 48
- normalized value: 6

## Search coverage

- total symmetry classes: 31,968
- closed classes: 29,157
- unresolved classes: 2,811
- closed fraction: 91.21%

## Refinement data for the same labeled tree

| inflation l | width | exact L_min | normalized C |
|---:|---:|---:|---:|
| 1 | 8 | 48 | 6 |
| 2 | 16 | 32 | 2 |
| 3 | 24 | 44 | 11/6 |
| 4 | 32 | 56 | 7/4 |
| 5 | 40 | 68 | 17/10 |

The drop from 6 at l=1 to 2 at l=2 is the corner-trap phenomenon that motivates distinguishing the first-resolution invariant from refinement-stable alternatives.
