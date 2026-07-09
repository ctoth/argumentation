#!/usr/bin/env bash
# Run the 4 abcgen frontier cells (t120) + the c25 microbench for the
# exp/abcgen-arc-acyc experiment. Usage:
#   run_abcgen_arc_acyc_cells.sh <phase> [skip-profile]
# where <phase> is "baseline" or "fixed". Logs to logs/abcgen-arc-acyc-<phase>-*.
set -u
PHASE="${1:?phase (baseline|fixed) required}"
SKIP_PROFILE="${2:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
ABAS=data/iccma/2025/extracted/instances/ABAs

run_cell() {
  local subtrack="$1" instance="$2" tag="$3"
  local label="abcgen-arc-acyc-$PHASE-$tag"
  local log="logs/$label.log"
  echo "=== $label start $(date -u +%H:%M:%S)" | tee -a "logs/abcgen-arc-acyc-$PHASE-driver.log"
  uv run tools/iccma2025_run_native.py --backend auto \
    --only-instance "ABAs/$instance" \
    --only-subtrack "$subtrack" \
    --max-aba-assumptions 2147483647 \
    --timeout-seconds 120 \
    --label "$label" \
    --event-log-path "logs/$label-events.jsonl" \
    >"$log" 2>&1
  echo "=== $label exit=$? end $(date -u +%H:%M:%S)" | tee -a "logs/abcgen-arc-acyc-$PHASE-driver.log"
}

if [ "$SKIP_PROFILE" != "skip-profile" ]; then
  echo "=== microbench c25 start $(date -u +%H:%M:%S)" | tee -a "logs/abcgen-arc-acyc-$PHASE-driver.log"
  uv run scripts/profile_abcgen_stable.py \
    "$ABAS/abcgen_c25_atoms25_asms35_mra3_mbs2_cp0.8_ins1.aba" 300 \
    >"logs/abcgen-arc-acyc-$PHASE-profile-c25.log" 2>&1
  echo "=== microbench c25 exit=$? end $(date -u +%H:%M:%S)" | tee -a "logs/abcgen-arc-acyc-$PHASE-driver.log"
fi

run_cell SE-ST abcgen_c25_atoms25_asms35_mra3_mbs2_cp0.8_ins1.aba sest-c25
run_cell SE-ST abcgen_c35_atoms35_asms30_mra3_mbs2_cp0.8_ins2.aba sest-c35
run_cell SE-PR abcgen_c25_atoms25_asms35_mra3_mbs2_cp0.8_ins1.aba sepr-c25
run_cell SE-PR abcgen_c35_atoms35_asms35_mra3_mbs2_cp0.8_ins2.aba sepr-c35

echo "=== ALL DONE $(date -u +%H:%M:%S)" | tee -a "logs/abcgen-arc-acyc-$PHASE-driver.log"
