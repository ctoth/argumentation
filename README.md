# argumentation

A finite, citation-anchored Python library for formal argumentation.

`argumentation` is a small, pure-Python kernel that implements the standard
objects and algorithms of computational argumentation theory: Dung abstract
argumentation, ASPIC+ structured argumentation, ABA / ABA+, abstract
dialectical frameworks, bipolar and value-based AFs, partial AFs with
completion-based reasoning, AF revision, probabilistic and gradual semantics,
ranking and weighted services, and pure-SAT and ASP encodings of the standard
extension semantics. Every algorithm cites the paper, definition, and (where
useful) page that fixes its behaviour. The pure-Python implementations are the
reference for package algorithms; solver adapters are typed boundaries around
external tools.

## Contents

- [Install](#install)
- [Quick start](#quick-start)
- [Surface tour](#surface-tour)
- [Core: Dung, labellings, preferences, dispatch](#core)
- [Structured: ASPIC+, ABA, accrual](#structured)
- [Quantitative and bipolar: ranking, weighted, gradual, DF-QuAD](#quantitative-and-bipolar)
- [Probabilistic and epistemic](#probabilistic-and-epistemic)
- [Specialized frameworks: ADF, SETAF, CAF, VAF, practical reasoning](#specialized-frameworks)
- [Dynamics, revision, enforcement](#dynamics-revision-enforcement)
- [Encoding and interop: ICCMA, SAT, datalog grounding](#encoding-and-interop)
- [Solver surfaces](#solver-surfaces)
- [`iccma-cli`](#iccma-cli)
- [Design](#design)
- [Non-goals](#non-goals)
- [Development](#development)

## Install

```powershell
uv add formal-argumentation
```

The PyPI distribution name is `formal-argumentation`; the import name is
`argumentation`. Requires Python 3.11+. The core kernel has no runtime
dependencies.

Optional extras unlock specific surfaces:

| Extra | What it unlocks | Pulls |
|---|---|---|
| `[z3]` | `argumentation.epistemic` linear atomic constraint satisfiability and entailment | `z3-solver>=4.12` |
| `[asp]` | Clingo-backed ABA solving (`argumentation.aba_asp`) and ASP backends in `argumentation.aspic_encoding` | `clingo>=5.7` |
| `[grounding]` | Datalog-style grounding of defeasible theories into ASPIC+ (`argumentation.datalog_grounding`) | [`gunray`](https://github.com/ctoth/gunray) (sourced from git, not PyPI) |

```powershell
uv add "formal-argumentation[z3]"
uv add "formal-argumentation[asp]"
```

The `[grounding]` extra requires resolving `gunray` from its git URL; see
`pyproject.toml` for the source declaration.

## Quick start

A Dung framework, three semantics, in eight lines:

```python
from argumentation.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)

af = ArgumentationFramework(
    arguments=frozenset({"a", "b", "c", "d"}),
    defeats=frozenset({("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")}),
)

grounded_extension(af)     # frozenset()
preferred_extensions(af)   # [frozenset({"a", "c"}), frozenset({"b", "d"})]
stable_extensions(af)      # [frozenset({"a", "c"}), frozenset({"b", "d"})]
```

Frameworks are immutable, equality is structural, and there is no global
state. The same dataclass flows into the labelling bridge, generic semantics
dispatch, the SAT encoder, the probabilistic kernel, and the ICCMA writer.

## Surface tour

| Family | Modules | One-line summary |
|---|---|---|
| [Core](#core) | `dung`, `labelling`, `preference`, `semantics` | Dung 1995 + Caminada/Gaggl-Woltran/DMT extensions, three-valued labellings, preference primitives, generic dispatch |
| [Structured](#structured) | `aspic`, `aspic_encoding`, `aspic_incomplete`, `subjective_aspic`, `aba`, `aba_asp`, `aba_sat`, `accrual` | ASPIC+ argument construction, ASP-style encoding, incomplete-premise reasoning, flat ABA / ABA+ with native, ASP, and SAT backends |
| [Quantitative and bipolar](#quantitative-and-bipolar) | `bipolar`, `gradual`, `gradual_principles`, `ranking`, `ranking_axioms`, `weighted`, `dfquad`, `equational`, `matt_toni` | Cayrol bipolar, Potyka quadratic energy + Shapley impacts, Categoriser/Burden rankings, Dunne-style weighted, DF-QuAD, Gabbay equational, zero-sum game strengths |
| [Probabilistic and epistemic](#probabilistic-and-epistemic) | `probabilistic`, `epistemic` | PrAFs over seven strategies (Monte Carlo, exact enum, tree-decomp DP, paper-faithful Popescu-Wallner, DF-QuAD), epistemic graphs with Z3-backed constraints |
| [Specialized frameworks](#specialized-frameworks) | `adf`, `setaf`, `setaf_io`, `caf`, `vaf`, `vaf_completion`, `practical_reasoning` | Brewka-Woltran ADFs with typed acceptance ASTs, collective-attack SETAFs, claim-augmented AFs, Bench-Capon value-based, Atkinson AATS practical arguments |
| [Dynamics and revision](#dynamics-revision-enforcement) | `partial_af`, `af_revision`, `dynamic`, `enforcement`, `approximate` | Partial AFs and completions, Baumann/Diller revision, dynamic update streams, minimal-change enforcement, k-stable approximation |
| [Encoding and interop](#encoding-and-interop) | `iccma`, `iccma_cli`, `sat_encoding`, `af_sat`, `aba_sat`, `datalog_grounding`, `llm_surface` | ICCMA AF/ADF/ABA exchange, pure-Python SAT encodings, incremental AF SAT kernel, Gunray-grounded ASPIC+, QBAF adapter for argumentative LLM pipelines |
| [Solver orchestration](#solver-surfaces) | `solver`, `solver_results`, `solver_differential`, `backends`, `solver_adapters/` | Typed solver tasks, capability detection, default backend routing, ICCMA / clingo subprocess adapters |

`docs/architecture.md` covers the kernel-and-adapters design in depth.
`docs/backends.md` documents the backend selection rule.

## Core

`argumentation.dung` provides the four canonical Dung semantics —
`grounded_extension`, `complete_extensions`, `preferred_extensions`,
`stable_extensions` — together with `naive_extensions`,
`semi_stable_extensions` (Caminada 2011), `stage_extensions`,
`cf2_extensions` (Gaggl & Woltran 2013), `stage2_extensions`,
`eager_extension`, `ideal_extension` (Dung, Mancarella & Toni 2007), and
prudent-semantics helpers. The `ArgumentationFramework` dataclass tracks both
a pre-preference `attacks` relation (used by conflict-freeness) and the
post-preference `defeats` relation (used by defence), following Modgil &
Prakken (2018) Def 14.

`argumentation.labelling` exposes the three-valued IN / OUT / UNDEC labelling
and a bridge from extensions to labellings:

```python
from argumentation.labelling import Labelling

labelling = Labelling.from_extension(af, frozenset({"a", "c"}))
labelling.in_arguments         # frozenset({"a", "c"})
labelling.out_arguments        # frozenset({"b", "d"})
labelling.undecided_arguments  # frozenset()
labelling.range                # in ∪ out
```

`argumentation.preference` provides preference primitives used across ASPIC+
and revision: `strict_partial_order_closure` (transitive closure with cycle
and reflexivity rejection), `strictly_weaker` (elitist and democratic
comparisons over numeric strength vectors, Modgil & Prakken Def 19), and
`defeat_holds` (generic attack-to-defeat resolution).

`argumentation.semantics` is a small set-returning dispatcher for callers that
work across framework families:

```python
from argumentation.semantics import accepted_arguments, extensions

extensions(af, semantics="grounded")
accepted_arguments(af, semantics="preferred", mode="credulous")
```

> Dung, P. M. (1995). On the acceptability of arguments and its fundamental
> role in nonmonotonic reasoning, logic programming and *n*-person games.
> *Artificial Intelligence*, 77(2), 321–357.
> Caminada, M. (2011). Semi-stable semantics. *Argument & Computation*, 2(1).
> Gaggl, S. A. & Woltran, S. (2013). The cf2 argumentation semantics
> revisited. *Journal of Logic and Computation*, 23(5), 925–949.
> Dung, P. M., Mancarella, P. & Toni, F. (2007). Computing ideal sceptical
> argumentation. *Artificial Intelligence*, 171(10–15), 642–674.

## Structured

`argumentation.aspic` builds arguments from a knowledge base and a set of
strict and defeasible rules over a logical language with a contrariness
function, then derives attacks and defeats. The full ASPIC+ surface includes
`build_arguments`, `compute_attacks`, `compute_defeats`, argument accessors
(`conc`, `prem`, `sub`, `top_rule`, `def_rules`, `last_def_rules`, `prem_p`,
`is_firm`, `is_strict`), `transposition_closure`, `strict_closure`,
`is_c_consistent`, and a `CSAF` type packaging the constructed structured AF.

```python
from argumentation.aspic import (
    ArgumentationSystem, ContrarinessFn, GroundAtom, KnowledgeBase, Literal,
    PreferenceConfig, Rule, build_arguments, compute_attacks, compute_defeats,
)

p, q = Literal(GroundAtom("p")), Literal(GroundAtom("q"))
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
    rule_order=frozenset(), premise_order=frozenset(),
    comparison="elitist", link="last",
)
arguments = build_arguments(system, kb)
defeats = compute_defeats(compute_attacks(arguments, system), arguments, system, kb, pref)
```

`argumentation.aspic_encoding` encodes ASPIC+ theories into a deterministic
ASP-style fact vocabulary (Lehtonen, Niskanen & Järvisalo 2024) and provides a
typed grounded-query surface backed by either the materialised reference
projection or an optional registered backend (e.g. clingo via the `[asp]`
extra).

`argumentation.aspic_incomplete` reasons over ASPIC+ theories with optional
ordinary premises. `evaluate_incomplete_grounded` enumerates all completions
of the unknown premises and classifies a query literal as `stable`,
`relevant`, `unknown`, or `unsupported`.

`argumentation.subjective_aspic` implements Wallner-style value filtering
before ASPIC+ argument construction. `argumentation.accrual` exposes
Prakken-style weak/strong applicability checks and accrual envelopes for
same-conclusion arguments.

`argumentation.aba` implements flat ABA and ABA+ over ASPIC literals,
including complete, preferred, stable, naive, grounded, well-founded, and
ideal assumption-extension functions plus a Dung projection.
`argumentation.aba_sat` provides task-directed support-mask SAT enumeration
for stable, complete, and preferred extensions. `argumentation.aba_asp`
provides clingo-backed extension queries when the `[asp]` extra is installed.

> Modgil, S. & Prakken, H. (2018). A general account of argumentation with
> preferences. *Artificial Intelligence*, 248, 51–104.
> Lehtonen, T., Niskanen, A., & Järvisalo, M. (2024). Reasoning over ASPIC+
> in answer set programming. *KR 2024*.
> Odekerken, D., Borg, A. & Bex, F. (2023). Justification, stability and
> relevance for case-based reasoning with incomplete focus cases.

## Quantitative and bipolar

`argumentation.bipolar` adds an explicit support relation alongside defeats.
Support chains induce *derived* defeats (supported and indirect), computed to
a fixpoint, and yield d-, s-, and c-admissibility variants.

```python
from argumentation.bipolar import (
    BipolarArgumentationFramework, cayrol_derived_defeats,
    d_preferred_extensions,
)

baf = BipolarArgumentationFramework(
    arguments=frozenset({"a", "b", "c"}),
    defeats=frozenset({("b", "c")}),
    supports=frozenset({("a", "b")}),
)
cayrol_derived_defeats(baf.defeats, baf.supports)   # {("a", "c")}
```

`argumentation.ranking` provides non-binary acceptability rankings —
Categoriser scores, iterative Burden numbers, and others. Results expose
`scores`, `ranking` (a tuple of frozensets, one per tier, best first),
`converged`, `iterations`, and `semantics`:

```python
from argumentation.ranking import categoriser_ranking

result = categoriser_ranking(af)
result.scores       # {"a": 0.618..., "b": 0.618..., ...}
result.ranking      # tuple of frozensets, best tier first
result.converged    # True / False
```

`argumentation.weighted` implements Dunne-style weighted argument systems by
enumerating attack sets whose deleted weight fits an inconsistency budget.

`argumentation.gradual` computes Potyka-style quadratic-energy strengths for
weighted bipolar graphs, exposes revised direct-impact attribution, and
computes exact Shapley-style per-attack impact scores (Al Anaissy et al. 2024
Def 13).

`argumentation.dfquad` exposes DF-QuAD aggregation/combination and strength
propagation. `argumentation.equational` provides iterative equational
fixpoint scoring schemes. `argumentation.matt_toni` computes finite zero-sum
game strengths and raises when the game matrix is too large for the in-package
solver.

`argumentation.gradual_principles` and `argumentation.ranking_axioms` contain
executable checks for balance, directionality, monotonicity, ranking
preorder, void-precedence, and cardinality-precedence obligations.

`argumentation.vaf` implements Bench-Capon value-based argumentation
frameworks. `argumentation.llm_surface` is a dependency-free QBAF adapter for
argumentative LLM pipelines (Freedman et al. 2025).

> Cayrol, C. & Lagasquie-Schiex, M.-C. (2005). On the acceptability of
> arguments in bipolar argumentation frameworks. In *ECSQARU 2005*.
> Al Anaissy, C., Toni, F., & Rago, A. (2024). Shapley value for argumentation.
> Freedman, G., Rago, A., Albini, E., Toni, F., & Cocarascu, O. (2025).
> Argumentative Large Language Models for explainable and contestable claim
> verification.

## Probabilistic and epistemic

`argumentation.probabilistic` implements probabilistic argumentation
frameworks (PrAFs). Each argument has an existence probability and each
defeat has a presence probability; acceptance is the probability over sampled
worlds.

```python
from argumentation.probabilistic import (
    ProbabilisticAF, compute_probabilistic_acceptance,
)

praf = ProbabilisticAF(
    framework=af,
    p_args={"a": 0.9, "b": 0.7, "c": 1.0, "d": 0.6},
    p_defeats={("a", "b"): 0.8, ("b", "c"): 1.0, ("c", "d"): 0.9, ("d", "a"): 0.5},
)
result = compute_probabilistic_acceptance(praf, semantics="grounded")
result.acceptance_probs    # {"a": ..., "b": ..., ...}
result.strategy_used       # auto-routed
```

`compute_probabilistic_acceptance` dispatches across seven strategies:

- `deterministic` — fast path when every probability is 0 or 1; collapses to
  standard Dung evaluation.
- `exact_enum` — brute-force enumeration over induced Dung AFs; default for
  small frameworks (up to ~13 arguments).
- `mc` — Monte Carlo sampling with Agresti–Coull stopping (Li, Oren & Norman
  2012 Algorithm 1), decomposed across connected components per Hunter &
  Thimm 2017 Proposition 18.
- `exact_dp` — adapted grounded edge-tracking tree-decomposition backend for
  credulous grounded acceptance on defeat-only worlds. Effective in practice
  for primal-graph treewidth ≤ ~15; not asymptotically faster than brute
  force, and not the full Popescu & Wallner I/O/U witness-table DP.
- `paper_td` — paper-faithful Popescu & Wallner (2024) Algorithm 1 for exact
  extension-probability queries. Opt-in only.
- `dfquad_quad` and `dfquad_baf` — DF-QuAD gradual semantics for
  quantitative bipolar frameworks (Freedman et al. 2025).

Two query kinds are supported. Per-argument acceptance is the default;
exact-set extension probability is opt-in via `query_kind="extension_probability"`
with `queried_set=...`. `summarize_defeat_relations` exposes exact defeat
marginals as a diagnostic.

`argumentation.epistemic` represents epistemic graphs with positive and
negative influences over belief levels, finite model enumeration, evidence
updates, and projection to constellation PrAFs. It is the only Z3-backed
surface in the package; install `[z3]` to use linear atomic constraint
satisfiability and entailment helpers.

> Li, H., Oren, N., & Norman, T. J. (2012). Probabilistic argumentation
> frameworks. In *TAFA 2011*.
> Hunter, A. & Thimm, M. (2017). Probabilistic reasoning with abstract
> argumentation frameworks. *JAIR*, 59, 565–611.
> Popescu, A. & Wallner, J. P. (2024). Tree-decomposition-based dynamic
> programming for probabilistic abstract argumentation.

## Specialized frameworks

`argumentation.adf` implements abstract dialectical frameworks with typed
acceptance-condition ASTs, three-valued interpretations,
grounded/admissible/complete/model/preferred/stable model enumeration,
structural link classification, JSON/formula I/O helpers, and Dung bridges.

`argumentation.setaf` implements argumentation frameworks with collective
attacks (conflict-free, admissible, complete, preferred, grounded, stable,
semi-stable, stage). `argumentation.setaf_io` provides ASPARTIX fact I/O plus
compact deterministic SETAF parser/writer helpers. See `docs/setaf.md` for
semantics details.

`argumentation.caf` implements claim-augmented AFs with inherited and
claim-level extension views plus a concurrence checker. See
`docs/caf-semantics.md`.

`argumentation.vaf` implements Bench-Capon value-based argumentation
frameworks: audience-specific defeat removes attacks whose target value is
preferred to the attacker value, and objective/subjective acceptance quantify
over audience orders. `argumentation.vaf_completion` adds finite
argument-chain and audience helpers for fact-uncertainty completions.

`argumentation.practical_reasoning` implements the Atkinson and Bench-Capon
AATS grounding for AS1-style practical arguments and the CQ5, CQ6, and CQ11
choice-stage objections.

## Dynamics, revision, enforcement

`argumentation.partial_af` represents AFs that leave some attack pairs
*uncertain*. Pairs over A × A are partitioned into `attacks`, `ignorance`, and
`non_attacks`; reasoning is by enumerating *completions*. The module also
provides three merge aggregations (`sum_merge_frameworks`,
`max_merge_frameworks`, `leximax_merge_frameworks`) and `consensual_expand`.

`argumentation.af_revision` adds arguments and attacks to an existing
framework, or revises an extension state by a formula or by a target
framework, while preserving rationality postulates:

```python
from argumentation.af_revision import (
    baumann_2015_kernel_union_expand,
    cayrol_2014_classify_grounded_argument_addition,
    AFChangeKind,
)

merged = baumann_2015_kernel_union_expand(base_af, incoming_af)
kind = cayrol_2014_classify_grounded_argument_addition(
    framework=base_af, argument="x",
    attacks=frozenset({("x", "a")}),
)
# AFChangeKind.DECISIVE | RESTRICTIVE | QUESTIONING |
# DESTRUCTIVE | EXPANSIVE | CONSERVATIVE | ALTERING
```

`argumentation.dynamic` provides a recompute-from-scratch dynamic AF wrapper
with argument/attack update streams and credulous/skeptical queries after
each state transition.

`argumentation.enforcement` provides a brute-force minimal-change oracle for
argument and extension enforcement, returning typed witness edits, the edited
framework, and the resulting extensions.

`argumentation.approximate` exposes k-stable semantics, bounded grounded
iteration, and budgeted semi-stable approximation with exactness metadata.

> Baumann, R. (2015). Context-free and context-sensitive kernels: update and
> deletion equivalence in abstract argumentation. In *ECAI 2014*.
> Diller, M., Haret, A., Linsbichler, T., Rümmele, S., & Woltran, S. (2015).
> An extension-based approach to belief revision in abstract argumentation.
> Cayrol, C., de Saint-Cyr, F. D., & Lagasquie-Schiex, M.-C. (2010).
> Change in abstract argumentation frameworks: adding an argument.
> *JAIR*, 38, 49–84.

## Encoding and interop

`argumentation.iccma` reads and writes ICCMA-style AF, ADF, and ABA exchange
formats:

```python
from argumentation.iccma import parse_af, write_af

af = parse_af("p af 3\n1 2\n2 3\n")
text = write_af(af)
```

`argumentation.sat_encoding` provides a pure-Python CNF encoding of stable
extension semantics over one Boolean variable per argument; the encoding is
solver-independent. `argumentation.af_sat` provides an incremental SAT kernel
for Dung AFs with telemetry (`SATCheck`, `SATTraceSink`, `AfSatKernel`).
`argumentation.aba_sat` provides task-directed SAT enumeration for ABA.

`argumentation.datalog_grounding` (requires the `[grounding]` extra) grounds
a Gunray `DefeasibleTheory` into propositional ASPIC+ via
`ground_defeasible_theory(theory) -> GroundedDatalogTheory`. It consumes
[Gunray](https://github.com/ctoth/gunray) — a sister project that owns the
defeasible-theory schema — rather than redefining one.

`argumentation.llm_surface` is a dependency-free adapter for argumentative
LLM pipelines: callers supply propositions and attack/support edges, the
package computes QBAF strengths, Shapley-style attack explanations, and
contestation witnesses.

The package ships with prebuilt clingo `.lp` encodings under
`argumentation.encodings/` (admissible/complete/stable for AF, ASPIC+, and
ABA), used by the ASP-backed paths.

## Solver surfaces

`argumentation.solver` separates solver tasks by result type:

- `ExtensionEnumerationSuccess` — all extensions for enumeration tasks.
- `SingleExtensionSuccess` — one witness extension or `None`.
- `AcceptanceSuccess` — credulous/skeptical yes/no plus a witness or
  counterexample when the backend supplies one.

Entry points include `solve_dung_extensions`, `solve_dung_single_extension`,
`solve_dung_acceptance`, `solve_aba_extensions`, `solve_aba_single_extension`,
`solve_aba_acceptance`, `solve_adf_models`, and `solve_setaf_extensions`.

ICCMA `SE` tasks produce one witness, not full enumeration. Use
`solve_dung_single_extension(..., backend="iccma", iccma=ICCMAConfig(...))` or
the ABA equivalent for that contract; `solve_dung_extensions(..., backend="iccma")`
returns typed unavailable instead of pretending one witness enumerates every
extension.

`argumentation.backends` exposes capability detection (`has_clingo`,
`has_z3`) and `default_backend(...)` / `backend_choice_reason(...)` for
routing decisions. `argumentation.solver_results` defines the typed
`SolverUnavailable`, `SolverProcessError`, and `SolverProtocolError` returns.
`argumentation.solver_differential` provides
`solver_capability_matrix` and task-aware comparison helpers across native,
ICCMA, SAT, clingo, ADF, SETAF, and unsupported backend combinations.

unsupported task/semantics/backend combinations return typed unavailable
results before subprocess invocation. Optional solver environment variables
used by smoke tests: `ICCMA_AF_SOLVER`, `ICCMA_ABA_SOLVER`, `ASPFORABA_SOLVER`.

External callers supply already-projected frameworks, theories, or benchmark
manifests and consume package result objects; the package does not own caller
identity, storage, merge policy, provenance, or rendering policy.

## `iccma-cli`

The package ships an ICCMA-format command-line solver, registered as the
`iccma-cli` console script:

```powershell
iccma-cli --problem SE-ST --file framework.af
iccma-cli --problem DC-PR --file framework.af --argument 3
iccma-cli --problem SE-CO --file theory.aba --backend sat
```

Supported problem codes: `SE` (single extension), `DC` (credulous decision),
`DS` (skeptical decision). Supported semantics: `CO`, `GR`, `PR`, `ST`, `SST`,
`STG`, `ID`, `CF2`. Backends: `auto`, `native`, `sat`. The CLI dispatches into
`argumentation.solver` and reads ICCMA `p af` and `p aba` input files.

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

`docs/architecture.md` is the long form. `docs/backends.md` documents the
default backend selection rule. `docs/gaps.md` enumerates known limitations
and open workstreams.

## Non-goals

`argumentation` does not own application provenance, source calibration,
subjective-logic opinion calculi, persistent storage, repository workflow, or
application-side argument rendering. Callers translate those concerns into
finite formal objects before invoking this package. The `iccma-cli` script
is a thin solver wrapper for ICCMA-format files; it is not an
application-side CLI.

## Development

```powershell
uv sync
uv run pyright src
uv run pytest -vv
```

Tests are tagged `unit`, `property`, and `differential`. Property tests use
Hypothesis. Differential tests cross-check independently implemented package
paths where the repository has more than one executable route.

See `CONTRIBUTING.md` for contribution guidelines.
