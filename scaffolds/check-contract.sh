#!/usr/bin/env bash
# Verifies the mechanical part of scaffolds/CONTRACT.md for one scaffold directory.
# Usage: scaffolds/check-contract.sh <scaffold-name>
set -u
root="$(cd "$(dirname "$0")" && pwd)"
name="${1:?scaffold name}"
dir="$root/$name"
fail=0
need_file() { [ -e "$dir/$1" ] || { echo "missing: $1"; fail=1; }; }
need_target() { grep -qE "^$1:" "$dir/Makefile" || { echo "missing make target: $1"; fail=1; }; }

[ -d "$dir" ] || { echo "no such scaffold: $dir"; exit 1; }
for f in README.md STACK.md BOOTSTRAP.md Makefile docker-compose.yml Dockerfile .env.example; do need_file "$f"; done
for t in check check-all test test-db test-external e2e migrations-check sync lock up migrate stack down; do need_target "$t"; done
need_file tests/scenarios
need_file tests/persistence/contracts/README.md
grep -q 'PG_HOST_PORT' "$dir/docker-compose.yml" || { echo "compose: PG_HOST_PORT not configurable"; fail=1; }
grep -q 'API_HOST_PORT' "$dir/docker-compose.yml" || { echo "compose: API_HOST_PORT not configurable"; fail=1; }
grep -qE '^\| `check` \|' "$dir/STACK.md" || { echo "STACK.md: no row for check"; fail=1; }

if [ "$fail" -eq 0 ]; then echo "scaffold contract: $name ok"; else echo "scaffold contract: $name FAILED"; fi
exit $fail
