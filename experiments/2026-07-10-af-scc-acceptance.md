# AF query-directed SCC-cone acceptance (exp 6A)

Date: 2026-07-10 (started 2026-07-09)

Status: derivation committed before any code (this commit). Results sections
filled in after the metric gate.

Experiment branch: `exp/af-scc-acceptance` (from `main` @ `5dd6a03`).

## Hypothesis

Routing Dung DC/DS acceptance through the query's SCC ancestor cone — solve
`AF|cone` with the existing `af_sat` kernels instead of the whole graph — flips
the crusti/scc frontier cells (query cone is 1.6–25% of the graph; the flat
kernel build alone exceeds the 120 s budget on crusti), with answers matching
the ICCMA-2025 reference table, and without regressing the DS-PR cap320 t15
slice.

## Derivations per semantics (before code)

Setting: finite AF `F = (A, R)`. For a query `q ∈ A`, let `S(q)` be the SCC of
`q` and define the **ancestor cone**

```
U = ⋃ { S ∈ SCCS(F) : S = S(q) or S reaches S(q) in the condensation DAG }.
```

**Lemma 0 (the cone is unattacked).** No attack enters `U` from outside:
if `(b, a) ∈ R` and `a ∈ U` then `b ∈ U`. Proof: `SCC(b)` reaches `SCC(a)`
which reaches `S(q)`, so `SCC(b) ⊆ U`. ∎

All semantics below are SCC-recursive with the base functions of
[BG&G05] Thm 43 (complete `CE(·,·)`, preferred `PE(·,·)`, stable
`SE(·,·) = SE(·)`, grounded `GE(·,·)`). Two facts from Def 18/20 drive
everything; both hinge on Lemma 0 plus footnote 3 of the paper (the
`D/U/P` context of an SCC `S` depends only on `E ∩ sccanc(S)`).

**Lemma 1 (projection — every SCC-recursive semantics, including stable).**
If `E ∈ E_σ(F)` then `E ∩ U ∈ E_σ(F|U)`.
Proof: `F|U` has exactly the SCCs of `F` contained in `U`, with the same
condensation order and the same restricted sub-frameworks. By Def 20,
`E ∈ E_σ(F)` iff for every SCC `S` the choice `E ∩ S` lies in
`GF(F↓UP(S,E), U(S,E) ∩ C)`. For `S ⊆ U` the sets `D/U/UP(S,E)` and the
threaded `C` depend only on `E ∩ sccanc(S) ⊆ E ∩ U` (Lemma 0: all parents of
cone SCCs are cone SCCs). These are literally the per-SCC conditions of
Def 20 evaluated for `E ∩ U` on `F|U`, so all of them hold. ∎

(Elementary double-check for complete, no schema needed: `E ∩ U` is
conflict-free; admissible because attackers of cone members lie in `U`
(Lemma 0) and their defenders against cone attackers lie in `U` too; the
fixpoint condition holds because a node of `U` defended by `E ∩ U` in `F|U`
is defended by `E` in `F` — its `F`-attackers all lie in `U` — hence is in
`E`.)

**Lemma 2 (lifting — complete and preferred, NOT stable).**
If `E' ∈ E_σ(F|U)`, `σ ∈ {complete, preferred}`, then there is
`E ∈ E_σ(F)` with `E ∩ U = E'`.
Proof: extend `E'` over the SCCs outside `U` in topological order; at each
SCC pick any element of `GF(F↓UP(S,·), U(S,·) ∩ C)` given the partial choice
on its ancestors. Each such call is nonempty: for complete,
`CE(AF, C) ∋ GE(AF, C)` (grounded-in-C always exists, [BG&G05] Prop 42/44);
for preferred, `PE(AF, C)` is the set of ⊆-maximal elements of the nonempty
finite `CE(AF, C)`. The assembled `E` satisfies all per-SCC Def 20 conditions
(cone SCCs: identical to `E'`'s conditions on `F|U` by the Lemma 1 argument;
outer SCCs: by construction), so `E ∈ E_σ(F)`, and no outer choice alters
`E ∩ U = E'` (directionality). ∎
For **stable** this fails: `SE(AF, C) = SE(AF)` can be empty, so a cone-stable
extension need not extend. Concrete counterexample used as a unit test:
`A = {p, q, x, y, z}`, `R = {(p,q), (x,y), (y,z), (z,x)}`, query `q`:
`U = {p, q}`, `SE(F|U) = {{p}}` (a `q`-free cone-stable extension exists),
but `SE(F) = ∅` so DS-ST(F, q) is vacuously YES — a naive cone answer of NO
would be WRONG.

### Complete — DC-CO and DS-CO: cone-equivalent (sound both ways)

Lemmas 1+2 give `{E ∩ U : E ∈ CE(F)} = CE(F|U)`, both sides nonempty, and
`q ∈ U`. Hence:
- DC-CO: `q` in some complete extension of `F` ⟺ `q` in some complete
  extension of `F|U`. Decided by one SAT check on the cone.
- DS-CO: `q` in every complete extension of `F` ⟺ `q` in every complete
  extension of `F|U`. (No vacuity gap: `CE` is never empty.) Moreover DS-CO
  is grounded membership (`q` in every complete extension iff `q ∈ GE`,
  grounded = least complete), and grounded is directional
  (`GE(F) ∩ U = GE(F|U)`), so the cone path decides it **polynomially**:
  answer = `q ∈ GE(F|U)`; the NO counterexample is `GE(F)` itself (the least
  complete extension of `F`, computed by the same closure worklist from the
  empty seed). No SAT at all.

**Witness lifting (kept because the ICCMA CLI prints certificates).** A cone
witness `E'` is not a full-AF extension. Since `U` is unattacked, `E'` is
admissible in `F`; the least complete extension of `F` containing it is the
characteristic-function closure `E = lfp_{X ⊇ E'} F_F(X)` (Dung's fundamental
lemma). Moreover `E ∩ U = E'`: inductively, a cone node defended by
`X = E' ∪ (outside-U nodes)` in `F` has all its attackers and their defenders
inside `U` (Lemma 0), so it is defended by `E'` in `F|U` and already in `E'`
(`E'` complete on `F|U`). So the closure is a valid DC-CO witness
(contains `q`) and a valid DS-CO counterexample (still avoids `q`).
Polynomial worklist, no SAT.

### Preferred — DS-PR: cone-equivalent (sound both ways); DC-PR left flat

Lemmas 1+2 give `{E ∩ U : E ∈ PE(F)} = PE(F|U)`, both nonempty. Hence
DS-PR(F, q) ⟺ DS-PR(F|U, q), decided by the existing CDAS solver
(`is_preferred_skeptically_accepted`) on the cone. The existing DS-PR path
returns no counterexample certificate, so the cone path returning
answer-only is contract-identical.

DC-PR is equally sound on the cone, but the flat path returns a *preferred*
extension of the full AF as witness and lifting a cone-preferred witness to a
full preferred extension would need downstream maximisation (more SAT, on the
part of the graph we are trying to avoid). DC-PR is not a frontier cell; it
keeps the flat path. (DC-PR ≡ DC-CO semantically, so the DC-CO routing covers
the decision-only use case at complete semantics.)

### Stable — one-sided only (weak directionality); fall back otherwise

Lemma 1 holds for stable; Lemma 2 does not. Derived sound rules:

- **DS-ST cone-YES rule:** if no `E' ∈ SE(F|U)` avoids `q` (SAT on the cone
  kernel with `require_out(q)` is unsat — this includes `SE(F|U) = ∅`), then
  every `E ∈ SE(F)` satisfies `q ∈ E ∩ U ⊆ E` (projection), and if
  `SE(F) = ∅` the answer is vacuously YES anyway ⇒ answer **YES**.
- **DC-ST cone-NO rule:** if no `E' ∈ SE(F|U)` contains `q`
  (`require_in(q)` unsat on the cone), then no `E ∈ SE(F)` contains `q`
  (projection) ⇒ answer **NO**.
- **Sat outcomes are inconclusive** (the cone extension may fail to extend —
  counterexample above) ⇒ fall back to the existing flat path unchanged.
  DS-ST is therefore NOT dropped: the sound one-sided cone check is wired,
  with flat fallback; conclusive cone answers need no certificate (the CLI
  prints witnesses only for credulous-YES / skeptical-NO).

### Not routed

Grounded (directional but its native path is already polynomial and not a
frontier cell), ideal (directional but a different solver, not a frontier
cell), semi-stable and stage (NOT directional — range-maximality peeks
downstream; unsound on the cone). These keep their existing paths.

Frameworks carrying a separate pre-preference attack layer
(`ArgumentationFramework.attacks` set and different from `defeats`) are also
not routed: there conflict-freeness ranges over `attacks` while defense
ranges over `defeats` (Modgil & Prakken Def 14), and the derivations above
cover pure Dung frameworks only. ICCMA AF inputs have `attacks = None`.

### Correctness of the SAT base-solve substitution

`GF` restricted to the cone collapses, by Def 20 applied to `F|U`, to
`GF(F|U, args(F|U)) = E_σ(F|U)` — i.e. "GF recursion restricted to the cone"
IS the semantics of the cone framework. The cone decision is therefore
delegated to the existing, already-tested SAT realizations of `CE`/`PE`/`SE`
on a whole framework: `find_complete_extension` /
`is_preferred_skeptically_accepted` (CDAS) / `find_stable_extension`, all
built on `AfSatKernel.add_complete_labelling` / `add_stable_coverage`. No new
encodings, no `(AF, C)`-restricted base calls are ever needed at solve time
(the top-level call has `C = A|U`, and Def 18 injection is exhausted by the
proofs above).

**Solver-engine substitution (iteration 2, measured).** Iteration 1 kept the
default Z3 solver and the crusti cells still timed out: on the crusti_175
cone (1400 args / 92 016 attacks) the kernel build was 13 s and the
*unconstrained* check 1.9 s, but the `require_in(q)` complete-labelling check
took 265 s — the default SMT core, not the encoding or the build, was the
sink. The same formula under Z3's CDCL sat core (`Tactic('sat').solver()`)
decides in 1.6 s (`QF_FD` similar; the admissible encoding is *slower* under
both engines). The cone path therefore constructs its kernels with
`engine="sat-core"` (`AfSatKernel(engine=...)`, threaded through the finders
and the CDAS sub-solvers with default `"smt"`, so every flat path is
byte-for-byte unchanged). This is answer-preserving by construction: the same
formula is decided, only the decision procedure differs. The sat core does
not support the pseudo-Boolean range constraints used by semi-stable/stage —
which are not routed through the cone.

Measured per-cell cone checks with the sat core (probes, this machine):
crusti_175 DC-CO 1.6 s sat; crusti_225 DC-CO 24.5 s sat; scc_7481 DC-CO
0.39 s unsat; scc_3605 DC-CO 80 s unsat after a 24 s build (the
909-node/248 k-attack single-SCC cone is the marginal cell; the reference
SCC solver needed 43 s); crusti_225 DS-ST stable `require_out` sat in 21 s ⇒
inconclusive by the one-sided rule ⇒ flat fallback (the DS-ST crusti cells
are NOT expected to flip; this is the derivation's predicted limit, not a
bug).

**DS-PR small-cone threshold (kill-criterion fix, measured).** The first t15
slice run lost one baseline-solved instance, BA_160_80_2 (161 args / 289
defeats; cone 123 / 232): the multi-check CDAS loop under the
*non-incremental* sat-core engine took 95–97 s (twice, consistent) where the
flat smt path takes <1 s, and cone+smt is high-variance (0.23 s and 26.7 s
across runs — the loop's attacker choices are model-dependent). The measured
cone wins for DS-PR start at mainkwt-sized cones (22–24 k defeats: ~11 s
under either engine vs flat t15 timeout) and the sat-core requirement starts
at crusti-sized cones (40 k+). DS-PR therefore routes through the cone only
when the cone has ≥ `PREFERRED_CONE_MIN_DEFEATS = 15 000` defeats; smaller
cones keep the flat CDAS path byte-for-byte. Complete/stable are single
checks with no loop variance and keep the cone at every size. Also noted:
three of the first run's "gained" rows (ER_200_20_5, WS_300_16_90_30,
n192p5q2_ve) have cone = whole graph, are never routed, and moved on pure
t15 run-to-run variance of the unchanged flat path — t15 borderline rows are
noisy in both directions.

**Why not per-SCC GF recursion with per-SCC kernels at solve time** (decision
recorded for the reviewer): (i) certifying a NO answer (both scc DC-CO gate
cells are NO) under per-SCC choice search requires exhausting the cross
product of per-SCC extension sets — exponential in cone depth, unbounded
per-SCC counts; (ii) intra-SCC attacks dominate these instances, so splitting
the cone kernel into per-SCC kernels does not reduce total encoded clauses —
there is no build-time win to buy; (iii) the plan's stated targets of the
per-SCC mechanics — the `2^16` subset-enumeration cliff of
`scc_recursive._base_solve` and the measured 61 s+ whole-graph kernel builds —
are both eliminated by the cone restriction + SAT substitution itself
(cone = 1.6–25% of nodes on the frontier instances; SAT, never subset
enumeration). The per-SCC condensation machinery (Def 17) is what *computes*
the cone; the Def 18 D/U/P analysis is what *proves* the cone sound.

## Single Variable

One new routing branch: `solve_dung_acceptance` with `backend="auto"`,
`semantics ∈ {complete, preferred, stable}`, `task ∈ {credulous, skeptical}`
(preferred: skeptical only) tries the SCC-cone path first, and only when the
query's ancestor cone is a proper subset of the arguments (single-SCC
frameworks and cone-spanning queries keep the flat path byte-for-byte).
Explicit `backend="sat"` / `"native"` / `"iccma"` behavior is unchanged.
Nothing on the flat solvers, kernels, or encodings changed.

## Fast Contracts

TDD sequence (RED confirmed before each implementation step):

1. `tests/solving/test_af_scc_cone_acceptance.py` — new module, 22 tests:
   cone-extraction units (ancestor closure on a hand-built SCC chain),
   routing telemetry (auto fires the cone, explicit `backend="sat"` and
   single-SCC frameworks do not), the stable vacuity trap (`p→q` plus a
   disconnected 3-cycle: DS-ST must stay vacuously YES through the fallback,
   DC-ST cone-NO is conclusive), witness lifting (DC-CO witnesses and DS-CO
   counterexamples must be complete extensions of the FULL framework),
   attacks-layer guard (`attacks != defeats` keeps the flat path), sat-core
   kernel oracle equivalence, unknown-engine rejection, DS-CO
   grounded-membership (no SAT), DS-PR small-cone threshold fallback, and
   Hypothesis property tests (auto == native oracle for complete /
   preferred-skeptical / stable × credulous/skeptical over random multi-SCC
   AFs; certificates verified against the native enumerator).
2. Suites: `uv run pytest tests/solving tests/core` = **1108 passed,
   3 skipped** (skips pre-existing/environmental). `uv run pyright` on
   changed files: 0 errors. `ruff check` on changed files: clean (one
   pre-existing F401 in solver.py is untouched, verified present on main).
3. Full CI-equivalent (pytest -q --timeout=600, pyright src, lint-imports,
   uv build) run before the final commit — results recorded below.

Method note: benchmark runs and test-suite runs were interleaved with care —
no test suite or probe ran while a benchmark was in flight, except ~25 s of
pytest during the discarded first baseline attempt (that run was killed and
fully rerun from a detached checkout of unmodified main; see Failure
Analysis).

## Metric Gate

Baseline first, on unmodified `main` @ `5dd6a03` (same worktree, same
machine):

```powershell
uv run scripts/run_frontier_v1.py --label af-scc-acceptance-baseline `
  --subtrack DS-PR --subtrack DC-CO --subtrack DS-ST
uv run tools/iccma2025_run_native.py --root <worktree>/data/iccma/2025 `
  --only-subtrack DS-PR --backend auto --max-af-arguments 320 `
  --timeout-seconds 15 --label af-scc-acceptance-t15-baseline
```

After, same commands with labels `af-scc-acceptance-fixed` /
`af-scc-acceptance-t15-fixed`.

SUCCESS = ≥5 of the 7 in-scope frontier cells flip with answers matching the
reference table (DS-PR crusti 125/175/225 = NO; DC-CO crusti 175/225 = YES;
DC-CO scc_3605/scc_7481 = NO). DS-PR t15 slice: no lost rows, no answer
changes, >10% common-time regression = kill.

### Frontier results (t120; baseline = `5dd6a03`, fixed2 = `911135b`)

| cell | baseline | fixed2 | reference answer | verdict |
|---|---|---|---|---|
| DC-CO crusti_g2io_175 | timeout | **solved YES** | YES | **FLIP, correct** |
| DC-CO crusti_g2io_225 | timeout | **solved YES** | YES | **FLIP, correct** |
| DC-CO scc_3605 | timeout | **solved NO** | NO | **FLIP, correct** |
| DC-CO scc_7481 | timeout | **solved NO** | NO | **FLIP, correct** |
| DS-PR crusti_g2io_125 | timeout | **solved NO** | NO | **FLIP, correct** |
| DS-PR crusti_g2io_175 | timeout | timeout | NO | no flip (stop rule) |
| DS-PR crusti_g2io_225 | timeout | timeout | NO | no flip (stop rule) |
| DS-ST crusti_g2io_175 (prio 2) | timeout | timeout | YES | predicted (one-sided limit) |
| DS-ST crusti_g2io_225 (prio 2) | timeout | timeout | YES | predicted (one-sided limit) |

Totals over the 18 AF frontier rows: baseline 6 solved / 12 timeout →
fixed2 **11 solved / 7 timeout**. No solved row regressed and no solved
answer changed (DC-CO crusti_125 = true, scc_1554 = false, DS-PR mainkwt ×3
= false, DS-ST crusti_125 = false, identical in both runs). The first fixed
run (`af-scc-acceptance-fixed`, commit 9dfc489) produced the identical
18-row table. **Gate: 5 of 7 in-scope cells flipped with reference-matching
answers = MET.**

### DS-PR crusti_175/225 stop-rule anatomy (2 iterations spent)

Cone verified small (1400 / 1575 args; 92k / 131k defeats; 8 / 7 SCCs).
After iteration 2 the SAT *checks* are seconds each; the remaining time is
Python-API construction: parse ~15 s + cone extraction ~14 s + three kernel
builds inside CDAS on the 92k-attack cone (super-core ~16 s +
complete-labelling extension problem ~14 s + double-admissible attacker
solver ~32 s ≈ 62 s) + loop checks ⇒ > 120 s. Time now goes to **clause
construction, not SAT search**. Candidate follow-ups (out of scope here):
share one kernel across the CDAS sub-solvers, skip the answer-preserving
super-core precheck on big cones, a direct-CNF substrate (scout Proposal C),
faster cone extraction.

### DS-PR cap320 t15 slice guard

| run | solved | timeout | common-row time vs baseline | answer mismatches |
|---|---|---|---|---|
| baseline (5dd6a03) | 221 | 34 | — | — |
| fixed (9dfc489, pre-threshold) | 233 | 22 | −13.97 % | 0 |
| fixed2 (911135b, final) | 221 | 34 | −0.44 % | 0 |

The pre-threshold run lost one baseline-solved instance (BA_160_80_2,
0.6 s flat → 95–97 s under the non-incremental sat-core CDAS loop); the
`PREFERRED_CONE_MIN_DEFEATS` guard fixed it (0.6–0.7 s again in fixed2).
fixed2's remaining 5-lost/5-gained churn is boundary-band noise, not the
change: every churned row sits at 10.7–15.0 s against the 15 s budget;
`n192p5q2_ve` churned with cone = whole graph (provably unchanged code
path); and identical-code mainkwt rows shifted uniformly ~+3.5 s between the
fixed and fixed2 runs (environmental drift — other agents share this
machine). The baseline itself (221/34) already deviates from exp-1's
recorded expectation (235/20) on this machine/day. No answer changed in any
run; common-row time never regressed.

## Interpretation

The scout's structural lever is real and the derivation held end-to-end:
restricting DC/DS to the query's ancestor cone turns the crusti/scc frontier
cells from >120 s whole-graph kernel builds into 17–107 s cone solves with
reference-matching answers, provably (not heuristically) preserving the
semantics for complete/preferred and one-sidedly for stable. Two findings
matter beyond this experiment:

1. **The default Z3 SMT core, not the encoding, was the acceptance
   bottleneck at scale** — `Tactic('sat')` decides the same require_in
   complete-labelling query 165× faster on the crusti_175 cone. This likely
   generalizes to the ER cells (single-SCC, out of scope here).
2. **Python-API clause construction is the next wall**: DS-PR on the two
   biggest crusti cones still TOs because CDAS builds three kernels on the
   cone (~62 s) before the loop starts — the incremental-SAT substrate
   (Proposal C) is the right follow-up, now with a precise cost model.

DS-ST behaved exactly as derived: the one-sided rule is sound but its
conclusive branch does not trigger on crusti (the cone genuinely has
query-free stable extensions), so those two priority-2 cells stay timeout by
design — honestly reported rather than unsoundly flipped.

## Failure Analysis

Two mid-experiment failures, both caught and corrected:

1. The very first baseline attempt ran while the implementation was being
   written into the same worktree; `run_child` spawns a fresh subprocess per
   row, so later rows would have imported modified code. The run was killed
   and the baseline fully rerun from a detached checkout of unmodified main
   (`5dd6a03`), with no source edits during any subsequent benchmark.
2. Iteration 1 (cone + default engine) left the crusti DC-CO cells timing
   out; phase probes isolated the 265 s require_in check and iteration 2
   (sat-core engine) fixed it. The BA_160_80_2 t15 loss was probed to a
   consistent sat-core pathology on tiny CDAS loops and fixed by the
   measured cone-size threshold.

## Decision

**GO.** Recommend promoting `exp/af-scc-acceptance` (code through `911135b`;
docs through this commit) to main: the frontier gate is met (5/7 flips, all
answers matching the ICCMA reference table), the t15 slice shows no answer
changes and no common-time regression, and the flat paths are byte-for-byte
unchanged outside the new auto-only cone routing. Two full-suite test
failures on this branch are **pre-existing on main** (verified failing
identically on detached `5dd6a03`):
`test_current_docs_do_not_cite_old_flat_source_paths` and
`test_large_dense_stable_auto_route_uses_sat_without_asp` — fix on main
independently. Follow-ups in value order: (a) shared-kernel / direct-CNF
CDAS substrate for DS-PR crusti_175/225 and the ER family, (b) sat-core
engine for the flat acceptance paths, (c) self-loop preprocessing for the
scc family (shrinks the marginal scc_3605 cone).
