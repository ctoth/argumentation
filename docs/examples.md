# Examples

These examples use only the base package unless a backend is named
explicitly. They are meant to show the current layered import paths and the
shape of the returned objects.

## Dung Extensions

```python
from argumentation.core.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)

af = ArgumentationFramework(
    arguments=frozenset({"a", "b", "c", "d"}),
    defeats=frozenset({("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")}),
)

assert grounded_extension(af) == frozenset()
assert preferred_extensions(af) == [
    frozenset({"a", "c"}),
    frozenset({"b", "d"}),
]
assert stable_extensions(af) == preferred_extensions(af)
```

## Solver Result Types

Solver entry points return typed results. ICCMA `SE` tasks produce one witness,
not full enumeration, so enumeration requests reject `backend="iccma"` before
any subprocess call.

```python
from argumentation.core.dung import ArgumentationFramework
from argumentation.core.solver_results import SolverUnavailable
from argumentation.solving.solver import ICCMAConfig, solve_dung_extensions

af = ArgumentationFramework(
    arguments=frozenset({"1", "2", "3"}),
    defeats=frozenset({("1", "2"), ("2", "1")}),
)

result = solve_dung_extensions(
    af,
    semantics="preferred",
    backend="iccma",
    iccma=ICCMAConfig(binary="external-solver"),
)

assert isinstance(result, SolverUnavailable)
assert result.reason == "ICCMA AF SE tasks return one extension witness, not enumeration"
```

Use `solve_dung_single_extension(..., backend="iccma", iccma=ICCMAConfig(...))`
when one external ICCMA witness is the intended contract.

## Flat ABA

Flat ABA uses ASPIC literals and rules, with assumptions mapped to their
contraries. Non-flat ABA is intentionally rejected by `ABAFramework`.

```python
from argumentation.structured.aba.aba import ABAFramework, preferred_extensions
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


alpha = lit("alpha")
beta = lit("beta")
leave = lit("leave")
stay = lit("stay")

framework = ABAFramework(
    language=frozenset({alpha, beta, leave, stay}),
    rules=frozenset({
        Rule((alpha,), leave, "strict"),
        Rule((beta,), stay, "strict"),
    }),
    assumptions=frozenset({alpha, beta}),
    contrary={alpha: stay, beta: leave},
)

assert preferred_extensions(framework) == (
    frozenset({alpha}),
    frozenset({beta}),
)
```

## Probabilistic AFs

Probabilistic AFs attach existence probabilities to arguments and relation
probabilities to defeats. Exact extension-probability queries are explicit.

```python
from argumentation.core.dung import ArgumentationFramework
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
)

af = ArgumentationFramework(
    arguments=frozenset({"a", "b"}),
    defeats=frozenset({("a", "b")}),
)
praf = ProbabilisticAF(
    framework=af,
    p_args={"a": 1.0, "b": 1.0},
    p_defeats={("a", "b"): 0.5},
)

result = compute_probabilistic_acceptance(
    praf,
    semantics="grounded",
    strategy="exact_enum",
    query_kind="extension_probability",
    queried_set={"a"},
)

assert result.extension_probability is not None
assert abs(result.extension_probability - 0.5) < 1e-12
```

## SETAF Collective Attacks

SETAF attacks have a nonempty tail. A collective attack fires only when every
tail argument is present in the candidate set.

```python
from argumentation.frameworks.setaf import SETAF, conflict_free

framework = SETAF(
    arguments=frozenset({"a", "b", "c"}),
    attacks=frozenset({(frozenset({"a", "b"}), "c")}),
)

assert conflict_free(framework, frozenset({"a", "c"})) is True
assert conflict_free(framework, frozenset({"a", "b", "c"})) is False
```

## Next Steps

- Use [`architecture.md`](architecture.md) when choosing import paths.
- Use [`backends.md`](backends.md) when selecting solver backends.
- Use [`performance-research.md`](performance-research.md) before solver
  optimization or benchmark work.
