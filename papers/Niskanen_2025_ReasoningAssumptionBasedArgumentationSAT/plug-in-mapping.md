# Plug-in Mapping: Niskanen et al. (2025) encodings → this repo's ABA SAT code

This maps the paper's four acyclicity variants (and its base semantics encoding)
onto the two ABA SAT modules in this repo:

- `src/argumentation/structured/aba/aba_acyc_sat.py` — the DC-CO-era "100ba-acyc"
  cone/acyclicity prototype (complete credulous acceptance).
- `src/argumentation/structured/aba/aba_sat.py` — the stable/preferred SAT solvers,
  including the `_NativeSparseNarrowStableSolver` ("exp-5 eager arc-acyclic stable")
  and `_NativeCnfPrefSatSolver` (native CNF PrefSat for preferred).

The paper's "100ba" name is literally this repo's source-of-truth
(https://bitbucket.org/coreo-group/100ba); these modules are a partial Python
re-implementation of its ideas.

## Paper variable ↔ code variable correspondence

| Paper (Sec. 3–4) | Meaning | `aba_acyc_sat.py` | `aba_sat.py` stable solver |
|---|---|---|---|
| `x_a` | a ∈ A_τ | `in_vars[a]` | `in_vars[a]` |
| `y_a` | A_τ attacks {a} | (via `out_vars[a]` = contrary derived-from-in) | implicit in stable clause `in_a ↔ ¬derived(contrary_a)` |
| `z_a` | {a} not defended (B_τ attacks {a}) | `attacked_by_undec_vars[a]` | not present (stable needs no z) |
| `d_s` (derived from A_τ) | non-assumption derivability | `derived_from_in_vars[s]` | `derived_vars[s]` (single combined copy) |
| `e_s` (derived from B_τ) | derivability from B_τ | `derived_from_undec_vars[s]` | not present (stable needs no B-side) |
| `r_{s,t}^d` | activated derivation edge (A-side) | `derived_from_in_edge_vars[(s,t)]` | — (no edge vars) |
| `r_{s,t}^e` | activated derivation edge (B-side) | `derived_from_undec_edge_vars[(s,t)]` | — |
| `φ_G` (r^d → r^e) | reuse A_τ derivations for B_τ | `_add_rule_is_justified_undec_clauses` (`-in_edge, undec_edge`) | n/a |
| rule-body-satisfied | rule body all true | `body_is_true_in_vars` / `_undec_vars`, `rule_is_justified_*_vars` | `support_vars[rule]` (Clark completion) |

Note both modules restrict edge/acyclicity machinery to **recursive rules only**
(rules whose head shares an SCC with a body atom), computed via Tarjan SCC. This is
a compaction not spelled out identically in the paper but consistent with its goal
of minimizing acyclicity variables; non-recursive rules can never participate in a
derivation cycle.

## Variant-by-variant status

### 1. Base semantics encoding (φ_cf / φ_adm / φ_com / φ_stb) — IMPLEMENTED (split across modules)
- **Complete (φ_com)**: `aba_acyc_sat.py` `_add_complete_clauses` → `_add_admissible_clauses`
  → `_add_conflict_free_clauses`, with `attacked_by_undec` (z) and the
  `¬z_a → x_a` completeness direction. Matches `φ_com(F)` for DC-CO. *(paper p.710)*
- **Stable (φ_stb)**: `aba_sat.py` `_NativeSparseNarrowStableSolver._add_completion_clauses`,
  final loop `in_a ↔ ¬derived(contrary_a)`. Matches `φ_stb` (drops z / B-side, per
  paper's note that φ_ndef and B-side are unneeded for stable). *(paper p.711)*
- **Admissible / preferred base**: `aba_sat.py` `_NativeCnfPrefSatSolver` (in/out/undec
  labelling + static conflict clauses + CEGAR grow to preferred). Corresponds to
  `φ_adm` used as the abstraction and the μ-toksia-style grow loop for DS-PR.

### 2. Level-based encoding (SAT-LEVEL, Sec. 3.1) — NOT IMPLEMENTED
No U-indexed `d_s^i` / `e_s^i` variables exist in either module. Neither module
encodes derivation *levels*; both instead use edge variables (acyc module) or lazy
loop formulas (stable solver). The paper's own results show SAT-LEVEL is the weakest
variant, so this is a deliberate non-target.

### 3. Graph-based acyclicity encoding (the clause side of SAT-VE / SAT-ACYC, Sec. 3.2) — PARTIALLY IMPLEMENTED
`aba_acyc_sat.py` builds the graph-acyclicity **encoding skeleton**: the `r^d`/`r^e`
edge variables (`derived_from_in_edge_vars`, `derived_from_undec_edge_vars`), the
`φ_A^acyc(s)` / `φ_B^acyc(s)` "if body satisfied then derived, and derived ⇒ edges
active" clauses (`_add_recursive_rule_clauses`, `_add_edge_target_clauses`,
`_add_nonrecursive_head_edge_clauses`, `_add_same_head_body_difference_clauses`), and
the `φ_G` link `r^d → r^e`. **What is NOT present**: the actual acyclicity of the
edge graph is *not* fully encoded as clauses. Only `_add_reciprocal_arc_guards`
eagerly forbids 2-cycles between reciprocal arcs; the remaining (longer) cycles are
ruled out lazily (see item 4). So the eager clause set alone is unsound for
acyclicity and relies on the solve-time refinement.

### 4. Vertex-elimination acyclicity encoding (SAT-VE, Sec. 3.2) — NOT IMPLEMENTED
This is the paper's **best-performing** variant. There is **no** vertex-elimination
fill-in in either module: no elimination ordering α, no `e_{s,t}^*` vertex-elimination
edge variables, no `F_{i-1}(α(i))` transitivity clauses (`e_{s,α(i)}^* ∧ e_{α(i),t}^*
→ e_{s,t}^*`), and no `r_{s,t} → e_{s,t}^*` linkage. The repo's `_add_reciprocal_arc_guards`
exploits the *same theoretical fact* the VE encoding rests on (a cycle induces a
2-cycle in the elimination graph, paper p.712) but only for direct reciprocal arcs,
not via a full elimination graph. This is the single most valuable gap to close if
we want to match the paper's headline performance. *(paper p.712, p.715)*

### 5. Graph-based acyclicity propagator (SAT-ACYC, Sec. 4.1) — IMPLEMENTED
`aba_acyc_sat.py` `_AcyclicityPropagator` (+ `_solve_with_cadical195_propagator`,
selected via `solver_name="cadical195"`) is a direct realization of the paper's
Section 4.1 propagator over the `derived_from_undec_edge_vars`:
- edges observed (`solver.observe`), tracked as enabled/disabled/possible with
  decision-level restore on backtrack (`on_assignment`/`on_new_level`/`on_backtrack`),
  matching the paper's possible/enabled/disabled labeling. *(paper p.712)*
- on each newly enabled edge (s,t): DFS from t to s along enabled edges; a found
  cycle → external clause `⋁ ¬r_{u,v}` (`_cycle_clause_for_enabled_edge`). *(paper p.712)*
- otherwise compute nodes reachable from t and reverse-reachable from s and propagate
  `¬r` for bridging "possible" edges, with the "almost-cycle" reason
  (`_candidate_cycle_clause`, `provide_reason`). This is exactly the paper's N1/N2 ∩ P
  propagation with the C' almost-cycle reason clause. *(paper p.712)*
Caveat: it targets CaDiCaL 1.9.5 via python-sat's `Cadical195`, whereas the paper
uses CaDiCaL 2.1.3 + IPASIR-UP directly; the interface shape is the same.

### 5b. Lazy CEGAR cycle-clause refinement (not a named paper variant) — IMPLEMENTED
`complete_credulous_acyc_sat_acceptance` (default `glucose4`) solves the eager base
encoding and, on each model, extracts selected edges, finds a directed cycle
(`_first_directed_cycle`), and adds a blocking clause — repeating up to
`max_cycle_refinements`. This is the "encode base + lazily forbid cycles" hybrid; it
is functionally a poor-man's SAT-ACYC without the propagator's in-search propagation.

### 6. Unfounded-set propagator (SAT-UFS, Sec. 4.2) — PARTIALLY IMPLEMENTED (as lazy loop formulas, not an IPASIR-UP propagator)
`aba_sat.py` `_NativeSparseNarrowStableSolver` enforces non-circular support the
ASP way, but as **lazy loop-formula refinement** rather than an in-solver source-pointer
propagator:
- `_unsupported_derived_loop_formulas`: after a candidate model, compares the model's
  `derived_vars` set against the *true* bitset Horn closure of the extension; literals
  derived in the model but absent from the real closure are **unfounded** (cyclically
  self-supported) — the same "no non-circular support" condition the UFS propagator
  detects. *(paper p.713)*
- `_unsupported_components` (Tarjan SCC over the unsupported subgraph) +
  `_loop_formula_for` add ASP-style **loop formulas** (`⋁ ¬derived(comp) ∨ ⋁ external_support`).
This captures the *unfounded-set idea* but differs from the paper's SAT-UFS in two
ways: (a) it is CEGAR/lazy-clause, invoked between full SAT solves, not an IPASIR-UP
source-pointer propagator running during propagation; (b) it maintains no persistent
`source_d`/`source_e` pointers. So: the *semantics* of UFS is realized for stable
(and preferred via the grow loop); the *mechanism* (Sec. 4.2 source-pointer propagator)
is not.

## Headline have/haven't summary

- **Have (fully):** base cf/adm/com/stb encoding; the graph-based acyclicity
  **propagator** (SAT-ACYC, Sec 4.1); a lazy cycle-clause CEGAR fallback.
- **Have (partially / different mechanism):** graph-based acyclicity **clause encoding**
  (edge vars + φ_A^acyc/φ_B^acyc + φ_G present, but full acyclicity only via reciprocal-arc
  guards + lazy refinement, not fully clausal); unfounded-set support (SAT-UFS *idea*
  realized as lazy loop formulas for stable, not as the Sec 4.2 source-pointer propagator).
- **Haven't:** the **level-based encoding** (SAT-LEVEL) and — most importantly — the
  **vertex-elimination encoding** (SAT-VE), which is the paper's best performer. Also
  absent: the beyond-NP CEGAR wrappers wired to these acyclicity variants for DS-PR /
  SE-ID exactly as the paper adapts μ-toksia (the repo has its own PrefSat grow loop,
  but not with all four acyclicity backends pluggable).

## Highest-value next step
Implement the **vertex-elimination acyclicity encoding (SAT-VE)** in `aba_acyc_sat.py`
alongside the existing edge variables: add an elimination order, `e_{s,t}^*` fill-in
variables, the transitivity clauses, and `r_{s,t} → e_{s,t}^*`. This is the paper's
top performer and the repo currently only exploits its 2-cycle corollary via the
reciprocal-arc guard. Reference: Rankooh and Rintanen 2022 (AAAI).
