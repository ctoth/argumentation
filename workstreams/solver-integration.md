# Solver Integration Workstream

## Goal

Make solver integration a first-class, task-explicit package surface across the
argumentation library. The target architecture is:

- pure-Python semantics remain the executable oracle;
- solver result types are shared across native and external backends;
- single-witness, full-enumeration, and decision tasks are separate result
  contracts;
- external solvers live behind typed subprocess adapters with protocol errors
  preserved;
- every solver-backed answer is differentially checked against native semantics
  on generated small frameworks before any broader conformance claim.

This workstream does not restore the deleted Dung Z3 backend. Dung Z3
enumeration was removed intentionally; solver integration now routes through
explicit adapters and solver-independent encodings rather than a hidden
`backend="auto"` path.

## Current State

- `argumentation.solver` exposes native Dung extension enumeration through
  `solve_dung_extensions`.
- `argumentation.solver` exposes one-extension Dung witness queries through
  `solve_dung_single_extension`.
- `argumentation.solver` exposes Dung credulous/skeptical acceptance through
  `solve_dung_acceptance`.
- `ICCMAAFBackend` can route Dung SE/DC/DS tasks through
  `argumentation.solver_adapters.iccma_af`.
- `solve_dung_extensions` rejects `ICCMAAFBackend`, because ICCMA SE tasks
  return one extension witness, not full extension enumeration.
- `argumentation.solver_adapters.iccma_af` has its own ICCMA-specific result
  union: success, unavailable, process error, protocol error.
- `argumentation.solver` has a separate top-level result union and currently
  maps ICCMA protocol errors into generic backend errors.
- `argumentation.sat_encoding` is stable-only and solver-independent; it is not
  wired to a real SAT backend.
- ABA and ADF I/O exist in `argumentation.iccma`; SETAF I/O exists in
  `argumentation.setaf_io`; none are wired to top-level solver entry points.
- ASPIC+ has deterministic encoding and a backend dispatch function, but only
  the materialized native grounded reference is implemented.

## Paper And Source Inventory Considered

I consulted existing repo notes and `../propstore/papers` notes, descriptions,
and claims. I did not reread page images in this planning slice.

Primary local plan/context:

- `notes/solver-integration-architecture-2026-04-30.md`
- `workstreams/iccma-solver-adapter.md`
- `plans/sota-completeness-and-ecosystem-workstream-2026-04-26.md`
- `plans/follow-on-sota-and-propstore-integration-spec-2026-04-26.md`

Primary paper directories already present in `../propstore/papers`:

- `Järvisalo_2025_ICCMA20235thInternational`
- `Niskanen_2020_ToksiaEfficientAbstractArgumentation`
- `Mahmood_2025_Structure-AwareEncodingsArgumentationProperties`
- `Charwat_2015_MethodsSolvingReasoningProblems`
- `Tang_2025_EncodingArgumentationFrameworksPropositional`
- `Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault`
- `Toni_2014_TutorialAssumption-basedArgumentation`
- `Brewka_2010_AbstractDialecticalFrameworks`
- `Brewka_2013_AbstractDialecticalFrameworksRevisited`
- `Lehtonen_2020_AnswerSetProgrammingApproach`
- `Lehtonen_2024_PreferentialASPIC`
- `Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation`
- `Odekerken_2025_ArgumentativeReasoningASPICIncompleteInformation`
- `Diller_2025_GroundingRule-BasedArgumentationDatalog`

Key planning consequences from those notes:

- ICCMA 2023 covers AF and ABA, introduces compact ICCMA23 formats, and uses
  fuzz/VBS-style cross-validation for solver correctness.
- SAT-based solvers dominate exact AF solving in ICCMA 2023; µ-toksia is the
  implementation-level reference for persistent SAT solving over Dung tasks.
- ASP-based solvers dominate ICCMA 2023 ABA tracks; ASPFORABA and ASPARTIX-DL
  are the practical targets before inventing a package-local ABA solver backend.
- ICCMA 2023 does not include ASPIC+ tracks; ASPIC+ solver claims must be based
  on ASPIC+ ASP/Datalog papers, not on ICCMA AF/ABA results.
- Mahmood 2025 and Tang 2025 are useful for encoding direction, but
  implementation-level Dung SAT work should start from Niskanen 2020 and only
  use newer structural encodings after the basic task contracts are stable.

## Control Rules

- Red/green TDD controls every implementation slice.
- Commit every red test slice before production edits; commit every green
  production slice before the next slice.
- Do not begin a new edit slice while files from the current slice remain
  uncommitted.
- Do not use broad git/index/worktree mutation commands. Commit with explicit
  paths only.
- Pure-Python semantics in `dung.py`, `aba.py`, `adf.py`, `setaf.py`, and
  `aspic_encoding.py` are the oracle for generated small instances.
- External solver success is not evidence of correctness unless the witness,
  answer, or extension set is checked against the native oracle.
- Every external solver adapter must return typed unavailable/process/protocol
  results. Missing binaries, nonzero exits, timeouts, malformed output, and
  unsupported task/semantics combinations must be distinguishable.
- Every solver adapter must preserve raw stdout/stderr for diagnosis.
- No dependency metadata may point to a local path or local repository URL.
- Optional heavy dependencies stay optional. Prefer subprocess adapters for
  external solvers; direct Python solver libraries are allowed only behind
  optional extras and typed unavailable paths.
- Do not claim ICCMA conformance for a formalism until the relevant ICCMA
  edition, input format, task names, and output grammar have been checked
  against primary sources.
- Do not claim paper conformance from notes alone. Before implementing
  paper-sensitive clauses, reread the relevant page images or primary web
  pages and record the page/source range in the red or green commit message.

## Testing Doctrine

Tests are the control surface for this workstream. Red/green means more than
one fixture turning green: every solver behavior must be pinned by deterministic
fixtures, paper/source-derived generated properties, and differential oracle
checks before it is called complete.

Generated properties must be useful, not decorative. A property is useful only
if it encodes one of:

- a definition, proposition, theorem, algorithm invariant, or complexity-neutral
  semantic equivalence from a cited paper after the relevant page-image reread;
- an official protocol rule from an ICCMA report or current competition page;
- an already-implemented native oracle contract that this workstream is wiring
  to a solver backend;
- a documented package boundary invariant, such as unsupported tasks returning
  typed unavailable before subprocess invocation.

Do not add arbitrary graph folklore, "seems plausible" monotonicity, or broad
metamorphic tests unless the named paper/source states the law and its
preconditions. Every generated property must cite the source in the test name or
an adjacent comment.

### Required Test Shapes

Every implementation slice must include:

- at least one deterministic fixture test for the exact bug, protocol behavior,
  or API contract being introduced;
- at least one paper/source-derived Hypothesis property unless the slice is pure
  documentation or a parser branch whose full input space is already covered by
  source-backed fixture/fuzz cases;
- a negative test for the failure mode most likely to cause overclaiming;
- a differential test against the native oracle for every solver success path
  where a native oracle exists.

If a slice cannot reasonably include a useful paper/source-derived Hypothesis
property, the red commit must say why in the test name or adjacent comment.
"The fixture passes" is not enough for solver work. Do not substitute random
properties just to satisfy the rule.

### Shared Strategy Library

Build reusable strategies as soon as two useful properties need the same
generator. Prefer small, bounded strategies that finish quickly under full-suite
runs:

- Dung AFs with 0-6 arguments and generated attack relations.
- Numeric ICCMA AFs with contiguous argument IDs.
- Flat ABA frameworks with tiny languages, acyclic rule sets where needed, and
  generated contraries.
- Small ADFs with bounded acceptance-condition AST depth.
- SETAFs with bounded collective-attack tails and a singleton-tail reduction
  generator.
- Tiny ASPIC+ theories with bounded strict/defeasible rules and premises.
- Protocol-output strings for ICCMA DC/DS/SE outputs, including malformed
  witness lines.

Strategies must generate source-relevant edge cases intentionally: empty
frameworks where the semantics/protocol defines them, self-attacks where the
paper examples or semantics permit them, isolated arguments where the source
states their behavior, duplicate-looking but distinct IDs for parser/protocol
rules, no-extension cases, multiple-extension cases, and unsupported
task/semantics pairs.

### Oracle Properties

For every external or optional backend, generated tests must check the strongest
applicable oracle property. These properties are useful because they are exactly
the solver contract this workstream is implementing:

- enumeration success equals the native extension set;
- single-extension success is either no extension when the native set is empty
  or a member of the native extension set;
- credulous acceptance equals `any(query in extension for extension in native)`;
- skeptical acceptance equals `all(query in extension for extension in native)`
  when the native extension set is non-empty;
- solver certificates are valid native extensions or valid counterexamples;
- unsupported task/semantics combinations return typed unavailable before any
  subprocess invocation.

For partial or approximate semantics, tests must state the weaker oracle
explicitly; do not reuse exact-oracle assertions when the backend intentionally
returns approximate answers.

### Source-Derived Properties

Every formalism-specific solver surface should accumulate generated properties
that come from cited papers, protocol reports, or native correspondence claims.
Examples of acceptable properties:

- ICCMA 2023 output rule: DC accepted output with a certificate must contain
  the query argument; DS rejected output with a counterexample must omit the
  query argument; SE output is one witness or `NO`.
- ICCMA 2023 input-format rule: numeric AF files use declared, in-range,
  contiguous argument IDs.
- Niskanen and Järvisalo 2020 / Dung 1995: SAT-backed stable results satisfy
  conflict-freeness and attack every argument outside the extension.
- Niskanen and Järvisalo 2020: SAT-backed admissible results are conflict-free
  and defend every accepted argument.
- Niskanen and Järvisalo 2020: grounded reasoning is the least fixed point of
  the Dung characteristic operator; any SAT/unit-propagation route must agree
  with the native grounded oracle on generated AFs.
- ICCMA task contract: SE is a single-extension witness task, not full
  enumeration.
- Järvisalo 2025 correctness-verification lesson: solver certificates must be
  independently checked by a reference implementation on fuzzed small inputs.
- Bondarenko 1997 / Toni 2014 flat ABA correspondence: flat ABA solver
  witnesses agree with the native ABA semantics and its AF projection where the
  package claims that projection.
- Brewka and Woltran 2010/2013 ADF reduction: ADF-encoded Dung AFs agree with
  Dung for the implemented semantics.
- SETAF definition: singleton-tail SETAFs reduce to the corresponding Dung AF
  for the semantics implemented by both modules.
- Lehtonen 2020/2024 ASPIC+ ASP encoding: clingo-backed grounded ASPIC+
  conclusions agree with the package's materialized ASPIC-to-Dung grounded
  reference on generated tiny theories satisfying the paper preconditions.

Only encode metamorphic laws that are true for the named semantics and paper
preconditions. If the law needs a precondition, generate only inputs satisfying
that precondition.

### Protocol Fuzzing

Every subprocess adapter must have generated or table-driven malformed-output
tests derived from the official protocol grammar for:

- missing answer line;
- unknown answer token;
- malformed witness prefix;
- non-numeric AF witness item when numeric format is expected;
- witness containing an unknown argument;
- DC `YES` witness missing the query;
- DS `NO` counterexample containing the query;
- SE output with multiple witnesses where only one is allowed;
- nonzero return code with stdout/stderr preserved;
- timeout with enough context to diagnose the command.

Malformed protocol output must produce `SolverProtocolError`, not a generic
process error, not an empty success, and not a raw exception.

### No-Overclaim Tests

Each phase must include tests that make false claims unrepresentable:

- ICCMA SE results must not satisfy enumeration result types.
- Unsupported solver tasks must not invoke subprocesses.
- Missing optional dependencies must not skip into native solving silently.
- A backend that returns a malformed but superficially plausible witness must
  be rejected by certificate verification.
- Docs tests must pin every public claim about solver support and unsupported
  semantics.

### Full-Suite Discipline

Hypothesis settings must be bounded enough for the full suite. If a property is
too expensive, shrink the generator, cap examples, or split the property into a
targeted test file. Do not rely on `deadline=None` and an unbounded generator as
evidence that the suite is stable.

## Target Architecture

### Task Contracts

The package exposes separate task contracts:

- `enumerate_extensions`: returns every extension under a semantics.
- `single_extension`: returns one witness extension or no-extension metadata.
- `acceptance`: returns credulous or skeptical yes/no plus witness or
  counterexample when the backend supplies one.
- `count_extensions`: future task for model-counting and benchmark work.

A backend may support any subset of these tasks. Unsupported task/semantics
pairs return a typed unavailable result before invoking a subprocess.

### Result Types

Move shared solver result objects into a dedicated module, for example
`argumentation.solver_results`:

- `SolverUnavailable`
- `SolverProcessError`
- `SolverProtocolError`
- `ExtensionEnumerationSuccess`
- `SingleExtensionSuccess`
- `AcceptanceSuccess`
- later: `CountSuccess`, `OptimizationSuccess`

Protocol errors must not collapse into generic process errors. A binary that
exits zero but emits malformed output is different from a binary that exits
nonzero.

### Backend Configuration

The current explicit `ICCMAAFBackend` object was useful for the first Dung
slice, but it is not the final broad architecture. Before expanding to
ABA/ADF/SETAF, switch to:

- backend selector strings such as `"native"`, `"iccma"`, `"sat"`, `"clingo"`;
- separate config objects such as `ICCMAConfig(binary, timeout_seconds, ...)`;
- per-formalism capability tables.

This avoids a public type per formalism/backend pair such as
`ICCMAAFBackend`, `ICCMAABABackend`, and `ICCMASETAFBackend`.

### Capability Tables

Every backend declares supported `(formalism, task, semantics)` tuples:

- Native Dung supports enumeration, single-extension, and acceptance for every
  semantics implemented in `dung.py`.
- ICCMA AF supports SE/DC/DS tasks only for task codes present in the selected
  ICCMA edition and adapter.
- ICCMA AF SE tasks are single-extension tasks, not enumeration tasks.
- ICCMA ABA support is limited to the official ABA tasks and semantics that the
  selected edition defines.
- ASPIC+ clingo support is limited to semantics and query types implemented by
  the ASPIC+ encoding program.

Capability checks happen before subprocess invocation.

### Adapters

External adapters are thin:

1. validate capability;
2. serialize the package-native object through the official writer;
3. build the protocol command;
4. run subprocess with timeout;
5. parse output into shared result types;
6. verify solver certificates against the native oracle where feasible.

## Dependency-Sorted Execution Order

1. Phase 0: Baseline and source gates.
2. Phase 1: Shared result types and task contracts.
3. Phase 2: Backend selector/config cleanup.
4. Phase 3: Dung ICCMA adapter hardening.
5. Phase 4: Dung SAT backend and encodings.
6. Phase 5: ABA ICCMA/ASPFORABA adapter.
7. Phase 6: ADF and SETAF external-solver boundaries.
8. Phase 7: ASPIC+ clingo/Datalog backends.
9. Phase 8: Solver differential harness and benchmark workflow.
10. Phase 9: Documentation, release surface, and propstore-facing guidance.

## Phase 0: Baseline And Source Gates

Goal: make the workstream auditable before the next code slice.

Tasks:

- Commit this workstream atomically.
- Run the current targeted solver gate:
  `uv run pytest -q tests/test_solver_availability.py tests/test_solver_adapters.py tests/test_solver_encoding.py`
- Run `uv run pyright src`.
- Run `git diff --check`.
- Audit current Hypothesis settings for solver-adjacent test files and record
  any unbounded or suite-slow properties that could mask regressions.
- Record the current full-suite caveat: a recent full run timed out in
  `tests/test_aspic.py::TestDefeatProperties::test_empty_ordering_still_respects_definition_19_edge_cases`, while that exact test passed alone.
- Before implementation starts, page-image or primary-source gates must be
  opened for:
  - Järvisalo, Lehtonen, and Niskanen 2025 / ICCMA 2023 report sections on
    AF/ABA formats, tasks, output grammar, and correctness verification.
  - Niskanen and Järvisalo 2020 sections on SAT encodings and task-specific
    solving architecture.

Acceptance:

- This file committed.
- No production code changed in this phase.
- Baseline command results recorded in the execution ledger.
- Hypothesis audit note added to the execution ledger before Phase 1 starts.

## Phase 1: Shared Result Types And Task Contracts

Goal: remove duplicated result hierarchies and make overclaiming impossible by
type.

Write set:

- `src/argumentation/solver_results.py`
- `src/argumentation/solver.py`
- `src/argumentation/solver_adapters/iccma_af.py`
- `tests/test_solver_availability.py`
- `tests/test_solver_adapters.py`

TDD slices:

1. Red: tests proving top-level Dung solver and low-level ICCMA adapter use the
   same unavailable/process/protocol result classes.
   Include generated malformed-output cases proving protocol failures are not
   collapsed into process failures.
2. Green: create shared result module and switch both layers to it.
3. Red: malformed ICCMA output must become shared `SolverProtocolError` at both
   adapter and top-level Dung solver surfaces.
   Use table-driven and generated malformed ICCMA outputs.
4. Green: preserve protocol errors distinctly through `argumentation.solver`.
5. Red: result type snapshot tests proving enumeration, single-extension, and
   acceptance successes are separate classes.
   Include a generated AF with multiple native extensions to prove a
   single-extension result cannot be treated as enumeration.
6. Green: remove any remaining path where a single ICCMA SE witness can be
   returned as an enumeration success.

Acceptance:

- `uv run pytest -q tests/test_solver_availability.py tests/test_solver_adapters.py`
- At least one ICCMA-source-derived protocol-output property is present.
- At least one generated multi-extension AF test proves SE is not enumeration.
- `uv run pyright src`
- `git diff --check`

## Phase 2: Backend Selector And Config Cleanup

Goal: settle the public backend API before broadening beyond Dung.

Target architecture:

- Use `backend="native"` for the pure-Python oracle.
- Use `backend="iccma"` plus `iccma=ICCMAConfig(...)` for ICCMA subprocesses.
- Use `backend="sat"` plus optional SAT config for SAT-backed Dung tasks.
- Keep `"labelling"` only if the user explicitly defers the rename. The target
  architecture is `"native"`, not dual names.

TDD slices:

1. Red: `solve_dung_extensions(..., backend="native")` succeeds.
   Include a Dung/Niskanen-source-derived generated AF property showing
   `"native"` enumeration equals direct `dung.py` semantics for stable,
   preferred, complete, and grounded.
2. Green: rename the native dispatch path from `"labelling"` to `"native"` and
   update every caller/test/doc. Delete the `"labelling"` production path unless
   the user explicitly requires compatibility.
3. Red: `solve_dung_single_extension(..., backend="iccma", iccma=ICCMAConfig(...))`
   delegates to the ICCMA adapter.
   Include a negative test proving missing `iccma=` config returns unavailable
   before subprocess invocation.
4. Green: replace `ICCMAAFBackend` with a formalism-neutral `ICCMAConfig`.
5. Red: missing config for `backend="iccma"` returns typed unavailable before
   subprocess invocation.
6. Green: capability/config validation layer.

Acceptance:

- `uv run pytest -q tests/test_solver_availability.py tests/test_solver_adapters.py`
- Native backend property tests cover generated Dung AFs under every native
  semantics exposed through this solver surface, with each property tied to the
  relevant Dung/Niskanen semantic contract.
- Unsupported/misconfigured backend tests assert subprocess is not called.
- README and architecture no longer mention `"labelling"` as a public backend
  unless intentionally deferred.
- `uv run pyright src`
- `git diff --check`

## Phase 3: Dung ICCMA Adapter Hardening

Goal: make AF subprocess solving protocol-accurate and oracle-checked.

Mandatory source gate:

- Reread ICCMA 2023 report pages for AF task names, output grammar, certificate
  requirements, unsupported tasks, and correctness verification.
- Reread current official ICCMA task pages before claiming support for any
  newer edition.

TDD slices:

1. Red: capability tests for each supported Dung `(task, semantics)` pair.
   Generate supported/unsupported `(task, semantics)` combinations and assert
   the capability table is total over them.
2. Green: explicit capability table for ICCMA AF.
3. Red: unsupported task/semantics combinations return unavailable with a
   precise reason and do not invoke subprocess.
4. Green: pre-invocation capability validation.
5. Red: SE witnesses are checked by native semantics before success is returned.
   Generate small AFs and choose witnesses both inside and outside the native
   extension set.
6. Green: witness verifier for single-extension tasks.
7. Red: DC/DS witnesses and counterexamples are checked against native
   semantics, not only query membership.
   Generate AF/query pairs and deliberately malformed certificates.
8. Green: decision certificate verifier.
9. Red: optional real solver smoke tests support custom binary path and
   skip cleanly when unavailable.
10. Green: real-solver smoke harness remains opt-in and path-free.

Acceptance:

- `uv run pytest -q tests/test_solver_adapters.py tests/test_solver_availability.py tests/test_iccma.py`
- Hypothesis certificate-verification properties cover SE, DC, and DS tasks on
  generated small Dung AFs.
- Protocol-fuzz tests cover malformed stdout and preserve stdout/stderr.
- Optional `ICCMA_AF_SOLVER` smoke test passes when a compatible solver is on
  PATH.
- No claim of full enumeration via ICCMA SE tasks.

## Phase 4: Dung SAT Backend And Encodings

Goal: make package-native SAT solving real rather than a stable-only CNF demo.

Mandatory page-image gate:

- Reread Niskanen and Järvisalo 2020 pages containing SAT variables, conflict
  free, admissible, stable, complete, preferred, semi-stable, stage, grounded,
  and ideal encodings.
- Reread Mahmood 2025 or Tang 2025 only for the slices that use their specific
  structural or propositional encoding claims.

TDD slices:

1. Red: shared SAT result type returns unavailable when optional SAT backend is
   not installed.
2. Green: SAT backend config and optional dependency boundary.
3. Red/green per semantics:
   - admissible;
   - complete;
   - stable;
   - grounded;
   - preferred;
   - semi-stable;
   - stage;
   - ideal.
   Each semantics starts with a paper-derived generated property comparing the
   encoding or SAT-derived result to the native `dung.py` oracle on small AFs.
4. Red: acceptance tasks reduce to SAT by adding query/negated-query
   constraints and agree with native semantics on generated small AFs.
5. Green: acceptance reduction.
6. Red: enumeration uses blocking clauses and agrees with native enumeration
   on generated small AFs.
7. Green: enumeration loop.

Acceptance:

- `uv run pytest -q tests/test_solver_encoding.py tests/test_solver_availability.py tests/test_dung.py`
- SAT backend unavailable path is typed and deterministic without the optional
  dependency.
- Every SAT success is differential-tested against native semantics with
  Hypothesis-generated AFs.
- Renaming-invariance properties cover every SAT-supported semantics.

## Phase 5: ABA ICCMA And ASPFORABA Adapter

Goal: add the first non-Dung external solver path using the formalism ICCMA
2023 actually covers.

Mandatory source gates:

- Reread ICCMA 2023 ABA format/task/output pages.
- Reread Bondarenko 1997 and Toni 2014 only for native ABA semantic details
  needed to verify solver certificates.
- Reread ASPFORABA documentation or primary source before naming an adapter
  `aspforaba`.

TDD slices:

1. Red: `solve_aba_single_extension(..., backend="native")` returns a native
   witness under supported ABA semantics.
   Include generated flat ABA frameworks and assert the witness belongs to the
   native ABA extension set.
2. Green: top-level ABA single-extension solver surface.
3. Red: `solve_aba_acceptance(..., backend="native")` returns credulous and
   skeptical answers with witnesses/counterexamples.
   Include generated ABA/query pairs and compare answers to native extension
   quantification.
4. Green: native ABA acceptance surface.
5. Red: ICCMA ABA subprocess adapter writes official ABA input and parses
   SE/DC/DS output according to ICCMA 2023.
   Add protocol-fuzz tests for ABA output before subprocess implementation.
6. Green: `argumentation.solver_adapters.iccma_aba`.
7. Red: ICCMA ABA witnesses are verified against native ABA semantics on small
   frameworks.
8. Green: certificate verifier.
9. Red: optional ASPFORABA smoke test gated by environment variable.
10. Green: adapter or documented unavailable result if no stable invocation
    contract is available.

Acceptance:

- `uv run pytest -q tests/test_aba.py tests/test_aba_iccma_io.py tests/test_solver_adapters.py`
- Generated flat ABA properties cover native witness validity, acceptance
  answers, and parser/writer round trips.
- Malformed ABA solver output returns protocol errors, not raw exceptions.
- Optional `ICCMA_ABA_SOLVER` or `ASPFORABA_SOLVER` smoke test skips cleanly
  without a binary.

## Phase 6: ADF And SETAF External-Solver Boundaries

Goal: decide and implement only externally grounded solver hooks for ADF and
SETAF.

Mandatory source gates:

- For ADF: reread Brewka 2010/2013 pages for semantics, plus the target solver
  or format primary source. Do not assume ICCMA coverage unless confirmed.
- For SETAF: reread the official source for the selected SETAF/collective-attack
  solver format. Do not call package-local `p setaf` an ICCMA format.

TDD slices:

1. Red: capability table says ADF/SETAF external solver support is unavailable
   unless a source-backed adapter exists.
   Generate representative ADF/SETAF inputs and assert unavailable is returned
   before subprocess invocation.
2. Green: explicit unavailable surfaces with precise reasons.
3. If a source-backed ADF solver format is selected, add parser/writer fixture
   tests before adapter code.
   Add generated ADF-encoded-Dung round-trip/differential properties first.
4. If a source-backed SETAF solver format is selected, add parser/writer fixture
   tests before adapter code.
   Add singleton-tail reduction properties first.
5. Add external subprocess adapters only after official fixture and native
   oracle checks exist.

Acceptance:

- No docs or APIs claim external ADF/SETAF solver conformance without a
  primary-source-backed adapter.
- Native ADF/SETAF semantics remain the oracle for generated small examples.
- Hypothesis properties cover ADF-encoded Dung agreement and SETAF singleton-tail
  reduction for every solver-exposed semantics.

## Phase 7: ASPIC+ Clingo And Datalog Backends

Goal: make ASPIC+ direct solver integration real without routing every query
through materialized AF construction.

Mandatory page-image gates:

- Reread Lehtonen 2020 and Lehtonen 2024 pages defining ASPIC+ ASP fact
  vocabulary, rules, semantics, and preference handling.
- Reread Odekerken 2023/2025 before extending incomplete ASPIC+ solver claims.
- Reread Diller 2025 before adding Datalog grounding claims.

TDD slices:

1. Red: `solve_aspic_with_backend(..., backend="clingo")` invokes a mocked
   clingo subprocess and parses a grounded answer set.
   Include generated malformed answer-set outputs and missing-binary cases.
2. Green: `argumentation.solver_adapters.clingo` subprocess helper with typed
   unavailable/process/protocol results.
3. Red: clingo grounded results agree with `solve_aspic_grounded` on small
   theories.
   Use bounded generated ASPIC+ theories plus deterministic paper/source
   fixtures.
4. Green: wire grounded clingo path.
5. Red: preferred/stable semantics are reported unavailable until the ASP
   program implements them.
6. Green: precise capability table for ASPIC+ clingo.
7. Later red/green slices: add preferred and stable only after paper reread and
   answer-set fixtures.
8. Later red/green slices: add Datalog grounding only after Diller 2025 reread.

Acceptance:

- `uv run pytest -q tests/test_aspic_encodings.py tests/test_aspic.py`
- Missing `clingo` is typed unavailable, not import crash or subprocess leak.
- Generated tiny ASPIC+ theory properties compare clingo-backed grounded answers
  to `solve_aspic_grounded` whenever the mocked/real backend returns success.
- No ICCMA claim is made for ASPIC+.

## Phase 8: Differential Harness And Benchmarks

Goal: scale correctness checks and performance signals without making optional
solvers mandatory.

Mandatory source gates:

- Reread ICCMA 2023 correctness-verification and fuzz/VBS sections.
- Reread benchmark-data documentation already present in `docs/iccma-data.md`
  and `docs/iccma-2025-data.md`.

TDD slices:

1. Red: pytest helper can compare native and external solver answers for a
   generated small AF under a declared task.
2. Green: reusable solver differential helpers.
3. Red: helpers reject comparing enumeration results to single-witness results.
4. Green: task-aware comparison layer.
5. Red: optional benchmark smoke reads a tiny manifest fixture and invokes no
   external solver by default.
6. Green: benchmark harness with environment-gated solver execution.
7. Red: generated solver-comparison matrix covers every registered backend
   capability and reports unsupported combinations explicitly.
8. Green: backend capability matrix helper.

Acceptance:

- `uv run pytest -q tests/test_solver_adapters.py tests/test_solver_availability.py`
- Differential helpers have Hypothesis coverage for generated AFs and flat ABA
  frameworks.
- Task-mismatch comparisons fail with precise assertion messages.
- Benchmark data and native runners remain path-free and CI-safe.

## Phase 9: Documentation And Propstore-Facing Guidance

Goal: document the solver boundary so propstore can consume it without owning
solver policy.

Tasks:

- Update README and architecture with:
  - task contracts;
  - backend selectors and configs;
  - unsupported-task behavior;
  - optional solver environment variables;
  - the distinction between one witness and full enumeration.
- Add docs for solver result types and error handling.
- Add docs tests that fail if README/architecture claim support for a backend,
  task, or formalism not present in the capability table.
- Add propstore-facing guidance: propstore supplies projected frameworks and
  consumes package result objects; argumentation does not know propstore
  identity, storage, merge policy, or provenance.
- Update `CITATIONS.md` if a backend intentionally diverges from a cited paper
  or protocol.

Acceptance:

- `uv run pytest -q tests/test_docs_surface.py`
- Docs tests pin task separation, unsupported-task behavior, and the difference
  between one ICCMA witness and full enumeration.
- `uv run pyright src`
- `git diff --check`

## Completion Criteria

- Shared solver result types are used by top-level solver surfaces and
  subprocess adapters.
- Native, ICCMA, SAT, and clingo backends have explicit capability tables.
- Dung AF external solving supports task-explicit single-extension and
  acceptance paths without pretending to enumerate all extensions.
- Dung SAT backend supports the implemented semantics or returns typed
  unavailable for unimplemented semantics.
- ABA external solving is wired through an official source-backed format and
  checked against native ABA semantics.
- ADF/SETAF surfaces either have source-backed external adapters or precise
  typed unavailable results; no false conformance claims remain.
- ASPIC+ clingo/Datalog support is limited to paper-reread-backed semantics and
  query types.
- Every solver-backed success is differentially tested against pure-Python
  semantics on generated small inputs.
- Optional real-solver smoke tests skip cleanly when binaries are absent and do
  not rely on local path dependency pins.

## Known Traps

- ICCMA SE means single extension, not all extensions.
- A binary on PATH is not evidence of ICCMA conformance.
- Protocol errors are not process errors.
- ASPIC+ is not covered by ICCMA 2023; use ASPIC+ papers for ASPIC+ solver
  claims.
- ABA ICCMA benchmarks in the paper notes were generated from AF translations;
  do not overgeneralize performance claims to natural ABA instances.
- Stable-only CNF encoding is not a general SAT backend.
- Passing tests with missing external binaries proves unavailable paths, not
  solver correctness.

## Execution Ledger

Status as of workstream creation:

- Docs cleanup commit: `ca6471a`.
- Initial Dung ICCMA backend routing commits: `6885bbb`, `d9be3fc`.
- Dung acceptance solver commits: `89f2043`, `55fd569`.
- Single-extension contract correction commits: `6f959c7`, `21e5e8a`.
- Solver architecture note commits: `b0e360e`, `c549535`.
- Architecture caveat fix commit: `f6439c4`.

Verification observed before this workstream:

- `uv run pytest -q tests/test_solver_availability.py tests/test_solver_adapters.py`:
  23 passed, 1 skipped.
- `uv run pytest -q tests/test_docs_surface.py`: 2 passed.
- `uv run pytest -q --timeout=600 -k "not test_empty_ordering_still_respects_definition_19_edge_cases"`:
  604 passed, 1 skipped, 1 deselected.
- `uv run pytest -q tests/test_aspic.py::TestDefeatProperties::test_empty_ordering_still_respects_definition_19_edge_cases --timeout=180`:
  1 passed.
- `uv run pyright src`: 0 errors.
- `git diff --check`: passed.

No page-image reread was performed while drafting this file. Page-image or
primary-source rereads are required by the phase gates above before
paper-sensitive implementation work.

## First Executable Slice

Target: Phase 1, shared result types only.

Write set:

- `src/argumentation/solver_results.py`
- `src/argumentation/solver.py`
- `src/argumentation/solver_adapters/iccma_af.py`
- `tests/test_solver_availability.py`
- `tests/test_solver_adapters.py`
- test helper module if needed for bounded Hypothesis strategies.

Red commit:

- Tests requiring top-level Dung solver and low-level ICCMA adapter to share
  unavailable/process/protocol result classes.
- Tests proving protocol errors remain protocol errors through
  `argumentation.solver`.
- ICCMA-source-derived Hypothesis property generating malformed ICCMA outputs
  that must produce protocol errors.
- ICCMA task-contract Hypothesis property generating small AFs with multiple
  native extensions, proving single-extension solver results cannot satisfy
  enumeration result contracts.

Green commit:

- Add shared result module.
- Replace duplicate top-level and ICCMA-specific unavailable/error/protocol
  classes with shared classes.
- Preserve current success semantics and task separation.

First-slice acceptance:

- `uv run pytest -q tests/test_solver_availability.py tests/test_solver_adapters.py`
- Red/green test set includes at least two Hypothesis properties.
- `uv run pyright src`
- `git diff --check`
