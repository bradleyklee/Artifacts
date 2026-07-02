# Toolchain Persistence and Transfer Cost

## Observed problem

A working Rust toolchain is reported in another context under a context-local
`/mnt/data/toolchains/...` path. This context cannot see that mount, has no
native Rust executable on `PATH`, and cannot validate the other context's
compiler directly.

The source-and-receipt transfer packet is small. The compiler environment is
not: operationally, seeding Rust into a fresh context has required a payload of
at least roughly 100 MiB. Repeating that transfer during normal experiment
iteration is not a viable development workflow.

## Required distinction

- **Portable scientific artifact:** source, tests, certificates, expected
  transcripts, and hashes. These should remain small and move freely.
- **Toolchain infrastructure:** compiler, standard library, linker/runtime
  components, and configuration. This should be cached, mounted, or
  platform-provided—not re-uploaded as part of every experiment.

## Desired platform contract

For a language that is usable in at least some code-execution contexts, the
platform should state whether the capability is:

1. available by default;
2. available only in specific surfaces, plans, workspaces, or rollout cohorts;
3. unavailable but supported through a documented build runner; or
4. unsupported.

For Rust, the durable solution is a verified reusable toolchain path or build
surface, with a smoke test and provenance, rather than repeated large uploads
into isolated context mounts.
