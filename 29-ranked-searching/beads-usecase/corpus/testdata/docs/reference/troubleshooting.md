---
title: Troubleshooting
description: Common fixes across installation, Dolt, sync, hooks, dependencies, and platform issues
---
Troubleshooting starts by distinguishing installation, logical consistency, physical database damage, server selection, and synchronization failures. Prefer supported commands such as `bd doctor`, `bd dolt stop/start`, `bd bootstrap`, and backup/restore. Do not remove Dolt internal lock or journal files as an improvised repair. See [Doctor](/cli-reference/doctor), [Database Corruption](/recovery/database-corruption), [Merge Conflicts](/recovery/merge-conflicts), and [Sync Concepts](/core-concepts/sync-concepts).
