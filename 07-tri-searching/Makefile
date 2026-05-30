SHELL := /bin/bash
PYTHON ?= python3
SOLVER ?= glucose4
PERIODIC_DEPTH ?= 10
COMPLETION_DEPTH ?= 7

OUT := out
DATA := data/periodic_certificates.txt
PDF := triangle_periodic_certificates.pdf
SVG_DIR := $(OUT)/periodic_certificate_svgs
SUMMARY := $(OUT)/search_summary.txt
SURVIVORS := $(OUT)/survivors.txt

.PHONY: all search records pdf verify clean

all: search pdf

$(OUT):
	mkdir -p $(OUT)

search: | $(OUT)
	$(PYTHON) src/triangle_sat_search.py \
		--periodic-depth $(PERIODIC_DEPTH) \
		--completion-depth $(COMPLETION_DEPTH) \
		--summary --solver $(SOLVER) \
		> $(SURVIVORS) \
		2> >(tee $(SUMMARY) >&2)

records: | $(OUT)
	mkdir -p data
	$(PYTHON) src/triangle_export_periodic_records.py \
		--search-script src/triangle_sat_search.py \
		--periodic-depth $(PERIODIC_DEPTH) \
		--solver $(SOLVER) \
		--output $(DATA)

pdf: records
	$(PYTHON) src/triangle_render_periodic_report.py $(DATA) \
		--svg-dir $(SVG_DIR) \
		--pdf $(PDF)

verify: SOLVER=glucose4
verify: PERIODIC_DEPTH=10
verify: COMPLETION_DEPTH=7
verify: search pdf
	grep -qx 'minimal_periodic_certificates=49' $(SUMMARY)
	grep -qx 'good_results=0' $(SUMMARY)
	grep -q '^meta periodic_area=10 solver=glucose4 count=49$$' $(DATA)
	test ! -s $(SURVIVORS)
	@echo 'verified: 49 periodic certificates and no survivors at the default bounds'

clean:
	rm -rf $(OUT) $(DATA) $(PDF)
