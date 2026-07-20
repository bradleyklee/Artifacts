# Layered Verifiable PDF

## Type definition

A Layered Verifiable PDF is a self-contained nonfiction publication with
multiple coordinated representations of its factual content.

It is intended for **relay and gatekeeping** across potentially many human and
LLM actors. A mathematical artifact may pass through authors, editors,
reviewers, proof assistants, publication systems, archives, and downstream
readers. Each actor should be able to inspect the same portable object, recover
its exact factual payload, repeat appropriate checks, and decide whether to
forward, qualify, reject, or accept it without reconstructing the author's
working environment.

1. **Human layer.** Pages contain readable prose, equations, tables, figures,
   citations, and links. This layer must stand on its own as a publication.
2. **Data layer.** One or more embedded machine-readable payloads encode the
   factual content needed for independent checking. JSON is the default
   interchange format.
3. **Formal layer.** The PDF may additionally embed Lean or another formal
   witness. Its presence, scope, toolchain, and theorem inventory must be
   declared. This layer is optional unless the document claims formal proof.

The PDF is the artifact. Sidecar files may document the type or provide
development tools, but a recipient must not need them to discover what the PDF
asserts or to begin checking it.

## Candidate standard

This document is a candidate datatype specification, not an adopted standard.
It records design work toward a possible consensus standard, potentially
through ANSI or a comparable standards process, for communicating mathematical
facts efficiently and reliably. Any eventual standard would require broader
participation, interoperable implementations, precise conformance language,
security and archival review, versioning rules, and an open process for
revision.

The immediate goal is practical: demonstrate that a familiar archival carrier
can support human exposition, exact machine data, optional formal witnesses,
and repeatable gatekeeping without fragmenting the mathematical object across
uncoordinated messages and files.

## Layers and their expectations

### Layer 1 — human-readable surface

The surface is the publication a person receives when the PDF is opened or
printed. It should communicate the result without requiring extraction of an
attachment.

The human layer is expected to:

- state the subject, definitions, notation, domains, and indexing conventions;
- present every central equation and factual figure legibly;
- include enough intermediate explanation that the intended logical route can
  be reconstructed rather than guessed;
- distinguish definitions, proved statements, computational evidence,
  conjectures, examples, and sourced facts;
- state qualifications and exceptional cases where they affect truth;
- identify external sources with durable citations or links;
- remain stable under ordinary PDF viewers and print workflows; and
- preserve mathematical meaning at the level of signs, exponents, indices,
  delimiters, ordering, and figure labels.

The human layer is not expected to contain every intermediate machine
calculation. It is expected to contain every premise and transition needed to
understand what is being claimed and why the supplied evidence is relevant.

### Layer 2 — embedded machine-readable data

The data layer is an exact semantic account of the factual surface and its
checking material. JSON is the initial interchange format, but the datatype
does not require JSON permanently if a future standard defines equivalent
canonical encodings.

The data layer is expected to:

- identify its schema and version;
- encode exact values rather than rounded display approximations when exact
  values exist;
- provide canonical source for every displayed mathematical expression;
- encode factual figures through reproducible structural data, not only image
  descriptions;
- include symbol definitions, domains, index ranges, exceptional cases, and
  ordering conventions;
- include provenance and external identifiers where claims depend on sources;
- expose sufficient intermediate objects for an independent checker to avoid
  trusting opaque conclusions;
- use stable identifiers where several surface objects could otherwise be
  confused;
- declare algorithms, coefficient conventions, and serialization conventions;
  and
- be extractable from the PDF without access to a sidecar service.

The data layer is not a second, hidden publication and should not introduce
undeclared claims that materially change the visible result. If it contains
additional witnesses or intermediate facts, their role and scope must be
discoverable.

### Layer 3 — optional formal witness

The formal layer contains proof-assistant source, proof objects, or another
machine-checkable formalization. It strengthens but does not replace the human
and data layers.

When present, the formal layer is expected to:

- name its language, version, libraries, and trusted computing base;
- compile or check in a pinned and reproducible environment;
- enumerate which discovered surface claims it proves and which it does not;
- define a mapping between formal declarations and data-layer objects;
- avoid unreported axioms, admitted goals, unsafe extensions, or generated
  assumptions;
- include hashes for source and relevant dependencies; and
- report the exact result of compilation or kernel checking.

Absence of a formal layer is permitted. It must not be present merely as an
empty prestige signal, and the artifact must not claim formal verification
outside the witness's actual scope.

### Cross-layer contract

The three layers describe one mathematical object. Conformance therefore
depends on relations between layers, not only on the validity of each layer in
isolation.

- Every factual surface object must have a machine-readable counterpart or an
  explicit reason why it is presentation-only.
- The data-layer expression used to generate or describe a visible equation
  must match the visible equation exactly up to declared typographic rules.
- Counts, orderings, labels, and case distinctions in figures must agree with
  their structural data.
- Any formal declaration associated with a claim must use definitions
  equivalent to those in the human and data layers.
- Changes to one layer require invalidation and repetition of affected gates in
  every dependent layer.
- Verification reports bind to the complete PDF by cryptographic digest; a
  report for one revision does not transfer automatically to another.

### The primary relay boundary

The boundary between the human-readable surface and the hidden
machine-readable layer is the most obvious and generally the most likely point
of systemic failure. It may not contain the deepest mathematics, but it is
where correct mathematics is most easily separated from the object a recipient
actually reads.

Typical failures include:

- a sign, exponent, index, coefficient, or condition rendered incorrectly;
- a figure whose visible ordering differs from its machine ordering;
- a corrected page paired with an old payload, or the reverse;
- a checker validating hidden data while never inspecting the visible claim;
- OCR or vision silently normalizing an unfamiliar symbol incorrectly;
- two equivalent-looking expressions that differ at a boundary case;
- payload substitution, duplicate attachments, or ambiguous attachment names;
  and
- a verification report relayed with a different revision of the PDF.

For this reason, cross-layer agreement is a separate gate rather than a minor
subtask of mathematical verification. A conforming transcription gate should:

1. enumerate factual objects from the surface instead of relying only on a
   predeclared checklist;
2. locate their exact machine-readable counterparts;
3. compare equations at token or syntax-tree level whenever semantic text is
   available;
4. compare factual figures against canonical structural encodings;
5. use high-resolution visual inspection as an independent check of the actual
   rendered ink;
6. reject missing, duplicated, stale, or ambiguous counterparts; and
7. bind its result to the digest of the complete PDF.

The data layer reduces ambiguity and enables exact recomputation, but it cannot
by itself establish that the reader saw the same facts. Conversely, inspection
of the visible layer cannot establish that the hidden witness is correct. Both
directions must be checked.

## Relay roles

Actors may perform more than one role, and no role is assumed to be human-only
or machine-only:

- **Producer:** creates or revises the visible and machine-readable layers.
- **Transcription gate:** checks agreement between visible claims and payload.
- **Mathematical gate:** independently recomputes consequences and proofs.
- **Source gate:** checks citations, provenance, and external consistency.
- **Presentation gate:** checks legibility, accessibility, and rendering.
- **Formal gate:** compiles and audits an optional formal witness.
- **Relay:** forwards the exact artifact together with a signed or hashed report.
- **Consumer:** reads the human layer and may repeat any earlier gate.

Passing one gate does not imply passing another. A report must identify the
exact artifact bytes, checker version, scope, result, and unresolved limits.

## Content expectations

- The visible document is nonfiction. Every displayed datum, equation, figure,
  inference, attribution, and qualification is a checkable claim unless it is
  clearly identified as notation, exposition, or conjecture.
- The data layer supplies exact, unambiguous representations of the visible
  claims. It may also contain intermediate data needed to check them.
- The layers must agree. A correct hidden payload does not excuse a stale or
  misleading visible page, and an attractive visible page does not excuse an
  inconsistent payload.
- Machine-readable data is evidence, not automatically proof. A checker must
  recompute consequences independently instead of merely confirming that two
  copied strings are equal.
- Any omitted domain restriction, indexing convention, exceptional value,
  branch choice, contour condition, or source qualification is a defect if it
  can change the truth of a displayed claim.
- Figures that encode factual cases or counts are subject to the same checking
  requirements as equations.
- External attributions must be precise enough to verify and must distinguish
  sourced facts from independently derived facts.

## Reader and checker expectations

A proof-assistant reader begins with no document-specific checklist. It reads
the pages and payload, treating each newly encountered equation or factual
graphic as a new obligation. For every obligation it should:

1. identify all symbols, domains, indexing conventions, and dependencies;
2. locate the exact corresponding data in the embedded payload;
3. compare the visible and machine-readable representations;
4. fill in omitted algebraic, combinatorial, analytic, or logical steps;
5. recompute the claim independently where practical;
6. test boundary cases and exceptional indices;
7. compare dependent equations across all pages, not only locally;
8. verify figures and enumerations against the same definitions;
9. check cited external claims against their sources; and
10. report pass, failure, ambiguity, or an unimplemented verification method.

The checker must continue until every factual object discovered on every page
and in every payload has a disposition. A fixed document-specific list of
claims is insufficient because it can silently omit a visible assertion.

## Surface accessibility

Exact cross-layer checking requires a semantic route from visible content to
machine data. Suitable routes include tagged PDF mathematics, actual embedded
text, stable claim identifiers, or a deterministic rendering manifest. Vector
outlines alone are visually sharp but are not semantically extractable by an
ordinary PDF parser. If the surface requires vision or OCR, that limitation
must be reported rather than hidden.

## Release expectation

A candidate may be released as verified only when:

- the PDF is readable and self-contained;
- every embedded payload passes integrity checks;
- every discovered factual claim has been checked across layers;
- all mathematical dependencies have been recomputed or formally proved;
- external attributions have been checked;
- limitations and unverified claims are visible; and
- the verification report identifies the exact PDF bytes it checked.
