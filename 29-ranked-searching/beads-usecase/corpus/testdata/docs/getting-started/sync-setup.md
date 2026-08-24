---
title: Sync Setup Guide
description: Set up Dolt sync across machines, remotes, and fresh-clone bootstrap
---
Initialize Beads once, verify or add the Dolt remote, and publish with `bd dolt push`. A normal `git clone` does not fetch `refs/dolt/data`; in a fresh clone run `bd bootstrap`. Day to day, use `bd dolt pull` and `bd dolt push`. Commit the Dolt working set before pulling, push before changing machines, and do not treat JSONL as sync. See [Sync Concepts](/core-concepts/sync-concepts), [Worktrees](/reference/worktrees), and [Troubleshooting](/reference/troubleshooting).
