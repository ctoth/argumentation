# Dedup B2 report: merge the two identical `_is_acyclic` into one core helper

Behavior-preserving refactor. Branch `refactor/dedup`. All commands run via `uv run`.

## 1. Confirmation: the two were identical-modulo-incidental

Before the change, both helpers ran the **same** iterative post-order DFS
(explicit `(node, entered)` stack, grey/black coloring, grey-on-grey = cycle,
return `True` iff acyclic). They differed only INCIDENTALLY, and neither
incidental difference changes the returned boolean:

- adjacency container: `set` vs `list` — a duplicate edge cannot create or
  destroy a cycle, so dedup vs not is irrelevant to acyclicity.
- root iteration order: `sorted(framework.arguments)` vs raw
  `framework.arguments` — DFS reachability and cycle existence are
  order-independent.

### `core/labelling.py` (before) — `set` adjacency, `sorted` roots

```python
def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing.setdefault(attacker, set()).add(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    for root in sorted(framework.arguments):
        if root in visited:
            continue
        stack: list[tuple[str, bool]] = [(root, False)]
        while stack:
            argument, entered = stack.pop()
            if entered:
                visiting.discard(argument)
                visited.add(argument)
                continue
            if argument in visited:
                continue
            if argument in visiting:
                return False
            visiting.add(argument)
            stack.append((argument, True))
            for target in outgoing.get(argument, set()):
                if target in visiting:
                    return False
                if target not in visited:
                    stack.append((target, False))

    return True
```

### `solving/af_sat.py` (before) — `list` adjacency, unsorted roots

```python
def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, list[str]] = {argument: [] for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing[attacker].append(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    for root in framework.arguments:
        if root in visited:
            continue
        stack: list[tuple[str, bool]] = [(root, False)]
        while stack:
            argument, entered = stack.pop()
            if entered:
                visiting.discard(argument)
                visited.add(argument)
                continue
            if argument in visited:
                continue
            if argument in visiting:
                return False
            visiting.add(argument)
            stack.append((argument, True))
            for target in outgoing.get(argument, []):
                if target in visiting:
                    return False
                if target not in visited:
                    stack.append((target, False))

    return True
```

Apart from the `set` vs `list` literal and the `sorted(...)` wrapper on the
root loop, the two bodies are byte-for-byte the same. **No behavioral
divergence** — proceeded with the merge.

## 2. New shared helper

Added to `src/argumentation/core/finite.py` (lowest `core` layer, already the
home of the iterative `strongly_connected_components`), in the same generic
style: generic over node type `T`, takes a `Mapping[T, Iterable[T]]` graph plus
an optional `key`, and uses the module's existing `_ordered_items` for
deterministic sorted iteration of roots and successors. The traversal is the
existing iterative explicit-stack DFS — **not** re-derived via SCC.

Signature:

```python
def is_acyclic(
    graph: Mapping[T, Iterable[T]],
    *,
    key: Callable[[T], Any] | None = None,
) -> bool:
```

The traversal now exists in exactly one place.

## 3. Call-site updates

Both former bodies are deleted; each `_is_acyclic(framework)` is now a thin
module-local adapter that builds the successor mapping and delegates:

`src/argumentation/core/labelling.py` (call site `complete_labellings`, line 198):

```python
def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, set[str]] = {argument: set() for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing.setdefault(attacker, set()).add(target)
    return is_acyclic(outgoing)
```

`src/argumentation/solving/af_sat.py` (call site at line 788, preferred-skeptical
shortcut path):

```python
def _is_acyclic(framework: ArgumentationFramework) -> bool:
    outgoing: dict[str, list[str]] = {argument: [] for argument in framework.arguments}
    for attacker, target in framework.defeats:
        outgoing[attacker].append(target)
    return is_acyclic(outgoing)
```

Both files import `is_acyclic` from `argumentation.core.finite` (labelling.py
extended its existing `core.finite` import; af_sat.py added a new import line).

## 4. Test update

`tests/solving/test_is_acyclic_recursion.py` previously parametrized BOTH copies
(`af_sat`, `labelling`). It now imports the single shared
`argumentation.core.finite.is_acyclic`, wraps it in a small framework-input
adapter, and parametrizes that one helper (id `finite`). Every assertion is
preserved unchanged: 3000-node chain -> `True` (no `RecursionError`);
small cycle / self-loop / 3000-node loop-back -> `False`; small DAG / empty /
single argument -> `True`.

## Pasted command output

### `uv run python -m pytest tests/solving/test_is_acyclic_recursion.py -q`

```
.......                                                                  [100%]
7 passed in 0.40s
```

### `uv run python -m pytest tests/core tests/solving -q` (tail)

```
........................................................................ [ 91%]
........................................................................ [ 98%]
...............                                                          [100%]
1021 passed, 2 skipped in 19.85s
```

(The 2 skips are pre-existing, unrelated to this change.)

### `uv run python -m pyright src/argumentation/core/finite.py src/argumentation/core/labelling.py src/argumentation/solving/af_sat.py tests/solving/test_is_acyclic_recursion.py`

```
0 errors, 0 warnings, 0 informations
```

(A pyright self-update notice about v1.1.408 -> v1.1.410 was printed to stderr;
not a diagnostic.)

## Commit

`0924752` on `refactor/dedup`.

## Out of scope — noticed

- The two adapter `_is_acyclic` wrappers still differ incidentally (`set` vs
  `list` adjacency). This is harmless and was left as-is to keep the change a
  minimal behavior-preserving move; a follow-up could collapse them to one
  adapter or build the mapping at the call site, but that touches the call-site
  contract and was out of scope for B2.
- `is_acyclic` could be reused by other modules that currently roll their own
  cycle checks; not surveyed here.
