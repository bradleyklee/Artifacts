# Artifact 08: Straight-path breaks in the Spectre substitution

## New structure theorem - straight-only baseline

For the Spectre substitution encoded by the included excerpts from Figures 4.2 and 5.1, every valid **straight-only positioned join** in the extracted catalogue breaks under inflation.

The positioned-state convention is \(X_{n,m}\), where \(n\) specifies the directional super-edge and \(m\) is the 1-based ordinary-edge position along that super-edge. Across a glued super-edge of length \(|E|\), the transported coordinate is \(m' = |E| - m + 1\).

From the paper excerpts, the program extracts **76 positioned straight-path records** and evaluates all **288 valid positioned straight joins**. Every inflated join leaves the straight-only catalogue; **25 break immediately at the join between their two parenthesized image words**.

Thus the established result is narrow and reproducible:

> **Breaks are forced in every straight-only positioned Spectre chain currently enumerated.**

This is not a claim that Spectre has no usable axis or no one-dimensional substitution dynamics. A larger catalogue containing bent paths may repair the breaks and remains to be extracted and analyzed.

## Reproducible proof flow

The artifact does not include the full paper TeX. It includes only the source excerpts needed for this computation:

```text
source_excerpt/figure_4_2_edge_tile_macros.tex
source_excerpt/figure_5_1_supertiles.tex
```

The build flow is:

```text
minimal Figure 4.2 / Figure 5.1 TeX excerpts
    -> source-derived edge dictionary and supertile placements
    -> 76 positioned straight-path records
    -> 288-row local join inflation audit
    -> typeset rule-table PDF and five-page audit PDF
```

Requirements: Python 3 and `pdflatex` with the standard AMS/booktabs/tabularx packages.

Run the visible clean rebuild and verification pass:

```bash
make smoke
```

Individual phases are also available through `make data`, `make audit`, `make pdf`, and `make check`. The Makefile prints each extraction, audit, rendering, and checking phase as it runs.

Outputs:

```text
data/figure_4_2_edge_dictionary.csv
data/figure_5_1_supertile_placements.csv
data/figure_5_1_macro_edges.csv
data/straight_path_records.csv
data/straight_local_join_audit.csv
data/straight_local_join_groups.csv
data/straight_local_join_summary.json
docs/spectre_straight_path_rule_tables.pdf
docs/spectre_straight_join_audit_5page.pdf
```

## What is source-derived, and what is computed?

`extract_source_data.py` parses the two source excerpts. The Figure 4.2 excerpt supplies the cyclic signed edge dictionary; the Figure 5.1 excerpt supplies child-tile placements, parent super-edge labels, and boundary vertices. The program derives every straight path between opposing super-edges and emits the 76 positioned records as CSV.

`audit_straight_joins.py` then reads `data/straight_path_records.csv` as its input rule table. It enumerates all valid positioned two-record joins, inflates their parenthesized image words, and tests whether those image words can themselves be re-labelled entirely by straight positioned records. It does not read the TeX source.

`render_rule_tables.py` and `render_audit_pdf.py` read the generated CSV/JSON data and generate the two PDFs.

## Scope and next extension

This artifact is a canonical, reviewable baseline for the **straight-only** system. It deliberately excludes path records that bend inside a supertile. The immediate-break pages in the audit PDF identify the first pathology family for extending the catalogue with bent records.

**Bad news for OEIS:** the straight-line sequence refuses to stay straight.  
**Good news for OEIS:** we might be able to bend some axes into existence.
