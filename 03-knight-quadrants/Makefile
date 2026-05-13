PY ?= python3
SCRIPT := src/knight_quadrant.py
TMPDIR ?= .tmp
COLORSETS := b br brg brgy
ORDERS := spiral dist-atan
GEOMETRIES := square hex

SQUARE_IMAGE_RADIUS := 500
HEX_IMAGE_RADIUS := 120
SQUARE_DEBUG_RADIUS := 6
HEX_DEBUG_RADIUS := 5

SQUARE_PNG_SCALE := 1
HEX_SVG_CELL := 6
SQUARE_DEBUG_CELL := 32
HEX_DEBUG_CELL := 22

.PHONY: all smoke dirs clean geometry debug-geometry data debug-data images debug examples

all: smoke debug images

# Always recreate the directory skeleton so deleted folders are not fatal.
dirs:
	mkdir -p \
	  $(TMPDIR) \
	  data/spiral/square data/spiral/hex \
	  data/dist-atan/square data/dist-atan/hex \
	  img/spiral/square img/spiral/hex \
	  img/dist-atan/square img/dist-atan/hex \
	  img/spiral/square/debug img/spiral/hex/debug \
	  img/dist-atan/square/debug img/dist-atan/hex/debug \
	  example

smoke: dirs
	$(PY) $(SCRIPT) check-hex-knight
	$(PY) $(SCRIPT) check-hex-spiral
	$(PY) $(SCRIPT) geometry --geometry square --order spiral --radius 6 > $(TMPDIR)/smoke_square.geom.csv
	mkdir -p $(TMPDIR)/smoke_square $(TMPDIR)/smoke_hex
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/smoke_square.geom.csv --colorsets b,brg --out-dir $(TMPDIR)/smoke_square >/dev/null
	$(PY) $(SCRIPT) check-fast $(TMPDIR)/smoke_square/b_square_spiral_r6.csv --points $(TMPDIR)/smoke_square.geom.csv
	$(PY) $(SCRIPT) geometry --geometry hex --order dist-atan --radius 4 > $(TMPDIR)/smoke_hex.geom.csv
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/smoke_hex.geom.csv --colorsets brgy --out-dir $(TMPDIR)/smoke_hex >/dev/null
	$(PY) $(SCRIPT) check-fast $(TMPDIR)/smoke_hex/brgy_hex_dist-atan_r4.csv --points $(TMPDIR)/smoke_hex.geom.csv

# Geometry cache for large final images.
geometry: dirs
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_IMAGE_RADIUS); else radius=$(HEX_IMAGE_RADIUS); fi; \
	  for order in $(ORDERS); do \
	    geo=data/$$order/$$geometry/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    if [ ! -f $$geo ]; then \
	      echo "geometry $$geo"; \
	      $(PY) $(SCRIPT) geometry --geometry $$geometry --order $$order --radius $$radius > $$geo; \
	    fi; \
	  done; \
	done

# Separate geometry cache for smaller debug windows.
debug-geometry: dirs
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_DEBUG_RADIUS); else radius=$(HEX_DEBUG_RADIUS); fi; \
	  for order in $(ORDERS); do \
	    geo=data/$$order/$$geometry/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    if [ ! -f $$geo ]; then \
	      echo "geometry $$geo"; \
	      $(PY) $(SCRIPT) geometry --geometry $$geometry --order $$order --radius $$radius > $$geo; \
	    fi; \
	  done; \
	done

# Large data files.
data: geometry
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_IMAGE_RADIUS); else radius=$(HEX_IMAGE_RADIUS); fi; \
	  for order in $(ORDERS); do \
	    dir=data/$$order/$$geometry; \
	    geo=$$dir/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    echo "data $$dir"; \
	    $(PY) $(SCRIPT) batch-data --points $$geo --colorsets "b,br,brg,brgy" --out-dir $$dir --check-fast >/dev/null; \
	  done; \
	done

# Small data files used only for debug rendering.
debug-data: debug-geometry
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_DEBUG_RADIUS); else radius=$(HEX_DEBUG_RADIUS); fi; \
	  for order in $(ORDERS); do \
	    dir=data/$$order/$$geometry; \
	    geo=$$dir/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    echo "debug-data $$dir"; \
	    $(PY) $(SCRIPT) batch-data --points $$geo --colorsets "b,br,brg,brgy" --out-dir $$dir --check-fast >/dev/null; \
	  done; \
	done

# Final large images.
images: data
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_IMAGE_RADIUS); else radius=$(HEX_IMAGE_RADIUS); fi; \
	  for order in $(ORDERS); do \
	    dir=data/$$order/$$geometry; \
	    out=img/$$order/$$geometry; \
	    geo=$$dir/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    mkdir -p $$out; \
	    for colors in $(COLORSETS); do \
	      csv=$$dir/$${colors}_$${geometry}_$${order}_r$${radius}.csv; \
	      if [ "$$geometry" = "square" ]; then \
	        img=$$out/$${colors}_$${geometry}_$${order}_r$${radius}.png; \
	        echo "image $$img"; \
	        $(PY) $(SCRIPT) image $$csv --points $$geo --out $$img --scale $(SQUARE_PNG_SCALE); \
	      else \
	        img=$$out/$${colors}_$${geometry}_$${order}_r$${radius}.svg; \
	        echo "image $$img"; \
	        $(PY) $(SCRIPT) image $$csv --points $$geo --out $$img --cell $(HEX_SVG_CELL); \
	      fi; \
	    done; \
	  done; \
	done

# Debug images come first in `make all`, so they exist even if the large image pass is slow.
debug: debug-data
	@for geometry in $(GEOMETRIES); do \
	  if [ "$$geometry" = "square" ]; then radius=$(SQUARE_DEBUG_RADIUS); cell=$(SQUARE_DEBUG_CELL); else radius=$(HEX_DEBUG_RADIUS); cell=$(HEX_DEBUG_CELL); fi; \
	  for order in $(ORDERS); do \
	    dir=data/$$order/$$geometry; \
	    out=img/$$order/$$geometry/debug; \
	    geo=$$dir/geometry_$${geometry}_$${order}_r$${radius}.csv; \
	    mkdir -p $$out; \
	    for colors in $(COLORSETS); do \
	      csv=$$dir/$${colors}_$${geometry}_$${order}_r$${radius}.csv; \
	      dbg=$$out/$${colors}_$${geometry}_$${order}_debug_r$${radius}.svg; \
	      echo "debug $$dbg"; \
	      $(PY) $(SCRIPT) debug-svg $$csv --points $$geo --radius $$radius --cell $$cell --out $$dbg; \
	    done; \
	  done; \
	done

clean: dirs
	find data -type f ! -name '.gitkeep' -delete
	find img -type f ! -name '.gitkeep' -delete


examples: dirs
	mkdir -p $(TMPDIR)/examples example
	$(PY) $(SCRIPT) geometry --geometry square --order dist-atan --radius 80 > $(TMPDIR)/examples/square_distatan.geom.csv
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/examples/square_distatan.geom.csv --colorsets b --out-dir $(TMPDIR)/examples >/dev/null
	$(PY) $(SCRIPT) image $(TMPDIR)/examples/b_square_dist-atan_r80.csv --points $(TMPDIR)/examples/square_distatan.geom.csv --out example/square-dist-atan-b.png --scale 2
	$(PY) $(SCRIPT) geometry --geometry square --order spiral --radius 80 > $(TMPDIR)/examples/square_spiral.geom.csv
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/examples/square_spiral.geom.csv --colorsets brgy --out-dir $(TMPDIR)/examples >/dev/null
	$(PY) $(SCRIPT) image $(TMPDIR)/examples/brgy_square_spiral_r80.csv --points $(TMPDIR)/examples/square_spiral.geom.csv --out example/square-spiral-brgy.png --scale 2
	$(PY) $(SCRIPT) geometry --geometry hex --order spiral --radius 12 > $(TMPDIR)/examples/hex_spiral.geom.csv
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/examples/hex_spiral.geom.csv --colorsets brgy --out-dir $(TMPDIR)/examples >/dev/null
	$(PY) $(SCRIPT) image $(TMPDIR)/examples/brgy_hex_spiral_r12.csv --points $(TMPDIR)/examples/hex_spiral.geom.csv --out example/hex-spiral-brgy.svg --cell 5
	$(PY) $(SCRIPT) geometry --geometry hex --order dist-atan --radius 12 > $(TMPDIR)/examples/hex_distatan.geom.csv
	$(PY) $(SCRIPT) batch-data --points $(TMPDIR)/examples/hex_distatan.geom.csv --colorsets brgy --out-dir $(TMPDIR)/examples >/dev/null
	$(PY) $(SCRIPT) image $(TMPDIR)/examples/brgy_hex_dist-atan_r12.csv --points $(TMPDIR)/examples/hex_distatan.geom.csv --out example/hex-dist-atan-brgy.svg --cell 5
