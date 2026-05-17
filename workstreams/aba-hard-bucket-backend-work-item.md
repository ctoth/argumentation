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
