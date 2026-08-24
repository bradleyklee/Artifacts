---
title: Circular Dependencies
description: Detect and break dependency cycles
---
Symptoms include circular-dependency errors, unexpected blocked work, or ready work disappearing. Inspect with `bd blocked`, `bd show`, and dependency traversal. Identify the least appropriate edge, remove it with `bd dep remove dependent blocker`, then verify with `bd blocked` and `bd ready`. Think in terms of “X needs Y” when adding edges. See [Dependencies](/core-concepts/dependencies) and [Ready](/cli-reference/ready).
