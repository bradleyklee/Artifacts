# Laurent-period certificate tool

This package computes exact differential operators and G,U,V,J certificates
for periods of bivariate Laurent polynomials:

```text
A_n = [F(x,y)^n]_0.
```

The coefficient field may be Q or Q(i). Results are written as JSON, and
terminal output is wrapped to 80 columns.

## Install

Run these commands from the repository root:

```text
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Python 3.11 or newer is recommended. Python 3.10 is also supported by the
requirements file.

## Run the checks

There are two kinds of check:

- A **replay** verifies the exact records already stored in the repository.
- A **full recomputation** first replays the stored records and then derives
  the canonical G,U,V,J certificates again.

Start with the replay commands. They are the quickest way to check that the
package and stored data are working.

### Check all public records

```text
python3 code/run_examples.py public
```

### Check all private records

```text
python3 code/run_examples.py private \
  --data-root examples/private/platonic
```

The private command requires the private data directory. That directory is
excluded from the public release.

### Fully recompute all public cases

```text
python3 code/run_examples.py public --derive-guvj
```

Public recomputation results are written below:

```text
results/public/canonical/
```

### Fully recompute all private cases

```text
python3 code/run_examples.py private \
  --data-root examples/private/platonic \
  --derive-guvj
```

Private reports and recomputed references remain below the selected private
data root.

### Check public and private records together

Replay both datasets:

```text
python3 code/run_examples.py all \
  --data-root examples/private/platonic
```

Replay and fully recompute both datasets:

```text
python3 code/run_examples.py all \
  --data-root examples/private/platonic \
  --derive-guvj
```

A command succeeds only if it exits normally. Any failed exact identity,
recurrence check, missing record, or unfinished derivation is reported in the
terminal output.

## List and inspect examples

List the available examples:

```text
python3 code/example.py list
```

Show one stored example without recomputing it:

```text
python3 code/example.py show A295870
```

The complete public walkthrough is in `WALKTHROUGH_PUBLIC.md`. The private
walkthrough is in `examples/private/WALKTHROUGH_PRIVATE.md`.

## Recompute one named public certificate

A295870:

```text
python3 code/example.py certify A295870 \
  --output results/public/A295870.json
```

A303790:

```text
python3 code/example.py certify A303790 \
  --output results/public/A303790.json
```

These commands derive the operator, construct the G,U,V,J certificate, replay
the exact identity, and check the recurrence.

## Enter a new Laurent polynomial

Supply an exact bivariate Laurent polynomial with integer, rational, or
Gaussian-rational coefficients:

```text
python3 code/example.py derive \
  --F "x + y + 1/(x*y) + y^2" \
  --output results/public/my_example.json
```

Use `--model` instead of `--F` to select a stored model:

```text
python3 code/example.py derive \
  --model private:O3 \
  --output results/private/O3.json
```

The optional arguments `--max-order`, `--max-shift`, and `--max-dilation` are
resource limits. Reaching one of these limits means that the search did not
finish within the selected bounds. It does not prove that no certificate
exists.

## Output records

A certificate JSON record contains the Laurent polynomial, operator,
constant terms, recurrence, certificate data, statistics, and exact checks.
The main fields are:

```text
F
operator
operator_stats
constant_terms
recurrence
certificate
checks
```

The reader-facing terminal output displays the operator as `A_theta`, where

```text
theta = t*d/dt.
```

It is sorted and factored for comparison with a paper. The stored symbolic
expression is not changed by this display formatting.

## Public and private data

Canonical public data are stored below:

```text
examples/public/
```

Canonical private data are stored below:

```text
examples/private/
```

Do not copy private records into public reports or archives. The repository
`.gitignore` excludes `examples/private/`.

## Known bounded failure

The public perturbation

```text
F(x,y) = x + y + 1/(x*y) + y/x^2
```

has a stored `resource_timeout` result in:

```text
examples/public/PERTURBATIONS_CERTIFIED.json
```

The operator search found an order-four operator, but certificate
reconstruction did not finish within the selected resource limit. This is a
bounded computational failure, not a proof of mathematical nonexistence.

## Build a public-only archive

```text
python3 code/build_public_release.py Laurent_period_public.zip
```

The release builder excludes private data, caches, recovery notes, and
generated archives.
