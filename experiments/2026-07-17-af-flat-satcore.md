# sat-core engine routing on flat AF SAT paths (completes exp 7A)

Date: 2026-07-17
Branch: `exp/af-flat-satcore` (from `main` @ `f4b8eac`).
Prior-art record: `experiments/2026-07-17-af-flat-satcore-prior-art.md`.
Supersedes/completes: `exp/af-satcore-flat` @ `3973193`
(`experiments/2026-07-10-af-satcore-flat.md`, "Decision: TO BE FILLED").

Status: **preregistered before implementation.** Results filled after the gate.

## Framing (from campaign manager)

Goal metric is full-corpus ICCMA solve count, not the 30-cell frontier proxy.
The prior 74-cell probe's off-gate TO→solved wins (ER_300_20_2 dc_co,
ER_400_60_3 se_pr) are census-level gains at the real 600 s+ budget. No
frontier flip is predicted or claimed. This lands the safe, answer-preserving
routing and closes the stalled record.

## Hypothesis

Routing the FLAT (non-cone) AF SAT acceptance/single-extension paths through
the Z3 `Tactic('sat')` sat-core engine — exactly per the `exp/af-satcore-flat`
per-op derivation — converts off-gate ER timeouts to solved without regressing
any currently-solved row and without changing any answer.

## Single variable

Engine selection for the flat (non-cone) dispatch only. Per op family,
following the committed 74-cell A/B probe:

| op family | route | reason (probe) |
|---|---|---|
| complete finder (DC-CO, DS-CO, SE-CO) | **sat-core** unconditional | win-or-tie every cell; ER_300_20_2 dc_co TO→87.6s |
| preferred witness (DC-PR, SE-PR; `find_preferred_extension`) | **sat-core** unconditional | win-or-tie; ER_400_60_3 se_pr TO→56.1s; no small-graph CDAS pathology (single kernel) |
| CDAS skeptical preferred (DS-PR; `is_preferred_skeptically_accepted`) | **sat-core iff `len(defeats) >= PREFERRED_CONE_MIN_DEFEATS` (15 000)** | BA_160_80_2 0.42s→11.55s (27×) below; win-or-tie from ~9 901 up |
| stable (DC-ST, DS-ST, SE-ST) | **smt** (unchanged) | no ≥1.1× win, one 1.18× loss |
| ideal | **smt** (unchanged) | 1.54× loss small, both-TO at scale |
| semi-stable / stage | **excluded by construction** | range-maximal loop uses `PbGe`/`PbEq`; `Tactic('sat')` cannot express them. **This is why ER DS-SST can never take this path.** |

Explicit callers are untouched: the SCC-cone path passes `engine="sat-core"`
directly to the finders; every other explicit-engine caller is byte-for-byte
unchanged. Only the flat auto/sat dispatch gains the routing.

## Operational contracts (committed failing/passing BEFORE implementation)

**(a) Engine-resolution + telemetry.** A pure `_flat_sat_engine(kind, framework)`
returns the table above (unit-tested per row incl. the CDAS threshold both
sides). Telemetry: a flat complete/preferred acceptance emits SAT-check events
with `engine == "sat-core"`; a flat stable acceptance emits `engine == "smt"`.
RED now (`_flat_sat_engine` absent; `SATCheck` has no `engine` field).

**(b) Answer preservation (oracle equivalence).** Auto (sat-core-routed) ==
native enumerator answer over random multi-SCC AFs for DC-CO/DS-CO,
DC-PR/DS-PR, SE-CO/SE-PR. Must be GREEN (zero disagreements — already measured
on the prior 74 cells; re-asserted on random inputs). Existing DS-PR/complete
fixtures stay GREEN.

**(c) Stable/ideal keep smt.** Telemetry guard: flat stable and ideal finders
construct `smt` kernels. RED now (no engine telemetry).

**(d) Triage gate.** Reproduce, on current main at `--jobs 1`, the two off-gate
TO→solved flips (ER_300_20_2 dc_co: smt TO → sat-core solved; ER_400_60_3
se_pr: smt TO → sat-core solved). If neither reproduces, the win evaporated on
`f4b8eac` → STOP and record NO-GO.

## Metric gate

1. Triage probe reproduces ≥1 off-gate flip (else STOP/NO-GO).
2. Contracts (a)(c) RED→GREEN; (b) GREEN; full pytest passes.
3. Regression guard: DS-PR cap200-class t15 slice — no lost rows, no answer
   changes, no >10% common-row time regression (predicted unchanged; verified).
4. Off-gate flips reproduced via the shipped routing (not just the probe).

## Results

### Triage probe (current main f4b8eac, --jobs 1) — off-gate flips reproduce

| cell | op | smt | sat-core | prior (b70a1d6) |
|---|---|---|---|---|
| ER_300_20_2 (301 args / 8 895 defeats) | dc_co | **TIMEOUT 121.1s** | **solved 82.5s** (answer NO) | TO → 87.6s |
| ER_400_60_3 (401 args / 48 036 defeats) | se_pr | (prior TO) | **solved 52.0s** (empty pref. ext.) | TO → 56.1s |

Both flips reproduce on current main; the smt half of ER_300_20_2 dc_co
confirmed TIMEOUT at the 120 s check budget. Triage gate MET.

### Shipped-path flips (production `solve_dung_acceptance`/`_single_extension`, backend="auto")

| cell | task | answer | time | before |
|---|---|---|---|---|
| ER_300_20_2 | DC-CO | False | **73.0 s** | smt TIMEOUT |
| ER_400_60_3 | SE-PR | empty ext | **50.6 s** | smt TIMEOUT |

The routing lands through the real dispatch (auto → cone returns None on these
single-SCC frameworks → flat dedicated solver → sat-core), not only the probe.

### Contracts + tests

- Contract module `tests/solving/test_af_satcore_flat_routing.py`: **45 passed**
  (engine predicate per row incl. CDAS threshold both sides; `engine` telemetry
  == sat-core for complete/preferred, smt for stable; native-oracle answer
  equivalence for DC/DS-CO, DC/DS-PR, SE-PR).
- `tests/solving tests/core`: **1176 passed, 3 skipped** (skips pre-existing).
- pyright on `af_sat.py` + `solver.py`: 0 errors.
- Full suite (`pytest -q --timeout=600`, excluding the pre-existing Probe 7
  collection error): **3136 passed, 1 failed, 4 skipped, 1 xfailed** in 366 s.
  Both non-passing items are **pre-existing on baseline f4b8eac** (verified
  failing identically there), unrelated to this change:
  - `test_aba_cadical2_eager_arc_contract.py` — collection error, Probe 7 red
    contract (`scripts.probe_iccma2023_cadical221_eager_arc` absent).
  - `test_decomposed_prefsat_page_image_contract` — asserts a paper page image
    (`papers/Cerutti_2013_.../pngs/page-008.png`) exists; a `papers/` fixture
    gap, nothing to do with af_sat/solver.

### Regression guard (DS-PR cap200 t15, --jobs 1, baseline f4b8eac vs after dd778ff)

| | solved | skipped | lost | gained | answer changes |
|---|---|---|---|---|---|
| baseline | 81 | 561 | — | — | — |
| **after** | **81** | 561 | **0** | **0** | **0** |

Common-row total time **−4.0%** (after faster; environmental, census worker
shared the machine). Only **2 of 81** solved rows have ≥15 000 defeats and thus
switch smt→sat-core; both are ties with identical answers
(afinput…yyy02 0.294→0.295 s `false==false`; …yyy09 0.308→0.318 s `true==true`).
The worst per-row delta (+10.8 %, 0.635→0.703 s) is on a 235-defeat row that
**stays on smt** (byte-identical code path) — pure noise, not the change. No
lost rows, no answer changes, no aggregate regression → **gate MET**.

Verdict: **GO** (coverage/robustness win; no frontier flip, as prior evidence
predicted).

## Interpretation / Decision

**GO — promote-recommend (recommend-only).** The change is answer-preserving
(45 contracts + 1176 solving/core + full-suite pass; the two exceptions are
pre-existing) and lands real full-corpus TO→solved gains on single-SCC families
the SCC-cone routing can never reach: ER_300_20_2 DC-CO and ER_400_60_3 SE-PR
flip from smt timeout to sat-core solved (73.0 s / 50.6 s through the shipped
`backend="auto"` dispatch). At the real ≥600 s ICCMA budget these are census
solve-count gains. The t15 DS-PR slice is unchanged (0 lost / 0 answer changes /
−4 % time), confirming the size gate protects small CDAS loops.

Honest scope, per prior evidence: **no frontier-manifest flip is claimed or
observed** — the ER DS-PR frontier cells stay both-TO under both engines, and
DS-SST can never take this path (semi-stable/stage range-maximality uses
pseudo-Boolean `PbGe`/`PbEq` that `Tactic('sat')` cannot express). This is a
coverage/robustness win, not a headline frontier move.

**Supersedes `exp/af-satcore-flat`** (`3973193`, "Decision: TO BE FILLED"): this
record completes that stalled experiment with the same routing derivation,
implemented, gated, and decided. That branch's record should be marked
superseded by this one.

### Next (NOT done here — Wave 2, needs a Q budget checkpoint)

The super-core SAT-search levers named by the candidate-A kill
(cross-iteration clause retention; grounded-lower-bound CEGAR priming) are
explicitly out of scope and not started.
