# Tested checkpoint

The included `examples/q2` through `examples/q5` were generated with:

```bash
./run_examples_q2_q5.sh examples
```

Each example includes both the fast shift-reduction path and the slower direct Klee ODE path.

| q | det(G) | direct ODE order | independent checks |
|---:|---:|---:|---:|
| 2 | -1 | 1 | 50/50 |
| 3 | -13 | 2 | 65/65 |
| 4 | -491 | 3 | 86/86 |
| 5 | -37531 | 4 | 113/113 |

For every case, the direct ODE induces exactly the same primitive P-recurrence as the fast shift reduction. The integrand-level recurrence certificate and direct ODE certificate both have exact zero cleared residuals.
