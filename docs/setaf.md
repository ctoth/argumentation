# SETAF Semantics and I/O

`argumentation.setaf` models finite SETAFs (argumentation frameworks with
collective attacks). The dataclass `SETAF(arguments, attacks)` is frozen;
each collective attack is a `CollectiveAttack = (frozenset[str], str)` with
nonempty tail. The constructor coerces tails to `frozenset` and arguments to
`str`, and raises `ValueError` on empty tails or attacks referencing
undeclared arguments.

## Core definitions

- A set `S` attacks argument `a` iff there is an attack `(T, a)` with
  `T ⊆ S`. (`attacks_argument(framework, S, a)`)
- `S` is conflict-free iff no active attack targets an argument in `S`.
  (`conflict_free(framework, S)`)
- `S` defends `a` iff, for every attacking tail `T` that attacks `a`, `S`
  attacks at least one member of `T`. (`defends(framework, S, a)`)
- `admissible(framework, S)` is conflict-free + defends every member.
- `characteristic_fn(framework, S)` returns the set of arguments defended by
  `S`.
- `range_of(framework, S)` returns `S ∪ {arguments attacked by S}`.

`conflict_free` and `admissible` raise `ValueError` if any candidate
argument is not in the framework.

## Implemented semantics

| Function | Definition |
|---|---|
| `complete_extensions` | admissible fixed points of the characteristic function |
| `grounded_extension` | least fixed point of the characteristic function |
| `preferred_extensions` | inclusion-maximal admissible sets |
| `stable_extensions` | conflict-free sets whose range is all arguments |
| `semi_stable_extensions` | range-maximal complete extensions |
| `stage_extensions` | range-maximal conflict-free sets |

```python
from argumentation.setaf import (
    SETAF, complete_extensions, grounded_extension, preferred_extensions,
    stable_extensions, semi_stable_extensions, stage_extensions,
)

framework = SETAF(
    arguments=frozenset({"a", "b", "c"}),
    attacks=frozenset({(frozenset({"a", "b"}), "c")}),
)
preferred_extensions(framework)
```

`solver.solve_setaf_extensions` provides the typed solver-result wrapper for
the same enumeration.

## I/O formats

`argumentation.setaf_io` supports the ASPARTIX SETAF fact format using
`arg/1`, `att/2`, and `mem/2`. `att(Name, Target)` gives the head and
`mem(Name, Argument)` facts give the nonempty tail. The parser skips lines
beginning with `%` and rejects missing terminating dots, `mem` referencing
unknown attack ids, and empty tails. The writer is deterministic — arguments
sorted, attacks sorted by `(sorted_tail, head)`, attack names emitted as
`r{index}`.

```python
from argumentation.setaf_io import parse_aspartix_setaf, write_aspartix_setaf

framework = parse_aspartix_setaf("""
arg(a).
arg(b).
arg(c).
att(r1,c).
mem(r1,a).
mem(r1,b).
""")
text = write_aspartix_setaf(framework)
```

`parse_compact_setaf` / `write_compact_setaf` are package-local helpers for a
compact `p setaf` format with `#` line comments. The compact format is not an
ICCMA SETAF input format — the ICCMA 2023 rules document AF and ABA tracks
only.

## Splitting (non-goal)

The current surface is core SETAF semantics plus SETAF I/O. It does not
implement SETAF splitting algorithms, and callers should not infer splitting
support from the core surface.

## References

The semantics implementations follow the standard SETAF formulations of
Nielsen & Parsons (2007) and the conflict-free / admissibility / range
formulations as adapted in the ICCMA-aligned literature; tests are pinned to
"Definition 1/2/3" of the SETAF reference paper and the
`test_definition_*_*` cases in `tests/test_setaf.py` are the executable
specification.
