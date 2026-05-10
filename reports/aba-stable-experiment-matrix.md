# ABA Stable Experiment Matrix

Workflow used: Workstream 5 from `workstreams/post-cap150-solver-frontier.md`.

Target row:

- subtrack: `SE-ST`
- instance: `ABAs/aba_500_0.1_10_5_7.aba`
- acceptance gate command shape: `uv run tools\iccma_run_timeout_rows.py --timeouts tests\manifests\iccma2025-cap150-timeouts.json --subtrack SE-ST --timeout-seconds 15 --backend auto ...`

Method:

- A known timeout row is first a profiling target, not a binary 15-second gate.
- Every experiment must record phase timings for parse, preprocessing/support
  build, encoding build, and SAT check where applicable.
- Every experiment must record encoding shape: variables by kind,
  assertions/constraints, dependency SCC sizes, and solver result/reason.
- Diagnostic caps are 60, 150, and 300 seconds unless a smaller cap already
  proves the branch is worse than baseline on the measured bottleneck.
- The 15-second acceptance gate is run only after a branch improves a measured
  bottleneck or reaches a lower diagnostic cap than baseline.
- A timeout at 15 seconds is not by itself a research conclusion.

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

Baseline profile under 60-second Z3 cap:

- integer ranks: build 2.5578s, 4099 assertions, 550 Boolean variables, 500
  integer rank variables, Z3 `unknown` after 60.0419s
- integer ranks plus forced literals: build 3.3495s, 4099 assertions, Z3
  `unknown` after 60.0486s
- bit-vector ranks: build 2.4858s, 3649 assertions, 550 Boolean variables,
  500 bit-vector rank variables, Z3 `sat` after 7.9613s
- bit-vector ranks plus forced literals: build 3.2443s, 3649 assertions, Z3
  `sat` after 7.7784s; not promoted because the forced-literal build overhead
  did not improve the bit-vector gate
- Boolean rank ladder: build 92.5043s, 251100 assertions, 251050 Boolean
  variables, Z3 `unknown` after a 1-second diagnostic cap; rejected on build
  bottleneck
- support-materialized stable encoding: support build exceeded a 10-second
  diagnostic cap; the earlier unbounded run was stopped only after the child
  process reached about 25GB working set

Experiments:

| Branch | Mechanism | Compatible With | Targeted Tests | Diagnostic Profile | 15s Acceptance Gate | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| `experiment/aba-stable-boolean-rank-ladder` | Boolean closure ladder instead of integer ranks | forced literals, SCC decomposition | passed closure and stable oracle tests | build 92.5043s, 251100 assertions, Z3 `unknown` after 1-second cap | timeout at 15 seconds | branch preserved; rejected on build bottleneck |
| `experiment/aba-stable-support-sat` | Materialize minimal supports for stable constraints | forced literals, SCC decomposition | passed support-stable and stable oracle tests | support build exceeded 10-second cap; unbounded run reached about 25GB working set | timeout at 15 seconds | branch preserved; rejected on support-build bottleneck |
| `experiment/aba-stable-bitvec-profiled` | Bit-vector ranks for stable closure | forced literals, SCC decomposition | passed bit-vector closure property and ABA regression tests | build 2.4885s, 3649 assertions, Z3 `sat` after 7.7699s under 15-second cap | solved target row at 15 seconds; whole manifest solved 6/16 | promoted in `57a5c98` |

Pending matrix entries:

- SCC decomposition as an experiment branch
- forced literals plus Boolean rank ladder
- forced literals plus support-materialized stable encoding
- SCC decomposition plus best non-SCC encoding

Deferred combination entries:

- forced literals plus bit-vector rank: profiled on the promoted bit-vector
  encoding; the combination solved, but did not improve the bit-vector-only
  profile enough to justify extra production constraints
