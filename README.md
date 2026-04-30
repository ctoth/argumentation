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
- Optional **Z3-backed epistemic linear-constraint** helpers

Every algorithm cites the paper, definition, and (where useful) page that fixes
its behaviour. The pure-Python implementation is the reference for package
algorithms and adapter checks.

## Install

```powershell
uv add formal-argumentation
```

To enable Z3-backed epistemic linear-constraint checks:

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
Dung extension enumeration is implemented through the package's labelling and
set-enumeration code paths. The old `argumentation.dung_z3` module and Dung
Z3 backend name have been removed.

Beyond the four core semantics, `argumentation.dung` also provides
`naive_extensions`, `semi_stable_extensions` (Caminada 2011),
`stage_extensions`, `cf2_extensions` (Gaggl & Woltran 2013),
`stage2_extensions`, `eager_extension`, `ideal_extension` (Dung, Mancarella &
Toni 2007), and prudent-semantics helpers. These are finite in-package
algorithms, not wrappers around an external solver.

```python
from argumentation.dung import (
    semi_stable_extensions,
    stage_extensions,
    cf2_extensions,
    ideal_extension,
)
```

### Three-valued labellings

`argumentation.labelling` exposes the standard IN / OUT / UNDEC labelling and
provides a bridge from extensions to labellings, used by accrual and other
quantitative services.

```python
from argumentation.labelling import Label, Labelling

labelling = Labelling.from_extension(framework, frozenset({"a", "c"}))
labelling.in_arguments         # frozenset({"a", "c"})
labelling.out_arguments        # arguments defeated by an in argument
labelling.undecided_arguments  # everything else
labelling.range                # in ∪ out
```

> Dung, P. M. (1995). On the acceptability of arguments and its fundamental
> role in nonmonotonic reasoning, logic programming and *n*-person games.
> *Artificial Intelligence*, 77(2), 321–357.
> Caminada, M. (2011). Semi-stable semantics. In *COMMA 2006*.
> Gaggl, S. A. & Woltran, S. (2013). The cf2 argumentation semantics revisited.
> *Journal of Logic and Computation*, 23(5), 925–949.
> Dung, P. M., Mancarella, P. & Toni, F. (2007). Computing ideal sceptical
> argumentation. *Artificial Intelligence*, 171(10–15), 642–674.

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

## ASPIC+ encodings and incomplete reasoning

The `argumentation.aspic_encoding` module encodes ASPIC+ theories into a
deterministic ASP-style fact vocabulary and provides a typed grounded-query
surface that can be backed by either the materialised reference projection or
an optional registered backend.

```python
from argumentation.aspic_encoding import (
    encode_aspic_theory,
    solve_aspic_grounded,
    solve_aspic_with_backend,
)

encoding = encode_aspic_theory(system, kb, pref)
encoding.facts        # tuple of axiom/premise/s_head/d_head/contrary/preferred facts
encoding.signature    # SHA-256 over the sorted fact tuple

result = solve_aspic_grounded(system, kb, pref)
result.accepted_argument_ids
result.accepted_conclusions
result.backend        # "materialized_reference"
```

`solve_aspic_with_backend` dispatches to a named backend; an unregistered
backend returns a typed `ASPICQueryResult` with `status="unavailable_backend"`
rather than raising. The fact vocabulary follows Lehtonen, Niskanen & Järvisalo
2024.

`argumentation.aspic_incomplete` reasons over ASPIC+ theories with optional
ordinary premises. `evaluate_incomplete_grounded` enumerates all completions of
the unknown premises and classifies a query literal as `stable`, `relevant`,
`unknown`, or `unsupported`.

```python
from argumentation.aspic_incomplete import (
    PartialASPICTheory,
    evaluate_incomplete_grounded,
)

theory = PartialASPICTheory(
    system=system, kb=kb, pref=pref,
    unknown_premises=frozenset({p, q}),
)
outcome = evaluate_incomplete_grounded(theory, query=p)
outcome.status                  # "stable" | "relevant" | "unknown" | "unsupported"
outcome.accepting_completions
outcome.completion_count
```

> Lehtonen, T., Niskanen, A., & Järvisalo, M. (2024). Reasoning over ASPIC+
> in answer set programming. *KR 2024*.
> Odekerken, D., Borg, A. & Bex, F. (2023). Justification, stability and
> relevance for case-based reasoning with incomplete focus cases.

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
result.strategy_used       # "deterministic" | "exact_enum" | "mc" | ...
```

`compute_probabilistic_acceptance` dispatches across six strategies:

- `deterministic` — fast path when every probability is 0 or 1; collapses
  to standard Dung evaluation (Li et al. 2012, p. 2).
- `exact_enum` — brute-force enumeration over induced Dung AFs; default
  when the framework has at most thirteen arguments (Li et al. 2012, p. 3).
- `mc` — Monte Carlo sampling with Agresti–Coull stopping per Li et al.
  (2012, Algorithm 1), decomposed across connected components per Hunter
  & Thimm (2017, Proposition 18).
- `exact_dp` — an adapted grounded edge-tracking tree-decomposition backend
  for credulous grounded acceptance on defeat-only worlds. It currently tracks
  full edge sets and forgotten arguments in table keys, so the asymptotic
  complexity is not better than brute-force enumeration; it is effective in
  practice for primal-graph treewidth ≤ ~15. This is *not* the full
  Popescu & Wallner I/O/U witness-table DP.
- `paper_td` — the paper-faithful Popescu & Wallner (2024) Algorithm 1 for
  exact extension-probability queries. Opt-in only (`strategy="paper_td"`,
  `query_kind="extension_probability"`); the auto-router does not select it.
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
weighted bipolar graphs, exposes revised direct-impact attribution, and
computes exact Shapley-style per-attack impact scores:

```python
from argumentation.gradual import (
    quadratic_energy_strengths,
    revised_direct_impact,
    shapley_attack_impacts,
)

strengths = quadratic_energy_strengths(graph)
impact = revised_direct_impact(graph, influencers=frozenset({"a"}), target="b")
shapley = shapley_attack_impacts(graph, target="b")
shapley.attack_impacts   # exact Shapley value per direct attack on "b"
```

`shapley_attack_impacts` enumerates all coalitions of the other direct attacks
on the target and averages their marginal contribution to the target's
quadratic-energy strength (Al Anaissy et al. 2024, Definition 13).

`argumentation.subjective_aspic` implements Wallner-style value filtering before
ASPIC+ argument construction: subjective knowledge bases add complementary
literals for rejected propositions, and defeasible rules are filtered by body,
head, and rule name.

`argumentation.vaf` implements Bench-Capon value-based argumentation frameworks:
audience-specific defeat removes attacks whose target value is preferred to the
attacker value, and objective/subjective acceptance quantify over audience
orders and preferred extensions.

`argumentation.practical_reasoning` implements the Atkinson and Bench-Capon
AATS grounding for AS1-style practical arguments and the CQ5, CQ6, and CQ11
choice-stage objections.

`argumentation.ranking_axioms` exposes executable checks for ranking preorder,
void-precedence, and cardinality-precedence obligations over `RankingResult`.

`argumentation.accrual` exposes Prakken-style weak/strong applicability checks
and accrual envelopes for same-conclusion arguments. It does not yet implement
the full labelling-relative defeat engine.

## Additional SOTA workstream surfaces

`argumentation.aba` implements flat ABA and ABA+ over ASPIC literals, including
complete, preferred, stable, naive, grounded, well-founded, and ideal
assumption-extension functions plus a Dung projection.

`argumentation.adf` implements abstract dialectical frameworks with typed
acceptance-condition ASTs, three-valued interpretations, grounded/admissible/
complete/model/preferred/stable model enumeration, structural link
classification, JSON/formula I/O helpers, and Dung bridges.

`argumentation.setaf` implements argumentation frameworks with collective
attacks, including conflict-free, admissible, complete, preferred, grounded,
stable, semi-stable, and stage semantics. `argumentation.setaf_io` provides
ASPARTIX fact I/O plus compact deterministic SETAF parser/writer helpers.

`argumentation.enforcement` provides a brute-force minimal-change oracle for
argument and extension enforcement over Dung AFs. It returns typed witness
edits, the edited framework, and the resulting extensions.

`argumentation.caf` implements claim-augmented AFs with inherited and
claim-level extension views plus a concurrence checker.

`argumentation.dynamic` provides a recompute-from-scratch dynamic AF wrapper
with argument/attack update streams and credulous/skeptical queries after each
state transition.

`argumentation.approximate` exposes k-stable semantics, bounded grounded
iteration, and budgeted semi-stable approximation with exactness metadata.

`argumentation.epistemic` represents epistemic graphs with positive and
negative influences over belief levels, finite model enumeration, evidence
updates, and projection to constellation PrAFs. Its linear atomic constraint
satisfiability and entailment helpers use `z3-solver` when the optional `z3`
extra is installed; this is the current Z3-backed surface.

`argumentation.dfquad` exposes DF-QuAD aggregation/combination and strength
propagation for quantitative bipolar graphs. `argumentation.equational`
provides iterative equational fixpoint scoring schemes. `argumentation.matt_toni`
computes finite zero-sum game strengths for small AFs and raises when the game
matrix is too large for the in-package solver.

`argumentation.gradual_principles` contains executable checks for balance,
directionality, and monotonicity over gradual strength functions.
`argumentation.vaf_completion` contains finite value-based argument-chain and
audience helpers for fact-uncertainty completion scenarios.

`argumentation.llm_surface` is a dependency-free adapter for argumentative LLM
pipelines: callers supply propositions and attack/support edges, while the
package computes QBAF strengths, Shapley-style attack explanations, and
contestation witnesses.

## ICCMA interop and pure SAT encoding

`argumentation.iccma` reads and writes ICCMA-style AF, ADF, and ABA exchange
formats, allowing frameworks to be exchanged with external argumentation
solvers.

```python
from argumentation.iccma import parse_aba, parse_adf, parse_af, write_af

framework = parse_af("p af 3\n1 2\n2 3\n")
text = write_af(framework)
```

`argumentation.sat_encoding` provides a pure-Python CNF encoding of the stable
extension semantics over one Boolean variable per argument. The encoding is
solver-independent: the included reference enumerator decides satisfaction by
direct assignment scan, and the same `CNFEncoding` can be handed to any SAT
solver that accepts DIMACS-style integer literals.

```python
from argumentation.sat_encoding import (
    encode_stable_extensions,
    stable_extensions_from_encoding,
)

encoding = encode_stable_extensions(framework)
extensions = stable_extensions_from_encoding(encoding)
```

## Solver surfaces

`argumentation.solver.solve_dung_extensions` is a typed dispatcher over the
single in-package Dung extension path. Its supported backend name is
`"labelling"`; asking for `"z3"` returns `SolverBackendUnavailable` with an
install hint to use `"labelling"`.

The package still has an optional `z3` extra, but it is for
`argumentation.epistemic` linear atomic constraint satisfiability and
entailment. There is no Dung Z3 extension backend in the current package
surface.

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

- Pure-Python algorithms are the reference implementation for package-owned
  algorithms. Solver adapters are typed boundaries around external tools or
  optional dependencies.
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
Hypothesis. Differential tests cross-check independently implemented package
paths where the repository has more than one executable route.
