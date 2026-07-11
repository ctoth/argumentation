# ICCMA 2023 Probe 7: CaDiCaL 2.2.1 on the Eager-Arc Stable CNF

Date: 2026-07-11

Status: **preregistered; capability not established; Probe 7 not consumed**.

Preregistration base: `50b7b0f22ce039aa0d9f9e6039c17f3bb7464ced`

This record reconciles the fresh read-only candidate inventory and adversarial
review. The adversary's `rel-2.1.3` recommendation is superseded here: the
candidate is pinned to CaDiCaL tag **`rel-2.2.1`**, commit
**`4198d817d0dcde5b1240eefbff70b555b7df2af9`**, the latest identified 2.x
release. No floating branch, newer major release, or other 2.x commit is the
candidate.

## Decision this probe can change

Probe 7 answers one question:

> Can direct CaDiCaL 2.2.1 prove the unchanged current eager-arc, one-shot CNF
> UNSAT for the sole SE-ST development timeout within the frozen cap, where
> Glucose4 still times out?

A negative result kills this exact engine/formula pairing. A positive result is
directional triage evidence only. The production route threshold currently
excludes this 600-assumption row, so a positive diagnostic does **not**
authorize a production change, promotion, holdout access, or a full-development
run. It authorizes only a separately preregistered routing experiment.

## Preregistration (frozen before capability or probe work)

### Hypothesis and single variable

**Hypothesis:** a pinned direct CaDiCaL 2.2.1 engine can turn the current
Glucose4 timeout on the one reachable SE-ST development row into an independently
validated one-shot UNSAT result under the campaign cap.

**Single variable:** solver engine only.

- Control: PySAT `glucose4`.
- Candidate: direct native CaDiCaL `2.2.1`, tag `rel-2.2.1`, commit
  `4198d817d0dcde5b1240eefbff70b555b7df2af9`.
- Formula: the unchanged current eager-arc stable CNF.
- Execution shape: eager path, exactly one solver call, no refinement, and no
  lazy fallback.

Frozen unchanged between control and candidate: parser result, semantic-to-SAT
variable numbering, ordered clauses and signed literals, assumptions, phase
vector, eager-cycle enumeration, worker/process path, witness interpretation,
and timeout accounting. There is no solver-option/configuration sweep, callback,
encoding change, preprocessing experiment, portfolio, seed search, or routing
change. No CaDiCaL option-setting call is allowed; the pinned build's default
configuration is used and recorded. In particular, there is no IPASIR-UP or
Python per-assignment callback.

### Sole permitted development instance

Only this row may be used:

`data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_0.aba`

Subtrack: `SE-ST`. Jobs: `1`.

No holdout row, full development population, SE-PR row, other hard row, or
already-solved guard row may be opened or executed by Probe 7.

### Exact identity contract

The diagnostic must serialize and SHA-256 hash the following values separately
for Glucose4 and CaDiCaL:

1. `formula_sha256`: canonical JSON containing the instance identity, variable
   count, ordered assumption literals, clause count, the three hashes below,
   eager-path flag, solver-call count, refinement count, and fallback count;
2. `variable_map_sha256`: the ordered semantic-variable-key to positive integer
   variable-number mapping;
3. `clause_stream_sha256`: every clause in original order, with signed integer
   literals in original order and a terminating `0` per clause;
4. `phase_vector_sha256`: the complete ordered signed phase-literal vector
   passed to the engine.

The candidate is valid only when all four hexadecimal hashes are byte-for-byte
identical to the paired Glucose4 control hashes. Reordering variables, clauses,
literals, assumptions, or phases is a formula change and an immediate kill,
even if the formulas appear equisatisfiable.

Every invocation must also report:

- `engine_api`, `engine_version`, and pinned source commit;
- variables, clauses, assumptions, and phase count;
- `solver_calls == 1`;
- eager path selected;
- `refinements == 0` and lazy fallback not entered;
- build time and solve time;
- native `conflicts`, `decisions`, `propagations`, and `restarts` statistics as
  available nonnegative integers.

Missing required identity or statistics telemetry fails closed.

### Semantic authorities

The engine never owns ABA or SAT semantics. These independent authorities are
exact and frozen:

1. Existing bounded ABA stable fixtures must agree with
   `support_extensions`; founded-witness, no-extension, and
   raise-on-unfounded-model behavior remain active.
2. A returned SAT model is checked outside CaDiCaL by evaluating every signed
   literal in every emitted clause against the complete assignment. Model
   access must obey IPASIR signed-literal semantics: for each assigned variable
   `v`, `val(v)` and `val(-v)` are opposite signed answers for the queried
   literals. Taking `abs(lit)`, collapsing the sign, or treating `val(-v)` as a
   query for `v` is forbidden.
3. Every claimed UNSAT result is accepted only when an independent proof
   checker—not CaDiCaL and not the diagnostic's status parser—validates the
   emitted proof against the exact hashed DIMACS formula. The proof checker
   identity, version/commit, command, exit status, and proof hash are recorded.
4. The prior independently recorded base-CNF UNSAT result establishes the
   expected hard-row answer. A SAT answer is therefore an immediate semantic
   kill even if its returned assignment passes local clause checking.

UNKNOWN, a process exit code without a parseable solver status, a missing or
invalid proof, a partial model, a crash, or a timeout is not UNSAT.

## Capability gate: before Probe 7 consumption

Capability work runs without the ICCMA target and does not consume the probe.
Use a temporary source checkout/build and a minimal diagnostic driver. All of
the following must pass once:

1. Source identity is exactly `rel-2.2.1` /
   `4198d817d0dcde5b1240eefbff70b555b7df2af9`; runtime reports exactly `2.2.1`.
2. Direct clause addition, assumptions, signed `phase(lit)`, termination,
   solve status, signed `val(lit)`, proof tracing, and the four required native
   statistics are callable from the real candidate process.
3. A trivial SAT fixture returns a complete model whose signed-literal `val`
   behavior and every clause are independently checked.
4. A trivial UNSAT fixture returns UNSAT and its emitted proof is accepted by
   the independent proof checker against the exact fixture CNF.
5. Both fixtures finish under a 5-second outer process cap, and no callback or
   option/configuration change is installed.

If any capability item is absent or ambiguous, status is exactly
**`blocked before probe; dependency/API capability absent`**. Probe usage stays
**6 / 8**. Do not open the ICCMA target, substitute another CaDiCaL version, or
count a build/API failure as a consumed or failed probe.

## Deterministic executable operational contract: red first

Before implementing the diagnostic engine, add and commit this normally running
contract red:

```powershell
uv run pytest -q `
  tests/structured/aba/test_aba_cadical2_eager_arc_contract.py `
  --timeout=30
```

The red contract must fail on the current Glucose4-only baseline and assert all
of the following deterministically:

- `engine_api == "cadical-direct"`;
- `engine_version == "2.2.1"` and source commit equals the full pinned SHA;
- Glucose4 and candidate `formula_sha256`, `variable_map_sha256`,
  `clause_stream_sha256`, and `phase_vector_sha256` are identical;
- eager path, exactly one solve, zero refinement, and no lazy fallback;
- conflicts, decisions, propagations, and restarts are present and are
  nonnegative integers;
- the exact ABA fixture authority is `support_extensions`;
- SAT uses the independent complete-clause model validator with correct signed
  `val` semantics;
- UNSAT uses the named independent proof checker against the exact hashed CNF.

Semantic equivalence alone is insufficient. The contract must be committed red
before the engine/driver implementation; a test written after the engine delta
invalidates the probe.

## Allowed diagnostic ownership surface

Prefer a temporary CaDiCaL checkout/build plus diagnostic-only repository
surfaces:

- the temporary pinned native source/build and minimal C++ driver outside the
  repository;
- `tests/structured/aba/test_aba_cadical2_eager_arc_contract.py`;
- `scripts/profile_abcgen_stable.py` or one narrowly owned Probe 7 diagnostic
  script if the existing script cannot emit the frozen manifest without
  changing production ownership;
- `experiments/artifacts/2026-07-11-probe-7-*.json` and recorded proof/profile
  evidence.

No file under production `src/` is allowed. No new production engine wrapper,
interface, helper, adapter, route, fallback, or dependency is allowed. Any
required production change blocks this diagnostic design and requires a new
preregistration; it is not silently widened into Probe 7.

## Probe sequence and primary metric

After the capability gate and green deterministic/semantic contracts, opening
the sole hard development row consumes Probe 7.

### Stage A: first candidate falsification

Run CaDiCaL once (`C0`) on the sole permitted row with:

- internal solve/termination cap: **9.0 seconds**;
- outer process cap: **10.0 seconds**;
- jobs: **1**;
- exactly one solver call;
- eager path and no lazy fallback.

`C0` must return independently proof-checked UNSAT strictly before 9.0 seconds.
Otherwise kill the candidate immediately and do not run the repetition set.

### Stage B: robustness/noise gate, only if C0 passes

Run exactly three interleaved paired repetitions in this frozen order:

`G1, C1, G2, C2, G3, C3`

where `G` is Glucose4 and `C` is direct CaDiCaL 2.2.1. Every invocation uses
the same 9-second internal and 10-second outer caps, jobs `1`, exact formula and
phase hashes, one solve, eager path, and no fallback. Do not add runs, retry a
valid run, peek-and-stop, change order, or replace a timeout with a remembered
control result.

**Primary metric:** CaDiCaL solve wall time for the three independently
proof-checked UNSAT repetition results.

**Survival threshold:** all of the following:

- `median(C1, C2, C3) <= 8.0 seconds`;
- every candidate `C1..C3 < 9.0 seconds`;
- every Glucose4 control `G1..G3` times out at the 9.0-second internal cap;
- all identity, one-solve, eager/no-fallback, semantic, and proof gates pass.

The minimum meaningful effect is exactly a transition from all paired Glucose4
timeouts to three valid CaDiCaL UNSAT results satisfying that median/every-run
gate. Native statistics, build time, proof size, and conflict rate are
diagnostic secondary metrics and cannot substitute for the primary gate.

### Kill and falsification conditions

Kill the candidate on any capability miss after the probe begins, hash mismatch,
semantic-authority failure, invalid/missing UNSAT proof, SAT/UNKNOWN/crash,
timeout, candidate time `>= 9.0s`, candidate median `> 8.0s`, a Glucose4 control
that solves, more than one solver call, any refinement/fallback, missing required
statistics, callback, option/config sweep, or encoding/routing change.

The falsification condition is any failure to clear every survival condition.
Lower native conflict counts or a near-timeout speedup do not survive.

## Mandatory diagnosis on any consumed-probe miss

On any miss after the ICCMA row has been opened, record status exactly:

`promotion no-go; diagnosis incomplete`

Then collect `py-spy` evidence on the real worker/process for both Glucose4 and
CaDiCaL, plus CaDiCaL native solver statistics. The diagnosis must record:

- profiler commands, real process identities, and raw artifact paths;
- the baseline/paired profile used for comparison;
- dominant cost before and after;
- conflicts, decisions, propagations, restarts, build time, and solve time;
- whether the intended invariant—one unchanged CNF solved under cap—changed;
- whether the hot path moved, shrank, or stayed unchanged;
- the exact next target named by that evidence.

The no-go remains diagnosis-incomplete until this evidence is committed. py-spy
on a Python wrapper without the real solver/worker process and wall-clock-only
reporting are insufficient.

## Budget and promotion boundary

At this preregistration commit, budget remains **6 / 8 triage probes** and
**0 / 3 full experiments**. Probe 7 is preregistered and **not consumed**.

Capability absence leaves usage at 6/8. Opening the sole permitted ICCMA row
after capability/contract validation consumes Probe 7 and changes usage to 7/8
regardless of its result. Even a fully positive Probe 7 is triage evidence only;
because the production route excludes the 600-assumption row, it authorizes
only a separate routing-experiment preregistration. It never authorizes holdout
access, a full-dev run, source promotion, or a direct route change.

## Inputs and provenance

- Fresh inventory:
  `C:\Users\Q\AppData\Local\Temp\iccma-candidate7-inventory-20260711.txt`
- Fresh adversarial review:
  `C:\Users\Q\AppData\Local\Temp\iccma-candidate7-adversary-20260711.txt`
- Historical CaDiCaL195 record:
  `experiments/2026-05-20-cadical195-sparse-narrow-engine.md`
- Current base-UNSAT evidence:
  `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md`

No candidate capability was established, no CaDiCaL source was built, no test
or source file was changed, no ICCMA row was run, Probe 7 was not consumed, and
the holdout remained sealed while writing this record.
