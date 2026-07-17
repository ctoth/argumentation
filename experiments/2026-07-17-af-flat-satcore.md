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

Verdict: _TBD._

## Interpretation / Decision

_TBD._
