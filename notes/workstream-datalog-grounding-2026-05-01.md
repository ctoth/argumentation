# Datalog grounding workstream — design report

Date: 2026-05-01
Goal: Write `reports/workstream-datalog-grounding.md` (~2500-4000 words) designing a Datalog-grounding workstream for first-order ASPIC+ in `argumentation`, using sibling project `gunray` as the Datalog engine. Diller 2025 is the theoretical basis.

## Confirmed observations

### `argumentation` codebase
- `src/argumentation/aspic.py`: data model is propositional. `GroundAtom(predicate, arguments=tuple[Scalar,...])` already supports arity > 0 syntactically — but `Literal.atom: GroundAtom` is named `GroundAtom` deliberately. There is no `Variable` type. `Rule.antecedents: tuple[Literal, ...]` and `Rule.consequent: Literal` are over ground literals.
- Grep for "first.?order|FirstOrder|Variable" in `src/argumentation/`: zero matches.
- `src/argumentation/__init__.py`: no FO module exported.
- Comment in `aspic.py` at GroundAtom docstring cites `Diller et al. 2025 Def 7` — author has anticipated this extension.
- `aspic_encoding.py`: ASP-style fact encoding for Lehtonen, Niskanen, Jarvisalo 2024 input format; works on the propositional ground theory `(ArgumentationSystem, KnowledgeBase, PreferenceConfig)`. This is the handoff target after grounding.
- `pyproject.toml`: ZERO runtime dependencies. `z3-solver` is an optional extra. Strong policy signal — gunray must be optional or vendored, not a hard dep.

### `gunray` codebase
- `src/gunray/types.py`: has `Variable(name)`, `Wildcard(token)`, `Constant(value)`, `Atom(predicate, terms)`, `Rule(heads, positive_body, negative_body, constraints, source_text)`, `GroundAtom`, `DefeasibleRule`, `GroundDefeasibleRule`. Function-free, Diller-compatible.
- `src/gunray/schema.py`: `Program(facts: PredicateFacts, rules: list[str])` — rules carried as **surface-syntax strings** parsed via `parser.parse_program`. So the bridge would emit text rules, OR build typed `Rule` objects directly via `_normalize_rules`.
- `SemiNaiveEvaluator.evaluate(program, *, negation_semantics=SAFE) -> Model` and `evaluate_with_trace(...) -> (Model, DatalogTrace)`. Public; in `__all__`.
- `Model.facts: ModelFacts = Mapping[str, set[FactTuple]]`. Lifting back to `argumentation.GroundAtom` is direct.
- `src/gunray/grounding_types.py`: already defines `GroundingInspection`, `GroundingSimplification` with `definite_fact_atoms`, `resolved_strict_rules`, `strict_rules_for_argumentation`, `defeasible_rules_for_argumentation`, `defeater_rules_for_argumentation`. **Diller-shaped data already exists in gunray.**
- `src/gunray/grounding.py`: `inspect_grounding(theory)` already does a CONSERVATIVE Diller-style strict/fact resolution (Definition 9, Algorithm 2). Self-cited Diller 2025 Definition 9 p.3, Algorithm 2 p.7. Comment says "Gunray only exposes the conservative DeLP-compatible fragment here: no defeasible or defeater rule is removed, and any strict rule whose body cannot be proven definite remains in the argumentation grounding report." — meaning the **non-approximated-predicates analysis (Definition 12) is NOT implemented**. That's the engineering payoff phase.
- License: MIT. Pyproject: zero runtime deps, `requires-python = ">=3.11"`. Same as `argumentation`. Fully compatible.
- Not on PyPI per README (install via git URL).
- `gunray.parser.parse_atom_text` is publicly exported — useful for Phase 2 emit-then-parse path.

### Diller 2025 (from notes.md)
- Two transformations: T1 maps each ASPIC+ rule (strict + defeasible) into a Datalog rule, queries Datalog engine for ground substitutions. T2 adds non-approximated-predicates optimization.
- Definition 8: T_P(I) = {h(r)θ | r ∈ P, θ ground subst, body(r)θ ⊆ I}. lfp(T_P) is the minimal Herbrand model.
- Definition 12: predicate p is non-approximated iff body conditions about strict-only-derivability hold; minimal set computed by fixed-point.
- Algorithm 2 simplifications: identify NAP, resolve NAP entirely in Datalog, generate ASPIC+ ground rules only for approximated, delete fact-only rules, eliminate unused contraries, fixpoint.
- Limitations: function-free FO ASPIC+ only; only complete extensions in correctness proofs; contrary function limited to atom-pair contraries; stratified negation limits.
- Prototype is ANGRY; benchmarked vs ASPforASPIC, TOAST.

## Strategic implications I've drawn (theory, marked as such)
- Phase 1 (FO ASPIC+ representation) is required, not optional.
- Gunray's schema.Program (rules as strings) is the natural input target; the bridge emits text. Alternative: typed `Rule` via `_normalize_rules` — but that's underscore-private; surface-string path is cleaner.
- Gunray's `GroundingInspection` machinery is built around `DefeasibleTheory` not `Program`. Two options for Phase 2: (a) shoehorn ASPIC+ into a `DefeasibleTheory` and call `inspect_grounding` (uses gunray's built-in conservative simplification); (b) call `SemiNaiveEvaluator` on a `Program` directly and do our own ground-substitution extraction. Option (a) saves work but tightly couples; option (b) is simpler and lets us own the Diller-12 logic in `argumentation`.
- Gunray's NegationSemantics.SAFE matches Diller's stratified negation requirement.

## Outstanding questions for Q (to put in §6)
- Does Q want FO ASPIC+ in `argumentation` at all?
- Optional extra `[grounding]` vs vendor vs hard dep?
- Build the Diller-12 NAP analysis in `argumentation` or upstream into gunray's `inspect_grounding`?
- ASP/SAT handoff target after grounding — existing `aspic_encoding.encode_aspic_theory` is ready; new ASP backend is sibling workstream.
- Preference orderings — Diller doesn't address them; punt or include?

## State
- Ready to draft the report. All required reads complete.
- No blockers.

## Next
Write `reports/workstream-datalog-grounding.md`.
