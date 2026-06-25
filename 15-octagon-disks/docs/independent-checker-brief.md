# Independent checker brief

Every file in `certificates/` is individually self-contained: it embeds the full exact model, container, initial state, collision rule, stopping rule, and complete pre/post ledger. A checker must use one certificate file only; no source paths, seed files, or producer execution are permitted.

For every ledger row independently: parse exact rationals and Q(sqrt(2)); confirm continuity; enumerate every candidate wall and pair event; select the global earliest positive time; require strict positive edge overlap for pairs; reject vertex-only contacts; compare the full simultaneous batch exactly; calculate the elastic vector update; compare the full post-state; and check energy, pair-only momentum, and fixed-wall impulse balance. Finally check the complexity-cutoff witness from the terminal valid state.

`source/check_certificate.py` performs this process on one certificate. It is a reference implementation, not an authority; an outside checker can reimplement the embedded model directly.
