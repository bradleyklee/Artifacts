PYTHON ?= python3
REF = reference/mclarnan_1981_ferrite.py

terms-21-60:
	$(PYTHON) $(REF) --n 4 6 8 10 --start-s 21 --end-s 60 > terms/ferrite_terms_S21_S60.txt

terms-21-100:
	$(PYTHON) $(REF) --n 4 6 8 10 --start-s 21 --end-s 100 > terms/ferrite_terms_S21_S100.txt

check:
	$(PYTHON) validation/ferrite_audit.py --audit --start-s 1 --end-s 1 >/dev/null
	@echo check: PASS
