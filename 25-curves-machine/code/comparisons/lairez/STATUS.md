# Comparison status — 2026-08-02

Research owner: Bradley Klee. Unpublished research; NO POACHING.

## Closed in this pass

1. The data-format bridge is exact and sheet-free:

   ```text
   (rho=(2H)_p=2H_p, omega=dq/H_p) -> f=2/(2H-alpha).
   ```

   Poincare residue gives `Res(f dp dq) = omega`.

2. Machine-readable adapters now cover both showcase examples:

   - triangle-square, known minimal order 2, current primitive denominator
     `rho^3`;
   - square-hexagon, known first exact order 4, current primitive denominator
     `rho^7`.

3. The generated Magma programs exercise Lairez reduction depths 1 through 4,
   print each operator/order, and separately exercise the code's `"cert"`
   representation path.

4. The comparison criterion is now gauge-aware. We will compare primitive Ore
   operators first, then pull back Lairez's primitive and test its difference
   from the Klee primitive in the curve function field.

## Current result on “are the certificates different?”

Not yet decidable from the public return value of `Periods`.

Pierre's code demonstrably carries certificate information internally:

```text
variant contains "cert" -> representation mode R:c
R:c reduction           -> (remainder, accumulated cofactor)
```

But `EDecode` returns only the remainder, and `Periods` ultimately returns only
the differential operator. Therefore running unmodified `Periods` can compare
annihilators but cannot print the Lairez primitive needed for the certificate
comparison.

This is an interface loss, not a mathematical incompatibility.

## Execution state

```text
adapter generation:       PASS
dependency-free selftest: PASS
Magma execution:          BLOCKED (Magma executable unavailable here)
SymPy port operators:     PASS (both showcases, exact normalized matches)
square-hexagon port time: 160.496 s reduction; order 4
primitive comparison:     BLOCKED on ledger/cofactor assembly
```

## Expected outcomes and their meaning

```text
same minimal operator + same pulled-back primitive
    exactly the same certificate in different internal bases

same minimal operator + primitives differing by a constant/gauge
    equivalent certificates

Ore-equivalent nonminimal operators
    same period equation, certificates must be transported before comparison

same operator + genuinely different primitives with identical differential
    distinct representatives of the same exact class

different minimal operators
    conversion/normalization error or genuinely different period subspace
```

## Next implementation shot

Add a new Magma intrinsic `PeriodsCertificate`, without changing Pierre's
existing `Periods`, that propagates the second `R:c` component through
`HomReduce`, `ComputeGM`, and the cyclic relation. Test triangle-square first;
its order-two certificate is small enough to debug. Once its pulled-back
primitive reproduces the known identity, run square-hexagon unchanged.
