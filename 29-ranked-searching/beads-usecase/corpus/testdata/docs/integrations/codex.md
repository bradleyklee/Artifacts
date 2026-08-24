---
title: Codex
description: Set up Beads for Codex with skills, AGENTS.md, and compaction-safe hooks
---
Use `bd setup codex` and `bd setup codex --check`. Project setup installs the Beads skill, managed `AGENTS.md` guidance, and native Codex hooks. SessionStart injects `bd prime`; compaction hooks detect context loss and schedule a refresh so the first prompt after compaction receives Beads context again. See [Introduction](/index).
