---
title: Dependencies and Gates
description: Ordering work with blocking and non-blocking dependencies
---
Use `bd dep add dependent blocker` when one issue needs another. `blocks`, `parent-child`, `conditional-blocks`, and `waits-for` can affect readiness; `related`, `tracks`, `discovered-from`, `caused-by`, `validates`, and `supersedes` are graph annotations. `bd ready` shows issues with no open blocking dependencies; `bd blocked` explains blocked work. Use `bd dep cycles` to detect cycles and `bd dep remove dependent blocker` to remove an edge. See [Ready](/cli-reference/ready), [Circular Dependencies](/recovery/circular-dependencies), and [Graph Links](/core-concepts/graph-links).
