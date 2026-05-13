# Reduction Tricks: Mapping Problems to Solver-Friendly Domains

*Synthesis report — 2026-05-01.*
*Anchored on the argumentation library's ABA-into-SAT work; generalised across CS.*
*Built from four parallel research streams; supporting reports linked at end.*

---

## 1. The intuition, confirmed

The intuition was: there is a small, finite catalog of "convert your problem
into a domain where a powerful solver becomes useful" tricks. Q noticed it in
the ABA → SAT work; the question was whether this generalises and how many
distinct tricks exist.

**The answer: yes, ~10 tricks.** Independently, two of the four research
streams (catalog enumeration and complexity-theoretic argument) committed to
"about nine" and "about ten" respectively. The argumentation literature shows
seven orthogonal targets in active use plus several specialisations — same
ballpark. The intuition is right, and the count is bounded for structural
reasons, not historical accident.

What this report adds beyond the intuition:

1. **The canonical catalog** — a single unified list of ten tricks.
2. **The structural precondition for each** — what has to hold for the trick
   to be *useful*, not merely possible. This is the "what has to hold" part
   of the original question.
3. **A decision tree** — given a source problem, which target should you
   reach for first.
4. **The bounding argument** — why the catalog stays small. Three
   orthogonal axes (complexity cell × theory × exploitable structure) form a
   sparse cube; most cells collapse into a neighbour or are empty.
5. **The argumentation anchor** — exactly which tricks the AF/ABA/ASPIC
   literature uses, and what this codebase already does versus could do next.

---

## 2. The canonical catalog

Ten reduction tricks. For each: the trick name, the structural precondition
that must hold on the source problem, the flagship target, and a one-line
argumentation example to keep things concrete.

| # | Trick | Structural precondition | Target | Argumentation example |
|---|---|---|---|---|
| 1 | **SAT (CDCL)** | Polynomial-size Boolean witness; one-quantifier verifier; no minimality, no counting | NP decision | DC under admissible/complete/stable on AFs (Toksia, Tang 2025) |
| 2 | **MaxSAT / PB / ILP** | Polynomial Boolean (or 0-1, or mixed-integer) witness + linear objective | OptP / Δ₂ᴾ | Semi-stable / stage range maximisation; AF enforcement (Baumann 2010) |
| 3 | **SMT** | Natural language is theory-rich (LIA, LRA, BV, arrays, strings, UF) | Theory-dependent | Quantitative argumentation with arithmetic weights; constraint-based ASPIC+ |
| 4 | **CP with global constraints** | Constraints are naturally global (`alldifferent`, `cumulative`, `circuit`) and dedicated propagators dominate clausal decompositions | NP | Argument scheduling, dialogue games with resource constraints |
| 5 | **Datalog (and stratified ASP)** | Semantics is the least fixed point of monotone derivation rules | P data complexity | Grounded extension; ASPIC+ first-order grounding (Diller 2025) |
| 6 | **ASP** | Nonmonotonic minimality, default negation, stable-model semantics | NP / Σ₂ᴾ | Stable / preferred extensions for ASPIC+ (Lehtonen 2020/2024) |
| 7 | **QBF (and CEGAR-over-SAT)** | Quantifier alternation Σₖᴾ / Πₖᴾ, k ≥ 2 | PSPACE (PH at fixed depth) | Skeptical preferred (Π₂ᴾ); semi-stable, stage on AFs |
| 8 | **#SAT / Knowledge compilation (d-DNNF, SDD, BDD)** | Question is "how many" or "what is the weighted volume" — not a decision | #P | Probability of acceptance under probabilistic AFs (Hunter 2017/2021) |
| 9 | **First-order theorem proving** | Decidable/semi-decidable FOL fragment with equality and quantifiers | RE (semi-decidable) | Logic-based argumentation (Besnard-Hunter style); ontology-grounded ASPIC+ |
| 10 | **FPT / treewidth dynamic programming** | Underlying constraint hypergraph has bounded treewidth (or clique-width, branchwidth) | FPT | AF semantics on small-treewidth graphs (Dvořák 2012, Fichte 2021, Mahmood 2025) |

That's the catalog. Two further entries sit on the boundary:

- **Planning / PDDL** — operationally distinct from SAT but theoretically a
  bounded-horizon reduction to (1); the planning *community* is real, the
  *category* is not new.
- **Probabilistic-inference systems (ProbLog, Dice, PSI)** — front-ends that
  compile to (8). Worth knowing as engineering targets even though they are
  not a separate cell.

---

## 3. What the structural preconditions mean (the "what has to hold" part)

Each trick is built around exploiting a specific structural property of the
source problem. A reduction is *useful* exactly when the source already has
that property. This is where Cook–Levin stops being helpful: yes, every NP
problem reduces to SAT in polynomial time, but unless the source has a
**polynomial-size Boolean witness with a one-quantifier verifier**, the
reduction throws away whatever structure was actually paying for the
solver's heuristics. Same story for every other trick in the catalog.

The preconditions, in capsule form:

1. **SAT** — local Boolean constraints, no alternation, no hidden minimality.
2. **MaxSAT/PB/ILP** — linear objective is single, not min-max or fractional;
   integer-vs-Boolean choice depends on whether continuous variables exist.
3. **SMT** — theory atoms exploit structure that bit-blasting destroys
   (Simplex on LRA pivots are O(constraints); bit-blasting an integer add is
   ~100 clauses).
4. **CP** — propagators prune more than unit propagation; if every constraint
   is already small clausal, CP is overhead.
5. **Datalog** — *all* rule heads can only become true (never retracted);
   monotone T_P operator; least fixed point exists.
6. **ASP** — minimality matters, or default negation is essential. Stable
   models are fixed points of the Gelfond-Lifschitz reduct.
7. **QBF** — quantifier alternation in the source problem statement.
   Flattening discards the prenex structure that QCDCL / CEGAR exploit.
8. **#SAT** — counting is the answer, not deciding. Decision-only solvers
   would have to enumerate.
9. **FO ATP** — quantifiers + equality, but no theory-rich operations
   (otherwise SMT). Saturation calculi handle paramodulation.
10. **FPT** — the constraint hypergraph has a width parameter bounded by a
    small constant; flat encoding rediscovers the structure poorly.

Full treatment, with worked positive and negative examples per precondition,
in `reports/encoding-preconditions.md`.

---

## 4. The decision tree (one walk, top-down)

Given a source problem, walk this:

1. **Quantifier alternation (∃∀ or deeper)?** → QBF or CEGAR-over-SAT.
   Don't flatten — you discard the structure the target was built around.
2. **Answer is a count, sum-of-weights, or probability?** → #SAT for one
   shot; knowledge compilation (d-DNNF, SDD) for repeated queries.
3. **Linear objective over Boolean / 0-1 / integer witnesses?** → MaxSAT
   (clausal-dominated), PB (cardinality-heavy), ILP (mixed integer).
4. **Theory-rich constraints (arithmetic, arrays, BV, strings)?** → SMT
   with the matching theory.
5. **Nonmonotonic minimality / default negation?** → ASP. Don't bolt
   minimality onto SAT manually.
6. **Least fixed point of monotone derivation rules?** → Datalog (or
   stratified ASP).
7. **Constraint hypergraph has small treewidth?** → FPT decomposition with
   per-bag SAT/ASP/#SAT.
8. **Constraints naturally global (`alldifferent`, `cumulative`)?** → CP.
9. **First-order with quantifiers and equality, no theory?** → FO ATP.
10. **None of the above** → SAT (CDCL via Tseitin / Plaisted-Greenbaum).

The order matters. Alternation and counting come first because they
disqualify everything below as a useful target. Theory richness comes before
nonmonotonicity because SMT can't easily handle stable-model semantics, but
ASP can encode bounded arithmetic only awkwardly — pick the solver whose
*primary* capability matches your *primary* difficulty.

---

## 5. Why the catalog stays small

Three orthogonal axes form a sparse cube:

**Axis 1 — Complexity cell.** The polynomial and counting hierarchies give a
finite set of complexity classes a problem can naturally inhabit. Each cell
with both a payoff and an engineering surface has, over decades, attracted a
flagship solver community (SAT, MaxSAT, QBF, MaxSAT, MIP, Model Counting,
QBFEval). Levels above Σ₃ never matter in practice — solver communities only
form where workloads exist. About **6–8 effective cells**.

**Axis 2 — Background theory.** SMT-LIB has formalised the menu: Boolean,
LIA, LRA, BV, arrays, UF, strings, FOL. Each new theory requires a new
decision procedure with industrial engineering investment; the marginal
payoff drops fast after the first few. About **5–7 theories**.

**Axis 3 — Exploitable structure.** Treewidth, acyclicity, symmetry,
sparsity, counting structure, alternation. Each corresponds to a closed-form
algorithmic technique with a published meta-theorem (Courcelle for
treewidth, the Knowledge Compilation Map for counting, etc.). About **5–7
structures**.

Naïve product: 6 × 6 × 6 = 216 cells. Honest count: ~10. Three structural
collapses do the work:

1. **Theory collapses into Boolean** — bit-vectors, finite arrays, bounded
   LIA all bit-blast to SAT for any *bounded* instance, leaving only
   unbounded / continuous cases as genuinely separate.
2. **Structure collapses into the solver** — CDCL implicitly exploits
   backbone variables, autarkies, community structure; modern MIP exploits
   sparsity. The structure axis is mostly about properties the solver
   *cannot* find on its own (symmetry, counting, alternation, treewidth).
3. **Higher PH levels collapse into QBF or CEGAR** — Σ₂ through Σₖ all map
   to the same QBF technology. One cell, not k.

Beyond the cube, two equilibrium forces pin the count down further:

- **Solvers compete at fixed points.** A mature solver community is an
  equilibrium between problem supply and engineering investment. CDCL took
  ~30 years; MIP took ~50; SMT took ~20. New target categories appear only
  when an unexploited structural property becomes important — e.g.,
  knowledge compilation rose in the 2000s because probabilistic inference
  workloads exposed counting structure that #SAT could not exploit
  efficiently. Without such a forcing function, no new category emerges.
- **Reduction is transitive and the graph has sinks.** SAT is a sink for NP
  decision; ILP for linear-structured optimization; QBF for PH. Sinks
  attract investment; once a sink exists, building anything that reduces
  *to* it is cheaper than building a new sink. Good sinks are rare —
  they require both completeness for a class and an engineering surface
  (CNF for SAT, LP-relaxable structure for MIP, prenex form for QBF) that
  supports decades of optimisation.

Counterarguments dissolve: planning and model checking are application
packages over named cells; LLMs are *encoders* into existing cells, not new
cells; MCMC and gradient methods form a parallel approximate catalog of
similar small size; domain-specific solvers (chess, Sudoku) are
specialisations within a cell.

Caveat: the catalog grows when computing changes — GPUs made gradient-based
optimization a serious option; quantum annealing introduced QUBO. The
catalog is for *current commodity hardware*, not eternal.

Full argument in `reports/why-bounded-catalog.md`.

---

## 6. Wasted-reduction failure modes

Cases where the reduction is technically valid and uselessly inefficient —
i.e., the trick fits formally but throws away the structure that made the
target worth using:

- **Bit-blasting LIA into SAT.** Loses Simplex; turns each integer addition
  into ~100 clauses; CDCL rediscovers arithmetic facts as conflicts.
- **Flattening QBF to SAT via Tseitin-then-quantifier-elim.** Worst-case
  exponential blowup; discards prenex structure that CEGAR-based QBF
  solvers exploit. (And the flat-SAT iterative trick — see §7 — is
  almost always faster anyway.)
- **Decomposing globals to clauses for SAT.** `alldifferent` pairwise
  loses the matching propagator; CDCL learns one conflict at a time what
  the matching algorithm sees in O(n^2.5) up front.
- **Pseudo-Boolean cardinality via binomial encoding.** O(n^k) clauses for
  `at-most-k`. Use sequential counter or totalizer if you must encode in
  CNF; better, a PB solver with native cutting planes.
- **Using #SAT for a decision problem.** Counting overhead for a yes/no
  answer; counting CDCL has worse decision-finding heuristics because it
  cannot terminate on first witness.
- **Encoding a treewidth-bounded problem with flat SAT.** CDCL doesn't see
  the decomposition; FPT machinery would solve in 2^k × n instead of
  worst-case 2^n.
- **BDD reachability on a structureless instance.** BDD blows up to
  enumeration; SAT-based BMC would find a counterexample in seconds.
- **ASP for a monotone fixed-point problem.** You pay for unfounded-set
  propagation and reduct checking when stratified Datalog computes the
  answer bottom-up in linear time.
- **Compiling to d-DNNF a formula with no decomposable structure.** Compile
  time exponential; never reach the (cheap) query phase.
- **SMT for purely Boolean problems.** Theory-dispatch overhead with no
  theory work to dispatch.

Unifying principle: **match the structure first; the encoding is the easy
part.** Each target solver is built around exploiting a specific structural
property. A reduction that preserves that property is a useful trick. A
reduction that destroys it leaves the solver running on the encoding's
complexity rather than the source's structure — which is what Cook-Levin
already promised would technically work.

---

## 7. What this means for the argumentation library

Anchored anchor — three observations from the literature reading
(`reports/argumentation-reductions-anchor.md`):

**Observation A — Toksia's lesson.** ICCMA 2019's main-track winner
(Niskanen 2020) used three tricks and beat the more sophisticated
alternatives:

1. Direct SAT encoding for NP/coNP semantics (admissible, complete, stable).
2. Iterated SAT for maximality (preferred = subset-maximal complete; climb
   the lattice with blocking clauses on a persistent solver).
3. Unit propagation for the polynomial fragment (grounded settled before
   touching SAT proper).

This is exactly what `argumentation/aba_sat.py` does. The codebase is on
the empirically winning track.

**Observation B — the "do PH-2 with PH-1 calls" trick is a generic move.**
Iterated SAT for skeptical preferred / semi-stable / stage on AFs is the
same shape as CEGAR-over-SAT for QBF. It is the iterative-refinement
pattern: solve a relaxed (lower-PH) problem, add a blocking constraint that
witnesses *why* the answer was insufficient, repeat. This pattern shows up
across the catalog (CEGAR for verification, lazy SMT, even MaxSAT
core-guided algorithms). Worth recognising as a meta-trick rather than a
one-off.

**Observation C — three unused-but-ripe tricks for this codebase.**

- **DG-style treewidth-aware encoding** (Fichte 2021, Mahmood 2025) — if
  ABA instances ever exhibit low primal-graph treewidth, this would be
  ETH-optimal. Bonus: bijective preservation also unlocks model counting.
  Currently unimplemented anywhere in the AF community; would be novel.
- **ASP as a backend for ABA+ / preferential ABA** — Lehtonen's
  Clingo-based pipeline outperforms argument-enumeration approaches by
  ~30× on atom counts (1500-1900 vs 50-80 in PyArg). If preferences enter
  the picture, ASP becomes the right backend, not SAT.
- **Datalog-style grounding for first-order ABA** — if the codebase ever
  lifts to first-order, Diller 2025's "non-approximated predicates"
  optimisation is the key engineering win.

Argumentation-specific tricks worth noting because they don't generalise:

- The **support-conflict-attack triple encoding** (Niskanen, Mahmood) —
  variables for "in", "attacked-by-in", "defended" — is unique to AFs.
- The **structured-to-abstract pipeline** (ABA → AF, ASPIC+ → AF) —
  worst-case exponential, but the formally proven correspondence is
  unique to argumentation.
- Tang 2025's **multi-valued PL semantic correspondences** — switching
  the truth-value lattice (Boolean → Kleene → Łukasiewicz → Gödel fuzzy)
  picks out stable vs complete vs equational semantics from one formula.
  Theoretical unification, not yet a practical speedup.

---

## 8. Bottom line

Q's intuition is correct. There are about ten reduction tricks. The
catalog is bounded by the structure of complexity theory (a finite
hierarchy with finite alternation depths that matter), the structure of
mature theories (a small stable list of decision procedures with
industrial investment behind each), and the structure of solver
engineering (sinks of the reduction graph attract investment, and good
sinks are rare).

The condition for a trick to be useful — the "what has to hold" question —
is always the same shape: **the source problem must already exhibit the
specific structural property that the target solver was built to exploit.**
SAT exploits Boolean witness shape with one-quantifier verification.
QBF exploits prenex alternation. ASP exploits stable-model fixed points.
Datalog exploits monotone closure. SMT exploits theory-specific decision
procedures. FPT exploits bounded width. Each is a different exploit, and
each is the *only* trick worth using when its precondition holds.

A new trick can appear, but only when (a) a new complexity cell becomes
economically important, (b) a new theory with a real decision procedure
matures, or (c) a new structural property gets a closed-form exploit.
Such events occur on the timescale of generations, not years.

Until then, the catalog is closed.

---

## Supporting reports

- `reports/reduction-targets-catalog.md` — full enumeration of the
  fourteen target formalisms (SAT, MaxSAT, PB, #SAT, QBF, SMT, ASP,
  Datalog, ILP, CP, Planning, BDD/ZDD, FO ATP, probabilistic inference)
  with native shape, complexity ceiling, flagship solvers, and a
  redundancy analysis collapsing them to ~9 distinct destinations.
- `reports/encoding-preconditions.md` — one section per structural
  property of the source problem, with positive and negative examples,
  canonical encoding pattern, and the failure mode when applied to a
  source that doesn't have the property.
- `reports/argumentation-reductions-anchor.md` — twelve reduction tricks
  observed in the AF/ABA/ASPIC literature, with paper-by-paper
  citations (Tang 2025, Mahmood 2025, Niskanen 2020, Fichte 2021, Diller
  2025, Lehtonen 2020/2024, Dvořák 2012, Dunne 2009), the complexity
  matrix for AF semantics, and direct connection to the codebase's own
  support-mask SAT.
- `reports/why-bounded-catalog.md` — first-principles argument for the
  bounded count, full counterargument engagement, honest caveats about
  GPU/quantum/approximate parallel catalogs.
