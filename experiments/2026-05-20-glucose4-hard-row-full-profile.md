# Glucose4 hard row full profile

Date: 2026-05-20

Status: measured on `main`.

Workflow used: worker-level py-spy profiling through the real ICCMA worker path.

Profile command:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba --subtrack SE-ST --backend auto --timeout-seconds 240 --profile-dir data\iccma\2025\profiles\engine-glucose4-hard-row-full --profile-format speedscope --output-json data\iccma\2025\runs\profile-glucose4-hard-row-full.json --output-csv data\iccma\2025\runs\profile-glucose4-hard-row-full.csv
```

Profile summary command:

```powershell
uv run tools\speedscope_hot_frames.py data\iccma\2025\profiles\engine-glucose4-hard-row-full\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.speedscope.json --limit 30
```

Result:
- Row: `ABAs/abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba`, `SE-ST`.
- Status: solved.
- Elapsed: 151.83979749993887 seconds.
- Witness size: 148.
- Validation: valid.
- Solver metadata:
  - algorithm: `native_sparse_narrow_sat`;
  - detail: `monotone_cegar_stable_witness`;
  - solver checks: 5;
  - candidate models: 5;
  - loop formulas: 344;
  - learned clauses: 33033;
  - closure checks: 5;
  - rule firings: 8702;
  - clingo calls: 0.

Hot frames:
- `pysat.solvers.py:3945 solve`: 150.96 seconds exclusive.
- `aba_sat.py:1014 stable_extension`: 150.96 seconds inclusive at the solver
  call.
- `aba_sat.py:1018 stable_extension`: 0.49 seconds inclusive for loop-formula
  processing after solver models.
- `aba_sat.py:1046 _unsupported_derived_loop_formulas`: 0.45 seconds
  inclusive.
- `aba_sat.py:1109 _loop_formula_for`: 0.38 seconds inclusive.

Conclusion:

The bottleneck is raw CDCL search inside the PySAT Glucose4 solver call, not
Python loop-formula generation, closure, SCC analysis, validation, runner
overhead, or clingo. This profile supports choosing the next experiment from
SAT-engine/search behavior rather than optimizing Python loop-formula code.

Decision:

Do not spend the next slice micro-optimizing `_unsupported_derived_loop_formulas`
or `_loop_formula_for`; they are below one second combined on the full run. If
continuing toward the 30-second gate, the next candidate experiment must change
what the SAT solver sees or how it searches. The `cadical195` engine-only
experiment was weakly positive but still far from the gate, so an IPASIR-UP
prototype is plausible only if it can affect CDCL search directly and has its
callback overhead measured first.

Generated diagnostics:
- `data\iccma\2025\profiles\engine-glucose4-hard-row-full\aba-SE-ST-auto-abcgen_c7_atoms200_asms100_mra3_mbs2_cp0.9_ins2.aba-a87d73ccc529.speedscope.json`
- `data\iccma\2025\runs\profile-glucose4-hard-row-full.json`
- `data\iccma\2025\runs\profile-glucose4-hard-row-full.csv`

These generated diagnostics were not committed.

## Retroactive protocol audit

Protocol status: true full-profile diagnostic experiment.

This record is the model for the new standard. It profiled the real ICCMA
worker path and showed the dominant cost was raw PySAT Glucose4 CDCL solving,
not Python loop-formula generation, closure, SCC analysis, validation, runner
overhead, or clingo.

Required follow-up: native sparse/narrow experiments must change SAT search
shape or solver behavior, not micro-optimize Python loop-formula code.
