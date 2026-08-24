---
title: Formulas
description: Declarative TOML or JSON workflow templates
---
A formula declares repeatable workflow steps, variables, dependencies, gates, and optional aspects. TOML is preferred. `needs` expresses step dependencies. Use `bd cook` to compile a formula into a proto, then `bd mol pour` to instantiate persistent work. Formula files may live at project or user level. See [Molecules](/workflows/molecules) and [Dependencies](/core-concepts/dependencies).
