# ABA Hard-Bucket Backend Work Item

Status: active backend work item, created from
`data/iccma/2025/runs/aba-shape-cap200-paper-features-rerun.json`.

## Decision

Do not promote a production route from the current cap-200 evidence.

The rerun has no exact structural signature with at least two rows and zero
counterexamples. The only emitted route candidate,
`flat_direct_asp_candidate`, has 21 counterexamples in 42 rows.

The hard class is not routable by the current coarse bucket fields. The
large/medium-arity/dense buckets are mixed:

- preferred: `all_timeout=5`, `best:asp=4`, `best:auto=2`;
- stable: `all_timeout=4`, `best:asp=3`, `best:auto=3`, `best:sat=1`.

The `best:sat=1` stable row and the easy `5_5_7` pair rule out a blanket
"large dense medium-arity means no current backend" route.

## All-Timeout Structural Signature

Repeated all-timeout rows share this structural envelope:

- `assumption_count`: 200
- `max_rule_arity`: 5
- `rule_count`: 5222 to 5560
- `rule_density`: 26.11 to 27.8
- `dependency_cycle_count_or_flag`: 1
- `p_acyclic`: false
- `dependency_scc_count`: 11 to 18
- `dependency_scc_max_size`: 1783 to 1790
- `tau_aba_primal_width_proxy`: 21 to 25
- `contrary_target_in_degree_max`: 2 to 3
- `assumption_incidence_width_proxy`: 17 to 19
- `rule_body_overlap_max`: 1
- `rule_body_overlap_avg`: 0.004439200662678256 to 0.004552148890709343
- `closure_growth_sample`: 0.03785714285714285 to 0.129
- `stable_obstruction_count`: 0

Preferred maximality risk is high: every preferred all-timeout row is in the
large/medium/dense bucket, and the same structural region has stable rows that
are either all-timeout or solver-sensitive. This says maximality checking and
large cyclic dependency structure are the next target, not filename routing.

## Distinct Row Targets

The next backend slice targets rows, not a coarse label. The primary target set
is the nine all-timeout rows from the rerun:

| Target | Instance | Subtrack | Purpose |
|---|---|---|---|
| T1 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-PR` | preferred all-timeout |
| T2 | `ABAs/aba_2000_0.1_5_5_0.aba` | `SE-ST` | stable all-timeout |
| T3 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-PR` | preferred all-timeout |
| T4 | `ABAs/aba_2000_0.1_5_5_1.aba` | `SE-ST` | stable all-timeout |
| T5 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-PR` | preferred all-timeout |
| T6 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-PR` | preferred all-timeout |
| T7 | `ABAs/aba_2000_0.1_5_5_6.aba` | `SE-ST` | stable all-timeout |
| T8 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-PR` | preferred all-timeout |
| T9 | `ABAs/aba_2000_0.1_5_5_9.aba` | `SE-ST` | stable all-timeout |

The nearby controls are mandatory because they live in the same coarse bucket
but current backends still solve them:

| Control | Instance | Subtrack | Baseline result |
|---|---|---|---|
| C1 | `ABAs/aba_2000_0.1_5_5_3.aba` | `SE-ST` | solved by `sat` |
| C2 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-PR` | solved by `asp` |
| C3 | `ABAs/aba_2000_0.1_5_5_7.aba` | `SE-ST` | solved by `auto` |

The first backend gate is deliberately small: solve at least one of T1-T9 under
the same 30-second budget while preserving C1-C3. The second gate is to solve a
preferred/stable pair on the same instance, preferably `5_5_0` or `5_5_1`. The
third gate is to generalize across at least three distinct instances, so a
single accidental row improvement does not masquerade as a backend.

## Explicit Non-Fit Signals

- Popescu-style low-width dynamic programming is not the immediate fit:
  `tau_aba_primal_width_proxy` is 21 to 25, not low.
- Toni/Dung p-acyclic dispute search is not the immediate fit:
  `p_acyclic` is false and the largest dependency SCC is about 1.8k literals.
- Dimopoulos normal-framework stable/preferred coincidence is not enough:
  `stable_obstruction_count` is 0, but the preferred and stable rows remain
  mixed or all-timeout.
- SAT/QBF/decomposition-guided routing is not promotable until a supporting
  paper is read into the collection or explicitly accepted from a neighboring
  paper store.

## Next Backend Hypothesis

Use a Lehtonen-style direct ASP refinement as the next implementation
hypothesis, but make it structure-aware:

- operate on the giant cyclic dependency SCC instead of treating the whole ABA
  input as an undifferentiated flat instance;
- add an SCC-aware preferred/maximality strategy for the large cyclic component;
- keep the existing ASP backend as the comparison baseline;
- measure against the exact hard rows above, not against filenames.

The acceptance gate for this backend slice is concrete:

- at least one current all-timeout row becomes solved under the same 30s
  solver budget;
- no currently solved row regresses;
- the selection predicate uses only shape fields and solver class;
- route promotion remains blocked until a rerun has zero counterexamples.

## Paper Stack

The hard-bucket backend work should cite distinct papers for distinct jobs:

- Lehtonen, Wallner, and Jarvisalo 2021,
  `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md`:
  primary ABA source for direct ASP encodings, the `assumption/head/body/
  contrary` fact surface, stable constraints, preferred maximality through
  ASPRIN-style subset optimization, and the warning that direct ABA avoids AF
  translation blow-up.
- Egly, Gaggl, and Woltran 2010,
  `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/notes.md`:
  ASPARTIX source for modular ASP encodings, saturation for preferred/semi-
  stable maximality, fixed-query/input-fact separation, and splitting-theorem
  proof discipline.
- Baroni and Giacomin 2005,
  `../propstore/papers/Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation/notes.md`:
  SCC-recursive directionality source. This is the paper to justify solving or
  conditioning the giant cyclic SCC differently from acyclic upstream/downstream
  structure.
- Cerutti, Dunne, Giacomin, and Vallati 2013,
  `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/notes.md`:
  preferred-extension search source for complete-labelling SAT, iterative
  maximality growth, blocking, and the empirical fact that encoding details
  materially change preferred performance.
- Cerutti, Vallati, and Giacomin 2015,
  `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/notes.md`:
  ICCMA-system source for complete-labelling SAT as an implementation surface
  over complete, preferred, grounded, and stable tasks.
- Niskanen and Jarvisalo 2020,
  `../propstore/papers/Niskanen_2020_ToksiaEfficientAbstractArgumentation/notes.md`:
  practical SAT-system source for persistent solver state, assumptions,
  iterative calls, unit-propagation grounded preprocessing, and ICCMA-proven
  solver engineering.
- Popescu and Wallner 2023,
  `papers/Popescu_2023_ReasoningAssumption-BasedArgumentationTree-Decompositions/notes.md`:
  ABA-specific tree-decomposition source. It is not the immediate hard-row fit
  while the width proxy is 21-25, but it defines the `tau_ABA` structure and the
  witness/counterwitness state we should measure against.
- Fichte, Hecher, Mahmood, and Meier 2021,
  `../propstore/papers/Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth/notes.md`:
  decomposition-guided SAT/QBF source. Use it when we have a real decomposition
  artifact, not as a slogan for dense hard rows.
- Dimopoulos, Nebel, and Toni 2002,
  `papers/Dimopoulos_2002_ComputationalComplexityAssumption-basedArgumentation/notes.md`:
  complexity and framework-class source, especially for not conflating flat,
  normal, simple, and general ABA behavior.
- Toni 2013 and Dung, Mancarella, and Toni 2007,
  `papers/Toni_2013_GeneralisedFrameworkDisputeDerivations/notes.md` and
  `papers/Dung_2007_ComputingIdealScepticalArgumentation/notes.md`: dispute
  derivation sources. They are controls for p-acyclic or query-shaped future
  routes, not the first attack on these cyclic hard rows.
