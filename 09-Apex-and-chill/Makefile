VENV ?= .venv
PYTHON ?= $(shell test -x "$(VENV)/bin/python3" && echo "$(VENV)/bin/python3" || echo python3)
BUILD ?= build

# Publication-facing root PDF.  The organized copy under data/ is kept for provenance.
PDF := apex_and_chill_page13_v88_bottom_spacing.pdf
SVG := data/v88_pdf_packet/artifact/apex_and_chill_page13_v88_bottom_spacing.svg
CERT := data/v88_pdf_packet/certificate/apex852_pdf_payload_v88_reduced_certificate.json
SEED_RECORDS := data/dh12_seed_data/records_combined_small_seed.jsonl
SIGNPOSTS := data/dh12_seed_data/signpost_genes_69x_to_852.json

VISIBLE_DIR := $(BUILD)/generated/visible_pdf
AUDIT_DIR := $(BUILD)/audit
SEARCH_DIR := $(BUILD)/search/policy

SEARCH_KEEP_MIN ?= 800
SEARCH_MUTATIONS ?= 15
SEARCH_MATES ?= 15
SEARCH_ADOPT_UPS ?= 15
SEARCH_ADOPT_DOWNS ?= 15
SEARCH_ADOPT_EQUALS ?= 6
SEARCH_MAX_FOUND ?= 25
SEARCH_MAX_EDITS ?= 8
SEARCH_MAX_REPLAY_STEPS ?= 70
SEARCH_MAX_CELLS ?= 1200
SEARCH_SEED ?= 2026061709
SEARCH_PROGRESS_EVERY ?= 50

# Longer exploratory target.  Goal: collect about 100 closed-chill
# same-family records without changing the short public search defaults.
SEARCH_LONG_DIR ?= $(BUILD)/search/policy_long
SEARCH_LONG_MUTATIONS ?= 110
SEARCH_LONG_MATES ?= 130
SEARCH_LONG_ADOPT_UPS ?= 100
SEARCH_LONG_ADOPT_DOWNS ?= 100
SEARCH_LONG_ADOPT_EQUALS ?= 40
SEARCH_LONG_MIN_FOUND ?= 100
SEARCH_LONG_MIN_OPERATOR_TRIALS ?= 20
SEARCH_LONG_MAX_REPLAY_STEPS ?= 62
SEARCH_LONG_MAX_CELLS ?= 900
SEARCH_LONG_PROGRESS_EVERY ?= 50

.PHONY: all doctor setup compile test test-pdf-structure test-pdf-visible test-pdf-derived-cert test-official-cert test-seeds rules-card search search-long clean dist

all: test

doctor:
	@$(PYTHON) code/check_deps.py

setup:
	@echo "[OK] setup: no external packages are required"

compile:
	@$(PYTHON) -m py_compile \
		code/visible_pdf_scrape_rederive_pdfonly_v88_plus.py \
		code/visible_svg_scrape_rederive_svgonly_v88_plus.py \
		code/make_compatible_certificate_from_visible_payload.py \
		code/verify_reduced_certificate_from_payload_v88.py \
		code/check_pdf_structure.py \
		code/search_dh12_policy.py \
		code/mini_dh12_sparse_search.py \
		code/validate_seed_records.py \
		code/assert_json.py \
		code/check_deps.py \
		code/run_test.py \
		code/print_test_report.py \
		code/print_search_report.py \
		code/print_rule_card.py

$(AUDIT_DIR)/pdf_structure_check.json: $(PDF) code/check_pdf_structure.py
	@mkdir -p $(AUDIT_DIR)
	@$(PYTHON) code/check_pdf_structure.py $(PDF) --out-json $@ > $(AUDIT_DIR)/pdf_structure_check_stdout.json

$(VISIBLE_DIR)/visible_pdf_rederived_payload.json: $(SVG) code/visible_svg_scrape_rederive_svgonly_v88_plus.py
	@mkdir -p $(VISIBLE_DIR)
	@$(PYTHON) code/visible_svg_scrape_rederive_svgonly_v88_plus.py $(SVG) \
		--out-json $(VISIBLE_DIR)/visible_pdf_rederived_payload.json \
		--out-state $(VISIBLE_DIR)/visible_pdf_scraped_main_state.json \
		--out-report $(VISIBLE_DIR)/visible_pdf_rederive_report.json \
		--audit-payload-json $(CERT) \
		> $(VISIBLE_DIR)/visible_pdf_rederive_stdout.json

$(VISIBLE_DIR)/visible_pdf_rederived_compatible_certificate.json: $(VISIBLE_DIR)/visible_pdf_rederived_payload.json code/make_compatible_certificate_from_visible_payload.py
	@$(PYTHON) code/make_compatible_certificate_from_visible_payload.py \
		--in-json $(VISIBLE_DIR)/visible_pdf_rederived_payload.json \
		--out-json $(VISIBLE_DIR)/visible_pdf_rederived_compatible_certificate.json \
		> $(VISIBLE_DIR)/visible_pdf_rederived_compatible_certificate_stdout.json

$(VISIBLE_DIR)/visible_pdf_rederived_certificate_verify.json: $(VISIBLE_DIR)/visible_pdf_rederived_compatible_certificate.json code/verify_reduced_certificate_from_payload_v88.py
	@$(PYTHON) code/verify_reduced_certificate_from_payload_v88.py --json \
		$(VISIBLE_DIR)/visible_pdf_rederived_compatible_certificate.json \
		> $(VISIBLE_DIR)/visible_pdf_rederived_certificate_verify.json

$(AUDIT_DIR)/official_certificate_verify_stdout.json: $(CERT) code/verify_reduced_certificate_from_payload_v88.py
	@mkdir -p $(AUDIT_DIR)
	@$(PYTHON) code/verify_reduced_certificate_from_payload_v88.py --json $(CERT) \
		> $(AUDIT_DIR)/official_certificate_verify_stdout.json

$(AUDIT_DIR)/seed_validation_summary.json: $(SEED_RECORDS) code/validate_seed_records.py code/mini_dh12_sparse_search.py
	@mkdir -p $(AUDIT_DIR)
	@$(PYTHON) code/validate_seed_records.py \
		--records $(SEED_RECORDS) \
		--out-jsonl $(AUDIT_DIR)/seed_validation_detail.jsonl \
		--min-total 52 \
		--min-closed-zero-unknown 50 \
		--min-exact 40 \
		--min-max-cells 852 \
		> $(AUDIT_DIR)/seed_validation_summary.json

# `make test` is intentionally from-scratch for the publication proof.
# It deletes generated proof artifacts first, then re-extracts visible/vector
# SVG image data, reconstructs JSON, and verifies the certificate.
test: compile
	@$(PYTHON) code/run_test.py

test-pdf-structure: $(AUDIT_DIR)/pdf_structure_check.json
	@$(PYTHON) code/assert_json.py --quiet $(AUDIT_DIR)/pdf_structure_check.json \
		--eq ok true \
		--eq pages 1 \
		--eq image_xobjects 0 \
		--ge uri_links 1

test-pdf-visible: $(VISIBLE_DIR)/visible_pdf_rederived_payload.json
	@$(PYTHON) code/assert_json.py --quiet $(VISIBLE_DIR)/visible_pdf_rederive_report.json \
		--eq ok true \
		--eq embedded_json_used false \
		--eq matrix_unique_contexts 536 \
		--eq matrix_counts.accept 48 \
		--eq matrix_counts.reject 41 \
		--eq independent_replay_from_rederived_payload.final_cells 852 \
		--eq independent_replay_from_rederived_payload.last_history_row.births 0 \
		--eq independent_replay_from_rederived_payload.unknown_terminal 0 \
		--eq independent_replay_from_rederived_payload.compare_to_transformed_visible_main.exact true \
		--eq audit_against_payload_json_not_used_for_derivation.accept_exact true \
		--eq audit_against_payload_json_not_used_for_derivation.reject_exact true

test-pdf-derived-cert: $(VISIBLE_DIR)/visible_pdf_rederived_certificate_verify.json
	@$(PYTHON) code/assert_json.py --quiet $(VISIBLE_DIR)/visible_pdf_rederived_certificate_verify.json \
		--eq ok true \
		--eq final_cells 852 \
		--eq terminal_births 0 \
		--eq terminal_unknown_frontier 0 \
		--eq used_accept_rules 48 \
		--eq used_reject_rules 41 \
		--eq a_sequence_matches_payload true \
		--eq first_differences_matches_payload true


$(VISIBLE_DIR)/used_accept_rules_card.txt: $(VISIBLE_DIR)/visible_pdf_rederived_payload.json code/print_rule_card.py
	@$(PYTHON) code/print_rule_card.py \
		$(VISIBLE_DIR)/visible_pdf_rederived_payload.json \
		--out-txt $(VISIBLE_DIR)/used_accept_rules_card.txt \
		--out-md $(VISIBLE_DIR)/used_accept_rules_card.md \
		> $(VISIBLE_DIR)/used_accept_rules_card_stdout.txt

rules-card: $(VISIBLE_DIR)/used_accept_rules_card.txt
	@cat $(VISIBLE_DIR)/used_accept_rules_card.txt

test-official-cert: $(AUDIT_DIR)/official_certificate_verify_stdout.json
	@$(PYTHON) code/assert_json.py --quiet $(AUDIT_DIR)/official_certificate_verify_stdout.json \
		--eq ok true \
		--eq final_cells 852 \
		--eq terminal_births 0 \
		--eq terminal_unknown_frontier 0 \
		--eq used_accept_rules 48 \
		--eq used_reject_rules 41

test-seeds: $(AUDIT_DIR)/seed_validation_summary.json
	@$(PYTHON) code/assert_json.py --quiet $(AUDIT_DIR)/seed_validation_summary.json \
		--eq ok true \
		--eq records 52 \
		--ge closed_zero_unknown 50 \
		--ge exact_state_matches 40 \
		--ge max_replay_cells 852
	@echo "Seed records: PASS - details in $(AUDIT_DIR)/seed_validation_summary.json"

# Release-facing search.  This is not the old weak one-rule smoke target.
# It uses the prior operator framework:
#   MUTATE = prior/statistics-informed random walk around one parent
#   MATE        = interior/averaging walk on the two-parent axis
#   ADOPT_UP    = exterior walk beyond the higher-lifetime parent
#   ADOPT_DOWN  = exterior walk beyond the lower-lifetime parent
#   ADOPT_EQUAL = equal-lifetime exterior walk, choosing either side
# It writes progress lines to the terminal and full JSON/JSONL audit files under $(SEARCH_DIR).
search: compile
	@rm -rf $(SEARCH_DIR)
	@mkdir -p $(SEARCH_DIR)
	@$(PYTHON) code/search_dh12_policy.py \
		--records $(SEED_RECORDS) \
		--signposts $(SIGNPOSTS) \
		--outdir $(SEARCH_DIR) \
		--seed $(SEARCH_SEED) \
		--keep-min $(SEARCH_KEEP_MIN) \
		--mutations $(SEARCH_MUTATIONS) \
		--mates $(SEARCH_MATES) \
		--adopt-ups $(SEARCH_ADOPT_UPS) \
		--adopt-downs $(SEARCH_ADOPT_DOWNS) \
		--adopt-equals $(SEARCH_ADOPT_EQUALS) \
		--max-edits $(SEARCH_MAX_EDITS) \
		--max-replay-steps $(SEARCH_MAX_REPLAY_STEPS) \
		--max-cells $(SEARCH_MAX_CELLS) \
		--max-found $(SEARCH_MAX_FOUND) \
		--progress-every $(SEARCH_PROGRESS_EVERY) \
		--found-mode brief \
		--allow-known-state \
		2>&1 | tee $(SEARCH_DIR)/search_progress.log
	@$(PYTHON) code/assert_json.py --quiet $(SEARCH_DIR)/policy_search_summary.json \
		--eq ok true \
		--eq loaded_records 52 \
		--ge valid_parent_records 50 \
		--ge new_closed_chill_ge_keep_min 1 \
		--ge best_new_cells $(SEARCH_KEEP_MIN)
	@$(PYTHON) code/print_search_report.py $(SEARCH_DIR)/policy_search_summary.json


# Longer bounded search for collecting a larger candidate batch.
# It deliberately enters every operator block, including ADOPT_*.
# Early target-stop is allowed only after each method has run a
# minimum number of trials, so MATE cannot prevent ADOPT from running.
search-long: compile
	@rm -rf $(SEARCH_LONG_DIR)
	@mkdir -p $(SEARCH_LONG_DIR)
	@$(PYTHON) code/search_dh12_policy.py \
		--records $(SEED_RECORDS) \
		--signposts $(SIGNPOSTS) \
		--outdir $(SEARCH_LONG_DIR) \
		--seed $(SEARCH_SEED) \
		--keep-min $(SEARCH_KEEP_MIN) \
		--mutations $(SEARCH_LONG_MUTATIONS) \
		--mates $(SEARCH_LONG_MATES) \
		--adopt-ups $(SEARCH_LONG_ADOPT_UPS) \
		--adopt-downs $(SEARCH_LONG_ADOPT_DOWNS) \
		--adopt-equals $(SEARCH_LONG_ADOPT_EQUALS) \
		--max-edits $(SEARCH_MAX_EDITS) \
		--max-replay-steps $(SEARCH_LONG_MAX_REPLAY_STEPS) \
		--max-cells $(SEARCH_LONG_MAX_CELLS) \
		--max-found $(SEARCH_LONG_MIN_FOUND) \
		--stop-after-max-found \
		--min-trials-before-stop $(SEARCH_LONG_MIN_OPERATOR_TRIALS) \
		--progress-every $(SEARCH_LONG_PROGRESS_EVERY) \
		--found-mode none \
		--allow-known-state \
		2>&1 | tee $(SEARCH_LONG_DIR)/search_progress.log
	@$(PYTHON) code/assert_json.py --quiet \
		$(SEARCH_LONG_DIR)/policy_search_summary.json \
		--eq ok true \
		--eq loaded_records 52 \
		--ge valid_parent_records 50 \
		--ge new_closed_chill_ge_keep_min $(SEARCH_LONG_MIN_FOUND) \
		--ge best_new_cells $(SEARCH_KEEP_MIN) \
		--eq all_operator_blocks_entered true \
		--ge operator_trials.ADOPT_UP $(SEARCH_LONG_MIN_OPERATOR_TRIALS) \
		--ge operator_trials.ADOPT_DOWN $(SEARCH_LONG_MIN_OPERATOR_TRIALS) \
		--ge operator_trials.ADOPT_EQUAL $(SEARCH_LONG_MIN_OPERATOR_TRIALS)
	@$(PYTHON) code/print_search_report.py \
		$(SEARCH_LONG_DIR)/policy_search_summary.json

clean:
	@rm -rf $(BUILD)

dist: clean test search
	@mkdir -p $(BUILD)/dist
	@zip -qr $(BUILD)/dist/09-Apex-and-chill_minimal_merge_v1.zip . \
		-x 'build/dist/*' '__pycache__/*' '*/__pycache__/*'
	@echo "Wrote $(BUILD)/dist/09-Apex-and-chill_minimal_merge_v1.zip"
