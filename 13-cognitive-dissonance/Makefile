PYTHON ?= python3
BUILD := build
PLOTS := $(BUILD)/plots
N18_CERT := data/certificates/n18_bidirectional_vertex_sweep_certificate.txt
N45_CERT := data/certificates/n45_site_model_polystick_circle_certificate.txt
N18_DATA := data/n18_witnesses.json
N45_DATA := data/n45_witnesses.json
ARCHIVE := dist/circle_lattice_mwe_v1.zip

.PHONY: all data-check check plots previews build-info archive clean

all: check plots

# Re-extract the normalized fixtures from the preserved certificate text before
# exact checking.  The only routine stdout is intentionally short.
data-check:
	@echo "Reading certificates: $(N18_CERT); $(N45_CERT)"
	@rm -rf $(BUILD)/extracted_data
	@mkdir -p $(BUILD)/extracted_data
	@$(PYTHON) code/bootstrap_data.py --n18 $(N18_CERT) --n45 $(N45_CERT) --out-dir $(BUILD)/extracted_data
	@cmp -s $(N18_DATA) $(BUILD)/extracted_data/n18_witnesses.json
	@cmp -s $(N45_DATA) $(BUILD)/extracted_data/n45_witnesses.json

check: data-check
	@mkdir -p $(BUILD)
	@$(PYTHON) code/verify.py --n18 $(N18_DATA) --n45 $(N45_DATA) --report $(BUILD)/verification_report.txt

plots: check
	@echo "Making N=18 polyomino plots and N=45 polystick plots in $(PLOTS)"
	@rm -rf $(PLOTS)
	@$(PYTHON) code/render.py --n18 $(N18_DATA) --n45 $(N45_DATA) --out $(PLOTS)

# Optional raster previews. SVG is the primary reproducible output.
previews: plots
	@echo "Making PNG contact-sheet previews in $(PLOTS)"
	@$(PYTHON) code/render_png_previews.py --plots $(PLOTS)

build-info:
	@$(PYTHON) code/build_info.py --root . --out $(BUILD)/BUILD_INFO.txt

archive: all previews build-info
	@$(PYTHON) code/make_archive.py --root . --out $(ARCHIVE)

clean:
	@rm -rf $(BUILD)/extracted_data $(BUILD)/plots $(BUILD)/verification_report.txt $(BUILD)/BUILD_INFO.txt $(ARCHIVE)
