# Apex 852 Sparse-Search Transfer Document

**Purpose.** This note transfers the sparse-search / GA-prior part of the Apex 852 project so it can be merged with the final page/certificate work. It is not itself a certificate. It is a compact recovery map for the search code, minimized priors, and best-result provenance.

## 0. Current status

The page/certificate handoff is separate. The compact page packet contains the frozen v42 layout proof, renderer inputs, the Apex 852 record, catalogues, and a warning that the 7-patch certificate has not yet been created.

This sparse-search transfer covers a different question:

> How did we search for records like Apex 852, what code/data needs to be recovered, and what needs to be audited before publication?

The present best result to merge into the final product is still:

- **Universe / model:** DH12 C6 local-rule bootstrap
- **Best record:** Apex 852
- **Reported growth invariant:** `a(∞) = 142`, with `N = 6a + 1`, so `N = 853`
- **Claim status:** layout and record candidate exist; final scientific certificate is not yet created
- **Critical open defect:** current 7-patch illustrations must be rebuilt from the exact video renderer before certificate publication

## 1. Files that must be recovered from the sparse-search thread

The next window should recover these from the earlier **Artifact 09 Sparse-Genome Search / Apex-and-chill** and **C6 Autonomous Bootstrap / GA-Prior** threads, or from the local working tree if available.

### Required scripts

- `build_sparse_registry.py`
- `sparse_policy_search.py`
- any local-rule replay/checker module used by `sparse_policy_search.py`
- any DH12 / C6 catalogue loader used by the search
- any script that converts search output into:
  - `apex_852_slowest_depth60.json`
  - accepted/rejected sparse arrays
  - rendered growth records
  - video frames

### Required prior/search data

- `sparse_genomes/`
- `registry.json`
- `priors/dh12_species_prior/representatives.jsonl`
- any minimized parent pool used to seed the DH12 search
- best-child JSON records for Apex 852 and close relatives
- search logs for mutation/mating/anti-mate runs
- seed/config files or command lines, especially around:
  - `--seed 2026060901`
  - `--target-level 5`
  - DH12 priors
  - mutation vs mating counts
  - parent loading

### Required provenance outputs

- the final Apex 852 record:
  - `apex_852_slowest_depth60.json`
- DH12 catalogue files:
  - `rows.csv`
  - `rows.jsonl`
  - `masks.csv`
  - `alphabet.csv`
- rule outputs:
  - accepted entries
  - rejected entries
  - output values
- video/rendering code:
  - `pretty_common.py`
  - `make_video.py`
  - `make_pattern_svg.py`

The compact page packet already contains the final record, small catalogue files, and renderer scripts. It does **not** contain the full search code or minimized prior pool.

## 2. Known sparse-search architecture

### Data model

The search worked with sparse rule data: accepted contexts, rejected contexts, and output values. Candidate children were produced by sparse mutations or by mating / anti-mating parent records.

The important invariant is not “did a picture look right,” but:

1. replay the sparse accepted/rejected rule data;
2. grow from the initial condition;
3. check for conflict or chill;
4. reconstruct the canonical code-space ordering;
5. verify accept/reject entries against the record;
6. render through the exact video renderer only after the data-level replay passes.

### Search modes

Known search modes:

- `mutation`
- `mating`
- `both`
- later `anti-mate` / extrapolation away from parents

Known depth/run styles:

- `shallow`
- `deep`
- `open`
- open-loop flattening / feedback expansion

Known mating logic:

- parent pool is separate from child pool
- keep roughly `2N` best out of `N^2` candidate pairs
- pair distance matters, often Jaccard-like
- directed walk from parent A toward parent B
- anti-mate walks away from both parents

Known mutation logic:

- random walks on accept/reject sparse arrays
- add/drop accept entries
- add/drop reject entries
- rerun after edits
- branch-bound / conflict checks

## 3. Known results and numbers

Earlier sparse-search milestones included:

- baseline replay: **342**
- mutation found: **354**
- common stall: **372**
- mating best stalled: **384**
- mutation best_any: **426**
- later conflict best_any: **468**
- later DH12 Apex result: **852 / 853 cells**, with `a(∞)=142`

One bounded shallow run had approximately:

- mutation trials: `400`
- best_any: `468`
- best_stalled: `372`
- stalled: `151`
- conflicts: `206`
- mating trials: `192`
- mating best_any / best_stalled: `384`

A longer mutation run had approximately:

- `~33,600` trials
- best: `426`
- new_big: `~3,100`
- parents: `~3,530`
- elapsed: `~458s`

These numbers are useful for sanity checking logs, not for publication unless recovered directly from log files.

## 4. Known implementation notes

The earlier scripts likely used conventions like:

```bash
python build_sparse_registry.py \
  --genomes <genome/seed inputs> \
  --out registry.json

python sparse_policy_search.py \
  --mode mutation \
  --universe dh12 \
  --seed 2026060901 \
  --target-level 5 \
  --priors priors/dh12_species_prior/representatives.jsonl
```

Known command-line or Make targets included:

- `search-shallow-parallel`
- `search-shallow`
- serial and two-process search
- progress tags like `[MUTATION]` and `[MATING]`

A suspicious point that must be audited:

> A prior-loading run showed `loaded 0 seed/prior records` while still running `12` mutates and `512` mates.

This must be checked. The final search audit should explicitly answer:

1. Did the prior file load?
2. If not, which runs were effectively unseeded?
3. Did any reported best depend on a run with broken prior loading?
4. Were accepted/rejected matrices used to block search spaces prematurely?
5. Was the search complete or partial?

## 5. Sparse-search audit questions

The final product should include a short sanity audit answering these.

### A. Was the search complete?

Expected answer: probably **no**. It was a heuristic sparse search over a large code space. It should be described as a discovery/search procedure, not an exhaustive proof.

### B. Does partial search invalidate the record?

No, not by itself. A partial search can still find a valid finite record. The record must be validated by replay and certificate, not by search completeness.

### C. Could search code errors have blocked better candidates?

Yes. This is why the search audit should separate:

- validity of the found record;
- completeness or optimality of the search;
- reliability of prior-loading / matrix-blocking / mask handling.

### D. What does the final certificate need to prove?

Not that the search was complete. It needs to prove the selected record:

- has the stated initial condition;
- has the stated accepted/rejected/output rules;
- grows to the stated Apex / chill state;
- has canonical code-space size and ordering as claimed;
- has valid matrix entries;
- has displayed 7-patches rendered from the exact video renderer.

## 6. How to merge with the page/certificate packet

Use the compact page handoff as the page/certificate base. Add this search transfer as a separate section or appendix:

- `search_transfer/Apex852_sparse_search_transfer.md`
- recovered search scripts under `search_transfer/code/`
- minimized prior pool under `search_transfer/priors/`
- search audit logs under `search_transfer/audit/`

Do **not** put raw bulky run directories into the final magazine handoff. Use a minimized search-audit bundle under 10 MB.

Recommended final bundle layout:

```text
apex852_final_handoff/
  00_READ_FIRST/
    README_FIRST.txt
    CERTIFICATE_STATUS.txt
  01_PAGE13/
    page13.svg
    page13.pdf
    page13.png
  02_CERTIFICATE/
    neighborhood_certificate.json
    neighborhood_audit_45_of_45.jsonl
    canonical_code_space_certificate.json
  03_RENDERER_AND_DATA/
    apex_852_slowest_depth60.json
    rows.csv
    masks.csv
    pretty_common.py
    make_video.py
  04_SEARCH_AUDIT/
    Apex852_sparse_search_transfer.md
    code/
    priors/
    audit/
  05_CHECKS/
    verify_handoff.py
    SHA256_MANIFEST.json
```

## 7. Minimal search-audit bundle target

Keep the search-audit bundle below **10 MB**. Include:

- only the scripts needed to rerun/replay the sparse search style;
- minimized priors, not huge run directories;
- final/best records and a small number of comparison records;
- compact logs showing:
  - prior loading
  - command lines
  - best-result trajectory
  - replay pass/fail
- a README saying exactly what is and is not proved.

Do not include videos, large image directories, or duplicate full repositories in the search-audit bundle.

## 8. Stop-work warning

Do not present the search audit as a proof of optimality. Do not present the current v42 7-patch panel as valid. Do not claim a certificate exists until it is created and checked.

The correct publication story is:

> A heuristic sparse search found a candidate. A separate deterministic replay/certificate validates the candidate. The search itself is documented for provenance and reproducibility, not for optimality.
