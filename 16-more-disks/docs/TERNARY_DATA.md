# Dodecagon ternary data

The dodecagon ternary convention applies only to ordinary pair-face contacts:
the recorded face label is reduced modulo 3. Wall collisions contribute no
symbol. The prescribed centered face contact at physical time zero is included
as pair-contact index zero.

| record | source | pair-face symbols | encoding |
|---|---|---:|---|
| forward checked full prefix | cap-2000 full certificate | 418 | `centered_dodecagon_f1_EN_cap2000.csv/.txt` |
| forward checked compact prefix | cap-7500 compact checkpoint | 1,578 | `centered_dodecagon_f1_EN_cap7500.csv/.txt` |
| negative-time stem | 3-batch full reverse certificate | `1` only | `centered_dodecagon_f1_EN_reverse_stem.csv/.txt` |

The negative-time stem begins at the same central face-1 geometry. From the
resolved time-zero state with all velocities negated, it encounters two wall
contacts and a pair corner. The source contact emits `1`; the walls and terminal
corner do not emit regular ternary digits. This is why the forward complexity
ray is one-sided under the current strict-contact convention.
