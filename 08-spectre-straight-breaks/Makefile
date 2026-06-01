PYTHON ?= env PYTHONDONTWRITEBYTECODE=1 python3 -S

EXCERPTS := source_excerpt/figure_4_2_edge_tile_macros.tex source_excerpt/figure_5_1_supertiles.tex
EXTRACT_SRC := src/spectre_straight.py src/extract_source_data.py
AUDIT_SRC := src/spectre_straight.py src/audit_straight_joins.py

.NOTPARALLEL:
.PHONY: all data audit pdf check smoke clean

all: pdf
	@printf '%s\n' '==> Artifact 08 build complete.'

data: data/.extract.stamp

data/.extract.stamp: $(EXCERPTS) $(EXTRACT_SRC)
	@printf '%s\n' '==> [1/4] Extract Figure 4.2 / 5.1 source data and straight-path records.'
	@$(PYTHON) src/extract_source_data.py
	@touch $@

audit: data/.audit.stamp

data/.audit.stamp: data/.extract.stamp $(AUDIT_SRC)
	@printf '%s\n' '==> [2/4] Audit all positioned straight joins under inflation.'
	@$(PYTHON) src/audit_straight_joins.py
	@touch $@

pdf: data/.audit.stamp docs/spectre_straight_path_rule_tables.pdf docs/spectre_straight_join_audit_5page.pdf

docs/spectre_straight_path_rule_tables.pdf: data/.extract.stamp src/render_rule_tables.py
	@printf '%s\n' '==> [3a/4] Render straight-path rule-table PDF.'
	@$(PYTHON) src/render_rule_tables.py

docs/spectre_straight_join_audit_5page.pdf: data/.audit.stamp src/render_audit_pdf.py
	@printf '%s\n' '==> [3b/4] Render five-page local-join audit PDF.'
	@$(PYTHON) src/render_audit_pdf.py

check: all
	@printf '%s\n' '==> [4/4] Check regenerated counts and deliverables.'
	@$(PYTHON) src/check_outputs.py

smoke:
	@printf '%s\n' '==> Smoke test: clean rebuild of Artifact 08.'
	@$(MAKE) --no-print-directory clean
	@$(MAKE) --no-print-directory all check
	@printf '%s\n' '==> Smoke test passed.'

clean:
	@printf '%s\n' '==> Cleaning generated Artifact 08 data and documents.'
	@rm -f data/*.csv data/*.json data/.extract.stamp data/.audit.stamp
	@rm -f docs/*.pdf build/*
	@rm -rf src/__pycache__ _verify
