# Enforcement Workstream

## Goal

Implement paper-faithful enforcement for abstract argumentation while keeping
the existing unconstrained edit oracle clearly separate.

## Primary Papers

- Baumann (2010/2012), expansion-based enforcement in abstract argumentation.
- Wallner, Niskanen, and Jarvisalo (2017), extension enforcement algorithms and
  complexity results.
- Baumann, Doutre, Mailly, and Wallner (2021), enforcement survey and
  unification.

Reread page images directly for expansion definitions, enforcement variants,
and examples before writing tests or code.

## Current State

- `argumentation.enforcement` keeps the unconstrained Hamming edit oracle over
  attacks between existing arguments as a separate fixed-argument API.
- The edit type can represent argument deletion and attack deletion, and tests
  pin that this behavior is not Baumann-style expansion enforcement.
- The module now also exposes Baumann-style normal, strong, and weak expansion
  predicates and a bounded brute-force expansion-enforcement oracle whose
  witnesses never delete old arguments, delete old attacks, or add old-old
  attacks.

## Execution Mode

Use TDD with paper-derived properties:

1. Reread the relevant definition/proposition page image.
2. Write a failing example or Hypothesis property that asserts the paper claim
   under its stated preconditions.
3. Implement only enough production code to satisfy that claim.
4. Differential-test any optimized algorithm against a brute-force oracle that
   obeys the same expansion constraints.

Do not implement a compatibility bridge from unconstrained edits to expansion
enforcement. The target architecture is a separate expansion-enforcement API.

## Phases

### Phase 1: Preserve and Rename the Existing Oracle

- Rename or document the existing API as unconstrained edit enforcement.
- Add tests proving it may perform old-old attack edits and deletions, so users
  cannot mistake it for Baumann enforcement.
- Avoid removing it until the expansion API has coverage if existing users/tests
  depend on it.

Acceptance criteria:
- Public docs do not cite Baumann as if the unconstrained oracle implements his
  enforcement setting.
- Tests pin the current oracle's intended scope.
- Status: complete.

### Phase 2: Expansion Model

- Add explicit data types for expansions over original AF `F=(A,R)` and new
  argument set `A*`.
- Implement normal, strong, and weak expansion predicates from Baumann's
  definitions.
- Forbid old-argument deletion, old-attack deletion, and added attacks between
  old arguments in Baumann mode.

Paper-derived properties:

- Normal expansion preserves the old attack relation exactly and adds only
  interactions involving new arguments.
- Strong expansion satisfies the paper's restriction on attacks between old and
  new arguments.
- Weak expansion satisfies the paper's weaker restriction.
- Every normal expansion is also a weak expansion if the paper states that
  relation; encode only relations actually stated or proved in the paper.

Acceptance criteria:
- Hypothesis generates old AFs, new argument sets, and candidate expansions,
  then checks expansion predicates against the paper constraints.
- Status: complete.

### Phase 3: Enforcement Variants

- Implement conservative, strong, and weak enforcement variants.
- Implement liberal variants only after rereading the semantics-change
  definition and writing tests for it.
- Keep acceptance-condition targets explicit: credulous, skeptical, and exact
  extension enforcement.

Paper-derived properties:

- Conservative enforcement keeps the semantics fixed.
- Liberal enforcement may change semantics only as the paper permits.
- Deleting old material or changing old-old attacks never appears in an
  expansion-enforcement witness.
- If a target is already enforced, the zero/new-argument witness is returned
  only when allowed by the paper definition.

Acceptance criteria:
- Every variant has at least one example where unconstrained edit enforcement
  finds a cheaper witness that Baumann enforcement correctly rejects.
- Status: conservative normal/strong/weak expansion variants are implemented
  for credulous, skeptical, and strict/non-strict extension targets. Liberal
  semantics-changing variants are intentionally not implemented because this
  pass did not reread and encode their semantics-change definition.

### Phase 4: Brute-Force Reference Oracle

- Implement a small expansion-only brute-force oracle for generated AFs.
- Use it as the executable specification for later SAT/MaxSAT-backed
  enforcement.
- Bound generated new arguments and new attacks in tests to keep runtime small.

Paper-derived properties:

- Returned witnesses satisfy the selected expansion predicate.
- Returned witnesses enforce the selected target under the selected semantics.
- Minimality is measured only over the paper's allowed expansion choices.

Acceptance criteria:
- Optimized enforcement, if added, is differential-tested against the
  expansion-only brute-force oracle on small AFs.
- Status: complete for the bounded brute-force reference oracle; no optimized
  backend was added.

### Phase 5: Algorithmic Backends

- Add SAT/MaxSAT encoding only after the expansion oracle is correct.
- Use paper-derived clauses/properties as tests before implementation.
- Keep solver dependency optional unless it resolves from CI without local pins.

Acceptance criteria:
- Backend results agree with the oracle for generated small cases.
- Solver-unavailable behavior is structured and tested.
- Status: not applicable in this execution pass; no SAT/MaxSAT backend was
  added.

## Tests

Targeted command:

```powershell
uv run pytest tests\test_enforcement.py -q
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- Existing unconstrained edit enforcement is not presented as Baumann
  enforcement.
- Expansion enforcement implements paper-defined normal, strong, and weak
  constraints.
- Enforcement witnesses never use operations the paper excludes.
- Hypothesis properties cover generated AFs and generated expansions.

## Known Traps

- Removing old attacks or adding old-old attacks can trivialize enforcement;
  Baumann explicitly excludes those moves.
- Do not let a minimal Hamming edit metric replace the paper's expansion
  constraints.
- Do not use passing acceptance tests as evidence of enforcement conformance
  unless the witness itself is checked against the expansion definition.
