# OEIS entry draft

This draft is for the **D|H fixed-point cell-count sequence** recorded in
`Mountain_and_Valley.json`.  It is **not** the false-center directed replay
sequence whose level-6 prefix begins `0, 1, 2, 3, 4, 5, 8, ...`.

For this count sequence, the linear recurrence is not an empirical guess: it
comes directly from the object substitution matrix for the two object counts
`D(n)` and `H(n)`.

## Form fields

### NAME

Number of hexagonal unit cells in the n-th Mountain-and-Valley inflation of the
D|H fixed-point seed.

### DATA

```text
3, 20, 137, 939, 6436, 44113, 302355, 2072372, 14204249, 97357371, 667297348, 4573724065, 31348771107, 214867673684, 1472724944681, 10094206939083, 69186723628900, 474212858463217, 3250303285613619, 22277910140832116, 152695067700211193, 1046587563760646235
```

### OFFSET

```text
0,1
```

### COMMENTS

Start with the fixed-point seed consisting of one valley dimer `D` and one
mountain hexagon `H`.  If `D(n)` is the number of dimers and `H(n)` is the
number of single hexagons after n inflations, then a dimer contributes two
hexagonal unit cells and a hexagon contributes one, so `a(n)=2*D(n)+H(n)`.

This is the object-count sequence for the D|H fixed-point seed of the
Mountain-and-Valley golden hex substitution system.  It is separate from the
false-center directed replay sequence defined by cumulative ON-cell arrival
times.

### REFERENCES

Bradley Klee, *Zine of Zany Sages*, page 12, "Mountain and Valley", 2026.

### LINKS

```html
Bradley Klee, <a href="https://github.com/bradleyklee/Artifacts/tree/main/10-golden-hex">Mountain-and-Valley / Golden-Ratio Hex Tree reference implementation and data</a>.
```

### FORMULA

Let `D(0)=1`, `H(0)=1`.  The substitution matrix gives

```text
D(n+1) = 2*D(n) + H(n),
H(n+1) = 9*D(n) + 5*H(n),
a(n) = 2*D(n) + H(n).
```

Equivalently,

```text
a(0)=3, a(1)=20, a(n)=7*a(n-1)-a(n-2) for n >= 2.
```

Ordinary generating function:

```text
(3 - x)/(1 - 7*x + x^2)
```

### EXAMPLE

For n=1, the first inflation has `D(1)=3` dimers and `H(1)=14` hexagons, hence
`a(1)=2*3+14=20` hexagonal unit cells.

For n=2, `D(2)=2*3+14=20` and `H(2)=9*3+5*14=97`, hence
`a(2)=2*20+97=137`.

### MAPLE

```text

```

### MATHEMATICA

```text

```

### PROG

```text
(Python)
def A(n):
    d, h = 1, 1
    for _ in range(n):
        d, h = 2*d + h, 9*d + 5*h
    return 2*d + h
print([A(n) for n in range(22)])
```

### CROSSREFS

```text

```

### KEYWORD

```text
nonn,easy
```

### AUTHOR

```text
_Bradley Klee_, Jul 09 2026
```

## Not-yet-submitted separate sequence

The false-center directed replay sequence uses cumulative ON-cell arrival times
`a_t=(N_t-1)/6`.  Its current artifact prefix is:

```text
0, 1, 2, 3, 4, 5, 8, 11, 14, 17, 20, 23, ...
```

Do not use the recurrence above for this replay sequence.
