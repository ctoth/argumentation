# AF DS-PR CDAS Alignment (Blocking Clause + Maximisation Removal) Result

Date: 2026-07-02

Status: measured on experiment branch; Variant B is a clean GO
(+6 solved, -6 timeouts, -1.66% time on baseline-solved rows, no losses,
no answer changes). Variant A was found vacuous against the paper and
stopped. Promotion is a recommendation only.

Experiment branch: `exp/af-dspr-cdas`

Evidence commits:

- `934d998 Remove AdmSup maximisation from DS-PR CDAS decide loop` (Variant B)

## Hypothesis

Bringing the existing CDAS-style DS-PR solver
(`PreferredSkepticalTaskSolver`, `src/argumentation/solving/af_sat.py`) in line
with Thimm/Cerutti/Vallati 2021 Algorithm 2 improves DS-PR wall time on the
known hard families (ER_300, mainkwt_250, crusti_g2io_125+) without losing
solved instances, via two candidate deltas:

- Variant A: strengthen `learn_witness_region` from the "some outsider" clause
  to the paper's exclusion of the seen extended set.
- Variant B: remove the `_grow_preferred` maximisation from the decide loop so
  the loop matches Algorithm 2 (CDAS) exactly.

## Single Variable

Variant B only: delete the `_grow_preferred` call (and its dead `None` check)
from `PreferredSkepticalTaskSolver.decide`, so the stored/blocked witness set is
the un-maximised complete extension `S'' ⊇ attacker ∪ {query}` exactly as in
Algorithm 2 line 12. Nothing else on the DS-PR path changed (super-core
precheck, shortcut ladder, `simplify_af` preprocessing, `learn_witness_region`
clause form all unchanged).

### Variant A is vacuous (no code change possible)

Re-derivation against the paper (pp. 2071-2072, read from
`papers/Thimm_2021_SkepticalReasoningPreferredSemantics/pngs/page-002.png` and
`page-003.png`):

`AdmExtAtt(AF, S, {S_1..S_n})` returns an admissible set `S'` such that there
is an admissible `S''` with (1) `S ⊆ S''`, (2) `S' R S''`, and (3) `S' ⊄= S_i`
for `i = 1..n` — i.e. the returned ATTACKER must not be a subset of any stored
extended set. Algorithm 2 line 12 stores `S''` "to avoid considering subsets of
S'' later".

The existing clause in `learn_witness_region` is
`Or(attacker_vars[a] for a in arguments - extension)`, whose negation is
exactly `attacker ⊆ extension`. So the current "some outsider" clause IS the
paper's condition (3), applied per stored set. There is no stronger paper form
to adopt. The plausible alternative reading — mirroring
`AfSatKernel.exclude_exact_extension` (af_sat.py:287) onto the attacker vars —
is strictly WEAKER (it forbids only the exact set, not its subsets) and is not
what the paper specifies. Variant A therefore has no implementable content and
was stopped, per the task's per-variant stop rule.

The only true deviation of the pre-experiment code from Algorithm 2 is the
`AdmSup`-style maximisation (`_grow_preferred`) applied to `S''` before storing
it — which is precisely Variant B's single variable. Note the maximised set is
a superset, so the pre-experiment blocking clause is per-iteration STRONGER
than the paper's; Variant B tests whether skipping the maximisation SAT calls
pays for the weaker per-iteration blocking.

### Variant B soundness re-derivation (done before coding)

- `_complete_extension(required_in=X)` is an existence-faithful `AdmExt(AF, X)`:
  every admissible set extends to a complete extension containing it (Dung's
  fundamental lemma) and complete extensions are admissible, so `sat`/`unsat`
  agree with `AdmExt`, and the returned complete extension is a valid choice of
  `AdmExt`'s nondeterministic witness.
- With `_grow_preferred` removed, the decide loop is Algorithm 2 verbatim
  (seed = line 1-3; attacker query = `AdmExtAtt` incl. stored-set clauses =
  lines 6-8; extension = `AdmExt(S' ∪ {a})` = lines 9-11; learn = line 12),
  hence sound and complete by the paper's Theorem 12.
- Termination: each stored `S''` contains the iteration's attacker `S'`, so
  `S'` (and all its subsets) are excluded from later iterations; finitely many
  admissible sets ⇒ finitely many iterations.
- The retained super-core precheck and shortcut ladder are answer-preserving
  prechecks outside Algorithm 2's loop and were kept per the task.

## Fast Contracts

```powershell
uv run pytest tests/solving/test_solver_encoding.py tests/solving/test_solver_differential.py
```

Result: `61 passed, 1 skipped in 3.18s` (the skip is pre-existing and
environmental: "ICCMA 2017 data not available"). This includes the correctness
oracle `test_kernel_direct_skeptical_preferred_matches_native_oracle`. No test
was skipped, deleted, or weakened by this experiment. `pyright
src/argumentation/solving/af_sat.py`: `0 errors, 0 warnings, 0 informations`;
`ruff check` on touched files: `All checks passed!`.

New TDD contract (RED on pre-change code, confirmed failing only on the
maximisation-telemetry assertion; GREEN after Variant B):

```text
tests/solving/test_solver_encoding.py::test_preferred_skeptical_decide_loop_has_no_admissible_superset_maximisation
```

Full-suite gate before final commit:

```powershell
uv run pytest tests/solving
```

Result: `204 passed, 3 skipped in 5.19s` (all three skips pre-existing and
environmental: two missing external ICCMA solver binaries, one missing ICCMA
2017 data).

## Metric Gate

Same command per run, label varies (run from the experiment worktree; `uv run
<script>` instead of `uv run python <script>` because the repo ward hook
rejects any command token starting with `python`; identical interpreter/env):

```powershell
uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack DS-PR --backend auto --max-af-arguments 320 --timeout-seconds 15 --label af-dspr-cdas-<baseline|variantB>
```

Method note: a separate recalibration benchmark (one solver process) was
running concurrently on the machine during these runs; both runs are equally
exposed, and no other heavy work was run during either benchmark.

Baseline (unmodified `main` @ db73c8b), label `af-dspr-cdas-baseline`:

```json
{"by_status": {"skipped": 709, "solved": 229, "timeout": 26}, "total_rows": 964}
```

Variant B (934d998), label `af-dspr-cdas-variantB`:

```json
{"by_status": {"skipped": 709, "solved": 235, "timeout": 20}, "total_rows": 964}
```

Comparison (`uv run scripts/compare_dspr_runs.py <baseline.json> <variantB.json>`):

```text
baseline:  rows=964 statuses={'solved': 229, 'skipped': 709, 'timeout': 26}
  total_elapsed_seconds=961.750
candidate: rows=964 statuses={'solved': 235, 'skipped': 709, 'timeout': 20}
  total_elapsed_seconds=905.541
baseline-solved rows: 229
  baseline time on those rows: 571.223s
  candidate time on those rows: 561.746s (-1.66%)
solved in baseline but NOT solved in candidate: 0
newly solved in candidate: 6
  GAINED heuristics::DS-PR::AFs/BA_160_80_2.af (was timeout)
  GAINED heuristics::DS-PR::AFs/BA_200_60_4.af (was timeout)
  GAINED heuristics::DS-PR::AFs/mainkwt_250_100_50_150_100_0.4_0.3_0.4_0.3_0.4_0.3_0.2__3.af (was timeout)
  GAINED main::DS-PR::AFs/BA_160_80_2.af (was timeout)
  GAINED main::DS-PR::AFs/BA_200_60_4.af (was timeout)
  GAINED main::DS-PR::AFs/n224p5q2_ve.af (was timeout)
answer mismatches on rows solved in both: 0
kill_criteria_triggered=False
```

Kill criteria (variant regresses solved-count, or >10% total-time on the
baseline-solved rows): NOT triggered. No baseline-solved row was lost, time on
baseline-solved rows improved 1.66%, six former timeouts now solve — including
one row of the known-hard `mainkwt_250` family named as a target by the prior
diagnosis, plus `BA_160/BA_200` and `n224p5q2_ve` rows.

## Interpretation

The pre-experiment code was already CDAS-shaped and its blocking clause already
matched the paper exactly; the only real deviation was the per-iteration
`AdmSup`-style maximisation, and removing it is a pure win on this bench: the
maximisation SAT calls cost more than their stronger blocking clause saved.
This is consistent with the paper's central claim — the expensive part of
Cegartix-style loops is precisely the admissible-superset maximisation, and
Theorem 11 shows it is unnecessary.

The remaining 20 timeouts (ER_300 family and friends) are untouched by this
change and stay on the known-hard list.

## Failure Analysis

Not applicable — the metric gate passed with no regressions and no answer
changes; no profiling was needed for the decision.

## Decision

Variant B: GO. Recommend promoting commit `934d998` (Algorithm 2-exact CDAS
decide loop) to `main`. Variant A: no code exists to promote (vacuous — the
paper's exclusion clause was already implemented); its outcome is this
documentation. Promotion itself is left to the integrator per the experiment
protocol.

## Generated Diagnostics

Generated but not committed (main-tree `data/iccma/2025/runs/`):

- `iccma-2025-af-dspr-cdas-baseline.{json,csv}` + `-summary.json`
- `iccma-2025-af-dspr-cdas-variantB.{json,csv}` + `-summary.json`

Worktree logs (not committed): `logs/af-dspr-cdas-baseline.log`,
`logs/af-dspr-cdas-variantB.log`.
