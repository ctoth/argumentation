# ICCMA 2023 ABA-600 Stable SAT Route

Date: 2026-07-11

Status: in progress; baseline and profiler evidence recorded before the route experiment.

Experiment branch: `exp/iccma2023-aba-600-stable-sat-route`

Hypothesis: the existing direct SAT stable-extension backend will solve the ICCMA 2023 `aba_2000_0.3_10_10_0.aba` `SE-ST` row within the five-second worker budget because the current automatic ASP route spends its dominant time inside one Clingo solve call.

Single variable: select `backend=sat` instead of the current `backend=auto` route, which selects the ASP/Clingo backend for this framework shape. Do not change encodings, preprocessing, solver options, or timeout.

Baseline:
- Branch/commit: `main` with production solver code at `84cbb04`.
- Focused command: `uv run tools\iccma2025_run_native.py --root data\iccma\2023 --backend auto --max-af-arguments 0 --max-aba-assumptions 1000000 --timeout-seconds 5 --only-instance benchmarks/aba/aba_2000_0.3_10_10_0.aba --only-subtrack SE-ST --jobs 1 --label main-84cbb04-aba-2000-row0-serial`.
- Result: `timeout>5.0` in the serial two-row baseline; the paired `SE-PR` row also timed out.
- Full-family screen: 715 solved and 85 timeout across 800 ABA `SE-PR`/`SE-ST` rows. The parallel screen selected targets only; its elapsed times are not baseline timings.
- Telemetry: automatic routing selects Clingo multishot; this stable task makes one solver call.

Instrumentation contract:
- Profiler command: the same row under `--profile-workers-format raw --profile-worker-subtrack SE-ST`.
- Profile: `data/iccma/2023/profiles/main-84cbb04-aba-2000-row0-sest/aba-SE-ST-aba_2000_0.3_10_10_0.aba-025953348c53.raw.txt`.
- Dominant baseline cost: 302 principal samples inside `clingo.Control.solve`, compared with 38 in grounding and 30 in program addition.
- The profile is attached to the real runner worker through the repository's `py-spy --subprocesses` hook.

Fast contracts:
- `uv run pytest -q tests/structured/aba/test_aba_sparse_narrow_route_contract.py tests/test_performance_contracts.py tests/solving/test_solver_availability.py`
- Before any promoted automatic-route change, add a deterministic route contract for the exact structural predicate being changed; it must fail on the baseline route and pass only when this measured shape selects SAT.

Metric gate:
- Command: identical serial row, `--backend sat`, five-second timeout, `jobs=1`.
- Positive gate: status `solved`, semantically valid stable witness, elapsed below five seconds, and solver metadata identifying the SAT owner.
- Promotion is not justified by this one row alone; a positive focused result advances to a frozen validation slice containing neighboring solved and timeout rows.

Failure-analysis gate:
- If SAT times out or misses the budget, profile the SAT worker on this exact row before selecting another target.
- Compare the dominant SAT cost to the Clingo baseline and record whether the bottleneck moved, shrank, or stayed unchanged.

Kill criteria:
- Abandon this route hypothesis if SAT times out and its real-worker profile does not show a smaller or meaningfully different bottleneck.
- Do not tune SAT options or alter an encoding within this experiment.

Experiment result:
- Pending.

Failure analysis:
- Pending if the metric gate misses.

Outcome: pending.

Decision: pending.

Generated diagnostics:
- ICCMA run JSON/CSV/summary/event logs and raw profiles under `data/iccma/2023/`; these generated files are not committed.
