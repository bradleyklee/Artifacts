PYTHON ?= python3

MODEL := data/spectre_unified_model_v0.dat
REDUCED := data/reduced_spectre_model.dat
OUT := out

.PHONY: all reduce-data verify artifacts clean

all: reduce-data verify artifacts

$(OUT):
	mkdir -p $(OUT)

reduce-data: | $(OUT)
	$(PYTHON) -u src/reduce_exact.py \
		--model $(MODEL) \
		--status-every 100 \
		--write-reduced $(REDUCED) \
		--verify-reduced $(REDUCED) \
		| tee $(OUT)/exact_reduction_summary.txt

verify: reduce-data
	$(PYTHON) -u src/sage_hexagons.py verify \
		--model $(REDUCED) \
		| tee $(OUT)/verify.txt

artifacts: reduce-data
	$(PYTHON) -u src/sage_hexagons.py make-artifacts \
		--model $(REDUCED) \
		--out $(OUT)

clean:
	rm -rf $(OUT)
