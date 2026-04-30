# SETAF and ICCMA SETAF Workstream

## Goal

Make SETAF semantics and SETAF I/O conform to the cited definitions and the
official competition format, rather than an invented compact format.

## Primary Papers and Sources

- Nielsen and Parsons-style SETAF definitions as used in the splitting paper
  inspected during the audit.
- The CEUR/competition material defining the SETAF or collective-attack input
  format used by ICCMA or related tracks.

Reread page images directly before using a definition, theorem, format example,
or complexity claim. If official format examples are not available as page
images, retrieve the primary source and convert it before changing code.

## Current State

- `argumentation.setaf` implements finite collective attacks
  `(tail_set, target)`.
- Conflict-free, defense, admissible, complete, grounded, preferred, stable,
  semi-stable, and stage semantics exist.
- `argumentation.iccma_setaf` currently uses a compact `p setaf` format that
  has not been verified against an official ICCMA format.

## Execution Mode

Use TDD for every slice:

1. Reread the relevant paper/source page images.
2. Add a failing paper example, format fixture, or Hypothesis property derived
   from a stated definition/proposition.
3. Implement the smallest conforming change.
4. Run targeted tests before the next slice.

Hypothesis properties must be paper-derived and must state the cited
definition/proposition they encode.

## Phases

### Phase 1: Semantic Definition Lockdown

- Add tests for Definition 1 collective attacks: `S` attacks `a` iff some tail
  `T` satisfies `T <= S` and `(T, a)` is an attack.
- Add tests for Definition 2 conflict-freeness and defense.
- Add tests for Definition 3 admissible, complete, grounded, preferred, and
  stable semantics.

Paper-derived properties:

- Singleton-tail reduction: if every SETAF attack tail is a singleton, SETAF
  conflict-free, admissible, complete, grounded, preferred, and stable results
  equal the corresponding Dung AF results.
- Stable full-range property: `S` is stable iff it is conflict-free and
  `S union S+ = A`.
- Grounded characterization: grounded is the subset-minimal complete extension.

Acceptance criteria:
- The test suite includes both fixed paper examples and generated singleton-tail
  reduction properties.

### Phase 2: Defense Edge Cases

- Generate collective attacks where a candidate attacks one member of an
  attacking tail but not all members.
- Assert the paper defense definition: to defend against a tail attack on `a`,
  the candidate must attack the attacking set, i.e. attack at least one member
  of each attacking tail.

Paper-derived properties:

- Defense monotonicity for the SETAF characteristic function where the paper
  relies on it.
- Admissible sets are conflict-free and defend each of their members.
- Complete sets are exactly admissible fixed points of the characteristic
  function.

Acceptance criteria:
- Hypothesis generates multi-attacker tails, self-attacks, and empty-candidate
  cases.

### Phase 3: Official SETAF I/O

- Identify the official input grammar for the intended SETAF/collective-attack
  track.
- Replace or clearly rename the compact `p setaf` format if it is not official.
- Add parser/writer round-trip tests using official examples.

Paper/source-derived properties:

- Parse/write round-trip preserves the exact SETAF relation up to documented
  ordering normalization.
- Writer output is accepted by the parser and contains no non-official line
  types.
- Parser rejects malformed lines the official grammar disallows.

Acceptance criteria:
- At least one official fixture is checked into tests.
- Docs say whether the format is official or package-local.

### Phase 4: Splitting Algorithms

- Decide whether splitting is part of the SOTA target or only a source of core
  definitions.
- If included, reread the splitting theorem pages and write failing tests for
  the decomposition result before implementing.
- If excluded, state that explicitly in docs and do not imply splitting support.

Acceptance criteria:
- Either splitting is implemented with theorem-derived tests or the surface is
  documented as core SETAF semantics only.

## Tests

Targeted commands:

```powershell
uv run pytest tests\test_setaf.py tests\test_iccma_setaf.py -q
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- Core SETAF semantics are backed by paper examples and paper-derived
  Hypothesis properties.
- SETAF I/O is either official and tested against official fixtures, or clearly
  named as package-local.
- No docs claim ICCMA SETAF conformance without primary-source evidence.

## Known Traps

- Do not treat a collective attack tail as independent binary attacks.
- Do not assume grounded-as-least-fixed-point is sufficient without checking it
  against the paper's minimal-complete characterization.
- Do not keep `p setaf` as "ICCMA" if the official grammar differs.
