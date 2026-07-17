#!/usr/bin/env bash
# Run the frozen 600s timeout sample, one runner invocation per subtrack,
# --only-track main to avoid the redundant heuristics-track duplicate solve.
set -u
WT="C:/Users/Q/AppData/Local/Temp/claude/C--Users-Q-code-argumentation/e531f1d6-db52-4333-8cee-1726098fa014/scratchpad/census-wt"
DATA_ROOT="C:/Users/Q/code/argumentation/data/iccma/2025"
MANIFEST="$WT/experiments/iccma-census/sample-timeout-600s.json"
LOG="C:/Users/Q/code/argumentation/logs/census-sample-600s-2026-07-17.log"

cd "$WT" || exit 3
echo "=== census sample run START $(date) ===" | tee "$LOG"

SUBTRACKS=$(uv run python -c "import json;m=json.load(open(r'$MANIFEST'));print(' '.join(sorted({e['subtrack'] for e in m['entries']})))" | tr -d '\r')
echo "subtracks: $SUBTRACKS" | tee -a "$LOG"

for ST in $SUBTRACKS; do
  # collect --only-instance args for this subtrack
  mapfile -t INSTS < <(uv run python -c "import json;m=json.load(open(r'$MANIFEST'));[print(e['instance']) for e in m['entries'] if e['subtrack']=='$ST']" | tr -d '\r')
  ARGS=()
  for i in "${INSTS[@]}"; do ARGS+=(--only-instance "$i"); done
  # DC/DS subtracks duplicate the AF solve across main+heuristics tracks; keep
  # main only. SE subtracks are main(af)+aba(aba) with no heuristics dup and the
  # ABA strata live under track "aba", so leave SE unfiltered.
  TRACK_ARGS=()
  case "$ST" in
    DC-*|DS-*) TRACK_ARGS=(--only-track main) ;;
  esac
  echo "=== [$ST] ${#INSTS[@]} instances track_filter='${TRACK_ARGS[*]}' START $(date) ===" | tee -a "$LOG"
  uv run python tools/iccma2025_run_native.py \
    --root "$DATA_ROOT" \
    --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 \
    --timeout-seconds 600 --jobs 4 --no-progress \
    "${TRACK_ARGS[@]}" --only-subtrack "$ST" "${ARGS[@]}" \
    --label "census-600s-$ST" >> "$LOG" 2>&1
  echo "=== [$ST] DONE rc=$? $(date) ===" | tee -a "$LOG"
done
echo "=== census sample run COMPLETE $(date) ===" | tee -a "$LOG"
