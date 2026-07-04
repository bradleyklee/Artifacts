# Artifact 19 — McLarnan ferrite terms

See [`ARTIFACT.md`](ARTIFACT.md) for the short result statement.

## Run

```sh
make terms-21-60
make terms-21-100
make check
```

The submission-facing program is:

```text
reference/mclarnan_1981_ferrite.py
```

It is a compact exact generator for the `M_N Y_S` barium-ferrite counts in
McLarnan (1981), using the source’s weak-composition encoding, `C_Nv` action,
and exact-layer-number correction. It contains no OEIS data and no copied term
table.

Example:

```sh
python3 reference/mclarnan_1981_ferrite.py --n 4 6 8 10 --start-s 21 --end-s 60
```

## Contents

```text
reference/    minimal runnable reference implementation
terms/        generated output; S=21..60 is independently matched
validation/   development-only audit and alternate implementation
FromClaude/   Claude submission, retained separately and unchanged
```

`terms/ferrite_terms_S21_S60.txt` is the exchanged range.  `S=61..100` is
additional output from the reference implementation; it was not part of the
Claude comparison.

## Source

T. J. McLarnan, “The numbers of polytypes in close-packings and related
structures,” *Zeitschrift für Kristallographie* **155** (1981), 269–291;
ferrite construction and count on pp. 285–288.
