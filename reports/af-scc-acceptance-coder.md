# Coder report: exp 6A — query-directed SCC-recursive acceptance (exp/af-scc-acceptance)

Worktree: `.claude/worktrees/agent-a51d50217dbe8f6c9`, branch
`exp/af-scc-acceptance` from `main` @ `5dd6a03`. Recommend-only; nothing
pushed or merged. Full detail in
`experiments/2026-07-10-af-scc-acceptance.md` (committed on the branch).

## Commits (in order)

| hash | content |
|---|---|
| `ed05467` | Derivation-before-code: per-semantics soundness of cone restriction (committed FIRST, before any code) |
| `3805f01` | Cone module + auto routing + 16 TDD tests (iteration 1) |
| `9dfc489` | Z3 sat-core engine for cone checks; DS-CO via grounded membership (iteration 2) |
| `911135b` | DS-PR minimum-cone-size guard (t15 kill-criterion fix) — final code commit |
| `8d4fda4`, `3b860e3` | Experiment doc: fast contracts, metric-gate results, GO decision |

## What was built

`src/argumentation/solving/af_scc_cone.py` + a routing hook in
`solve_dung_acceptance` (auto backend only): for DC/DS on
complete/preferred/stable, compute the query's SCC ancestor cone (Baroni
2005 Def 17; the cone is attack-closed) and decide on `AF|cone` with the
existing `af_sat` kernels. Per the derivation (committed first):

- **Complete**: fully directional (projection for all SCC-recursive
  semantics via Def 18/20; lifting via nonempty `GF` for complete/preferred)
  ⇒ DC-CO decided by one cone SAT check; DS-CO decided **polynomially** as
  grounded membership; certificates lifted to full-framework complete
  extensions by a characteristic-function closure (proved to preserve the
  cone choice; property-tested against the native enumerator).
- **Preferred**: DS-PR cone-equivalent, decided by the existing CDAS solver
  on the cone (answer-only, contract-identical). DC-PR left flat (witness
  contract; not a frontier cell).
- **Stable**: NOT directional — one-sided rules only (DC-ST cone-NO and
  DS-ST cone-YES conclusive; sat outcomes fall back to the flat path). The
  vacuous-YES trap (downstream odd cycle kills SE(AF)) is a unit test.
  DS-ST was NOT dropped: the sound one-sided check is wired with fallback.
- Guards: single-SCC / cone-spanning queries, explicit backends, and
  frameworks with a separate pre-preference `attacks` layer all keep the
  flat path byte-for-byte.
- `AfSatKernel` gained an `engine` parameter (`"smt"` default = unchanged;
  `"sat-core"` = `Tactic('sat')`), threaded through the finders and CDAS
  sub-solvers; only the cone path uses it.

**Plan-mechanics note for the reviewer**: the plan's "GF recursion restricted
to the cone with per-SCC base solves" collapses, by Def 20 applied to
`AF|U`, to deciding the cone framework's semantics; the derivation commit
records why solve-time per-SCC extension enumeration was rejected (NO
answers require exhausting per-SCC cross products — exponential; per-SCC
kernels don't shrink total clauses since intra-SCC attacks dominate). The
per-SCC machinery computes the cone; Def 18 proves it sound; SAT replaces
the `2^n` base-solve cliff. Both stated targets of the mechanics (no subset
enumeration, no whole-graph 61 s+ kernel builds) are met.

## Verified anatomy deltas (probes on this machine)

- crusti_175 (89 425 args / 6.24 M attacks): cone = **1400 args / 92 016
  defeats / 8 SCCs** (matches scout). Phase costs: parse 14.7 s, cone
  extraction 14.1 s, kernel build 13.3 s, unconstrained check 1.9 s.
- **The real sink was the Z3 default SMT core, not kernel build**: the
  `require_in(q)` complete-labelling check = 265 s default vs **1.6 s**
  under `Tactic('sat')` (same formula; QF_FD similar; admissible encoding
  slower under both). Iteration 1 (cone + default engine) still TO'd for
  exactly this reason.
- Witness lifting closure on the full 6.2 M-attack graph: 11 s, verified
  `q ∈ closure` and closure complete.
- Cone checks under sat-core: crusti_175 DC-CO 1.6 s sat; crusti_225 24.5 s
  sat; scc_7481 0.39 s unsat; scc_3605 80 s unsat after 24 s build
  (909-node/248 k single-SCC cone — the marginal cell); crusti_225 DS-ST
  `require_out` sat in 21 s ⇒ inconclusive ⇒ fallback (predicted).

## Per-cell before/after vs ground truth (frontier t120, labels af-scc-acceptance-{baseline,fixed2})

| cell | baseline | after | reference | verdict |
|---|---|---|---|---|
| DC-CO crusti_175 | TO | solved **YES** | YES | FLIP correct |
| DC-CO crusti_225 | TO | solved **YES** | YES | FLIP correct |
| DC-CO scc_3605 | TO | solved **NO** (~103 s) | NO | FLIP correct |
| DC-CO scc_7481 | TO | solved **NO** | NO | FLIP correct |
| DS-PR crusti_125 | TO | solved **NO** (29 s) | NO | FLIP correct |
| DS-PR crusti_175 | TO | TO | NO | stop rule (see below) |
| DS-PR crusti_225 | TO | TO | NO | stop rule |
| DS-ST crusti_175 | TO | TO | YES | one-sided rule inconclusive by design |
| DS-ST crusti_225 | TO | TO | YES | same |

18 AF frontier rows: 6/12 → **11 solved / 7 TO**; zero regressions, zero
answer changes on already-solved rows (incl. DS-ST crusti_125 = false,
DC-CO scc_1554 = false, mainkwt ×3 = false). **Metric gate (≥5 of 7 in-scope
cells, answers matching the table): MET — exactly 5/7.**

**Stop-rule report (DS-PR crusti_175/225, 2 iterations spent)**: cone
verified small; time now goes to Python-API clause construction — CDAS
builds three kernels on the 92 k-attack cone (super-core ~16 s + extension
~14 s + double-admissible attacker ~32 s ≈ 62 s) on top of parse ~15 s +
cone ~14 s, before its loop starts. SAT checks are seconds. Follow-up:
shared-kernel / direct-CNF CDAS substrate (scout Proposal C), super-core
skip on big cones.

## Slice guard (DS-PR cap320 t15, 964 rows)

| run | solved | TO | common-row time | mismatches |
|---|---|---|---|---|
| baseline | 221 | 34 | — | — |
| fixed (pre-guard) | 233 | 22 | −13.97 % | 0 |
| fixed2 (final) | 221 | 34 | −0.44 % | 0 |

Kill evaluation: zero answer changes everywhere; common-row time never
regressed. The pre-guard run genuinely lost BA_160_80_2 (0.6 s flat → 95–97 s
under the non-incremental sat-core CDAS loop on a 232-defeat cone) — fixed
by `PREFERRED_CONE_MIN_DEFEATS = 15 000` (measured bounds: pathology at 232
defeats, wins from 22 k up); it solves in 0.6–0.7 s again. fixed2's residual
5-lost/5-gained churn is t15 boundary noise: all churned rows are 10.7–15.0 s
rows, one (`n192p5q2_ve`) churned with cone = whole graph (unchanged code
path), and identical-code mainkwt rows shifted uniformly ~+3.5 s between
runs (environmental drift; other agents share the machine). Note the
baseline itself (221/34) deviates from exp-1's recorded 235/20. Substance:
kill NOT triggered; the one code-caused loss was found and fixed.

## Correctness gates

- New suite `tests/solving/test_af_scc_cone_acceptance.py`: 22 tests (RED
  first at each step), including Hypothesis auto-vs-native equivalence for
  all three semantics × both tasks on random multi-SCC AFs, certificate
  validity against the native enumerator, the stable vacuity trap, and the
  attacks-layer guard.
- `pytest tests/solving tests/core`: 1108 passed, 3 skipped (pre-existing
  environmental). Full CI-equivalent: `pytest -q --timeout=600` = 2970
  passed, 4 skipped, 1 xfailed, **2 failed — both verified pre-existing on
  unmodified main** (run on detached `5dd6a03`, identical failures):
  `test_current_docs_do_not_cite_old_flat_source_paths` (docs relocated to
  main by `8800185` cite old flat paths) and
  `test_large_dense_stable_auto_route_uses_sat_without_asp` (ABA-only path,
  untouched by this branch). Main needs a separate fix; this branch adds no
  red.
- `pyright src`: 0 errors. `lint-imports`: 2 kept, 0 broken. `uv build`: ok.

## Process notes

- The first baseline attempt was killed and redone from a detached checkout
  of `5dd6a03` after realizing the runner's per-row subprocesses import the
  live worktree (contamination risk); all reported numbers come from clean
  runs with no source edits in flight.
- Benchmark artifacts: worktree `data/iccma/2025/runs/iccma-2025-af-scc-
  acceptance-{baseline,fixed,fixed2,t15-baseline,t15-fixed,t15-fixed2}*`
  (gitignored); logs under worktree `logs/`. ICCMA data was read via
  junctions into the main repo's `data/` (read-only; main tree untouched).

## Promotion recommendation

**GO** — promote `exp/af-scc-acceptance` through `911135b` (code) +
`3b860e3` (docs). Highest-value follow-ups: (a) incremental/direct-CNF CDAS
substrate (unlocks DS-PR crusti_175/225 and the ER family — cost model now
measured), (b) sat-core engine on the flat acceptance paths, (c) self-loop
preprocessing for the scc family.
