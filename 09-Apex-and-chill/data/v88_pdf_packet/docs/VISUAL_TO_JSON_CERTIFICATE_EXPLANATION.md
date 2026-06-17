# Visual data → JSON certificate → replay closure

This reduced packet is deliberately small. It does not include the broad search/prior history. It contains the final v88 artifact, the explicit JSON certificate, and the code needed to replay/check that certificate.

## What the visual page contains

The PDF/SVG page is the human audit surface. The important visible objects are:

1. the 852-cell final pattern;
2. the 15 displayed P7 templates;
3. the 6-bit mask convention, with slots 1..6 in the displayed order `E, NE, NW, W, SW, SE`;
4. the 536-row canonical matrix derived from `15 × 64` P7-mask contexts modulo C6;
5. the reduced accept/reject status: 48 accept rows and 41 reject rows;
6. the growth-count sequence, with a finite preview of the terminal plateau.

## How visual data becomes JSON

The full visual-to-JSON derivation has three conceptual stages:

1. **Extract visible atoms.** Read the visible SVG geometry and labels for the main pattern and P7 thumbnails. The relevant helper scripts are included in `pipeline_code/`, especially:
   - `visible_pdf_scrape_rederive_v44.py`
   - `apex_v58_visible_svg_extract_verify_v59.py`
   - `apex_v58_visible_svg_image_to_growth_json_v60.py`

2. **Canonicalize P7 × masks.** For each displayed P7 template and each 6-bit mask, form a six-slot neighbor key. Canonicalize it under the current visible-frame rotation convention:

   ```text
   slot p       → p + k
   state index i → i + k
   ```

   The 960 raw P7-mask pairs reduce to 536 unique canonical contexts. This is the `|V′| = 536` number printed in the pseudocode.

3. **Reduce to the finite certificate.** Replay the known finite growth and mark which accept/reject matrix rows are actually used. The final finite closure certificate keeps only the rows needed to replay this 852-cell record:

   ```text
   accept rules: 48
   reject rules: 41
   terminal cells: 852
   terminal births: 0
   terminal unknown frontier: 0
   ```

## Is the JSON itself the certificate?

Yes. The file `certificate/apex852_pdf_payload_v88_reduced_certificate.json` is already the reduced finite closure certificate.

The verifier does **not** need to scrape the PDF, read the SVG, or consult search priors. It uses only these JSON fields:

- `seed_axiom`
- `accept_rules`
- `reject_rules`
- `canonicalization`
- `growth_counts`
- `verification`

The verifier starts from the seed, scans frontier cells, canonicalizes each six-neighbor context, applies accept rules to birth cells, treats reject rules as closed/waiting frontier, and fails if an unknown frontier context appears. It stops when no births occur. In v88 it reaches:

```text
final_cells: 852
terminal_step: 60
terminal_births: 0
terminal_unknown_frontier: 0
used_accept_rules: 48
used_reject_rules: 41
OK: true
```

Run:

```bash
cd verify
python verify_reduced_certificate_from_payload_v88.py ../certificate/apex852_pdf_payload_v88_reduced_certificate.json --json
```

## What the PDF embeds

The PDF embeds the JSON certificate as an explicit file attachment, not an opaque hidden payload:

- `apex852_pdf_payload_v88_reduced_certificate.json`
- `pseudocode_style_object_v40.json`

The SVG metadata also records the payload filename and SHA-256 so the visual page can be checked against the sidecar/payload.

## Plateau preview

The numeric growth prefix is the computed finite record. The repeated terminal 142s and trailing zero differences are a finite preview of the terminal plateau after closure. The payload keeps both forms distinct:

- `a_sequence`
- `first_differences`
- `a_sequence_plateau_preview`
- `first_differences_plateau_preview`
