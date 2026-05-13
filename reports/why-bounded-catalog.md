# Reduction Tricks: Why the Catalog Is Bounded

*A first-principles argument that the set of useful "convert your problem into a domain a solver can attack" tricks is small — roughly five to twelve entries — and that this is forced by the structure of complexity theory and the structure of solver engineering, not an artifact of fashion.*

---

## 1. Thesis

When a working engineer sits down with a hard combinatorial or logical problem and asks "what should I encode this into?", the honest list of answers is short. It is short because three independent forces conspire to keep it short:

1. The polynomial / counting hierarchy gives a finite set of complexity *cells* a problem can naturally inhabit, and each cell has a cost-effective *target solver* shaped to that cell.
2. The set of background theories with mature decision procedures is small — roughly Boolean, linear arithmetic (rational and integer), bit-vectors, arrays, and uninterpreted functions — and the marginal payoff of inventing a seventh theory drops fast.
3. The structural properties a problem can expose to a solver — flatness, treewidth, symmetry, locality, alternation, counting structure — are themselves a small set, because they correspond to algorithmic regularities that have closed-form algorithms attached to them.

The product of these axes is multiplicative *in principle* but sparse *in practice*: most cells of the cube are either empty or collapse into a neighboring cell. Below I argue the cube has roughly 5–12 occupied cells, name them, and defend the count.

This is a structural argument. It is not "I cannot think of more" — it is "more would have to come from a place we have reason to believe is empty."

---

## 2. Axis 1 — The Complexity Cell

The polynomial hierarchy and the counting hierarchy are not arbitrary. They are forced by quantifier alternation and by the difference between deciding and counting. Each meaningful level has a *canonical complete problem*, and the solver community has, over decades, built a flagship tool for each:

| Cell | Canonical problem | Target solver | Active competition |
|---|---|---|---|
| P | Linear programming, 2-SAT, matching | LP, polynomial-time alg | (no solver competition needed) |
| NP | SAT | CDCL SAT | SAT Competition |
| coNP | Tautology / UNSAT cores | Same SAT engine, different output (UNSAT proof, MUS) | SAT Competition (UNSAT track) |
| Δ_2^P / OptP | MaxSAT, ILP | MaxSAT, MIP | MaxSAT Evaluation, MIPLIB |
| Σ_2^P / Π_2^P | 2QBF | QBF, or CEGAR-over-SAT | QBFEval (2QBF track) |
| PH-complete | k-QBF for unbounded k | QBF | QBFEval (PCNF / QCIR tracks) |
| #P | #SAT, model counting | #SAT, knowledge compilation | Model Counting Competition |
| PSPACE | Planning, model checking, games | Planners, BDD/SAT model checkers | IPC, HWMCC |

That is eight cells, and they are not freely choosable: each is the *coarsest* class whose complete problems show up in real workloads. Levels above Σ_3 essentially never matter in practice — there are technically interesting problems at Σ_3 and above, but solver communities have not formed around them because the workload does not exist. PSPACE is in some sense "the practical ceiling" for solver engineering, because once you have PSPACE-power (QBF, planning, symbolic model checking) you can encode everything in PH below it.

The competition evidence is direct: SAT, MaxSAT, QBFEval, Model Counting, MIPLIB, and the IPC/HWMCC family are the only sustained communities. Communities form when a complexity cell has both (a) a payoff and (b) an engineering surface that rewards specialization. Cells without both — say, Σ_5 — get absorbed by the nearest QBF-shaped neighbor.

**Cell count: 6–8 effective cells.** P collapses out (no solver), and coNP usually collapses into NP (same engine). The non-trivial cells are NP, OptP/Δ_2, Σ_2/Π_2, PH/QBF, #P, PSPACE — six.

---

## 3. Axis 2 — The Theory

Independent of *complexity*, a problem speaks in some *theory*. SMT-LIB has formalized this: the menu of theories supported by competing solvers is small and stable.

- **Pure Boolean** → SAT family.
- **Linear real arithmetic (LRA)** → LP and SMT(LRA). Polynomial in continuous form, NP-hard in mixed form.
- **Linear integer arithmetic (LIA)** → ILP, SMT(LIA). NP-hard in general; the engineering target is branch-and-cut MIP.
- **Bit-vectors (BV)** → SAT-via-bit-blasting, SMT(BV). The point of having a separate theory is local rewriting before bit-blasting, not a fundamentally different solver.
- **Arrays + UF** → SMT theory plug-ins (extensional arrays, congruence closure for uninterpreted functions). These exist as theory glue, not as standalone solvers.
- **Strings, regex** → SMT(STRINGS). Mature enough to be a separate solver category (cvc5, Z3-str).
- **First-order with equality, quantifiers** → first-order theorem provers (Vampire, E, Prover9). The CASC competition tracks this.
- **Higher-order logic, dependent types** → not solver targets; this is the interactive-prover frontier (Coq, Lean, Isabelle). HK-47 notes: there is no decision procedure here; calling Lean a "solver" is a category error.

**Theory count: 5–7.** The diminishing returns are visible. After bit-vectors and arrays, the next theory addition (strings) was a multi-decade gap, and the one after that (transcendentals, nonlinear arithmetic) has only barely produced competitive solvers. The SMT-LIB list is the empirical answer to "how many theories are there?", and it is short because each new theory requires a new decision procedure with an industrial engineering investment.

---

## 4. Axis 3 — The Exploitable Structure

Independent of complexity *and* theory, a problem has *structure* the solver can exploit. The set of structures with a known algorithmic exploit is small:

- **None / flat** → flat encoding, ride the solver's general engine.
- **Bounded treewidth / pathwidth** → dynamic programming, FPT decomposition, tree-clustering.
- **Acyclic / hierarchical / stratified** → stratified Datalog, magic-set rewriting, negation-as-failure with stratification.
- **Symmetric** → symmetry-breaking predicates plus SAT, or graph-isomorphism-aware solvers.
- **Sparse / local constraint structure** → CP solvers with global constraints (alldifferent, table, regular).
- **Counting / probabilistic structure** → BDD / d-DNNF / SDD knowledge compilation, weighted model counting.
- **Game / alternation structure** → CEGAR over SAT, QBF expansion, or game-tree solvers (alpha-beta, MCTS).

**Structure count: 5–7.** Each of these corresponds to a closed-form algorithmic technique with a published meta-theorem (Courcelle for treewidth, the Knowledge Compilation Map for counting, the symmetry-breaking literature for symmetry). The list is short because *structure that admits a polynomial speedup* is itself a rare property of problems — most natural problems have no exploitable structure beyond what CDCL already discovers.

---

## 5. The Cube Is Sparse

The naïve product is 6 × 6 × 6 = 216 cells. The honest count of *occupied* cells — combinations where a real engineering tool exists and is the right answer — is roughly 8–12.

Why so empty? Three collapses:

1. **Theory collapses into Boolean.** Bit-vectors, finite arrays, and bounded LIA all bit-blast to SAT. Most "different theory" cells collapse onto the SAT backbone for any bounded instance, leaving only the unbounded / continuous cases as genuinely separate.

2. **Structure collapses into the solver.** CDCL implicitly exploits backbone variables, autarkies, community structure. Modern MIP exploits sparsity. The "structure axis" is mostly about *which structural properties you must explicitly encode* because the solver will not find them on its own — symmetry, counting, alternation. Treewidth-based DP is a separate target *only* for problems where treewidth is small enough to dominate.

3. **Higher PH levels collapse into QBF or CEGAR.** Σ_2 through Σ_k all map to the same QBF technology, with CEGAR-over-SAT as the practical alternative. There is one cell, not k cells.

After collapses, the catalog is the cross-product of *active* (cell × tool) pairs:

- (NP, Boolean, any) → SAT
- (OptP, Boolean or LIA, any) → MaxSAT or MIP
- (Σ_2 / PH, Boolean, alternation) → QBF or CEGAR
- (#P, Boolean, counting structure) → #SAT or knowledge compilation
- (NP, LIA / mixed, sparse) → MIP / CP
- (NP, SMT theories, mixed) → SMT
- (NP, hierarchical / nonmonotonic, recursive) → ASP / Datalog
- (PSPACE, action-and-state, bounded horizon) → planners or BMC
- (decidable FOL, equality) → first-order theorem prover
- (any, low treewidth) → FPT / DP

That is ten. Adding two convenient siblings (BDDs as a stand-alone target for symbolic reachability; LP as a stand-alone target whenever the relaxation is the whole answer) gives twelve.

---

## 6. Why the Catalog Converges

Two forces beyond complexity theory pin the count down:

**Solvers compete at fixed points.** A mature solver community is an equilibrium between problem supply and engineering investment. CDCL took roughly thirty years to mature; MIP took fifty; SMT took twenty; ASP took twenty. New target categories appear only when an *unexploited structural property* becomes important enough to merit a dedicated engine — knowledge compilation rose in the 2000s precisely because probabilistic-inference workloads exposed a counting structure that #SAT could not exploit efficiently. Without such a forcing function, no new category emerges, because re-routing through SAT is almost always cheaper than building a new solver.

**Reduction is transitive and the graph has sinks.** SAT is a sink for the decision problems in NP. ILP is a sink for optimization problems with linear structure. QBF is a sink for PH. The "sinks" of the reduction graph attract investment, and once a sink exists, building anything that reduces *to* it is more cost-effective than building a new sink. The catalog is small because *good sinks are rare* — they require both completeness for a class and an engineering surface (CNF for SAT, LP-relaxable structure for MIP, prenex form for QBF) that supports decades of optimization.

---

## 7. Counterargument: Isn't the Catalog Actually Larger?

An honest skeptic will list more candidates. Engage them:

- **Planning, model checking** → these are *application packages* on top of SAT/QBF/BDD/explicit-state search. Modern planners are SAT-based (SATPlan), heuristic-search-based (FF, LAMA), or symbolic (BDD-based). Model checking is BDD-based, SAT-based (BMC, IC3), or explicit-state. They do not introduce a new *target representation*; they reuse the cells we already named.

- **Probabilistic inference** → variable elimination is dynamic programming, belief propagation is message-passing on a tree decomposition, and exact inference compiles to d-DNNF. These map onto the FPT and knowledge-compilation cells.

- **Theorem proving (FOL, HOL)** → first-order is its own cell (CASC). HOL is interactive and *not* a solver target — it is a proof-assistant frontier. The line is sharp because HOL is not even semi-decidable.

- **Neural reasoning / LLM-as-solver** → these do not fit the cube because they are *not solvers* in the relevant sense. They are heuristics with no completeness or soundness guarantee. They are properly classified as preprocessing (problem reformulation, candidate generation) feeding into one of the cells, not as a cell themselves. When LLMs have been integrated successfully (e.g., for SAT instance generation, ILP modeling assistance), they have served as *encoders* into the existing catalog — confirming the catalog rather than expanding it.

- **MCMC / gradient methods** → these are *approximate* solvers, a different game. The cube as drawn is for exact / sound reductions. Approximate methods deserve their own cube, smaller still: MCMC, variational inference, gradient descent, and a handful of metaheuristics (SA, GA, tabu). They are sufficiently different in semantics (no soundness guarantee, no UNSAT certificate) that they are not substitutable for the exact catalog.

- **Domain-specific solvers (chess, SAT-modulo-X, Sudoku)** → these are specializations within a cell, not new cells. A chess engine is a game-tree solver with hand-tuned heuristics; it is the (PSPACE, alternation, structure) cell, not a thirteenth entry.

- **Hybrid / portfolio solvers** → portfolios are meta-strategies *over* the catalog. They confirm the catalog's shape (you need finite portfolio members) rather than expand it.

The skeptic's list, examined one by one, dissolves into the existing cells.

---

## 8. Honest Caveats

The thesis is bounded:

- **The catalog grows when computing changes.** GPUs made gradient-based optimization a serious option for large-scale combinatorial problems. Quantum annealing introduced QUBO as a reduction target with its own competitions. The catalog is not eternal; it is the catalog *for current commodity hardware*.

- **The line between "solver" and "preprocessor" is fuzzy at the edges.** Constraint propagation, symmetry breaking, preprocessing in MIP — these are integral to the solver, but they are also algorithms in their own right. The catalog counts decision-procedure backends, not preprocessing techniques.

- **Approximate solvers have a parallel small catalog.** I asserted six to twelve for the *exact* family. The approximate family — MCMC, variational, SDP relaxations, Lagrangian relaxation, gradient — is a separate axis I did not fully develop here. It, too, is bounded and small, for the same structural reasons.

---

## 9. Verdict

**There are approximately ten distinct useful reduction tricks in the exact-solver catalog, with two more on the boundary.** The canonical list:

1. **SAT** — for any NP-decision problem with finite Boolean encoding. The default sink.
2. **MaxSAT** — for OptP problems with weighted soft constraints over a Boolean structure.
3. **MIP / ILP** — for OptP problems with linear arithmetic structure and natural LP relaxations.
4. **SMT** — for NP problems whose natural language is a combination of theories (LIA, BV, arrays, UF, strings).
5. **CP with global constraints** — for NP problems with rich combinatorial substructure (sequencing, scheduling) where global constraints amortize propagation.
6. **ASP / Datalog** — for problems with recursive, hierarchical, or nonmonotonic structure (default reasoning, transitive closure, stable-model semantics).
7. **QBF** — for problems genuinely at Σ_2 or higher in the PH (synthesis, two-player games, conformant planning).
8. **CEGAR over SAT** — the practical sibling of QBF for problems with one or two quantifier alternations and a natural refinement loop.
9. **#SAT / weighted model counting** — for #P problems and probabilistic inference.
10. **Knowledge compilation (BDD, d-DNNF, SDD)** — for problems requiring repeated queries, exact counting, or compact symbolic representation.

Honorable mentions:

11. **First-order theorem proving (Vampire, E)** — for decidable / semi-decidable fragments of FOL with equality.
12. **FPT / treewidth DP** — for problems with a small structural parameter that dominates input size.

That is twelve. Q's intuition was right: the catalog is small, finite, and bounded by the structure of complexity theory and the economics of solver engineering, not by the imagination of researchers. New entries appear only when a new structural property becomes economically important enough to merit decades of dedicated engineering investment, and such events occur on the timescale of generations, not years.

The number ten is defensible; twelve is generous; twenty would be padded with sub-cases or with things that are not solvers. Anyone selling a thirteenth must show either a new complexity cell, a new theory with a real decision procedure, or a new structural property with a closed-form exploit. Until then, the catalog is closed.
