# af-dspr-cdas coder report

Task: bring the CDAS-style DS-PR solver in line with Thimm/Cerutti/Vallati
IJCAI-21 as two separately committed, separately measured variants
(prompts/af-dspr-cdas-coder.md). Branch: `exp/af-dspr-cdas` in isolated
worktree `.claude/worktrees/agent-ab87306436d1fb3e1`.

## Verdict

- **Variant A: STOPPED as vacuous** — the paper's exclusion clause is already
  implemented, verbatim, by the existing `learn_witness_region`. Derivation
  below. No code change exists to commit or measure for it.
- **Variant B: GO** — committed as `934d998`. +6 solved (229 → 235), −6
  timeouts (26 → 20), −1.66% time on baseline-solved rows, zero lost rows,
  zero answer changes. Kill criteria not triggered.
- Recommendation (recommend-only): promote `934d998` to `main`.

## Before/after table (DS-PR, cap 320, 15s timeout, backend auto)

| Run | Label | Solved | Timeout | Error | Skipped | Total elapsed (row sums) | Time on the 229 baseline-solved rows |
|---|---|---|---|---|---|---|---|
| Baseline (`main` @ db73c8b) | af-dspr-cdas-baseline | 229 | 26 | 0 | 709 | 961.750 s | 571.223 s |
| Variant B (`934d998`) | af-dspr-cdas-variantB | 235 | 20 | 0 | 709 | 905.541 s | 561.746 s (−1.66%) |

Newly solved under Variant B (all former timeouts): `BA_160_80_2.af` (main +
heuristics), `BA_200_60_4.af` (main + heuristics),
`mainkwt_250_100_50_150_100_0.4_0.3_0.4_0.3_0.4_0.3_0.2__3.af` (heuristics),
`n224p5q2_ve.af` (main). `mainkwt_250` is one of the timeout families the task
targeted. Rows lost: none. Answer mismatches on rows solved in both runs: 0
(checked per-row by `scripts/compare_dspr_runs.py`).

Kill-criteria evaluation: "regresses solved-count" — no (gains 6, loses 0);
">10% total-time on baseline-solved rows" — no (−1.66%). `kill_criteria_triggered=False`.

## Why Variant A is vacuous (the load-bearing finding)

Paper (read from `papers/Thimm_2021_SkepticalReasoningPreferredSemantics/pngs/`
pages 002–003, pp. 2071–2072): `AdmExtAtt(AF, S, {S_1..S_n})` returns an
admissible attacker `S'` with condition (3) `S' ⊄= S_i for i = 1..n` — the
attacker must not be a **subset** of any stored extended set; line 12 stores
`S''` "to avoid considering subsets of S'' later".

Existing clause (af_sat.py `learn_witness_region`):
`Or(attacker_vars[a] for a in arguments − extension)`. Its negation is exactly
`attacker ⊆ extension`. So the "weak some-outsider clause" **is** the paper's
condition (3). There is no stronger paper form to adopt. The scout's proposed
mirror of `AfSatKernel.exclude_exact_extension` (af_sat.py:287) is strictly
*weaker* (forbids only the exact set, not its subsets) and is not the paper's
form. Per the task's own conditional ("if the paper's loop requires a
different exclusion form than Variant A, implement exactly the paper's form"),
the paper's form is what was already there; Variant A therefore has no
implementable content and was stopped per the per-variant stop rule, with this
derivation as its report.

The only true deviation from Algorithm 2 was the `AdmSup`-style maximisation
(`_grow_preferred` at the old af_sat.py:761) — exactly Variant B's variable.
Note the maximised witness gives a per-iteration *stronger* blocking clause
(supersets block more attackers), so Variant B was a genuine trade-off
question, resolved empirically in favour of the paper.

## Variant B soundness re-derivation (done before coding, as required)

- `_complete_extension(required_in=X)` is an existence-faithful
  `AdmExt(AF, X)`: every admissible set extends to a complete extension
  containing it (Dung's fundamental lemma) and complete extensions are
  admissible; the returned complete extension is a valid nondeterministic
  `AdmExt` witness.
- With the maximisation removed, the decide loop is Algorithm 2 verbatim
  (lines 1–3 seed; 6–8 attacker/None→YES; 9–11 extend/None→NO; 12 store) —
  sound and complete by the paper's Theorem 12.
- Termination: each stored witness `S'' ⊇ attacker`, so each iteration's
  attacker (and its subsets) is excluded afterwards; finitely many admissible
  sets ⇒ finitely many iterations.
- Retained per the plan: shortcut ladder, `PreferredSuperCoreSolver` precheck,
  `simplify_af` preprocessing, `learn_witness_region` clause form,
  `_grow_preferred` for its other callers (find_preferred_extension paths).

## TDD

- RED: added
  `tests/solving/test_solver_encoding.py::test_preferred_skeptical_decide_loop_has_no_admissible_superset_maximisation`
  — AF `{a,b,c,q}` with `a↔b, a→c, b→c, c→q` (preferred `{a,q}`,`{b,q}`;
  DS-PR(q)=True; no shortcut fires; super-core empty; loop runs ≥2 iterations
  with successful extensions). Confirmed failing on unmodified code:
  `FAILED ... AssertionError: assert 'preferred_skeptical_extend_attacker_maximal' not in [...]`
  (`1 failed, 56 deselected in 2.14s`) — failing only on the maximisation
  assertion; the decide-True and extend-attacker-present assertions held.
- GREEN: removed the `_grow_preferred` call + its dead `None` check from
  `PreferredSkepticalTaskSolver.decide`; targeted test `1 passed`.
- REFACTOR: class docstring now documents the exact Algorithm 2
  correspondence and the answer-preserving prechecks.

## Test outcomes (quoted)

- Per-variant gate: `uv run pytest tests/solving/test_solver_encoding.py
  tests/solving/test_solver_differential.py` → `61 passed, 1 skipped in 3.18s`
  (skip is pre-existing/environmental: "ICCMA 2017 data not available").
  Includes the oracle
  `test_kernel_direct_skeptical_preferred_matches_native_oracle`.
- Final full gate: `uv run pytest tests/solving` → `204 passed, 3 skipped in
  5.19s`; all three skips pre-existing/environmental (`set ICCMA_AF_SOLVER
  ...`, `set ASPFORABA_SOLVER or ICCMA_ABA_SOLVER ...`, `ICCMA 2017 data not
  available`). No test skipped, deleted, or weakened by me.
- `uv run pyright src/argumentation/solving/af_sat.py` → `0 errors, 0
  warnings, 0 informations`. `uv run ruff check` on touched files → `All
  checks passed!`.

## Method notes

- Benchmark command per run (only the label differed), run from this worktree:
  `uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025
  --only-subtrack DS-PR --backend auto --max-af-arguments 320
  --timeout-seconds 15 --label af-dspr-cdas-<baseline|variantB>`.
  Deviation from the plan's literal text: the word `python` is dropped because
  the repo ward rule `python/uv-not-python.yaml` denies any command token
  starting with `python` — including `uv run python ...` (denial text: "Use
  `uv run python` instead of bare python. Run: ward allow bare-python"). I did
  NOT run `ward allow` (permission change, not authorized); `uv run <script>`
  uses the same interpreter/env.
- A separate recalibration benchmark (one solver process, Q's) ran
  concurrently during BOTH runs; exposure is symmetric. I ran no other heavy
  work during either benchmark window.
- Baseline was run on unmodified code before any edit; the RED→GREEN flip
  after the src edit demonstrates the uv-managed env picks up source changes,
  so the variantB run exercised commit `934d998`'s code.
- Run artifacts land in the main tree's `data/iccma/2025/runs/` (that is what
  `--root` points at, per the plan); they are data outputs, not commits.
- Setup notes: repo has no `master`; branched `exp/af-dspr-cdas` off `main`
  (db73c8b), the integration branch — intent preserved. `ward set
  experiment-worker` succeeded: `ward: phase → experiment-worker`.
- Scout citations verified before work: `PreferredSkepticalTaskSolver` :699,
  `_grow_preferred` call :761, `learn_witness_region` :1150,
  `exclude_exact_extension` :287.

## Commits (on `exp/af-dspr-cdas`, this worktree only)

- `934d998` Remove AdmSup maximisation from DS-PR CDAS decide loop
  (src/argumentation/solving/af_sat.py, tests/solving/test_solver_encoding.py)
- `ae9bb15` Record AF DS-PR CDAS alignment experiment result
  (experiments/2026-07-02-af-dspr-cdas-blocking.md,
  scripts/compare_dspr_runs.py, reports/af-dspr-cdas-coder.md)
- Working-tree leftovers: only untracked benchmark logs
  (`logs/af-dspr-cdas-*.log`), intentionally uncommitted.

## Promotion recommendation (recommend-only)

Promote `934d998` to `main`. It is a small, paper-faithful deletion with a
telemetry contract test, no oracle/differential regressions, strictly better
DS-PR bench results, and it removes SAT work from the hot loop. Nothing else
on this branch needs promotion decisions beyond docs/tooling
(`scripts/compare_dspr_runs.py`, experiment record).

Residuals for a future slice: the remaining 20 DS-PR timeouts (ER_300-family
dominated) are unaffected by this change; scout risks #3 (two unshared Z3
solvers) and #4 (no SCC on the acceptance path) remain open.
