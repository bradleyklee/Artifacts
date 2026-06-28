PYTHON ?= python3

verify:
	$(PYTHON) cases/four_quadrant_halfedge_octagons/tools/extract_ternary.py --check
	$(PYTHON) cases/four_quadrant_quarter_edge_squares/code/search.py --output /tmp/16-squares.json
	diff -u cases/four_quadrant_quarter_edge_squares/data/result.json /tmp/16-squares.json

hashes:
	find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
