# Lean transfer plan

Lean and Lake were not available in the PoC execution environment.

## Goal

Mechanize correctness of the deterministic 1–2 rewrite system, then use the Go
test corpus as the implementation correspondence check.

## Suggested modules

    SkipList/Model.lean
    SkipList/Order.lean
    SkipList/Invariant.lean
    SkipList/Insert.lean
    SkipList/DeleteLocal.lean
    SkipList/DeleteType2.lean
    SkipList/Termination.lean
    SkipList/Tree23.lean
    SkipList/Main.lean

## Core definitions

Define an abstract finite layered structure with:

- ordered bottom vertices;
- horizontal predecessor/successor relation;
- level membership;
- tag in `{1,2,3,4,5}`;
- start/stop boundaries.

Define `Valid` as the conjunction of:

- sortedness;
- reciprocal horizontal linkage;
- tower/promotion consistency;
- horizontal type grammar;
- sentinel consistency;
- finite level bound.

## Primary theorems

    search_correct
    insert_local_preserves_valid
    insert_preserves_valid
    shift_vertical_preserves_valid

    delete_type1_preserves_valid
    delete_type2_top_preserves_valid
    delete_type2_merge_right_preserves_valid
    delete_type2_merge_left_preserves_valid
    delete_type2_recurse_right_preserves_valid
    delete_type2_recurse_left_preserves_valid
    delete_type3_preserves_valid
    delete_type4_preserves_valid
    delete_type5_preserves_valid

    delete_recursion_progress
    delete_terminates
    delete_preserves_valid

## Type-2 priority proof obligation

The code evidence already shows that recurse-right cannot generally preempt
merge-right. The Lean proof should therefore make branch preconditions explicit
rather than treating the `Which` priority as cosmetic.

A useful theorem shape is:

    Valid s ->
    Type2Context s x l ->
    selectedBranch B0 s x l = b ->
    Valid (applyBranch b s x l)

with separate lemmas proving the branch predicate coverage and recursion
progress.

## 2–3 tree correspondence

A second proof layer may define a map `Phi` from valid 1–2 skip lists to 2–3
trees and prove:

    Valid12 s <-> Valid23 (Phi s)

This can make global height and update correctness easier to explain even if the
imperative closure remains locally ugly.

## Transfer corpus

Bring into the software factory:

- the 12-key exhaustive state/transition generator in the Go tests;
- the four-key bad alternative witness;
- closure branch names and counts.

The proof should not silently alter B0. Any repaired or simplified rule becomes
a new candidate and must differential-test against B0 before promotion.
