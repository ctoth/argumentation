# Reduction Tricks: Mapping Problems to Solver-Friendly Domains

*Structural preconditions on the source problem that make a reduction **practical**, not merely possible.*

---

## Why "Cook-Levin says yes" is the wrong starting point

Every problem in NP reduces to SAT in polynomial time. This fact is useless for engineering. What we actually want is: when does the reduction (a) keep the encoded instance small relative to the natural input size, (b) preserve enough source structure that the solver's heuristics — VSIDS, clause learning, propagator scheduling, Simplex pivots — can exploit it, and (c) terminate in seconds rather than centuries?

Each target solver answers a different existential or counting question and propagates over a different algebraic structure. A reduction is "useful" exactly when the source already has the structural invariant the target was built to exploit. Everything else is paying CNF blowup or theory-overhead for nothing.

What follows: one section per **structural property of the source problem**. For each — the invariant, an example that has it, an example where it fails, the canonical encoding pattern, and the failure mode when applied wrong.

---

## 1. Polynomial-size witness with classical truth-value semantics → SAT

**Invariant.** A "yes" instance has a certificate polynomial in the input, encodable as a Boolean assignment, with a *single-quantifier* verifier ("there exists an assignment such that all constraints hold"). No alternation. No hidden minimality. No counting.

**Has it.** *k*-coloring; bounded-horizon classical planning (SATPlan); CDCL-style hardware bug-finding.

**Doesn't have it.** Skeptical reasoning under preferred semantics is Π_2 (∀ extension. argument is in). Encoding it as flat SAT requires explicit co-NP simulation (see §5).

**Canonical pattern.** Tseitin transformation: replace each subformula or gate with a fresh variable plus a constant-size clausal definition, linear in circuit size, equisatisfiable. Plaisted-Greenbaum is the polarity-aware refinement: only generate the implication direction the polarity demands — fewer clauses, same satisfiability.

**Win condition.** The source decomposes into a polynomial number of *local* checks, each expressible as a constant-size clause. If expressing one constraint already needs nontrivial encoding tricks, you are paying for the wrong solver.

---

## 2. Polynomial-size witness plus a linear objective → MaxSAT / PB / ILP

**Invariant.** Boolean witness as in §1, plus a single linear functional (or sum of weighted soft clauses) to maximize or minimize. Not a min-max, not a quantile, not a fraction.

The interesting choice is *which* of MaxSAT / pseudo-Boolean / ILP, and it depends on the ratio of combinatorial-to-arithmetic structure:

- **MaxSAT** wins when constraints are mostly clausal and the objective is a sum of unit weights on soft clauses; CDCL conflict analysis still drives search. MaxSAT evaluations show SAT-based solvers dominate on industrial-shaped instances.
- **Pseudo-Boolean** wins when constraints themselves involve linear arithmetic over Booleans (cardinality, knapsack-shaped). Native cutting-plane reasoning is exponentially stronger than any clausal encoding of `sum(x_i) ≤ k` for large `k`.
- **ILP** wins when variables are genuinely integer (not just Boolean), the LP relaxation is tight enough to give useful dual bounds, or the instance has the arithmetic regularity (matchings, flows, large-coefficient set cover) that Simplex collapses cheaply. ILP dominates on "crafted" instances; MaxSAT dominates on industrial.

**Has it.** Weighted vertex cover, MaxCut, weighted set cover, scheduling with sum-of-completion-time.

**Doesn't have it cleanly.** Lexicographic / leximax objectives need successive solver calls or special encodings. Linear-fractional objectives don't fit at all.

**Failure mode.** Encoding `sum x_i ≤ k` as raw clauses (binomial encoding is O(n^k)). Throwing pure-Boolean problems at ILP, where LP relaxations are 0/1-trivial and the solver collapses to plain branch-and-bound on a fundamentally clausal instance.

---

## 3. Monotone fixed-point / least-model semantics → Datalog (and stratified ASP)

**Invariant.** Semantics is "smallest set of facts closed under finite derivation rules." Once derived, a fact stays derived; rules never retract. The operator T_P that maps fact-sets to fact-sets is monotone, and the answer is its least fixed point.

Bottom-up evaluation with semi-naive optimization is polynomial in the database size and exponential only in rule size. Implementations are well-understood.

**Has it.** Reachability, transitive closure, same-generation, parsing as fixed-point (Earley), Andersen-style points-to analysis, type inference for HM-like systems.

**Doesn't have it.** Anything requiring negation under "if not derivable, assume false" *with cycles through negation*: stratified Datalog is fine, but `p :- not q.` and `q :- not p.` makes T_P non-monotone, the least fixed point doesn't exist, and you need ASP (§4).

**Canonical pattern.** Magic sets for query-directed evaluation; semi-naive evaluation to avoid O(n²) re-derivation per round.

**Structural test.** Can each rule be written `head :- body` with no negated body literals and a *conjunctive* body over already-derived facts? If yes, Datalog. If you need "the answer is the model where as little as possible is true beyond what's forced," you've crossed into §4.

---

## 4. Nonmonotonic minimality / closed-world default → ASP

**Invariant.** The semantics requires "the model where as little as possible is true beyond what's forced," and/or default negation that can be retracted by later derivations. Operationally, a stable model is a fixed point of the *Gelfond-Lifschitz reduct*: drop the negative literals satisfied by a candidate model, then check the reduct's least model equals the candidate.

This is the disqualifying property for Datalog. Once minimality matters, monotone fixed-point gives you the wrong answer — you need a solver that searches over candidate models.

**Has it.** Diagnosis ("minimal failed components explaining symptoms"); conformant planning with default initial conditions; minimal hitting sets, minimum-cardinality model repair; AF stable extensions are exactly stable models of a tiny ASP program (`in(A) :- not out(A)` plus attack constraints) — the minimality is intrinsic, not bolted on.

**Doesn't have it.** Problems wanting *all* models (use #SAT, §6) or particular optima over a linear objective (often MaxSAT/PB/ILP outperform `#minimize` when the objective dominates).

**Canonical pattern.** Generate-define-test: a `{p(X) : domain(X)}` choice rule generates candidate truth values; deterministic rules define derived facts; integrity constraints `:- bad_combination` rule out violators. The solver does CDCL over choice atoms with unfounded-set propagation handling minimality.

**Failure mode.** Encoding a truly monotone problem in ASP because the syntax is convenient — you pay for unfounded-set machinery and the reduct check for nothing. Use stratified Datalog where possible.

---

## 5. Quantifier alternation (Σ_k^P / Π_k^P) → QBF

**Invariant.** The decision question has the form "∃X ∀Y ∃Z … φ(X,Y,Z,…)" with at least one alternation. A flat SAT encoding requires either exponentially expanding the inner quantifier (for every value of the universal, instantiate the inner existential) or encoding co-NP witnesses inside SAT via tricks that, while polynomial, force the solver to rediscover the alternation structure with no help from CDCL.

**Has it.** Two-player games with bounded horizon. Adversarial planning. Strategy synthesis. Skeptical preferred semantics in argumentation (Π_2^P). Abductive reasoning (∃ explanation ∀ consistent completion). Symbolic test pattern generation under don't-care universals.

**Doesn't have it.** Plain existential search; nothing to gain by adding a vacuous universal.

**Canonical pattern.** Native QBF in QDIMACS prefix form, alternating quantifier blocks over a CNF matrix. Modern QBF solvers split into:
- *Search-based with learning:* CDCL generalized with both clause and *cube* learning (cube = universal-side dual).
- *Expansion-based:* instantiate universals when their count is small.
- *CEGAR:* treat inner quantifiers as oracles; refine on each spurious witness. Effective when most universal assignments are "obvious."

**Failure mode.** Tseitin-flatten then quantifier-eliminate inside SAT — exponential worst-case and discards the prenex structure QBF solvers exploit. Reverse failure: throwing pure-existential SAT at a QBF solver pays the QBF overhead for nothing (empty universal block degenerates to a slower SAT solver).

---

## 6. Counting / weighted volume → #SAT, knowledge compilation, ProbLog

**Invariant.** The question is not "does a witness exist" but "how many," or "what is the total weight (sum of products) over witnesses." The answer is in #P, not NP. Decision-only solvers cannot answer it without enumerating.

**Has it.** Probabilistic inference in Bayesian networks (marginalization is weighted model counting over a network encoding). Probabilistic logic programming (ProbLog reduces to weighted model counting). Probabilistic argumentation: probability of an argument's acceptance under a distribution over sub-AFs is a #SAT instance. Reliability under independent edge failures.

**Doesn't have it.** Pure decision problems where one witness suffices.

**Canonical pattern.** Two approaches:
- *Direct #SAT:* component-caching CDCL with model counting; works when components are small and reusable.
- *Knowledge compilation:* compile once into a tractable target language — d-DNNF, SDD, OBDD — that supports weighted model counting in time linear in compiled size. Compile is expensive (and can blow up); queries are then trivial. Win condition: many queries on the same model, or bounded "circuit complexity" in the target language.

**Failure mode.** Compiling a formula with no decomposable structure: d-DNNF explodes; never reach query time. Conversely, running #SAT on a decision problem pays counting overhead for a yes/no answer, and counting CDCL has worse decision-finding heuristics because it can't terminate on first witness.

---

## 7. Theory-rich constraints (arithmetic, arrays, bit-vectors, strings) → SMT

**Invariant.** Constraints mention objects that are not Boolean: integers with arithmetic, real-valued linear (or nonlinear) constraints, arrays with select/store, fixed-width bit-vectors, strings with length and concatenation. A pure SAT encoding must "bit-blast," losing the algebraic structure that domain-specific decision procedures exploit.

**Has it.** Software verification with integer variables (LIA / LRA). Hardware verification at the bit-vector level (sometimes — see failure mode). Constraint solving over arrays and uninterpreted functions in program analysis. String solving for sanitizer analysis.

**Doesn't have it.** Pure combinatorial problems where every constraint is naturally Boolean — SMT still works but you pay dispatch overhead for no theory work.

**Canonical pattern.** DPLL(T): a SAT solver searches over the Boolean abstraction, calling a theory solver when a candidate is propositionally consistent. Theory solvers: Simplex for LRA, Gomory cuts for LIA, congruence closure for uninterpreted functions, lazy bit-blasting for bit-vectors when bit-vector reasoning fails.

**Failure mode.** Bit-blasting LIA into SAT: a single 32-bit addition becomes ~100 clauses and destroys the chance for Simplex to do its job in O(constraints) per pivot. Inverse: very *narrow* bit-vectors (4 or 8 bits) may be faster bit-blasted than handed to a bit-vector decision procedure, because solver overhead exceeds CNF-handling cost at that scale. SMT only beats SAT-with-bit-blasting when the theory genuinely exploits structure.

---

## 8. Structural sparsity / bounded treewidth / acyclicity → FPT, dynamic programming, BDD

**Invariant.** The source has an underlying graph (constraint graph, primal/incidence graph of a CSP, AF attack graph, planning dependency DAG) whose treewidth, branchwidth, or related width parameter is bounded by a small constant — or at least small relative to instance size. By Courcelle's theorem and descendants, any MSO-expressible property is decidable in linear time (in the instance) with a constant factor that is a tower in the treewidth and the formula size.

**Has it.** Many real-world planning instances. Argumentation frameworks from real debates often have small treewidth (Dvořák and others have shown FPT tractability for several semantics under treewidth). Junction trees in Bayesian inference. Bounded-grammar parsing.

**Doesn't have it.** Random k-SAT, dense random graphs, cryptographic instances designed structureless — treewidth ≈ n, base-case tables of size 2^n.

**Canonical pattern.** Compute a tree decomposition (heuristic — optimal treewidth is NP-hard, but min-fill and hybrids do well). Walk bottom-up, maintaining a table over partial assignments to the "bag" at each node. Table size `2^treewidth × poly(n)`. Per-bag operations can be handed to a SAT, ASP, or #SAT engine — this is "decomposition-guided reduction," used by tools like dynASP and treewidth-aware AF solvers.

**Failure mode.** Encoding a tree-decomposable problem with the natural flat SAT encoding: CDCL doesn't see the tree structure and rediscovers it (poorly) via conflict analysis. The instance solves, but you've paid `2^n` worst-case where `2^k × n` was available.

**Structural test.** Extract the constraint hypergraph; run a treewidth heuristic. Small number → FPT structure. Near n → no.

---

## 9. Constraint compositionality with global constraints → CP

**Invariant.** The problem is naturally written in terms of high-level constraints whose individual semantics admit a *custom propagator* that prunes the domain far more than any clausal encoding could: `alldifferent` (matching-based bounds propagator achieves arc consistency in O(n^2.5)); `cumulative` (energetic reasoning for resources); `circuit` (Hamiltonicity with reachability pruning); `regular` (membership in a finite-automaton language with NFA propagation).

**Has it.** Job-shop scheduling (`cumulative` over machines, `disjunctive` over jobs). Vehicle routing (`circuit` plus `cumulative` for capacity). Personnel timetabling (`alldifferent` plus `regular`). Sudoku, n-queens, Latin squares (`alldifferent`).

**Doesn't have it.** Naturally clausal problems — every constraint already a small disjunction. CP brings overhead (propagator dispatch loop, the trail) that pays only when propagators prune more than unit propagation.

**Canonical pattern.** Express each high-level constraint as a global with a known propagator; use CP branching heuristics (`first-fail`, `dom/wdeg`); use lazy clause generation in modern hybrids (Chuffed, Choco) for CDCL-style learning while keeping global propagators.

**Failure mode.** Decomposing globals into clauses for SAT — `alldifferent` decomposed pairwise loses the matching-based reasoning, and SAT re-derives the same arc-consistency conclusions one conflict at a time.

---

## 10. Symbolic reachability over states with shared structure → BDD / symbolic methods

**Invariant.** The state space is huge (`2^n` for `n` Boolean state variables), but the *transition relation* and *set of reachable states* both have compact symbolic representation — typically a BDD whose size depends on variable ordering and state-space regularity rather than enumeration.

**Has it.** Hardware model checking of synchronous circuits (canonical BDD success story for two decades). Reachability in bounded counter systems. Symbolic game solving (μ-calculus model checking). Planning with regular structure where states share local descriptions.

**Doesn't have it.** State spaces with no symbolic regularity — BDD blows up to enumeration. Deep counterexample search where you only want one bug, not the full reachable-state set (SAT-based BMC dominates here precisely because it doesn't insist on representing all reachable states).

**Canonical pattern.** Encode initial states, transition relation, and target as BDDs over present-state and next-state variable copies. Iterate `image = ∃present-vars (transition ∧ current-image)` until a fixed point. Variable ordering is everything — bad orderings turn linear-size BDDs into exponential-size BDDs for the same Boolean function.

**Failure mode.** Choosing BDDs for problems with no Boolean-function regularity — modern verification largely shifted to SAT-based BMC and IC3/PDR for exactly this reason: bug-finding wants one path, not the closed reachable set.

---

## Synthesis

### Decision tree

Walk this top-down on the source problem:

1. **Quantifier alternation (∃∀ or deeper)?**
   → Yes: QBF (or DQBF for branching dependencies). Don't flatten.
   → No: continue.

2. **Answer is a count, sum-of-weights over witnesses, or probability?**
   → Yes: #SAT for one-shot; knowledge compilation (d-DNNF / SDD) for repeated queries on the same model.
   → No: continue.

3. **Linear (or pseudo-Boolean) objective over Boolean witnesses?**
   → Yes: MaxSAT for clausal-dominated structure; PB for cardinality-heavy; ILP for genuinely-integer or LP-tight instances.
   → No: continue.

4. **Theory-rich constraints (arithmetic, arrays, bit-vectors, strings)?**
   → Yes: SMT with the matching theory. Bit-blast only if widths are very narrow.
   → No: continue.

5. **Semantics demands minimal-model / nonmonotonic / default-negation reasoning?**
   → Yes: ASP. Don't bolt minimality onto SAT manually.
   → No: continue.

6. **Answer is the least fixed point of monotone derivation rules?**
   → Yes: Datalog (or stratified ASP). Bottom-up with semi-naive evaluation.
   → No: continue.

7. **Constraint hypergraph has small treewidth or other width?**
   → Yes: FPT decomposition + per-bag SAT/ASP/#SAT. Or BDD if Boolean-function regularity is also present.
   → Continue regardless: also check (8).

8. **Constraints are naturally global (`alldifferent`, `cumulative`, `circuit`)?**
   → Yes: CP. Don't decompose globals to clauses.
   → No: SAT (CDCL via Tseitin / Plaisted-Greenbaum).

The order matters. Quantifier alternation is checked first because it disqualifies everything below it as a useful target — any flat reduction loses the essential structure. Counting comes before objectives because counting is in #P, strictly above NP. Theory richness comes before nonmonotonicity because SMT can't easily handle nonmonotonic minimality, but ASP can encode bounded arithmetic awkwardly; pick the solver whose *primary* capability matches your *primary* difficulty.

### The "wasted reduction" failure modes

Cases where the reduction is technically valid and uselessly inefficient:

- **Bit-blasting LIA into SAT.** Loses Simplex; turns each integer addition into ~100 clauses; CDCL rediscovers arithmetic facts as conflicts.
- **Flattening QBF to SAT via Tseitin-then-quantifier-elim.** Worst-case exponential blowup; discards prenex structure that CEGAR-based QBF solvers exploit.
- **Decomposing globals to clauses for SAT.** `alldifferent` pairwise loses the matching propagator; CDCL learns one conflict at a time what the matching algorithm sees in O(n^2.5) up front.
- **Pseudo-Boolean cardinality via binomial encoding.** O(n^k) clauses for `at-most-k`. Use sequential counter or totalizer if you must encode in CNF; better, a PB solver with native cutting planes.
- **Using #SAT for a decision problem.** Counting overhead for a yes/no answer; counting CDCL has worse decision-finding heuristics because it can't terminate on first witness.
- **Encoding a treewidth-bounded problem with flat SAT.** CDCL doesn't see the decomposition; FPT machinery would solve in `2^k × n` instead of worst-case `2^n`.
- **BDD reachability on a structureless instance.** BDD blows up to enumeration; SAT-based BMC would find a counterexample in seconds.
- **ASP for a monotone fixed-point problem.** You pay for unfounded-set propagation and reduct checking when stratified Datalog computes the answer bottom-up in linear time.
- **Compiling to d-DNNF a formula with no decomposable structure.** Compile time exponential; never reach the (cheap) query phase.
- **SMT for purely Boolean problems.** Theory-dispatch overhead with no theory work to dispatch.

The unifying principle: each target solver is built around exploiting a specific structural property. A reduction that preserves that property is a useful trick. A reduction that destroys the property — by flattening, decomposing, or bit-blasting — leaves the solver running on the encoding's complexity rather than the source's structure, which is what Cook-Levin already promised would technically work.

The engineering question is not "which target *can* encode my problem" — almost all of them can — but "which target's exploited structure is *already present* in my source." Match the structure first; the encoding is the easy part.
