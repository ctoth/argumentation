# Probe 5 operational measurement: collective-attack SCC shape

Date: 2026-07-11

Status: **promotion no-go diagnosed; Round 1 probe 5 operationally killed.**
This was a development-only triage measurement, not a benchmark and not a
production experiment.

Measurement HEAD: `2dba279c97a55079b100d0b7cb5472f060a6bb31`

Frozen preregistration:
`experiments/2026-07-11-iccma2023-probe-5-scc-semantic-contract.md`

Failure artifact:
`experiments/artifacts/2026-07-11-probe-5-scc-shape.json`

## Scope and exact command

The six focused operational-shape tests passed before the frozen development-
only command began:

```text
uv run pytest -q tests/structured/aba/test_aba_scc_composition_shape.py
```

Result: `6 passed`.

The exact preregistered command was then run without changing its caps or
population:

```text
uv run scripts/measure_aba_scc_composition_shape.py --manifest experiments/iccma2023-frame/population-dev.json --baseline-record experiments/2026-07-11-iccma2023-campaign-frame-baseline.md --only-baseline-timeouts --collective-attack-cap 4096 --branch-state-cap 65536 --boundary-item-cap 4096 --output experiments/artifacts/2026-07-11-probe-5-scc-shape.json
```

No holdout path, production source change, production solver timing, or full
extraction rerun belongs to this reconciliation.

## Operational result

After about 13 minutes, the command had not completed the first exact support
extraction and had produced no partial output artifact. The real hot process,
PID `362188`, had accumulated about `800.42` CPU-seconds and had a working set
of `2,318,831,616` bytes.

The run was interrupted only after attaching `py-spy` to that real process:

```text
uv run --with py-spy py-spy dump --pid 362188
```

The active stack reported by the profiler was:

```text
_add_minimal_support line 155
  -> _minimal_set line 164
  -> _combine_supports line 146
  -> _minimal_supports line 120
     in aba_support_model.py
  -> _measure_framework line 400
  -> main line 529
     in scripts/measure_aba_scc_composition_shape.py
```

The diagnostic calls eager `_minimal_supports(framework)` before it computes
the resulting collective-attack count and calls `require_cap`. Therefore the
frozen `4,096` collective-attack cap bounds only a count available after eager
extraction; it does not bound extraction itself on this hard row.

No per-row structural metrics exist. In particular, no support count, SCC
count or sizes, useful-SCC count, cross-SCC tail measurement, conditioned
residual, branch-state count, or boundary-item count completed. None is
inferred or fabricated in the failure artifact.

## Failed clause and diagnosis

Frozen survival clause 2 required:

> Exact collective-support extraction completes under the 4,096-attack cap on
> every measured hard development framework.

Clause 2 failed operationally. More precisely, its intended bound was not
executable on the first hard row because the cap check occurs only after eager
minimal-support enumeration completes.

Failure analysis required by `AGENTS.md`:

- Profiler/operational measurement: real-process `py-spy dump`, elapsed
  observation, CPU time, and working-set observation above.
- Compared against: the frozen hypothesis that exact extraction would complete
  under an executable 4,096 collective-attack bound before SCC conditioning
  was assessed. There was no production source delta and no prior hard-row
  extraction profile to treat as a numeric baseline.
- Dominant cost before: the preregistered intended operation was bounded exact
  support extraction followed by collective-attack counting and SCC
  conditioning; no earlier hard-row extraction profile localized that cost.
- Dominant cost observed: eager minimal-support antichain construction in
  `_add_minimal_support`, `_minimal_set`, `_combine_supports`, and
  `_minimal_supports`, before any cap check.
- Intended operational invariant: exact collective-support extraction is
  bounded by the frozen 4,096 collective-attack cap.
- Invariant change: **unchanged**. The measurement infrastructure did not make
  that bound executable on the hard row.
- Next target from this profile: before this SCC route could be reconsidered,
  exact support generation would need an executable in-generation bound or an
  equivalent bounded extraction contract. This record does not design a new
  enumerator or authorize that work.

## Disposition

This is a diagnosed triage kill:

- status: `promotion_no_go_diagnosed`;
- probe 5 does not survive to a production source slice or full experiment;
- probe budget remains **5 / 8 used**;
- full-experiment budget remains **0 / 3 used**;
- Round 1 remains open. The budget is not exhausted, only one triage round is
  active, and this diagnostic-only kill does not advance the consecutive kept-
  production-improvement criterion.

The next candidate named by the committed history inventory is **small
backdoor/cutset conditioning into exact residual components**. It remains only
an inventory candidate: its first admissible evidence is bounded cutset and
strict-residual telemetry plus a lift/validation semantic contract. No work on
that candidate starts here.

Worker recommendation: record the diagnosed operational kill and continue
Round 1 candidate selection; do not promote or revive the SCC route from this
measurement.
