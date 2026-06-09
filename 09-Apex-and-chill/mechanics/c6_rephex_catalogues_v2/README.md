# C6 rephex catalogue extraction v1

Generated directly from `repo(146).zip` / `rephex_print` using F level 4 and level 5 targets.

Models extracted:
- `dh12`: lowest reduced D/H oriented alphabet.
- `ordinary`: ordinary palette semantics: D0, D1, and H, each oriented.
- `tree`: tree palette semantics: D0, D1, PASS, CAP, LEAF, each oriented.
- `split`: split palette semantics: D0, D1, PASS, CAP, TRI, PAR, each oriented; boundary UNKNOWN (`leaf_tag U`) is dropped.

Frozen conventions:
- row tuple: `(center, E, NE, NW, W, SW, SE)`
- C6 quotient only; no reflection
- canonical row: lexicographically least rotation, with orientation suffix decremented by rotation k
- row order: sorted ascending canonical rows
- mask bits 0..5: `E, NE, NW, W, SW, SE`
- `bit = 1` means KEEP / visible; `bit = 0` means dropped / forgotten
- `bit_index = row_id * 64 + keep_mask`

Rule files are prehistory/data-shape files, not search results. `accepted_matrix_entries.csv` means the masked visible input has a unique output within the observed catalogue; `rejected_matrix_entries.csv` means the masked visible input is ambiguous over outputs.


v2 correction
-------------
Raw F targets contain all six CAP orientations equally. Earlier v1 summaries reported alphabets by labels appearing inside canonical row representatives; that is not the model alphabet because C6 canonicalization can rotate labels out of a representative. v2 reports orbit-closed model alphabets. Row ids, row ordering, keep-mask convention, and matrix entry ids are unchanged from v1.
