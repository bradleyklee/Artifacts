#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "usage: $0 Q [extra generate.py arguments...]" >&2
  exit 2
fi
Q="$1"
shift
exec /usr/bin/time -v python generate.py "$Q" "$@"
