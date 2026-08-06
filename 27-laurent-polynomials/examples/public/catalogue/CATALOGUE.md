# Public period catalogue

This catalogue contains the eleven public plane-Hamiltonian records supplied in the complete fact sheet. The records are normalized in `models.json`; all exact certificate files are under `certificates/`.

| # | fibres | Hamiltonian 2H | arithmetic variable | Laurent status | certificate status |
|---:|---|---|---|---|---|
| 1 | I1 I1 I1 III* | `p**2 + p*q**2 + q**3 + q**2` | `t = E/32` | complete | double exact |
| 2 | I1 I1 I2 IV* | `p**3 + p**2 + q**3 + q**2` | `t = E/32` | complete | double exact |
| 3 | I1 I1 II IV* | `-p**3 - 3*p**2*q + p**2 - 2*q**3 + q**2` | `t = E/32` | complete | double exact |
| 4 | I1 I1 I1 I3* | `8*p**4 - 8*p**3 - 16*p**2*q**2 + p**2 + 8*p*q**2 + 8*q**4 + q**2` | `t = E/1` | open | period/ODE data only |
| 5 | I1 I1 I2 I2* | `180*p**4 - 4*p**3 - 90*p**2*q**2 - 32*p**2*q + p**2 + p*q**2 + 45*q**4/4 + 8*q**3 + q**2` | `t = E/16` | open | period/ODE data only |
| 6 | I1 I1 I2* II | `88209*p**4/2368 - 27*p**3/37 - 3267*p**2*q**2/32 - 63*sqrt(111)*p**2*q/37 + p**2 + p*q**2 + 4477*q**4/64 + 7*sqrt(111)*q**3/3 + q**2` | `t = E/262848` | open | period/ODE data only |
| 7 | I1 I1 I1* I3 | `p**4 + p**3 + 2*p**2*q**2 + p**2*q + p**2 + p*q**2 + q**4 + q**3 + q**2` | `t = E/2` | open | period/ODE data only |
| 8 | I1 I1 I1* III | `5*p**4/32 - p**3 - 5*p**2*q**2/16 + p**2 + p*q**2 + 5*q**4/32 + q**2` | `t = E/128` | open | period/ODE data only |
| 9 | I1 I1* I2 I2 | `16*p**4 - 8*p**2*q**2 + p**2 + q**4 + q**2` | `t = E/16` | complete | double exact |
| 10 | I1 I1* I2 II | `9*p**4/32 - p**3 - 9*p**2*q**2/16 + p**2 + p*q**2 + 9*q**4/32 + q**2` | `t = E/128` | open | period/ODE data only |
| 11 | I1 I1* II II | `p**4/4 - 42*sqrt(2)*p**3/73 - p**2*q**2 - 30*sqrt(2)*p**2*q/73 + p**2 + 84*sqrt(2)*p*q**2/73 + q**4 + 60*sqrt(2)*q**3/73 + q**2` | `t = E/341056` | open | period/ODE data only |

## Release boundary

Models 1, 2, 3, and 9 have exact Hamiltonian and Laurent certificates. The other seven are public catalogue entries with exact period coefficients and stored second-order ODEs, but their Laurent realizations remain open.

Model 2 is OEIS A303790 and is also stored as the named worked example in `../A303790/`. Candidate formulas from the source quarantine directory were not imported as completed examples.

## Replay

```text
python code/run_examples.py public
```

The replay writes reports only under `examples/public/`.
