# Closed square-hexagon certificate packet

Research owner: Bradley Klee. Unpublished research; NO POACHING.

The principal identity is

```text
A4(omega) = d(V/rho^7),
rho=(2H)_p=2H_p,
omega=dq/H_p=2*dq/rho.
```

This revision adds a deduction of `A4` and `V` from the finite exact quotient,
an exhaustive source-weight theorem, exact exclusion of orders 1-3 in that
reduction, and proof that the pole `rho^7` cannot be lowered.

Start with `CLOSURE_REPORT.md`.

Replay:

```text
python3 exact/verify_merged_certificate.py
python3 exact/derive_deductive_certificate.py
python3 exact/verify_reduced_primitive.py
python3 exact/verify_operator_ladder_400.py
python3 exact/verify_ore_relations.py
```

Final release files:

- `square_hexagon_plane_curve_certificate_2026-08-02.pdf` - three-page human-readable certificate with ten embedded payload attachments;
- `logs/closure_replay.txt` - clean replay transcript for all five verification layers;
- `logs/pdf_attachment_verification.txt` - byte-for-byte attachment round-trip check;
- `manifest.sha256` - checksum manifest for the complete packet.
