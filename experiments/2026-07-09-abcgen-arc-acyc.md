# 2026-07-09 — abcgen: eager arc-acyclic foundedness for the sparse-narrow stable solver

Branch: `exp/abcgen-arc-acyc` (base 2d11b94). Groundwork:
`reports/abcgen-levelmap-scout.md` (mandate + hardness probe),
`reports/aba-sepr-sest-scout.md` §3 (routing), and the `aba_acyc_sat.py`
prototype on `exp/iccma-aba-dcco-100ba-acyc` (58b13df) as the reuse inventory.
NOTE: `aba_acyc_sat.py` is NOT on main — the port copies the mechanism, not the
module.

## Hypothesis

The 3 abcgen frontier instances (SE-PR c25/c35, SE-ST c25/c35) time out because
`_NativeSparseNarrowStableSolver` enforces well-foundedness with a lazy
loop-formula CEGAR whose clauses are long disjunctions over whole unsupported
literal-SCCs; each added loop formula degrades subsequent CDCL solves (scout
measured 14→13→52→13→64→92s per solve, 247.9s total on the smallest cell).
Replacing the lazy loop formulas with an eager SCC-local arc-acyclicity
justification encoding (the externally validated `acyc` mechanism; `level`
order-vars are a proven dead end) removes the growing-solve blow-up: per-solve
times stay flat and the SE-ST cells solve inside a 120s budget.

## Derivation (soundness + completeness for STABLE, done BEFORE implementing)

### Setting

Flat ABA framework F = (L, R, A, ¯·). For E ⊆ A let Cn(E) be the least set
containing E and every zero-body rule head, closed under rules (least Horn
model). E is a **stable extension** iff for every a ∈ A: a ∈ E ⟺ contrary(a) ∉
Cn(E). (This subsumes conflict-freeness and closedness of flat frameworks: the
biconditional at each assumption is exactly the solver's existing contrary
clause pair.)

### Existing encoding (unchanged parts)

Variables: `in[a]` (a ∈ A), `derived[l]` (l ∈ literals), `support[r]` (rules
with nonempty body). Clauses (aba_sat.py `_add_completion_clauses`):

1. `in[a] → derived[a]`.
2. Zero-body rule head h: unit `derived[h]`.
3. `support[r] ↔ ⋀_{b∈body(r)} derived[b]`, `support[r] → derived[head(r)]`,
   `(⋀ body) → derived[head]`.
4. Completion only-if (for l not a zero-body head):
   `derived[l] → ⋁ {support[r] : head(r)=l} ∪ {in[l] if l ∈ A}`
   (or unit `¬derived[l]` if no option).
5. Stable contraries: `in[a] ↔ ¬derived[contrary(a)]`.

A model of 1–4 makes `derived` a *supported* (Clark-completion) model:
Cn(E) ⊆ derived always (derived is a pre-fixed point containing the base, by
1–3), but derived may strictly exceed Cn(E) via unfounded cycles. Clause 5 then
tests stability against the wrong closure — hence the current lazy loop-formula
CEGAR.

### Port: static shape (identical mechanism to `_build_abf_shape`)

Build the bipartite dependency graph over atom nodes and body nodes: for each
rule r with nonempty body, edges b → body(r) for each body atom b, and
body(r) → head(r). Tarjan-SCC it. Rule r is **recursive** iff its body node and
its head are in the same SCC. The **intra-SCC derivation edges** are the pairs
(b, h) with r recursive, h = head(r), b ∈ body(r), SCC(b) = SCC(h).

Two structural facts used below (proved here, relied on by the encoding):

* **(F1) A non-recursive rule has no body atom in its head's SCC.** If
  b ∈ body(r) with SCC(b) = SCC(head(r)), then head(r) reaches b (same SCC) and
  b → body(r) → head(r), so body(r) lies on a cycle through head(r) and
  SCC(body(r)) = SCC(head(r)) — r would be recursive.
* **(F2) Every recursive rule has ≥ 1 body atom in its head's SCC.** If
  SCC(body(r)) = SCC(head(r)), some path returns from head(r) to body(r); the
  only in-edges of a body node come from its body atoms, so that path passes
  through some b ∈ body(r) with SCC(b) = SCC(head(r)).

### New clauses

New variables: `edge[(b,h)]` per intra-SCC derivation edge, `just[r]` per
recursive rule r. Let internal(r) = {b ∈ body(r) : SCC(b) = SCC(head(r))}
(nonempty by F2).

* (J) `just[r] ↔ support[r] ∧ ⋀_{b ∈ internal(r)} edge[(b, head(r))]`.
* (C′) Completion only-if (replaces clause 4's disjunct for recursive rules):
  `derived[l] → ⋁ {just[r] : recursive r, head(r)=l}
              ∪ {support[r] : non-recursive r, head(r)=l}
              ∪ {in[l] if l ∈ A}`.
* (D) Demand pruning: `edge[(b,h)] → ⋁ {just[r] : recursive r, head(r)=h,
  b ∈ internal(r)}` — a selected edge must be demanded by a justified rule
  (correctness-neutral, see Completeness; kills spurious edge cycles).
* (G) Reciprocal guards: `¬edge[(u,v)] ∨ ¬edge[(v,u)]` for 2-cycles (eager
  special case of ACYC).
* (ACYC) The selected edges {(b,h) : edge[(b,h)] true} contain no directed
  cycle. Enforced by a lazy **edge**-cycle CEGAR: after each SAT model, find a
  directed cycle among selected edges; if found, add the short all-negative
  clause `⋁_{e ∈ cycle} ¬edge[e]` and re-solve. (Fallback if this loops
  excessively: the IPASIR-UP acyclicity propagator from the prototype.)

Clauses 1, 2, 3, 5 are unchanged. Non-recursive rules keep exactly their old
clauses. Singleton/acyclic SCCs get no edge machinery.

### Soundness

Claim: any model M of {1,2,3,J,C′,5} ∪ ACYC (with or without D, G) has
derived = Cn(E) for E = {a : in[a]}, hence (by 5) E is stable.

Cn(E) ⊆ derived: derived contains E (1) and all zero-body heads (2) and is
closed under all rules (3's `(⋀body) → head`), so it contains the least such
set.

derived ⊆ Cn(E): The selected edges form a DAG (ACYC). Order derived literals
by the pair (condensation rank of SCC(l), position of l in a topological order
of the selected edges restricted to SCC(l)); condensation order is well-founded
across SCCs and the DAG order within. Strong induction on this order for
l ∈ derived:

* l a zero-body head → l ∈ Cn(E). l ∈ A with in[l] → l ∈ E ⊆ Cn(E).
* Otherwise C′ gives a true disjunct:
  * `support[r]`, r non-recursive: body(r) ⊆ derived (J-free, from 3), and by
    F1 every body atom is in a strictly lower SCC (body atoms always reach the
    head, so their condensation rank is ≤; F1 rules out equality). By induction
    each body atom ∈ Cn(E), so l ∈ Cn(E).
  * `just[r]`, r recursive: by (J), support[r] holds so body(r) ⊆ derived, and
    edge[(b,l)] holds for every b ∈ internal(r). Body atoms outside SCC(l) are
    in strictly lower SCCs (rank ≤ as above, and ≠ since b ∉ SCC(l)) → Cn(E)
    by induction. Body atoms b ∈ internal(r): edge (b,l) is selected, so b
    precedes l in the intra-SCC topological order, and b ∈ derived (from
    support[r] → derived[b]) → b ∈ Cn(E) by induction. All body atoms in
    Cn(E) ⇒ l ∈ Cn(E).

So derived = Cn(E), and clause 5 asserts precisely the stability biconditional
at every assumption. Any model therefore yields a stable extension. Adding D
and G only shrinks the model set — soundness is preserved.

### Completeness

Claim: every stable extension E extends to a model of all clauses.

Set in := E, derived := Cn(E), support[r] := (body(r) ⊆ Cn(E)). Clauses 1, 2,
3, 5 hold (5 is the definition of stability). Define level(l) = the first
stage of the bottom-up T_P iteration from E ∪ {zero-body heads} at which l
appears. For each derived l that is neither in E nor a zero-body head, pick a
justifying rule r_l with head l and body(r_l) ⊆ {levels < level(l)}(one exists
by definition of the iteration). Select edges := {(b, l) : b ∈ internal(r_l),
l derived non-base}; set just[r] := support[r] ∧ ⋀ edges (its defining ↔).

* ACYC: every selected edge (b, l) has level(b) < level(l), so selected edges
  cannot form a cycle. G follows a fortiori.
* (J): holds by construction of just.
* (C′): for derived non-base l, if r_l is non-recursive then support[r_l] is a
  true disjunct; if recursive, its internal edges were all selected and its
  body is true, so just[r_l] is true. For l ∈ E, in[l]. Zero-body heads are
  exempt from 4/C′ (unchanged).
* (D): every selected edge (b, l) came from r_l with just[r_l] true, and r_l
  is a recursive head-rule of l with b ∈ internal(r_l) (b ∈ internal(r_l)
  requires SCC(b) = SCC(l), which forces body(r_l) into SCC(l), making r_l
  recursive) — the disjunction has a true member.

So the encoding is sound and complete for stable semantics; the CEGAR loop
terminates because each blocking clause removes ≥1 edge subset and the edge
set is finite (same argument as the prototype), and on "no cycle" the returned
E is exactly stable. A belt-and-braces bitset-closure verification
(`derived == Cn(E)` check, once per final answer) is kept as a
raise-on-encoding-bug guard; the derivation says it can never fire.

### Preferred routing note

`_native_sparse_narrow_stable_extension` serves semantics ∈ {preferred,
stable}: a stable extension is also preferred (stable ⇒ complete and
maximal), so returning one for SE-PR is unchanged behaviour; the SE-PR
fallback path when no stable extension exists (`native_cnf_prefsat_extension`)
is untouched.

## Single Variable

The well-foundedness mechanism inside `_NativeSparseNarrowStableSolver`: lazy
literal-SCC loop-formula CEGAR → eager SCC-local arc-justification encoding
(edge + just vars, clauses J/C′/D/G) with a lazy short-clause edge-cycle CEGAR.
Nothing else changes: same completion/contrary clauses, same routing, same
result/telemetry surfaces (plus new edge telemetry keys).

## Fast Contracts

- RED: new fixture test — a framework whose completion has an unfounded
  2-cycle; assert exact result AND
  `telemetry["native_sparse_narrow_loop_formulas"] == 0` (fails on the current
  lazy CEGAR, which counts loop formulas on that fixture).
- Existing property tests (tests/structured/aba/test_aba_sparse_narrow_native_sat.py)
  stay green: stable/preferred vs `support_extensions` oracle.
- `uv run pytest tests/solving tests/interop tests/structured`, then full
  CI-equivalent suite before final commit (main is 2951 passed / 4 skipped /
  1 xfail — must stay).
- Committed microbench `scripts/profile_abcgen_stable.py` (port of the scout's
  scratchpad probe): per-solve times must be FLAT, not growing.

## Metric Gate

Re-baselined on THIS tree (scout numbers were from an older branch):

1. Baseline on unmodified 2d11b94: the 4 frontier cells at t120 via
   `tools/iccma2025_run_native.py` (labels `abcgen-arc-acyc-baseline-*`), plus
   the microbench profile on c25.
2. After: same commands (labels `abcgen-arc-acyc-fixed-*`). SUCCESS = both
   SE-ST cells solve < 120s (target well under 247.9s); SE-PR cells measured
   and reported (flip = bonus, not required).
3. Regression guard: SE-ST slice at t15 (label `abcgen-arc-acyc-sest-guard`) —
   no baseline-solved row lost/changed; >10% common-time regression = kill.
4. STOP RULE: if after 2 implementation iterations the per-solve profile still
   GROWS on abcgen, the wall is giant-SCC size, not the CEGAR — stop, record
   evidence, recommend SCC-decomposition/cutset escalation.

## Interpretation

Mechanism result (microbench, c25 = the scout's probe instance):

| variant | checks | per-solve seconds | total |
|---|---:|---|---:|
| baseline loop-formula CEGAR (b446dfb) | 6 | 15.3, 14.1, 55.9, 14.1, 71.7, 108.6 (growing; 191 loop formulas) | 280.7s |
| iter 1: edge-cycle CEGAR (08e19cd) | 12 | 1.2 … 46.5 (still trending up; 11 cycle clauses) | 178.3s |
| iter 2: eager all-cycles (9ca0b56) | **1** | 56.0 (single solve, 0 CEGAR) | **56.0s** |

The static intra-SCC edge graphs are tiny (c25: 194 edges / 92 elementary
cycles; c35s: ~800 edges / 718-822 cycles, enumerable in ≤0.02s), so full
eager cycle blocking is essentially free and removes the iteration mechanism
entirely: the per-solve profile is flat by construction. Encoding volume never
exploded (build ≤0.6s), so the IPASIR-UP propagator fallback was not needed.
Witnesses closure-verified (the raise-on-bug founded check never fired);
exactness property tests and the new unfounded-cycle fixtures pass.

Cell results (t120, runner auto backend, baseline = pristine b446dfb):

| cell | baseline | fixed |
|---|---|---|
| SE-ST c25 | timeout | timeout — **routes to clingo, not this solver** |
| SE-ST c35_asms30 | timeout | timeout (this solver; its ONE solve takes 522s) |
| SE-PR c25 | timeout | **solved 65.3s (witness 76)** |
| SE-PR c35_asms35 | timeout | timeout (this solver) |

Two mandate premises did not survive contact with current main:

1. **Routing:** SE-ST single-extension goes to `sat` only for
   `large_dense_flat_aba_shape` (rule density > 25) AND sparse-narrow
   (`solving/solver.py:487`, set deliberately by
   `experiments/2026-07-07-aba-sest-clingo-route.md`). abcgen c25's density is
   20.7, so SE-ST c25 goes to clingo and cannot be flipped by any change to
   this solver. (SE-PR c25 rides the sparse-narrow preferred gate and DID
   flip.)
2. **Instance scale:** on c35 the wall after the fix is a single hard CDCL
   solve (522s), not CEGAR degradation — the giant-SCC/instance-hardness wall
   the stop rule anticipated. Two implementation iterations were used; the
   profile no longer grows, so the stop rule's growth trigger is not met, and
   no third encoding iteration was attempted.

Guard (SE-ST t15 slice, exp-4B command): baseline (detached b446dfb)
241 solved / 79 timeout on the 320 ABA rows. Fixed-run comparison recorded in
reports/abcgen-arc-acyc-coder.md §6.

## Decision

Keep the eager arc-acyclic foundedness encoding on this branch and recommend
promotion, with caveats (recommend-only; no merge from this worktree):

- The mechanism goal is achieved: loop-formula CEGAR deleted, per-solve
  profile flat, c25 stable witness 280.7s → 56.0s (5x), SE-PR c25 frontier
  cell flips timeout → solved 65.3s, nothing lost (guard tables in the coder
  report).
- The two remaining abcgen timeouts need DIFFERENT variables, out of scope
  here: (a) a routing-gate experiment so abcgen-shaped SE-ST rows
  (sparse-narrow, density ≤ 25, cycle-heavy) reach the native stable solver
  instead of clingo — clingo also times out on them, so the gate currently
  picks a loser; (b) for c35-scale single-solve hardness, escalate to
  SCC-decomposition / cutset preprocessing (queue items 5 and 9), per the
  scout's stop-rule recommendation.
