PYTHON ?= python3
WORKERS ?= 4
TIME_LIMIT ?= 120
HEARTBEAT ?= 30
LIMIT ?= 0
STAGE ?=
FROM ?=

.PHONY: help reports verify level5 level5-smoke push push-smoke \
        status logs import-search clean-search

help:
	@echo "P^4 extraction commands"
	@echo "  make level5 WORKERS=10 TIME_LIMIT=30"
	@echo "      Run the initial unresolved queue."
	@echo "  make push WORKERS=10 TIME_LIMIT=120"
	@echo "      Retry only the current timeout cases."
	@echo "  make push WORKERS=10 TIME_LIMIT=600"
	@echo "      Push the timeout remainder again."
	@echo "  make status"
	@echo "      Show deduplicated current results."
	@echo "  make import-search FROM=/path/to/old/search"
	@echo "      Carry existing checkpoints into this extraction."
	@echo "  make verify"
	@echo "      Verify extraction."

reports:
	$(PYTHON) src/generate_reports.py

verify:
	$(PYTHON) src/verify_extraction.py

level5:
	$(PYTHON) src/resume_level5.py \
		--workers $(WORKERS) \
		--time-limit $(TIME_LIMIT) \
		--heartbeat $(HEARTBEAT) \
		--limit $(LIMIT)

level5-smoke:
	$(PYTHON) src/resume_level5.py \
		--workers $(WORKERS) --time-limit 10 \
		--heartbeat 2 --limit 1

push:
	$(PYTHON) src/resume_level5.py \
		--retry-timeouts \
		--workers $(WORKERS) \
		--time-limit $(TIME_LIMIT) \
		--heartbeat $(HEARTBEAT) \
		$(if $(STAGE),--stage $(STAGE),) \
		--limit $(LIMIT)

push-smoke:
	$(PYTHON) src/resume_level5.py \
		--retry-timeouts \
		--workers $(WORKERS) --time-limit 1 \
		--heartbeat 0.2 --stage smoke --limit 1

status:
	@$(PYTHON) src/search_status.py

logs:
	tail -f logs/*worker_*.log

import-search:
	@test -n "$(FROM)" || \
		(echo "usage: make import-search FROM=/path/to/search"; exit 2)
	$(PYTHON) src/import_search.py "$(FROM)"

clean-search:
	rm -f search/*.jsonl
	rm -f logs/*worker_*.log
