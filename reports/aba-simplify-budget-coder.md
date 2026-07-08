# Coder report: exp 4B — simplify_aba(stable) pre-solve hang (ABA SE-ST)

Branch: `exp/aba-simplify-stable-budget` off main@cc50c4a.
Commits: **8a934dc** (grounded fixpoint via Horn closures), **23c6856**
(reporting-encoding support facts gated on backend), plus a docs commit
(hash in the final summary).
Status: COMPLETE. Both named rows flip. Recommendation: **PROMOTE**.

## Preflight

main@cc50c4a contains the exp-4 routing gate (bc140ba "Gate ABA SE-ST sat
override on sparse-narrow shape") — sequencing requirement met. All three
evidence reports read (aba-sepr-sest-scout, aba-sest-route-coder,
aba-sest-route-verifier). `ward set experiment-worker` done.

## Design decision (before implementing): option (a), justified

Profiled first (`scripts/profile_aba_simplify_stable.py`, quoted):

```
== aba_2000_0.1_5_5_1.aba: atoms=2000 asms=200 rules=5560
  bail-out closures: 0.026s (bails-out=False)
  closure-based grounded prototype: 0.131s |grounded|=152
  _SupportState.from_framework: TIMEOUT >60s (killed after 60.0s)
== aba_2000_0.1_5_5_6.aba: ... prototype 0.124s |grounded|=152; from_framework TIMEOUT >60s
== aba_100_0.1_10_5_7.aba: current=13.962s prototype=0.004s equal=True
```

The hang is the worst-case-exponential `_minimal_supports` enumeration
(aba_support_model.py:108, Cartesian `_combine_supports` over rule bodies up
to 5 antecedents) — the same primitive the 2026-06-29 DC-CO profile measured
at 92.7%. Everything else in `simplify_aba` is polynomial. So this is a
straightforward algorithmic inefficiency: option (a), the best outcome in the
task's ranking. (b) time-budget was rejected as unnecessary once the pass is
worst-case polynomial (a budget would add a config surface and forfeit a
152-of-200-assumption `fixed_in` on expiry); (c) skip was rejected because
the simplification is genuinely valuable on these rows (pins 152/200
assumptions) and a skip would leave the exponential primitive live for every
other simplify caller. Full justification in the experiment record.

## What changed

1. **8a934dc** — `grounded_assumption_set_via_supports`
   (aba_preprocessing.py) rewritten from the support-mask def fixpoint to an
   exact closure-based def fixpoint: per round `attacked_by(S) = {b :
   contrary(b) in Th(S)}` and `a` defended iff `contrary(a) not in
   Th(assumptions - attacked_by(S))` (equivalent by monotonicity of Th,
   one-to-one with the old empty-support / support-intersection cases; at
   most |assumptions|+1 rounds x 2 linear Horn closures). Renamed
   `grounded_assumption_set_via_closures` (the old name described the old
   algorithm); callers updated (`simplify_aba`,
   `AbaIncrementalSolver.grounded_extension`, tests). Existing differential
   oracles (`== native_aba.grounded_extension` on the hand battery + 200
   random frameworks) unchanged and green.
2. **23c6856** — after (1), the named rows STILL timed out (first fixed
   benchmark, preserved as label `aba-simplify-fixed-simplifyonly`: 226/94,
   both named rows 15s). Second call site of the same primitive:
   `_solve_simplified` (aba_asp.py:436) and `_solve_simplified_ds_pr` (:486)
   rebuilt `encode_aba_theory(original)` with default
   `include_supports=True` — `_minimal_supports` on the FULL original
   framework for `support_*` facts the asp/clingo backends never read (the
   encoding there is reporting-only; the residual solve builds its own
   core-facts encoding). Fix mirrors the existing `needs_support_facts`
   gate in `solve_aba_with_backend`: include support facts only for backends
   outside {"asp", "clingo"}.

## TDD

RED (quoted): all three new tests hang under the old code and fail via
`pytest.mark.timeout(60)` with the stack pinned at the exact blow-up —

```
  File ...\aba_support_model.py", line 153, in _add_minimal_support
    if any(existing <= candidate for existing in supports):
+++++++++++++++++++++++++++++++++++ Timeout +++++++++++++++++++++++++++++++++++
```

(commit-1 tests via `_SupportState.from_framework`; commit-2 test via
`_solve_simplified`'s `encode_aba_theory`). Test vehicle:
`_layered_choice_blowup_framework(12)` — 3**12 minimal supports, known
grounded set (36 choice assumptions), `fixed_out={t}`, known stable witness.

GREEN: `3 passed in 0.36s` on the blowup selection;
`tests/structured/aba/test_aba_preprocessing.py` whole file 133 passed.
REFACTOR: rename + module/inline docs updated to describe the closure
fixpoint (no stale "support-mask" references in src/tests/scripts).

## Correctness gates (final commit)

```
uv run pytest tests/solving tests/interop -q
291 passed, 3 skipped in 6.38s
uv run pytest tests/structured -q
1481 passed in 1990.33s
```

Skips are the 3 pre-existing environment skips (ICCMA_AF_SOLVER,
ASPFORABA_SOLVER/ICCMA_ABA_SOLVER, ICCMA 2017 data), unchanged from exp 4.
tests/structured was 1478 at exp-4; +3 = exactly the new regression tests.
(The 1990s wall time vs exp-4's ~280s is machine load; all green.)

## Metric gate (SE-ST slice, 15s cap, 320 ABA rows + 322 AF skipped)

Command = exp 4's slice command with this experiment's labels (note:
`--max-af-arguments 1` is in exp 4's command; the task prompt's inline
command omitted it but requires "Same SE-ST slice command as exp 4" — I used
exp 4's, which only skips AF rows and matches its row set):

```
uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025
  --only-subtrack SE-ST --backend auto --max-af-arguments 1
  --max-aba-assumptions 1000000 --timeout-seconds 15
  --label aba-simplify-<baseline|fixed> --no-progress
```

Baseline ran with the worktree detached at main@cc50c4a (editable-venv
lesson from exp 4); fixed at 23c6856. Compared with exp-4's
`scripts/compare_aba_sest_routes.py` (includes native witness checks).

| run | solved | timeout |
|---|---|---|
| baseline (cc50c4a) | 225 | 95 |
| fixed (23c6856) | **241** | **79** |

### Named rows (the gate's MUST)

| instance | baseline | fixed |
|---|---|---|
| ABAs/aba_2000_0.1_5_5_1.aba | timeout 15.027s | **solved 0.743s** (w=152) |
| ABAs/aba_2000_0.1_5_5_6.aba | timeout 15.014s | **solved 0.681s** (w=152) |

End-to-end probe on the production entry point agrees
(`scripts/probe_aba_sest_named_row.py`): 0.539s / 0.483s, witness_size=152,
solver=clingo_multishot, preprocessing=grounded_reduct_aba.

### Kill evaluation

- Baseline-solved row lost: **0** — pass.
- Answer changed on the 225 commonly-solved: **0** — pass.
- Commonly-solved aggregate elapsed: 348.71s -> 312.82s = **-10.29%**
  (faster) — pass. 10 per-row >10% slowdowns exist, all sub-second rows with
  0.05-0.25s deltas; quiet-machine spot reruns of the 3 worst returned to
  baseline level (0.226s vs 0.226s; 0.315s vs 0.323s; 0.297s vs 0.287s) —
  environmental, not change-caused.
- Named rows flip: **PASS** (the exp-4 miss is closed).

### Other rows

- Gained 16 total (all timeout -> solved): aba_2000_0.1_5_5_{1,3,6,9},
  aba_5000_0.1_5_5_1, aba_500_0.3_5_5_3, aba_2000_0.3_10_10_9, and 9
  abcgen_c5/c7-family rows. All 9 positive gained witnesses natively
  verified as stable extensions by the comparison script's independent
  closure check; the 7 unverified are negative "no stable extension"
  clingo-UNSAT answers with no cheap native check (flagged, same treatment
  as exp 4).
- abcgen c25/c35/c7 dense rows: unchanged row-for-row (expected — their
  bottleneck is completion-SAT/clingo search, not preprocessing).

### Frontier-v1 SE-ST (120s, frozen manifest, branch code)

`scripts/run_frontier_v1.py --subtrack SE-ST --timeout-seconds 120 --label
frontier-v1-aba-simplify-23c6856`: 4 cells -> 2 solved + 2 timeout. The two
solves are exactly the named cells (flagged as deviations from their frozen
`hard` timeout expectation — the desired flips, w=152 each); the two 120s
timeouts are the abcgen hard cells, out of scope (scout verified clingo
also times out on that shape).

## Honest notes

- The task title says "budget"; no budget was implemented. The task's own
  design space ranks "(a) fix the algorithmic blow-up" as the best outcome,
  and the record justifies why (b)/(c) would be strictly worse here.
- The hypothesis under-counted the blow-up sites: fixing simplify alone did
  NOT flip the named rows. The intermediate benchmark
  (`aba-simplify-fixed-simplifyonly` in data/iccma/2025/runs) is preserved
  as the controlled evidence for the second call site, which the metric gate
  then caught — exactly what the gate is for.
- `_minimal_supports` remains worst-case exponential for its remaining
  consumers (DC-* `sat_support_extension`, `support_reference` backend,
  support-facts encodings for non-asp backends). Follow-up filed in the
  record.

## Promotion recommendation

PROMOTE `exp/aba-simplify-stable-budget` (2 code commits + docs commit) to
main. It meets every gate: named rows flip (0.7s at 15s cap; confirmed at
120s frontier replay), +16 solved / 0 lost / 0 answer changes, -10.29%
aggregate on commonly-solved, suites green with 3 new red->green regression
tests pinning both call sites.
