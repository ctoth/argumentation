# Dedup B8 report — merge the two Int ranked-closure Z3 encoders

Branch: `refactor/dedup`
File: `src/argumentation/structured/aba/aba_sat.py` (pure LF, confirmed below)

## STEP 1 — identity proof (BEFORE merging)

The two pre-merge encoders, quoted verbatim from disk.

### `_add_ranked_closure_constraints` (pre-merge)

```python
def _add_ranked_closure_constraints(z3, solver, framework, variables):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    derived = {
        literal: z3.Bool(f"der_{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.Int(f"rank_{_literal_key(literal)}")
        for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)

    for literal in literals:
        solver.add(ranks[literal] >= 0, ranks[literal] <= rank_bound)

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == 0))

    for rule in sorted(framework.rules, key=repr):
        antecedents = tuple(rule.antecedents)
        if not antecedents:
            solver.add(derived[rule.consequent])
        else:
            solver.add(
                z3.Implies(
                    z3.And(*(derived[antecedent] for antecedent in antecedents)),
                    derived[rule.consequent],
                )
            )

    for literal in literals:
        if literal in framework.assumptions:
            continue
        support_terms = []
        for rule in rules_by_consequent[literal]:
            antecedents = tuple(rule.antecedents)
            if not antecedents:
                support_terms.append(z3.BoolVal(True))
                continue
            support_terms.append(
                z3.And(
                    *(
                        z3.And(
                            derived[antecedent],
                            ranks[antecedent] < ranks[literal],
                        )
                        for antecedent in antecedents
                    )
                )
            )
        solver.add(
            z3.Implies(
                derived[literal],
                z3.Or(*support_terms) if support_terms else z3.BoolVal(False),
            )
        )
    return derived
```

### `_prefsat_add_closure_constraints` (pre-merge)

```python
def _prefsat_add_closure_constraints(z3, solver, framework, variables, *, prefix: str):
    literals = tuple(sorted(framework.language, key=repr))
    rank_bound = len(literals)
    derived = {
        literal: z3.Bool(f"{prefix}_derived_{_literal_key(literal)}")
        for literal in literals
    }
    ranks = {
        literal: z3.Int(f"{prefix}_rank_{_literal_key(literal)}")
        for literal in literals
    }
    rules_by_consequent = _rules_by_consequent(framework, literals)
    clause_count = 0

    for literal in literals:
        solver.add(ranks[literal] >= 0, ranks[literal] <= rank_bound)
        clause_count += 1

    for assumption in sorted(framework.assumptions, key=repr):
        solver.add(derived[assumption] == variables[assumption])
        solver.add(z3.Implies(variables[assumption], ranks[assumption] == 0))
        clause_count += 2

    for rule in sorted(framework.rules, key=repr):
        antecedents = tuple(rule.antecedents)
        if not antecedents:
            solver.add(derived[rule.consequent])
        else:
            solver.add(
                z3.Implies(
                    z3.And(*(derived[antecedent] for antecedent in antecedents)),
                    derived[rule.consequent],
                )
            )
        clause_count += 1

    for literal in literals:
        if literal in framework.assumptions:
            continue
        support_terms = []
        for rule in rules_by_consequent[literal]:
            antecedents = tuple(rule.antecedents)
            if not antecedents:
                support_terms.append(z3.BoolVal(True))
                continue
            support_terms.append(
                z3.And(
                    *(
                        z3.And(
                            derived[antecedent],
                            ranks[antecedent] < ranks[literal],
                        )
                        for antecedent in antecedents
                    )
                )
            )
        solver.add(
            z3.Implies(
                derived[literal],
                z3.Or(*support_terms) if support_terms else z3.BoolVal(False),
            )
        )
        clause_count += 1
    return derived, clause_count
```

### Exact difference list (the ONLY differences)

1. **Signature**: prefsat adds keyword-only `*, prefix: str`; plain has none.
2. **`derived` Bool name template**: `f"der_{key}"` vs `f"{prefix}_derived_{key}"`.
3. **`ranks` Int name template**: `f"rank_{key}"` vs `f"{prefix}_rank_{key}"`.
4. **Clause tally**: prefsat keeps `clause_count` (`+1` per rank-bound literal,
   `+2` per assumption, `+1` per rule, `+1` per non-assumption support clause)
   and returns `(derived, clause_count)`; plain returns bare `derived`.

Every `solver.add(...)` call — rank bounds (`>=0`, `<=rank_bound`), assumption
equality + rank-0 implication, rule implications (empty vs non-empty
antecedents), and the support / `ranks[ant] < ranks[lit]` ordering clauses — is
**byte-identical in structure** across the two functions. There is **no
semantic divergence**: same variables created (modulo name prefix), same
constraints added in the same order, same `derived` map. Identity confirmed —
merge proceeds.

### Callers and what each relies on

- `_add_ranked_closure_constraints`:
  - `aba_sat.py:1728` (`self.derived = ...`) — uses returned `derived` map; indexes it later (`self.derived[...]`). Relies on bare-dict return.
  - `aba_sat.py:1926` (`derived = ...`) — uses returned `derived` map; indexes it. Bare-dict return.
  - `tests/structured/aba/test_aba.py:274` (parity test) — uses returned `derived` to read the model. Var names only need to be unique within one solver.
- `_prefsat_add_closure_constraints`:
  - `aba_sat.py:1383` (inside `_add_closure_constraints`) — unpacks `derived, clause_count`, adds `clause_count` to `self.telemetry["prefsat_complete_clauses"]`, returns `derived`. Relies on the tuple return + tally + the `{prefix}_...` var names being distinct per `prefix`.

No caller depends on the literal text of the var-name prefix beyond
within-solver uniqueness; the tally is consumed only by prefsat telemetry.

## STEP 2 — merge

One shared body `_emit_ranked_closure_constraints(...)` now holds the
constraint emission, parametrized by `derived_prefix` and `rank_prefix`, and
**always** returns `(derived, clause_count)` (concrete tuple — keeps pyright
return types unambiguous). The two public encoders are thin wrappers that
reconstruct their exact original prefixes and return contracts:

```python
def _add_ranked_closure_constraints(z3, solver, framework, variables):
    derived, _clause_count = _emit_ranked_closure_constraints(
        z3, solver, framework, variables,
        derived_prefix="der_", rank_prefix="rank_",
    )
    return derived            # bare dict, exactly as before


def _prefsat_add_closure_constraints(z3, solver, framework, variables, *, prefix: str):
    return _emit_ranked_closure_constraints(
        z3, solver, framework, variables,
        derived_prefix=f"{prefix}_derived_", rank_prefix=f"{prefix}_rank_",
    )                          # (derived, clause_count) tuple, exactly as before
```

- Plain wrapper passes `derived_prefix="der_"`, `rank_prefix="rank_"` →
  identical Bool names `der_{key}` and Int names `rank_{key}`; discards the
  tally and returns bare `derived` (its original contract).
- prefsat wrapper passes `derived_prefix=f"{prefix}_derived_"`,
  `rank_prefix=f"{prefix}_rank_"` → identical names `{prefix}_derived_{key}` /
  `{prefix}_rank_{key}`; returns the `(derived, clause_count)` tuple, so the
  telemetry tally at `aba_sat.py:1390` is unchanged.

The clause count is computed unconditionally in the shared body; that is free
of side effects and only observed by the prefsat path that keeps it. The
emitted Z3 constraints for any `(framework, variables, prefix)` are identical
to before.

### Note: pyright interaction caught and fixed before commit

An initial version used a `tally: bool` flag with a `dict | tuple` union
return. That made `_add_ranked_closure_constraints` return a union, so the two
`self.derived[...]` / `derived[...]` call sites failed pyright (11 errors,
`Literal not assignable to slice`). The base file had 0 pyright errors. The
final form (single concrete tuple return from the shared body, wrapper unpacks)
restores 0 errors. Behavior is unchanged — only the internal return shape of
the private helper changed, not either public encoder's contract.

## STEP 3 — verification (all via `uv run`)

### Parity test

```
$ uv run python -m pytest tests/structured/aba/test_aba.py::test_ranked_closure_matches_native_closure -q
.                                                                        [100%]
1 passed in 0.75s
```

### Full aba suite (covers prefsat contract suites)

```
$ uv run python -m pytest tests/structured/aba -q
........................................................................ [ 97%]
....................................                                     [100%]
1332 passed in 219.69s (0:03:39)
```

(prefsat coverage included: `test_aba_decomposed_prefsat_contract.py`,
`test_aba_native_cnf_prefsat.py`, `test_aba_real_prefsat_contract.py`,
`test_aba_route_properties.py`, `test_prefsat_closure_equivalence_probe.py`.)

### pyright

```
$ uv run python -m pyright src/argumentation/structured/aba/aba_sat.py
0 errors, 0 warnings, 0 informations
```

(Base HEAD version also reports `0 errors, 0 warnings, 0 informations` — parity maintained.)

### Line endings + numstat (no EOL churn, proportional change)

```
$ python -c "d=open('.../aba_sat.py','rb').read(); print('CRLF:',d.count(b'\r\n'),'LF:',d.count(b'\n'))"
CRLF: 0 LF: 2427

$ git diff --numstat -- src/argumentation/structured/aba/aba_sat.py
43      64      src/argumentation/structured/aba/aba_sat.py
```

aba_sat.py stays **pure LF (0 CRLF)**. +43/-64 (net −21) on a ~2400-line file —
proportional to merging two ~58-line bodies into one shared body + two small
wrappers. No whole-file churn.

## Commit

On `refactor/dedup`. The commit bundles `aba_sat.py` (the merge) and this
report. Run `git log -1` for the exact hash (it changed as this hash line was
finalized via `--amend`).

## Out of scope — noticed

- The two encoders use *different* name templates (`der_` / `rank_` vs
  `{prefix}_derived_` / `{prefix}_rank_`). Harmonizing them to a single scheme
  would be a behavior change (different Z3 var names) and was intentionally NOT
  done — prefixes preserved exactly.
- `_emit_ranked_closure_constraints`, like the originals, has untyped `z3`/
  `solver`/`framework`/`variables` params (z3 is an untyped dependency). Adding
  type stubs is a broader effort, out of scope here.
