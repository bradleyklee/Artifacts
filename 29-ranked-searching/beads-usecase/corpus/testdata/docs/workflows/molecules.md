---
title: Molecules
description: Epics whose children flow through bd ready as ordered workflow steps
---
A molecule is a work graph, usually an epic whose child steps are connected by dependencies. Children are parallel by default; only explicit dependencies impose sequence. Agents repeatedly query `bd ready --mol`, claim a step, do it, close it, and continue. Formulas can create reusable protos that are poured into molecules. See [Formulas](/workflows/formulas), [Dependencies](/core-concepts/dependencies), and [Ready](/cli-reference/ready).
