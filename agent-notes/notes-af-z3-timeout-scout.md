# Scout Report: Z3 per-check timeout + failover groundwork

NOTE ON LOCATION: The prompt asked for `reports/af-z3-timeout-scout.md`, but the
active foreman hook blocks all Writes except to `prompts/` and `notes-*.md`
(verified: two Write/Bash attempts to `reports/` were denied with
"Write is allowed only to prompts/ and notes-*.md"). This file is the report in
the only writable location. Also could not run `z3.get_version_string()` (Bash
blocked by the same hook), so the version claim rests on the `pyproject.toml`
pin, not a live check.

## 1. Every Z3 Solver/Optimize creation and `.check()` site under `src/argumentation`

Six modules import/use z3 via `load_z3` (`core/optional_deps.py`).

**`solving/af_sat.py`** — the Dung SAT engine, highest-traffic module:
- `AfSatKernel.__init__`: `self.solver = self.z3.Solver()` at `af_sat.py:110`; `.check()` wrapper at `af_sat.py:309-347` (actual call `af_sat.py:320`, returns `str(result_ref)`).
- Standalone stable-explanation solver: `z3.Solver()` at `af_sat.py:490`, `.check()` at `af_sat.py:522`.
- `_PreferredSkepticalAttackerSolver`: `z3.Solver()` at `af_sat.py:1091`, `.check()` at `af_sat.py:1116` (`find_attacker`).
- Callers of `AfSatKernel.check(...)` in-file: `af_sat.py:443`, `:662`, `:988`, `:1049`, `:1071`.

**`structured/aba/aba_sat.py`** — ABA stable SAT:
- `z3.Solver()` at `aba_sat.py:355`, `:410`, `:1008`, `:1265`, `:1441`.
- `.check()` at `aba_sat.py:371`, `:375`, `:387`, `:423`, `:1121`, `:1275`, `:1452`. All compare against the z3 *constant* `z3.sat` (e.g. `if solver.check() != z3.sat`), not a string.

**`probabilistic/epistemic.py`**:
- `z3.Solver()` at `epistemic.py:587`; results read as strings — `str(solver.check()) == "sat"` at `epistemic.py:537` (`constraints_satisfiable`) and `str(solver.check()) == "unsat"` at `epistemic.py:549` (`constraints_unsatisfiable`).

**`dynamics/optimization.py`**:
- `z3.Optimize()` at `optimization.py:110`; `.check()` at `optimization.py:134`.

**`structured/aba/aba_asp.py`**: imports `load_z3` but is the clingo/ASP CEGAR routing layer; its check traffic is via `aba_sat.support_extensions` and clingo, not a directly held Z3 solver.

## 2. How Z3 is loaded/configured

`core/optional_deps.py:13-24` — `load_z3(feature)` lazily imports `z3`, raising `RuntimeError(f"{feature} requires z3-solver")` on `ImportError`. It sets **no** parameters. Wrapped per-module: `af_sat.py:1643 _load_z3()`, `aba_sat.py:1581 _load_z3()`.

**No timeout or rlimit is set on any Z3 Solver/Optimize object anywhere in the source.** The only `.set(...)` on a z3 object is `optimization.py:111` (`optimizer.set(priority="lex")`) — objective priority, not a budget. Confirmed by a full-tree grep for `set_option|set_param|"timeout"|rlimit|z3.set`: no budget-setting hits.

## 3. Z3 timeout mechanism in this codebase's usage style

- Dependency pin: `pyproject.toml:54` and `:147` require `z3-solver>=4.12` (not exact). **Could not run `z3.get_version_string()`** — Bash blocked by the foreman hook — so only the pin is verified, not the installed build.
- In z3-solver 4.12+, the per-solver `timeout` parameter is **milliseconds** (`solver.set("timeout", ms)`); `rlimit` is a deterministic resource bound. On exhaustion `.check()` returns `unknown` (a `CheckSatResult` whose `str(...)` is `"unknown"`, `!= z3.sat`, `!= z3.unsat`). This matches both result idioms in the code: stringified (`af_sat.py:322`, `epistemic.py:537`) and constant comparison (`aba_sat.py:371`). A budget implementation must satisfy both.

## 4. How callers interpret results today — the correctness hazard

**No SAT caller in `af_sat.py` or `aba_sat.py` handles `unknown`.** Every one collapses non-`sat` into the negative branch:

- `find_stable_extension`: `if problem.check(...) != "sat": return None` (`af_sat.py:443`). Same shape at `af_sat.py:662`, `:988-995`, `:1049-1054`, `:1071`.
- `_PreferredSkepticalAttackerSolver.find_attacker` (`af_sat.py:1114-1140`): sets `extension` only when `result == "sat"`, else `None`.
- `aba_sat.py`: `!= z3.sat` → treated as unsat/absent at `:371`, `:375`, `:387`, `:1121`, `:1275`; loop guards `while solver.check() == z3.sat` at `:423`, `:1452` terminate on unknown.

Downstream this is a **wrong answer, not an error**: `_solve_sat_acceptance` (`solver.py:821-855`) sets `answer = witness is not None` (credulous) and `answer = counterexample is None` (skeptical). A Z3 `unknown` on a hard instance yields credulous→`False`, skeptical→`True`, silently, with no timeout signal.

The sole exception that records the raw value is `explain_stable_unsat`: `status = "sat" if ... else ("unsat" if ... else "unknown")` at `af_sat.py:559` — but it is a diagnostic API, off the acceptance path.

The one place that handles `unknown` correctly today: `dynamics/optimization.py:134-138`: `check = optimizer.check(); if check == z3.unsat: return unsat; if check != z3.sat: return OptimizationResult(status="unknown", trace={"z3_status": str(check)})`. This is the in-codebase template for distinguishing unknown from unsat.

## 5. Where a budget value would come from

- Library SAT entry config `SATConfig` (`solver.py:82-88`): fields are `require_external`, `trace_sink`, `metadata` — **no time-budget field**. SAT finders (`find_stable_extension` etc., `af_sat.py:425`) take `require_in/require_out/trace_sink/metadata/simplify` — **no timeout parameter exists in the SAT library API today.**
- The subprocess wall-clock budget lives on a different config: `ICCMAConfig.timeout_seconds: float = 30.0` (`solver.py:74-79`), used only by external ICCMA binary adapters (`solver.py:1028`, `:1048`, `:1071`, `:1098`).
- Runner flow: `tools/iccma2025_run_native.py` parses `--timeout-seconds` (default 5.0) at `:126`, stores it in `RunConfig.timeout_seconds` (`:87`), enforces it as a **subprocess wall-clock kill** in `run_child` via `process.wait(timeout=timeout_seconds)` → `{"status": "timeout"}` (`:530`, `:564`, `:570`, `:584`). The child worker (`:830-838`) builds `ICCMAConfig(timeout_seconds=float(job["solver_timeout_seconds"]))` and a **bare `SATConfig()` with no budget** (`:837`). For clingo it derives `max(0.1, solver_timeout_seconds - 5.0)` → `clingo_solve_timeout_seconds` (`:1007`, `:1053`). **No analogous derived budget is threaded into Z3.** A hard in-process Z3 check therefore hangs until the outer subprocess wall-clock kill — the gap this mission targets.

## 6. Existing failover patterns to imitate

- **ABA clingo timeout (closest analog):** `ClingoSolveTimeout(TimeoutError)` at `aba_incremental.py:91`; raised at `aba_incremental.py:419` when `handle.wait(self.solve_timeout_seconds)` doesn't finish (`:402-421`, via `ctl.solve(async_=True)`). Caught in `aba_asp.py:309` and `:346`, converted to structured `_failure_result(status="timeout", ...)`. This is the "budget exhausted → distinct timeout status, never a boolean answer" pattern.
- **Result-type vocabulary already present:** `core/solver_results.py` defines `SolverTimeout` (`:58-63`; `backend/problem/message/metadata`) alongside `SolverUnavailable` (`:9-13`), `SolverProcessError`, `SolverProtocolError`. `SolverTimeout` is the natural shape for a Z3-unknown failover.
- **Union types:** `solver.py:96-113` (`ExtensionSolverResult` etc.) list `SolverBackendUnavailable | SolverBackendError | SolverBackendTimeout | SolverProtocolError`, but the SAT success paths only ever construct `AcceptanceSolverSuccess` — a timeout variant is not yet produced by the SAT branch.
- **SolverUnavailable failover:** aliased/used across adapters (`solver.py:64,68`; `solver_adapters/clingo.py:54`; `iccma_aba.py:92`; `iccma_af.py:119`); runner already branches on `result.status == "timeout"` at `solver.py:735`.

## 7. Existing tests around solver dispatch / timeouts

Load-bearing ones among 37 matched files:
- `tests/interop/test_iccma_runner_timeout_contract.py` — asserts `run_or_skip` enforces the worker subprocess timeout (`RunConfig(timeout_seconds=0.05)`, monkeypatches `build_worker_command`).
- `tests/interop/test_iccma_timeout_corpus.py`, `tests/interop/test_iccma_run_timeout_rows.py` — timeout corpus / row shaping.
- `tests/solving/test_solver_adapters.py`, `tests/solving/test_solver_availability.py` — dispatch + backend availability (`SolverUnavailable`).
- `tests/probabilistic/test_epistemic_lp.py` — exercises the `constraints_satisfiable` Z3 path.
- Manifests: `tests/manifests/iccma2025-cap150-timeouts.json`, `iccma2025-cap200-timeouts.json`.

Run commands (project convention): `uv run pytest tests/interop/test_iccma_runner_timeout_contract.py`; `uv run pytest tests/solving`.

**No test exercises an in-process Z3 `unknown`/timeout path** — that behavior is currently untested, consistent with no code producing it.

## Summary of load-bearing facts

1. No Z3 Solver/Optimize object in the source sets `timeout` or `rlimit`; the only budget plumbing is the outer subprocess wall-clock (`iccma2025_run_native.py`) and the clingo async-solve budget (`aba_incremental.py`).
2. `SATConfig` has no time-budget field and the SAT finder API takes no timeout, so no budget can reach an in-process Z3 check.
3. Correctness hazard is concrete: every SAT acceptance caller collapses `unknown` into the negative answer (`!= "sat"` / `!= z3.sat` → `None`/`False`), so a Z3 timeout becomes a silent wrong answer. `_solve_sat_acceptance` (`solver.py:833-853`) mints the wrong boolean.
4. Two in-repo patterns to imitate: `dynamics/optimization.py:134-138` (distinguishes `unknown` from `unsat` in-process) and `aba_incremental.py:91/419` + `aba_asp.py:309/346` (raise a `TimeoutError` subclass → structured `status="timeout"`). `SolverTimeout` (`core/solver_results.py:58`) already exists for the failover shape.

## Could not determine
- Exact installed z3-solver build (Bash blocked by foreman hook); only the `>=4.12` pin is verified. Standard z3 4.12+ semantics (ms `timeout` param, `unknown` on exhaustion) assumed and consistent with existing string/constant result handling.
