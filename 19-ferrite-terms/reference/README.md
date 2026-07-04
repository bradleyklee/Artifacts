# Reference implementations

Each `a*.py` fixes its OEIS sequence parameter and prints terms from `n = 1`
through `n = 100`.  There is no run-time parameter selecting the sequence.

```text
A011961  a011961.py  M = 4
A011962  a011962.py  M = 6
A011963  a011963.py  M = 8
A011964  a011964.py  M = 10
```

`all.py` prints the same four fixed sequences together.  It is retained as a
convenient common generator, not as the OEIS-facing per-sequence reference.

The only adjustable bound is the literal `MAX_N` near the top of each file.
