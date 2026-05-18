# ABA Next Optimization Possibilities

Status: possibility queue, not an implementation workstream.

Purpose: keep every plausible next speed tactic visible, paper-driven, and
convertible into a hypothesis-first workstream. The last completed workstream
proved that exact independent-product decomposition is real but too narrow for
the remaining hard rows: T8 solved on SAT, while T1/T3/T5/T6 timed out after
parse and shape computation. The next work must attack backend solving and the
`component_plan_not_exact` class.

## Rules For Turning Any Item Into Work

Before implementing any tactic below:

1. Check existing paper page images under `./papers/**/pngs/page-*.png` and
   sibling paper collections before retrieving anything.
2. Reread the relevant page images directly before writing paper-derived tests
   or production code.
3. Write an operational contract first: route selection, bounded solver calls,
   residual reduction, learned-clause reuse, bitset-operation count, table-size
   bound, or hard-row metric gate.
4. Run the contract before source implementation and record the expected failing
   result.
5. Implement one tactic per workstream; no mixed successes.

## Current Evidence

- T1/T3/T5/T6 reached backend execution and timed out across auto/ASP/SAT.
- T8 solved on SAT with `validation.status == "valid"` under the Phase 9 gate.
- Shape/decomposition metadata is now bounded, so the remaining timeout class is
  backend solving, not parse, shape, or validation.
- The hard rows report `decomp_no_reduction_reason ==
  "component_plan_not_exact"` when shape planning is bounded.

## Paper Inventory

Already in this repo or sibling collections:

- `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract`
- `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers`
- `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions`
- `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults`
- `papers/deKleer_1986_AssumptionBasedTMS`
- `papers/deKleer_1986_ProblemSolvingATMS`
- `../propstore/papers/Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth`
- `../propstore/papers/Dunne_2009_ComplexityAbstractArgumentation`
- `../propstore/papers/Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation`
- `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation`

Retriever/reader queue before some later workstreams:

- `Tractable Abstract Argumentation via Backdoor-Treewidth` by Dvorak, Hecher,
  Konig, Schidler, Szeider, and Woltran.
- `Structure-Aware Encodings for Argumentation Properties` by Mahmood et al.
- `D-FLAT: dynamic programming on tree decompositions`.
- `D-FLAT^2: subset minimization in dynamic programming on tree decompositions
  made easy`.
- A modern SAT preprocessing / inprocessing reference for CaDiCaL or Kissat.
- A graph modular-decomposition or clique-width algorithm reference suitable for
  implementation.

## Possibility Queue

### 1. Py-spy Backend Attribution

Question: where do T1/T3/T5/T6 spend backend time after the current changes?

Hypothesis contract:

- Hard-row runner emits worker-stage progress: parse, simplify, plan, encode,
  solve, candidate-block, validate, print.
- A py-spy profile exists for one timed-out SAT primary row.
- The profile attribution names one dominant stage before any new solver tactic
  is implemented.

Implementation surface:

- `tools/run_aba_hard_bucket.py`
- `tools/iccma2025_run_native.py`
- `src/argumentation/aba_sat.py`

Gate:

```powershell
uv run tools\run_aba_hard_bucket.py --target-id T1 --backend sat --subtrack SE-PR --timeout-seconds 30 --profile-duration-seconds 25 --profile-format speedscope --profile-dir data\iccma\2025\profiles\aba-next --output-json data\iccma\2025\runs\aba-next-t1-profile.json --output-csv data\iccma\2025\runs\aba-next-t1-profile.csv
```

### 2. Bitset-Native Closure, Attack, And Validation

Question: are Python literal/set loops dominating complete-labelling checks?

Tactic: pre-index literals, rules, consequents, contraries, and assumption masks.
Compute closure, attack, conflict-free, and necessary validation using integer
masks and adjacency arrays instead of Python object sets.

Paper anchors:

- de Kleer ATMS papers for bit-vector environment/nogood discipline.
- Cerutti/ArgSemSAT for complete-labelling SAT loops.

Hypothesis contract:

- Existing semantic properties still pass.
- A calibrated microbenchmark shows closure/attack checks are faster than the
  object-set path by a declared factor.
- Hard-row profile shows reduced Python time in closure/validation/candidate
  checking.

Row targets: T1/T3/T5/T6 SAT backend.

### 3. Persistent Z3 PrefSat Kernel

Question: are we losing time rebuilding solver state or relearning conflicts?

Tactic: keep one Z3 solver object for the base complete-labelling constraints,
use assumptions/push-pop for candidate growth, and preserve globally valid
blocking/defense clauses across PrefSat iterations.

Paper anchors:

- Cerutti 2013/2015 complete-labelling PrefSat.
- Niskanen 2020 Toksia-style incremental solver engineering.

Hypothesis contract:

- Bounded number of base-encoding rebuilds per call: exactly one.
- Candidate-block clauses are monotonically accumulated.
- Solver checks do not increase relative to current PrefSat on Hypothesis
  products.

Row targets: T1/T3/T5/T6, with T8 as no-regression solved row.

### 4. CNF Export To A Real SAT Backend

Question: is Z3 the wrong engine for the complete-labelling CNF?

Tactic: emit DIMACS/WCNF-style complete-labelling constraints and run a modern
SAT backend with assumptions, incremental solving, and native preprocessing.

Paper anchors:

- ArgSemSAT uses Glucose rather than SMT.
- SAT preprocessing/inprocessing reference to retrieve/read before coding.

Hypothesis contract:

- CNF variable count and clause count are deterministic and reported.
- Witness maps back to the same assumption set as Z3 on small properties.
- On one hard row, SAT backend reaches either solved+valid or a strictly later
  internal stage than Z3 under the same timeout.

Row targets: T1/T3/T5/T6.

### 5. Small Backdoor / Cutset Conditioning

Question: can a small assignment set break the giant incidence component into
solvable components?

Tactic: find candidate cutsets over assumptions or contrary literals. Branch on
their IN/OUT/UNDEC labels, simplify each branch, then run exact component
solving. This is not product decomposition; it is conditional decomposition.

Paper anchors:

- Dvorak et al. backdoor-treewidth paper to retrieve/read.
- Popescu 2023 tree-decomposition ABA paper.
- Fichte 2021 decomposition-guided reductions.

Hypothesis contract:

- For a generated framework with a known separator, branch residuals have
  smaller max component size.
- For each branch, lifted witnesses validate against the original framework.
- Branch count is bounded by `3^k` and route only fires when `k <= threshold`.

Row targets: T1/T3/T5/T6 shape telemetry first; implementation target only if a
small separator is found.

### 6. SCC-Recursive Preferred Conditioning

Question: can directed SCC structure reduce preferred solving even when the
undirected product certificate fails?

Tactic: compute SCCs on a directed ABA attack/proof dependency graph, solve SCCs
in topological order, and condition later components on earlier labels.

Paper anchors:

- Baroni 2005 SCC-recursiveness.
- Gaggl 2013 CF2/SCC implementation details.

Hypothesis contract:

- SCC route must not claim independence.
- It must report SCC count, max SCC assumptions, cross-SCC attacks, and exact
  conditioning obligations.
- On acyclic SCC condensation graphs, no full-instance PrefSat call occurs
  unless a conditioning obligation fails.

Row targets: T1/T3/T5/T6 SCC telemetry.

### 7. Tree-Decomposition Dynamic Programming For ABA

Question: do hard rows have low enough width after the right graph projection?

Tactic: compute an approximate tree decomposition of the ABA primal/incidence
graph. If width is below threshold, run DP over nice tree decomposition with
labelling/witness state.

Paper anchors:

- Popescu 2023 ABA tree-decomposition DP.
- Dunne 2009 bounded-treewidth complexity.
- Fichte 2021 DG reductions.

Hypothesis contract:

- Width computation is bounded and reported.
- DP table sizes are bounded by a declared function of width.
- Route fires only when measured width is below threshold.

Row targets: all hard rows first as shape-only telemetry.

### 8. Decomposition-Guided SAT/QBF Reduction

Question: can we preserve graph width while still using a SAT/QBF backend?

Tactic: build local formulas per tree-decomposition bag instead of one dense
global formula. Use auxiliary variables to propagate attack/defense state.

Paper anchors:

- Fichte 2021 DG reductions.
- Mahmood 2025 clique-width/DDG paper if retrieved/read.

Hypothesis contract:

- Generated formula primal width proxy is linearly bounded by input width proxy.
- Naive global encoding and DG encoding report different width proxies on a
  constructed family.

Row targets: low/moderate-width rows, not necessarily T1/T3/T5/T6 unless shape
telemetry says width is useful.

### 9. Clone / Twin / Module Compression

Question: do ICCMA hard rows contain many structurally equivalent assumptions?

Tactic: quotient assumptions with identical relevant neighborhoods: same
contrary-target behavior, same rule-body participation signature, same outgoing
support/attack role. Solve quotient with multiplicities, then lift.

Paper anchors:

- Need modular decomposition / clique-width paper.
- Mahmood 2025 if retrieved/read.

Hypothesis contract:

- Renaming and row-order invariants hold.
- Quotient/lift round-trip preserves preferred witness validity on generated
  clone families.
- Route fires only with a measured compression ratio.

Row targets: shape telemetry across T1/T3/T5/T6.

### 10. Dominance And Subsumption Kernelization

Question: can assumptions/rules be deleted because another assumption/rule
dominates their effect under preferred semantics?

Tactic: implement paper-backed safe reductions only: rule subsumption,
duplicate consequents, dominated supports, forced-out assumptions, and dead
contrary targets.

Paper anchors:

- Need a SAT/argumentation preprocessing reference.
- Current ABA preprocessing work for grounded fixed-in/fixed-out.

Hypothesis contract:

- Every deletion has a proof obligation and a lift map.
- Residual assumption/rule counts strictly decrease on generated dominated
  families.
- Preferred witness validates against original framework.

Row targets: hard-row preprocessing telemetry.

### 11. Backbone / Forced Label Extraction

Question: can cheap propagation force IN/OUT/UNDEC labels before PrefSat?

Tactic: repeatedly derive forced labels from unattacked assumptions, factual
contraries, single-support attacks, and stable/preferred necessary conditions.

Paper anchors:

- Cerutti complete labelling.
- ABA grounded reduct already implemented.

Hypothesis contract:

- Forced-label extraction is idempotent.
- Forced labels agree with all preferred extensions on small oracle cases.
- Solver variable count shrinks before PrefSat.

Row targets: hard-row variable-count reduction.

### 12. Optimizer-First Maximal Admissible Seed

Question: can a large initial admissible set reduce PrefSat grow/block rounds?

Tactic: find a large admissible seed with Z3 Optimize, MaxSAT, local search, or
greedy repair, then use exact PrefSat only to prove maximality.

Paper anchors:

- Cerutti PrefSat loop.
- SAT/MaxSAT optimization reference to retrieve/read if we leave Z3 Optimize.

Hypothesis contract:

- Seed is admissible.
- Seed size is at least current first model size on generated cases.
- Exact final answer still validates as preferred.

Row targets: T1/T3/T5/T6 if profile shows grow/block iteration cost.

### 13. MUS/MCS-Style Learned Counterexamples

Question: are candidate blocks too weak?

Tactic: when a candidate is rejected, learn a minimal reason: conflict set,
undefended attack support, or impossible label combination. Block that reason
instead of only the whole candidate.

Paper anchors:

- SAT MUS/MCS reference to retrieve/read.
- Cerutti candidate-blocking algorithm.

Hypothesis contract:

- Learned reason is smaller than the rejected candidate on generated cases.
- Learned clauses preserve preferred witnesses.
- Candidate-model count decreases on stress families.

Row targets: profile-dependent.

### 14. Portfolio Routing Inside SAT

Question: does one backend dominate on specific shape classes?

Tactic: treat SAT, ASP, Z3, bitset search, tree-DP, and decomposition as a
portfolio. Route by measured structural telemetry, not filenames.

Paper anchors:

- ICCMA system papers and Toksia.
- Existing route-property tests.

Hypothesis contract:

- Route decisions are invariant under filename/path/year/manifest.
- Every production route has benchmark evidence id.
- A row is promoted only if solved+valid under the declared budget.

Row targets: all hard-bucket rows.

### 15. Parallel Branch Portfolio

Question: can we exploit multicore by racing exact tactics rather than picking
one?

Tactic: run bounded exact solvers concurrently for a row and accept the first
valid witness. Keep worker limits explicit to avoid machine exhaustion.

Paper anchors:

- Solver-portfolio literature to retrieve/read if this becomes production.

Hypothesis contract:

- Parallel runner never reports a witness until validation succeeds.
- Timeout cleanup is deterministic.
- On a controlled fixture, fastest backend wins and slower backends terminate.

Row targets: hard bucket after at least two exact tactics exist.

### 16. Proof-Carrying Translation / Institution Comapping

Question: can we safely solve in a different formalism and map witnesses back?

Tactic: define translations as explicit satisfaction-preserving morphisms:
source ABA, target AF/SAT/ASP/DP state, witness comap, and proof obligation.
This is the discipline for non-product reductions that are not obviously
semantics-preserving.

Paper anchors:

- Institution/comorphism reference to retrieve/read before implementation.
- Existing structured-argumentation translation papers in collection.

Hypothesis contract:

- Every translated witness carries a checkable lift/comap certificate.
- If certificate validation fails, the route is invalid even if tests pass.
- No production route returns target-only witnesses.

Row targets: applies to future translation-heavy tactics, not a standalone speed
win.

## Suggested Execution Order

1. Py-spy backend attribution.
2. Bitset-native closure/attack validation.
3. Persistent Z3 PrefSat kernel.
4. Hard-row structural telemetry pass for separators, SCCs, treewidth, clones,
   and dominance.
5. Pick the first graph tactic with a real measured reduction:
   backdoor/cutset, SCC conditioning, tree-DP, or clone compression.
6. Add CNF/native SAT only if profiling says Z3 itself is the bottleneck after
   Python and structural reductions.

## Completion Criterion For This Queue

This document is exhausted only when each item has either:

- an executed workstream with a kept measured win,
- an executed failed-hypothesis record with profiler/telemetry evidence, or
- a documented paper-backed reason it is inapplicable to our target classes.
