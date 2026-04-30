# Solver integration architecture survey — 2026-04-30

## Observed solver surfaces after first implementation slices

- `src/argumentation/solver.py` — `solve_dung_extensions(framework, *, semantics, backend="labelling")` returns `ExtensionSolverSuccess | SolverBackendUnavailable | SolverBackendError`. The native `"labelling"` backend dispatches semantics to `argumentation.dung` functions. Passing `ICCMAAFBackend` is rejected because ICCMA SE-* tasks return one witness, not full extension enumeration.
- `src/argumentation/solver.py` — `solve_dung_single_extension(framework, *, semantics, backend="labelling" | ICCMAAFBackend(...))` returns `SingleExtensionSolverSuccess | SolverBackendUnavailable | SolverBackendError`. The native path returns the first deterministic pure-Python extension witness; the explicit `ICCMAAFBackend` object delegates SE-* single-extension queries to `solver_adapters.iccma_af`.
- `src/argumentation/solver.py` — `solve_dung_acceptance(framework, *, semantics, task, query, backend="labelling" | ICCMAAFBackend(...))` handles credulous/skeptical queries. The native path computes witnesses/counterexamples from pure-Python extensions; the ICCMA path delegates DC/DS-* acceptance queries to `solver_adapters.iccma_af`.
- `src/argumentation/sat_encoding.py` — `CNFEncoding` dataclass plus `encode_stable_extensions` and `stable_extensions_from_encoding` (brute-force enumeration over all assignments). Stable-only; no preferred/complete/semi-stable encodings.
- `src/argumentation/solver_adapters/iccma_af.py` — subprocess adapter for ICCMA 2023 AF CLI (`-p problem -f path [-a query]`). Result variants: `ICCMASolverSuccess | ICCMASolverUnavailable | ICCMASolverError | ICCMASolverProtocolError`. Provides `solve_af_extensions` (SE-*) and `solve_af_acceptance` (DC/DS-*) with parsing in `parse_iccma_output` (DECISION / SINGLE_EXTENSION kinds, witness validation rules: DC YES witness must contain query, DS NO counterexample must omit query). Only Dung AF currently — no ABA, ADF, SETAF adapters.
- `src/argumentation/solver_adapters/__init__.py` — exposes only `iccma_af`.

## Inconsistencies / asymmetries

- Top-level Dung solver results now preserve unavailable/error outcomes, but `solver_adapters.iccma_af` still has its own ICCMA-specific result hierarchy. The mapping is local to `solver.py`; there is no shared result module yet.
- Backend identification is mixed: native uses the string `"labelling"`, while external ICCMA uses a typed backend object carrying binary path and timeout.
- No unified `solve_*` for non-Dung formalisms (ABA, ADF, SETAF) even though `iccma_io` modules exist for SETAF and ADF (`setaf_io.py`, `adf.py` has its own ICCMA round-trip, `aba.py` ICCMA tests in `test_aba_iccma_io.py`).
- SAT encoding stands alone — neither `solver.py` nor `iccma_af.py` calls into `sat_encoding.py`; brute-force enumeration in `stable_extensions_from_encoding` makes it a reference oracle, not a real SAT path.
- "labelling" backend label is decorative — it's actually the `dung.py` semantics dispatcher, not a labelling-specific algorithm choice.

## Tests pinning current shape

- `tests/test_solver_availability.py` — native extension solving, deleted-Z3 rejection, ICCMA rejection for full enumeration, explicit ICCMA single-extension routing, unavailable/error mapping, native acceptance witnesses/counterexamples, and explicit ICCMA acceptance routing.
- `tests/test_solver_adapters.py` — parsing rules, monkeypatched subprocess invocation, missing-binary, error, protocol-error, plus optional real-binary smoke gated on `ICCMA_AF_SOLVER` env.
- `tests/test_solver_encoding.py` — CNF determinism, conflict + outsider clauses, hypothesis property: encoding round-trip equals `stable_extensions(framework)`.

## Project conventions observed

- Pure Python semantics live in `dung.py`, `aba.py`, `adf.py`, `setaf.py`. No optional native backend currently switches them.
- `iccma.py` / `setaf_io.py` provide format I/O; round-trips are validated against pure Python semantics.
- Result variants use `@dataclass(frozen=True)` unions, no exceptions for protocol/availability failures.

## Open questions / unknowns

- Whether to keep explicit backend objects (`ICCMAAFBackend`) or switch to named backend strings plus side parameters before broadening to ABA/ADF/SETAF. The object design avoids ambiguous strings and carries protocol-specific options, but it makes the public API less uniform.
- Whether to rename `"labelling"` to `"native"` in a deletion-first API change. This would be clearer but is user-facing.
- Which external solver formats are primary for ABA, ADF, and SETAF. Do not claim ICCMA conformance for those until the target edition and parser/writer behavior are pinned against primary sources.
- Whether SAT should become an optional runtime backend through `python-sat` or remain a pure CNF/reference surface.

## Status

Initial Dung solver integration is implemented and tested in:

- `6885bbb` / `d9be3fc`: initial explicit `ICCMAAFBackend` extension routing.
- `89f2043` / `55fd569`: native and ICCMA-backed Dung acceptance routing.
- `6f959c7` / `21e5e8a`: corrected the ICCMA SE-* contract so single-extension witnesses are not presented as full enumeration.

Pure Python semantics in `dung.py` etc. remain the oracle by convention. The next high-value slice is either shared solver result types or the first non-Dung external adapter, preferably ABA because `parse_aba`/`write_aba` already exist and tests already cover official ABA I/O.
