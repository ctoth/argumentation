# ABA Stable Experiment Matrix

Workflow used: Workstream 5 from `workstreams/post-cap150-solver-frontier.md`.

Target row:

- subtrack: `SE-ST`
- instance: `ABAs/aba_500_0.1_10_5_7.aba`
- gate command shape: `uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --subtrack SE-ST --timeout-seconds 15 --backend auto ...`

Diagnostics:

- branch: `main`
- commit: `57f8295`
- mechanism: current integer-rank stable SAT diagnostics
- result: Z3 returned `unknown` after a 15-second diagnostic timeout
- measured shape:
  - assumptions: 50
  - language literals: 500
  - rules: 2499
  - Z3 assertions: 4099
  - Boolean variables: 550
  - integer rank variables: 500
  - rule dependency SCC count: 53
  - largest dependency SCC: 448 literals
- promotion decision: kept diagnostics tool

Experiments:

| Branch | Mechanism | Compatible With | Targeted Tests | Stable-Row Gate | Decision |
| --- | --- | --- | --- | --- | --- |
| `experiment/aba-stable-boolean-rank-ladder` | Boolean closure ladder instead of integer ranks | forced literals, SCC decomposition | passed closure and stable oracle tests | timeout at 15 seconds | failed; branch preserved |
| `experiment/aba-stable-support-sat` | Materialize minimal supports for stable constraints | forced literals, SCC decomposition | passed support-stable and stable oracle tests | timeout at 15 seconds | failed; branch preserved |

Pending matrix entries:

- forced-literal simplification as an experiment branch
- bit-vector rank as an experiment branch, preserving branch instead of reverting on `main`
- SCC decomposition as an experiment branch
- forced literals plus Boolean rank ladder
- forced literals plus bit-vector rank
- forced literals plus support-materialized stable encoding
- SCC decomposition plus best non-SCC encoding
