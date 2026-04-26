# SOTA Completeness And Ecosystem Workstream

Date: 2026-04-26

Status: spec; not yet executed.

This workstream picks up after
`plans/follow-on-sota-and-propstore-integration-spec-2026-04-26.md` reported
package Tracks A through D done and propstore Track E integrated. The package
is now a strong formal kernel covering the canonical 1995-2018 line plus a
handful of 2024 surfaces (Popescu and Wallner adapted DP, DF-QuAD, Lehtonen
ASPIC encoding, Odekerken-Borg-Bex incomplete ASPIC). It is not yet SOTA.

The remaining gap is twofold. First, several of the existing surfaces are
self-flagged as adapted or narrow — `probabilistic.exact_dp` is brute-force
asymptotic, `aspic_encoding.solve_aspic_with_backend` only ships the
materialized reference, `sat_encoding` only encodes stable, `iccma` only
parses and writes. These should become the things they advertise. Second,
several SOTA argumentation families are entirely absent: ADFs, ABA, SETAFs,
enforcement, claim-augmented AFs, dynamic/incremental reasoning, approximate
semantics, and epistemic graphs. Adding them puts the library in
ICCMA-class territory and converts propstore's claim-graph reasoning into a
first-class argumentation projection, not a workaround.

This spec is intentionally large. The motivation is **completeness**: when
given a chance to scope down a track to a thin slice, the executing agent is
expected to scope up — pick the surface that another argumentation
researcher would call complete, not the smallest surface that compiles
green.

## Verdict In One Paragraph

The package is good. It is not great. The path from good to great runs
through finishing the things the docstrings already admit are unfinished,
adding the four families of argumentation framework the literature has
moved on to (ADF, ABA, SETAF, CAF), implementing enforcement to close the
revision/enforcement gap, integrating with the ICCMA solver ecosystem so
big problems route to real solvers, and building a property + benchmark
suite that turns "we cite the paper" into "we match the paper". Done well,
the result is a Python package that an argumentation researcher can use
without reaching for ASPforABA, mu-toksia, or the DIAMOND/QADF stack as
externals — the package speaks their formats, runs their semantics, and
agrees with their solvers on shared inputs.

## Control Rules

- Red/green TDD remains the control surface. Each production slice starts
  with a failing test commit and is followed by the smallest green
  implementation commit that passes the target tests.
- Commit after each edit slice. Do not begin another slice while edited
  files in the current repo remain uncommitted.
- Reach up, not down. Whenever a slice could be implemented as a thin
  surface (one query, one semantics, one backend) or as a complete one
  (the family of queries, semantics, or backends a researcher in that
  area expects), choose the complete one. The motivation for this
  workstream is that this package is a serious argumentation library, not
  a pile of demos.
- Read the papers. Each paper-sensitive slice has a mandatory page-image
  reread gate. Existing notes, claim files, or extracted text may guide
  prioritization but are not source of truth. Record which pages were
  reread in the red or green commit message.
- If a paper reread changes the plan, update and commit this workstream
  before continuing implementation.
- Find new papers. The paper list in this spec is a starting point. If
  during execution the agent finds a more current or canonical paper
  on a track topic, prefer it; record the swap in the commit and update
  this workstream.
- Keep the package pure. `argumentation` must not import `propstore`,
  know about propstore storage, or know about Semantic OS identity
  machinery. Heavy or external solvers must live behind extras or typed
  adapters.
- Every backend absence path returns deterministic typed metadata, not
  an import crash. This invariant is already part of the package
  surface (`solve_aspic_with_backend`, `solver.SolverUnsat`) and must
  extend to every new adapter.
- Every milestone acceptance gate includes:
  - `uv run pytest -q`
  - `uv run pyright src`
  - `git diff --check`
  - `git status --short`
- Differential acceptance: every solver-backed surface must agree with a
  pure-Python reference (or with brute-force enumeration for small
  inputs) under property tests. The pure path stays the oracle.

## Cross-Cutting Surface Decisions

Several decisions apply across multiple tracks; recording them once
prevents drift.

- **External-solver dependency.** External solver invocation (ASP,
  clingo, SAT, ICCMA-protocol binaries) lives behind subprocess
  adapters under `argumentation.solver_adapters` (new module). The
  package never imports a solver Python binding directly except for
  `z3-solver`, which is already an extra. Subprocess adapters detect
  the binary on PATH at call time and return typed
  `SolverUnavailable(reason)` results when missing.
- **Result-object idiom.** New semantic surfaces follow the
  `argumentation.solver` result-type style: `SolverSat | SolverUnsat |
  SolverUnknown | SolverUnavailable` plus a typed payload. Surfaces
  that already exist (`PrAFResult`, `ASPICQueryResult`,
  `IncompleteASPICResult`, `Labelling`) are not refactored unless a
  slice in this workstream demands it.
- **Module naming.** New formalism modules follow the existing pattern:
  `argumentation.adf`, `argumentation.aba`, `argumentation.setaf`,
  `argumentation.caf`, `argumentation.enforcement`,
  `argumentation.dynamic`, `argumentation.approximate`,
  `argumentation.epistemic`. Each gets its own test file under
  `tests/`.
- **Generic dispatch.** Where a new formalism has a clear projection
  into an existing one (CAFs into Dung; flat ABA into Dung; SETAFs into
  Dung when collective attacks degenerate), the new module exposes
  both the native semantics and the projection. The generic
  `argumentation.semantics` dispatcher is extended to accept the new
  framework types only after the native semantics are in.
- **ICCMA conformance.** Where a formalism has an ICCMA file format
  (`apx`/`tgf` for AFs, `aba` for ABA, ICCMA SETAF format), the
  module includes a parser and writer in the same file or a sibling
  `*_iccma.py`. The existing `argumentation.iccma` module covers AFs;
  parallel modules cover the others.
- **Property tests are mandatory.** Every track defines lattice or
  inclusion properties that must hold across its semantics (e.g.
  grounded ⊆ ideal ⊆ ⋂preferred for AFs; flat-ABA admissible
  agrees with its AF projection; SETAF admissible reduces to AF
  admissible when all attacks are singleton). Hypothesis-based
  property tests pin these.

## Phase 0: Spec, Paper Gates, And Baseline

Goal: lock in the spec and the test baseline before adding code.

Tasks:

- Commit this file atomically.
- Re-run the full package gate on master to record the baseline:
  `uv run pytest -q --timeout=300` and `uv run pyright src`. Record
  test count and runtime in this file's execution ledger when
  available.
- Add a paper-reading checkpoint convention to the agent's reading
  log: each paper-sensitive slice records the paper title, year, page
  range reread, and what it implemented or intentionally left out.
- Confirm the agent has access to local PDF copies (or web image
  access) of every paper cited in this spec. Where a paper is not
  available, the agent must record the unavailability before
  proceeding to the implementation slice and pick a route that does
  not depend on that specific paper, or escalate.

Acceptance:

- `git diff --check`
- `git status --short`
- New file committed; no other code changes.

## Phase 1: Finish The Self-Confessed Surfaces

Goal: make every "this is currently adapted / narrow / not the full
algorithm" caveat in the codebase either go away or move from caveat
to honest specialization.

Mandatory page-image gates:

- Reread Meier, Niskanen, Mailly 2024 (KR 2024,
  *Advancing Algorithmic Approaches to Probabilistic Argumentation
  under the Constellation Approach*, arXiv 2407.05058) before
  implementing the real exact tree-decomposition DP for PrAFs. This
  paper provides bag-local-state DP for complete-extension probability
  and credulous acceptability under constellation semantics. It is
  the paper to make `exact_dp` honest.
- Reread Lehtonen, Niskanen, Järvisalo 2024 before extending the
  ASPIC+ ASP backend from materialized-reference to a real ASP-driven
  backend.
- Reread Niskanen, Wallner, Järvisalo 2020 (mu-toksia / ICCMA solver
  protocol) before adding preferred / complete / admissible /
  grounded CNF encodings.

Track 1.1: Probabilistic AF tree-decomposition DP, real

Goal: remove `exact_dp`'s "tracks full edge sets, no asymptotic
improvement over brute-force, effective only for treewidth ≤ ~15"
caveat.

TDD slices:

1. Red: bag-local DP table tests for leaf, introduce, forget, and
   join nodes computing complete-extension probability on a tiny
   PrAF.
2. Green: implement bag-local row state and the four nice-TD
   transitions per Meier et al. 2024 Section 4.
3. Red: differential tests vs `exact_enum` on generated PrAFs with
   treewidth ≤ 6 and up to 15 arguments.
4. Green: full nice-TD evaluator wired into `_compute_exact_dp`.
5. Red: tests proving credulous acceptability is exact and matches
   enumeration.
6. Green: extend the DP for credulous acceptance per Meier et al.
   2024 Section 5.
7. Red: tests removing the "no asymptotic improvement" caveat from
   the module docstring (test reads the docstring and asserts it no
   longer contains the warning).
8. Green: rewrite the docstring honestly. Either the new
   implementation is bag-local and the warning leaves, or the slice
   is not done.

Track 1.2: Stage and CF2 SAT/solver backends

Goal: remove "Solver-backed ... is a later workstream item" from
`stage_extensions` and `cf2_extensions`.

TDD slices:

1. Red: SAT encoding tests for stage on small AFs (range-maximal
   conflict-free).
2. Green: stage encoding in `sat_encoding`.
3. Red: encoding-vs-brute differential property tests.
4. Green: stage backend wired into `argumentation.dung.stage_extensions`
   via `backend="z3"`.
5. Red: CF2 encoding tests over SCC-decomposed AFs.
6. Green: CF2 encoding in `sat_encoding` per Gaggl-Woltran 2013
   Section 4 with explicit per-SCC encoding helpers.
7. Red: CF2 backend tests, including AFs with multiple SCCs and
   self-attackers.
8. Green: CF2 Z3 backend wired into `cf2_extensions`.

Track 1.3: Full SAT encodings for the AF semantics

Goal: extend `sat_encoding` from stable-only to admissible / complete
/ grounded / preferred / semi-stable / stage / ideal / CF2.

TDD slices per semantics: encoding red, encoding green, enumeration
red against encoding-derived enumerator, enumeration green. Each
encoding cites a published source (Besnard-Doutre, Caminada, Gaggl-
Woltran, Wallner-Niskanen-Järvisalo). Differential tests compare to
the existing reference path.

Track 1.4: Real ASPIC+ ASP backend

Goal: replace the `unavailable_backend` stub for ASP-driven ASPIC
queries with a clingo subprocess adapter that actually runs the
Lehtonen 2024 fact vocabulary.

TDD slices:

1. Red: subprocess driver tests with a fixture clingo binary or a
   mock subprocess that returns canned answers; covers
   `solve_aspic_with_backend(backend="clingo", semantics="grounded")`.
2. Green: `argumentation.solver_adapters.clingo` subprocess
   driver, fact-emission, and answer-set-parsing.
3. Red: differential tests against `solve_aspic_grounded` on small
   theories where both must agree.
4. Green: wire `solve_aspic_with_backend` to the new driver.
5. Red: tests for preferred and stable semantics via clingo, with
   the encoder extended to emit the relevant program rules.
6. Green: extend `aspic_encoding.encode_aspic_theory` with the
   semantics-program rules per Lehtonen 2024 Section 5-6.

Acceptance for Phase 1:

- `uv run pytest -q tests/test_probabilistic.py
  tests/test_probabilistic_treedecomp.py tests/test_dung.py
  tests/test_sat_encoding.py tests/test_aspic_encoding.py`
- `uv run pyright src`
- All caveats removed from docstrings or honestly retitled to
  describe specialization rather than incompleteness.

## Phase 2: ICCMA External-Solver Ecosystem

Goal: make the package a first-class participant in the ICCMA
solver ecosystem. Talk the protocols, run the solvers, agree on
results.

Mandatory page-image gates:

- Reread Bistarelli, Kotthoff, Lagniez et al. 2025 (the third and
  fourth ICCMA report, AAC 2025) before claiming ICCMA conformance.
- Reread Niskanen, Wallner, Järvisalo 2020 mu-toksia paper before
  implementing the AF subprocess driver.
- Read the ICCMA 2025 track specification at
  argumentationcompetition.org/2025/tracks.html for current
  semantics, queries, and file formats.

Tracks:

Track 2.1: Subprocess drivers for AF solvers

- `argumentation.solver_adapters.iccma_af`: invokes any
  ICCMA-protocol AF solver as a subprocess. Inputs are written via
  `argumentation.iccma.write_af`; outputs are parsed per ICCMA 2023
  output format (`YES`/`NO` for decision queries, witness encoding
  for SE-σ).
- Drivers shipped: mu-toksia (Niskanen 2020), pyglaf (Alviano), and
  any solver discovered via PATH lookup. The driver accepts a custom
  binary path.
- Typed unavailable-backend results for missing binaries.

Track 2.2: ICCMA file formats beyond AF

- `argumentation.iccma_aba`: ICCMA 2023 ABA format parser/writer.
- `argumentation.iccma_setaf`: ICCMA SETAF format parser/writer
  (after Phase 5 lands SETAFs).
- Round-trip property tests for every parser/writer pair.

Track 2.3: Differential test harness

- A pytest plugin that, when configured with a solver binary, runs
  every available semantic query against the package reference and
  compares with the solver. Failures report the divergent input.
- Test fixtures generate random small AFs (Erdős-Rényi, Barabási-
  Albert) for differential coverage.

Track 2.4: Benchmark harness

- `bench/` directory with pytest-benchmark suites.
- Benchmark the auto-router thresholds: validate that
  `_AUTO_BACKEND_MAX_ARGS = 12` and `treewidth_cutoff=12` are
  defensible numbers on contemporary hardware. Adjust if the
  measurement says otherwise.
- Run on the ICCMA 2023 benchmark archive (downloaded once, cached
  under `bench/iccma2023/`) to give the user a real-world signal.

Acceptance for Phase 2:

- `uv run pytest -q tests/test_solver_adapters.py
  tests/test_iccma.py tests/test_iccma_aba.py`
- `uv run pyright src`
- A README section showing how to invoke the package via an
  external solver and how to run the benchmark suite.
- Benchmark harness is *runnable*; the suite numbers themselves
  do not need to land in tests.

## Phase 3: Abstract Dialectical Frameworks

Goal: add Brewka-Strass abstract dialectical frameworks, the strict
generalization of bipolar+ that the SOTA assessment flagged as
gap candidate #2.

Mandatory page-image gates:

- Reread Brewka and Woltran 2010 (KR, original ADF paper).
- Reread Brewka, Strass, Ellmauthaler, Wallner, Woltran 2013
  (IJCAI, *Abstract Dialectical Frameworks Revisited*).
- Reread Linsbichler, Pichler, Spendier 2022 (AI 305,
  *Advanced algorithms for ADFs based on complexity analysis of
  subclasses and SAT solving*) before implementing the SAT-based
  evaluator.
- Reread Keshavarzi-Zafarghandi, Verbrugge, Verheij 2022 (AAC,
  strong admissibility for ADFs) for the strong-admissible
  semantics.

Target package surfaces (`argumentation.adf`):

- `AbstractDialecticalFramework` dataclass: arguments and a mapping
  from each argument to its acceptance condition (a propositional
  formula over its parents). Acceptance conditions represented via a
  small AST (`Var`, `Not`, `And`, `Or`, `Iff`, `Const`).
- Semantics: two-valued model, three-valued admissible, complete,
  preferred, grounded, stable, well-founded, and strong-admissible.
- Bipolar-ADF detection and the simpler algorithm path that
  exploits the bipolar restriction.
- SAT-based evaluator using `argumentation.solver` (Z3 or
  subprocess CNF) for the general case.
- Optional roBDD-backed evaluator (Linsbichler et al. 2022).
- Reductions: Dung AF → ADF (acceptance condition is conjunction
  of negated parents); bipolar AF → ADF.
- ICCMA ADF format parser/writer if there is a published format;
  otherwise document the package-native serialization.

TDD slices: one semantics per slice, each with red property tests
against the Brewka-Strass examples and reductions, green
implementation, then differential tests against Z3 evaluation.

Acceptance for Phase 3:

- `uv run pytest -q tests/test_adf.py`
- `uv run pyright src`
- Property test: ADF-encoded Dung AF agrees with `argumentation.dung`
  on all four core semantics.

## Phase 4: Assumption-Based Argumentation

Goal: add Bondarenko-Kakas-Kowalski-Toni assumption-based
argumentation, the most-cited SOTA framework the library still
lacks. Propstore already has rules and predicates; ABA imports
almost for free at the data-model level.

Mandatory page-image gates:

- Reread Bondarenko, Dung, Kowalski, Toni 1997 (AI 93, original
  ABA paper).
- Reread Toni 2014 (AC, *A tutorial on assumption-based
  argumentation*).
- Reread Cyras, Toni 2016 (KR, *ABA+: assumption-based
  argumentation with preferences*) before adding preferences.
- Reread Lehtonen, Wallner, Järvisalo 2021 (KR, *Reasoning over
  assumption-based argumentation via ASP*) for the ASPforABA
  approach.
- Reread Apostolakis, Toni, Rapberger 2024 (KR, *Abstraction in
  assumption-based argumentation*) for abstraction support.
- Reread Rapberger et al. 2024 (AAAI, *Redefining ABA+ semantics
  via abstract set-to-set attacks*) for the SETAF connection.

Target package surfaces (`argumentation.aba`):

- `ABAFramework`: language, rules (head + body atoms), assumptions,
  contraries function. Flat-ABA invariant checked at construction
  (no rule head is an assumption).
- Argument construction: deduction trees from assumptions.
- Attacks: assumption-on-assumption via contrary derivation.
- Semantics: admissible, complete, preferred, grounded, ideal,
  well-founded, stable.
- Reduction: flat ABA → AF (the Dung-equivalent abstract AF where
  arguments are deduction trees and attacks are derived). Round-
  trip tests prove that semantics agree on the projection.
- ABA+: preference order over assumptions, normal-attack vs
  reverse-attack semantics per Cyras-Toni 2016.
- ASPforABA / ACBAR adapters in
  `argumentation.solver_adapters.aspforaba` /
  `acbar`.
- ICCMA 2023/2025 ABA file format parser/writer in
  `argumentation.iccma_aba`.

TDD slices:

1. Red: ABAFramework construction, deduction tree, contrary attack
   tests on tiny examples from Bondarenko et al. 1997.
2. Green: data model and deduction-tree builder.
3. Red: each ABA semantics on small examples.
4. Green: each ABA semantics. One slice per semantics.
5. Red: flat-ABA → AF reduction round-trip on generated tiny
   frameworks.
6. Green: reduction implementation; reuse `argumentation.dung`
   for extension computation as oracle.
7. Red: ABA+ preference handling on Cyras-Toni 2016 examples.
8. Green: ABA+ semantics with normal/reverse-attack switching.
9. Red: ICCMA 2023 ABA-format round-trip on benchmark fixtures.
10. Green: parser, writer, and ICCMA solver subprocess adapter.

Acceptance for Phase 4:

- `uv run pytest -q tests/test_aba.py tests/test_iccma_aba.py
  tests/test_solver_adapters.py`
- `uv run pyright src`
- Property test: every ABA semantics on a flat ABAF agrees with
  the corresponding AF semantics on the projected AF.
- Differential test (when ASPforABA or ACBAR is on PATH): ABA
  semantics agree with the external solver on ICCMA 2023 ABA
  benchmark fixtures.

## Phase 5: SETAFs (Argumentation With Collective Attacks)

Goal: add Nielsen-Parsons SETAFs and the recent Dvořák-König-
Woltran complexity and algorithm work.

Mandatory page-image gates:

- Reread Nielsen, Parsons 2006 (ArgMAS, original SETAF paper).
- Reread Dvořák, König, Woltran 2024 (JAIR 79, *Principles and
  their computational consequences for argumentation frameworks
  with collective attacks*).
- Reread Dvořák, König, Woltran 2025 (JOAR, *Parameterized
  complexity of abstract argumentation with collective attacks*).
- Reread Flouris, Bikakis 2024 (IJCAI, *Justifying argument
  acceptance with collective attacks: discussions and disputes*).
- Reread the SETAF splitting paper (CEUR-WS Vol-3757 paper3, *Splitting
  argumentation frameworks with collective attacks*).

Target package surfaces (`argumentation.setaf`):

- `SETAF` dataclass: arguments and a set of attack relations where
  each attacker is a set of arguments (`frozenset[str]`) and each
  target is a single argument.
- Semantics: conflict-free, admissible, complete, preferred,
  stable, grounded, semi-stable, stage.
- Reduction: when all attack sets are singletons, agrees with Dung
  AF on the same attacks. Round-trip property tests.
- Splitting algorithm per CEUR-WS 2024 paper.
- ICCMA SETAF format parser/writer.

TDD slices: one semantics per slice with property tests against the
Dung-equivalent restriction and against Dvořák et al. 2024 examples.

Acceptance for Phase 5:

- `uv run pytest -q tests/test_setaf.py tests/test_iccma_setaf.py`
- `uv run pyright src`

## Phase 6: Enforcement

Goal: close the revision/enforcement gap. The library has revision
(Baumann 2015 kernel union, Diller 2015 revise-by-formula) but no
enforcement (Baumann 2012 minimal change). They are dual problems
and propstore needs both.

Mandatory page-image gates:

- Reread Baumann 2012 (ECAI, *What does it take to enforce an
  argument? Minimal change in abstract argumentation*).
- Reread Wallner, Niskanen, Järvisalo 2017 (JAIR 60, *Complexity
  results and algorithms for extension enforcement in abstract
  argumentation*).
- Reread Baumann, Doutre, Mailly, Wallner 2021 (JAL 8(6),
  *Enforcement in formal argumentation*).
- Reread Mailly 2024 (AIC, *Constrained incomplete argumentation
  frameworks: expressiveness, complexity and enforcement*).

Target package surfaces (`argumentation.enforcement`):

- Enforcement variants: strict, non-strict, normal, weak, conserva-
  tive (per Baumann 2012 and Baumann et al. 2021).
- Argument enforcement: make a target argument credulously or
  skeptically accepted by adding/removing arguments and attacks
  with minimal Hamming change.
- Extension enforcement: make a target set of arguments an
  extension under a chosen semantics.
- Algorithms: SAT/MaxSAT encoding per Wallner-Niskanen-Järvisalo
  2017, plus a brute-force reference for small AFs.
- Constrained-incomplete enforcement per Mailly 2024.
- Result type: minimal change set + witness AF + cost.

TDD slices: one variant per slice; brute-force reference oracle for
property tests; MaxSAT subprocess adapter as scale path.

Acceptance for Phase 6:

- `uv run pytest -q tests/test_enforcement.py`
- `uv run pyright src`
- Property: every enforcement result, when applied, makes the
  target accepted/extension under the requested semantics.

## Phase 7: Claim-Augmented Argumentation Frameworks

Goal: add Dvořák-Greßler-Rapberger-Woltran CAFs. This is the
formalism propstore is closest to natively (claims attached to
arguments, multiple arguments per claim, claim-level acceptance).

Mandatory page-image gates:

- Reread Dvořák, Greßler, Rapberger, Woltran 2023 (AI 322,
  *The complexity landscape of claim-augmented argumentation
  frameworks*).
- Reread Dvořák et al. 2020 (KR, *Argumentation semantics under a
  claim-centric view*).
- Reread the IJCAI 2025 *Featured Argumentation Framework: semantics
  and complexity* if it materially extends the CAF surface.

Target package surfaces (`argumentation.caf`):

- `ClaimAugmentedAF`: a Dung AF plus a `claims` mapping from each
  argument to a claim symbol.
- Inherited semantics: take the Dung extensions and project to
  claim sets.
- Claim-level semantics: maximize / minimize / count at the claim
  level rather than the argument level. Per Dvořák et al. 2023:
  inh-σ vs cl-σ for σ in {preferred, naive, stable, semi-stable,
  stage}.
- Concurrence checker: decide whether inherited and claim-level
  agree on a given CAF for a given semantics.
- Reduction: a CAF with bijective `claims` reduces to its Dung AF.
- Generic-dispatch entry: `extensions(caf, semantics=...,
  view="inherited" | "claim_level")`.

TDD slices: data model first, inherited semantics next, claim-
level per semantics, concurrence last. Property tests against
Dvořák et al. 2023 worked examples.

Acceptance for Phase 7:

- `uv run pytest -q tests/test_caf.py`
- `uv run pyright src`

## Phase 8: Dynamic And Incremental Reasoning

Goal: support ICCMA 2025 Dynamic Track conformance. Add an
incremental reasoning API that maintains extension state under
sequences of argument and attack additions and removals.

Mandatory page-image gates:

- Reread the ICCMA 2025 Dynamic Track specification at
  argumentationcompetition.org/2025/tracks.html.
- Reread Greenwood et al. or Alfano-Greco-Parisi 2018 on dynamic
  argumentation and recomputation; pick the most current source.
- Reread Fichte, Hecher, Meier 2024 (JAIR, *Counting complexity
  for reasoning in abstract argumentation*) for treewidth-based
  incremental updates.

Target package surfaces (`argumentation.dynamic`):

- `DynamicArgumentationFramework`: a stateful wrapper around an
  AF that supports `add_argument`, `remove_argument`, `add_attack`,
  `remove_attack`, plus `query_credulous(arg, semantics)` and
  `query_skeptical(arg, semantics)`.
- ICCMA 2025 Dynamic Track API conformance: reads the standardized
  add/del stream, emits the standardized result stream.
- Incremental algorithm: at minimum a recompute-from-scratch
  reference; ideally an incremental algorithm exploiting locality
  per the chosen paper.
- Connects to existing `argumentation.af_revision` for principled
  state transitions.

TDD slices: stream parser red/green; recompute-from-scratch
oracle red/green; incremental algorithm red/green with property
tests proving incremental answers match recompute-from-scratch on
generated update streams.

Acceptance for Phase 8:

- `uv run pytest -q tests/test_dynamic.py`
- `uv run pyright src`
- Differential test against any ICCMA 2025 Dynamic Track solver
  if such a binary is on PATH.

## Phase 9: Approximate And k-Stable Semantics

Goal: support ICCMA 2025 Heuristics Track conformance and modern
approximation work.

Mandatory page-image gates:

- Reread Skiba, Thimm 2024 (KR, *Optimisation and approximation in
  abstract argumentation: the case of k-stable semantics*).
- Reread Thimm 2014 or its current successor on ranking-based
  approximate semantics.
- Reread Kuhlmann, Thimm 2019 (TAFA, *Using graph convolutional
  networks for approximate reasoning with abstract argumentation
  frameworks*) before any ML-backed surface; treat ML approaches
  as optional add-ons, not the primary path.

Target package surfaces (`argumentation.approximate`):

- `k_stable_extensions(framework, k)`: the Skiba-Thimm 2024
  generalisation of stable semantics with k-conflict tolerance.
- `approximate_grounded(framework, k_iterations)`: bounded-iteration
  characteristic-function approximation.
- `approximate_semi_stable(framework, time_budget)`: anytime
  approximation suitable for the ICCMA Heuristics Track.
- Optional GNN-backed surface only behind an extra dependency,
  with the pure-Python heuristics as the always-on default.

TDD slices: k-stable red/green with property tests proving k=0
matches stable; bounded-iteration grounded red/green with
convergence-rate tests; anytime semi-stable red/green with
property tests proving budget=∞ matches exact.

Acceptance for Phase 9:

- `uv run pytest -q tests/test_approximate.py`
- `uv run pyright src`

## Phase 10: Epistemic Graphs

Goal: implement the epistemic-graphs branch of probabilistic
argumentation that the SOTA assessment listed as a propstore
ranking-semantics complement.

Mandatory page-image gates:

- Reread Hunter, Polberg, Thimm 2018-2020 (AI, *Epistemic graphs
  for representing and reasoning with positive and negative
  influences of arguments*).
- Reread Hunter 2014 (IJAR, *Probabilistic argumentation with
  epistemic extensions and incomplete information*) for the
  epistemic-vs-constellation distinction.
- Reread Bona-Hunter-Vesic 2019 (TAFA, *Polynomial-time updates of
  epistemic states in a fragment of probabilistic epistemic
  argumentation*) for the tractable fragment.

Target package surfaces (`argumentation.epistemic`):

- `EpistemicGraph`: arguments, edges (positive / negative / neutral
  influence), and per-argument epistemic constraints over belief
  levels.
- `belief_assignment_satisfies(graph, assignment)`: constraint
  evaluation.
- `enumerate_satisfying_assignments(graph)`: model enumeration over
  discretized belief levels.
- `update_assignment(graph, evidence)`: polynomial-time updates per
  Bona-Hunter-Vesic 2019 in the supported fragment, generic-
  enumeration fallback otherwise.
- Connection to existing `probabilistic`: project an EpistemicGraph
  onto a constellation PrAF where the projection is well-defined,
  and document where it is not.

TDD slices: data model; constraint evaluator; enumerator; updater
in supported fragment; projection.

Acceptance for Phase 10:

- `uv run pytest -q tests/test_epistemic.py`
- `uv run pyright src`

## Phase 11: Argumentative LLM Surfaces

Goal: a thin, optional, opinionated surface for using
`argumentation` as the formal-reasoning layer behind argumentative
LLMs (Freedman, Dejl, Gorur, Yin, Rago, Toni 2024-2025).

This phase is intentionally narrow. The package is finite formal
argumentation, not an LLM framework. The goal is to make
`argumentation` callable from an ArgLLM-style pipeline without
pulling LLM dependencies into the package.

Mandatory page-image gates:

- Reread Freedman et al. 2024-2025 (AAAI 2025,
  *Argumentative large language models for explainable and
  contestable claim verification*).

Target package surfaces (`argumentation.llm_surface`, optional):

- `build_qbaf_from_proposition_set(propositions, edges)`: a
  package-native QBAF builder driven by externally-supplied
  proposition sets and edges. The LLM's job is to produce the set
  and the edges; the package's job is to compute the gradual
  semantics.
- `explain_acceptance(qbaf, target)`: Shapley-style attribution
  using `gradual.shapley_attack_impacts`.
- `contest(qbaf, claim, evidence)`: typed contestation result with
  the witnesses required to challenge a claim's acceptance.

This phase has only the surface; no LLM is shipped, no LLM
binding is taken as a dependency.

Acceptance for Phase 11:

- `uv run pytest -q tests/test_llm_surface.py`
- `uv run pyright src`

## Phase 12: Quality Bar, Property Tests, Benchmarks, Release

Goal: turn the result of phases 1-11 into a release that the
literature would accept.

Tasks:

- Property test suite: cross-semantics lattice properties for
  every framework family. For Dung: grounded ⊆ ideal ⊆
  ⋂preferred ⊆ ⋂stable; complete ⊆ admissible; semi-stable ⊆
  preferred; CF2 = naive on a single SCC. For ABA: every flat-ABA
  semantic agrees with its AF projection. For SETAF: degenerate
  case agrees with Dung. For ADF: encoded Dung AF agrees with
  Dung. For CAF: bijective `claims` reduces to Dung. For PrAF:
  Meier 2024 DP agrees with enumeration.
- Benchmark harness on ICCMA 2023 and ICCMA 2025 archives.
  Validate all auto-router thresholds. Tune any that are
  measurably wrong.
- Architecture and README documentation update covering every
  new module.
- Doctest pass: every public surface has at least one runnable
  example. CI runs them.
- CI configuration: `.github/workflows/test.yml` runs pytest +
  pyright on push and PR. Optional `iccma-benchmarks` job runs
  weekly.
- Release: bump to `0.2.0`, tag, build, publish via `uv publish`.

Acceptance for Phase 12:

- `uv run pytest -q --timeout=600`: full suite green.
- `uv run pyright src`: zero errors.
- `uv build` produces wheel + sdist.
- README, architecture, and CITATIONS reflect every surface.

## Track Dependencies

- Phase 1 has no upstream dependencies.
- Phase 2 depends on Phase 1.4 (clingo subprocess adapter
  conventions).
- Phase 3 has no upstream dependencies.
- Phase 4 depends on Phase 2 (ICCMA file conventions, subprocess
  conventions).
- Phase 5 depends on Phase 2.
- Phase 6 has no upstream dependencies but is more useful after
  Phase 1.3 (full SAT encodings).
- Phase 7 depends on Phase 1.3 (encoder conventions).
- Phase 8 depends on Phase 2 (ICCMA Dynamic format).
- Phase 9 has no upstream dependencies.
- Phase 10 has no upstream dependencies.
- Phase 11 depends on Phase 1.
- Phase 12 depends on all of the above.

Suggested execution order: 0 → 1 → 2 → 3 / 4 / 5 in parallel
where the agent can hold parallel work; otherwise 4 → 5 → 3 → 6
→ 7 → 8 → 9 → 10 → 11 → 12.

## Read The Papers, Find New Papers

The paper list above is a starting point, not a closed set. While
executing each track the agent should:

- Search Google Scholar, arXiv, and DBLP for any newer paper
  superseding the cited one. ICCMA, KR, IJCAI, AAAI, ECAI, JAIR,
  AIJ, AC, COMMA, TAFA, and SAFA are the relevant venues.
- Read the cited paper's "related work" and "future work"
  sections; if a successor or sibling paper looks more
  authoritative, switch the citation in the workstream and the
  implementation.
- When a paper has an open-source reference implementation, read
  the code and compare. Adopt the reference's invariants where
  they are formal and credit the source.
- Record every paper that was read, even if not implemented, in
  this file's execution ledger so the next agent does not
  duplicate the search.

## Boundary

`argumentation` continues to own only finite formal objects and
algorithms. It does not import `propstore`, does not know about
situated assertions, does not own merge policy, calibration, or
storage. Every new module preserves this boundary. The
import-boundary test (`tests/test_propstore_import_boundary.py`,
landed in commit `88ad5ec`) must keep passing.

If a phase produces a surface propstore wants, propstore consumes
it from outside; the package does not gain a propstore-shaped
adapter.

## Execution Ledger

Status as of spec commit:

- Spec committed as `eda2678` (`Add SOTA completeness workstream
  spec`). No production code changed in that commit.

Phase 0 baseline checkpoint, 2026-04-26:

- `uv run pytest -q --timeout=300` failed with `379 passed, 1
  failed in 30.92s`.
- Failing baseline test:
  `tests/test_docs_surface.py::test_readme_documents_new_package_surfaces`.
  The assertion expects the README to contain
  `adapted grounded edge-tracking TD backend`; current `README.md`
  does not contain that phrase.
- `uv run pyright src` passed with `0 errors, 0 warnings, 0
  informations`.

Paper-availability checkpoint, 2026-04-26:

- Used the `research-papers:paper-retriever` workflow instructions for
  the availability pass.
- `rg --files -g "*.pdf"` found no local PDF files under this
  repository.
- `C:\Users\Q\code\research-papers-plugin\papers` contains local
  PDFs, but only for unrelated biomedical/scientific-documentation
  papers; no cited argumentation PDFs were found there.
- The availability status below is therefore web/PDF availability, not
  local page-image availability. No paper was reread in this slice.
- First plan defect: the Phase 1 gate names Meier, Niskanen, Mailly
  2024 for arXiv `2407.05058`, but the arXiv/KR record for
  `2407.05058` is Popescu and Wallner, *Advancing Algorithmic
  Approaches to Probabilistic Argumentation under the Constellation
  Approach*. Update the gate before Track 1.1 implementation.
- Second plan defect: the Phase 10 gate names Bona-Hunter-Vesic 2019
  for polynomial-time epistemic updates, but the matching paper found
  is Potyka, Polberg, Hunter 2019, *Polynomial-time Updates of
  Epistemic States in a Fragment of Probabilistic Epistemic
  Argumentation*. Update the gate before Track 10 implementation.

Web/PDF availability notes:

- Popescu and Wallner 2024, probabilistic constellation DP:
  KR/arXiv PDF found (`https://arxiv.org/abs/2407.05058`,
  `https://proceedings.kr.org/2024/55/`).
- Lehtonen, Odekerken, Wallner, Järvisalo 2024, preferential ASPIC+:
  KR PDF found (`https://proceedings.kr.org/2024/49/`).
- Lehtonen, Wallner, Järvisalo 2020/2021 ASPIC+/ABA ASP papers:
  author/arXiv/Cambridge PDFs found for the ASPIC+ and ABA surfaces.
- Niskanen, Wallner, Järvisalo 2020, mu-toksia: author PDF found
  (`https://www.cs.helsinki.fi/u/mjarvisa/papers/nj.kr20b.pdf`).
- Bistarelli, Kotthoff, Lagniez et al. ICCMA report: author PDF found
  for the third/fourth ICCMA report; exact 2025 AAC citation metadata
  should be rechecked at the Phase 2 gate.
- ICCMA 2025 tracks/rules: official HTML pages found at
  `https://argumentationcompetition.org/2025/tracks.html` and
  `/2025/rules.html`.
- Brewka and Woltran 2010 ADF: CiteSeerX PDF found.
- Brewka, Strass, Ellmauthaler, Wallner, Woltran 2013 ADF Revisited:
  CiteSeerX PDF/DBLP record found.
- Linsbichler, Pichler, Spendier 2022 ADF algorithms: ScienceDirect
  page and open university PDF found.
- Keshavarzi-Zafarghandi, Verbrugge, Verheij 2022 strong ADF
  admissibility: arXiv/author PDFs found.
- Bondarenko, Dung, Kowalski, Toni 1997 ABA: ScienceDirect open
  archive page found.
- Toni 2014 ABA tutorial: Sage open-access PDF page found.
- Cyras and Toni 2016 ABA+: arXiv PDF found.
- Apostolakis, Saribatur, Wallner 2024 ABA abstraction: KR PDF found;
  the plan currently names Toni/Rapberger, which should be checked
  before implementation.
- Dimopoulos, Dvorak, König, Rapberger, Ulbricht, Woltran 2024 ABA+
  set-to-set attacks: AAAI/reposiTUm record found.
- Nielsen and Parsons 2006 SETAF: Aalborg/ArgMAS records found; direct
  PDF still needs to be downloaded or otherwise verified before Phase
  5.
- Dvorak, König, Ulbricht, Woltran 2024 SETAF principles: journal page
  found; direct author PDF not confirmed in this pass.
- Dvorak, König, Woltran 2025 SETAF parameterized complexity: Sage
  open-access PDF page found.
- Flouris and Bikakis 2024 collective-attack justification: no direct
  PDF confirmed in this pass; must be retrieved or replaced before
  Phase 5 work that depends on it.
- Buraglio, Dvorak, König, Woltran 2024 SETAF splitting: CEUR PDF
  found (`https://ceur-ws.org/Vol-3757/paper3.pdf`).
- Baumann 2012 argument enforcement: exact PDF not confirmed in this
  pass; retrieve before Phase 6.
- Wallner, Niskanen, Järvisalo 2017 extension enforcement: reposiTUm
  and author PDFs found.
- Baumann, Doutre, Mailly, Wallner 2021 enforcement survey/chapter:
  author PDF found.
- Mailly 2024 constrained incomplete AFs: Sage page found; direct PDF
  not confirmed in this pass.
- Dvorak, Gressler, Rapberger, Woltran 2023 CAF complexity: open
  ScienceDirect article found.
- Dvorak, Rapberger, Woltran 2020 claim-centric semantics: author PDF
  found.
- Alfano, Greco, Parisi, Trubitsyna 2025 Featured AF: IJCAI PDF found.
- Dynamic reasoning source in Phase 8 is under-specified
  ("Greenwood et al. or Alfano-Greco-Parisi 2018"); exact paper must
  be chosen before implementation.
- Fichte, Hecher, Meier 2024 counting complexity: JAIR/arXiv records
  found.
- Skiba and Thimm 2024 k-stable approximation: author PDF found.
- Thimm/ranking-based 2014 approximate semantics: author PDFs found,
  but exact citation should be pinned before Phase 9.
- Kuhlmann and Thimm 2019 GCN approximation: author PDF found.
- Hunter, Polberg, Thimm epistemic graphs: arXiv/ScienceDirect/author
  PDFs found.
- Hunter and Thimm 2014 epistemic probabilistic argumentation: arXiv
  and author PDFs found.
- Potyka, Polberg, Hunter 2019 polynomial-time epistemic updates:
  arXiv/UCL/Cardiff PDFs found; replaces the apparent
  Bona-Hunter-Vesic citation defect above.
- Freedman, Dejl, Gorur, Yin, Rago, Toni 2024/2025 argumentative
  LLMs: arXiv and AAAI/ResearchGate PDF records found.
- Track 1.3's broad SAT-encoding author families
  (Besnard-Doutre, Caminada, Gaggl-Woltran,
  Wallner-Niskanen-Järvisalo) are not unique paper identities. Pin
  exact titles before the first Track 1.3 page-image gate.

Page-image checkpoints expected during execution: per-track gates
listed above, amended by the citation defects recorded here. Each must
be honored before the implementation slice that depends on it.

## First Executable Slice

Target: Phase 0, baseline only.

Write set:

- This file (already committed in the spec slice).

Tasks for the first edit slice:

- Run `uv run pytest -q --timeout=300` on master and record the
  test count and time in this section.
- Run `uv run pyright src` and record errors.
- Confirm or update the paper-availability log for every paper
  cited above. Where a PDF is not on disk and not retrievable
  via the paper-retriever skill, record the unavailability and
  pick the smallest implementable subset for that phase that
  does not depend on the unavailable paper.
- Commit the updated execution ledger atomically.

Do not implement Phase 1 work in the first executable slice.

First-slice acceptance:

- `uv run pytest -q`
- `uv run pyright src`
- `git diff --check`
- `git status --short`
- This file edited; no other code changes.

## Spec Acceptance

This spec slice is documentation-only. Acceptance is:

- `git diff --check`
- `git status --short`
- Commit this file atomically before any implementation work
  starts.
