---
title: Git Worktrees Guide
description: Worktrees share one Beads workspace unless BEADS_DIR overrides discovery
---
Normal Git worktrees in the same repository share the repository's `.beads` workspace. Issue changes live in Dolt and are independent of the current source branch. Cross-clone synchronization still uses `bd dolt pull` and `bd dolt push`. `BEADS_DIR` can point multiple code worktrees at an external Beads workspace. See [Sync Concepts](/core-concepts/sync-concepts) and [Sync Setup](/getting-started/sync-setup).
