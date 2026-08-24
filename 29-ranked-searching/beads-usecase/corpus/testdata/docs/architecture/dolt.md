---
title: Dolt Backend for Beads
description: Architecture and operational notes for the Dolt-backed issue database
---
Beads stores issue data in Dolt, providing versioned SQL state independent of normal Git source branches. Operational details depend on embedded, server, or proxied-server mode. Use Beads commands rather than improvising against internal database files. See [Sync Concepts](/core-concepts/sync-concepts), [Sync Setup](/getting-started/sync-setup), and [Troubleshooting](/reference/troubleshooting).
