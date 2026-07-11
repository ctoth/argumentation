# ICCMA ABA SE-PR Git-history inventory

Date: 2026-07-11
Scope: preferred single-witness (`SE-PR`) optimization history in this repository
Inventory HEAD: `ece99962e4a5a442735eea4ff08ac5904e16a47c` (`main`)
Mode: read-only Git-object inspection; no solver or holdout access

## Method and repository state

The expected HEAD was present exactly. `main` had no tracked modifications before
this report. The worktree contained many unrelated untracked files; none was used
as committed evidence and none was modified. Evidence was collected with
`git for-each-ref`, `git log --all`, `git log --all --not main`, `git show`, Git
path history, and the committed experiment/workstream/report records. All local
and remote refs visible to `git for-each-ref` were included. “Kept” below means
reachable from current `main`, not merely described as promising on a branch.

The current campaign baseline is `21/24` solved at `5f75a7c`; the three 10-second
development timeouts are the two SE-PR rows and one SE-ST row on the 600-assumption
`aba_2000_0.3` shape. The campaign ledger is `experiments/INDEX.md` at HEAD.

## Executive finding

The repository has already tried nearly every obvious “different solver” or
“different maximality loop” answer to SE-PR. In particular, the history contains:

- the current exact multi-shot Clingo CEGAR algorithm, which was a major kept win;
- stable-first, direct ASP, greedy growth, support-aware Z3 CEGAR, exact
  three-valued PrefSat, native PySAT CNF, exact-product decomposition, and one-shot
  ASP `#maximize` variants;
- persistent solver/assumption reuse, batching attacker checks, bitset closure,
  optimizer-first selection, solver-engine swaps, support preprocessing, and
  several learning/inprocessing variants;
- committed profiles repeatedly showing that the surviving hard preferred rows
  spend their budget in solver search, not Python orchestration or re-grounding.

The campaign ledger correctly kills its four Round-1 proposals and now correctly
marks the max-cardinality premise invalid. It is not, however, a full history
ledger: it omits several material mainline successes and branch-only failures
listed below. Those omissions matter because they invalidate a number of otherwise
plausible “next candidate” suggestions.

## Materially distinct approaches

### 1. Incremental ASP / multi-shot CEGAR: the kept baseline family

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| merged branch `experiment/graph-speedup-wave-a-preprocessing`; `466d38d` (implementation), `76e6366` (workstream merge); later `52cb484` preferred routing and `37148ed` lean facts | Lehtonen Algorithm 1/4: one grounded `pi_com` control, assumptions for transient requirements, monotone refinement parts, grow-to-maximal complete sets, exact preferred witness | Cap-150 ICCMA comparison: ABA SE-PR changed from 28 solved / 12 timeout to 39 solved / 1 timeout at 5 s; 11 of 12 prior SE-PR timeouts cleared. Current 2023 hard row is only 4 calls / 1 outer / 3 inner / 3 refinements, with 928 py-spy samples in `clingo.Control.solve` and 3 in refinement grounding. | **Kept on main and still the production hard-row baseline.** Re-grounding elimination is dead as a current candidate because grounding is not the cost. |
| `9873b47` plus `experiments/2026-07-11-iccma2023-cegar-regrounding-churn-triage.md` | Same current CEGAR loop; proposed avoiding refinement re-grounding | Even perfect removal of observed non-solve work cannot move the 11.07 s row under 10 s. | **Diagnosed negative; no source slice.** |

This family is not “untried CEGAR.” A new CEGAR proposal must change the search
inside the inner solves or prove a strict reduction in their formulas/search
space; reducing call plumbing, control construction, or refinement grounding is
history-invalidated.

### 2. Stable-first and stable-derived preferred shortcuts

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| `experiment/aba-se-pr-st-assumption-kernel` @ `8ab2a6f`; `7219823`, `bba03f1`, `9d6a3c8`, `f005404` | Assumption-kernel stable shortcut followed by admissible growth/direct ASP defense | Became part of the early preferred implementation chain; later superseded by multi-shot Clingo and exact PrefSat/native-CNF routes. | **Historical kept ancestry, algorithmically superseded.** |
| `experiment/aba-iccma-speedup-20260514` @ `8f37df5`; `7f472b4`, `1befc15` | Ranked-Z3 stable witness accepted as a preferred witness | Correct shortcut and merged. It helps only when a stable witness exists and is found cheaply. | **Kept capability, not a general SE-PR solver.** |
| `experiment/aba-direct-stable-witness` @ `37148ed`; `f865867`..`c7d2719` records an earlier direct helper added and then removed; `0ac957f`, `5b91f33`, `37148ed` are the surviving multishot/lean-fact route | Direct or first-model stable witness through ASP | Direct-helper WIP was removed; lean multishot stable solving survived. | **One abandoned WIP chain; surviving capability supersedes it.** |
| `2091a7d`, `experiments/2026-07-11-iccma2023-stable-preferred-triage.md` | Run stable first on the exact 2023 SE-PR timeout shape and independently validate as preferred | Stable query finished in 0.834 s but produced no extension. Preferred still took 10.18 s and entered the normal 4/1/3/3 path. | **Dead for this campaign shape.** |

The ledger’s R1-P1 conclusion is correct. “Try stable first,” “use the stable
winner as preferred,” and “direct stable encoding” are not novel suggestions.
The separate lean stable-only encoding (`4b6ee26`, record `4deb85d`) solved 0/5
SE-ST rows and had essentially unchanged Clingo-solve profiles; it supplies
additional negative evidence against encoding-only stable rescue.

### 3. Direct ASP routing and alternative ASP maximality

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| `exp/aba-se-pr-asp-vs-sat` @ `f735fee` | Explicit ASP versus SAT on six 2025 SE-PR timeouts | ASP solved 1/6 valid at the boundary; auto and SAT solved 0/6. | **Exploratory lead only.** |
| `exp/aba-se-pr-asp-routing` @ `f765ec0`; source `ddaaff5`, `6c30f97` | Blanket sparse/narrow SE-PR auto route to ASP | Full 10x10 stayed 9 solved / 11 timeout; boundary row timed out at 30.01 s. | **Abandoned branch-only source.** |
| `exp/aba-se-pr-boundary-asp-stability` @ `0262385` | Repeat the ASP-only boundary row | 30 s: 3/5 solved, 2/5 timeout; 35 s: 3/3 solved but still near boundary. Profile: 2467 samples in Clingo solve, single-digit grounding/encoding samples. | **Diagnosed no-go for routing alone.** |
| `experiment/aba-asp-saturation-preferred` @ `408f4b0`; properties `fe1c317`, implementation `94679ab`, routing `aa56b7c`, proved-optimum return `b6c9b1d` | One-shot Lehtonen complete-set ASP with `#maximize {1,X:in(X)}`; wait for proved optimum and return one exact preferred witness | Semantic gates passed. T1/T3/T5/T6/T8 timed out under auto, ASP, and SAT. | **Branch-only, dead for dense preferred.** Despite the branch name, the tested mechanism is optimization/max-cardinality, not a still-untried magical saturation variant. |
| `dd95143`, `b2971e`, `56a946e`, `experiments/2026-07-11-iccma2023-clingo-config-triage.md` | Default, handy, crafty, trendy configurations on the current hard SE-PR row | Best (`trendy`) median 9.759 s and every run >9 s; handy timed out once; successful arms retained 4/1/3/3. No arm met the preregistered gate. | **Killed without source change.** |

Therefore blanket ASP routing, another generic built-in configuration sweep,
and global `#maximize`/maximum-cardinality complete-set selection are explicitly
invalidated by history.

### 4. Z3/support-aware CEGAR and greedy maximality variants

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| early main history `af4e54a`, `7033b6b`, `e1d6aba`; query fixes `e6c0926`, `eb67654`; CEGAR gate `2b72779`, `ae4abbd` | Support-SAT preferred witness growth with query constraints and admissible CEGAR | Correctness established; later variants and hard-row records show the class remained solver-bound. | **Kept ancestry, superseded by later implementations.** |
| `experiment/aba-preferred-maximality-backend` @ `753f582`; `d631a83`, `93f9b4b` | Remove the stable precheck and route preferred directly into support-aware maximality CEGAR | T1/T3 all-timeout, T5 on timeout path; targeted gate failed. This was not true three-valued PrefSat. | **Branch-only failed approximation.** |
| `experiment/aba-greedy-preferred-growth` @ `d84b18e`; `a662316`, `fbc0661`, failure `7a8e463` | Greedy preferred growth from grounded complete control, repeated constrained complete-superset solves | T1/T3/T5/T6/T8 timed out across auto/ASP/SAT. T1 profile attributed cost to solver calls, not wrapper work. Branch also contains unrelated commit `d47c870`, which is not salvageable evidence. | **Branch-only, dead.** |
| `e54facf` and `f2e93e0`, `048ee40`, `69e1c7a`, `44d1094` | Persistent Z3 base solver; assumptions/push-pop; reuse attacker solvers; batch target checks; Horn then bitset closure | Synthetic preferred-growth reuse improved about 5-6x. On real T1 the bottleneck moved from attacker-support Z3/object closure to the main PrefSat Z3 checks. | **Kept engineering improvements; the simple reuse/batching idea is exhausted.** |
| `5505c63`, reverted by `86658d8` | Z3 optimizer-first/max-cardinality candidate selection | Optimizer consumed the profile window; T1 still timed out. | **Explicitly reverted and dead.** |

This invalidates “reuse the solver,” “use assumptions,” “batch attacker checks,”
“bitset the closure,” “greedily grow,” and “use Optimize/max-cardinality as the
seed” as standalone new candidates. They may be components of a genuinely new
structural algorithm, but cannot be credited as its novelty or expected gain.

### 5. Complete-labelling PrefSat, native rule closure, and native CNF

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| `experiment/aba-complete-labelling-prefsat-backend` @ `07f5478`; `54951d6`, `d1ac405` | Eager minimal-support, three-valued complete labelling with Cerutti-style grow/block | Properties passed; T1/T3/T5/T6/T8 timed out on SAT; solved C2 also regressed to timeout on SAT. | **Branch-only, dead.** |
| `experiment/aba-native-rule-closure-prefsat` @ `5b37653`; `4d688a1` | Replace eager support enumeration with ranked native rule-closure variables plus CEGAR refinement | Same hard preferred rows timed out; C2 also timed out on SAT. | **Branch-only, dead; proves support enumeration was not the only blocker.** |
| merged `experiment/aba-real-complete-labelling-prefsat` @ `a6ff9cfe`; core `fe4bd14`, route `365c4ac`, failure `5be324c` / `66a1f23` | Direct ABA three-valued Z3 PrefSat, persistent solver, exact grow/block, no old CEGAR fallback | All T1/T3/T5/T6/T8 timed out across auto/ASP/SAT. T1 profile: 2498 samples; `Z3_solver_check_assumptions` 2099 leaves, `_unanswered_attack_support` 2271 inclusive. | **Implementation retained as fallback/test surface, performance hypothesis failed.** |
| merged `exp/native-cnf-prefsat` @ `84ee777`; `331ce3c`, `c3c45b0`, `23c42ea`; follow-up `aef28fe`, `fb4bf8c`; timeout fixes `01a3050`, `d2494df`, `7e34a2b`, `338e503`, merge `f6027b0` | Plain PySAT complete-labelling CNF, persistent assumptions/refinement, zero main Z3 checks, cached bitset closure; dense-shape route | T8 and then T1 solved valid within the historical 30 s 2025 hard-row gate; focused 80-test gate passed. Follow-up bypassed support preprocessing and closure materialization. | **Kept on main and still live. Not novel.** It has not, however, been shown to clear the current 2023 10 s timeouts. |

The current campaign’s N1 (`15ae450`, runner instrumentation `000ae2c`, record
`6d2d113`) tested the native SAT route for the 600-assumption **stable** task and
moved the bottleneck from Clingo solve to ranked-closure construction (391/399
samples) without shrinking it. N2 (`5f75a7c`) showed the exact base-UNSAT proof
took 46.12 s. Those results invalidate routing the current row through that
stable SAT precheck. They do not erase the historical native-CNF preferred win,
but they mean “switch to SAT” is not an evidence-backed 10-second campaign
candidate without a preferred-specific shape and construction contract.

### 6. Decomposition, SCC, and preprocessing

| Ref / commits | Semantic scope | Operational result | Disposition |
|---|---|---|---|
| merged `experiment/aba-decomposed-prefsat-composition` @ `bb0acab`; planner `3536db3`, routing `dff109c`, bounded metadata `47fdd90`, promotion `a4257aa` | Exact independent product over the ABA proof/contrary incidence graph, simplify, solve components, lift and validate | T8 solved valid on SAT in 28.08 s; T1/T3/T5/T6 reported `component_plan_not_exact` and timed out in backend solving. | **Kept narrow win.** Independent-product decomposition is exhausted for non-exact rows. |
| `e54facf`; current triage `f701c2f` | Grounded/well-founded ABA reduct, fixed-in/out, rule rewriting, support-free ASP facts | Useful on collapsing synthetic structure; current two 600-assumption hard frameworks retain 600/600 assumptions and every rule, covering 0/3 timeout rows. Production Clingo already omits materialized supports. | **Kept capability; dead as current-row candidate.** |
| May stable-only experiments `cd2fd22`/`9cd40ce` (static SCC loop preload) and `0936d01`/`a82c413` (SCC-local founded levels) | SCC-local constraints inside completion/native stable SAT | Both failed and were removed; records are `experiments/2026-05-20-static-scc-loop-preload.md` and `...scc-local-founded-levels.md`. | **Dead for those stable encodings.** They are not a test of directed SCC-recursive preferred conditioning. |
| AF-only Wave B2 `cebb9a9` and later AF SCC-cone refs | SCC-recursive AF solving/acceptance | Successful or measured on AF tasks, not direct ABA SE-PR. Full ABA-to-AF materialization is explicitly rejected as exponential. | **Not ABA SE-PR evidence; cannot be substituted.** |

Exact product decomposition and grounded reduction are therefore not novel.
Directed, conditioned ABA SCC recursion remains semantically distinct from both,
but has no hard-row ABA shape/proof record yet.

### 7. Support preprocessing, learning, solver engines, and abandoned WIP

These commits are material because they invalidate “small mechanical SAT tweak”
suggestions, although most targeted sparse/narrow stable machinery rather than
the current preferred Clingo path:

- `c1cd687` small support nogoods was a kept branch improvement;
  `51afae5` extended supports failed and the smaller behavior was restored.
- `dd9667e`, `5512441`, `721a967`, `c1f8c4` formed the best branch completion-SAT
  baseline (4/5 focused rows, one timeout dominated by PySAT solve), but it was
  never promoted. Support-core reduction `633b72a`/revert `9f3e827` and CaDiCaL
  inprocessing `bd9cf3b`/reverts `105da14`, `8317568` regressed.
- Assumption projection and projected candidate-loop tightening (`59a224b`,
  `bde9d06`) were reverted by `f875e35`, `6799be9`, `54bd9c4`; the profile still
  showed nontrivial CDCL work.
- Learned coverage, singleton conflicts, cached frontiers, and stable seeds
  (`75253fe` through `1c45e01`) did not displace the hard solver bottleneck and
  were superseded by completion SAT.
- Glucose4 was solve-bound; the CaDiCaL195 swap (`8be1ccc`, record branch
  `7e39df8`) was only weakly positive, not promoted. IPASIR-UP observe-all was
  too expensive (`b910d05`); check-only was cheap (`c6846dc`) but the real
  check-model route (`f38493d`, `71f3aa3`, record `90a9f1f`) was slower and
  abandoned.
- Static SCC preload, SCC-founded levels, support-derived phases, greedy stable
  seeds, and stronger support nogoods all have explicit add/remove or revert
  pairs in the May 20 history.
- `exp/aba-satve` @ `777c5ea` is an unmerged measured NO-GO for an alternative
  foundedness encoding on sparse/narrow **stable** solving; it is not an untried
  SE-PR backend.
- `exp/iccma-aba-dcco-100ba-acyc` @ `f21c22f` has 47 unmerged commits, but is a
  DC-CO/acyclic acceptance campaign. Its lazy-CNF/IPASIR work is recorded as too
  slow and cannot be relabeled as an SE-PR attempt.

No committed SE-PR record shows beneficial per-instance batching or parallel
portfolio execution. The kept `--jobs` runner parallelism (`b70a1d6`) improves
campaign throughput across independent rows, but the frozen campaign explicitly
uses `--jobs 1`; it does not improve one witness inside a 10-second row.

## Reconciliation against `experiments/INDEX.md`

The ledger’s current negative judgments are supported by history:

- N1/N2: native stable SAT and base-UNSAT screening do not fit the current cap.
- R1-P1: stable-first has no witness on the exact hard preferred row.
- R1-P2: no generic Clingo built-in configuration survived.
- R1-P3: support-free facts and the grounded reduct already exist and reduce
  none of the hard rows.
- R1-P4: CEGAR re-grounding is not the hotspot.
- H2: direct stable-only deletion was already tried and failed.
- H3-S1: global one-shot `#maximize` was already tried and failed.

Material omissions that should be remembered when selecting candidates:

1. Multi-shot Clingo CEGAR (`466d38d`) is a large historical SE-PR success and
   the baseline being optimized, not an unexplored technique.
2. Exact complete-labelling Z3 PrefSat, native PySAT CNF, and exact-product
   decomposition were all implemented; native CNF and decomposition had narrow
   2025 hard-row wins and remain on main.
3. Persistent assumptions, batching, Horn/bitset closure, and optimizer-first
   candidate selection were already exercised; optimizer-first was reverted.
4. Blanket ASP routing and the boundary-row instability/profile predate the
   current campaign and rule out route-only revival.
5. Several branch-only failed preferred implementations remain reachable by
   refs and must not be mistaken for untouched ideas.

## Candidate suggestions invalidated by history

Do **not** present any of the following as a remaining novel candidate without a
new mechanism-specific contract that distinguishes it from the cited attempt:

- eliminate CEGAR re-grounding or reduce the already-small call count;
- stable-first, direct-stable, or “stable implies preferred” routing;
- global `#maximize`, maximum-cardinality complete sets, or Z3 Optimize seeds;
- greedy maximal growth or direct support-aware preferred CEGAR;
- “real PrefSat,” three-valued complete labelling, native rule closure, or plain
  native CNF/PySAT as if none had been built;
- persistent solver state, assumptions/push-pop, attacker-check batching, Horn
  closure, or bitset closure as standalone ideas;
- blanket ASP/SAT route switching, another generic Clingo configuration sweep,
  CaDiCaL inprocessing, engine-only swaps, or IPASIR check-model callbacks;
- grounded/core-fact preprocessing, support materialization removal, exact
  independent-product decomposition, static SCC loop preload, or SCC-local
  founded levels;
- generic support nogoods, singleton conflicts, coverage refinement, phase
  hints, or greedy seeds without evidence of a new preferred-specific invariant;
- runner `--jobs` parallelism as a per-row SE-PR optimization.

## Genuinely novel SE-PR candidates

Only three candidate families survived the history check, and none is ready for
a solver probe yet:

1. **Directed ABA SCC-recursive preferred conditioning.** This is not the tried
   exact undirected product split and not the AF SCC solver. Evidence gap: a
   committed shape contract for the two current SE-PR timeout rows showing more
   than one useful SCC, a strictly smaller maximum conditioned residual, bounded
   cross-SCC obligations, and an exact assumption-level composition proof.
2. **Small backdoor/cutset conditioning into exact residual components.** No Git
   object implements this for ABA preferred. Evidence gap: committed telemetry
   must find a cutset of size small enough for bounded branching on at least one
   current timeout and prove every branch strictly reduces the residual while
   preserving lift/validation.
3. **Clone/twin/module quotienting with multiplicity-aware lifting.** No history
   commit implements an ABA preferred quotient. Evidence gap: committed hard-row
   telemetry must demonstrate a meaningful quotient ratio on a current timeout,
   followed by a semantic contract proving preferred-witness lift correctness.

Tree-decomposition DP and decomposition-guided SAT/QBF are also literally
unimplemented, but they are omitted from the small candidate list because the
history contains no width measurement showing that either current timeout lies
in a tractable regime. Their first admissible action would be shape telemetry and
a table/formula-width contract, not a solver probe.

## Inventory-freeze selection

**Selected next target family: directed ABA SCC-recursive exact
conditioning/decomposition.** It is the single selected family because it is the
cheapest common falsification target across both hard framework shapes: one
executable semantic contract can kill an invalid composition rule before any
shape measurement, while a valid rule would create the precondition for later
SE-PR and SE-ST residual-shape contracts. The history above distinguishes it
from the already-tried undirected independent product, SCC-local foundedness or
acyclicity encodings, and AF SCC recursion. That distinction establishes only
novelty, not semantic composition or operational usefulness.

The exact next executable semantic composition contract question is:

> For every finite ordinary flat ABA framework in the bounded generated test
> domain, does a directed assumption-dependency/attack SCC recursion with
> explicit predecessor-boundary conditioning return, after lifting, exactly the
> same stable-extension set and exactly the same preferred-extension set as the
> direct semantic oracles, in both directions, including cross-SCC rule and
> contrary dependencies, empty and factual attackers, and branches with no
> extension?

This question must be encoded and answered before any hard-row shape
measurement, operational contract, solver call, benchmark, or source slice.
The other genuinely novel families remain unselected; this freeze does not
authorize work on them.
