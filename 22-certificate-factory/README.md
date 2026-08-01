# 22-certificate-factory — 23-case illustrated release

This revision contains the complete verified calculus for exactly 23 OEIS records:
A120588–A120607, A244594, A244627, and A244856.

## Start here

- `release/ALL_23_CERTIFICATES.pdf` — the final 24-page aggregate, including the cover and all 23 one-page certificates.
- `reports/REVISION_QUALITY_AUDIT.md` — independent exact-arithmetic coverage and release checks.
- `work/OEIS_FIELD_DELTAS_23_CASES.md` — per-record comparison of existing OEIS content and proposed additions.
- `work/OEIS_FIELD_ADDITIONS_23_CASES.txt` — paste-ready OEIS internal-field lines.
- `examples/q3/ReleaseCandidate/A120590_ternatree_human.pdf` — the reviewed verbose q=3 explanatory model.

Each `examples/Axxxxxx/release/` directory contains one concise illustrated
`certificate.tex`, one `certificate.pdf`, and `certificate_payload.json`. Every
individual PDF embeds its payload.
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

Canonical material is organized by A-number under `examples/`. Legacy run objects were
reduced into the standard `data/*.json` records, so no historical run directory is needed
to interpret a final certificate. Superseded names, shot logs, caches, build debris, and
duplicate review material are excluded from the final tree.

The underlying general certificate generator remains available through `generate.py`,
`run.py`, and `check.py`. Its symbolic generation path requires Python 3.10+ and SymPy;
the presentation builders and arithmetic release audit do not require SymPy.
