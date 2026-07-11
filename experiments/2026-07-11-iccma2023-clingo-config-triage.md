# ICCMA 2023 Clingo Configuration Triage

Date: 2026-07-11

Status: preregistered dev-only Round 1 probe 2; no measurements run yet.

Code baseline: `2091a7d59adc484ca0abfbd282a774ea2c447267` (`main`,
tracked files clean before the probe). This is a triage probe, not a source
experiment. Production solver code, evaluator tests, runner code, and the sealed
holdout are out of scope.

## Preregistration (frozen before measurements)

### Hypothesis and single variable

Hypothesis: one Clingo 5.8.0 built-in control configuration reduces the dominant
Clingo search cost of
`benchmarks/aba/aba_2000_0.3_10_10_1.aba` SE-PR enough to cross the frozen
10-second campaign metric boundary without changing semantics.

Single variable: the user-supplied `clingo.Control` configuration argument. All
arms use the same parsed framework, production `solve_aba_with_backend` direct
API, `backend="clingo"`, `semantics="preferred"`,
`task="single-extension"`, sequential execution (`--jobs 1` equivalent), and a
15.0-second direct Clingo solve cap. No solver, encoding, evaluator, or runner
code changes are allowed.

Installed solver documentation was captured before selecting arms:

```text
uv run -m clingo --version
pyclingo version 5.8.0; libclingo version 5.8.0; libclasp version 3.4.0

uv run -m clingo --help=3
--configuration={auto|frumpy|jumpy|tweety|handy|crafty|trendy|many|<file>}
auto selects tweety for ASP; handy targets large problems; crafty targets
crafted problems; trendy targets industrial problems.
```

The exact four arms are frozen as:

| Arm | User control args | Effective `Control` args |
|---|---|---|
| `default` | `()` | `--models=0 --warn=none` (Clingo `auto`, ASP selects `tweety`) |
| `handy` | `("--configuration=handy",)` | `--models=0 --warn=none --configuration=handy` |
| `crafty` | `("--configuration=crafty",)` | `--models=0 --warn=none --configuration=crafty` |
| `trendy` | `("--configuration=trendy",)` | `--models=0 --warn=none --configuration=trendy` |

No arm or argument may be added, removed, or tuned after results are visible.
`tweety` is not a separate arm because it is the ASP configuration selected by
the default `auto` arm.

### Operational contract and pinned surfaces

The fast operational contract is emitted for every run before the campaign gate:
status, elapsed wall time, exact effective control args, solver calls, outer
iterations, inner iterations, and refinement clauses. A telemetry type/error or
control-argument mismatch fails that run. This directly observes whether the
same preferred-growth path performs less search work before the 10-second frame
boundary.

Pinned live/reference surfaces at the baseline commit:

| Surface | Git blob |
|---|---|
| `src/argumentation/structured/aba/aba_asp.py` | `53e77a01b4fe5d963678ca5e45be44872301a455` |
| `src/argumentation/structured/aba/aba_incremental.py` | `1a41f08255db497c7fe6fc400a5f8ba3ff9477e9` |
| `src/argumentation/structured/aba/aba.py` | `63a092cc376a9eb975826cdc7c2116767259cf3b` |
| `src/argumentation/structured/aba/aba_kernel.py` | `720b20a7eec77de4e8238e7b84b8e16139ecb832` |
| `src/argumentation/interop/iccma.py` | `861fae9775b370ee4e54a02fb084a628efdd0354` |
| `tools/iccma2025_run_native.py` | `4c1c7d35cd2028fa6ce93c8091ab0fbc1054d9b5` |

The reusable probe script may be added under `scripts/`; it must not alter any
pinned surface.

### Instance, run order, cap, and command

Development instance only:
`data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_1.aba`.
The sealed holdout is neither read nor run.

Each arm runs exactly three times in this fixed interleaved order:

```text
default, handy, crafty, trendy,
default, handy, crafty, trendy,
default, handy, crafty, trendy
```

Each call passes `clingo_solve_timeout_seconds=15.0`. Runs are sequential in one
process, which is the direct-API equivalent of `--jobs 1`. The exact metric
command is:

```text
uv run scripts/probe_iccma2023_clingo_config.py \
  --output data/iccma/2023/runs/probe2-clingo-config-triage.json
```

The diagnostic may exit nonzero after writing complete evidence when no arm
survives; that is the expected fail-closed kill outcome, not a reason to rerun or
tune.

### Independent witness check

Every `success` result must contain exactly one preferred witness and its
`accepted_assumptions` must match that witness. The script then validates the
same witness independently of the measured Clingo preferred encoding:

1. the polynomial Horn-closure characterization of the reference flat-ABA
   semantics must establish subset/closure, conflict-freeness, and defense: for
   `U`, the assumptions not attacked by the witness, no witness member's
   contrary may occur in `closure(U)`;
2. the separate `AssumptionKernel` admissibility encoding is asked for an
   admissible proper superset by requiring all witness assumptions and at least
   one outside assumption;
3. the witness is preferred-valid only when that query returns no superset.

The direct `aba.admissible` reference function is intentionally not invoked on
this 600-assumption instance because its reference implementation enumerates the
full assumption powerset. The Horn-closure criterion is the equivalent
polynomial flat-ABA check already used by probe 1; the separate kernel query
supplies the maximal-admissible (preferred) check.

No witness, a malformed witness, failed admissibility, a returned proper
admissible superset, or any checker exception is a closed failure for that run.

### Analysis and survival threshold

For each arm, record all three statuses, elapsed seconds, witness/checker status,
exact effective control args, and the four telemetry counters. Report elapsed
median and spread as `[min, max]` (also `max - min`), plus per-counter medians and
ranges. This is a small multiple comparison; no point-estimate-only winner is
accepted.

An arm survives only if all hold:

1. all 3/3 runs return a correct preferred witness;
2. elapsed median is at most **8.0 seconds** and every run is below **9.0
   seconds**;
3. no solver, telemetry, control-argument, or independent-checker error occurs;
4. the only changed input is the Clingo configuration, so any improvement is in
   Clingo search rather than evaluator behavior.

If exactly one arm survives, profile only that arm on the real runner worker
with the existing py-spy hook and the same control argument, then compare its
dominant samples with probe 1's default profile (`928` samples in
`clingo.Control.solve`, `27` in initial grounding, `19` in program addition, `3`
in refinement grounding). If zero arms survive, do not profile a loser: the
three repeated timings and operational telemetry are the kill evidence. If more
than one arm survives, this discriminator is ambiguous and no profile is run.

### Kill and falsification conditions

Kill every non-surviving arm without follow-up tuning. Kill the hypothesis for
this probe if no built-in arm survives, if multiple arms survive without a
unique discriminator, or if correctness/telemetry cannot be proven. The
hypothesis is falsified by zero arms meeting every preregistered threshold.

This probe is directional triage only. A survivor does not authorize a source
experiment, production default change, holdout run, promotion, push, or merge.

## Results

Pending preregistered measurements.
