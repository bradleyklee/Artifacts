---
title: bd ready
description: Show ready work with no active blockers
---
`bd ready` uses blocker-aware semantics to find truly claimable work. It excludes in-progress, blocked, deferred, and hooked issues. `--explain` gives dependency-aware reasons; `--claim` atomically claims the first matching ready issue; `--mol` restricts to one molecule. See [Dependencies](/core-concepts/dependencies) and [Molecules](/workflows/molecules).
