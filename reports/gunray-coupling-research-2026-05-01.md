# Gunray Coupling Research

Date: 2026-05-01

Verdict: Architecture A is viable. `argumentation` can depend only on gunray's
public Datalog surface: `Program`, `Model`, `NegationSemantics`, and
`SemiNaiveEvaluator`.

Evidence inspected in `../gunray`:

- `src/gunray/__init__.py` exports `Program`, `Model`, `NegationSemantics`, and
  `SemiNaiveEvaluator` in `__all__`.
- `src/gunray/schema.py` defines `Program(facts, rules)` as the public Datalog
  schema. Rules are surface strings, so the bridge can avoid private
  `_normalize_rules` internals.
- `src/gunray/evaluator.py` exposes `SemiNaiveEvaluator.evaluate(program,
  negation_semantics=NegationSemantics.SAFE) -> Model`.
- DeLP-flavoured types (`DefeasibleTheory`, `DefeasibleSections`,
  `inspect_grounding`) are separate and do not have to appear in the
  `argumentation` bridge.

Dependency style:

- `../QRead/pyproject.toml` uses project dependency names plus unpinned Git
  sources in `[tool.uv.sources]`, for example
  `gui-builder = { git = "https://github.com/AccessibleApps/gui_builder.git" }`.
- This workstream follows that style for gunray:
  `gunray = { git = "https://github.com/ctoth/gunray.git" }`.
- No explicit SHA, branch, tag, or `rev` is pinned in `pyproject.toml`.

Risk notes:

- `uv.lock` records a resolved Git commit for reproducibility, as QRead's
  lockfile does. That is lockfile resolution, not a source-level SHA pin.
- Gunray's Datalog parser accepts surface-rule strings; bridge tests must cover
  the exact atom rendering used for ASPIC+ positive and negated literals.
- Diller Definition 12 non-approximated-predicate analysis is not present on the
  public gunray surface today. The first argumentation-side implementation should
  treat Transformation 2 as unavailable unless the upstream API appears.
