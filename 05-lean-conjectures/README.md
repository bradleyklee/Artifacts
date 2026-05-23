# Lean gap-dominance proof notes

This folder checks a small Lean proof of the structural part of the Catalan reciprocal interval-sum argument.

## How to check

Run from the Lake project root:

```bash
lake env lean src/expConj.lean
```

If Lean prints nothing, the file checked successfully.

Do not use plain `lean src/expConj.lean` for files importing `Mathlib`; plain Lean does not know the project dependency paths.

## Where Mathlib went

Lean itself is installed by `elan`, typically under:

```text
~/.elan/toolchains/
```

Mathlib and build artifacts belong to the local Lake project, typically under:

```text
.lake/
.lake/packages/
.lake/build/
```

So the Mathlib download is expected to live in this project directory’s `.lake` folder, not globally in the Lean toolchain. To inspect size:

```bash
du -sh .lake ~/.elan 2>/dev/null
```

## What is being compared

The checked file `src/expConj.lean` proves the abstract structural theorem:

> If a positive sequence has strong enough tail domination, then its finite interval sums are injective.

It does **not** prove the Catalan growth estimates. Those are packaged as hypotheses.

The DeepMind OEIS 108 proof proves the concrete Catalan statement. To compare fairly, we split its proof into:

```text
x = comparable structural/Catalan interval-sum proof
y = extra wrapper for the OEIS fractional-part target and the (1,1) case
```

For the uploaded DeepMind file, the agreed greedy ranges are:

```text
x = lines 124–272
y = lines 274–328
```

So:

```text
DeepMind relevant proof = x + y
                         = 149 + 55
                         = 204 raw lines
```

## Complexity comparison

Raw line count is useful, but it is not the best complexity measure. A better quick measure is:

- nonblank, noncomment lines;
- token count after stripping comments;
- declaration count.

| Proof slice | Raw lines | Nonblank noncomment lines | Token count | Declarations |
|---|---:|---:|---:|---:|
| DeepMind x, comparable | 149 | 130 | 2527 | 18 |
| DeepMind y, extra wrapper | 55 | 49 | 544 | 1 |
| DeepMind x+y, relevant proof | 204 | 179 | 3071 | 19 |
| `src/expConj.lean` | 141 | 80 | 704 | 4 |

By raw lines, the abstract gap-dominance proof is shorter than the DeepMind relevant proof:

```text
141 vs 204 raw lines
```

By stripped token count, the difference is larger:

```text
704 vs 3071 tokens
```

So the abstract proof is about 23% of the DeepMind relevant proof by this token metric.

## Caveat

The gap-dominance file is cleaner because it abstracts away the Catalan arithmetic. DeepMind’s comparable block includes concrete Catalan tail-bound machinery. So the right conclusion is not “ours proves more”; it is:

> The structural proof can be made much smaller and clearer once the Catalan growth/tail facts are isolated as hypotheses.

## Proof comparison

| Proof | Main idea | Human readability | Lean usefulness |
|---|---|---:|---:|
| DeepMind concrete proof | Proves Catalan-specific arithmetic plus final theorem directly | Medium-low | High in its environment |
| Gap-dominance proof in `src/expConj.lean` | Assumes strong tail domination and proves interval-sum injectivity by cases | High | High as reusable structure |
| Human four-endpoint proof | Uses `a < b <= c < d` and compares possible gaps | Highest | Needs formal hypotheses |


