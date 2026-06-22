#!/usr/bin/env bash
# Rebuild the bundled executable from the included Go source.
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT"
if ! command -v go >/dev/null 2>&1; then
  echo "Go was not found. The bundled Linux x86-64 executable can be run directly with ./run-both.sh." >&2
  exit 2
fi
go version
mkdir -p bin
go build -trimpath -ldflags='-s -w' -o bin/a181785-linux-amd64 ./cmd/a181785
printf 'built %s\n' "$ROOT/bin/a181785-linux-amd64"
