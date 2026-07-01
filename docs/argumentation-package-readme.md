# Argumentation Package README Draft

This is the propstore-side historical README draft from the first
argumentation extraction workstream. The live package README is maintained in
the sibling `argumentation` repository.

`argumentation` is a small Python package for finite formal argumentation
systems.

The package now provides citation-anchored implementations of:

- Dung abstract argumentation frameworks
- ASPIC+ structured argumentation
- Cayrol-style bipolar argumentation frameworks
- partial argumentation frameworks
- AF-level revision
- probabilistic / quantitative AF kernels
- generic semantics dispatch

It does not know about propstore claims, stances, repositories, sidecars,
contexts, provenance, source promotion, worldlines, or CLI policy.

## Install

Install from Git:

```powershell
uv add "argumentation @ git+https://github.com/ctoth/argumentation@<commit>"
```

## Dung Abstract Argumentation

```python
from argumentation.dung import ArgumentationFramework, grounded_extension

framework = ArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({
        ("a", "b"),
        ("b", "a"),
        ("b", "c"),
    }),
)

accepted = grounded_extension(framework)
```

The Dung module computes:

- grounded extensions
- complete extensions
- preferred extensions
- stable extensions
- conflict-free and admissibility predicates

## ASPIC+ Structured Argumentation

```python
from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    Rule,
    build_arguments,
    compute_attacks,
    compute_defeats,
)

p = Literal(GroundAtom("p"))
q = Literal(GroundAtom("q"))

system = ArgumentationSystem(
    language=frozenset({p, p.contrary, q, q.contrary}),
    contrariness=ContrarinessFn(
        contradictories=frozenset({(p, p.contrary), (q, q.contrary)}),
    ),
    strict_rules=frozenset(),
    defeasible_rules=frozenset({
        Rule(antecedents=(p,), consequent=q, kind="defeasible", name="r1"),
    }),
)

kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())
arguments = build_arguments(system, kb)
attacks = compute_attacks(arguments, system)
```

The ASPIC+ module implements the formal argumentation kernel only. Domain
translation belongs in caller packages.

## Bipolar Argumentation

```python
from argumentation.bipolar import (
    BipolarArgumentationFramework,
    cayrol_derived_defeats,
    d_preferred_extensions,
)

framework = BipolarArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({("b", "c")}),
    supports=frozenset({("a", "b")}),
)

derived = cayrol_derived_defeats(framework.defeats, framework.supports)
extensions = d_preferred_extensions(framework)
```

## Non-Goals

`argumentation` does not provide:

- a claim store
- a scientific knowledge model
- YAML or repository loading
- source promotion
- context/CEL reasoning
- sidecar SQLite compilation
- worldline materialization
- CLI commands
- propstore compatibility import shims

Those concerns belong in adapter packages such as propstore.

## Optional Backends

The base package does not require Z3.

`argumentation.dung_z3` provides solver-backed extension enumeration using
local solver-result and timeout handling. Install the `z3` extra or use the
development environment to run those tests.

## Citation Discipline

Implementations should cite the formal source they implement in module
docstrings and tests.

Core references:

- Dung, P. M. 1995. On the acceptability of arguments and its fundamental role
  in nonmonotonic reasoning, logic programming and n-person games.
- Modgil, S. and Prakken, H. 2018. A general account of argumentation with
  preferences.
- Cayrol, C. and Lagasquie-Schiex, M.-C. 2005. On the acceptability of
  arguments in bipolar argumentation frameworks.

## Relationship To Propstore

Propstore uses `argumentation` as a formal kernel.

Propstore-owned adapters translate active claims, justifications, stances,
grounded rule bundles, and source metadata into formal objects, then use
`argumentation` to compute attacks, defeats, and extensions.

That split keeps the formal algorithms reusable and keeps scientific-claim
policy in propstore.
