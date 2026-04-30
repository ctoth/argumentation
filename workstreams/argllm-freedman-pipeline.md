# ArgLLM / Freedman Pipeline Workstream

## Goal

Implement the formal, testable structure of Freedman et al.'s Argumentative LLM
claim-verification pipeline without pretending the package owns the empirical
LLM component.

## Primary Paper

- Freedman, Dejl, Gorur, Yin, Rago, and Toni (2025), "Argumentative Large
  Language Models for Explainable and Contestable Claim Verification".

Reread page images directly before implementing pipeline stages, DF-QuAD
semantics, thresholds, or example behavior.

## Current State

- `argumentation.llm_surface` builds package-native weighted bipolar graphs.
- It computes strengths using the package's Potyka-style quadratic-energy
  gradual semantics.
- It provides explanation and contestation wrappers.
- It does not implement the paper's argument generation, intrinsic strength
  attribution, DF-QuAD main semantics, prompt orchestration, or empirical
  evaluation pipeline.

## Execution Mode

Use TDD with paper-derived examples and properties:

1. Reread the paper page for the pipeline component.
2. Add a failing fixture or property for the stated formal behavior.
3. Implement that component without adding live LLM dependencies to core tests.
4. Use fixtures and typed boundaries for all LLM-generated artifacts.

Hypothesis properties should target formal QBAF and semantics claims from the
paper and its cited definitions, not prompt-quality assumptions.

## Phases

### Phase 1: Pipeline Types

- Add typed records for claim input, generated BAF, intrinsic strength
  attribution, QBAF, strength calculation result, threshold decision, and
  explanation artifact.
- Keep LLM prompts and model calls outside the core formal package surface.
- Provide fixture loaders for paper-style examples.

Paper-derived properties:

- A generated BAF contains attacking and supporting arguments for the target
  claim exactly as the pipeline stage specifies.
- Intrinsic strength attribution maps generated arguments to base scores in the
  paper's strength codomain.
- QBAF construction preserves arguments, attacks, supports, and intrinsic
  strengths.

Acceptance criteria:
- The pipeline can be exercised end-to-end with fixtures and no network/model
  calls.

### Phase 2: DF-QuAD Semantics

- Implement discontinuity-free quantitative argumentation debate (DF-QuAD)
  gradual semantics as used in the paper's main experiments.
- Keep Potyka quadratic-energy semantics as an alternate semantics only if the
  API names it explicitly.
- Add tests from the paper's formulas and simple hand-computable cases.

Paper-derived properties:

- With no attackers, the attacker aggregation function returns the value stated
  by the DF-QuAD definition.
- With no supporters, the supporter aggregation function returns the value
  stated by the DF-QuAD definition.
- Strength values stay in the paper's codomain.
- Increasing supporter strength does not reduce target strength under the
  DF-QuAD equations, where the equations imply that monotonicity.
- Increasing attacker strength does not increase target strength under the
  DF-QuAD equations, where the equations imply that monotonicity.

Acceptance criteria:
- Hypothesis generates acyclic QBAFs for stable recursive evaluation.
- Cyclic handling is either implemented from a cited semantics or explicitly
  rejected.

### Phase 3: Decision Threshold and Claim Verification

- Implement the paper's true/false decision threshold as a configurable value
  with the paper default.
- Return both strength and decision, not just a boolean.
- Preserve the QBAF explanation artifact.

Paper-derived properties:

- A claim with computed strength above the threshold returns true.
- A claim with computed strength below the threshold returns false.
- Boundary behavior at exactly the threshold matches the paper's stated rule.

Acceptance criteria:
- Tests include threshold examples from the paper figures or text where
  available.

### Phase 4: Explanation and Contestation

- Model the QBAF as the reasoning trail for the output.
- Implement contestation as adding typed evidence/arguments and recomputing the
  selected gradual semantics.
- Add attribution/counterfactual helpers only if the cited paper definitions are
  reread and tested.

Paper-derived properties:

- The explanation artifact contains the generated arguments, their relations,
  intrinsic strengths, and final strengths.
- Adding contesting evidence changes only the augmented QBAF components unless
  the paper's pipeline specifies regeneration.
- Recomputing after contestation is deterministic for fixed fixtures.

Acceptance criteria:
- No explanation function claims faithfulness beyond the QBAF reasoning trail it
  actually returns.

### Phase 5: Empirical Pipeline Boundary

- Add adapter interfaces for LLM argument generation and strength attribution.
- Keep concrete providers outside deterministic tests.
- Add contract tests for provider outputs using fixtures.

Paper-derived/source-derived properties:

- Provider outputs must be total over generated arguments.
- Provider outputs must not reference unknown arguments or relations.
- Dataset/model claims are not encoded unless the repository actually includes
  the relevant data and evaluation harness.

Acceptance criteria:
- Core tests remain offline and deterministic.
- Docs distinguish formal pipeline reproduction from empirical replication.

## Tests

Targeted command:

```powershell
uv run pytest tests\test_llm_surface.py -q
```

Expected additional test files:

```text
tests/test_df_quad.py
tests/test_argllm_pipeline.py
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- DF-QuAD is implemented and selected by default for the Freedman pipeline.
- Potyka quadratic-energy semantics is clearly an alternate formal backend.
- Pipeline stages are typed and fixture-testable without LLM calls.
- Hypothesis properties cover the formal QBAF/DF-QuAD behavior derived from the
  paper.
- Docs state that empirical LLM generation/evaluation is outside core package
  conformance unless separately implemented.

## Known Traps

- Do not use quadratic-energy semantics as a silent substitute for DF-QuAD in
  the ArgLLM paper path.
- Do not add live LLM calls to deterministic unit tests.
- Do not claim explanation faithfulness beyond the returned QBAF and strength
  computation.
- Do not encode empirical accuracy claims as package behavior.
