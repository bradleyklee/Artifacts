PYTHON ?= python3
GO ?= go
THREE := 1152 1241 1273 1489 1529 1643 2142 2925 3097 4092 4678 5629 5722
CLOCK := 031 086 091 124 125

.PHONY: all check check-three check-clock extract extract-three extract-clock render index smoke evolve-three evolve-clock

all: check extract render index

check: check-three check-clock

check-three:
	@set -e; for id in $(THREE); do \
	  $(PYTHON) code/check_three.py data/three-body/evolve/$$id.json --out data/three-body/check/$$id.json; \
	done

check-clock:
	@set -e; for id in $(CLOCK); do \
	  $(PYTHON) code/check_clock.py data/clock/evolve/$$id.json --out data/clock/check/$$id.json; \
	done

extract: extract-three extract-clock

extract-three:
	@set -e; for id in $(THREE); do \
	  tmp=$$(mktemp -d); \
	  $(PYTHON) code/extract_three.py data/three-body/evolve/$$id.json --outdir $$tmp >/dev/null; \
	  cp $$tmp/class_$$id.pairs.csv data/three-body/pairs/$$id.csv; \
	  cp $$tmp/class_$$id.ternary.sequence.csv data/three-body/ternary/$$id.csv; \
	  cp $$tmp/class_$$id.ternary.summary.json data/three-body/ternary/$$id.json; \
	  rm -rf $$tmp; \
	done

extract-clock:
	@set -e; for id in $(CLOCK); do \
	  $(PYTHON) code/extract_clock.py data/clock/evolve/$$id.json --out data/clock/pairs/$$id.csv >/dev/null; \
	done

render:
	$(PYTHON) code/render_initial.py --all .

index:
	$(PYTHON) code/build_index.py

# Fast representative check of both independent-checker paths and the data-driven SVG renderer.
smoke:
	$(PYTHON) code/check_three.py data/three-body/evolve/1489.json --out /tmp/1489.check.json
	$(PYTHON) code/check_clock.py data/clock/evolve/086.json --out /tmp/086.check.json
	$(PYTHON) code/render_initial.py --all .
	@test $$(find data/three-body/images -name '*.svg' | wc -l) -eq 13
	@test $$(find data/clock/images -name '*.svg' | wc -l) -eq 5

# Producers are retained for regeneration. They are not part of the fast verification path.
evolve-three:
	@set -e; for id in $(THREE); do \
	  $(GO) run code/evolve_three.go --class $$id --complexity-cutoff-bits 192 --out /tmp/$$id.three.json; \
	done

evolve-clock:
	@set -e; for id in $(CLOCK); do \
	  $(GO) run code/evolve_clock.go code/clock_core.go --seed data/clock/initial/$$id.json --out /tmp/$$id.clock.json --batches 20000 --complexity-bits 192; \
	done
