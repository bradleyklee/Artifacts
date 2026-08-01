# Merger notes

## Recommended placement

1. Put the first seven literal members and the cost rule in the human explainer.
2. State the generating equation and contour integral next.
3. Display the recurrence, but keep the full `P(n,t)` outside the main narrative.
4. Embed `payload/certificate.json`, `payload/pseudocode.md`, and `code/verify_all.py` as the hidden verification layer.
5. Link the complete `data/members_n0_n4.txt` rather than printing all 1614 size-4 members in the visible document.

## Important claim boundaries

- The grammar is a proposed typogeometric interpretation of A244856.
- Once the grammar is accepted, its generating equation and literal counts are exact.
- Unary growth costs one; four-slot junctions cost zero.
- A unary wrapper `{W}` must not be silently rewritten as one of four positional one-active-slot junctions.
- Four-slot closures require at least two nonzero children, not merely “not all zero.”
- The telescoping certificate proves the recurrence for generic `n`, hence for integers `n>=1` where the displayed rational terms are defined.
- The recurrence at `n=0` is a separate exact initial-value check.
- No minimal-order claim is made for the recurrence.
- `formal/A244856_statement.lean` is only a statement scaffold and is not included among the verified outputs.

## Suggested merger acceptance test

Run:

```bash
python code/verify_all.py
```

Reject the merge unless every check passes without numerical approximation.
