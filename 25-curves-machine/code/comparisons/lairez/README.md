# Pierre Lairez `periods` comparison harness

Research owner: Bradley Klee. Unpublished research; NO POACHING.

This directory bridges the plane-curve period format used in the current
certificate program to the rational-integral input expected by Pierre
Lairez's Magma package [`periods`](https://github.com/lairez/periods).

## Mathematical bridge

Write `E = 2H` and let the energy curve be `E(p,q) = alpha`.  Our period form
is

```text
rho = (2H)_p = 2H_p,   omega = dq/H_p = 2*dq/rho.
```

It is the Poincare residue

```text
omega = Res_{2H=alpha}( 2*dp*dq/(2H-alpha) ).
```

Consequently the adapter sends a case to Lairez's ambient rational integral

```text
f(alpha,p,q) = 2/(E(p,q)-alpha),
```

with `alpha` as the first variable, exactly as required by `Periods(f)`.
No root solving, sheet choice, or elimination of `p` is needed.

## Run

Generate Magma inputs and perform dependency-free format checks:

```text
python3 adapter.py --all --out generated
python3 selftest.py
```

Run the executable SymPy port:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lairez_port.py cases/triangle_square.json --max-order 3
```

The first exact port results and timings are recorded in `PORT_RESULTS.md`.
The expanded same-machine crossover study is in `EXTENDED_BENCHMARKS.md` and
`extended_benchmark_results_2026-08-02.json`.
Certificate transport, validity, and hybrid equivalence results are in
`CERTIFICATE_COMPARISON.md`.

Priority non-harmonic quartic: `cases/elliptic_must_have.json` represents
`alpha=2H_ell=p^2+q^2+(q^3-3p^2q)+(q^2-3p^2)^2/4` exactly.
The symbolic `c1,c2` family, specialization checks, and coefficient-grid
results are summarized in `WIDE_REGIME_RESULTS.md`.

Wide-grid workflow:

```text
.venv/bin/python generate_test_grid.py
.venv/bin/python benchmark_grid.py PAIR_ROOT --group mixed_quartic --engine lairez
.venv/bin/python verify_grid_scaling.py grid_lairez_mixed_quartic.json cases/grid
.venv/bin/python benchmark_free_specializations.py free_coefficients_symbolic_result.json
```

`benchmark_grid.py` is sequential, timeout-aware, and checkpoints JSON after
every case. Use `--resume` to continue an interrupted grid without rerunning
completed cases.

Exact certificate modes:

```text
.venv/bin/python lairez_port.py cases/triangle_square.json --max-order 3 --certificate
.venv/bin/python lairez_port.py cases/square_hexagon.json --max-order 4 --certificate-summary
.venv/bin/python hybrid_primitive_reconstruction.py PAIR_ROOT --family triangle_square
```

The ordinary port command remains operator-only, so certificate overhead never
silently contaminates the baseline timing.
Same-machine benchmark results and workload qualifications are recorded in
`TIMING_REPORT.md` and `benchmark_results_2026-08-02.json`. Future runs can use
`benchmark_showcases.py`; it records timeouts and child-process memory as well
as wall time.

With Magma and Lairez's package available:

```text
magma -b PERIODS_SPEC=/absolute/path/to/periods/src/PF.spec generated/triangle_square.m
magma -b PERIODS_SPEC=/absolute/path/to/periods/src/PF.spec generated/square_hexagon.m
```

The generated scripts try reduction depths `r = 1,2,3,4`, print the resulting
operator, and compare its order with the known showcase operator.  The package
automatically increases `r` when its internal closure test reports
`r_toosmall`.

## Certificate warning

The public `Periods` intrinsic returns an annihilating operator, not the
accumulated exact differential.  Lairez's `RhamKoszul.m` contains a real
certificate-carrying representation (`variant := {"cert"}` and representation
mode `R:c`), but the cofactor is decoded away before `Periods` returns.

Thus the current harness establishes the input equivalence and enables an
operator comparison immediately.  A literal certificate comparison requires
a small instrumentation patch to expose the accumulated cofactor from
`HomReduce`.  `PSEUDOCODE.md` specifies that patch and the correct gauge-aware
comparison.

## Attribution

The Rham--Koszul/extended Griffiths--Dwork reduction, Gauss--Manin construction,
cyclic-equation extraction, and Magma interface referenced here are due to
Pierre Lairez, *Computing periods of rational integrals*, Math. Comp. 85
(2016), 1719--1752.  This harness and its action-period adapter are comparison
work for Bradley Klee's research program.
