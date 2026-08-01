# A244856 typogeometry and creative-telescoping certificate

This package gives a proposed typogeometric realization of OEIS A244856 and an exact certificate chain:

1. a literal grammar over `{`, `}`, `,`, `0`, `1`;
2. direct enumeration of members for small sizes;
3. the algebraic generating-function equation;
4. a Lagrange-inversion contour integral;
5. an order-4 recurrence;
6. a rational creative-telescoping certificate;
7. exact verification scripts.

## Core result

Let `T=A-1`, where OEIS A244856 satisfies

```text
A(x) = (4 + A(x)^4)/(5-x).
```

Then

```text
T = x + x*T + 6*T^2 + 4*T^3 + T^4.
```

The proposed grammar is:

```text
G ::= 0                         empty/closed geometry, cost 0
    | 1                         terminal geometry, cost 1
    | {G}                       unary growth, G != 0, extra cost 1
    | {G1,G2,G3,G4}             ordered four-slot junction, cost 0
```

For a four-slot junction, at least two entries must be nonzero. Thus all-zero and one-active-slot four-tuples are forbidden. This distinction is essential: unary *growth* costs one unit, while binary/ternary/quaternary junctions are free.

## Verification

From the package root, run:

```bash
python code/verify_all.py
```

Expected final line:

```text
ALL CHECKS PASSED
```

The symbolic checker requires SymPy. The literal enumerator uses only the Python standard library.

## Package map

- `docs/HUMAN_EXPLAINER.md` — short explanation for a human-facing certificate.
- `docs/DERIVATION.md` — generating function, contour integral, and recurrence derivation.
- `docs/MERGER_NOTES.md` — claim boundaries and suggested integration order.
- `payload/certificate.json` — machine-readable recurrence and telescoping certificate.
- `payload/pseudocode.md` — implementation-neutral checks.
- `code/verify_all.py` — exact symbolic and enumerative verification.
- `code/enumerate_members.py` — literal member generator.
- `data/members_n0_n4.txt` — every member through size 4.
- `data/oeis_initial_terms.json` — terms currently displayed by OEIS.
- `data/derived_terms_n0_n50.txt` — terms extended by the certified recurrence.
- `formal/A244856_statement.lean` — theorem-statement scaffold only; not a compiled Lean proof.

## Source

OEIS A244856: https://oeis.org/A244856

Source definition and displayed initial terms were checked on 2026-07-30.
