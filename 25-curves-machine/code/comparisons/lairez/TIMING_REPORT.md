# Timing report: current honest comparison

Date: 2026-08-02  
Research owner: Bradley Klee  
Privacy: unpublished research; NO POACHING.

## Outcome

The Klee support-driven solver currently has the best completed
square--hexagon timing in this environment:

```text
full exact square--hexagon derivation
runs:    61.11, 64.74, 60.92 seconds
median:  61.11 seconds
mean:    62.26 seconds
```

The run derives the first relation through orders 1--4, normalizes the
operator, reconstructs the 40-slot/514-term primitive, checks the exact matrix
identity, and compares the basis-free and explicit-quotient answers.

The improved SymPy port uses a Lairez-style cached generic profile and
fraction-free polynomial solves. Its completed from-scratch timings are:

```text
triangle--square: setup 0.082 s, exact reduction 2.503 s
square--hexagon:  setup 0.131 s, exact reduction 160.496 s
```

Both normalized operators are reproduced coefficient-for-coefficient. The
primitive ledgers are retained but not yet assembled into returned primitives.

## Where the port is slow

SymPy computes the bare Gröbner normal form quickly. To retain a certificate,
the prototype then reconstructs

```text
P - remainder = Gp*F_p + Gq*F_q + Gz*F_z
```

using a cached generic rank profile and fraction-free solves over `QQ[alpha]`.
This changes triangle--square from about 84 seconds to 2.503 seconds. On
square--hexagon, the four 131 by 131 solves consume only about 23 seconds; most
of the 108.584-second fourth reduction is SymPy expression assembly and
canonicalization. Pierre's full extended Rham--Koszul and modular machinery is
still not ported, and Magma itself remains unmeasured.

## Same-machine environment

```text
CPU:      Intel Xeon Platinum 8370C @ 2.80 GHz
cores:    9 visible, one thread per core
RAM:      15 GiB visible
swap:     none
Python:   3.12.13
SymPy:    1.14.0
NumPy:    absent from benchmark environment
SciPy:    absent from benchmark environment
```

The exact symbolic workers are single-threaded. The square--hexagon replay
uses fresh subprocesses for the order computations.

## Workloads must stay separated

| Engine/case | Workload | Median/result |
|---|---|---:|
| Klee square--hexagon | full derivation + primitive + comparisons | 61.11 s |
| Klee triangle--square | lean from-scratch fixed-support derivation + primitive verification | 9.972 s median |
| profiled Lairez-style port triangle--square | from-scratch operator + witness ledger | 2.503 s reduction, one run |
| profiled Lairez-style port square--hexagon | from-scratch operator + witness ledger | 160.496 s reduction, one run |
| full Lairez Rham--Koszul/modular port | not yet implemented | no timing claim |
| original Magma code | unavailable here | no timing claim |

The retired 39.94-second triangle number measured verbose stored-certificate
trace generation. The new lean kernel supplies a valid from-scratch comparison:
9.972-second median at fixed order/support, or 23.237 seconds for a bounded
order-first search, versus 2.572 seconds for the port. See
`EXTENDED_BENCHMARKS.md` for square-only, hexagon-only, and mixed sextic rows.

## Required target benchmark

The faithful port must expose the following timers independently:

```text
homogenize
Jacobian Groebner/module profile
syzygy profile
each reduced alpha derivative
Gauss-Manin closure
cyclic nullspace
rational/modular reconstruction
primitive assembly
identity verification
total cold run
total warm-profile run
peak resident memory
```

For each showcase, run at least one cold process and three warm-profile
processes. A method ranks as faster only if it returns the same normalized
minimal operator and a verified exact primitive.

## Current conclusion

The Klee method is presently complete and about 2.63 times faster on
square--hexagon than this exact profiled port (160.496/61.11), while also
returning the assembled primitive. This does not establish that it is faster
than Pierre's original Magma implementation. A certificate-equivalent ranking
still requires primitive assembly and an original-Magma or full-port run.
