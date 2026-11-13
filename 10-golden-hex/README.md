# 10-golden-hex

Reference implementation for the Mountain-and-Valley / Golden-Ratio Hex Tree
substitution system.

This folder carries `Mountain_and_Valley.pdf`, its JSON sidecar, the original
short Python script, and a small Go implementation.  The PDF is the
human-facing source page.  The JSON file mirrors the machine-readable payload
attached to the PDF.

## Files

```text
Mountain_and_Valley.pdf
Mountain_and_Valley.json
golden_hex.py              original compact Python replay
go.mod
cmd/goldenhex/main.go      CLI entry point
goldenhex/*.go             readable Go reference package
Makefile
README.md
```

## Rules

The replay expands the REPHEX/Lindenmayer substitution from the false center.
The address inflation is:

```text
D_i     -> D_i K_i
K_i,H_i -> D_i K_i H_i
a_i     -> D_{i-2} a_i H_i
b_i     -> D_{i-1} b_i H_i
g_i,h_i -> g_i H_i, h_i H_i
```

The retained false center emits the first six branch tiles:

```text
F -> F + B_i@g_i,  i = 0,...,5
```

## Coloring

After inflation, cells have six states:

```text
F  false center
0  first cell of a D dimer
1  second cell of a D dimer
B  branch pass-through
C  branch cap
G  leaf
```

For the binary sequence:

```text
ON  = F, 0, 1, B
OFF = C, G
```

The cap rule is:

```text
axis_cap = (parent is G) or parent.axis_cap
```

So an axis `B` with `axis_cap=1` is counted as `C`, hence OFF.

## Directed replay sequence

The directed replay gives cumulative ON-cell counts `N_t`.  The printed replay
sequence is

```text
a_t = (N_t - 1) / 6
```

The `-1` removes the central false-center cell.  Thus `a_0 = 0`.

```sh
make sequence
make differences
make sequence LEVEL=5
```

The computed level-6 prefix begins:

```text
0, 1, 2, 3, 4, 5, 8, 11, 14, 17, 20, 23, ...
```

## Fast integer count data

The JSON sidecar also records the object-count recurrence for the `D|H`
fixed-point seed:

```text
D' = 2D + H
H' = 9D + 5H
a(n) = 2D(n) + H(n)
```

with scalar recurrence:

```text
a(0)=3, a(1)=20, a(n)=7*a(n-1)-a(n-2)
```

The Go CLI prints this data without building the geometric patch:

```sh
make counts N=40
make table N=10
```

The count sequence begins:

```text
3, 20, 137, 939, 6436, 44113, 302355, 2072372, ...
```

## Tests

```sh
make test
```

The tests check the count rows, the scalar recurrence, and the directed replay
prefix above.

The original Python commands remain available as:

```sh
make python-sequence
make python-differences
```
