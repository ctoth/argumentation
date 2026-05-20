# IPASIR-UP no-op overhead probe

Date: 2026-05-20

Status: measured on experiment branch; probe tool should be promoted.

Experiment branch: `exp/ipasir-up-overhead-probe`.

Evidence commit:
- `64fdfbe` Add IPASIR-UP overhead probe.

Changed path:
- `tools/probe_ipasir_up_overhead.py`

Hypothesis: a PySAT `cadical195` IPASIR-UP user propagator would have low
enough callback overhead to justify building a real sparse/narrow ABA
unfounded-set propagator.

Single variable: compare `cadical195` baseline solving against `cadical195`
with a connected no-op propagator observing all variables.

Smoke command:

```powershell
uv run tools\probe_ipasir_up_overhead.py --case smoke:30:100:3 --repeat 1 --seed 1
```

Metric command:

```powershell
uv run tools\probe_ipasir_up_overhead.py --repeat 5 --seed 20260520 --output-json data\iccma\2025\runs\ipasir-up-noop-overhead.json
```

Metric result:

| Case | Baseline median | Observed no-op median | Ratio | Assignment callbacks | Decision callbacks |
|------|-----------------|-----------------------|-------|----------------------|--------------------|
| `small` | 0.033606300014071167s | 0.020732600009068847s | 0.6169259930545159x | 16290 | 1761 |
| `medium` | 0.3913907000096515s | 1.113656200002879s | 2.8453823761663646x | 970060 | 69273 |
| `aba_like` | 0.6240379000082612s | 2.095958499936387s | 3.3587038542188545x | 2821865 | 285278 |

Outcome: negative for an all-variable eager propagator.

Decision: do not build a production all-variable IPASIR-UP propagator next. The
no-op observed propagator is already about 3.36x slower on the ABA-like
synthetic case, before doing any useful ABA reasoning. The small case win is
not meaningful because the search changed and the run is too tiny.

Recommendation: if IPASIR-UP is revisited, the next probe must be narrower:
observe only a small candidate variable set, or test lazy model-check-only
callbacks. A real propagator must first show that it avoids the late
refinement solves enough to pay for callback overhead. The immediate next
solver experiment should avoid per-assignment Python callbacks over every SAT
variable.

Generated diagnostics:
- `data\iccma\2025\runs\ipasir-up-noop-overhead.json`

This generated diagnostic was not committed.
