# Reduction Tricks in Computational Argumentation: An Empirical Anchor

This report catalogs the reduction tricks that the computational argumentation
literature has actually deployed to push reasoning tasks onto solver-friendly
domains. It is intentionally narrow: it answers the question "what reductions
have been used in argumentation?" and does not attempt to generalise to other
nonmonotonic settings. Sources are local paper notes in `propstore/papers/`;
claim citations name the paper directory and (where available) the
`claims.yaml` claim id.

## 1. The argumentation problem matrix

Cells give the worst-case complexity of the decision problem; CFG = polynomial,
NPC = NP-complete, coNPC = coNP-complete, PiP2 = Pi_2^P-complete, sigP2 =
Sigma_2^P-complete. DC = credulous acceptance, DS = skeptical acceptance, VER
= verification ("is set S a sigma-extension?"), EE = enumeration, EX =
existence of a non-empty extension. Source: Dunne & Wooldridge 2009 Table 1
(`Dunne_2009_ComplexityAbstractArgumentation`), refined by subsequent surveys
referenced in `Niskanen_2020_ToksiaEfficientAbstractArgumentation` and
`Lehtonen_2024_PreferentialASPIC` (Theorem 16).

| Semantics    | DC     | DS     | VER    | EX (non-empty) | EE        |
|--------------|--------|--------|--------|----------------|-----------|
| grounded     | P      | P      | P      | trivial (always exists) | P (unique) |
| complete     | NPC    | P (= grounded) | P | trivial | output-poly via SAT iter |
| admissible   | NPC    | trivial (empty set) | P | NPC | output-poly |
| preferred    | NPC    | PiP2   | coNPC  | trivial | output-poly via blocking clauses |
| stable       | NPC    | coNPC  | P      | NPC      | output-poly via blocking clauses |
| semi-stable  | sigP2  | PiP2   | coNPC  | trivial | iter MaxSAT |
| stage        | sigP2  | PiP2   | coNPC  | trivial | iter MaxSAT |
| ideal        | in Theta_2^P | in Theta_2^P | coNPC | trivial | unique |
| CF2          | NPC    | coNPC (refined classes vary by sub-semantics) | in P | trivial | SCC-recursive enumeration |

The *shape* of this matrix — P, NP/coNP, and PH-2 stratified by semantics —
forces the choice of solver target. Polynomial rows (grounded, ideal in part)
admit deterministic procedures; NP/coNP rows fit SAT or ASP; PH-2 rows fit
QBF, two ASP layers, or iterated SAT.

## 2. Reduction tricks observed

### 2.1 Direct SAT encoding (Besnard-Doutre style)

- **Source problem(s):** DC/DS/VER/EE under conflict-free, admissible,
  complete, stable.
- **Target:** SAT (CNF).
- **Why:** Conflict-freeness and "in or attacked" are local Boolean
  constraints over per-argument variables; the natural witness for DC is an
  extension, which is exactly a satisfying assignment.
- **Encoding sketch:** One variable `x_a` per argument. Conflict-free clauses
  `(neg x_a or neg x_b)` for each `(a,b) in R`. Stable adds the
  outsider-coverage clause `x_a or OR_{(b,a) in R} x_b` for every argument
  (Mahmood claim15 in `Mahmood_2025_Structure-AwareEncodingsArgumentationProperties/claims.yaml`;
  Niskanen Fig 1 in `Niskanen_2020_ToksiaEfficientAbstractArgumentation/notes.md`).
  Admissible adds defense: `x_a -> r_{a'}` for each attacker `a'`. Complete
  augments admissible with "every defended argument is in".
- **Trade-off:** Linear in `|A|+|R|`, so it scales. But for preferred /
  semi-stable / stage you need maximisation, which one CNF cannot express.
- **Citation:** `Niskanen_2020_ToksiaEfficientAbstractArgumentation` (Toksia
  is the ICCMA 2019 main-track winner built entirely on this trick).

### 2.2 Iterative SAT for maximality (the "do PH-2 with PH-1 calls" trick)

- **Source:** DS-PR (skeptical preferred, PiP2-complete), SE-PR (one
  preferred extension), EE-PR, semi-stable, stage.
- **Target:** SAT, repeatedly, with persistent solver state.
- **Why:** Preferred = subset-maximal complete. You can't write maximality as
  one CNF, but you can witness it: solve for an admissible set `S`, then add
  a blocking constraint `OR_{a not in S} x_a` and solve again; if UNSAT, `S`
  was preferred. Iterating climbs the maximality lattice.
- **Encoding sketch:** Toksia keeps the SAT solver instance alive across
  calls and uses *assumptions* to add/retract per-query literals, plus
  blocking clauses to enumerate maximal models. For semi-stable it first
  checks stable existence (cheap) and falls back to MaxSAT-style range
  maximisation `S union S^+` only if needed (`Niskanen_2020.../notes.md`,
  "Semi-Stable Semantics").
- **Trade-off:** Many calls in the worst case (one per candidate
  superset/maximal extension), but each call is on a *small* persistent CNF
  and benefits from learned clauses. In practice this beats the "honest"
  PH-2 encoding: Mahmood 2025 explicitly notes their QBF preferred encoding
  is theoretically optimal in clique-width but "may not outperform iterative
  SAT approaches (like CEGAR) in practice"
  (`Mahmood_2025/claims.yaml` claim14).
- **Citation:** `Niskanen_2020_ToksiaEfficientAbstractArgumentation`.

### 2.3 Unit-propagation for the polynomial fragment (grounded)

- **Source:** Grounded extension and DC/DS-GR.
- **Target:** Boolean constraint propagation, no full SAT search.
- **Why:** Grounded is the least fixed point of the characteristic function
  and computable in polynomial time; running a full SAT solver wastes the
  polynomial guarantee. Toksia simulates the iterative
  "accept-unattacked-then-reject-what-they-attack" loop with unit propagation
  (`Niskanen_2020/notes.md`, "Grounded Semantics"). It is also used as
  *preprocessing* before more expensive semantics — anything in grounded
  trivially settles DC, anything attacked by grounded trivially fails.
- **Trade-off:** Only the grounded core is settled this way; everything
  outside still needs SAT.
- **Citation:** `Niskanen_2020_ToksiaEfficientAbstractArgumentation`.

### 2.4 QBF for genuinely PH-2 tasks

- **Source:** DS-PR, DC/DS-semi-stable, DC/DS-stage, ARG/ARG-Rel for
  logic-based argumentation.
- **Target:** 2-QBF (one quantifier alternation; Pi_2 or Sigma_2 prefix).
- **Why:** Skeptical preferred says "for every preferred extension `E`,
  `q in E`", which translates as "for all candidate supersets, either it is
  not admissible, or it contains `q`". That is exactly a forall-exists
  formula.
- **Encoding sketch:** Mahmood 2025 builds preferred from admissible by
  introducing starred variables `v*` for the candidate superset and asserting
  no admissible superset exists, "converted to CNF via inner-most universal
  quantifier elimination on DNF matrices" (`Mahmood_2025/claims.yaml`
  claim9). Fichte 2021 uses fresh extension variables `tilde e_a` plus
  inequality variables `q_a`, `q^t` propagated along the tree decomposition
  to express "no proper superset of `E` is also admissible" without making
  the primal graph dense (`Fichte_2021/notes.md`, formulas 8-11).
- **Trade-off:** QBF solvers are less mature than SAT solvers; in ICCMA
  practice the iterative-SAT trick (2.2) beats the QBF route. Mahmood
  acknowledges no experimental evaluation
  (`Mahmood_2025/claims.yaml` claim14).
- **Citation:** `Mahmood_2025_Structure-AwareEncodingsArgumentationProperties`,
  `Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth`.

### 2.5 Decomposition-guided (DG/DDG) treewidth/clique-width preserving SAT

- **Source:** All standard Dung semantics, plus counting (#sigma).
- **Target:** SAT or 2-QBF with linearly-preserved treewidth / clique-width.
- **Why:** Modern SAT solvers are empirically fast on instances of small
  treewidth, and Courcelle-style FPT results (Dunne 2009 Theorem 17) say the
  argumentation problems are linear-time on bounded-treewidth AFs. The
  catch: a *naive* CNF encoding destroys treewidth. The "in-or-attacked"
  clause `x_a or OR_{(b,a)} x_b` connects `a` to all its attackers in the
  primal graph, so a high in-degree node creates a dense bag. Fichte's DG
  reduction introduces propagated auxiliary variables `d^t_a` (defeated at
  TD node `t`) so attack information flows along the tree decomposition
  rather than through long-range clauses (`Fichte_2021/notes.md`,
  formulas 1-5).
- **Encoding sketch:** Walk the tree decomposition bottom-up; at each bag
  emit clauses that only mention variables for arguments currently in the
  bag plus the propagation variables for the children. Bag-size growth is
  bounded by a constant factor (`|chi'(t)| <= 5 |chi(t)|` for stable,
  Theorem 5 in `Fichte_2021/notes.md`). Mahmood 2025 generalises to
  clique-width by guiding the encoding along the k-expression parse tree
  (`Mahmood_2025/claims.yaml` claim1), with overhead `11k+2` colours
  (claim2).
- **Trade-off:** Theoretically optimal — runtime `2^O(k) * poly(s)` for
  stable/admissible/complete and `2^O(k^2) * poly(s)` for
  preferred/semi-stable/stage (`Mahmood_2025/claims.yaml` claims3,4) — and
  these bounds match the ETH lower bound (claim5). In practice nobody yet
  ships a TD-aware encoder; ICCMA winners still use direct flat encodings.
  The DG approach also bijectively preserves solutions, so it doubles as a
  model-counting reduction (`Mahmood_2025/claims.yaml` claim11).
- **Citation:** `Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth`,
  `Mahmood_2025_Structure-AwareEncodingsArgumentationProperties`.

### 2.6 ASP for nonmonotonic semantics (the "stable models eat preferred for
breakfast" trick)

- **Source:** DC/DS under admissible/complete/stable/preferred for ASPIC+
  argumentation theories; same for AFs.
- **Target:** Answer Set Programming (Clingo).
- **Why:** Stable extensions of an AF correspond directly to stable models
  of a small disjunctive logic program; preferred extensions correspond to
  subset-maximal answer sets, which Clingo computes natively via
  `#minimize`/`#maximize` or saturation. The argumentation semantics is
  nonmonotonic and the ASP semantics is nonmonotonic; the impedance match is
  near-perfect.
- **Encoding sketch:** Lehtonen 2020 gives a *direct* ASP encoding for
  ASPIC+: `Gamma_guess` chooses a subset of defeasible elements
  `{sel(X) : ordinary(X)}`, `Delta_der` derives the closure, attack rules
  enforce conflict-freeness, completeness rules enforce defense
  (`Lehtonen_2020/notes.md`, listings 1-4). The crucial detail is that this
  works on `(P, D)` pairs of premises and defeasible rules, not on the
  exponentially many *arguments* you would get by translating ASPIC+ to an
  AF first (`Lehtonen_2020/notes.md`, sigma-Assumptions). Lehtonen 2024
  extends this to preferential ASPIC+ under both elitist and democratic
  last-link liftings (`Lehtonen_2024_PreferentialASPIC/notes.md`).
- **Trade-off:** ASP scales to thousands of atoms (Lehtonen 2024 reports
  1500-1900 atoms vs PyArg's 50-80). The cost is solver opacity — debugging
  Clingo timeouts is harder than reading a SAT trace — and ASP is weaker at
  fine-grained iteration than incremental SAT. Diller 2025 explicitly
  picks Datalog *over* ASP for ASPIC+ grounding because Datalog's bottom-up
  evaluation produces only the needed atoms without computing answer sets
  (`Diller_2025/notes.md`, "Why Datalog over ASP for grounding").
- **Citation:** `Lehtonen_2020_AnswerSetProgrammingApproach`,
  `Lehtonen_2024_PreferentialASPIC`.

### 2.7 Datalog for grounding and the strict-rule fragment

- **Source:** First-order ASPIC+ grounding; closures under strict rules.
- **Target:** Datalog (with stratified negation).
- **Why:** First-order ASPIC+ rules with variables would naively blow up
  exponentially when grounded over the Herbrand universe. Datalog computes
  the *minimal* set of ground atoms reachable by the immediate-consequence
  operator `T_P` (`Diller_2025/notes.md`, Definition 8); only these can
  ever appear in arguments, so only these need ground rule instances.
- **Encoding sketch:** Diller 2025 maps each ASPIC+ rule
  `phi_1, ..., phi_n -> psi` to a Datalog rule with the same body and head
  (`Diller_2025/notes.md`, Algorithm 1). The optimisation that makes the
  approach scale is "non-approximated predicates" (Definition 12): if a
  predicate's ground instances are completely determined by strict rules
  and facts, resolve it inside Datalog and never emit the corresponding
  ground ASPIC+ rules at all (`Diller_2025/notes.md`, Transformation 2).
  Maher 2021 and Bozzato 2020 use Datalog as the target for *defeasible*
  reasoning more broadly, leveraging the polynomial data complexity of
  Datalog as a hard upper bound.
- **Trade-off:** Datalog is monotonic; you cannot encode preferred or
  stable directly. Diller's pipeline only handles the *grounding* phase and
  then hands off to an AF/ASP solver for the nonmonotonic part
  (`Diller_2025/notes.md`, Limitations).
- **Citation:** `Diller_2025_GroundingRule-BasedArgumentationDatalog`.

### 2.8 Multi-valued / fuzzy propositional encodings

- **Source:** Stable, complete, and graded/equational semantics.
- **Target:** 3-valued PL (Kleene, Lukasiewicz), fuzzy PL[0,1] with
  Godel/Product/Lukasiewicz t-norms.
- **Why:** Tang 2025's observation is structural: a *single* propositional
  formula `ec1(AF) = AND_a (a <-> AND_{(b,a) in R} not b)` produces
  different argumentation semantics depending on which logic system
  evaluates it. Stable = `ec1` over Kleene PL3; complete = `ec1` over
  Lukasiewicz PL3; Gabbay's `Eq^R_max` = `ec1` over Godel fuzzy PL[0,1]
  (`Tang_2025/claims.yaml` claims3-9).
- **Encoding sketch:** See the equation above for `ec1`; pick the t-norm
  to pick the semantics. For computation you need a model checker for the
  chosen logic, which for PL3 collapses to a small SAT-with-don't-cares.
- **Trade-off:** Theoretical unification, not a practical speedup —
  Tang explicitly notes "no computational complexity analysis of model
  checking in the different PLSs" (`Tang_2025/notes.md`, Limitations).
  The ICCMA solvers all stick with classical SAT.
- **Citation:** `Tang_2025_EncodingArgumentationFrameworksPropositional`.

### 2.9 ABA / structured framework -> AF: the meta-trick

- **Source:** ABA, ASPIC+, defeasible logic.
- **Target:** Abstract Dung framework `(A, R)`, then any of 2.1-2.6.
- **Why:** Once you have an abstract AF you can use the entire SAT/ASP
  machinery. The classic translation (Bondarenko et al. 1997, exposed in
  `Toni_2014_TutorialAssumption-basedArgumentation`) builds one argument
  per minimal `(P, D)` deduction, and one attack per contrary derivation.
- **Trade-off:** Worst-case exponential blowup. Lehtonen 2020 motivates
  the whole sigma-assumption reformulation by this fact: "the translation
  can produce exponentially many arguments from a polynomially-sized ASPIC+
  theory" (`Lehtonen_2020/notes.md`, Problem Addressed). The modern
  practice is to *avoid* the AF construction and reason directly on
  defeasible elements — but the meta-trick is still available when the
  blowup is tolerable, and it's how this codebase's own ABA solver
  historically worked before the support-mask optimisation
  (see `argumentation/aba.py`, `argumentation/aba_sat.py`).

### 2.10 Support-mask SAT (this codebase's ABA encoding)

- **Source:** ABA stable/complete/preferred, flat ABA only.
- **Target:** SAT over assumption indicator variables, with derivation
  closures precomputed as bitmasks.
- **Why:** Flat ABA assumption sets are closed under derivation, so the
  search space is `2^|A|` over assumptions, not over all literals. Each
  contrary's derivation tree can be precomputed to a set of "minimal
  supports" (sets of assumptions that derive it); attack relations then
  become `OR_{S in supports(c(a))} (AND_{b in S} x_b)`.
- **Encoding sketch:** `argumentation/aba_sat.py:sat_stable_extension`
  emits, for each assumption `a` with contrary `c(a)`:
  - defense: `x_a -> NOT (any support of c(a) selected)`
  - stable closure: `x_a OR (any support of c(a) selected)`
- **Trade-off:** Avoids materialising abstract arguments. Limited to flat
  ABA — the module raises `NotFlatABAError` on non-flat input
  (`argumentation/aba.py:27`). For preferred, the implementation uses
  iterative SAT on admissible models (the trick from 2.2). This is a
  domain-specific specialisation of (2.1)+(2.2) that exploits the ABA
  structural property "extensions are determined by their assumptions".

### 2.11 MaxSAT for range maximisation (semi-stable, stage, enforcement)

- **Source:** Semi-stable, stage (DC/DS), enforcement / minimal change.
- **Target:** MaxSAT (or SAT with iterated optimisation calls).
- **Why:** Semi-stable maximises the *range* `S union S^+`; stage does the
  same over conflict-free sets. That is a cardinality maximisation over
  a Boolean witness, i.e. MaxSAT.
- **Encoding sketch:** Soft clauses `(x_a OR r_a)` for each `a` (one for
  range membership), hard clauses for admissibility/conflict-freeness.
  Toksia uses iterative SAT with optimisation calls rather than a
  monolithic MaxSAT formulation (`Niskanen_2020/notes.md`,
  "Semi-Stable Semantics"). Enforcement (Baumann 2010) and AF revision
  problems also fit MaxSAT naturally — minimise the number of attacks
  added/removed subject to a target acceptance pattern.
- **Trade-off:** MaxSAT solvers are mature enough; the pragmatic question
  is whether you trust the MaxSAT solver more than a hand-coded iterated
  SAT loop. In ICCMA-style benchmarks Toksia's iterated SAT wins.
- **Citation:** `Niskanen_2020_ToksiaEfficientAbstractArgumentation`.

### 2.12 FPT dynamic programming on the tree/clique decomposition

- **Source:** All standard semantics on bounded-treewidth AFs.
- **Target:** Direct DP, no SAT.
- **Why:** Courcelle's theorem (Dunne 2009 Theorem 17) gives MSOL-definable
  problems linear time on bounded-treewidth graphs; Dvorak 2012 develops
  *concrete* DP algorithms rather than going through MSOL. The DP
  maintains, at each tree-decomposition node, a table of partial labellings
  consistent with admissibility/completeness/etc., updated as bags grow.
  Popescu 2024 applies the same idea to probabilistic AFs.
- **Trade-off:** The Courcelle constants are non-elementary
  (`Dunne_2009/notes.md`, Limitations). Hand-rolled DPs (Dvorak 2012,
  Popescu 2024) are practical for small width. Fichte 2021's DG-to-SAT
  reductions are an alternative: instead of running DP, compile to SAT and
  let the SAT solver implicitly exploit treewidth.
- **Citation:** `Dvorak_2012_FixedParameterTractableAlgorithmsAbstractArgumentation`,
  `Dunne_2009_ComplexityAbstractArgumentation`.

## 3. Meta-observations

### How many distinct tricks?

Counting the sections above, twelve. Of these, seven are genuinely
*orthogonal* in their target formalism: SAT, iterated SAT, QBF, ASP,
Datalog, multi-valued PL, MaxSAT, plus the structural FPT/DP family. The
remainder (unit propagation, DG/DDG, ABA-meta, support-mask) are
*specialisations* — tricks layered on top of one of the seven.

### Argumentation-specific vs generic

Generic tricks any nonmonotonic problem would use:
- SAT for NP witnesses (2.1).
- Iterated SAT to climb a maximality lattice (2.2).
- ASP for stable-model-style nonmonotonic semantics (2.6).
- MaxSAT for cardinality optimisation (2.11).
- FPT-DP on treewidth (2.12).

Argumentation-specific tricks:
- The **support-conflict-attack triple encoding** that distinguishes "in",
  "attacked-by-in", and (for complete) "defended" — see Niskanen's `x_a` /
  `r_a` / `o_c^v` variable family (`Mahmood_2025/claims.yaml` claims6-8).
  Other nonmonotonic settings don't have this exact tripartite labelling
  structure.
- **DG/DDG reductions guided by the AF's primal graph** specifically
  designed to defeat the high-in-degree-blows-up-treewidth pathology of
  the naive AF encoding (`Fichte_2021/notes.md`, "in-or-attacked").
- **The structured-to-abstract pipeline** (ABA -> AF, ASPIC+ -> AF) which
  is unique to argumentation precisely because argumentation has both a
  structured layer and an abstract layer, with formally proven
  correspondence (Lehtonen 2020 Theorem 5, `Lehtonen_2020/notes.md`).
- **Multi-valued PL semantic correspondences** (Tang 2025) — switching
  the truth-value lattice picks out stable vs complete vs equational
  semantics from a single formula. This is specific to argumentation
  because argumentation has a canonical "in / out / undecided" labelling
  that maps onto PL3 truth values.

### What does ICCMA reveal about which trick wins?

ICCMA 2019 main track: Toksia's direct SAT + iterated SAT + grounded-by-UP
combination won every reasoning task
(`Niskanen_2020/notes.md`, Key Contributions). That is, the simplest
applicable trick beat the more theoretically sophisticated alternatives:

- The DG/DDG treewidth approach (Fichte 2021, Mahmood 2025) is provably
  ETH-optimal but unimplemented; no DG-aware solver has competed.
- QBF encodings of skeptical preferred lose to iterated SAT in practice
  (`Mahmood_2025/claims.yaml` claim14 acknowledges this).
- ASP solvers (Aspartix family) are competitive but generally a step
  behind SAT-based Toksia in the main track.
- For ASPIC+ (off the main AF track) ASP wins decisively over the
  argument-enumeration approach: ASPforASPIC scales to ~1900 atoms vs
  PyArg's ~50-80 (`Lehtonen_2024/notes.md`, Key Contributions).

The pattern: the closer the source problem sits to the solver's native
domain, the better it does. Pure AF problems are NP/coNP/PiP2 over a
*Boolean* witness, which is SAT's native domain — direct SAT wins. ASPIC+
problems carry first-order grounding plus nonmonotonic rules, which is
ASP/Datalog's native domain — those win there. The "structure-aware" and
"FPT-decomposed" tricks are bets on instance structure (low treewidth,
low clique-width) that ICCMA benchmarks do not currently reward, possibly
because the benchmarks are not generated with such structure in mind.

### One pragmatic conclusion for the ABA-into-SAT engineer

The argumentation literature converges on three pieces of advice you
already implicitly follow:

1. Encode directly into SAT and keep the solver alive across queries
   (Toksia, `aba_sat.py`).
2. Reformulate the structured problem to avoid materialising the abstract
   AF (Lehtonen's sigma-assumptions, this codebase's support masks).
3. Treat preferred / semi-stable as iterated calls over the SAT solver,
   not as a PH-2 monolith (Toksia, and the implementation in
   `aba_sat.py:support_extensions` for `preferred`).

The tricks you do *not* yet use, ranked by how much fruit they look ripe
for:

- DG-style treewidth-aware encoding (Fichte 2021), if your ABA instances
  ever exhibit low primal-graph treewidth. Bijective preservation also
  unlocks model counting (`Mahmood_2025/claims.yaml` claim11).
- ASP as a backend for preferential ABA / ABA+, where Lehtonen's
  Clingo-based pipeline outperforms argument enumeration by orders of
  magnitude (`Lehtonen_2024/notes.md`).
- Datalog-style grounding if you ever lift to first-order ABA, with the
  non-approximated-predicate optimisation as the key win
  (`Diller_2025/notes.md`, Definition 12).
