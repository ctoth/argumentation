# argumentation

A finite, citation-anchored Python library for formal argumentation.

`argumentation` implements the standard objects and algorithms of computational
argumentation theory as a small, dependency-free kernel:

- **Dung** abstract argumentation frameworks and extension semantics
- **ASPIC+** structured argumentation
- **Flat ABA / ABA+** assumption-based argumentation with preference-aware attack reversal
- **ADF** abstract dialectical frameworks with typed acceptance-condition ASTs
- **Cayrol-style bipolar** argumentation frameworks
- **Partial** argumentation frameworks with completion-based reasoning
- **AF revision** under formula and framework constraints
- **Probabilistic** argumentation frameworks (PrAFs) with Monte Carlo,
  exact enumeration, tree-decomposition DP, and DF-QuAD gradual semantics
- **Ranking, weighted, and gradual** quantitative argumentation services
- **Value-based and accrual** helpers for ASPIC+ input filtering and
  same-conclusion support envelopes
- **Generic semantics dispatch** over Dung, bipolar, and partial AF objects
- An optional **Z3-backed** backend for extension enumeration

Every algorithm cites the paper, definition, and (where useful) page that fixes
its behaviour. The pure-Python implementation is the reference; solver backends
must agree with it.

## Install

```powershell
uv add formal-argumentation
```

To enable the Z3-backed Dung backend:

```powershell
uv add "formal-argumentation[z3]"
```

The distribution name on PyPI is `formal-argumentation`; the import name is
`argumentation` (the name `argumentation` on PyPI was already taken by an
unrelated project).

Requires Python 3.11 or later.

## Dung abstract argumentation

An argumentation framework is a set of arguments together with a defeat
relation. Extensions are sets of arguments that survive together under a chosen
semantics.

```python
from argumentation.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
    complete_extensions,
)

framework = ArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({
        ("a", "b"),
        ("b", "a"),
        ("b", "c"),
    }),
)

grounded_extension(framework)      # frozenset()
preferred_extensions(framework)    # [frozenset({"a", "c"}), frozenset({"b"})]
stable_extensions(framework)       # [frozenset({"a", "c"}), frozenset({"b"})]
complete_extensions(framework)     # [frozenset(), frozenset({"a", "c"}), frozenset({"b"})]
```

The framework dataclass tracks `defeats` (the post-preference attack relation
used by Dung's defence) and an optional pre-preference `attacks` relation used
by conflict-freeness, following Modgil & Prakken (2018) Def 14.

`grounded` / `complete` / `preferred` / `stable` semantics are all provided.
`complete`, `preferred`, and `stable` accept a `backend` argument; the default
`"auto"` selects brute-force enumeration for small frameworks (≤12 arguments)
and Z3 above that threshold.

> Dung, P. M. (1995). On the acceptability of arguments and its fundamental
> role in nonmonotonic reasoning, logic programming and *n*-person games.
> *Artificial Intelligence*, 77(2), 321–357.

## ASPIC+ structured argumentation

ASPIC+ builds arguments from a knowledge base and a set of strict and
defeasible rules over a logical language with a contrariness function, then
derives attacks and defeats between those arguments.

```python
from argumentation.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
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
pref = PreferenceConfig(
    rule_order=frozenset(),
    premise_order=frozenset(),
    comparison="elitist",
    link="last",
)

arguments = build_arguments(system, kb)
attacks = compute_attacks(arguments, system)
defeats = compute_defeats(attacks, arguments, system, kb, pref)
```

The module provides:

- `GroundAtom`, `Literal`, `ContrarinessFn`, `Rule`, `KnowledgeBase`,
  `ArgumentationSystem`, `PreferenceConfig`
- `PremiseArg`, `StrictArg`, `DefeasibleArg` and the `Argument` union
- `build_arguments`, `compute_attacks`, `compute_defeats`
- Argument accessors `conc`, `prem`, `sub`, `top_rule`, `def_rules`,
  `last_def_rules`, `prem_p`, `is_firm`, `is_strict`
- `transposition_closure`, `strict_closure`, `is_c_consistent`
- A `CSAF` type packaging the constructed structured AF

> Modgil, S. & Prakken, H. (2018). A general account of argumentation with
> preferences. *Artificial Intelligence*, 248, 51–104.

## Bipolar argumentation

Bipolar frameworks add an explicit support relation alongside defeats. Support
chains induce *derived* defeats (supported and indirect), computed to a
fixpoint, and yield d-, s-, and c-admissibility variants.

```python
from argumentation.bipolar import (
    BipolarArgumentationFramework,
    cayrol_derived_defeats,
    d_preferred_extensions,
    s_preferred_extensions,
    c_preferred_extensions,
    stable_extensions,
)

framework = BipolarArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({("b", "c")}),
    supports=frozenset({("a", "b")}),
)

cayrol_derived_defeats(framework.defeats, framework.supports)  # {("a", "c")}
d_preferred_extensions(framework)
```

> Cayrol, C. & Lagasquie-Schiex, M.-C. (2005). On the acceptability of
> arguments in bipolar argumentation frameworks. In *ECSQARU 2005*.

## Partial argumentation frameworks

A partial AF leaves some attack pairs *uncertain*. Pairs over A × A are
partitioned into `attacks`, `ignorance`, and `non_attacks`; the partition is
checked at construction. Reasoning is by enumerating *completions* — the Dung
AFs obtained by resolving each ignorance pair as attack or non-attack.

```python
from argumentation.partial_af import (
    PartialArgumentationFramework,
    enumerate_completions,
    skeptically_accepted_arguments,
    credulously_accepted_arguments,
    sum_merge_frameworks,
    max_merge_frameworks,
    leximax_merge_frameworks,
)

partial = PartialArgumentationFramework(
    arguments=frozenset({"a", "b"}),
    attacks=frozenset({("a", "b")}),
    ignorance=frozenset({("b", "a")}),
    non_attacks=frozenset({("a", "a"), ("b", "b")}),
)

enumerate_completions(partial)
skeptically_accepted_arguments(partial, semantics="grounded")
credulously_accepted_arguments(partial, semantics="preferred")
```

Multiple sources can be merged into a single AF by minimising edit distance
(Hamming over pair labels) under three aggregation rules: `sum_merge_frameworks`,
`max_merge_frameworks`, and `leximax_merge_frameworks`. `consensual_expand`
lifts a Dung AF onto a wider argument universe by marking out-of-scope pairs as
ignorance.

Completion-based semantics are also available through the generic
`argumentation.semantics` dispatcher.

## AF revision

Add arguments and attacks to an existing framework, or revise an extension
state by a formula or by a target framework, while preserving rationality
postulates.

```python
from argumentation.af_revision import (
    ExtensionRevisionState,
    baumann_2015_kernel_union_expand,
    diller_2015_revise_by_formula,
    diller_2015_revise_by_framework,
    cayrol_2014_classify_grounded_argument_addition,
    AFChangeKind,
)

merged = baumann_2015_kernel_union_expand(base_af, incoming_af)

kind = cayrol_2014_classify_grounded_argument_addition(
    framework=base_af,
    argument="x",
    attacks=frozenset({("x", "a")}),
)
# AFChangeKind.DECISIVE | RESTRICTIVE | QUESTIONING |
# DESTRUCTIVE | EXPANSIVE | CONSERVATIVE | ALTERING
```

> Baumann, R. (2015). Context-free and context-sensitive kernels: update and
> deletion equivalence in abstract argumentation. In *ECAI 2014*.
> Diller, M., Haret, A., Linsbichler, T., Rümmele, S., & Woltran, S. (2015).
> An extension-based approach to belief revision in abstract argumentation.
> Cayrol, C., de Saint-Cyr, F. D., & Lagasquie-Schiex, M.-C. (2014).
> Change in abstract argumentation frameworks: adding an argument.

## Probabilistic argumentation

A probabilistic argumentation framework (PrAF) attaches an existence
probability to each argument and a presence probability to each defeat (and
optionally to each attack and support). Acceptance is then a probability over
*sampled worlds*: the realised Dung framework drawn by sampling each
argument and each edge from its primitive opinion.

```python
from argumentation.dung import ArgumentationFramework
from argumentation.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
)

framework = ArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({("a", "b"), ("b", "c")}),
)

praf = ProbabilisticAF(
    framework=framework,
    p_args={"a": 0.9, "b": 0.7, "c": 1.0},
    p_defeats={("a", "b"): 0.8, ("b", "c"): 1.0},
)

result = compute_probabilistic_acceptance(praf, semantics="grounded")
result.acceptance_probs    # {"a": 0.9, "b": ..., "c": ...}
result.strategy_used       # "exact_enum" | "mc" | "exact_dp" | "deterministic"
```

`compute_probabilistic_acceptance` dispatches across five strategies:

- `deterministic` — fast path when every probability is 0 or 1; collapses
  to standard Dung evaluation (Li et al. 2012, p. 2).
- `exact_enum` — brute-force enumeration over induced Dung AFs; default
  when the framework has at most thirteen arguments (Li et al. 2012, p. 3).
- `mc` — Monte Carlo sampling with Agresti–Coull stopping per Li et al.
  (2012, Algorithm 1), decomposed across connected components per Hunter
  & Thimm (2017, Proposition 18).
- `exact_dp` — an adapted grounded edge-tracking TD backend using
  tree decompositions for defeat-only frameworks. It is exact for the
  supported grounded PrAF route, but not the full Popescu & Wallner I/O/U witness-table DP.
- `dfquad_quad` and `dfquad_baf` — DF-QuAD gradual semantics for
  quantitative bipolar frameworks (Freedman et al. 2025).

Two query kinds are supported. Per-argument acceptance is the default;
exact-set extension probability is opt-in:

```python
result = compute_probabilistic_acceptance(
    praf,
    semantics="preferred",
    query_kind="extension_probability",
    queried_set={"a", "c"},
)
result.extension_probability   # P({a, c} is a preferred extension)
```

Probabilities are plain floats in `[0, 1]`. Calling code that owns richer
uncertainty objects, subjective opinions, or beta posteriors converts them to
probabilities before constructing the kernel object.

`compute_probabilistic_acceptance` also accepts an explicit `strategy=` to
force a backend; `summarize_defeat_relations` exposes exact defeat marginals
as a diagnostic.

> Li, H., Oren, N., & Norman, T. J. (2012). Probabilistic argumentation
> frameworks. In *TAFA 2011*.
> Hunter, A. & Thimm, M. (2017). Probabilistic reasoning with abstract
> argumentation frameworks. *JAIR*, 59, 565–611.
> Popescu, A. & Wallner, J. P. (2024). Tree-decomposition-based dynamic
> programming for probabilistic abstract argumentation.
> Freedman, G., Rago, A., Albini, E., Toni, F., & Cocarascu, O. (2025).
> Argumentative Large Language Models for explainable and contestable
> claim verification.

## Ranking, weighted, gradual, and value-based services

`argumentation.ranking` provides non-binary acceptability rankings for Dung
AFs, including Categoriser scores and iterative Burden numbers:

```python
from argumentation.ranking import categoriser_ranking

ranking = categoriser_ranking(framework)
ranking.ordered_tiers
```

`argumentation.weighted` implements Dunne-style weighted argument systems by
enumerating attack sets whose deleted weight fits an inconsistency budget:

```python
from argumentation.weighted import weighted_grounded_extensions

weighted_grounded_extensions(weighted_framework, budget=1.0)
```

`argumentation.gradual` computes Potyka-style quadratic-energy strengths for
weighted bipolar graphs and exposes revised direct-impact attribution:

```python
from argumentation.gradual import quadratic_energy_strengths, revised_direct_impact

strengths = quadratic_energy_strengths(graph)
impact = revised_direct_impact(graph, influencers=frozenset({"a"}), target="b")
```

`argumentation.value_based` implements Wallner-style value filtering before
ASPIC+ argument construction: subjective knowledge bases add complementary
literals for rejected propositions, and defeasible rules are filtered by body,
head, and rule name.

`argumentation.accrual` exposes Prakken-style weak/strong applicability checks
and accrual envelopes for same-conclusion arguments. It does not yet implement
the full labelling-relative defeat engine.

## Optional Z3 backend

`argumentation.dung_z3` provides SAT-encoded enumeration of complete,
preferred, and stable extensions. It is automatically selected by the `"auto"`
backend on larger frameworks and can be requested explicitly:

```python
preferred_extensions(framework, backend="z3")
```

Z3 results are surfaced through three local result types — `SolverSat`,
`SolverUnsat`, `SolverUnknown` — with a default 30-second timeout. A two-valued
caller that cannot represent unknown receives `Z3UnknownError`. Install the
`z3` extra to enable the backend.

## Generic semantics dispatch

`argumentation.semantics` provides a small set-returning dispatcher for callers
that work across framework families:

```python
from argumentation.semantics import accepted_arguments, extensions

extensions(framework, semantics="grounded")
accepted_arguments(framework, semantics="preferred", mode="credulous")
accepted_arguments(partial_framework, semantics="stable", mode="skeptical")
```

Supported inputs are argumentation-owned Dung, bipolar, and partial-AF
dataclasses. The dispatcher does not know about application records, storage
rows, projection policy, or command-line rendering.

## Preferences

`argumentation.preference` provides preference primitives shared by ASPIC+ and
revision code:

- `strict_partial_order_closure` — transitive closure with cycle and
  reflexivity rejection.
- `strictly_weaker` — elitist and democratic comparisons over numeric strength
  vectors (Modgil & Prakken Def 19).
- `defeat_holds` — generic attack-to-defeat resolution for undercutting,
  rebutting, undermining, and supersedes attacks.

## Design

- Pure-Python algorithms are the reference implementation. Optional solver
  backends must produce the same formal results on the same finite framework,
  except where the solver explicitly reports unknown.
- Frameworks, rules, arguments, and extensions are immutable frozen
  dataclasses over frozensets. Equality is structural.
- Conflict-freeness is checked against the pre-preference attack relation;
  defence is checked against defeats. Both are tracked separately on
  `ArgumentationFramework`.
- Algorithms cite their formal source in module and function docstrings.

## Non-goals

`argumentation` does not own application provenance, source calibration,
subjective-logic opinion calculi, persistent storage, repository workflow, or
CLI presentation. Callers should translate those concerns into finite formal
objects before invoking this package.

## Development

```powershell
uv sync
uv run pyright src
uv run pytest -vv
```

Tests are tagged `unit`, `property`, and `differential`. Property tests use
Hypothesis. Differential tests cross-check the brute-force and Z3 backends on
the same frameworks.
