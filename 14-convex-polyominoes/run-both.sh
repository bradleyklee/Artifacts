#!/usr/bin/env bash
# Run both independent enumerators and print one checked sequence.
# Example: ./run-both.sh --max-n 24 --workers 10
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BIN="$ROOT/bin/a181785-linux-amd64"

if [ "$(uname -m)" != "x86_64" ] && [ "$(uname -m)" != "amd64" ]; then
  echo "Bundled executable is Linux x86-64 only; rebuild with ./build.sh on this architecture." >&2
  exit 2
fi
if [ ! -x "$BIN" ]; then
  echo "Missing executable: $BIN" >&2
  echo "Rebuild it with ./build.sh (requires Go 1.23+)." >&2
  exit 2
fi
exec "$BIN" --mode both "$@"
