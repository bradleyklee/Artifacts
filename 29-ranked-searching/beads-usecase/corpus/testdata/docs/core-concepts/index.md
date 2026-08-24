---
title: How Beads Works
description: Orientation to the dependency-aware issue graph, ready work, workflows, and Dolt sync
---
Every unit of work is a bead in a persistent dependency graph. `bd ready` returns the claimable frontier: open beads with no active blockers. Blocking and non-blocking edge semantics are detailed in [Dependencies](/core-concepts/dependencies), while richer informational relations are in [Graph Links](/core-concepts/graph-links). Repeatable workflows move from [Formulas](/workflows/formulas) to [Molecules](/workflows/molecules). Cross-machine state moves through [Dolt sync](/core-concepts/sync-concepts).
