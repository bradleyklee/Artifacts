# 09-Apex-and-chill minimal merge v1

This is a minimal, auditable merge of the current Apex 852 publication packet
and the DH12 seed/search data packet.

The publication PDF is intentionally present at the package root:

```text
apex_and_chill_page13_v88_bottom_spacing.pdf
```

## What is included

- `apex_and_chill_page13_v88_bottom_spacing.pdf`: root publication PDF.
- `data/v88_pdf_packet/`: organized copy of the final v88 PDF/SVG/certificate packet.
- `data/dh12_seed_data/`: uploaded 600+/800+ DH12 seed records and hints.
- `data/search_transfer_doc/`: transfer note for the older search effort. This
  note is included for provenance, but it is not runnable code and says no search
  code/certificate is included.
- `code/visible_svg_scrape_rederive_svgonly_v88_plus.py`: no-dependency
  visible/vector reconstruction checker. It derives the rule payload from
  visible SVG shapes and visible text rather than from embedded JSON.
- `code/visible_pdf_scrape_rederive_pdfonly_v88_plus.py`: older optional
  PDF-object scraper kept for archaeology; it is not used by default targets.
- `code/make_compatible_certificate_from_visible_payload.py`: normalizes the
  PDF-derived payload into verifier-compatible certificate JSON and computes its
  own growth-count sequence.
- `code/verify_reduced_certificate_from_payload_v88.py`: independent replay
  verifier for reduced certificate JSON.
- `code/search_dh12_policy.py`: release-facing bounded search around the uploaded
  seed records using the prior operator framework: `MUTATE`, `MATE`,
  `ADOPT_UP`, `ADOPT_DOWN`, and `ADOPT_EQUAL`. It writes progress logs and
  candidate JSON files.
- `code/validate_seed_records.py`: replay validator for the uploaded seed data.
- `audit/`: prior audit outputs copied into the merge for comparison.
- `source_packets/`: original uploaded zips for provenance.


## Requirements

The default public targets use only the Python standard library.
No `pip install`, local venv, PyMuPDF, or `python3-venv` package is needed.

Check dependencies:

```bash
make doctor
```

Setup is intentionally a no-op:

```bash
make setup
```

Then run:

```bash
make test
```

The proof path reads the visible SVG vector art source and verifies the
root PDF by a shallow stdlib structure check.  The older PyMuPDF PDF-object
scraper remains in `code/` only as optional archaeology.

## Main targets

There are two intended public commands:

```bash
make test
```

and

```bash
make search
```

### `make test`

This is the thorough certificate check. It does all of the following:

1. Checks the root PDF structure: one page, no image XObjects, and at least one
   URI link.
2. Opens the visible SVG art source and reconstructs JSON from vector
   shapes/text: main pattern, P7 thumbnails, matrix statuses, and visible
   accept list.
3. Replays the PDF-derived rules directly and checks that they close at 852 cells
   with zero terminal births and zero unknown frontier.
4. Converts the PDF-derived JSON into a verifier-compatible certificate JSON.
5. Runs the independent certificate verifier on that PDF-derived certificate, so
   the JSON reconstructed from the PDF is double-checked by a second replay path.
6. Runs the same verifier on the official reduced certificate.

Seed-record validation remains available as `make test-seeds`, but the public
`make test` target is focused on the PDF/certificate proof.

Expected key facts:

```text
SVG-derived unique contexts: 536
SVG-derived accept rules:    48
SVG-derived reject rules:    41
SVG-derived final cells:     852
terminal births:             0
terminal unknown frontier:   0
```

### `make search`

This launches the same style of sparse search used in the earlier Apex work, not
the weak one-rule smoke edit. It loads and replays the uploaded seed records,
builds basic prior statistics over the sparse rule universe, and then runs three
operators with explicit progress lines:

```text
MUTATE     = prior/statistics-informed random walk around one parent
MATE       = interior/averaging walk on the axis between parents A and B
ADOPT_UP   = exterior walk beyond the higher-lifetime parent on the same axis
ADOPT_DOWN = exterior walk beyond the lower-lifetime parent on the same axis
ADOPT_EQUAL= equal-lifetime exterior walk, choosing either side explicitly
```

```bash
make search
```

Default settings are deliberately bounded but nontrivial:

```text
SEARCH_KEEP_MIN=800
SEARCH_MUTATIONS=15
SEARCH_MATES=15
SEARCH_ADOPT_UPS=15
SEARCH_ADOPT_DOWNS=15
SEARCH_ADOPT_EQUALS=6
SEARCH_MAX_FOUND=25
SEARCH_MAX_REPLAY_STEPS=70
SEARCH_MAX_CELLS=1200
```

The replay horizon is above the 852 certificate closure step of 60, but it avoids
wasting the public search target on large still-growing open states. The search
also stores rule hashes and terminal-state hashes so the report can distinguish
new rule records from genuinely new terminal phenotypes.

The search output is written to:

```text
build/search/policy/
```

The important files are:

```text
build/search/policy/search_progress.log
build/search/policy/policy_search_summary.json
build/search/policy/policy_search_trials.jsonl
build/search/policy/candidates/candidate_*.json
```

The current deterministic default run found 14 closed-chill candidate records
>= 800 cells, including 6 at 852 cells, with hits from MUTATE, MATE,
ADOPT_UP, ADOPT_DOWN, and ADOPT_EQUAL. The default is intentionally bounded so
`make search` stays interactive. Larger local runs can be launched by
overriding the knobs, for example:

```bash
make search \
  SEARCH_MUTATIONS=300 \
  SEARCH_MATES=300 \
  SEARCH_ADOPT_UPS=300 \
  SEARCH_ADOPT_DOWNS=300 \
  SEARCH_ADOPT_EQUALS=100 \
  SEARCH_MAX_FOUND=100 \
  SEARCH_MAX_CELLS=1200
```

## Caution

This package supports the finite Apex 852 chill certificate and shows that the
seed packet can generate more same-family closed-chill examples. It does not
claim exhaustive optimality and does not prove an infinite growth theorem.

## v1 bottom-pane patch

The root PDF and the organized copy under `data/v88_pdf_packet/artifact/` include
a minimal bottom-pane fix: the wrapped `a_t` growth-count preview now shows all
4 wrapped lines instead of truncating after 3. The certificate data was not
changed.

## Public targets

`make test` is a from-scratch artifact proof run. It deletes generated proof
outputs, extracts visible/vector data from the SVG art source, reconstructs JSON,
replays to 852-cell chill, builds a verifier-compatible certificate from the
reconstruction, and verifies both that derived certificate and the official
reduced certificate.

`make search` runs the bounded mutate / mate / adopt policy search. It
deletes the previous search output directory, prints method-labelled progress
lines, and writes candidate JSON files plus:

```text
build/search/policy/policy_search_summary.json
```

MATE, ADOPT_UP, ADOPT_DOWN, and ADOPT_EQUAL are all two-parent axis walks.
The parents A and B define the axis. MATE walks inside the segment as an
averaging/interior operator. ADOPT_UP and ADOPT_DOWN are not arbitrary
A-side/B-side labels: they are oriented by the lifetime differential. ADOPT_UP
walks beyond the higher-lifetime parent, ADOPT_DOWN walks beyond the
lower-lifetime parent, and ADOPT_EQUAL is used when the two parents have equal
lifetime and either exterior side must be chosen explicitly. MUTATE is a
one-parent walk informed by prior frequencies/signposts, not a two-parent axis
walk.

`make rules-card` prints the 48 used ACCEPT rules reconstructed from the
PDF-visible payload and writes both `used_accept_rules_card.txt` and
`used_accept_rules_card.md` under `build/generated/visible_pdf/`.


## Search targets

`make search` runs a short same-family search using MUTATE, MATE,
ADOPT_UP, ADOPT_DOWN, and ADOPT_EQUAL.

`make search-long` runs a larger bounded batch.  Its default goal is about
100 new closed-chill candidate rule records at or above `SEARCH_KEEP_MIN`
(default 800).  Output is kept within an 80-column terminal and candidate
JSON files are written under `build/search/policy_long/candidates/`.

The search stores rule hashes, terminal-state hashes, and replay-cache entries.
This avoids rechecking identical rule tables and reports whether a candidate
has a terminal phenotype already present in the seed set.

`make search-long` now enters every operator block, including
`ADOPT_UP`, `ADOPT_DOWN`, and `ADOPT_EQUAL`.  The target count is
`SEARCH_LONG_MIN_FOUND`, but a method may stop only after
`SEARCH_LONG_MIN_OPERATOR_TRIALS` trials, so MATE cannot prevent ADOPT
from running.  The default deterministic long run completed locally with
108 closed-chill candidates: 55 at 852, 22 at 846, and the remainder at
804--840.  All five method blocks ran: MUTATE, MATE, ADOPT_UP, ADOPT_DOWN,
and ADOPT_EQUAL.
