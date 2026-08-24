#!/bin/sh
set -eu

# Reproducibly materialize only the authored Beads documentation tree.
# Usage: ./scripts/acquire-pinned-beads-docs.sh DEST COMMIT_SHA

dest=${1:?destination directory required}
ref=${2:?immutable commit SHA required}
repo=https://github.com/gastownhall/beads.git

if [ -e "$dest" ]; then
  echo "refusing existing destination: $dest" >&2
  exit 2
fi

git clone --filter=blob:none --no-checkout "$repo" "$dest"
git -C "$dest" sparse-checkout init --cone
git -C "$dest" sparse-checkout set docs
git -C "$dest" checkout --detach "$ref"
actual=$(git -C "$dest" rev-parse HEAD)
if [ "$actual" != "$ref" ]; then
  echo "checkout mismatch: wanted $ref got $actual" >&2
  exit 2
fi
printf '%s\n' "$actual"
