# ABA Sparse/Narrow Propagator Engine Workstream

Status: executable.

## Literal Goal

Finish the sparse/narrow ABA hard-class fix by adding a second native engine for
the high-cycle rows that the current completion-plus-loop-formula SAT route does
not solve under the 30-second row gate.

The final repository state keeps the current loop-formula solver for
sparse/narrow rows where it is cheap, routes high-cycle sparse/narrow rows to a
bitset-native assumption propagator, preserves all 10 previously solved 10x10
fixture rows, solves at least 6 of the 10 previous timeout rows, and never calls
clingo on this route.

## Evidence Already Established

- The committed sparse/narrow route is structural and not filename-based:
  flat ABA, `max_rule_body_width <= 2`, bounded contrary fan-in/fan-out,
  `assumption_to_atom_ratio <= 0.45`, `assumptions >= 700`, and
  `rule_to_assumption_ratio >= 4.0`.
- The original clingo hot path was removed for the class; current telemetry
  reports `clingo_solver_calls == 0`.
- Current best kept source state after `9ddb563`:
  - targeted tests pass;
  - the 10x10 gate solves 7/20 rows;
  - `clingo_solver_calls == 0`;
  - remaining failure is the metric gate, not semantic tests.
- Rejected experiments:
  - unvalidated fixedpoint returned fast but did not satisfy exact semantics;
  - per-literal loop strengthening regressed 7 solved to 6 solved and was
    reverted;
  - static ranked closure regressed 7 solved to 5 solved and was reverted.
- The current loop-formula solver remains useful for cheap rows but is not the
  right main path for the remaining high-cycle rows.

## Paper Page Anchors

Use these existing page images directly while writing tests and code:

- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-002.png`
  for ABA frameworks, assumptions, contraries, derivability, and attacks.
- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/pngs/page-003.png`
  for conflict-free, admissible, complete, preferred, and stable semantics.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
  for guess `in/out`, support propagation, defeat through contraries, and
  conflict-freeness.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`
  for stable, admissible, complete, and preferred constraints.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-012.png`
  for the stable condition that every out argument is defeated.
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/pngs/page-020.png`
  for preferred saturation/maximality.
- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/pngs/page-008.png`
  and `page-009.png` for PrefSat refinement and termination.
- `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/pngs/page-006.png`
  and `page-007.png` for SAT/no-good refinement and complexity-sensitive
  exact solving.
- `papers/deKleer_1986_AssumptionBasedTMS/pngs/page-001.png` and
  `page-002.png` for bit-vector assumption-context consequence caching.

## Exact Row Targets

Add a focused 5-row fixture for the remaining previous-solved misses plus
controls:

- Miss: `aba|SE-PR|ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba|solved`
- Miss: `aba|SE-ST|ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba|solved`
- Miss: `aba|SE-ST|ABAs/abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba|solved`
- Control: `aba|SE-PR|ABAs/abcgen_c5_atoms150_asms200_mra3_mbs2_cp0.9_ins1.aba|solved`
- Control: `aba|SE-ST|ABAs/abcgen_c7_atoms100_asms100_mra3_mbs2_cp0.9_ins1.aba|solved`

The full final gate remains
`tests/manifests/iccma2025-abcgen-10x10.json`.

## Final State

- Add a bitset-native sparse/narrow propagator engine in
  `src/argumentation/aba_sat.py`.
- The propagator owns high-cycle sparse/narrow rows selected by framework shape:
  same sparse/narrow predicate plus `rule_dependency_scc_count >= 4000`.
  Production routing uses static shape only; runtime loop telemetry is a
  test/diagnostic signal, not a production route predicate.
- Stable solving is exact:
  - state is `(forced_in, forced_out, undecided)` over assumption bitmasks;
  - closure is computed by indexed Horn propagation and cached by assumption
    mask;
  - propagation forces out every assumption whose contrary is already derived;
  - conflict is raised when a forced-in assumption is attacked by the current
    closure;
  - impossibility is raised when a forced-out assumption's contrary is not in
    the over-approximate closure of `forced_in | undecided`;
  - branching uses a structural pressure score from contrary-support fan-in and
    closure growth, not filenames;
  - a returned stable witness passes the existing ABA stable validator.
- Preferred solving is exact:
  - first return a validated stable witness because stable extensions are
    preferred under the cited ABA/Dung semantics;
  - when no stable witness exists, run bitset admissible branch-and-bound;
  - admissible candidates are conflict-free and defend against attacks from
    undefeated assumptions per Lehtonen page 026;
  - subset maximality is proved by the same branch-and-bound search before
    returning;
  - no grounded/fixedpoint result is returned unless it validates as preferred.
- Current loop-formula SAT remains available for sparse/narrow rows outside the
  high-cycle propagator route.
- Native telemetry reports:
  - `native_sparse_narrow_engine`;
  - `native_sparse_narrow_solver_checks`;
  - `native_sparse_narrow_branch_nodes`;
  - `native_sparse_narrow_closure_checks`;
  - `native_sparse_narrow_cache_hits`;
  - `native_sparse_narrow_pruned_conflicts`;
  - `native_sparse_narrow_pruned_unattackable_out`;
  - `native_sparse_narrow_validated_witnesses`;
  - `clingo_solver_calls == 0`.

## Owned Paths

- `src/argumentation/aba_route_policy.py`
- `src/argumentation/aba_sat.py`
- `src/argumentation/aba_telemetry.py`
- `src/argumentation/solver.py`
- `tests/test_aba_sparse_narrow_native_sat.py`
- `tests/test_aba_sparse_narrow_route_contract.py`
- `tests/test_aba_sparse_narrow_propagator.py`
- `tests/manifests/iccma2025-abcgen-sparse-propagator-5.json`
- `tools/run_aba_10x10_fixture.py`
- `workstreams/aba-sparse-narrow-propagator-engine.md`

## Deletion Targets

- Delete any production fallback that sends the high-cycle sparse/narrow route
  to ASP/clingo under `backend="auto"`.
- Delete any production route predicate that inspects `abcgen`, ICCMA year,
  manifest path, basename, filename, archive, row id, or directory name.
- Delete any returned answer path that skips semantic witness validation.
- Delete any unvalidated fixedpoint answer path.
- Delete the use of loop-formula SAT as the main high-cycle sparse/narrow route
  after the propagator route is installed.

## Ordered Execution

1. Start from clean tracked-file `main`. Create
   `exp/aba-sparse-narrow-propagator-engine` from `main` because this is a
   benchmark-gated implementation slice. Promote only a passing final diff back
   to `main`.
2. Add `tests/manifests/iccma2025-abcgen-sparse-propagator-5.json` containing
   exactly the 5 row targets above, copied from the existing 10x10 fixture row
   objects.
3. Add failing operational contracts in
   `tests/test_aba_sparse_narrow_propagator.py`:
   - generated high-SCC sparse/narrow ABA frameworks route to
     `native_sparse_narrow_propagator`;
   - route selection is unchanged by locator metadata and path text;
   - returned telemetry includes the paper page anchors;
   - `clingo_solver_calls == 0`;
   - generated cyclic narrow-rule frameworks report
     `native_sparse_narrow_branch_nodes <= assumptions * 8`;
   - generated cyclic narrow-rule frameworks report
     `native_sparse_narrow_loop_formulas == 0`.
4. Add semantic Hypothesis contracts in the same test file:
   - propagator stable result equals the existing `support_extensions`
     stable oracle on small generated cyclic sparse/narrow frameworks;
   - propagator preferred result is a member of the existing preferred oracle on
     small generated cyclic sparse/narrow frameworks;
   - every returned preferred result is subset-maximal admissible;
   - required assumptions are enforced for both stable and preferred.
5. Update `tools/run_aba_10x10_fixture.py` so it accepts fixture files with any
   positive row count. The current 20-row fixture remains valid. The focused
   command must be:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-sparse-propagator-5.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\sparse-propagator-5.json
```

6. Implement high-cycle structural telemetry in
   `src/argumentation/aba_telemetry.py` or `aba_route_policy.py`:
   - `rule_dependency_scc_count`;
   - `rule_dependency_max_scc_size`;
   - `body_literal_fanout_max`;
   - `closure_probe_max_growth`;
   - no path-derived fields.
7. Implement `native_sparse_narrow_propagator_extension` in
   `src/argumentation/aba_sat.py`:
   - build literal and assumption indexes once;
   - build rule waitlists for body width 0, 1, and 2;
   - cache closures by assumption mask;
   - implement stable propagation/search exactly as specified in Final State;
   - implement preferred stable-first plus admissible branch-and-bound exactly
     as specified in Final State;
   - validate each returned witness before returning.
8. Wire `src/argumentation/solver.py` so high-cycle sparse/narrow
   `single-extension` `stable` and `preferred` tasks use the propagator before
   the loop-formula SAT route and before ASP.
9. Run targeted tests:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_aba_sparse_narrow_propagator.py tests\test_aba_structural_telemetry.py tests\test_aba_native_cnf_prefsat.py tests\test_iccma_runner_timeout_contract.py
```

10. Run the focused 5-row metric gate with a 225-second command timeout:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-sparse-propagator-5.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\sparse-propagator-5.json
```

11. Focused metric gate:
    - all 5 rows solve under 30 seconds;
    - all 5 rows route through `native_sparse_narrow_propagator`;
    - `clingo_solver_calls == 0`;
    - every solved row validates under existing runner validation;
    - no production metadata contains path-derived route fields.
12. Run the full 10x10 gate with a 750-second command timeout:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\sparse-narrow-fix-10x10.json
```

13. Full metric gate:
    - all 20 rows route through native SAT or native propagator;
    - `clingo_solver_calls == 0`;
    - all 10 previous solved rows remain solved under 30 seconds;
    - at most 4 of the 10 previous timeout rows remain timed out;
    - every solved row validates under existing runner validation.
14. Search gates:

```powershell
rg -n -F -- "abcgen" src tools tests
rg -n -F -- "clingo_solver_calls" src tests
rg -n -F -- "native_sparse_narrow_propagator" src tests tools
rg -n -F -- "native_sparse_narrow_fixedpoint" src tests
```

15. Commit each source/test/tool slice atomically with explicit pathspecs. Keep
    generated JSON, logs, profiles, screenshots, and benchmark outputs
    uncommitted.

## Required Completion Claim

Completion can be reported only with:

- the exact workflow used;
- the paper page anchors listed above;
- the passing targeted test command;
- the focused 5-row fixture summary;
- the full 10x10 fixture summary;
- confirmation that production route predicates are structural and not
  ICCMA/filename-based;
- confirmation that generated diagnostics were not committed.
