---
title: Merge Conflicts
description: Resolve Dolt merge conflicts
---
When `bd dolt pull` reports conflicts or clones disagree, inspect database health with `bd doctor` and preview repairs with `bd doctor --dry-run`. Back up the local `.beads` state, reconcile with `bd doctor --fix`, verify the issue state, then `bd dolt push`. See [Doctor](/cli-reference/doctor), [Sync Concepts](/core-concepts/sync-concepts), and [Troubleshooting](/reference/troubleshooting).
