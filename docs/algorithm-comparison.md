# Algorithm Comparison

Papers often describe the same algorithm differently — different variable names, intermediate variables, loop styles, algebraic rearrangements. propstore uses the [ast-equiv](../ast-equiv) package to determine whether two Python function bodies compute the same thing, independent of variable naming, coding style, or intermediate variables.

## Algorithm Claims

Algorithm claims have `type: algorithm` with these key fields:

```yaml
- id: claim50
  type: algorithm
  concept: expected_loss
  body: |
    def compute(p, L):
        return sum(p_i * l_i for p_i, l_i in zip(p, L))
  variables:
    - name: p
      concept: probability_distribution
    - name: L
      concept: loss_vector
  conditions:
    - "domain == 'decision_theory'"
```

- `body` — Python source code containing a function definition
- `variables` — list mapping local variable names to concept IDs
- `concept` — the output concept this algorithm computes (falls back to first variable's concept if omitted)
- `conditions` — optional CEL condition strings
- `stage` — optional pipeline stage label

At build time, the body is parsed and validated: it must contain a function definition, variables must be non-empty, each variable's concept must exist in the registry, and AST names are cross-checked against declared variables (unbound names trigger warnings, excluding known builtins like `sum`, `zip`, `range`).

## Variable Binding

Variable bindings are the bridge between propstore's concept vocabulary and algorithm-local names. Without them, comparison would fail because the same concept would have different names in different implementations.

Two transformers operate in sequence:

1. **ConceptNormalizer** — an `ast.NodeTransformer` that replaces `Name` and `arg` nodes with their concept IDs from the bindings dict. Also renames all function definitions to `"algorithm"`.
2. **PositionalRenamer** — alpha-renames remaining non-concept variables to positional names (`_v0`, `_v1`, ...) based on first-appearance order.

After both passes, two implementations of the same algorithm that used different local names for the same concepts produce identical ASTs.

## The Comparison Ladder

The core comparison (`ast_equiv.compare()`) implements a tiered equivalence check. Each tier is strictly more expensive than the last; the ladder short-circuits on the first match.

### Tier 1: Canonical AST Match

Both bodies are parsed, concept-normalized, positionally renamed, and run through the full canonicalization pipeline:

- Docstring stripping
- Dead code removal
- Augmented assignment normalization (`x += y` to `x = x + y`)
- Range simplification (`range(0, N, 1)` to `range(N)`)
- Boolean simplification (`x == True` to `x`)
- Constant folding
- Identity elimination (`x + 0`, `x * 1`, `x ** 1`)
- Repeated multiplication to power (`x * x` to `x ** 2`)
- Commutative sort for `+` and `*`
- While-to-for loop conversion
- Temp variable inlining (single-assignment, single-use locals)
- Dead branch elimination

`canonical_dump()` produces `ast.dump()` of the canonical tree. String equality on the two dumps determines a match. Result: `tier=1, equivalent=True, similarity=1.0`.

### Tier 2: Algebraic / Bytecode Equivalence

Two sub-strategies run at this tier:

**SymPy algebraic equivalence.** Both canonical ASTs are walked in parallel. Control flow must match structurally (same statement types in same order). Expression subtrees are converted to SymPy expressions and compared via `sympy.simplify(a - b) == 0`. When statement counts differ, the longer side's assignments are inlined to attempt a match. This catches cases like `x/d + y/d` vs `(x+y)/d`.

**Bytecode comparison.** Canonical ASTs are compiled to Python bytecode via `dis.get_instructions()`. Layout-dependent opcodes (`RESUME`, `NOP`, `CACHE`, etc.) are skipped. Augmented assignment binary ops are normalized to plain ops. Instruction sequences are compared for equality.

Either sub-strategy matching produces `tier=2, equivalent=True`.

### Tier 3: Partial Evaluation

Only runs when `known_values` are provided (a dict of `concept_name -> float`). A `ParameterSubstituter` replaces `Name` nodes with `Constant` values and removes substituted parameters from the function signature. The result is re-canonicalized and compiled to bytecode.

Two algorithms that differ only in a parameter value become identical after substitution. Result: `tier=3, equivalent=True`.

### Tier 4: Structural Similarity (informational only)

`SequenceMatcher` ratio on AST node signatures (node types, constant values, variable names, operator types, attribute names). This score is computed and reported but deliberately **not** used for equivalence claims — syntactically similar code can be semantically different (e.g., `a and b` vs `a or b` have near-identical ASTs but different semantics).

Result: `tier=0, equivalent=False, similarity=<float>`.

## Conflict Detection

The conflict detector (`conflict_detector/algorithms.py`) integrates algorithm comparison into the build pipeline:

1. Algorithm claims are grouped by output concept via `_collect_algorithm_claims()`
2. For each concept with 2+ claims, pairwise `ast_compare()` is called
3. If `result.equivalent and result.tier <= 2`: no conflict (equivalent algorithms)
4. Otherwise: a conflict is recorded with `derivation_chain = f"similarity:{result.similarity:.3f} tier:{result.tier}"`
5. Condition overlap and explicit context lifting are respected — two algorithms with fully disjoint conditions produce a `PHI_NODE`, not a conflict

Error tolerance: if `ast_compare` raises `ValueError` or `SyntaxError` for a pair, the pair is logged and skipped rather than failing the entire conflict detection run.

## Pre-computed Canonical ASTs

The `canonical_ast` is computed at build time by `build_sidecar.py` and stored in the sidecar database:

```sql
CREATE TABLE claim_algorithm_payload (
    claim_id TEXT PRIMARY KEY,
    body TEXT,
    canonical_ast TEXT,     -- ast_equiv.canonical_dump() output
    variables_json TEXT,
    algorithm_stage TEXT,   -- algorithm sub-phase (e.g. "excitation"); distinct from claim_core.stage
    FOREIGN KEY (claim_id) REFERENCES claim_core(id)
);
```

This enables fast pairwise comparison without re-parsing. The CLI `compare` command reads directly from this table.

## CLI Usage

```bash
# Compare two algorithm claims
pks claim compare claim50 claim51

# With known parameter values for tier 3 partial evaluation
pks claim compare claim50 claim51 -b T0=0.008
```

Output includes: `Tier`, `Equivalent`, `Similarity`, and `Details`.

## Design Notes

- **Equation comparison is a separate subsystem.** Equations use a grammar-driven safe parser plus deterministic SymPy normalization on our own AST (`equation_comparison.py` and `equation_parser.py`); algorithms use AST-based comparison (`ast-equiv`). They share no code.
- **Tier 4 is deliberately conservative.** Similarity alone cannot prove equivalence. The score is useful for triage — high similarity with non-equivalence suggests the algorithms are worth investigating manually.
- **Error tolerance over strictness.** Unparseable algorithm bodies are logged and skipped, not fatal. This keeps the build pipeline resilient against malformed claims from early-stage extraction.

## References

- [ast-equiv](../ast-equiv) — sibling repo implementing the canonicalization and comparison pipeline
