PYTHON ?= python3

.PHONY: terms check

terms:
	$(PYTHON) reference/a011961.py > terms/a011961_n1_100.txt
	$(PYTHON) reference/a011962.py > terms/a011962_n1_100.txt
	$(PYTHON) reference/a011963.py > terms/a011963_n1_100.txt
	$(PYTHON) reference/a011964.py > terms/a011964_n1_100.txt
	$(PYTHON) reference/all.py > terms/all_n1_100.txt

check:
	$(PYTHON) validation/check_claude.py
