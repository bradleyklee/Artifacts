BIN := bin/a181785-linux-amd64
N ?= 24
W ?= 10

.PHONY: build test both fast complete clean

build:
	./build.sh

test: build
	./$(BIN) --mode test

# One authoritative sequence; exits nonzero at the first disagreement.
both: build
	./$(BIN) --mode both --max-n $(N) --workers $(W)

fast: build
	./$(BIN) --mode fast --max-n $(N) --workers $(W)

complete: build
	./$(BIN) --mode complete --max-n $(N) --workers $(W)

clean:
	rm -f $(BIN)
