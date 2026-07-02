#!/usr/bin/env bash
set -euo pipefail
n=355
d=113
whole=$((n / d))
rem=$((n % d))
digits=""
for _ in 1 2 3 4; do
  rem=$((rem * 10))
  digits+=$((rem / d))
  rem=$((rem % d))
done
printf 'hello %s.%s world!\n' "$whole" "$digits"
