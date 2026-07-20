# Artifact 21

Artifact 21 is a release-candidate instance of the Layered Verifiable PDF
datatype. The primary object is `Artifact21_Certificate.pdf`.

The PDF contains two human-readable vector pages and an embedded JSON payload.
The payload carries exact mathematical data, canonical MathText/LaTeX for every
displayed equation, and canonical codes for every displayed quadtree
representative. The PDF can therefore be relayed as one object to human or LLM
reviewers.

The principal relay risk is disagreement between visible ink and hidden data.
Mathematical verification of the payload and visual verification of the pages
are separate gates: neither result implies the other.

## Package contents

- `Artifact21_Certificate.pdf` — primary self-contained certificate.
- `TYPE_SPEC.md` — candidate datatype and relay/gatekeeping expectations.
- `manifest.json` — package/type metadata; it does not prescribe the claims a
  reader must discover.
- `payload/certificate.json` — an exposed copy of the PDF's embedded payload for
  convenience and byte comparison.
- `verification/verify_layered_pdf.py` — independent checker that begins with
  the PDF and extracts its payload.
- `verification/report.json` — checker result bound to a PDF SHA-256 digest.
- `source/build_certificate_spread.py` — deterministic publication source.
- `source/interior_prose_page_style.json` — style data used by the builder.
- `requirements.txt` — Python dependencies for the verifier and source.
- `SHA256SUMS` — digests for the primary PDF, payload, checker, and report.
- `FromClaude/` — drop location for review files returned by Claude.

## Verification

From the package root:

```sh
python3 verification/verify_layered_pdf.py \
  Artifact21_Certificate.pdf \
  --output verification/recomputed_report.json
```

The included report records sixteen passing checks and no failures. It verifies
container properties, embedded data, quadtree counts, residue extraction, the
rational telescoping identity over `Q(n,u)`, the P-recurrence, the differential
operator, the algebraic generating equation, the surface-math inventory, and
the quadtree representative manifest.

The remaining ordinary presentation assumption is that the vector math
renderer faithfully drew the embedded MathText source. A human or vision model
can compare the rendered pages with that source as an additional gate.

## Status

The artifact is a checked release candidate. The datatype is experimental and
standards-oriented; it is not an ANSI standard and carries no ANSI endorsement.
