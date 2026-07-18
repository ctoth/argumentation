#!/usr/bin/env bash
# Build the vendored CaDiCaL 2.2.1 batch binary used by the flat-stable strong
# engine (src/argumentation/structured/aba/aba_sat.py: _find_cadical221_binary).
#
# Output: tools/solvers/cadical-2.2.1/cadical.exe  (or set
# ARGUMENTATION_CADICAL221=<path> to point at an existing binary).
#
# Requires: git, a C++11 compiler (MinGW g++ on Windows), make.
# Evidence for the pinned rev: experiments/2026-07-17-aba-c35-cadical-engine.md
# (rel-2.2.1 / commit 4198d817 solves the c35 eager-arc CNF 25.28s vs glucose4
# >651s) and the D0-FAIL record in
# experiments/2026-07-18-aba-cadical-engine-prod.md (pysat cadical195 does NOT
# reproduce the win).
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
out_dir="$repo_root/tools/solvers/cadical-2.2.1"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git clone --depth 1 --branch rel-2.2.1 https://github.com/arminbiere/cadical "$work/cadical"
cd "$work/cadical"
./configure
make -j"$(nproc)"
mkdir -p "$out_dir"
cp build/cadical.exe "$out_dir/cadical.exe" 2>/dev/null || cp build/cadical "$out_dir/cadical.exe"
"$out_dir/cadical.exe" --version
echo "vendored: $out_dir/cadical.exe"
