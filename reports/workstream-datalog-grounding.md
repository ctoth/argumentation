# Workstream — Datalog grounding for first-order ASPIC+

Date: 2026-05-01
Author: design report (no implementation)
Theory anchor: Diller, Gaggl, Hanisch, Monterosso, Rauschenbach 2025, *Grounding Rule-Based Argumentation Using Datalog* (KR-25)
Engine anchor: sibling project `gunray` (`../gunray`), MIT, pure-Python defeasible-Datalog evaluator with a stratified-negation `SemiNaiveEvaluator`.

---

## 1. Technical summary

### 1.1 The pipeline Diller 2025 actually proposes

ASPIC+ as standardly used (Modgil and Prakken 2018) lets rules carry first-order variables: `bird(X) -> flies(X)`, `penguin(X) => not_flies(X)`. Reasoners — SAT-based, ASP-based, AF-based — operate on *propositional* (ground) theories. The bridge from the first-order surface to a ground theory is **grounding**.

The naive grounding strategy is to substitute every variable with every constant from the Herbrand universe. With `r` rules each carrying `v` variables and a universe of `c` constants the ground theory has `O(r * c^v)` rules. For the small experimental configurations Diller benchmarks (10-50 rules, 3-30 constants, 1-3 variables per rule) the naive grounding already breaks 5-minute timeouts. For realistic theories it is hopeless.

Diller's insight: *most of those substitutions never produce arguments anyway.* An argument is built bottom-up from premises through rules; a ground rule is reachable only when there is a derivation chain that grounds its body. That chain follows the immediate-consequence operator `T_P` from Datalog. So the grounding restricted to atoms in `lfp(T_P)` is sound (preserves the complete extensions of the induced AF) and dramatically smaller.

The Diller pipeline has two transformations.

**Transformation 1 (the basic version, Diller 2025 §3, Algorithm 1).** Translate the ASPIC+ theory `T = (R_s, R_d, K, ~)` into a Datalog program `P_T`:

- For each rule `r: phi_1, ..., phi_n -> psi` (or `=> psi`) in `R_s ∪ R_d`, emit the Datalog rule `psi :- phi_1, ..., phi_n`.
- For each contrariness pair, emit a Datalog rule that links the conclusion atoms (so contraries become reachable in the Datalog model).
- For each premise `phi ∈ K`, emit a Datalog fact.

Run a Datalog engine on `P_T` to get `lfp(T_{P_T})`. For each original rule `r`, query the engine for ground substitutions `theta` such that `body(r) theta ⊆ lfp(T_{P_T})`. Emit the ground instance `r theta`. The Datalog model also gives us the ground knowledge base and ground contrariness function. The resulting propositional ASPIC+ theory `T'` is correct (Diller 2025 Theorem 3): the complete extensions of the induced AF coincide with those of the original first-order theory.

**Transformation 2 (the engineering payoff, Diller 2025 §4, Algorithm 2).** Identify *non-approximated predicates* (Definition 12). A predicate `p` is non-approximated when its ground instances are completely determined by strict rules and facts — informally, no defeasible rule could ever produce or kill a `p`-atom. For non-approximated predicates we do not need to materialize ground ASPIC+ rules at all; the Datalog engine already knows the answer and the answer is unconditional. The simplification keeps a fixpoint of two further removals: fact-only rules (every body atom is a fact and the head is already a fact) are deleted, and contrary relations whose attacking predicate has no ground instances are deleted. Theorem 5 proves Transformation 2 also preserves complete extensions.

The deliverable, in both cases, is a propositional ASPIC+ theory ready to be fed to an existing reasoner — Diller's prototype ANGRY pipes into ASP/AF solvers; we already have `aspic_encoding.py` and the SAT pipeline for that handoff in `argumentation`.

### 1.2 Worked example

Take a theory with two predicates `bird/1` and `penguin/1` and the conclusion predicate `flies/1`:

- Strict rules `R_s`:
  - `s1: penguin(X) -> bird(X)`
  - `s2: flies(X) -> not_grounded(X)`
- Defeasible rules `R_d`:
  - `d1: bird(X) => flies(X)`
  - `d2: penguin(X) => not flies(X)`
- Knowledge base `K_n`: `{ penguin(opus), bird(tweety) }`
- Constants in the language: `{ opus, tweety, eric, daffy, kowalski }` (e.g. drawn from a separate facts file).

**Naive grounding.** With 5 constants and 4 rules each having 1 variable, the naive grounding produces 4 * 5 = 20 ground rule instances:

- `s1` ground: `penguin(opus) -> bird(opus)`, `penguin(tweety) -> bird(tweety)`, ..., `penguin(kowalski) -> bird(kowalski)` (5 instances)
- `s2` ground: `flies(opus) -> not_grounded(opus)`, ..., `flies(kowalski) -> not_grounded(kowalski)` (5 instances)
- `d1` ground: 5 instances
- `d2` ground: 5 instances

Plus 5 ground facts for `not_grounded/1` if we include it as a contrary. Plus contrariness ground pairs. The ground language explodes from 4 schemas to roughly 4 * 5 = 20 ground atoms each requiring SAT variables and clauses downstream.

**Datalog-restricted grounding (Transformation 1).** We emit the Datalog program:

```
bird(X) :- penguin(X).
not_grounded(X) :- flies(X).
flies(X) :- bird(X).        % defeasible rule, but T1 still emits it
nflies(X) :- penguin(X).    % "nflies" representing the contrary of flies
penguin(opus).
bird(tweety).
```

`SemiNaiveEvaluator` returns:

- `penguin = { (opus,) }`
- `bird    = { (opus,), (tweety,) }` — `opus` from `s1`, `tweety` from the seed
- `flies   = { (opus,), (tweety,) }` — both via `d1`
- `nflies  = { (opus,) }`
- `not_grounded = { (opus,), (tweety,) }`

Now back-query each ASPIC+ rule for satisfying ground substitutions. Only substitutions that make the body subset of `lfp(T_P)` survive:

- `s1`: body `penguin(X)`. Only `X = opus` matches. *1 ground instance*.
- `s2`: body `flies(X)`. `X ∈ {opus, tweety}`. *2 instances*.
- `d1`: body `bird(X)`. `X ∈ {opus, tweety}`. *2 instances*.
- `d2`: body `penguin(X)`. `X = opus`. *1 instance*.

Total: 6 ground rule instances. From 20 down to 6. The other 14 substitutions (e.g. `s1` with `X = eric`) have empty `penguin/1` extension and would never produce an argument.

**Non-approximated predicates optimisation (Transformation 2).** Predicates `penguin/1` and `bird/1` depend only on facts and strict rules. They are *non-approximated*: no defeasible rule produces or kills them, no contrariness affects them. Diller 2025 Definition 12 lets us resolve these entirely inside Datalog and *not emit ASPIC+ ground rules* for them.

So we drop the `s1` ground instance (`penguin(opus) -> bird(opus)`) and instead push `bird(opus)` into the ground knowledge base directly. We keep:

- Knowledge base: `K_n' = { penguin(opus), bird(tweety), bird(opus) }`
- Strict rules ground: `s2[opus]`, `s2[tweety]` (the heads of `s2` are still arg-relevant via `flies/1` which IS approximated, since `d2` produces its negation)
- Defeasible rules ground: `d1[opus]`, `d1[tweety]`, `d2[opus]`

Down from 6 to 5 rule instances, plus a richer KB. The savings grow with the size of the strict-only sublanguage. In Diller's S2 benchmarks Transformation 2 produces consistently smaller ground theories than Transformation 1, sometimes by orders of magnitude when most predicates are infrastructural (taxonomies, indexes, type hierarchies) and only a few carry argumentative tension.

The point of the workstream is to plug this exact pipeline into `argumentation`'s SAT/ASP handoff, using `gunray`'s `SemiNaiveEvaluator` as the Datalog back end.

---

## 2. Evidence base

**Primary source.** Diller, Gaggl, Hanisch, Monterosso, Rauschenbach 2025, *Grounding Rule-Based Argumentation Using Datalog*, KR-25; doi.org/10.48550/arXiv.2508.10976. Notes at `propstore/papers/Diller_2025_GroundingRule-BasedArgumentationDatalog/notes.md`.

What Diller actually delivered:

- A grounding procedure (Algorithms 1 and 2) plus correctness proofs that complete extensions of the induced AF are preserved (Theorems 3 and 5).
- A prototype implementation called **ANGRY** that uses an external Datalog engine (the paper does not commit to a specific engine — Souffle and clingo-style grounders are mentioned in related work).
- Empirical evaluation on three scenarios: random first-order ASPIC+ (S1), grounding-quality comparison T1 vs T2 (S2), and ICCMA 2023 + ASPforASPIC + TOAST baselines (S3). T2 consistently wins on grounded theory size; ANGRY handles instances that ASPforASPIC and TOAST time out on at the 5-minute mark.

What Diller explicitly left out (Limitations §6, paper p.9):

1. ANGRY is a **grounder**, not a complete reasoner. After grounding, the propositional theory is piped to an external AF/ASP solver. We need a downstream reasoner; in our case `aspic_encoding.py` already exists.
2. Function-free first-order ASPIC+ only. No function symbols beyond constants. Acceptable: this matches Datalog and gunray.
3. Correctness proven only for **complete-extension semantics**. Other ASPIC+ semantics (preferred, stable, grounded, ideal) are *expected* to follow but are not proven in the paper. For our use case, the SAT backend handles preferred and stable; we should not assume Diller's correctness theorem covers them, and we should ground-truth with differential testing against the existing propositional pipeline on small instances.
4. Contrariness is restricted to atom pairs (not arbitrary formulas). Matches `argumentation.aspic.ContrarinessFn` exactly.
5. Stratified negation in Datalog. Aligned with `gunray.NegationSemantics.SAFE` (Apt-Blair-Walker).
6. Diller's preference orderings are not addressed at all. Our existing `PreferenceConfig` (last-link / weakest-link, elitist / democratic) lifts into the ground theory unchanged because it operates on rule and premise *names* — but we need to verify that (a) ground rule names retain the link to original rule preferences and (b) ground premise names retain link to original premise preferences. This is a Phase 1 design constraint, not a blocker.
7. Non-approximated-predicate detection is conservative — some predicates that could be simplified may not be identified. Acceptable; correctness is preserved.

**Companion sources** (notes confirmed present in `propstore/papers/`):

- *Maher 2021* (`Maher_2021_DefeasibleReasoningDatalog/notes.md`) — broader survey of defeasible reasoning over Datalog. Useful for §5 risk analysis: confirms stratified negation is the standard tool for contrariness-style negation in this lineage.
- *Bozzato 2020* (`Bozzato_2020_DatalogDefeasibleDLLite/notes.md`) — defeasible DL-Lite via Datalog. Different ontology layer, but the grounding mechanism is structurally identical to Diller's.
- *Morris 2020* (`Morris_2020_DefeasibleDisjunctiveDatalog/notes.md`) — KLM closures (rational, lexicographic, relevant) over disjunctive Datalog. Tangential to the grounding workstream itself, but `gunray.closure.ClosureEvaluator` already implements these on the propositional fragment; if we ever extend the workstream to KLM-style entailment over the ground theory the integration is already in scope.

These broader pieces are not load-bearing for the workstream design; Diller 2025 is the only mandatory reference.

---

## 3. Codebase inspection

### 3.1 `argumentation` (this project)

**`src/argumentation/aspic.py`** — Modgil and Prakken 2018 ASPIC+ data model. The relevant types:

- `GroundAtom(predicate: str, arguments: tuple[Scalar, ...])` — already has arity and supports first-order-shaped atoms syntactically. Docstring already cites *Diller et al. 2025 Def 7* (the author was anticipating this work).
- `Literal(atom: GroundAtom, negated: bool)` — over ground atoms only.
- `Rule(antecedents: tuple[Literal, ...], consequent: Literal, kind: str, name: str | None)` — over ground literals only.
- `ContrarinessFn`, `KnowledgeBase`, `ArgumentationSystem`, `PreferenceConfig` — all propositional.

**Grep result:** No occurrences of `Variable`, `FirstOrder`, `first_order` in `src/argumentation/`. There is no first-order ASPIC+ representation in the codebase today. Phase 1 must introduce one.

**`src/argumentation/aspic_encoding.py`** — `encode_aspic_theory(system, kb, pref) -> ASPICEncoding` produces ASP-style facts in the Lehtonen, Niskanen, Jarvisalo 2024 Section 5 vocabulary: axioms, premises, rule heads/bodies, contrariness, preferences. This is the natural handoff target *after* grounding. The grounder produces a propositional `(ArgumentationSystem, KnowledgeBase, PreferenceConfig)` and `aspic_encoding` takes it from there.

**`src/argumentation/__init__.py`** — exports every module by name. Adding a new `aspic_first_order` module and a `grounding_bridge` module is a one-line registration.

**`pyproject.toml`** — `dependencies = []`. Zero runtime dependencies. Only `z3-solver` is offered, and only as an optional extra. This is a strong policy signal: gunray must be either an optional extra (`pip install formal-argumentation[grounding]`) or vendored; it cannot be a hard dep.

### 3.2 `gunray` (sibling)

**`src/gunray/types.py`** — has `Variable(name: str)`, `Constant(value: Scalar)`, `Wildcard(token: str)`, `Atom(predicate: str, terms: tuple[AtomTerm, ...])`, `Rule(heads, positive_body, negative_body, constraints, source_text)`, `GroundAtom`, `DefeasibleRule`, `GroundDefeasibleRule`. Function-free — Diller-compatible.

**`src/gunray/schema.py`** — `Program(facts: PredicateFacts, rules: list[str])`. The Datalog input to `SemiNaiveEvaluator` carries rules as **surface-syntax strings** (e.g. `"path(X, Y) :- edge(X, Y)."`), parsed via `parser.parse_program`. So our bridge has two emission strategies:

- **Surface emission**: build the rule strings, hand to `Program`. Loose coupling. Lets us debug by looking at the emitted Datalog.
- **Typed construction**: build `gunray.types.Rule` objects directly via the package-private `_normalize_rules`. Tighter coupling, faster, no string round-trip — but reaches into underscore-private machinery.

Recommend the surface path for the first cut.

**`src/gunray/evaluator.py`** — `SemiNaiveEvaluator` is a public class with two methods:

- `evaluate(program, *, negation_semantics=SAFE) -> Model`
- `evaluate_with_trace(program, trace_config=None, *, negation_semantics=SAFE) -> tuple[Model, DatalogTrace]`

`Model.facts: Mapping[str, set[FactTuple]]`. Lifting back to `argumentation.GroundAtom` is mechanical: for each predicate `p` and each tuple `t` in `model.facts[p]`, emit `GroundAtom(predicate=p, arguments=t)`.

The class is exported in `gunray.__all__`, callable from outside without ceremony.

**`src/gunray/grounding_types.py` and `src/gunray/grounding.py`** — the surprise. Gunray already implements a *conservative* version of Diller's Transformation 2 for its DeLP pipeline:

- `GroundingInspection` carries `fact_atoms`, `strict_rules`, `defeasible_rules`, `defeater_rules`, plus a `simplification: GroundingSimplification`.
- `GroundingSimplification` carries `definite_fact_atoms`, `resolved_strict_rules` (strict ground rules whose body was already definite), `strict_rules_for_argumentation`, `defeasible_rules_for_argumentation`, `defeater_rules_for_argumentation`.
- `inspect_grounding(theory: SchemaDefeasibleTheory) -> GroundingInspection` applies a fixpoint over strict-rule resolution: a strict rule whose body is fully in the fact base produces a new fact and is removed from the argumentation grounding output.

The docstring cites *Diller 2025 Definition 9 (p.3)* and *Algorithm 2 (p.7)* explicitly, and notes: *"Gunray only exposes the conservative DeLP-compatible fragment here: no defeasible or defeater rule is removed, and any strict rule whose body cannot be proven definite remains in the argumentation grounding report."*

Translation: gunray already handles fact-only-strict-rule resolution (a sub-case of Transformation 2). It does **not** implement non-approximated-predicate detection (Diller 2025 Definition 12). That analysis is the engineering payoff Phase 3 needs to deliver — either upstream into gunray or downstream in `argumentation`.

**License:** MIT.
**Python policy:** `requires-python = ">=3.11"`. Identical to `argumentation`.
**Distribution:** Not on PyPI per README — installed via `pip install git+https://github.com/ctoth/gunray.git`. This affects the optional-extras phrasing in Phase 0.

### 3.3 Implication for the workstream

There are *two* plausible top-level architectures:

- **Architecture A (loose).** `argumentation` owns FO ASPIC+, owns the bridge, owns the Diller-12 NAP analysis. Gunray is consumed only as a Datalog evaluator (call `SemiNaiveEvaluator.evaluate(Program(...))` and lift the result). Only requires gunray's stable public surface.
- **Architecture B (tight).** `argumentation` owns FO ASPIC+; the bridge converts FO ASPIC+ to gunray's `DefeasibleTheory`, calls `inspect_grounding`, and lifts a `GroundingInspection` back to ground ASPIC+. Diller-12 NAP analysis is upstreamed into gunray's `_simplify_strict_fact_grounding`. Tighter coupling but reuses more.

Recommendation: start with **A**, refactor toward **B** only if Phase 5 benchmarks demand it. Reasoning: gunray's `DefeasibleTheory` carries DeLP semantics (Garcia and Simari 2004 §6.2 presumptions, García-style superiority pairs, defeaters as a separate Nute-Antoniou rule kind) that ASPIC+ does not natively have, and forcing ASPIC+ through that schema risks impedance loss. The `Program`-only path is cleanly Datalog-typed.

---

## 4. Workstream design

Six phases. Each lists effort estimate, files touched, success criterion, and risks.

**Architectural posture (decisions 2026-05-01).** This workstream
adopts:

- **Q4 (loose coupling, Architecture A):** bridge to `gunray.Program`
  + `SemiNaiveEvaluator` only; do not route through gunray's
  `DefeasibleTheory` or `inspect_grounding`. *Caveat: Q flagged this
  decision as needing more research before Phase 0 begins.* Action:
  dispatch a research subagent to audit gunray's `Program` API
  surface area, breaking-change history, DeLP-flavoured leakage, and
  whether `SemiNaiveEvaluator.evaluate` is genuinely a public stable
  surface. Block Phase 0 on this research landing.
- **Q5 (Diller-Def-12 NAP analysis lives upstream in gunray):** Q
  controls both packages. Phase 3 in this workstream becomes "consume
  upstream NAP analysis"; the actual algorithm implementation moves
  to a parallel gunray-side workstream that runs concurrently with
  Phases 1-2 here.
- **Q11 (preferences + rule-name plumbing in Phase 1):** built in
  from the start, not retrofitted.
- **Q15 (serial execution, after ASP):** this workstream cannot
  begin until the ASP backend workstream ships.

### Phase 0 — Dependency posture and gunray API research

**Effort:** 0.5 day setup + 1-2 days for the Q4 research subagent.

**Files:** `pyproject.toml`, `README.md`, `CONTRIBUTING.md`,
`reports/gunray-coupling-research-2026-MM-DD.md` (new, from Q4
subagent).

**Decisions resolved (2026-05-01):**

1. **Optional extra confirmed.** `pip install
   formal-argumentation[grounding]` (decision Q1). Zero-deps policy
   preserved for users not doing FO grounding.
2. **gunray pin via `git+`.** gunray is not on PyPI per its README
   (decision Q1 explicitly accepts this); pin to a tagged commit:
   `gunray @ git+https://github.com/ctoth/gunray.git@<tag>`. Specific
   tag chosen at Phase 0 close.
3. **CI symmetric (decision Q2).** Add `gunray @ git+...` to
   `[dependency-groups].dev` so CI installs it and the grounding
   tests run in CI alongside the existing z3-solver-driven tests.
4. **License compatibility verified.** gunray MIT, `argumentation`
   MIT-or-Apache. Compatible.

**Q4 research subagent deliverable:** confirms Architecture A is
viable and identifies any DeLP-flavoured pieces that would leak
through `Program` / `SemiNaiveEvaluator` and need wrapping. Worst
case escalates to Architecture C (vendored thin Datalog engine
inside `argumentation`); cheap insurance to know now.

**Success criterion:** `pyproject.toml` carries the
`[grounding]` extra; CI installs gunray; the Q4 research report
sits in `reports/` with an unambiguous Architecture A
confirmation (or escalation to a documented alternative).

**Risks:** Optional-extras testing matrix doubles. Mitigation: a
single `tests/test_grounding/` folder gated on
`pytest.importorskip`.

### Phase 1 — First-order ASPIC+ representation

**Effort:** 3-5 days.

**Files:** new `src/argumentation/aspic_first_order.py`; updates to `src/argumentation/__init__.py`; new `tests/test_aspic_first_order.py`.

**Deliverables:**

- `Variable(name: str)` — frozen dataclass.
- `Term: TypeAlias = Variable | Scalar` (consistent with existing `Scalar`).
- `Atom(predicate: str, terms: tuple[Term, ...])` — possibly-non-ground atom.
- `FOLiteral(atom: Atom, negated: bool)`.
- `FORule(antecedents: tuple[FOLiteral, ...], consequent: FOLiteral, kind: str, name: str | None)`.
- `FOArgumentationSystem`, `FOKnowledgeBase` — first-order analogues.
- `FOTheory` — convenience wrapper carrying the system, KB, contrariness, and an explicit `constants: frozenset[Scalar]` field (Herbrand universe seed).
- A `ground(theory: FOTheory, ground_atoms: dict[Atom, frozenset[GroundAtom]]) -> tuple[ArgumentationSystem, KnowledgeBase]` plumbing function — used by Phase 2 to assemble the propositional theory from substitutions returned by gunray.
- **(Decision Q11, 2026-05-01) Preference and rule-name plumbing
  built in from the start** — not deferred to Phase 4. Specifically:
  - Each ground `Rule` produced from an `FORule` carries an explicit
    `source_rule: FORule` field. Document this on the `Rule` dataclass.
  - `PreferenceConfig.translate_to_ground(fo_pref, fo_to_ground:
    dict[FORule, frozenset[Rule]]) -> PreferenceConfig` — promotes
    every FO pair `(weaker_fo, stronger_fo)` to all matching ground
    pairs whose source rules match. Tested in Phase 1 against a
    propositional baseline.
  - Defeasible rule naming convention: `name =
    f"{fo_rule.name}__{substitution_hash}"`. Each ground instance is
    a distinct attack target.

**Success criterion:** Round-trip property test — for any propositional `(ArgumentationSystem, KnowledgeBase)` lifted into a degenerate `FOTheory` (no variables) and grounded with the empty substitution, you get back the original; tested with Hypothesis. **Plus:** the preference-translation regression test from §Risks below passes.

**Risks:**

- *Preference orderings are over Rule and Literal identity.* The
  `translate_to_ground` deliverable above closes this — preferences
  are now first-class plumbing in Phase 1, not a Phase-4
  retrofit. Add a focused regression test that lifts a propositional
  theory with non-trivial preferences to FO, grounds, and verifies
  preferences survive on the ground rules.
- *Naming for defeasible rules* (`Rule.name` for undercut targeting). The naming convention above (`name = f"{fo_rule.name}__{substitution_hash}"`) is now a Phase 1 deliverable. Test on a small theory with two defeasible rules sharing a head but differing in body — undercuts must target distinct ground rules.

### Phase 2 — Bridge to gunray (Transformation 1)

**Effort:** 4-6 days.

**Files:** new `src/argumentation/grounding_bridge.py`; new `tests/test_grounding_bridge.py`.

**Deliverables:**

- `theory_to_program(theory: FOTheory) -> gunray.Program` — emits surface-syntax rules. For each `FORule`, produce one Datalog rule (using `~p(X)` for negated literals; gunray's parser supports strong negation per `parser.py`). For each contrariness pair, produce a Datalog rule connecting the conclusion atoms (matches Algorithm 1 step 2). For each premise, emit as a Datalog fact via `Program.facts`.
- `extract_substitutions(model: gunray.Model, rule: FORule) -> frozenset[dict[str, Scalar]]` — for each FO rule, the set of substitutions `theta` such that `body(rule) theta ⊆ model`. Implementation: Cartesian iteration over per-body-atom matching tuples followed by variable-binding consistency check.
- `ground_theory(theory: FOTheory, *, evaluator=None) -> tuple[ArgumentationSystem, KnowledgeBase, PreferenceConfig]` — orchestrates: build Program → run `SemiNaiveEvaluator.evaluate` → extract substitutions per rule → assemble propositional theory via Phase-1 plumbing.

**Success criterion:**

- A 4-rule, 3-constant FO theory with a known small ground theory passes a round-trip differential test: `ground_theory` output equals a hand-built propositional theory.
- Differential test on a propositional theory lifted to FO and back: same complete extensions as the original (computed via `argumentation.dung` after ASPIC+ build).

**Risks:**

- *Defeasible rules in the Datalog program.* Diller emits all ASPIC+ rules into the Datalog program; defeasible rules contribute to `lfp(T_P)` for grounding-substitution purposes only — they are not "fired" defeasibly inside Datalog. This means a defeasible rule like `bird(X) => flies(X)` becomes the Datalog rule `flies(X) :- bird(X).` The Datalog model may overstate which conclusions are defeasibly *warranted*, but that is fine — we only use it to find which substitutions could possibly produce arguments. Document this clearly because it surprises readers.
- *Contrariness in Datalog.* Encoding contrary pairs as Datalog rules can introduce loops if we're not careful (`p :- ~p` style). Use distinct predicate suffixes for negative literals (`p__neg`) and test on toy cycles.
- *Surface syntax round-trip.* gunray's parser is strict; an FO rule with an unhappy character ordering could parse-fail. Build emitter against `gunray.parser.parse_atom_text` test fixtures.

### Phase 3 — Non-approximated predicates (Transformation 2)

**Decision Q5 (2026-05-01): the NAP analysis lives upstream in
gunray, not in `argumentation`.** Q controls both packages, the
algorithm benefits gunray's own `inspect_grounding` directly, and
keeping it upstream avoids the architectural debt of duplicating
Diller-12 across two repos.

This phase therefore splits into a **parallel cross-repo workstream**:

#### Phase 3a — Upstream NAP analysis in gunray (gunray repo)

**Effort:** 5-8 days. The engineering payoff. **Runs concurrently
with Phases 1-2 here** — no blocking dependency until Phase 3b.

**Repo:** `../gunray/`.

**Files:** extend `gunray/src/gunray/grounding.py`; new
`gunray/tests/test_diller_def12.py`; update
`gunray/CHANGELOG.md`; bump `gunray/pyproject.toml` minor version.

**Deliverables (in gunray):**

- `compute_non_approximated(program: Program) -> frozenset[str]` —
  exposed via `gunray.grounding.compute_non_approximated`. Predicate
  names that satisfy Diller 2025 Definition 12. Implementation is a
  fixed-point over predicate-dependency edges:
  1. Build the dependency graph `predicate -> {(predicate, polarity, rule_kind)}` from all rules.
  2. Initialise NAP set with all fact predicates.
  3. Iterate: for each predicate `p`, add to NAP if every rule whose head predicate is `p` is strict AND every body predicate is already in NAP.
  4. Negative-dependency clause from Definition 12: if `p` depends negatively on `q`, then `q` must also be in NAP for `p` to qualify.
  5. Stop at fixpoint.
- `simplify_program(program: Program, non_approximated: frozenset[str], model: Model) -> Program` — apply the three Transformation-2 reductions in `Program` terms (the consumer in `argumentation` then lifts the simplified ground program back into ASPIC+ data structures):
  1. Drop rules whose head predicate is non-approximated; promote the head atom to facts directly.
  2. Drop fact-only rules.
  3. Drop contraries that have no ground attacking instance.
  4. Repeat until fixpoint.
- Update `inspect_grounding` to call the new analysis, replacing the
  current conservative DeLP-only fragment. Keep the conservative
  path callable for backwards compat.

**Cross-repo coordination plan:** open the gunray PR with a draft
of the API surface before the implementation lands so the
`argumentation` consumer can be written against the agreed shape.
Tag the gunray release before Phase 3b begins.

#### Phase 3b — Consume upstream NAP in `argumentation`

**Effort:** 1-2 days.

**Files:** update `src/argumentation/grounding_bridge.py` to call
`gunray.grounding.compute_non_approximated` and
`gunray.grounding.simplify_program` after the
`SemiNaiveEvaluator.evaluate` call; update test fixtures.

**Deliverables:**

- Consume the new gunray API; thread the simplified `Program` through
  the existing lift-back path from Phase 2.
- Pin `[grounding]` extra to the gunray version that includes the
  new API (`gunray @ git+...@vX.Y` where vX.Y has Diller-12).

**Success criterion:**

- Differential test (in `argumentation`): for several FO theories,
  `extensions(simplify_grounding(ground(T)))  ==  extensions(ground(T))`. Same complete extensions, fewer arguments built.
- Size test on the worked example from §1.2: NAP correctly
  identifies `penguin`, `bird` as non-approximated; ground theory
  shrinks from 6 to 5 rules with the predicted KB enrichment.

**Risks:**

- *Definition 12 is non-trivial.* The four clauses interact recursively. A naive implementation may either under- or over-approximate. Mitigation (in gunray): implement straight from the paper's fixpoint formulation (notes.md lines 78-87), then property-test against Transformation 1 output: any predicate marked NAP must produce the same ground atoms via simplification as via the full ASPIC+ argument tree. This is Diller's Lemma 1.
- *Cross-repo PR cadence.* The two repos must stay in lockstep
  during Phase 3a/3b. Mitigation: develop both branches in parallel
  with the gunray PR open as draft from day one of Phase 3a;
  `argumentation`'s Phase 3b PR pins the exact gunray commit hash
  until the gunray release tag is cut.
- *Contrary elimination corner case.* Diller's Algorithm 2 step 8 removes contraries whose attacking predicate has no ground instances. Edge case: contrary added by transposition-closure of a strict rule (Modgil and Prakken 2018 Def 12) — must ensure the closure runs *before* simplification, not after, or we risk dropping a contrary that the closure would have re-introduced. Test this on both sides of the repo boundary.

### Phase 4 — Lift back and integrate with existing reasoners

**Effort:** 2-3 days.

**Files:** `grounding_bridge.py` (extend); `tests/test_grounding_bridge.py` (extend); `docs/grounding.md` (new).

**Deliverables:**

- `ground_theory` returns a `(ArgumentationSystem, KnowledgeBase, PreferenceConfig)` triple that is a drop-in input to:
  - `argumentation.aspic.build_arguments` / `build_abstract_framework` for in-memory reasoning.
  - `argumentation.aspic_encoding.encode_aspic_theory` for the ASP-style fact handoff.
  - The SAT pipeline via `aspic_encoding` plus `sat_encoding`.
- A short `docs/grounding.md` explaining the pipeline and how to use it — three code examples (FO theory, ground it, query extensions).

**Success criterion:** the worked example from §1.2 runs end-to-end: build FO theory → ground → encode → enumerate complete extensions → verify against a hand-grounded baseline.

**Risks:** Preference plumbing forgets to translate. Add a focused regression test that lifts a propositional theory with non-trivial preferences to FO, grounds, and verifies preferences survive on the ground rules.

### Phase 5 — Benchmark

**Effort:** 4-6 days.

**Files:** new `tools/bench_grounding.py`; new `notes/bench-grounding-2026-MM-DD.md` for results capture.

**Deliverables:**

- Synthetic FO benchmark generator parameterised on the Diller S1/S2 axes (number of strict rules, number of defeasible rules, variables per rule, constants, contrary count). Generate 20 instances per configuration as Diller does.
- Naive grounder for comparison (substitute every variable with every constant; no Datalog filtering).
- Three-way comparison: naive, Transformation 1, Transformation 2.
- **(Decision Q12, 2026-05-01) External-systems columns required,
  not stretch:**
  - **ASPforASPIC** (Lehtonen reference)
  - **ANGRY** if reachable
  - **TOAST** if reachable
  - **Diller's own reference implementation** if accessible
  - Document install instructions, version numbers, and any patching
    in `bench/README.md` for reproducibility
  - Windows install caveat: external systems may need WSL or
    container fallback; CI runs only the base three-way comparison,
    external columns stay manual.

**Success criterion:**

- Transformation 2 ground-theory size is empirically dominated by Transformation 1, and both dominate naive, on configurations with a non-trivial sublanguage of strict-only predicates. (Matches Diller's published results.)
- A reproducible script + a written-up table in `notes/bench-grounding-...md` that we can cite when writing the workstream completion report.

**Risks:**

- Benchmark instances must be carefully generated: too few constants and Transformation 1 already collapses the space; too many and the naive baseline times out before producing any data point. Use the parameter ranges from Diller paper §5.1 (`n_s` 10-100, `n_c` 5-90, vars 1-3, constants 3-30) as starting calibration.
- Differential correctness: every benchmark instance must produce the same complete extensions across all three grounders. A grounder that loses arguments wins benchmarks for the wrong reason. Bake a correctness-cross-check into the harness on every instance, not as a separate suite.

### Phase totals

| Phase | Effort (days) | Repo | Cumulative |
|---|---|---|---|
| 0 | 0.5 + 1-2 (Q4 research) | argumentation | 1.5-2.5 |
| 1 | 3-5 (preferences now in scope per Q11) | argumentation | 4.5-7.5 |
| 2 | 4-6 | argumentation | 8.5-13.5 |
| 3a | 5-8 (parallel with 1-2) | **gunray** | concurrent, no addition |
| 3b | 1-2 | argumentation | 9.5-15.5 |
| 4 | 2-3 | argumentation | 11.5-18.5 |
| 5 | 4-6 + 2-4 (external systems per Q12) | argumentation | 17.5-28.5 |

**Three to six engineering weeks** for the full workstream in
`argumentation`, plus Phase 3a (5-8 days in `gunray`) running
concurrently with Phases 1-2. Phase 3b is the gating step where
the two repos meet.

This workstream **runs second** in the serial sequence per decision
Q15 (ASP → Datalog → DG). It cannot begin until the ASP backend
workstream ships. The DG workstream cannot begin until this one
ships.

---

## 5. Risks and unknowns

**R1. gunray's Datalog feature set vs Diller's needs.** Diller requires stratified negation, function-free Herbrand universe, and the basic positive Datalog body grammar. Gunray supplies all three: `NegationSemantics.SAFE` is exactly Apt-Blair-Walker stratified negation; `Wildcard`, `Variable`, `Constant`, `Atom` cover the term grammar; `Comparison` and arithmetic constraints are bonuses. Gunray also has compiled-matcher fast paths for common rule shapes. The gap I have not directly verified: whether gunray's parser accepts the surface form we want to emit (specifically: ASPIC+ negative literals as `~p(X)` body atoms versus `not p(X)` default-negated atoms — these mean different things). The bridge spec needs to nail this in Phase 2.

**R2. First-order representation.** Verified absent. Phase 1 must build it. Risk is moderate: the existing `GroundAtom`/`Literal`/`Rule` shape is a clean precedent, and the author has anticipated the work (the `aspic.py` Diller citation is already there).

**R3. Coupling concern.** A breaking change in gunray's `Program` shape, `Model` shape, or `SemiNaiveEvaluator.evaluate` signature ripples into our bridge. Mitigations:

- Pin to a tagged gunray version, not main.
- Define an internal `DatalogBackendProtocol` (a typing.Protocol) that captures only the methods we use (`evaluate(Program) -> Model`); the bridge depends on the protocol, the optional-extra binding glues gunray to it. Future swap-in of a different Datalog engine (Souffle bindings, embedded clingo grounder) is then a matter of writing one adapter.
- Property tests on the bridge are independent of the engine implementation.

**R4. Two-project coordination.** The workstream lives entirely in `argumentation`. Gunray modifications would only become necessary in two scenarios: (a) Phase 3's NAP analysis is upstreamed, (b) we want to use `gunray.grounding.GroundingInspection` directly (Architecture B from §3.3). Neither is required for the v1. If we touch gunray it should be a separate PR with its own design note.

**R5. Diller's NAP analysis corner cases.** The Definition 12 fixed-point is non-trivial. Specific corner cases I expect to hit:

- *Mutual recursion through negation.* Stratified negation forbids it, so should not arise in correct inputs — but the analysis must defensively detect and refuse rather than infinite-loop.
- *Predicates appearing only in contrariness*, never in any rule body. Are these non-approximated? Per Definition 12 yes (no rule consumes them, all consumers strict). Test explicitly.
- *Predicates produced by a strict rule whose body contains an approximated predicate.* By clause (3) negated, so the head predicate is approximated. Test explicitly.
- *Transposition-closure interaction.* `argumentation.aspic.transposition_closure` produces extra strict rules; Phase 3's NAP analysis must run *after* transposition closure on the ground theory, or *before* on the FO theory if we transpose first-order rules (currently the codebase only transposes propositional rules — Phase 1 may need to extend this).

**R6. Preferences and Diller silence.** Diller does not address preference orderings. Our `PreferenceConfig` is structural and lifts cleanly, but only if Phase 1 carries the source-rule link through grounding. This is a design constraint, not a research risk.

**R7. Semantics other than complete.** Diller proves correctness only for complete extensions. Preferred, stable, grounded, ideal *should* be preserved by the same grounding (extensions of complete-preserving relation), but we have no theorem. Mitigation: a differential test suite that compares each semantics' extensions across the FO->ground->reason and propositional-only paths on small generated instances.

**R8. Optional-dependency UX.** A user who installs `formal-argumentation` without `[grounding]` and tries to use the FO API gets `ImportError: gunray`. Mitigation: at module-import time of `grounding_bridge`, raise an actionable `ImportError("formal-argumentation grounding requires the [grounding] extra: pip install 'formal-argumentation[grounding]'")`. Existing `aspic` etc. continue to work without gunray.

**R9. PyPI status.** Per gunray's README, install is via git URL. If gunray is not on PyPI, the optional-extra spec must use a `git+` URL, which complicates PyPI distribution of `argumentation` itself. Recommended sequence: gunray gets tagged and PyPI'd before `argumentation` cuts a release that advertises the `[grounding]` extra publicly. In the interim, document the install form in README and CI.

---

## 6. Decisions (resolved 2026-05-01)

All five gating decisions resolved. Restated here as the canonical
record:

1. **First-order ASPIC+ in `argumentation`?** → **Yes.** Existing
   Diller citation in `aspic.py:GroundAtom` docstring confirmed the
   intent.
2. **gunray dependency posture?** → **Optional extra `[grounding]`
   with `git+` install** (gunray not on PyPI). CI symmetric — gunray
   in `[dependency-groups].dev` so grounding tests run in CI.
3. **Where does Diller-Def-12 NAP analysis live?** → **Upstream in
   gunray.** Q controls both packages. Phase 3 split into Phase 3a
   (gunray repo, parallel with Phases 1-2) and Phase 3b
   (argumentation repo, consumes the upstream API).
4. **Preference and rule-name plumbing in Phase 1 or Phase 4?** →
   **Phase 1.** Built in from the start. Retrofitting hurts.
5. **Benchmark scope?** → **Include external systems** (ASPforASPIC,
   ANGRY, TOAST, Diller's reference if accessible). Phase 5 expands
   by 2-4 days for install + calibration.

Cross-workstream decisions also affecting this workstream:

- **Q4 (gunray coupling Architecture A) needs a research subagent
  before Phase 0 begins.** Q flagged this as needing more research.
  Phase 0 now includes dispatching that subagent; report lands in
  `reports/gunray-coupling-research-2026-MM-DD.md`. Worst case
  escalates to Architecture C (vendored thin Datalog engine).
- **Q15 (serial execution).** This workstream runs **second**, after
  ASP backend ships and before DG/treewidth begins.
- **Q3 (keyword dispatch, no Backend Protocol).** When this
  workstream's ground-theory output hands off to the existing SAT or
  ASP backends, it uses the widened keyword dispatch from the ASP
  workstream — no new Protocol introduction here.

---

## Appendix — file inventory after the workstream

New files:

- `src/argumentation/aspic_first_order.py`
- `src/argumentation/grounding_bridge.py`
- `src/argumentation/grounding_simplification.py`
- `tests/test_aspic_first_order.py`
- `tests/test_grounding_bridge.py`
- `tests/test_grounding_simplification.py`
- `tools/bench_grounding.py`
- `docs/grounding.md`
- `notes/bench-grounding-2026-MM-DD.md`

Modified files:

- `pyproject.toml` (add `[grounding]` extra)
- `src/argumentation/__init__.py` (register new modules)
- `README.md` (mention the grounding pipeline and the extras install)

No file in `src/argumentation/aspic.py` or `aspic_encoding.py` needs to change for the workstream's core: the propositional pipeline is untouched, the FO layer sits on top, and the bridge produces propositional outputs that flow into the existing reasoners unchanged.
