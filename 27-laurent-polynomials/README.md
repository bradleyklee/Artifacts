# Laurent-period certificate tool

This package computes exact differential operators and G,U,V,J certificates
for bivariate Laurent-polynomial periods

```text
A_n = [F(x,y)^n]_0.
```

The supported input coefficient fields are Q and Q(i).  Rational inputs use the
ordinary exact path.  Gaussian-rational inputs are detected before row
reduction and sent through a modular sampled solver with an exact final replay.
The rare Q(i) case therefore does not slow down the rational majority.

All progress messages are wrapped to 80 columns.  Machine-readable results are
written as JSON.

## Install

Python 3.11 or newer is recommended.

```text
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Start here

List the available public and private examples:

```text
python code/example.py list
```

Recompute the two primary public certificates:

```text
python code/example.py certify A295870
python code/example.py certify A303790
```

The default output files are:

```text
certificate-A295870.json
certificate-A303790.json
```

A complete public walkthrough is in `WALKTHROUGH_PUBLIC.md`.  The private
walkthrough is in `examples/private/WALKTHROUGH_PRIVATE.md` and is excluded from
the public release.

## Primary public use case: A295870

The Laurent polynomial is

```text
F(x,y) = ((1+x)^3/x)*((1+y+y^2+y^3)^2/y^3).
```

Recompute its certificate:

```text
python code/example.py certify A295870 \
  --output results/public/A295870.json
```

The command derives the operator from exact constant terms, constructs the
G,U,V,J certificate, replays the divergence identity exactly, and checks the
resulting recurrence.  The stored reference is

```text
examples/public/A295870/certificates/reference_guvj_certificate.json
```

## Primary public use case: A303790

The Laurent polynomial is

```text
F(w,y) =
  ((1+w)^3*(1+y)^2*(y^2-4*y+1)^2)/(w^2*y^3).
```

Recompute its general G,U,V,J certificate:

```text
python code/example.py certify A303790 \
  --output results/public/A303790.json
```

The stored general certificate is

```text
examples/public/A303790/certificates/reference_guvj_certificate.json
```

The same directory also retains the shorter A303790-specific scalar and
Laurent certificate replays used by the paper.

## Enter a new example

Use an exact bivariate Laurent polynomial.  Integers, rational numbers, and
Gaussian rationals are accepted.

```text
python code/example.py derive \
  --F "x + y + 1/(x*y) + y^2" \
  --output results/public/my_example.json
```

Use `--model` instead of `--F` to select a stored example:

```text
python code/example.py derive \
  --model private:O3 \
  --output results/private/O3.json
```

The optional controls `--max-order`, `--max-shift`, and `--max-dilation` are
resource limits.  Exhausting a limit is reported as an unfinished search, not
as proof that a certificate does not exist.

## Canonical data and privacy boundary

The canonical examples are exactly those stored below:

```text
examples/public/
examples/private/
```

The global README reports public work.  The separate private README reports
private work.  `.gitignore` excludes `examples/private/` so a normal public
commit cannot include private records.

Current public status:

```text
11/11 stored catalogue records replay exactly
4/4 catalogue Laurent models recompute and certify
A295870 recomputes and certifies as a named public example
```

Public catalogue replay:

```text
python code/example.py baseline public
```

Private replay:

```text
python code/example.py baseline private
```

Full private re-solve:

```text
python code/run_examples.py private \
  --data-root examples/private/platonic \
  --derive-guvj
```

## Output record

Each certificate JSON file contains:

```text
F
operator
operator_stats
constant_terms
recurrence
certificate
checks
```

A successful result requires exact G,U,V,J replay, exact divergence replay,
and exact recurrence replay.  A guessed operator without these checks is not a
completed certificate.

## Known unresolved perturbation

The controlled perturbation

```text
F(x,y) = x + y + 1/(x*y) + y/x^2
```

is the one public failure retained in the package.  The exact constant-term
search found an order-four operator, but certificate reconstruction did not
finish inside the 60-second per-case resource limit.  The record is marked
`resource_timeout` in

```text
examples/public/PERTURBATIONS_CERTIFIED.json
```

This is not a mathematical nonexistence result.  It is a bounded computational
failure in rational reconstruction after operator discovery.  It is kept near
the end of the public report so users can reproduce the limitation without
confusing it with the canonical suite.

## Build a public-only archive

```text
python code/build_public_release.py Laurent_period_public.zip
```

The builder excludes `examples/private/`, caches, recovery notes, and generated
archives.
