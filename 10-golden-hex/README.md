# 10-golden-hex

Minimal working example for the Golden-Ratio Hex Tree sequence.

This folder carries `Mountain_and_Valley.pdf`, its JSON sidecar, and one short
script.  The PDF is the human-facing source page.  The JSON file mirrors the
machine-readable payload attached to the PDF.

## Files

```text
Mountain_and_Valley.pdf
Mountain_and_Valley.json
golden_hex.py
Makefile
README.md
```

## Rules

The script expands the REPHEX/Lindenmayer substitution from the false center.
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

## Counting

The directed replay gives cumulative ON-cell counts `N_t`.
The printed sequence is

```text
a_t = (N_t - 1) / 6
```

The `-1` removes the central false-center cell.  Thus `a_0 = 0`.

## Commands

```sh
make sequence
make differences
```

Both default to level 6.  To use a smaller finite patch:

```sh
make sequence LEVEL=5
```

The computed level-6 prefix begins:

```text
0, 1, 2, 3, 4, 5, 8, 11, 14, 17, 20, 23, ...
```
