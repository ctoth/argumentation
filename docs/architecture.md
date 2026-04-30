# Architecture

`argumentation` is a finite, formal argumentation kernel. The library owns
data types and algorithms over argumentation frameworks; it does not own
any application-level concepts (storage, persistence, schedulers, CLIs).

## Modules

- `argumentation.dung` — Dung 1995 abstract argumentation frameworks and
  extension semantics. Core: grounded, complete, preferred, stable.
  Extended: naive, semi-stable (Caminada 2011), stage, CF2 (Gaggl &
  Woltran 2013), and ideal (Dung, Mancarella & Toni 2007).
- `argumentation.labelling` — Three-valued IN / OUT / UNDEC labelling and
  the extension-to-labelling bridge used by accrual and quantitative
  services.
- `argumentation.sat_encoding` — Solver-independent CNF encoding of stable
  extensions, plus a reference scan-based enumerator.
- `argumentation.iccma` — ICCMA-style AF, ADF, and ABA I/O for interop with
  external argumentation solvers.
- `argumentation.solver_adapters.iccma_af` — ICCMA 2023 AF solver subprocess
  adapter for `solver -p <task> -f <file> [-a <query>]`, with typed DC/DS/SE
  output parsing.
- `argumentation.aspic` — ASPIC+ literals, rules, premise/strict/defeasible
  arguments, attacks, defeats, and CSAF construction (Modgil & Prakken
  2018).
- `argumentation.aspic_encoding` — Deterministic ASP-style fact encoding
  of ASPIC+ theories (Lehtonen, Niskanen & Järvisalo 2024) and a typed
  grounded query surface with a backend-dispatch entry point.
- `argumentation.aspic_incomplete` — ASPIC+ reasoning with optional
  ordinary premises by exact completion enumeration; classifies a query
  as stable, relevant, unknown, or unsupported.
- `argumentation.aba` — Flat ABA and ABA+ frameworks over ASPIC literals,
  with constructor-level rejection of non-flat frameworks and preference-aware
  attack reversal (Bondarenko et al. 1997; Čyras & Toni 2016).
- `argumentation.adf` — Abstract dialectical frameworks with typed
  acceptance-condition ASTs, three-valued operator semantics, structural link
  classification, and Dung bridges (Brewka & Woltran 2010; Brewka et al. 2013).
- `argumentation.setaf` — SETAFs with collective attacks and Dung-style
  grounded, complete, preferred, stable, semi-stable, and stage semantics.
- `argumentation.setaf_io` — ASPARTIX SETAF facts plus package-local compact
  SETAF parser/writer.
- `argumentation.enforcement` — Brute-force minimal-change argument and
  extension enforcement with separate typed witnesses for unconstrained
  fixed-argument edits, conservative Baumann-style normal/strong/weak
  expansions, and explicit liberal source-to-target semantics changes.
- `argumentation.caf` — Claim-augmented AFs with inherited and claim-level
  views plus concurrence checks.
- `argumentation.dynamic` — Dynamic AF update streams with a named
  recompute oracle, Alfano-Greco-Parisi-style single-attack incremental
  influenced/reduced-AF updates for grounded, complete, preferred, and stable
  semantics, and query results with explicit fallback metadata.
- `argumentation.approximate` — k-stable semantics, bounded grounded
  iteration, and budgeted semi-stable approximation.
- `argumentation.epistemic` — Hunter-style epistemic language and belief
  distributions, labelled epistemic graphs with positive/negative/dependent
  labels, Potyka-style linear atomic constraints over probability labellings,
  and explicitly approximate belief-grid helpers.
- `argumentation.llm_surface` — Dependency-free QBAF construction,
  Shapley-style explanation, and contestation witnesses for externally supplied
  argumentative LLM proposition graphs.
- `argumentation.bipolar` — Cayrol-style bipolar argumentation frameworks
  with derived defeats and d/s/c-admissibility semantics.
- `argumentation.partial_af` — Partial argumentation frameworks with a
  three-way attack/ignorance/non-attack partition, completion enumeration,
  skeptical and credulous acceptance, and Sum / Max / Leximax merge
  operators.
- `argumentation.af_revision` — AF-level revision: kernel union expansion
  (Baumann 2015), revise-by-formula and revise-by-framework (Diller 2015),
  and grounded-argument-addition classification (Cayrol 2014).
- `argumentation.probabilistic` — Probabilistic argumentation frameworks
  (PrAFs) with primitive-relation uncertainty. Auto-routing strategy
  dispatcher across deterministic, Monte Carlo (Li et al. 2012),
  brute-force exact enumeration, tree-decomposition DP (Popescu & Wallner
  2024), and DF-QuAD gradual semantics (Freedman et al. 2025).
- `argumentation.probabilistic_components` — Connected component
  decomposition over the primitive semantic dependency graph (Hunter &
  Thimm 2017, Proposition 18).
- `argumentation.dfquad` — DF-QuAD aggregation/combination and strength
  propagation for quantitative bipolar graphs.
- `argumentation.probabilistic_treedecomp` — Min-degree treewidth
  estimation, tree decomposition computation, nice tree decomposition
  conversion, and an adapted grounded edge-tracking DP. This is exact for
  the supported grounded PrAF route, but not the full Popescu & Wallner I/O/U
  witness-table DP.
- `argumentation.equational` — Iterative equational fixpoint scoring schemes
  over weighted bipolar graphs.
- `argumentation.ranking` — Categoriser and Burden ranking-based semantics
  over Dung AFs.
- `argumentation.weighted` — Dunne-style weighted argument systems with
  inconsistency-budget grounded semantics and deleted-attack witnesses.
- `argumentation.gradual` — Potyka-style quadratic-energy gradual
  strengths for weighted bipolar graphs, revised direct-impact
  attribution, and exact Shapley-style per-attack impact scores
  (Al Anaissy et al. 2024).
- `argumentation.gradual_principles` — Executable balance, directionality,
  and monotonicity checks over gradual strength functions.
- `argumentation.matt_toni` — Finite zero-sum game strengths for small AFs,
  with explicit intractability signalling for oversized game matrices.
- `argumentation.subjective_aspic` — Wallner-style value filtering helpers for
  ASPIC+ subjective knowledge bases and defeasible rules.
- `argumentation.vaf` — Bench-Capon value-based argumentation frameworks,
  audience-specific defeat, and objective/subjective acceptance.
- `argumentation.vaf_completion` — Value-based argument-chain construction,
  line classification, fact-first audiences, and two-value cycle completion
  helpers.
- `argumentation.practical_reasoning` — Atkinson and Bench-Capon AATS-backed
  AS1 practical arguments with CQ5, CQ6, and CQ11 objection generation.
- `argumentation.ranking_axioms` — Executable ranking postulate checks over
  `RankingResult` outputs.
- `argumentation.accrual` — Prakken-style weak/strong applicability
  helpers and same-conclusion accrual envelopes.
- `argumentation.semantics` — Generic set-returning semantics dispatch over
  argumentation-owned Dung, bipolar, and partial-AF dataclasses.
- `argumentation.preference` — Strict-partial-order helpers and elitist
  and democratic preference comparisons (Modgil & Prakken 2018 Def 19).
- `argumentation.solver` — Typed Dung extension solve results. The supported
  Dung backend is `labelling`; unknown backend names, including the deleted
  `z3` backend name, return `SolverBackendUnavailable`.

## Backend policy

Pure Python algorithms are the reference implementation. Dung extension
enumeration currently has one package-owned execution path: labelling and
finite set enumeration in `argumentation.dung` / `argumentation.labelling`.

`argumentation.solver.solve_dung_extensions` exposes that path through the
backend name `labelling`. Other backend names return
`SolverBackendUnavailable`; this includes the old `z3` backend name. The
deleted `argumentation.dung_z3` module is not part of the current public
surface.

## Z3 usage

`z3-solver` remains an optional package dependency (extra: `z3`) and a
development dependency for tests, but not for Dung extension enumeration.
The current Z3-backed package surface is in `argumentation.epistemic`:
`constraints_satisfiable` and `constraints_entail` build linear real
constraints over argument probability labels and call Z3 when the optional
dependency is installed. Without `z3-solver`, those functions raise a
runtime error naming the missing dependency.

## Probabilistic backend routing

`compute_probabilistic_acceptance` selects among six strategies:
`deterministic`, `exact_enum`, `mc`, `exact_dp`, `paper_td`,
`dfquad_quad`, and `dfquad_baf`. The `auto` policy is:

1. If every argument and every relevant edge has a deterministic
   probability (within `1e-12` of 0 or 1), fall through to standard Dung
   evaluation in a single sampled world.
2. Otherwise, if the framework has at most thirteen arguments, enumerate
   induced Dung frameworks exactly (Li et al. 2012, p. 8).
3. Otherwise, if the framework requires relation-rich worlds (explicit
   support relations, or `attacks != defeats`), use Monte Carlo with
   Agresti–Coull stopping.
4. Otherwise, estimate primal-graph treewidth via the min-degree
   heuristic. If treewidth is at most the cutoff (default twelve) and the
   query is credulous-grounded acceptance, run the adapted edge-tracking
   tree-decomposition DP.
5. Otherwise, fall back to Monte Carlo.

`paper_td` is the paper-faithful Popescu & Wallner (2024) Algorithm 1 for
exact extension-probability queries. It is opt-in only, distinct from
`exact_dp`, and rejects queries other than `query_kind="extension_probability"`.

`dfquad_quad` and `dfquad_baf` are gradual semantics rather than Dung
semantics; they are never selected by `auto` and require explicit
selection. The `exact_dp` backend currently supports only credulous
grounded acceptance on defeat-only frameworks; calling it on richer
queries raises. Its current implementation tracks full edge sets and
forgotten arguments in table keys, so its asymptotic cost is not better
than brute-force enumeration; it is effective in practice for primal-graph
treewidth ≤ ~15.

## Generic semantics dispatch

`argumentation.semantics.extensions` returns extension sets for Dung,
bipolar, and partial AFs under their supported semantics names.
`accepted_arguments` derives credulous or skeptical accepted-argument sets
from that extension relation. The dispatcher is intentionally limited to
argumentation-owned dataclasses and does not accept application records,
storage rows, projection contexts, or presentation flags.

## Invariants

- Frameworks, rules, arguments, and extensions are immutable frozen
  dataclasses over frozensets. Equality is structural.
- `PartialArgumentationFramework` enforces at construction that
  `attacks`, `ignorance`, and `non_attacks` are pairwise disjoint and
  partition A × A.
- `ExtensionRevisionState` rebuilds its ranking on construction so that
  every named extension has rank zero and every non-extension has a
  strictly greater rank.
- Conflict-freeness is checked against the pre-preference attack relation
  when present (Modgil & Prakken 2018 Def 14); defence is checked against
  defeats (Dung 1995 Def 6). `ArgumentationFramework` carries both as
  separate fields.

## Non-goals

The package does not own application provenance, source calibration,
subjective-logic opinion calculi, persistent storage, repository workflow,
or CLI presentation. Those concerns belong outside the formal kernel and
must be projected into finite argumentation objects before calling these
algorithms.

## Citation discipline

Every public algorithm names its source paper, definition, and (where
useful) page in its docstring. When an implementation deliberately
diverges from a cited definition, the divergence is documented and a
focused test pins the chosen behaviour.
