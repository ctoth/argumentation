# Argumentation Package Boundary

Date: 2026-04-18
Status: implemented for Dung, ASPIC+, bipolar, partial AFs, AF revision,
probabilistic / quantitative AF kernels, gradual kernels, generic semantics
dispatch, and generic preference helpers

This document records the boundary between propstore and the external
`argumentation` Python package.

## Boundary In One Sentence

`argumentation` owns finite formal argumentation objects and algorithms;
propstore owns the projection from scientific-claim repositories into those
objects and the policy surfaces that consume the results.

## Package Name

Use `argumentation` for both the distribution and import package.

The name is deliberately literal. The package should remain citation-anchored
instead of accumulating metaphor-driven APIs.

## Extracted Formal Kernel

The package contains the formal kernels:

```text
argumentation.dung
argumentation.aspic
argumentation.bipolar
argumentation.partial_af
argumentation.af_revision
argumentation.probabilistic
argumentation.probabilistic_components
argumentation.dfquad
argumentation.gradual
argumentation.matt_toni
argumentation.equational
argumentation.gradual_principles
argumentation.probabilistic_treedecomp
argumentation.semantics
argumentation.preference
argumentation.solver
```

The core source files are:

- `argumentation/src/argumentation/dung.py`
- `argumentation/src/argumentation/aspic.py`
- `argumentation/src/argumentation/bipolar.py`
- `argumentation/src/argumentation/partial_af.py`
- `argumentation/src/argumentation/af_revision.py`
- `argumentation/src/argumentation/probabilistic.py`
- `argumentation/src/argumentation/probabilistic_components.py`
- `argumentation/src/argumentation/dfquad.py`
- `argumentation/src/argumentation/gradual.py`
- `argumentation/src/argumentation/matt_toni.py`
- `argumentation/src/argumentation/equational.py`
- `argumentation/src/argumentation/gradual_principles.py`
- `argumentation/src/argumentation/probabilistic_treedecomp.py`
- `argumentation/src/argumentation/semantics.py`
- `argumentation/src/argumentation/preference.py`
- `argumentation/src/argumentation/solver.py`

The implementation workstream cut directly to the external package: the
`argumentation` repo owns the kernel modules and kernel tests, propstore depends
on the pinned package, callers import the external package directly, and the old
propstore module paths are deleted. No in-tree compatibility package is part of
the target architecture.

## What Does Not Move

These propstore surfaces stay in propstore:

- `propstore/aspic_bridge/`
- `propstore/claim_graph.py`
- `propstore/structured_projection.py`
- `propstore/defeasibility.py`
- `propstore/argumentation.py`
- `propstore/praf/` adapters, opinion/calibration helpers, provenance
  projection, and store-facing construction
- `propstore/support_revision/` operational support-incision adapters; formal
  AGM and IC-merge kernels stay in the external `belief_set` package
- `propstore/world/`
- `propstore/worldline/`
- `propstore/storage/`
- `propstore/cli/`
- CEL, context, sidecar, source, provenance, and repository modules

The reason is ownership, not importance. These modules know about claims,
stances, stores, sidecars, contexts, provenance, source-local state, worldline
policy, or CLI presentation. That is propstore's domain.

## Extracted Adjacent Helpers

`argumentation.dung_z3` owns the optional Z3-backed Dung backend. Solver-result
wrappers live in `argumentation.solver`; CEL authoring, `ConditionIR`,
`CheckedCondition`, and `ConditionSolver` remain in
`propstore.core.conditions`.

`argumentation.preference` owns the generic helpers:

- strict partial-order closure
- Modgil/Prakken set comparison
- generic attack-to-defeat filtering

`propstore.preference` owns only metadata strength vectors over `ActiveClaim`
and mapping-like claim metadata.

`argumentation.partial_af` owns partial-framework completion enumeration,
completion queries, exact edit-distance merge operators, and `consensual_expand`.

`argumentation.af_revision` owns AF-level revision and accepts formula-like
extension constraints through an argumentation-owned protocol. Propstore
belief-set formulas remain propstore-owned adapters into that protocol.

`argumentation.probabilistic` owns the float-valued probabilistic AF kernel:
deterministic fallback, exact enumeration, Monte Carlo with component
decomposition, and tree-decomposition DP. `argumentation.dfquad` and
`argumentation.gradual` own DF-QuAD / QBAF gradual semantics, while
`argumentation.matt_toni`, `argumentation.equational`, and
`argumentation.gradual_principles` own their named gradual kernels and principle
predicates.
Propstore keeps subjective-logic opinions, calibration, provenance rows, store
projection, and CLI/worldline policy.

`argumentation.semantics` owns generic dispatch over argumentation-owned Dung,
bipolar, and partial-AF dataclasses. `propstore.argumentation` owns backend
policy validation, claim projection, result packaging, and worldline state.

## Target Runtime Shape

External package imports:

```python
from argumentation.dung import ArgumentationFramework, grounded_extension
from argumentation.aspic import Literal, Rule, build_arguments
from argumentation.bipolar import BipolarArgumentationFramework
from argumentation.partial_af import PartialArgumentationFramework
from argumentation.af_revision import ExtensionRevisionState
from argumentation.probabilistic import ProbabilisticAF
from argumentation.dfquad import dfquad_strengths
from argumentation.gradual import WeightedBipolarGraph
from argumentation.semantics import extensions
```

Propstore adapter imports:

```python
from argumentation.aspic import ArgumentationSystem, KnowledgeBase
from argumentation.dung import ArgumentationFramework
from argumentation.partial_af import sum_merge_frameworks
from argumentation.probabilistic import compute_probabilistic_acceptance
```

Forbidden production shape:

```python
# Do not keep compatibility shims at deleted propstore module paths.
from argumentation.dung import *
```

Old production import paths should be deleted, not forwarded.

## Documentation Boundary

The external package README explains formal systems and examples.

Propstore documentation should explain how claim data is translated into those
formal systems:

- `propstore.aspic_bridge` maps active claims, justifications, stances, and
  grounded bundles into ASPIC+ inputs.
- `propstore.claim_graph` maps active claim rows and stances into Dung AFs.
- propstore world/worldline/CLI modules choose backend semantics and present
  results.

## Execution Plan

The full execution plan lives in:

- `plans/argumentation-package-extraction-workstream-2026-04-18.md`

That plan is the control surface for implementation. This document is the
architectural boundary record.
