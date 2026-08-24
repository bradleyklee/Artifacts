---
title: bd doctor
description: Sanity check the Beads installation and data
---
`bd doctor` checks database/schema health, permissions, dependencies, hooks, metadata, and other integrity conditions. `--dry-run` previews repairs; `--fix` applies supported repairs; `--deep` validates graph integrity; `--agent --json` emits rich machine-readable diagnostics for an agent. Use specialized migration and server modes when relevant. See [Troubleshooting](/reference/troubleshooting) and [Database Corruption](/recovery/database-corruption).
