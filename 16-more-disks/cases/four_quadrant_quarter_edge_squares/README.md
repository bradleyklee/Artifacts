# Four-quadrant square control: edge ratio 1:4

## Geometry

- outer container: axis-aligned square of edge 4, `[-2,2]^2`;
- mover: axis-aligned square of edge 1;
- start centres: `(±1,±1)`;
- velocities: cardinal unit vectors;
- exact arithmetic: Python `Fraction`;
- D4-reduced initial atlas; N=2 and N=3.

A pair corner contact or a simultaneous batch involving one body is recorded as
a terminal degeneracy; it is not assigned an arbitrary collision resolution.

## Generated result at event cap 20,000

- N=2: 16 classes = 9 `RETURN`, 6 `CORNER`, 1 `SIMULTANEOUS`.
- N=3: 32 classes = 8 `RETURN`, 18 `CORNER`, 6 `SIMULTANEOUS`.

There were no `EVENT_CAP` cases. This is a negative control for this exact
finite atlas, not a general theorem about square billiards.
