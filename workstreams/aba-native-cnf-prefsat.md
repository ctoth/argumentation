# ABA Native CNF PrefSat Workstream

Status: executable.

Workflow actually requested: continue the main PySAT-native path while a
separate worker repairs `pypblib`.

## Final State

- Dense flat ABA preferred single-extension solving has a native CNF/PySAT
  PrefSat path that does not call Z3 for the main complete-labelling solver.
- The existing Z3 PrefSat implementation remains available as a named fallback
  for non-native routes and differential tests.
- No dependency is pinned to a local path. The first implementation uses plain
  `python-sat`, without `pypblib`, `aiger`, or PB extras.
- The native path reports deterministic CNF telemetry:
  `native_cnf_variables`, `native_cnf_clauses`,
  `native_cnf_solver_checks`, `native_cnf_candidate_models`,
  `native_cnf_candidate_blocks`, and `native_cnf_z3_main_checks`.
- T1/T3/T5/T6 route decisions are based on ABA shape data, not filenames,
  target IDs, parent directories, or ICCMA year.

## Paper Page Anchors

Before source implementation, reread page images directly:

- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-009.png`
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-010.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-002.png`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/pngs/page-003.png`
- `papers/Thimm_2021_FudgeLight-weightSolverAbstract/pngs/page-002.png`
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png`
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-007.png`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/pngs/page-003.png`

## Owned Paths

- `pyproject.toml`
- `uv.lock`
- `src/argumentation/aba_sat.py`
- `src/argumentation/aba_decomposition.py`
- `tools/aba_shape_benchmark.py`
- `tests/test_aba_real_prefsat_contract.py`
- `tests/test_aba_route_properties.py`
- New focused native CNF tests under `tests/`

## Deletion Targets

- No production deletion in this workstream. This is a backend addition with a
  route switch for the dense preferred shape.
- The optimizer-first Z3 path remains absent; do not reintroduce it.
- Do not add `pypblib`, `python-sat[pblib]`, `python-sat[aiger]`, or local
  dependency pins.

## Ordered Phases

1. Dependency gate:
   - Add plain `python-sat` as an optional/runtime dependency required by the
     native SAT backend.
   - Regenerate `uv.lock` with `uv`.
   - Verify `uv run pytest --version` still works.

2. Contract gate:
   - Add Hypothesis properties for native CNF PrefSat on small flat ABA
     frameworks.
   - Required failing signals before implementation:
     `native_cnf_z3_main_checks == 0`,
     deterministic positive CNF variable/clause counts, and extension equality
     against the existing preferred oracle.

3. CNF encoder:
   - Encode complete-labelling variables for every assumption:
     `in`, `out`, `undec`.
   - Encode exactly-one labelling per assumption using ordinary CNF.
   - Encode closure-derived contrary observations through Tseitin-style CNF
     variables over the existing Horn rule graph.
   - Encode complete-labelling consistency so selected assumptions are not
     attacked by selected assumptions.

4. Native PrefSat loop:
   - Use PySAT incremental solving with ordinary assumptions and permanent
     refinement clauses.
   - Return one preferred extension.
   - Map SAT models back to ABA assumptions and labelling dictionaries.
   - Emit native CNF telemetry.

5. Route gate:
   - Route dense flat preferred ABA rows to the native CNF path by shape.
   - Keep filename/year/manifest identity irrelevant.
   - T8 remains solved+valid.

6. Benchmark gate:
   - Run T1 SAT/SE-PR with 30 second solver cap.
   - If it solves, validate the witness.
   - If it times out, profile it and record the new dominant native-CNF stage.
   - Keep only a measured improvement or a new strictly later bottleneck.

7. Regression gate:
   - Run focused ABA PrefSat, decomposition, route, shape, runner, and
     speedscope tests.

## Required Commands

```powershell
uv run pytest -q tests\test_aba_real_prefsat_contract.py
uv run pytest -q tests\test_aba_decomposed_prefsat_contract.py tests\test_aba_shape_benchmark.py tests\test_aba_route_properties.py
uv run tools\run_aba_hard_bucket.py --target-id T8 --backend sat --subtrack SE-PR --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-native-cnf-t8.json --output-csv data\iccma\2025\runs\aba-native-cnf-t8.csv
uv run tools\run_aba_hard_bucket.py --target-id T1 --backend sat --subtrack SE-PR --timeout-seconds 30 --no-profile --output-json data\iccma\2025\runs\aba-native-cnf-t1.json --output-csv data\iccma\2025\runs\aba-native-cnf-t1.csv
```
