# Shot 13: OEIS field-delta conversion

## Outcome

Compared the 23 certificate cases with their current OEIS records and generated:

- `work/OEIS_FIELD_DELTAS_23_CASES.md`: per-item comparison and recommended
  additions;
- `work/OEIS_FIELD_ADDITIONS_23_CASES.txt`: additions only, in `%F`, `%C`,
  `%e`, and `%H` internal-field format;
- `reports/oeis_field_delta_audit.json`: machine-readable classification.

## Comparison result

- The 18 primary algebraic cases already contain their defining equations,
  reversion/Lagrange formulas, and polynomial recurrences in the same or an
  equivalent shifted/scaled normalization.
- A120589 and A120591 already contain their power/convolution definitions but
  lack the certificate recurrences.
- A244594, A244627, and A244856 already contain their algebraic/reversion or
  composition definitions but lack the certificate recurrences.
- Contour formulas, scalar linear ODEs, typogeometric interpretations, readable
  brace-word examples, and reduction-certificate descriptions are absent from
  all 23 records.

## Brace-word examples

Examples use only `{`, `}`, `,`, `0`, and `1`. Constructor/color labels are
removed from the displayed word and their contribution is recorded as a
multiplicity. Here `1` is a true leaf and `0` is a false leaf.

## Checks

- 23/23 A-number comparison sections.
- 23/23 paste blocks.
- 146 recommended field-addition lines.
- All recurrence and ODE identities were read from verified canonical payloads.
- All example words pass the five-symbol alphabet assertion.
- Audit JSON parses.

## Blockers

No mathematical blocker. OEIS pages were changing during the comparison day;
the report therefore labels already-present recurrences as equivalent
normalizations rather than claiming byte-for-byte equality.

## Proposed next shot

Editorial pass in submission-sized batches, beginning with A120589, A120591,
A244594, A244627, and A244856 because their recurrences are genuinely absent.
