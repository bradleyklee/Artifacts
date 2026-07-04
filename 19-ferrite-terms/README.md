# Artifact 19 — McLarnan ferrite terms

Artifact 19 extends McLarnan's barium-ferrite enumerations for OEIS
A011961-A011964.  The four fixed-parameter reference implementations print
terms from `n = 1` onward, using the paper's composition, dihedral-symmetry,
registry, and exact-period rules.  An independently developed Claude
implementation agreed exactly on all 160 newly compared terms for
`n = 21,...,60`.

## Run

```sh
python3 reference/a011961.py
python3 reference/a011962.py
python3 reference/a011963.py
python3 reference/a011964.py
python3 reference/all.py
make check
```

Each OEIS-facing file fixes one parameter:

```text
reference/a011961.py   M = 4
reference/a011962.py   M = 6
reference/a011963.py   M = 8
reference/a011964.py   M = 10
```

`reference/all.py` prints all four fixed sequences.  It is retained for the
common use case, but does not replace the separate reference files.

## Layout

```text
reference/    fixed-sequence reference implementations
terms/        outputs through n = 100; matched range n = 21,...,60
validation/   development-only comparison against the Claude submission
FromClaude/   Claude files retained without edits
```

## Source

T. J. McLarnan, "The numbers of polytypes in close-packings and related
structures," Zeitschrift für Kristallographie 155 (1981), 269-291;
barium-ferrite construction and count on pp. 285-288.
