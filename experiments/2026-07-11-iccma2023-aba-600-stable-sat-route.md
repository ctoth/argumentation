# ICCMA 2023 ABA-600 Stable SAT Route

Date: 2026-07-11

Status: measured on the experiment branch; automatic SAT routing not promoted.

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
- The required ICCMA runner initially rejected `--backend sat`; that earlier capability premise was wrong.
- Instrumentation commit `000ae2c` adds the missing SAT selection surface and a CLI contract without changing solver behavior.
- Metric command: the baseline command with only `--backend sat` and label `exp-aba600-sest-sat-row0`.
- Result: `timeout>5.0`, elapsed `5.023400s`, no witness.
- The SAT route did not pass the focused promotion gate.

Failure analysis:
- Profiler command: the same SAT row with `--profile-workers-format raw --profile-worker-subtrack SE-ST`.
- Profile: `data/iccma/2023/profiles/exp-aba600-row0-sest-sat/aba-SE-ST-aba_2000_0.3_10_10_0.aba-025953348c53.raw.txt`.
- Compared against: the automatic ASP worker profile recorded in the baseline section.
- Dominant cost before: Clingo solving, 302 of 384 principal samples; grounding and program addition accounted for 38 and 30 samples respectively.
- Dominant cost after: ranked-closure constraint construction, 391 of 399 samples inside `_add_ranked_closure_constraints` / `_emit_ranked_closure_constraints`; 27 samples included `Z3_solver_assert`, and the worker did not reach the Z3 solve.
- Interpretation: the bottleneck moved from ASP solver search to Python/Z3 ranked-closure encoding construction and did not shrink enough to meet the gate.
- Next target from evidence: reduce the operational size or construction cost of ranked-closure constraints before reconsidering this SAT route.

Outcome: negative for route selection; useful instrumentation retained.

Decision: abandon automatic SAT-route promotion for this shape. Promote only the runner's SAT selection instrumentation, then begin a separate one-variable ranked-closure construction experiment.

Generated diagnostics:
- ICCMA run JSON/CSV/summary/event logs and raw profiles under `data/iccma/2023/`; these generated files are not committed.
