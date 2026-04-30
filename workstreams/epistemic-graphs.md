# Epistemic Graphs Workstream

## Goal

Implement paper-faithful epistemic graph and probabilistic epistemic
argumentation reasoning, replacing the current finite belief-level approximation
where the public API claims more than it proves.

## Primary Papers

- Hunter, Polberg, and Thimm (2018), "Epistemic Graphs for Representing and
  Reasoning with Positive and Negative Influences of Arguments".
- Potyka, Polberg, and Hunter (2019), "Polynomial-Time Updates of Epistemic
  States in a Fragment of Probabilistic Epistemic Argumentation".
- Related probabilistic argumentation sources only after the primary
  definitions are locked down.

Reread page images directly before implementing epistemic language syntax,
arc labels, satisfiability, entailment, or update procedures.

## Current State

- `argumentation.epistemic` includes Hunter's epistemic language,
  probability functions over possible worlds, induced probability labellings,
  multi-labelled arcs with dependent labels, Potyka-style linear atomic
  constraints, z3-backed satisfiability/entailment, and a least-squares
  probability-labelling update surface.
- The older argument-to-float influence helpers remain available as an
  explicitly approximate finite-grid API.

## Execution Mode

Use TDD with paper-derived properties:

1. Reread the page defining the syntax, semantics, constraint, or theorem.
2. Write a failing parser, evaluator, satisfiability, or entailment test.
3. Add a Hypothesis property for the paper claim under generated inputs that
   satisfy the paper's preconditions.
4. Implement the smallest change that satisfies the test.

Do not keep adding local propagation rules unless they are explicitly grounded
in a reread paper statement.

## Phases

### Phase 1: Epistemic Language AST

- Implement argument terms and Boolean combinations of arguments.
- Implement probability terms `p(alpha)` where `alpha` is an argument term.
- Implement arithmetic combinations of probability terms.
- Implement epistemic atoms with comparisons against constants in `[0, 1]`.
- Implement Boolean combinations of epistemic atoms.

Paper-derived properties:

- Parsed formulas round-trip through the writer for every grammar form the paper
  defines.
- Formula evaluation over a probability function matches the paper's semantic
  clauses.
- Constants outside `[0, 1]` are rejected where the paper requires that domain.

Acceptance criteria:
- Tests include each syntactic form from the paper's epistemic language
  definition.

### Phase 2: Probability Functions and Labellings

- Represent possible worlds over finite argument sets.
- Represent probability functions over worlds.
- Represent probability labellings over arguments.
- Implement the paper's relationship between probability functions and induced
  labellings.

Paper-derived properties:

- World probabilities are nonnegative and sum to 1.
- Induced argument probabilities equal the sum of worlds where the argument is
  true.
- Any probability function induces a valid probability labelling.
- Any theorem claiming a labelling can replace a probability function in a
  fragment is encoded only for that fragment.

Acceptance criteria:
- Hypothesis generates small normalized probability functions and checks induced
  labellings.

### Phase 3: Labelled Epistemic Graphs

- Implement arcs with sets of labels from the paper's label alphabet, including
  positive, negative, and dependent labels.
- Allow multiple labels per arc when the paper permits it.
- Define graph satisfaction using the paper's epistemic constraints, not local
  ad hoc inequalities.

Paper-derived properties:

- Positive, negative, and dependent labels have exactly the semantics stated by
  the paper.
- Multi-labelled arcs satisfy the conjunction/disjunction behavior stated by
  the paper; do not infer behavior not stated.
- Graph examples from the paper evaluate to the stated satisfiable/unsatisfiable
  or influence outcomes.

Acceptance criteria:
- The current `InfluenceKind.NEUTRAL` surface is either replaced by the paper's
  dependent label or documented as package-local.

### Phase 4: Potyka 2019 Constraint Compilation

- Implement atomic linear constraints used by the polynomial fragment.
- Compile COH, SFOU, FOU, SOPT, OPT, JUS and support-dual constraints exactly
  where the paper defines them.
- Add LP-backed satisfiability and entailment for the supported fragment.

Paper-derived properties:

- COH attack constraints enforce the paper inequality for generated attacks.
- Support-dual constraints enforce the paper inequality for generated supports.
- PArgAtSAT/PArgAtENT results agree with direct finite-world enumeration on
  small generated instances where enumeration is feasible.
- LP objective/feasibility results are invariant under argument renaming.

Acceptance criteria:
- LP solver dependency resolves from normal package/CI sources, not a local
  path.
- If no acceptable solver is available, the workstream stops at a clear blocker
  rather than implementing a fake LP.

### Phase 5: Update Procedures

- Implement Potyka et al.'s update procedure only after the constraint and LP
  layer is correct.
- Add paper examples as tests before implementation.
- Compare update outputs against satisfiability/entailment checks.

Paper-derived properties:

- Updates preserve the constraints the paper says they preserve.
- Polynomial-fragment updates produce labellings that satisfy the compiled
  constraints.

Acceptance criteria:
- The old local propagation heuristic is renamed or removed from any
  paper-faithful API path.

## Tests

Targeted command:

```powershell
uv run pytest tests\test_epistemic.py -q
```

Expected additional test files:

```text
tests/test_epistemic_language.py
tests/test_epistemic_probability.py
tests/test_epistemic_lp.py
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- Epistemic language syntax and semantics are implemented from the paper.
- Probability functions/labellings and graph labels match paper definitions.
- Potyka fragment reasoning is LP-backed and tested against enumeration on
  small generated instances.
- Existing approximation APIs are clearly named as approximations or removed
  from paper-faithful paths.

## Known Traps

- Local monotone propagation is not Potyka's polynomial LP procedure.
- Interval constraints over arguments are not Hunter's full epistemic formula
  language.
- Do not collapse dependent labels into neutral/no-op labels unless the paper
  says so.
- Do not claim satisfiability or entailment without a solver or exhaustive
  finite-world check.
