# Artifact 18: exact 12/24-gon burner, compact corpus, and reviewer handoff.
GO ?= go
PYTHON ?= python3
TEST_EVENTS ?= 1000
TEST_WORKSPACE ?= .test-workspace
WORD_TERMS ?= 50
RUN_STAMP := $(shell date -u +%Y%m%dT%H%M%SZ)
RUN_DIR ?= reruns/$(RUN_STAMP)

.PHONY: help build test test-go test-monitor words words-check words-print corpus-check burn-50k rerun-50k clean

help:
	@printf '%s\n' \
	  'build        build the exact Go burner at bin/burner' \
	  'test         Go regressions plus a monitored one-division smoke in every lane' \
	  'words        certify and regenerate the six 10,000-term quotient integer words' \
	  'words-print  print checksum-checked saved quotient-word prefixes (WORD_TERMS=50)' \
	  'words-check  verify saved integer words against all 50,000 events per lane' \
	  'corpus-check verify all retained compact blocks and decoded chain linkage' \
	  'burn-50k     fresh 50,000-event burn per lane in a timestamped rerun workspace' \
	  'rerun-50k    alias for burn-50k' \
	  'clean        remove build output and disposable smoke workspace'

build:
	@mkdir -p bin
	$(GO) build -o bin/burner ./cmd/burner

test: test-go test-monitor

test-go:
	$(GO) test ./...

# Runs one 1,000-event division in each lane through the actual 80-column
# monitor. In a TTY it is live; --snapshot emits a final monitor frame in logs.
# The disposable workspace is deleted only after its three compact blocks verify.
test-monitor:
	@rm -rf $(TEST_WORKSPACE)
	$(PYTHON) tools/launch_v2_50k.py --target $(TEST_EVENTS) --workspace $(TEST_WORKSPACE) --skip-go-test --snapshot --no-png --poll 0.1 --report-poll 0.25
	$(PYTHON) tools/check_test_workspace.py --root $(TEST_WORKSPACE) --target $(TEST_EVENTS)
	@rm -rf $(TEST_WORKSPACE)
	@echo 'PASS Artifact 18 monitored smoke: 1 division per lane.'

words:
	$(PYTHON) tools/export_words.py --root . --out-dir words --terms 10000 --target-events 50000

words-check:
	$(PYTHON) tools/export_words.py --root . --out-dir words --terms 10000 --target-events 50000 --check

words-print:
	$(PYTHON) tools/print_words.py --root . --terms $(WORD_TERMS)

corpus-check:
	$(PYTHON) tools/check_corpus.py --root . --target 50000 --full

# Reruns never target ./blocks: preserving the delivered corpus is intentional.
burn-50k:
	@echo 'Artifact 18 fresh burn workspace: $(RUN_DIR)'
	$(PYTHON) tools/launch_v2_50k.py --target 50000 --workspace $(RUN_DIR)
	$(PYTHON) tools/check_corpus.py --root $(RUN_DIR) --target 50000 --full

rerun-50k: burn-50k

clean:
	rm -rf bin $(TEST_WORKSPACE)
