# 22-certificate-factory — 23-case illustrated release

This revision contains the complete verified calculus for exactly 23 OEIS records:
A120588–A120607, A244594, A244627, and A244856.

## Start here

- `ALL_23_ILLUSTRATED_CERTIFICATES.pdf` — conspicuous root-level copy of the complete current portfolio.
- `release/ALL_23_CERTIFICATES_RHO_INLINE_v10.pdf` — current physical 24-page aggregate; it includes the cover and all 23 one-page certificates.
- `ALL_23_CERTIFICATES_INLINE_MULTIPLICITIES_v7.pdf` and `release/HANNA_23_CALCULUS_CERTIFICATES.pdf` — compatibility links to that current aggregate, retained without duplicate PDF bytes.
- `reports/REVISION_QUALITY_AUDIT.md` — independent exact-arithmetic coverage and release checks.
- `work/OEIS_FIELD_DELTAS_23_CASES.md` — per-record comparison of existing OEIS content and proposed additions.
- `work/OEIS_FIELD_ADDITIONS_23_CASES.txt` — paste-ready OEIS internal-field lines.
- `examples/q3/ReleaseCandidate/A120590_ternatree_human.pdf` — the reviewed verbose q=3 explanatory model.

Each `examples/Axxxxxx/release/` directory contains a concise illustrated `certificate.tex`,
`certificate.pdf`, fresh-named `certificate_WITH_INLINE_MULTIPLICITIES.pdf`/`.tex` copies, and
`certificate_payload.json`. Every individual PDF embeds its payload.
The combined portfolio embeds a SHA-256 index of all constituent certificates and payloads.
The root-level and `release/` aggregate PDFs are byte-identical; the duplicate filename is
intentional so the all-cases deliverable cannot be confused with an earlier individual PDF.
Legible exact `G`, `U`, `V`, and `J` matrices are printed directly; larger matrices remain in
their canonical case records. Every page includes the telescoper identity, its rational
certificate form, a binomial/multinomial coefficient sum where available, and constructor
multiplicities beside the typogeometric codes.

## Rebuild and verify

```bash
python3 src/build_concise_certificates.py
python3 src/build_certificate_portfolio.py
python3 src/quality_check_revision.py
python3 src/generate_oeis_field_deltas.py
```

The release audit independently checks the defining equations (or companion power
convolutions), all stored recurrence instances, every stored published prefix, PDF
integrity, embedded-payload byte identity, and overfull-box-free TeX layout.

## Data organization

Canonical material is organized by A-number under `examples/`. Four exceptional matrix
pilots remain under `runs/` because their wrappers cite them directly. Legacy q-numbered
runs, nested archives, duplicate A120590 review trees, build logs, and the multi-megabyte
generated Markdown dump were staged outside the deliverable; the exact inventory and
hashes are in `reports/PRUNING_LEDGER_2026-07-31.md`.

The underlying general certificate generator remains available through `generate.py`,
`run.py`, and `check.py`. Its symbolic generation path requires Python 3.10+ and SymPy;
the presentation builders and arithmetic release audit do not require SymPy.
