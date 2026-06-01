SHELL := /bin/bash
PYTHON ?= python3
SOLVER ?= glucose4
FAMILY ?= anchored
PERIODIC_DEPTH ?= 6
PERIODIC_AREA := $(shell echo $$(( $(PERIODIC_DEPTH) * $(PERIODIC_DEPTH) )))
COMPLETION_DEPTH ?= 7

OUT := out
DATA := data/periodic_certificates.txt
SURVIVOR_DATA := data/survivor_configurations.txt
PDF := triangle_periodic_certificates.pdf
SURVIVOR_PDF := triangle_survivor_configurations.pdf
SVG_DIR := $(OUT)/periodic_certificate_svgs
SURVIVOR_SVG_DIR := $(OUT)/survivor_configuration_svgs
SUMMARY := $(OUT)/search_summary.txt
SURVIVORS := $(OUT)/survivors.txt

.PHONY: all search records pdf survivor-records survivor-pdf unrestricted unrestricted-reports free free-periodic-pdf free-survivor-pdf verify clean

all: search pdf survivor-pdf

$(OUT):
	mkdir -p $(OUT)

search: | $(OUT)
	@echo "==> periodic scale N=$(PERIODIC_DEPTH); testing torus area <= $(PERIODIC_DEPTH)^2 = $(PERIODIC_AREA)"
	$(PYTHON) src/triangle_sat_search.py \
		--family $(FAMILY) \
		--periodic-depth $(PERIODIC_AREA) \
		--completion-depth $(COMPLETION_DEPTH) \
		--summary --solver $(SOLVER) \
		> $(SURVIVORS) \
		2> >(tee $(SUMMARY) >&2)

records: | $(OUT)
	mkdir -p data
	$(PYTHON) src/triangle_export_periodic_records.py \
		--search-script src/triangle_sat_search.py \
		--family $(FAMILY) \
		--periodic-depth $(PERIODIC_AREA) \
		--solver $(SOLVER) \
		--output $(DATA)

pdf: records
	$(PYTHON) src/triangle_render_periodic_report.py $(DATA) \
		--svg-dir $(SVG_DIR) \
		--pdf $(PDF)

survivor-records: search
	mkdir -p data
	$(PYTHON) src/triangle_export_survivor_records.py \
		--search-script src/triangle_sat_search.py \
		--family $(FAMILY) \
		--periodic-depth $(PERIODIC_AREA) \
		--completion-depth $(COMPLETION_DEPTH) \
		--solver $(SOLVER) \
		--output $(SURVIVOR_DATA)

survivor-pdf: survivor-records
	$(PYTHON) src/triangle_render_survivor_report.py $(SURVIVOR_DATA) \
		--svg-dir $(SURVIVOR_SVG_DIR) \
		--pdf $(SURVIVOR_PDF)

# The unrestricted 20-bit family may leave too many survivor panels for an
# automatic report at weak bounds.  Search first, then request reports explicitly.
unrestricted:
	$(MAKE) search FAMILY=unrestricted \
		OUT=out/unrestricted \
		SUMMARY=out/unrestricted/search_summary.txt \
		SURVIVORS=out/unrestricted/survivors.txt \
		PERIODIC_DEPTH=$(PERIODIC_DEPTH) COMPLETION_DEPTH=$(COMPLETION_DEPTH) SOLVER=$(SOLVER)

unrestricted-reports:
	$(MAKE) all FAMILY=unrestricted \
		OUT=out/unrestricted \
		DATA=data/unrestricted_periodic_certificates.txt \
		SURVIVOR_DATA=data/unrestricted_survivor_configurations.txt \
		PDF=triangle_unrestricted_periodic_certificates.pdf \
		SURVIVOR_PDF=triangle_unrestricted_survivor_configurations.pdf \
		SVG_DIR=out/unrestricted/periodic_certificate_svgs \
		SURVIVOR_SVG_DIR=out/unrestricted/survivor_configuration_svgs \
		SUMMARY=out/unrestricted/search_summary.txt \
		SURVIVORS=out/unrestricted/survivors.txt \
		PERIODIC_DEPTH=$(PERIODIC_DEPTH) COMPLETION_DEPTH=$(COMPLETION_DEPTH) SOLVER=$(SOLVER)

# The fully free 21-bit family quotients masks by independent cyclic relabeling
# of ABC and DEF plus swapping the two prototiles (18 symmetry actions).
# A weak bound can leave many survivor panels, so PDF generation is explicit.
free:
	$(MAKE) search FAMILY=free \
		OUT=out/free \
		SUMMARY=out/free/search_summary.txt \
		SURVIVORS=out/free/survivors.txt \
		PERIODIC_DEPTH=$(PERIODIC_DEPTH) COMPLETION_DEPTH=$(COMPLETION_DEPTH) SOLVER=$(SOLVER)

free-periodic-pdf:
	$(MAKE) pdf FAMILY=free \
		OUT=out/free \
		DATA=data/free_periodic_certificates.txt \
		PDF=triangle_free_periodic_certificates.pdf \
		SVG_DIR=out/free/periodic_certificate_svgs \
		PERIODIC_DEPTH=$(PERIODIC_DEPTH) SOLVER=$(SOLVER)

free-survivor-pdf:
	$(MAKE) survivor-pdf FAMILY=free \
		OUT=out/free \
		SURVIVOR_DATA=data/free_survivor_configurations.txt \
		SURVIVOR_PDF=triangle_free_survivor_configurations.pdf \
		SURVIVOR_SVG_DIR=out/free/survivor_configuration_svgs \
		SUMMARY=out/free/search_summary.txt \
		SURVIVORS=out/free/survivors.txt \
		PERIODIC_DEPTH=$(PERIODIC_DEPTH) COMPLETION_DEPTH=$(COMPLETION_DEPTH) SOLVER=$(SOLVER)

verify: FAMILY=anchored
verify: SOLVER=glucose4
verify: PERIODIC_DEPTH=3
verify: COMPLETION_DEPTH=7
verify: search pdf survivor-pdf
	grep -qx 'minimal_periodic_certificates=43' $(SUMMARY)
	grep -qx 'good_results=40' $(SUMMARY)
	grep -q '^meta family=anchored periodic_area=9 solver=glucose4 count=43$$' $(DATA)
	grep -q '^meta family=anchored periodic_area=9 completion_depth=7 solver=glucose4 count=40$$' $(SURVIVOR_DATA)
	test "$$(wc -l < $(SURVIVORS))" -eq 40
	@echo 'verified: 43 periodic certificates and 40 survivors at the default bounds'

clean:
	rm -rf out $(DATA) $(SURVIVOR_DATA) $(PDF) $(SURVIVOR_PDF) \
		data/unrestricted_periodic_certificates.txt data/unrestricted_survivor_configurations.txt \
		triangle_unrestricted_periodic_certificates.pdf triangle_unrestricted_survivor_configurations.pdf \
		data/free_periodic_certificates.txt data/free_survivor_configurations.txt \
		triangle_free_periodic_certificates.pdf triangle_free_survivor_configurations.pdf
