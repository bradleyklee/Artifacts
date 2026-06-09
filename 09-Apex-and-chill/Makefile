PYTHON ?= python3
ROOT := $(CURDIR)
APEX ?= data/records/best/apex_852_verified_depth57.json

# Clean video defaults. Override at command line, e.g. make video TILE=12 WIDTH=1400 HEIGHT=900
WIDTH ?= 1280
HEIGHT ?= 720
TILE ?= 10
SIDEBAR ?= 260
FPS ?= 2

# Search defaults
TRIALS ?= 100
SEARCH_OUT ?= runs/search_mixed
SEEDS ?= data/records/pools/pool_852_unique.jsonl
OP ?= mixed
MOVE ?= 32
ACCEPT ?= 0.65
MUTRATE ?= 0.05
PRINT_EVERY ?= 25

.PHONY: target depict video search smoke clean-video

target:
	$(PYTHON) scripts/generate_target_data.py --root $(ROOT) --model dh12 --level 5

depict:
	$(PYTHON) scripts/depict_record.py $(APEX) --out images/depict_from_make.png

video:
	$(PYTHON) scripts/animate_record.py $(APEX) --root $(ROOT) --target-level 5 \
	  --outdir videos/make_video --mp4 --fps $(FPS) \
	  --width $(WIDTH) --height $(HEIGHT) --tile-size $(TILE) --sidebar-width $(SIDEBAR)

search:
	$(PYTHON) scripts/search.py --root $(ROOT) --seeds $(SEEDS) --outdir $(SEARCH_OUT) \
	  --op $(OP) --trials $(TRIALS) --target-level 5 --move-count $(MOVE) \
	  --accept-bias $(ACCEPT) --mutate-rate $(MUTRATE) --print-every $(PRINT_EVERY)

smoke: target depict
	$(PYTHON) scripts/search.py --root $(ROOT) --seeds $(SEEDS) --outdir runs/smoke \
	  --op mixed --trials 9 --target-level 5 --max-depth 20 --print-every 3

clean-video:
	rm -rf videos/make_video
