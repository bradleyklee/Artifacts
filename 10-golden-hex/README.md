# 10-golden-hex

Minimal working example for the Golden-Ratio Hex Tree sequence.

This folder carries the `Mountain and Valley` PDF, its JSON sidecar, and one
short script.  The script expands the REPHEX/Lindenmayer rules, applies the tree
parity coloring, replays the directed growth timing, and prints the sequence.

## Rule data

The PDF contains the machine-readable substitution payload as a standard JSON
attachment.  The file `mountain_valley_substitution_payload_v47.json` is a
plain sidecar copy for easy reading.

The script is deliberately self-contained, so the same rules are also written
directly in `golden_hex.py`.

## Coloring

The expanded patch has these visible states:

```text
F  retained false center
0  first cell of a D dimer
1  second cell of a D dimer
B  branch pass-through
C  branch cap
G  leaf
```

For the binary sequence,

```text
ON  = {F, 0, 1, B}
OFF = {C, G}
```

The cap rule is the extra parity bit:

```text
axis_cap = (parent is G) or parent.axis_cap
```

So a `B` with `axis_cap=1` is rendered/counts as `C`, not as ON.

## Counting

The replay gives cumulative ON-cell counts `N_t`.  We print

```text
a_t = (N_t - 1) / 6
```

The `-1` removes the central false-center cell, so the result is a multiple of
six divided by six.  Thus `a_0 = 0`.

## Commands

```sh
make sequence
make differences
```

Both default to level 6.  Use another level with:

```sh
make sequence LEVEL=5
```
