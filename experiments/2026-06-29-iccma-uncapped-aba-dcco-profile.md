# ICCMA 2025 Uncapped ABA DC-CO Profile

Date: 2026-06-29

Status: diagnostic stocktake on `main`; no solver behavior change promoted.

Experiment branch: `main` (diagnostic-only continuation after the ABA query
sidecar fix).

Evidence commits:
- `5ea0c34` runner correctness fix for ABA decision query sidecars.
- Pending commit: raw collapsed profile summary instrumentation and this record.

Hypothesis: The stopped uncapped ICCMA 2025 run should identify whether the
early ABA DC-CO timeouts are caused by solver search, ABA support construction,
or runner/query plumbing.

Single variable: No solver variable was changed. The diagnostic variable was
targeted replay and profiling of one timed-out DC-CO row against one solved
same-size DC-CO control.

Baseline:
- Command: `uv run tools\iccma2025_run_native.py --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 5 --label full-uncapped-auto-t5-20260629-after-queryfix-instrumented --event-log-path data\iccma\2025\runs\full-uncapped-auto-t5-20260629-after-queryfix-instrumented-events.jsonl`
- Result: stopped at 669/7394 rows, all ABA. Status counts were 497 solved and
  172 timeout. DC-CO contributed 83 solved and 29 timeout rows.
- Telemetry: no `missing_query` rows and no non-timeout errors after the query
  sidecar fix.

Targeted rows:
- Timeout row: `ABAs/aba_2000_0.3_10_5_6.aba`, `DC-CO`, 2000 atoms,
  600 assumptions, 7644 rules.
- Solved control: `ABAs/aba_2000_0.3_5_10_8.aba`, `DC-CO`, same 2000/600
  shape; solved at the 5 second gate.

Experiment result:
- Timeout command: `uv run tools\iccma_run_selected.py data\iccma\2025\metadata\iccma2025-main.csv --instance ABAs/aba_2000_0.3_10_5_6.aba --subtrack DC-CO --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 5`
- Timeout result: `{"error": null, "reason": "timeout>5.0", "status": "timeout"}`.
- Control command: `uv run tools\iccma_run_selected.py data\iccma\2025\metadata\iccma2025-main.csv --instance ABAs/aba_2000_0.3_5_10_8.aba --subtrack DC-CO --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 5`
- Control result: solved with `answer=true` and `witness_size=412`.

Failure analysis:
- Profiler or operational command: `uv run tools\iccma2025_run_native.py --backend auto --max-af-arguments -1 --max-aba-assumptions 2147483647 --timeout-seconds 15 --label targeted-20260629-dcco-timeout-profile --event-log-path data\iccma\2025\runs\targeted-20260629-dcco\timeout-runner-profile-events.jsonl --only-instance ABAs/aba_2000_0.3_10_5_6.aba --only-subtrack DC-CO --profile-workers-dir data\iccma\2025\profiles\targeted-20260629-dcco\timeout-runner --profile-workers-format raw --profile-worker-subtrack DC-CO`
- Compared against: `data\iccma\2025\profiles\targeted-20260629-dcco\control-aba_2000_0.3_5_10_8-dcco-t15.raw.txt`.
- Dominant cost before source optimization: the timeout profile has 1399 raw
  samples; 1297 samples, or about 92.7%, are exclusive in
  `argumentation\structured\aba\aba_support_model.py` minimal-support insertion
  and subset filtering (`_add_minimal_support` line 153/155 and its generator).
- Control profile: the solved control has only 20 total samples, with no
  comparable long-running hot frame.
- Interpretation: the hot path is not runner overhead and not a completed Z3
  search. The timeout spends almost all sampled time building/minimizing ABA
  supports for `sat_support_extension`.
- Next target from evidence: add an operational contract for bounded
  minimal-support growth or support-construction telemetry, then test a single
  optimization of `_minimal_supports` / `_add_minimal_support` in
  `src\argumentation\structured\aba\aba_support_model.py`.

Fast contracts:
- `uv run pytest tests\interop\test_iccma_runner.py -q`
- `uv run pytest tests\test_collapsed_profile_summary.py -q`

Metric gate:
- Correctness gate for the stopped baseline: no `missing_query` rows after
  `5ea0c34`.
- Diagnostic gate for the timeout row: py-spy attached to the real worker and
  produced a raw collapsed profile before the 15 second row timeout.

Outcome: valid diagnostic.

Decision: do not tune DC-CO through routing or Z3 yet. The next kept source slice
should target support-model minimality checks, but only after an executable
operational contract records support-growth shape before the full ICCMA gate.

Generated diagnostics:
- `data\iccma\2025\runs\full-uncapped-auto-t5-20260629-after-queryfix-instrumented-events.jsonl`
- `data\iccma\2025\runs\targeted-20260629-dcco\timeout-aba_2000_0.3_10_5_6-dcco-t5.json`
- `data\iccma\2025\runs\targeted-20260629-dcco\control-aba_2000_0.3_5_10_8-dcco-t5.json`
- `data\iccma\2025\runs\targeted-20260629-dcco\timeout-raw-profile-summary.json`
- `data\iccma\2025\runs\targeted-20260629-dcco\control-raw-profile-summary.json`
- `data\iccma\2025\profiles\targeted-20260629-dcco\timeout-runner\aba-DC-CO-aba_2000_0.3_10_5_6.aba-8fdcb921fcd2.raw.txt`
- `data\iccma\2025\profiles\targeted-20260629-dcco\control-aba_2000_0.3_5_10_8-dcco-t15.raw.txt`

These generated diagnostics were not committed; this record captures the
decision-relevant result.
