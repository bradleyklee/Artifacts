# Artifact 16: Go owns production physics; Python only independently post-checks
# emitted exact JSON and renders checked records.
GO ?= go
PYTHON ?= python3
BIN := bin/lattice

.PHONY: help build test scan certs deep-dodecagon check derive audit render index manifest package clean

help:
	@printf '%s\n' \
	  'build            build canonical Go producer' \
	  'test             Go engine regression/parity suite' \
	  'scan             rebuild all committed low-family atlases' \
	  'certs            rebuild public positive full certificates' \
	  'deep-dodecagon   rebuild checked 7,500-batch compact checkpoint' \
	  'check            independent Python replay of all committed records' \
	  'derive           derive ternary CSV/text and symmetry audit' \
	  'audit            verify public claim summaries against checked records' \
	  'render           code-render the two checked vertical Shorts' \
	  'index            rebuild per-family manifests and artifact index' \
	  'manifest         regenerate SHA256SUMS after index' \
	  'package          build portable artifact zip under /mnt/data' \
	  'clean            remove Go binary and generated Short frame folders'

build:
	@mkdir -p bin
	$(GO) build -o $(BIN) ./cmd/lattice

test:
	$(GO) test ./...

scan: build
	@mkdir -p data/square_L2_N4 data/dodecagon_L2_N2 data/dodecagon_L3_N2 data/dodecagon_centered data/24gon_L2_N2 data/octagon_L2_N3
	$(BIN) atlas --model square --L 2 --N 4 --cap 256 --id square_L2_N4_cardinal_lattice --out data/square_L2_N4/atlas.json
	$(BIN) atlas --model dodecagon --L 2 --N 2 --cap 100 --id dodecagon_L2_N2_cardinal_lattice --out data/dodecagon_L2_N2/atlas.json
	$(BIN) atlas --model dodecagon --L 3 --N 2 --cap 100 --id dodecagon_L3_N2_cardinal_lattice --out data/dodecagon_L3_N2/atlas.json
	$(BIN) centered-atlas --model dodecagon --L 2 --cap 500 --id dodecagon_centered_all_faces --out data/dodecagon_centered/atlas_all_faces_cap500.json
	$(BIN) centered-atlas --model dodecagon --L 2 --cap 500 --offcardinal-only --id dodecagon_centered_offcardinal_faces --out data/dodecagon_centered/atlas_offcardinal_cap500.json
	$(BIN) atlas --model 24gon --L 2 --N 2 --cap 100 --id 24gon_L2_N2_cardinal_lattice --out data/24gon_L2_N2/atlas.json
	$(BIN) atlas --model octagon --L 2 --N 3 --cap 256 --id octagon_L2_N3_cardinal_lattice --out data/octagon_L2_N3/atlas.json

certs: build
	@mkdir -p data/dodecagon_centered/certificates data/24gon_L2_N2/certificates
	$(BIN) cert-centered --model dodecagon --L 2 --face 1 --va E --vb N --cap 500 --id centered_dodecagon_f1_EN_cap500 --out data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap500.json
	$(BIN) cert-centered --model dodecagon --L 2 --face 1 --va E --vb N --cap 2000 --id centered_dodecagon_f1_EN_cap2000 --out data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap2000.json
	$(BIN) cert-centered-reverse-stem --model dodecagon --L 2 --face 1 --va E --vb N --cap 16 --id centered_dodecagon_f1_EN_reverse_stem --out data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_reverse_stem.json
	$(BIN) cert-lattice --model 24gon --L 2 --sites 0,1 --velocities E,S --cap 100 --id 24gon_L2_N2_class_A_ES_cap100 --out data/24gon_L2_N2/certificates/24gon_L2_N2_class_A_ES_cap100.json
	$(BIN) cert-lattice --model 24gon --L 2 --sites 0,1 --velocities W,N --cap 100 --id 24gon_L2_N2_class_B_WN_cap100 --out data/24gon_L2_N2/certificates/24gon_L2_N2_class_B_WN_cap100.json

deep-dodecagon: build
	$(BIN) checkpoint-centered --model dodecagon --L 2 --face 1 --va E --vb N --cap 7500 --id centered_dodecagon_f1_EN_cap7500_compact --out data/dodecagon_centered/centered_dodecagon_f1_EN_cap7500_compact.json

check:
	@mkdir -p check
	$(PYTHON) scripts/postcheck_go.py data/square_L2_N4/atlas.json --out check/square_L2_N4.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_L2_N2/atlas.json --out check/dodecagon_L2_N2.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_L3_N2/atlas.json --out check/dodecagon_L3_N2.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/atlas_all_faces_cap500.json --out check/dodecagon_centered_all_faces.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/atlas_offcardinal_cap500.json --out check/dodecagon_centered_offcardinal.python.json
	$(PYTHON) scripts/postcheck_go.py data/24gon_L2_N2/atlas.json --out check/24gon_L2_N2.python.json
	$(PYTHON) scripts/postcheck_go.py data/octagon_L2_N3/atlas.json --out check/octagon_L2_N3.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap500.json --out check/centered_dodecagon_f1_EN_cap500.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_cap2000.json --out check/centered_dodecagon_f1_EN_cap2000.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/certificates/centered_dodecagon_f1_EN_reverse_stem.json --out check/centered_dodecagon_f1_EN_reverse_stem.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/centered_dodecagon_f1_EN_cap4000_compact.json --out check/centered_dodecagon_f1_EN_cap4000_compact.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/centered_dodecagon_f1_EN_cap6000_compact.json --out check/centered_dodecagon_f1_EN_cap6000_compact.python.json
	$(PYTHON) scripts/postcheck_go.py data/dodecagon_centered/centered_dodecagon_f1_EN_cap7500_compact.json --out check/centered_dodecagon_f1_EN_cap7500_compact.python.json
	$(PYTHON) scripts/postcheck_go.py data/24gon_L2_N2/certificates/24gon_L2_N2_class_A_ES_cap100.json --out check/24gon_L2_N2_class_A_ES_cap100.python.json
	$(PYTHON) scripts/postcheck_go.py data/24gon_L2_N2/certificates/24gon_L2_N2_class_B_WN_cap100.json --out check/24gon_L2_N2_class_B_WN_cap100.python.json

derive:
	$(PYTHON) scripts/derive_sequences_and_symmetry.py

audit: derive
	$(PYTHON) scripts/audit_claims.py

render:
	$(PYTHON) scripts/render_shorts.py

index:
	$(PYTHON) scripts/build_index.py

manifest:
	@rm -f SHA256SUMS
	@find . -type f ! -name SHA256SUMS ! -path './bin/*' ! -path '*/__pycache__/*' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > SHA256SUMS

package: index manifest
	cd /mnt/data && rm -f artifact-16-lattice-chaos_20260629.zip && zip -qr artifact-16-lattice-chaos_20260629.zip artifact-16-lattice-chaos -x 'artifact-16-lattice-chaos/bin/*' 'artifact-16-lattice-chaos/**/__pycache__/*'
	@ls -lh /mnt/data/artifact-16-lattice-chaos_20260629.zip

clean:
	rm -rf bin renders/shorts/frames_dodecagon_lexmin renders/shorts/frames_24gon_two_classes
