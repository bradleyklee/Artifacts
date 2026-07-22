# 22-certificate-factory v0.2 — RELAY

Generate exactly one certificate case per process. Exact validation is enabled by default.

## Fast default

```bash
python3 generate.py 9
```

This derives and emits:

- the algebraic OGF and typogeometric starting points;
- `D_q(u)`, `rho_q(u)`, and the fully defined integrand `H_{q,n}(u)`;
- exact bases and all fast-path matrices `G`, `G_inverse`, `E`, `U`, `V`, `J`, `X_full`, `X`;
- every pole-lowering chain with input, `V`-certificate, and output vectors;
- the primitive P-recurrence and rational recurrence certificate;
- the standard ODE mechanically transformed from the P-recurrence;
- coefficientwise recurrence–ODE compatibility witnesses;
- dimensions, stage timings, environment metadata, peak RSS, and exact dynamic checks.

## Slower dissertation-style ODE audit

```bash
python3 generate.py 5 --derive-ode-direct
```

The switch adds a second Klee-style matrix reduction based on repeated `x`-derivatives of

```text
F_q(x,u) = 1/(rho_q(u)-x),
A_q'(x) = Res F_q(x,u) du.
```

It emits `Gx`, `Gx_inverse`, `Ux`, `Vx`, the derivative-remainder matrix, a direct ODE for `A_q'(x)`, and its rational `u`-derivative certificate. The checker converts that ODE back to a primitive coefficient recurrence and requires exact equality with the fast P-recurrence.

Slow mode is a strict superset: it always includes all fast-path data.

## Commands

```bash
# One q, fast path plus validation
python3 generate.py 9

# One q, both reductions plus validation
python3 generate.py 5 --derive-ode-direct

# Generation assertions only; skip the separate checker
python3 generate.py 9 --skip-validate

# Recheck an emitted blob without regenerating it
python3 check.py runs/q9/case.json

# Generate the included five-case direct-ODE smoke suite
./run_examples_q2_q5.sh

# External time/RSS audit
./time_audit.sh 9 --skip-validate --output audit-runs
```

Each run prints the mathematical stage currently active. Direct mode separately reports parameter-dependent matrix assembly, determinant, inversion, every derivative reduction, ODE kernel solve, certificate assembly, and exact identity check.

Requirements: Python 3.10+ and SymPy.
