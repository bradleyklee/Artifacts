GO ?= go
PYTHON ?= python3
LEVEL ?= 6
N ?= 40

.PHONY: sequence differences counts table test python-sequence python-differences

sequence:
	@$(GO) run ./cmd/goldenhex sequence -level $(LEVEL)

differences:
	@$(GO) run ./cmd/goldenhex differences -level $(LEVEL)

counts:
	@$(GO) run ./cmd/goldenhex counts -n $(N)

table:
	@$(GO) run ./cmd/goldenhex counts -n $(N) -table

test:
	@$(GO) test ./...

python-sequence:
	@$(PYTHON) golden_hex.py sequence $(LEVEL)

python-differences:
	@$(PYTHON) golden_hex.py differences $(LEVEL)
