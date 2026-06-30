# Dataset status

All figures below are executed Go outputs and independently replayed in Python.
Finite caps are stated as caps; no record is labelled chaotic.

| Family | Raw starts | Horizon | Result |
|---|---:|---:|---|
| square `L=2,N=4` | 256 | 256 | 32 return; 168 pair corner; 32 wall corner; 24 coupled; **0 cap** |
| dodecagon `L=2,N=2` cardinal lattice | 96 | 100 | 64 return; 24 pair corner; 8 wall corner; **0 cap** |
| dodecagon `L=3,N=2` cardinal lattice | 576 | 100 | 424 return; 136 pair corner; 16 wall corner; **0 cap** |
| centered dodecagon, all faces | 68 | 500 | 20 return; 32 pair corner; 16 cap |
| centered dodecagon, off-cardinal faces | 48 | 500 | 16 return; 16 pair corner; 16 cap |
| 24-gon `L=2,N=2` cardinal lattice | 96 | 100 | 72 return; 8 wall corner; 16 cap = **two D4 classes** |
| octagon `L=2,N=3` cardinal lattice | 256 | 256 | 80 return; 88 pair corner; 56 wall corner; 16 coupled; 16 cap = two D4 classes |

The selected centered dodecagon representative is face `1`, incoming `(E,N)`.
Its cap-500 and cap-2000 full certificates pass independent Python replay. Its
cap-4000, cap-6000, and cap-7500 compact checkpoints also pass independent Python replay.

The selected 24-gon representatives are sites `[0,1]` with velocities `(E,S)`
and `(W,N)`. They are each independently checked to 100 batches; direct
velocity negation at the same sites swaps the two D4 classes.

The corresponding negative-time continuation is also stored as a full independent
certificate. Starting from the resolved central contact with velocities negated,
it hits the south wall, then the west wall, then reaches a `PAIR_CORNER` after
three batches. Its only regular face trit is the source contact trit `1`; see
`data/dodecagon_centered/ternary/centered_dodecagon_f1_EN_reverse_stem.*`.
