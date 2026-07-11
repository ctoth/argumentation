# ICCMA 2023 Support-Free/Core-Fact Preprocessing Triage

Date: 2026-07-11

Status: **Round 1 probe 3 triaged out; diagnosed negative.** Evidence-only
integration of the semantic and operational scout artifacts. No production
source slice was created, no benchmark was rerun, and the sealed holdout was
neither read nor run.

Code baseline: `main` at `56a946eed4845f3190a4e6be9200cc834c1b0e3a`,
with clean tracked state before integration.

## Candidate and preregistered survival gate

Candidate as stated: extend support-free/core-fact preprocessing to flat-ABA
SE-ST and SE-PR so that materialized minimal supports are avoided and the
solver receives a smaller residual framework.

This is a campaign triage probe, not a full experiment-protocol run. The
operational scout fixed the following finite development-only gate before
integration of its result:

1. Current source/encoding metadata must show that support-free/core-fact
   execution is not already the applicable production Clingo baseline.
2. The existing semantics-preserving grounded reduct must strictly reduce at
   least one of the two 600-assumption development instances that supply all
   campaign headroom. A reduction of one assumption or one rule was sufficient
   to survive this deliberately permissive gate.
3. Any solver failure, missing measurement, holdout access, or absence of
   strict reduction fails closed. A triage survivor would authorize only a
   separately preregistered source experiment, never promotion.

The gate tests the claimed mechanism before wall clock: an already-active
encoding or an identity residual cannot change the profiled search problem.

## Evidence adjudicated

The two scout artifacts were checked against:

- the committed campaign frame, 21/24 three-repeat baseline, probe ledger, and
  prior negative records;
- current production paths in `aba_asp.py`, `aba_incremental.py`, and
  `aba_preprocessing.py`;
- the committed core-fact, multishot, residual-lift, and acceptance-equivalence
  tests; and
- the committed real-worker py-spy evidence from Round 1 probe 1 and the
  repeated operational telemetry from probe 2.

Relevant current blobs at the adjudicated commit:

| Surface | Git blob |
|---|---|
| `src/argumentation/structured/aba/aba_asp.py` | `53e77a01b4fe5d963678ca5e45be44872301a455` |
| `src/argumentation/structured/aba/aba_incremental.py` | `1a41f08255db497c7fe6fc400a5f8ba3ff9477e9` |
| `src/argumentation/structured/aba/aba_preprocessing.py` | `2fd6f981c76a142ef86c8f259ae072f6614f1139` |
| `tests/structured/aba/test_aba_multishot.py` | `47dd80b06c8889d93179b2772d54c82491ab1b3a` |
| `tests/structured/aba/test_aba_preprocessing.py` | `893fc116aea6a145257d3f91c721b6ee1faa4fab` |
| `tests/structured/aba/test_aba_incremental_paper_properties.py` | `5bd6c89d75c6cae30d047e3ca398bae35b0809de` |
| `tools/aba_iccma_probe.py` | `ceb6f14e1586107d8fb3f90470c15ca028d06dba` |

The scout reports are the retained raw narrative evidence:

- `reports/iccma-s2-semantic-scout-20260711.md`;
- `reports/iccma-s2-operational-scout-20260711.md`.

## Exact measurements

The operational measurement used the existing bounded, solver-free diagnostic
on development instances only:

```text
uv run tools/aba_iccma_probe.py \
  data/iccma/2023/extracted/instances/<relative_path> \
  --mode simplify-stable --timeout-seconds 5
```

Stable and preferred share the same `simplify_aba` grounded-reduct gate, so the
residual measurement applies to both semantics without a duplicate solve.

| Development instance | Elapsed | Fixed IN | Fixed OUT | Residual assumptions | Residual rules |
|---|---:|---:|---:|---:|---:|
| `aba_2000_0.3_10_10_0.aba` | 0.272 s | 0 | 0 | 600 / 600 | 7867 / 7867 |
| `aba_2000_0.3_10_10_1.aba` | 0.269 s | 0 | 0 | 600 / 600 | 7699 / 7699 |

Exact headroom result: **0/2 hard instances reduced**, covering **0/3 baseline
timeout rows**. Both instances retain every assumption and every rule. Across
the full 12-instance development population, the existing reduct is non-trivial
on 6/12 low-density instances and a no-op on all six `0.3` instances; those
low-density rows already solve and cannot increase the 21/24 primary metric.

The core-fact half is also already active: all 21 completed baseline rows report
`encoding=flat_aba_core_facts`, and current source forces
`include_supports=False` for ASP/Clingo. The timed-out rows traverse that same
source-guaranteed route; the later completed hard preferred probe reports the
same encoding.

No benchmark command was run during this integration. Repeating the 10-second
frame would not change either failed mechanism gate.

## Semantic verdict

**Semantically coherent, but already implemented.** For finite ordinary flat
ABA, direct ASP can compute forward derivability and attacks from complete
assumption/head/body/contrary facts without enumerating minimal-support facts.
For preferred and stable semantics, the grounded set and the assumptions it
attacks can be fixed IN/OUT, the residual can be solved, and extensions can be
lifted. Current production code already does both.

The committed tests establish the relevant boundaries: direct core facts omit
`support_*`; preferred single-extension succeeds while `_minimal_supports` is
made forbidden; and simplified/lifted extension families plus credulous and
skeptical answers match unsimplified/native oracles for grounded, complete,
preferred, and stable cases. The reduction is correctly gated away from ABA+
and semantics such as admissible enumeration.

Broader shortcuts are not licensed. In particular, optional support for a
contrary does not force an assumption OUT, absence of a direct contrary rule
does not prove support-freedom, and stable nonexistence does not imply preferred
nonexistence. A stronger reduction would be a new semantic hypothesis rather
than this candidate.

Semantic verdict: **KILL as stated** because there is no missing semantic route
to implement. The earlier premise that core facts still needed extension to
SE-ST/SE-PR was wrong against current source and tests.

## Operational verdict and profiler comparison

**Operational invariant: unchanged.** The only headroom frameworks produce an
identity residual, so this candidate cannot shrink the assumption search space
or rule surface presented to the solver.

Committed real-worker py-spy evidence for the hard preferred row records `928`
samples in `clingo.Control.solve`, versus `27` in initial grounding, `19` in
program addition, and `3` in refinement grounding. Its live shape is 4 solver
calls / 1 outer iteration / 3 inner iterations / 3 refinements. Probe 2 then
observed the same 4/1/3/3 shape for every successful configuration arm.

Dominant cost before: Clingo search inside preferred growth. Dominant cost after:
unchanged by construction—there is no source/config delta, the core-fact route
is already live, and both hard residuals equal their originals. No new py-spy
run was warranted because there was no changed execution path to compare; the
recorded profile already observes the real worker/solver process and directly
rules out support materialization or program addition as the dominant cost.

Operational verdict: **KILL at triage; expected primary-metric gain 0 rows.**
Do not spend a production slice, benchmark probe, or full experiment on the
candidate as stated.

## Budget and campaign status

- Probe budget before this record: 2/8 used.
- This record consumes Round 1 probe 3: **3/8 used; 5 probes remain**.
- Full experiments: **0/3 used; 3 remain**.
- No candidate survives this probe.

No campaign kill criterion fires under the committed ledger convention. Budget
is not exhausted; Round 1 is still the first triage round, so there are not two
consecutive no-survivor rounds; and this read-only triage created no production
source slice, so it does not advance the three-consecutive-source-slices
criterion. Round 1 remains open.

## Next evidence-directed target

The next candidate must reduce Clingo search inside preferred growth rather
than remove already-absent support facts or rerun the existing grounded reduct.
The narrow qualifying target is a **semantics-proven stronger fixed-core or
search-space reduction** that, before any solver call:

1. extends the existing semantic equivalence battery with the new claim;
2. fails meaningfully on the current baseline rather than restating current
   behavior; and
3. strictly reduces assumptions, rules, or body literals on at least one hard
   600-assumption development instance.

Without such a proof and executable shrinkage contract, do not implement or
benchmark another preprocessing variant. The evidence does not support another
generic Clingo configuration sweep, the killed SAT route, or support-fact work.

## Final accounting

- Production source slice: **none**.
- Benchmark rerun: **none**.
- Sealed holdout access/run: **none**.
- Promotion/full experiment: **none**.
- Retained outcome: diagnosed negative triage evidence only.
