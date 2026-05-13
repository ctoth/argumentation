# Reduction Targets: A Catalog of Solver-Friendly Domains

*Companion to "Reduction Tricks: Mapping Problems to Solver-Friendly Domains."
This half enumerates the destinations — the formalisms a problem can be
**reduced into** — without arguing over when to choose which.*

For each target the layout is fixed:

1. **Native shape** — what kind of question the formalism literally asks.
2. **Expressiveness ceiling** — the worst-case complexity class it captures.
3. **Mature solvers** — one or two flagship engines.
4. **Characteristic source-problems** — what naturally lands here.

---

## 1. SAT (CDCL)

**Native shape.** A *decision* problem: given a Boolean formula in CNF, does
there exist a truth assignment satisfying every clause? The answer is one bit
plus, optionally, a witness assignment. There is no notion of "best" model and
no quantifier alternation.

**Expressiveness ceiling.** **NP-complete** by Cook–Levin. Anything in NP can be
polynomially reduced to SAT, which is exactly what makes it the lingua franca of
combinatorial reasoning.

**Flagship solvers.** **Kissat** and **CaDiCaL** (Biere et al.) dominate the
recent SAT Competitions; **Glucose** and the historical **MiniSat** remain
common embedded back-ends. All are CDCL: conflict-driven clause learning with
VSIDS branching, restarts, and clause-database management.

**Characteristic source-problems.** Bounded model checking of finite-state
hardware, equivalence checking of combinational circuits, classical planning
under a fixed horizon (SATplan), graph colouring, k-SAT-style cryptanalysis,
and the existence half of essentially every NP problem (Hamiltonian cycle,
3-colouring, subgraph isomorphism). When a problem says "does *some* witness
exist?" and the witness is polynomial-size, SAT is the default landing zone.

---

## 2. MaxSAT (partial / weighted)

**Native shape.** *Optimization.* Clauses split into hard (must hold) and soft
(weighted, may be violated). Find an assignment satisfying all hard clauses
that minimises total weight of violated soft clauses. Witness plus optimal
cost.

**Expressiveness ceiling.** Function-class **FP^NP** (equivalently the
optimisation analogue of NP); the decision version "is the optimum ≤ k?" is
NP-complete and the search version is complete for OptP / Δ₂^P under standard
reductions.

**Flagship solvers.** **EvalMaxSAT** and **UWrMaxSat** consistently medal in
the [MaxSAT Evaluation 2024](https://maxsat-evaluations.github.io/2024/);
**RC2** (PySAT) and **Open-WBO** are the standard library back-ends. Modern
solvers are core-guided (OLL, PMRES) on top of a CDCL SAT engine.

**Characteristic source-problems.** Maximum-likelihood decoding, Boolean
group-testing, fault localisation in software, minimum-correction-set / MUS
extraction, package-manager dependency resolution, scheduling with soft
preferences, and any "satisfy these constraints; minimise these violations"
formulation. Crucially: any problem expressible as "find an extension that
maximises some count" lives here.

---

## 3. Pseudo-Boolean (PB) / 0–1 ILP-lite

**Native shape.** Decision **and** optimisation over linear inequalities on
0/1 variables: clauses generalise to ∑ aᵢ xᵢ ≥ b. Optionally minimise a linear
objective ∑ cᵢ xᵢ. Native cardinality and "at-most-k" constraints without the
exponential CNF blow-up.

**Expressiveness ceiling.** **NP** for the decision version, **NP-optimisation**
for the cost version — same class as MaxSAT and ILP, but with a stronger proof
system: cutting planes (used by RoundingSat) is exponentially more concise than
resolution on certain families (e.g. pigeonhole).

**Flagship solvers.** **RoundingSat** (MIAO group) — by 2024 the kernel inside
~9 of the top 12 entries in the
[Pseudo-Boolean Competition](http://www.cril.univ-artois.fr/PB24/) — and
**Sat4j** as the JVM/Eclipse-embedded reference implementation. SCIP-based PB
solvers also compete strongly.

**Characteristic source-problems.** Cardinality-heavy combinatorial design,
Eclipse plugin dependency solving (the original Sat4j use-case), some MIP
benchmarks recast as 0/1, max-clique, and any problem whose constraints are
naturally "at least k of these atoms hold." When you find yourself encoding
"exactly-k" with sequential counters in CNF, PB is the more honest target.

---

## 4. #SAT / Model Counting

**Native shape.** *Counting.* Given a CNF, output |{satisfying assignments}|.
Weighted model counting (WMC) generalises: each literal carries a weight and
output ∑_{models} ∏_{literals true} weight(literal).

**Expressiveness ceiling.** **#P-complete** (Valiant). Strictly harder than NP
under standard assumptions: Toda's theorem places PH ⊆ P^#P. Approximate
counting with (ε,δ) guarantees sits in **BPP^NP**.

**Flagship solvers.** **Ganak** (Soos & Meel) — exact, won every track of the
[2024 Model Counting Competition](https://mccompetition.org/assets/files/2024/MC2024_awards.pdf);
**ApproxMC** for approximate counting via XOR-hashing; **sharpSAT-TD** as the
classic exact baseline. Compilation back-ends (c2d, dsharp, D4) compile to
d-DNNF and count in linear time over the circuit.

**Characteristic source-problems.** Probabilistic inference (Bayesian network
marginals via WMC), reliability analysis, network reachability under failures,
quantitative information-flow, neural-network verification volume, and
*credulous-vs-sceptical-with-cardinality* reasoning. Any time the question is
"how many" rather than "whether," #SAT is the target.

---

## 5. QBF — Quantified Boolean Formulas

**Native shape.** Decision over a *quantifier-alternated* Boolean formula:
∃X₁ ∀X₂ ∃X₃ … φ. Models games, two-player adversarial situations, and
"forall-exists" specifications.

**Expressiveness ceiling.** **PSPACE-complete** for the unbounded case; with a
fixed prefix of k alternations the problem is complete for the k-th level Σ_k^P
(or Π_k^P) of the polynomial hierarchy. So Σ_2^P (one ∀ inside one ∃) is
exactly 2-QBF.

**Flagship solvers.** **CAQE** and **QuAbS** (Tentrup, Rabe) — abstraction-
based, recent [QBFEVAL winners](https://www.qbflib.org/index_eval.php) in
prenex CNF and prenex non-CNF tracks respectively; **DepQBF** (Lonsing) as the
canonical search-based QCDCL solver.

**Characteristic source-problems.** Reactive synthesis from LTL specs,
two-player game solving, conformant planning, controller synthesis,
symbolic CEGAR for hardware verification, and Σ_2^P-complete fragments such as
**stable** and **semi-stable** semantics in abstract argumentation, certain
modal-logic satisfiability problems, and minimisation/uniqueness questions
("does there exist an X such that for all Y …").

---

## 6. SMT — Satisfiability Modulo Theories

**Native shape.** Decision over first-order formulas where atoms come from
**theories** beyond pure Booleans: linear integer arithmetic (LIA), linear real
arithmetic (LRA), bit-vectors (BV), arrays, algebraic datatypes, strings,
non-linear real arithmetic (NRA), uninterpreted functions (UF). The Boolean
skeleton is handed to a CDCL core; theory atoms are checked by specialised
solvers in a DPLL(T) loop (Moura & Bjørner, [Z3 description](
file:///C:/Users/Q/code/propstore/papers/Moura_2008_Z3EfficientSMTSolver/description.md)).

**Expressiveness ceiling.** **Theory-dependent.** QF_LIA / QF_BV are
NP-complete; QF_LRA is in P; QF_NRA is decidable but doubly-exponential
(CAD); strings + length is undecidable in general; quantifiers push you out of
decidability for many theories.

**Flagship solvers.** **Z3** (Microsoft) and **cvc5** (Stanford / Iowa) are the
two giants; **Yices2** is the speed-king for QF_LIA / QF_BV. Optimisation
extensions exist as **νZ** in Z3 and **OptiMathSAT** for MathSAT5.

**Characteristic source-problems.** Program verification (Dafny, Why3, F\*),
symbolic execution (KLEE), test-case generation, Hoare-logic VC discharge,
constraint-based type inference, refinement-type checking, and any problem
naturally expressed in mixed logic + arithmetic + arrays where pure SAT would
require a bit-blasting blow-up.

---

## 7. ASP — Answer Set Programming

**Native shape.** Find **answer sets** (stable models) of a normal/disjunctive
logic program with negation-as-failure. Native shape is *enumerating models*,
but the engine handles decision (existence), optimisation (`#minimize`), and
brave/cautious reasoning uniformly.

**Expressiveness ceiling.** **Σ_2^P-complete** for disjunctive ASP with
negation; **NP-complete** for normal logic programs without disjunction.
Optimisation pushes one level higher in Δ.

**Flagship solvers.** **clingo** (Potassco, Gebser et al.) — grounder *gringo*
plus solver *clasp*, the de-facto standard; **DLV** for disjunctive programs
with strong front-ends (DLV2). Both ground first-order rules to propositional
ASP and run a CDCL-like *conflict-driven nogood learning* search.

**Characteristic source-problems.** Combinatorial configuration, planning with
non-trivial control knowledge, biological pathway reasoning, ontology repair,
phylogenetic tree inference, and almost every benchmark used in the
*ICCMA argumentation competitions* — abstract-argumentation semantics map
cleanly because stable models match the fixpoint flavour of admissibility.

---

## 8. Datalog (and stratified extensions)

**Native shape.** *Bottom-up deductive closure.* Given a set of Horn rules and
a set of facts, compute the (finite) least fixpoint — i.e. all derivable atoms.
Natural shape is *materialised query answering*, not search.

**Expressiveness ceiling.** Polynomial-time data complexity; **EXPTIME**
combined complexity. Plain Datalog captures exactly the queries computable in
polynomial time on ordered structures (Immerman–Vardi). Stratified negation
and aggregation stay polynomial; recursive aggregation with arbitrary lattices
can climb higher.

**Flagship solvers.** **Soufflé** (Oracle, originally for static analysis) —
compiles to C++ and scales to billions of tuples; **RDFox** (Oxford
Semantic) — main-memory parallel materialisation with stratified negation,
aggregation, SWRL-style rules.

**Characteristic source-problems.** Static program analysis (Doop's
points-to, Datalog disassembly, taint analysis), graph reachability and
transitive-closure queries, deductive databases, SPARQL/OWL2-RL reasoning,
network management (Network Datalog), declarative networking, and any problem
naturally framed as "compute the closure under these rules."

---

## 9. ILP / MILP

**Native shape.** *Optimisation.* Minimise (or maximise) **c·x** subject to
**Ax ≤ b** with some or all xᵢ integer. Pure LP relaxation is solved at every
node of a branch-and-cut tree.

**Expressiveness ceiling.** **NP-hard** (decision NP-complete); pure LP is in
P. MILP gives both decision and optimisation in one frame, with continuous
variables built in.

**Flagship solvers.** **Gurobi** and **CPLEX** as the commercial duopoly;
**HiGHS** and **SCIP** as the open-source state of the art. All combine
simplex / barrier LP with branch-and-cut, presolve, and a battery of cut
families (Gomory, MIR, clique, cover).

**Characteristic source-problems.** Vehicle routing, crew scheduling, network
design, facility location, production planning, portfolio optimisation, energy
unit commitment, and any operations-research textbook problem. The decisive
feature: real-valued variables can sit alongside integer ones, which is awkward
to express in SAT/SMT (you would need rationals or bit-vectors).

---

## 10. CP / CSP / FlatZinc

**Native shape.** *Constraint satisfaction* over finite-domain integer
variables (and increasingly reals, sets, intervals). Distinguished by **global
constraints** — `alldifferent`, `cumulative`, `circuit`, `regular` — each with
a dedicated propagator that enforces domain consistency more strongly than any
naïve clausal encoding.

**Expressiveness ceiling.** **NP-complete** for finite-domain CSP; richer
versions (cumulative scheduling, set CSPs) stay NP. CP solvers also handle
optimisation by bound-propagation.

**Flagship solvers.** Google's **OR-Tools CP-SAT** — actually a lazy-clause-
generation hybrid, dominant on MiniZinc Challenges since 2018; **Choco** as
the JVM reference implementation. **MiniZinc** is the modelling language;
**FlatZinc** the solver-facing IR.

**Characteristic source-problems.** Job-shop and resource-constrained project
scheduling, nurse rostering, timetabling, vehicle routing variants, quasigroup
completion, n-queens-style puzzles, configuration. Anywhere the structure is
"these variables take finite values; these global constraints hold," CP buys
you the propagators for free.

---

## 11. Planning / PDDL

**Native shape.** *Sequential decision*: given an initial state, a goal
condition, and a set of typed actions with preconditions and effects, find a
sequence (or partial order) of actions that reaches the goal. Optionally
optimise plan length, makespan, or numeric cost.

**Expressiveness ceiling.** **PSPACE-complete** for propositional STRIPS
planning; **EXPSPACE**-complete with conditional effects and quantified
preconditions; back down to **NP-complete** when the horizon is bounded
(SATplan trick).

**Flagship solvers.** **Fast Downward** (Helmert) with the **LAMA** portfolio
config — the perennial IPC anchor; **SymBA*** for optimal symbolic planning.
**Madagascar** (M, Mp, MpC) is the canonical SAT-based planner that compiles
bounded-horizon PDDL to SAT and unrolls until a plan is found.

**Characteristic source-problems.** Robotics task planning, logistics,
elevator/lift control, narrative generation, web-service composition, and the
benchmark set of the International Planning Competition. SATplan reveals the
deeper trick: bounded planning *is* SAT, so any PDDL spec is a witness that
this target is reducible to (3) on a per-horizon basis.

---

## 12. BDD / ZDD — Symbolic Representation

**Native shape.** A **canonical** representation of Boolean functions (BDD) or
sets-of-sets (ZDD) as reduced-ordered DAGs. Once built, equivalence,
satisfiability, model counting, projection, image computation, and Boolean
operations are all polynomial in the size of the diagram. The catch: diagram
size is variable-order-sensitive and worst-case exponential.

**Expressiveness ceiling.** Decision problems on the represented function are
free; counting is polynomial in BDD size. Fixed-point computation (μ-calculus,
CTL model checking) is decidable for finite Kripke structures and is exactly
the historical killer-app.

**Flagship solvers.** **CUDD** (Somenzi) — the C library every academic
project links against; **Sylvan** (van Dijk) for parallel/multi-core BDD &
ZDD operations. **MEDDLY** for multi-valued and edge-valued variants.

**Characteristic source-problems.** Symbolic CTL model checking (NuSMV),
combinational equivalence checking, reachability in finite-state systems,
exact #SAT (when BDD compiles), enumeration of paths / cuts / minimal hitting
sets (ZDD's specialty: Knuth's "Simpath"), Bayesian-network compilation,
binate covering. Whenever you need *all* solutions and the function is
structured, this beats enumeration.

---

## 13. First-Order Theorem Provers

**Native shape.** Decide whether a first-order (typically untyped or sorted)
formula is **valid** or whether a clause set is **unsatisfiable** — and, on
success, return a *proof object*. Saturation-based provers maintain a
clause set closed under inference rules (resolution, superposition,
paramodulation) until they derive ⊥ or saturate.

**Expressiveness ceiling.** First-order logic is **semi-decidable**:
recursively enumerable for valid formulas, undecidable in general. With
equality, superposition is a complete refutation calculus. Many useful
fragments (effectively propositional / EPR, monadic, two-variable) are
decidable in NEXPTIME / NP.

**Flagship solvers.** **Vampire** (Kovács, Voronkov) — repeat CASC champion;
**E** (Schulz) and **iProver** (Korovin) as the other two stalwarts. All
participate in CASC annually.

**Characteristic source-problems.** Proof obligations from interactive
theorem provers (Sledgehammer in Isabelle, hammer tactics in Coq/Lean),
mathematical lemma discovery, ontology consistency checking (when SMT or DL
reasoners give up), software verification with quantifiers, axiomatic
specifications. The contrast with SMT is sharp: theorem provers handle
quantifiers but lack rich theory back-ends; SMT does the opposite.

---

## 14. Probabilistic Inference / Knowledge Compilation

**Native shape.** Compute a **probability** (marginal, conditional, MAP) of a
query in a probabilistic model — Bayes net, factor graph, probabilistic
program. Reduces beautifully to **weighted model counting (WMC)**: encode the
network as a CNF whose weighted model count equals the desired probability.

**Expressiveness ceiling.** Exact inference is **#P-hard** even for
poly-treewidth Bayes nets; PP-complete decision version. MAP is NP^PP.
Approximation has FPRAS only under structural assumptions; in general it is
NP-hard to approximate within any factor.

**Flagship solvers / systems.** **ProbLog2** (Leuven) — probabilistic Prolog
that compiles to **d-DNNF** via c2d/dsharp/SDD then linearly evaluates;
**Dice** (Holtzen) — discrete probabilistic programs to BDD, scaling via
program-structure exploitation; **PSI** — symbolic exact inference for
mixed discrete-continuous programs. **Ace** and **miniC2D** as the canonical
WMC compilers.

**Characteristic source-problems.** Bayesian-network marginals, probabilistic
logic programs over biological/social networks, neuro-symbolic systems
(DeepProbLog), reliability analysis, statistical-relational learning, and any
"how probable is X given Y?" query where samples are too noisy and the model
is small enough to compile. The trick is essentially: probabilistic inference
is #SAT with weights, so compile once and query cheaply.

---

## Summary Table

| Target | Native shape | Complexity ceiling | Distinguishing strength | Flagship solver |
|---|---|---|---|---|
| **SAT** | Decision | NP | Lingua franca; cheapest engine per clause | Kissat, CaDiCaL |
| **MaxSAT** | Optimisation | FP^NP / Δ₂^P | Hard + soft + weights, native | EvalMaxSAT, RC2 |
| **PB** | Decision + opt. | NP | Cardinality / linear ≥ on 0-1 | RoundingSat, Sat4j |
| **#SAT** | Counting | #P | Counts / weighted sums | Ganak, ApproxMC |
| **QBF** | Decision | PSPACE (PH at fixed depth) | Quantifier alternation | CAQE, DepQBF |
| **SMT** | Decision | Theory-dependent | Theories: arith/BV/arrays/strings | Z3, cvc5 |
| **ASP** | Models / opt. | Σ₂^P | Stable-model semantics, rules | clingo, DLV |
| **Datalog** | Fixpoint | P (data) | Bottom-up materialisation | Soufflé, RDFox |
| **ILP / MILP** | Optimisation | NP-hard | Real ∪ integer vars; LP relaxation | Gurobi, HiGHS |
| **CP / CSP** | Decision + opt. | NP | Global constraints with strong propagators | OR-Tools CP-SAT |
| **Planning** | Sequencing | PSPACE | State / action structure native | Fast Downward |
| **BDD / ZDD** | Canonical repr. | Repr.-size dependent | All-solutions / fixpoint queries | CUDD, Sylvan |
| **FO ATP** | Validity / proof | RE (semi-decidable) | Quantifiers + proofs | Vampire, E |
| **Prob. infer.** | Marginal / MAP | #P / NP^PP | Weighted compilation | ProbLog, Dice |

## Redundant vs Genuinely Distinct

If you collapse by complexity ceiling alone you get a misleading picture: SAT,
MaxSAT, PB, ILP, CSP, ASP-normal all sit in the NP / FP^NP band, yet they are
not redundant — the distinction is **what is *cheap to express*** and **which
inference rules the engine knows**.

- **PB vs ILP** — *related but distinct*. PB restricts to 0-1 with linear
  Boolean inequalities and inherits a cutting-plane proof system tuned to
  SAT-style learning; ILP allows continuous variables and leans on simplex
  relaxations. On a pure 0-1 instance with no continuous slack, modern MILP
  solvers and PB solvers genuinely compete and the boundary blurs (SCIP plays
  in both arenas), but the *target* is different: PB still *outputs Boolean
  proofs*; MILP outputs LP-bounded branch-and-bound traces.
- **MaxSAT vs PB-opt** — *almost the same target*, modulo encoding of
  cardinality. Either can simulate the other with linear blow-up. Treat them as
  one family with two dialects.
- **Datalog vs ASP** — *distinct*. Datalog is monotonic least-fixpoint; ASP
  is non-monotonic stable-model semantics. ASP can encode Datalog trivially;
  Datalog cannot capture defaults / disjunction without strata gymnastics.
- **SAT vs SMT (QF_UF only)** — *the same engine wearing a different hat*. But
  once you turn on LIA / BV / arrays the theory propagators do work no SAT
  encoding could match in practice.
- **#SAT vs probabilistic inference** — *same target, different front-ends*.
  WMC is the common substrate; ProbLog/Dice/Ace are essentially modelling
  languages whose compilers emit weighted CNF or d-DNNF.
- **BDD/ZDD vs everything else** — *uniquely a representation*, not a
  search procedure. BDDs are the only entry on this list whose post-build
  cost is polynomial across decision, counting, and image computation.
- **Planning vs SAT** — *operationally distinct, theoretically not*.
  Bounded-horizon STRIPS planning compiles to SAT (SATplan), but Fast Downward
  uses heuristic forward search with delete-relaxation heuristics that nothing
  else exploits. Different target, same complexity.
- **First-order ATP vs SMT** — *complementary, not redundant*. ATPs handle
  unbounded quantifiers and equality with paramodulation; SMT handles theories
  with decision procedures. Their intersection (EPR, array fragments) is where
  they meet; outside it they cover disjoint terrain.

**Real count of distinct tricks: about nine.**
(1) propositional decision (SAT), (2) propositional optimisation (MaxSAT/PB),
(3) propositional counting / weighted compilation (#SAT, prob. inference, BDD
when used for counting), (4) quantified-Boolean / PH alternation (QBF),
(5) modulo-theories (SMT), (6) mixed continuous-integer optimisation (MILP),
(7) finite-domain global-constraint reasoning (CP), (8) rule-based fixpoint /
deduction (Datalog, ASP-normal as a non-monotonic dialect), (9) first-order /
proof-producing reasoning (ATP). Planning fits inside (1) for bounded horizons
and inside (4) for unbounded; symbolic representation (BDD/ZDD) is a *technique
across* (1)/(3) more than a separate destination. Stable-model ASP straddles
(8) and (4) when disjunctive. Everything else on the catalogue is a dialect or
front-end of one of these nine.

---

## Sources

- [Z3 paper notes (Moura & Bjørner, 2008)](file:///C:/Users/Q/code/propstore/papers/Moura_2008_Z3EfficientSMTSolver/description.md)
- [νZ MaxSAT/MaxSMT in Z3 (Bjørner et al., 2014)](file:///C:/Users/Q/code/propstore/papers/Bjorner_2014_MaximalSatisfactionZ3/abstract.md)
- [OptiMathSAT (Sebastiani & Trentin, 2015)](file:///C:/Users/Q/code/propstore/papers/Sebastiani_2015_OptiMathSATToolOptimizationModulo/description.md)
- [SAT Competition 2024](https://satcompetition.github.io/2024/output.html)
- [MaxSAT Evaluation 2024](https://maxsat-evaluations.github.io/2024/)
- [Pseudo-Boolean Competition 2024](http://www.cril.univ-artois.fr/PB24/)
- [Model Counting Competition 2024 results (Ganak)](https://mccompetition.org/assets/files/2024/MC2024_awards.pdf)
- [QBFLIB / QBFEVAL portal](https://www.qbflib.org/index_eval.php)
- [Soufflé Datalog](https://souffle-lang.github.io/)
- [RDFox documentation — reasoning](https://docs.oxfordsemantic.tech/reasoning.html)
- [RoundingSat (J. Nordström software)](https://jakobnordstrom.se/software/)
- [Ganak (Meel group)](https://github.com/meelgroup/ganak)
- [QuAbS](https://github.com/ltentrup/quabs)
- [ProbLog](https://github.com/ML-KULeuven/problog)
