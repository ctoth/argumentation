# Probe 5 preregistration: collective-attack SCC operational shape

Date: 2026-07-11

Status: semantic contract implemented; operational measurement preregistered but not run.

Branch: `main`

Contract base: `0d03790a0d62e06f013910898810a1fbf0538bdf`

## Evidence boundary

No ICCMA hard-row measurement has occurred for this probe. No benchmark,
solver worker, holdout row, or production source slice has been run or created.
The semantic gate must pass before the separately committed operational
measurement may begin. The semantic gate is exact stable- and preferred-family
equality against both current direct native and minimal-support oracles on the
named deterministic fixtures and bounded generated frameworks.

The operational measurement is development-only. It must not access
`experiments/iccma2023-frame/population-holdout.json`, edit `src/`, or introduce
a solver/routing source slice. It is a shape-survival probe, not promotion
evidence and not a benchmark result.

## Preregistered hypothesis

The exact minimal-support collective-attack primal graph has useful directed
SCC structure on at least one campaign-hard development framework, and exact
conditioning reduces the largest residual while keeping support extraction and
the full `D/P/U/UP/C/M` boundary within deterministic caps.

Single variable: observe exact collective-support SCC conditioning on the
campaign-hard development frameworks with the semantic-contract reference
state fixed. Do not change solver behavior, routing, semantics, caps, or the
development population during the measurement.

## Planned command and fixed caps

The separately committed operational measurement must expose this command:

```text
uv run scripts/measure_aba_scc_composition_shape.py --manifest experiments/iccma2023-frame/population-dev.json --baseline-record experiments/2026-07-11-iccma2023-campaign-frame-baseline.md --only-baseline-timeouts --collective-attack-cap 4096 --branch-state-cap 65536 --boundary-item-cap 4096 --output experiments/artifacts/2026-07-11-probe-5-scc-shape.json
```

The caps are frozen at 4,096 materialized collective attacks per framework,
65,536 recursion branch states per framework, and 4,096 stored boundary items
per component state. A cap hit is fail-closed and kills operational survival;
it must not be converted into sampling, truncation, approximate supports, or a
larger post-hoc cap.

## Operational survival gate

The route survives only if every condition below holds:

1. The executable semantic gate passes first.
2. Exact collective-support extraction completes under the 4,096-attack cap on
   every measured hard development framework.
3. At least one measured hard framework has more than one useful support-primal
   SCC: at least two nonempty SCCs participate in an inter-SCC collective
   attack path used by conditioning.
4. At least one measured hard framework has a strictly smaller maximum exact
   conditioned residual than its factual-normalized assumption count.
5. Every measured branch stays within both the 65,536-state cap and the
   4,096-item full-boundary cap, including selected/attacked sets, `D/P/U/UP`,
   preferred candidate set `C`, conditioned collective tails, and mitigated
   set `M`.
6. The measurement touches no holdout path and creates no production
   `src/` delta or solver/routing source slice.

All six clauses are conjunctive. Failure of any clause kills this operational
route without weakening the semantic theorem.

## Falsification and analysis plan

The hypothesis is falsified if support extraction hits its cap, all hard
development frameworks collapse to one useful SCC, the maximum conditioned
residual never strictly shrinks, or the exact boundary exceeds either bound.
The analysis is deterministic per framework: report normalized assumption
count, support count, SCC count and sizes, cross-SCC collective-tail count and
width, maximum conditioned residual, branch-state count, maximum boundary
items, and every cap status. No wall-clock threshold or hard-row solved result
may be substituted for these structural fields.

No hard-row result belongs in this preregistration. Results, if authorized by
the passing semantic gate, belong only in the later separately committed
operational measurement record.
