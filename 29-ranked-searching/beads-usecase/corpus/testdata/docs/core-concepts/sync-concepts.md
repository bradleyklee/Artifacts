---
title: Sync Concepts
description: Dolt is the source of truth and JSONL is an export, not the sync channel
---
Beads issue data lives in Dolt. Cross-machine sync uses `bd dolt push` and `bd dolt pull`; a new clone uses `bd bootstrap` to obtain `refs/dolt/data`. `.beads/issues.jsonl` is for viewers, interchange, migration, and backup, not routine synchronization. If an older project has no remote, configure one from the machine with authoritative local Dolt state and push it. See [Sync Setup](/getting-started/sync-setup) and [Troubleshooting](/reference/troubleshooting).
