---
title: Database Corruption
description: Recover from Dolt database corruption
---
For persistent lock errors, missing issues, or inconsistent database state, inspect with `bd doctor` and the Dolt health commands. Stop the server before filesystem-level recovery, preserve a backup, preview repairs, then use the supported recovery path and verify with `bd doctor` and `bd list`. Do not casually delete Dolt internal files. See [Doctor](/cli-reference/doctor), [Troubleshooting](/reference/troubleshooting), and [Sync Concepts](/core-concepts/sync-concepts).
