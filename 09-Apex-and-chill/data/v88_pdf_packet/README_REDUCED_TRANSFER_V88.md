# Apex 852 v88 reduced transfer packet

This is the small handoff packet for the current window. It contains only the final v88 artifact, the explicit JSON certificate, local replay/structure checks, and the minimum code/docs needed to explain and verify this artifact.

Broad search history, priors, original upload archaeology, and unrelated scripts are intentionally excluded for a later package.

## Reduced file structure

```text
apex852_v88_reduced_transfer_packet/
  README_REDUCED_TRANSFER_V88.md
  REDUCED_MANIFEST_V88.json
  checksums_sha256.txt

  artifact/
    apex_and_chill_page13_v88_bottom_spacing.pdf
    apex_and_chill_page13_v88_bottom_spacing.svg
    apex_and_chill_page13_v88_bottom_spacing_report.json

  certificate/
    apex852_pdf_payload_v88_reduced_certificate.json

  verify/
    verify_reduced_certificate_from_payload_v88.py
    verify_payload_stdout_v88.json
    pdf_structure_v88.json

  rebuild_pdf/
    rebuild_pdf_from_final_svg.py
    pseudocode_style_object_v40.json

  docs/
    VISUAL_TO_JSON_CERTIFICATE_EXPLANATION.md

  pipeline_code/
    visible_pdf_scrape_rederive_v44.py
    apex_v58_visible_svg_extract_verify_v59.py
    apex_v58_visible_svg_image_to_growth_json_v60.py
    apex_v58_step_by_visible_accept_rules_v62.py
    apex_v58_first_rule_fixture_v63.json
    apex_svg_stage4_plus_matrix_v69.py
    apex_svg_stage5_reduced_certificate_v70.py
    apex_svg_stage16_rule_arrows_v83.py
    apex_svg_stage20_plateau_preview_v87.py
    apex_svg_stage21_bottom_spacing_v88.py

  source_data/
    apex_852_slowest_depth60.json
    original_page_v41.pdf
    original_page_v41.svg
```

## Certificate status

The JSON in `certificate/` is the reduced finite closure certificate. It can be replayed without scraping the PDF/SVG.

Expected verifier result:

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

See `docs/VISUAL_TO_JSON_CERTIFICATE_EXPLANATION.md` for the clean explanation of the visual-data-to-JSON path and why the JSON is already enough to recompute the finite closure certificate.

## Main output

The main output PDF is duplicated at the packet root for easy handoff:

```text
apex_and_chill_page13_v88_bottom_spacing.pdf
```

The organized copy remains under `artifact/` with the SVG and report.

