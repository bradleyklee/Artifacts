# Baseline

This package’s normal `both` display is terminal-oriented and ends with an
OEIS-ready list.  Reproduce it from source with:

```bash
go run ./cmd/a181785 --mode both --max-n 14 --workers 1 \
  | tee output/both_n14_w1.txt
```

The expected checked prefix is:

```text
1,1,2,5,10,25,48,107,193,365,621,1082,1715,2777
```

Do not treat timing as portable: it depends on CPU model, worker count, and
memory behavior.
