# ICCMA 2023 S2 Operational Scout — support-free/core-fact preprocessing

Date: 2026-07-11

Status: **KILL at triage.** Read-only development-corpus scout; no production
slice, benchmark gate, commit, or holdout access.

## Decision

The candidate does not survive. Its two proposed operational mechanisms are
already in the measured baseline:

1. The production ASP/Clingo route already emits
   `flat_aba_core_facts` with `include_supports=False`; it does not materialize
   `_minimal_supports` facts.
2. Stable and preferred queries already run the grounded ABA reduct whenever
   that reduct is non-trivial, solve the residual through the same core-fact
   multishot Clingo owner, and lift the result.

The earlier archaeology characterization of S2 as a dormant single-extension
route was therefore wrong. There is no support-free/core-fact route change left
to make. More importantly, the existing preprocessing is a no-op on every
development row that supplies campaign headroom: both 600-assumption instances,
and therefore all three baseline timeout rows, retain the complete search
problem.

This is not a promotion judgment. It is a cheap campaign kill: the candidate
cannot reduce the dominant preferred-growth cost because the baseline already
contains it and its residual invariant does not move on the hard rows.

## Frame and bottleneck used

- Current checkout: `main` at `56a946eed4845f3190a4e6be9200cc834c1b0e3a`.
  Tracked files were clean before measurement; unrelated untracked files were
  present and untouched.
- Frozen development population:
  `experiments/iccma2023-frame/population-dev.json`, 12 ABA instances crossed
  with `{SE-ST, SE-PR}` = 24 rows.
- Frozen baseline: 21/24 solved in each of three repeats at 10 seconds per row.
  The three timeouts are SE-ST and SE-PR on
  `aba_2000_0.3_10_10_0.aba`, plus SE-PR on
  `aba_2000_0.3_10_10_1.aba`.
- Existing real-worker py-spy evidence for the hard preferred row has 928
  samples in `clingo.Control.solve`, versus 27 in initial grounding, 19 in
  program addition, and 3 in refinement grounding. The direct preferred probe
  reports the operational shape `4 solver calls / 1 outer / 3 inner / 3
  refinements`; the later configuration triage repeated the same shape for
  every successful arm. Search inside preferred growth, not support
  materialization or grounding, is the live cost.

The sealed holdout JSON was neither read nor run.

## Source-path verification

At the current checkout:

- `src/argumentation/structured/aba/aba_asp.py:115-133` invokes
  `simplify_aba` for gated stable/preferred semantics and routes a non-trivial
  reduct through `_solve_simplified`.
- `aba_asp.py:146-147` sets `needs_support_facts = backend not in {"asp",
  "clingo"}`. Thus every Clingo solve calls `encode_aba_theory(...,
  include_supports=False)`.
- `aba_asp.py:170-181` sends stable/preferred single-extension work to the
  multishot solver using that encoding.
- `aba_asp.py:387-472` recursively solves a non-trivial residual with
  `simplify=False`, then lifts it. The residual solve builds its own core-fact
  encoding.
- `src/argumentation/structured/aba/aba_incremental.py:322-344` adds those facts
  plus the completion module once per control. Preferred single-extension then
  uses `enumerate_preferred(limit=1)` and its grow-to-maximal loop.

Git blame places the no-support Clingo gate at commit `37148eda` (2026-05-16)
and the multishot single-extension route at `466d38da` (2026-05-12), both well
before the frozen 2026-07-11 baseline. This is not a recently landed change that
the baseline missed.

## Finite cheap measurement

### Operational invariant

For every development instance, measure the semantics-preserving grounded
reduct without solving:

- `fixed_in`, `fixed_out`;
- residual assumptions and rules;
- whether the residual is strictly smaller than the parsed original.

Survival condition: at least one of the two 600-assumption headroom instances
must have a strict residual reduction (even one assumption or rule would pass
this deliberately permissive first gate). If neither hard instance shrinks,
preprocessing cannot reduce the assumption search space or rule surface seen by
the profiled preferred-growth loop. Separately, encoding metadata/source must
show that support-free/core-fact execution is not already the baseline. Failure
of either condition kills the candidate before a benchmark.

This is finite, deterministic, and directly tied to the bottleneck. It does not
use wall-clock success as a proxy.

### Commands

Baseline metadata was inspected with `jq` from:

```text
data/iccma/2023/runs/iccma-2023-frame-dev-baseline-run1-2026-07-11.json
```

Each of the 12 paths in `population-dev.json` was then measured with the
existing bounded probe (path varied only):

```text
uv run tools/aba_iccma_probe.py \
  data/iccma/2023/extracted/instances/<relative_path> \
  --mode simplify-stable --timeout-seconds 5
```

Stable and preferred use the same `simplify_aba` reduct implementation and the
same gated semantics set, so a duplicate preferred run would not produce a
different residual. All 12 correct-path probes returned `status=success`; each
completed in 0.167-0.707 seconds. An initial invocation against the wrong local
corpus path failed closed with `FileNotFoundError`; it contributed no data and
was rerun against the resolved `extracted/instances` paths above.

### Results

| Development pair | Original assumptions | Fixed IN/OUT by instance | Residual assumptions | Rule reduction | Result |
|---|---:|---|---|---|---|
| `aba_100_0.1_*_{0,1}` | 10 | `9/1`, `6/4` | `0`, `0` | `6.6%`, `21.3%` | non-trivial |
| `aba_100_0.3_*_{0,1}` | 30 | `0/0`, `0/0` | `30`, `30` | `0%`, `0%` | no-op |
| `aba_500_0.1_*_{0,1}` | 50 | `44/6`, `41/6` | `0`, `3` | `6.0%`, `6.5%` | non-trivial |
| `aba_500_0.3_*_{0,1}` | 150 | `0/0`, `0/0` | `150`, `150` | `0%`, `0%` | no-op |
| `aba_2000_0.1_*_{0,1}` | 200 | `157/43`, `160/40` | `0`, `0` | `11.0%`, `10.6%` | non-trivial |
| `aba_2000_0.3_*_{0,1}` | 600 | `0/0`, `0/0` | `600`, `600` | `0%`, `0%` | no-op |

Quantified prevalence:

- Non-trivial grounded reduct: **6/12 instances (50%)**, exactly the six
  low-density `0.1` instances. Because every instance is crossed with two
  subtracks, baseline metadata tags preprocessing on **12/24 rows (50%)**.
- No-op reduct: **6/12 instances (50%)**, exactly the six `0.3` instances.
- Headroom coverage: **0/2 hard 600-assumption instances**, hence **0/3 baseline
  timeout rows**, receive any residual reduction.
- Core-fact encoding: all **21 completed baseline rows** explicitly report
  `encoding=flat_aba_core_facts`. The three outer-process timeouts cannot
  serialize solver metadata, but they traverse the same source-guaranteed
  Clingo route; the hard preferred row's later completed 15-second probe also
  reports the same core-fact path and `4/1/3/3` growth shape.

The preprocessing is useful on easy low-density rows, but those rows already
solve in roughly 0.3-1.7 seconds and cannot increase the campaign's solved-count
metric. On the only rows that can increase 21/24, the residual is identical to
the original framework.

## Why this predicts no material reduction

The candidate has no mechanism left to change the profiled cost:

1. Removing materialized supports cannot help because the live Clingo baseline
   never materializes them.
2. Existing grounded preprocessing cannot help the headroom rows because it
   fixes zero assumptions IN or OUT and returns a no-op reduct.
3. Consequently the preferred row still enters the same four-call,
   three-inner-refinement growth shape over all 600 assumptions and the same
   core rule surface. Existing py-spy evidence places the cost in those solves,
   not in program addition.

A new transformation capable of shrinking the `0.3` frameworks would be a new
semantic hypothesis, not S2 as described. It would require its own derivation,
counterexamples, fast semantic contract, and preregistered operational gate.
This scout does not broaden the killed candidate into that work.

## Verdict

**KILL.** Survival gate result: **0/2** hard instances reduced; core-fact
non-materializing execution is already **100% of the applicable Clingo route**.
Expected solved-count gain from the candidate as stated is **0 rows**. Do not
create a production source slice, run the sealed holdout, or spend a full
experiment slot on it.
