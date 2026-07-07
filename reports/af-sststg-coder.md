# Coder report: AF SST/STG Dvořák fragment shortcuts (exp/af-sststg-shortcuts)

Worker: af-sststg-coder. Isolated worktree
`.claude/worktrees/agent-ac73286e4e44be5a9`, branch `exp/af-sststg-shortcuts`
off main@57da538 (ancestor check passed; `ward set experiment-worker` done).
Main repo tree untouched; nothing pushed or merged; promotion is
recommend-only.

## Commits (in order)

- `2ae940a` Derive SST/STG stable-first and acyclic fragment shortcuts —
  experiment record with the derivations, committed BEFORE implementation.
- `39f6acc` Add stable-first and acyclic fragment shortcuts to SST/STG SAT
  path — RED tests (8 failing) then implementation to green.
- `e4593ee` Extract shared range-maximal task finder and simplify shortcut
  label — refactor step, no behavior change.
- `8078758` Record fast contracts and add SST run comparison script.
- `4f3d057` Record SST shortcut metric gate results and witness verification.

Experiment record: `experiments/2026-07-02-af-sststg-shortcuts.md`
(Hypothesis / Derivations / Single Variable / Fast Contracts / Metric Gate /
Interpretation / Decision — all filled).

## What changed (file:line at `4f3d057`)

`src/argumentation/solving/af_sat.py`:

- `_emit_fragment_shortcut` (:1451) — oracle-free fragment-dispatch trace
  event (SATCheck with elapsed 0).
- `_acyclic_fragment_answer` (:1479) — acyclic dispatch: gated on
  `attacks is None or attacks == defeats` (grounded is defeat-based, kernel
  conflict-freeness is attack-based); answers from
  `grounded_extension(residual)`; fires before kernel construction; trace
  labels `semi_stable_acyclic_grounded` / `stage_acyclic_grounded`.
- `_find_range_maximal_task_extension` (:948) — shared
  prepare/acyclic-dispatch/kernel/range-maximal pipeline;
  `find_semi_stable_extension` (:924) and `find_stage_extension` (:1047) are
  now thin wrappers.
- `RangeMaximalTaskSolver.find_extension` (:1558) — stable-first dispatch
  after the base-feasibility check; `_stable_first` (:1613): constrained
  full-range witness probe, then (constrained queries only) unconstrained
  full-range probe; `(decided, answer)` protocol; runs in the dense-graph
  regime where the bounded probes are disabled — that is the intended new
  behavior. Labels `*_stable_first_witness` / `*_stable_first_global`.
- `_high_range_shortcut` (:1663) — depth-0 (empty missing set) probe removed
  as subsumed by stable-first (once the constrained full-range probe fails it
  can never succeed later, since loop iterations only add blocking
  constraints); `_range_shortcut_utility` → `_high_range_shortcut_utility`
  (:1793); the `*_full_range_shortcut` label no longer exists.

`tests/solving/test_solver_encoding.py` — trace tests moved to cyclic
fixtures with the same assertion strength (the old `a->b` fixtures are now
answered by the acyclic dispatch); new tests: stable-first witness routing,
stable-first global deciding a constrained query as None with the exact
3-check trace, acyclic sem+stg answers (SE / require_in / require_out), the
`attacks != defeats` gate, plus an explicit pin that the old label is gone.

`scripts/compare_af_sststg_runs.py`, `scripts/verify_sststg_se_witnesses.py`
— metric-gate comparison and independent SE-witness verification.

Not touched: range encoding (already Pu 2017's r=x+R+(x)), binary-search
seed machinery, blocking clauses, `GROUNDED_REDUCT_SEMANTICS` (stage is
still excluded; the documented counterexample has a self-loop and is
therefore outside the acyclic fragment).

## Derivations (full text in the experiment record, committed before impl)

1. **Stable-first (SST and STG).** Lemma 0: a full-range base extension of
   the kernel (complete base for SST, conflict-free base for STG) is exactly
   a stable extension (the coverage clause IS the range variable). Claim: if
   one exists, the range-maximal base extensions are exactly the full-range
   ones (any smaller range is strictly dominated). Dispatch matching the
   loop's global-maximality contract: constrained full-range witness → return
   it; else unconstrained full-range SAT → answer None; else fall back.
   Dvořák 2014 p.56 (stb ⊆ sem), Def. 10/Thm. 1 p.59 (k=0
   stable-consistency), depth-0 of CEGARTIX SHORTCUTS (p.61-62).
2. **Acyclic (SST and STG, stage derived separately).** Finite acyclic AF is
   well-founded; Dung 1995 Thm. 30: grounded G is the unique complete
   extension and is stable. Hence sem = {G}; and for stage explicitly:
   G stable ⇒ full-range conflict-free exists ⇒ stg = stb = {G} (no grounded
   reduct involved). Gated on `attacks == defeats`/None. Dvořák 2014 p.57
   (acyclic ⇒ P-c for prf/sem/stg tasks).

## Test outcomes (quoted)

- RED before impl: `8 failed, 4 passed`.
- After impl: `uv run pytest -q tests/solving/test_solver_encoding.py` →
  `61 passed, 1 skipped in 3.06s`.
- `uv run pytest tests/solving` → `224 passed, 3 skipped in 4.82s` (all 3
  pre-existing environmental: ICCMA_AF_SOLVER / ASPFORABA_SOLVER / ICCMA
  2017 data).
- `uv run pytest tests/interop` → `57 passed in 1.88s`.
- After refactor, both suites: `281 passed, 3 skipped in 5.58s`.
- Differential native-oracle property tests (sem/stg) and
  `tests/solving/test_solver_differential.py` unmodified and green.

## Metric gate (before/after)

Command (both sides, same):
`uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025 --only-subtrack DC-SST --only-subtrack DS-SST --only-subtrack SE-SST --backend auto --max-af-arguments 320 --timeout-seconds 15 --label af-sststg-<baseline|shortcuts>`

**Baseline provenance:** the first baseline attempt was contaminated — 185
rows errored with `name '_acyclic_fragment_answer' is not defined` because
my source edits landed while its pool workers were importing the worktree's
editable install. It was discarded and rerun on pristine main (detached HEAD
57da538, clean tree, zero concurrent edits). The candidate run was clean.

| metric | baseline (main 57da538) | candidate (shortcuts) | gate |
| --- | --- | --- | --- |
| rows | 1610 | 1610 | — |
| solved | 576 | 578 | PASS |
| timeout | 44 | 42 | — |
| skipped (cap>320) | 990 | 990 | — |
| lost / gained | — | 0 / 2 | PASS |
| answer mismatches (576 common) | — | 0 | PASS |
| commonly-solved elapsed | 591.04 s | 568.04 s (−3.89%) | PASS (<+10%) |
| solved by subtrack | DC 242 / DS 222 / SE 112 | DC 242 / DS 224 / SE 112 | — |

Gained: `AFs/n256p5q2_e.af` DS-SST on main AND heuristics tracks
(timeout>15.0 → solved ~8.2 s; trace shows only base-feasibility +
stable-first-witness checks).

Named target rows:

| row | baseline | candidate |
| --- | --- | --- |
| ER_200_20_3 DS-SST (main) | timeout>15.0 (15.008 s) | timeout>15.0 (15.020 s) |
| ER_200_20_3 DS-SST (heur) | timeout>15.0 (15.009 s) | timeout>15.0 (15.014 s) |
| ER_300_50_8 DS-SST (main) | timeout>15.0 (15.017 s) | timeout>15.0 (15.016 s) |
| ER_300_50_8 DS-SST (heur) | timeout>15.0 (15.022 s) | timeout>15.0 (15.009 s) |
| crusti DS-SST family (19 × 2 tracks) | skipped cap>320 | skipped cap>320 |

ER_200_20_3 was a 79.6s@120s row in recalibration, so timing out at 15 s on
both sides is expected. All crusti DS-SST instances exceed this gate's
320-argument cap on both sides — no claim possible about them here.

STG: the ICCMA 2025 data root has no STG subtrack rows
(`DEFAULT_AF_SUBTRACKS` has no `-STG`, no STG `.results` dirs); stage is
covered by the test suite only. Stated in the experiment record.

SE witness audit: 16 commonly-solved SE-SST rows changed witness (expected —
extra probes change which model Z3 returns).
`scripts/verify_sststg_se_witnesses.py` independently verified BOTH sides of
all 16 (conflict-free + complete polynomially, range-maximality via one SAT
call each): 32/32 OK, `failures: 0` (7 stable witnesses, 9 genuinely
non-stable range-maximal ones from the unchanged fallback loop).

Shortcut firing over the candidate run: `stable_first_witness` 452,
`stable_first_global` 74, `acyclic_grounded` 21 (vs `high_range_shortcut`
1248, `max_range_at_least` 641).

## Kill-criteria evaluation

- Baseline-solved row lost: **0** — not triggered.
- Baseline-solved answer changed: **0 of 576** — not triggered (SE witness
  changes are not answer changes; all verified valid).
- Total-time regression on baseline-solved rows: **−3.89%** (improvement;
  threshold +10%) — not triggered.

## Promotion recommendation

**Recommend promotion** of `exp/af-sststg-shortcuts` (2ae940a..4f3d057).
Sound by derivation, correct by differential/property gates, and a
strict-improvement metric gate (+2 solved rows, −3.89% time, 0 lost,
0 answer changes). Residual opportunities intentionally out of scope: the
binary-search loop dominating ER_300/ER_200 DS-SST timeouts, and any
stage-specific bench evidence (no STG bench rows exist).
