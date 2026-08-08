# Current search and analyze snapshot

## Primary current engine

`q2_order6_engine/` is the broadest current search-and-analysis snapshot. It
contains:

- exact and modular period-series generation;
- order/degree scanning and held-out tests;
- Cartesian cohomology reduction;
- reductive exact-image and nullspace searches;
- CRT reconstruction of differential operators;
- exact primitive recovery by shifted energy recurrence;
- finite squarefree degree bounds;
- a complete dense asymmetric quartic order-6 certificate and regression data.

Its source modules are kept together unchanged so their local imports remain
runnable.

## Specialist analyzers

- `quartic_elliptic_detector/` — detects elliptic quotients of even quartics
  and derives the binary-quartic invariant operator.
- `two_node_genus1_annihilator/` — exact order-2 operator and certificate for
  the general split two-node genus-one quartic family.
- `quartic_addition_decision/` — projective genus decision and direct
  adjoint-conic addition-law analysis on plane quartics.
- `differential_addition_law/` — differential-preservation checks and search
  prototypes for cubic and Edwards-type addition laws.
- `general_cubic_symbolic/` — symbolic universal order-2 Picard–Fuchs
  operator for general cubic fibers, with exact and modular regressions.

## Example-specific specialization

The triangle–rectangle `mu` calculation and modular/hypergeometric pullback
checks live under `../showcase/TriangleRectangle/`, because they are part of
that reproducible certificate rather than the generic engine.
