# Infographic source-of-truth sheet — v20

**Use the two diagrams separately.** The six literal raw quine β-states are **not** the six live Scott phases. A combined wheel claiming otherwise is an illustration of a research goal, not v20 code.

## Bare quine, independently proven
`Δ = λx.xx`; `H = λy.Δ`; `G = λx.(xH)x`; `Q = Δ G`.
`ΔG → GG → (GH)G → ((HH)H)G → (ΔH)G → (HH)G → ΔG`: exactly **six** actual β-contractions; six distinct intermediate states. This raw clock is NOT coupled to the live controller.

## Live controller, as coded
Six **Scott-encoded** states. Phases 0,1,3,5 pass the product through; phase **2** runs `STEP(p)`; phase **4** contracts `(λx.x) p` and its identity contraction is an actual redex. The labels LISTEN/PREPARE/VERIFY/REPORT are proposed human descriptions, **not separately implemented operations**. No general verification/failure mechanism.

## Evidence and counts
- 10 complete simulated controller cycles; 10 decoded exports.
- First cycle: **81 dispatcher β-contractions** (13+11+23+11+12+11).
- Subsequent cycles: **79 β each** (11+11+23+11+12+11).
- 10-cycle dispatcher total: **792 = 81 + 9×79**.
- Peak process RSS from recorded run: **96,528 KiB ≈ 94.27 MiB**.
- Wall-clock from archived run: **0.09784 seconds** (specific host/run; not intrinsic λ cost).
- Costs EXCLUDE product readout/Church numeral decoding and their normalization.
- Trace notation `E((a,b)) → (a,b)` is an **observer-decoded annotation of a real identity contraction**; the raw de Bruijn prefix does not contain `E` variable names or numeric tuple literals.
- Raw Q's six β-steps are **not included** in the 792 controller steps.

## Scroll fidelity rule
Use a literal `before_prefix` or `after_prefix` value from `example_trace/beta_history.jsonl` (example in `docs/VERBATIM_TRACE_EXCERPT.txt`), or use a mechanically verified syntax conversion. Do NOT synthesize a plausible lambda expression and label it verbatim.

## What must not be claimed
Not a fully coupled raw-Q-driven controller, not a single continuous infinite λ-term, not a general VERIFY/REPORT/LISTEN implementation, and not an external I/O primitive inside pure λ-calculus.
