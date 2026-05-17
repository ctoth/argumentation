# ABA Preferred Salvage Inventory

## Decision

Salvage the operational learning, not the failed preferred solvers.

The inspected branches agree on the same class-level result: semantic
preferred-correctness tests are too weak for dense monolithic ABA preferred
rows. The branches produced useful page citations, failure records, runner
fixes, and route/contracts, but none produced a production preferred backend
that solved the hard preferred rows under the benchmark budget.

Production code from these branches is rejected unless a later workstream first
adds an operational contract that the code satisfies. Filename, path, generator,
ICCMA-year, and manifest-id routing remain forbidden.

## Current Main Guardrails

- `tests/test_performance_contracts.py` includes a preferred no-attack contract
  that bounds solver calls instead of accepting only semantic correctness.
- `tests/test_aba_route_properties.py` includes dense preferred route
  guardrails: the current large/dense preferred shape may expose experimental
  route candidates, but it must not be marked as a production route without
  benchmark evidence.
- `tests/performance_contracts.py` and `tools/perf_calibrate.py` provide
  calibrated timing support for future operational contracts.
- `tools/run_aba_hard_bucket.py --no-profile` provides status runs without
  py-spy/profile plumbing contaminating worker output.

## Branch Inventory

### `experiment/aba-greedy-preferred-growth`

Touched paths included `src/argumentation/aba_asp.py`,
`src/argumentation/aba_incremental.py`, ABA tests, the hard-bucket runner, and
`workstreams/aba-greedy-preferred-growth.md`. The branch also contained
unrelated dialectical-chess deletions; those are rejected as out of scope.

Rejected production path: greedy preferred growth over a grounded complete
control extension. It repeatedly called constrained complete-superset solvers
and still timed out on T1/T3/T5/T6/T8 across `auto`, `asp`, and `sat`.

Useful salvage:

- failure record that greedy local growth does not avoid the hard-row preferred
  search class;
- py-spy attribution from T1 showing time dominated by solver calls, not Python
  wrapper overhead;
- page citations around Lehtonen complete/preferred ABA encodings and Egly
  maximality reasoning;
- the operational lesson that a route must prove it reduces solver work, not
  just construct semantically valid preferred candidates.

Contract implication: future greedy/grow algorithms need bounded call-count or
residual-reduction contracts before benchmark work. A semantically valid
preferred witness test is insufficient.

### `experiment/aba-complete-labelling-prefsat-backend`

Touched paths included `src/argumentation/aba_sat.py`,
`tests/test_aba_incremental_paper_properties.py`, the hard-bucket runner, and
`workstreams/aba-complete-labelling-prefsat-backend.md`.

Rejected production path: eager complete-labelling PrefSat using precomputed
minimal supports plus Cerutti-style grow/block maximality. The property suite
passed, but T1/T3/T5/T6/T8 timed out on `sat`, and C2 preferred also timed out
on `sat` despite being solved by existing `auto`/`asp`.

Useful salvage:

- semantic properties for exactly-one labelling, attacked/out equivalence,
  conflict-free and defended `in`, complete-extension equivalence, preferred
  maximality, subset blocking, and skeptical counterexamples;
- failure record that eager support enumeration and expanded SAT constraints
  are not viable for the dense hard rows;
- Cerutti 2013/2015 page citations for complete-labelling PrefSat and
  candidate blocking.

Contract implication: complete-labelling work must include operational
contracts around support materialization, clause growth, solver calls, or
candidate blocking progress. Semantic PrefSat equivalence alone is not a pass.

### `experiment/aba-native-rule-closure-prefsat`

Touched paths overlapped the complete-labelling branch:
`src/argumentation/aba_sat.py`, ABA paper-property tests, the hard-bucket
runner, and the PrefSat workstream.

Rejected production path: ranked native rule-closure SAT variables with CEGAR
complete-labelling refinement. This removed the eager `_minimal_supports`
surface, but T1/T3/T5/T6/T8 still timed out on `sat`; C2 also timed out on
`sat` while existing routes solved it.

Useful salvage:

- negative evidence that the losing surface is not only Python support
  pre-enumeration;
- failure record pointing at SAT encoding/search shape as the next bottleneck;
- the same PrefSat semantic-property set if future contracts need small-case
  oracle coverage.

Contract implication: native rule-closure encodings require a structural
progress metric or benchmark-backed route evidence before becoming production
routes for dense preferred rows.

### `experiment/aba-asp-saturation-preferred`

Touched paths included `src/argumentation/aba_asp.py`,
`src/argumentation/aba_incremental.py`, ABA tests, the hard-bucket runner, and
`workstreams/aba-asp-saturation-preferred-backend.md`.

Rejected production path: single ASP optimization over the Lehtonen complete
program with `#maximize` for preferred witnesses. The local semantic contract
and broad regression suite passed, but T1/T3/T5/T6/T8 timed out on all
backends. C1 required later rebaseline work; C2/C3 remained solved by existing
routes.

Useful salvage:

- failure record that global ASP optimization over complete extensions does not
  solve the dense preferred class;
- page-image citations: Egly pages 010/011/014/015/018/019/020/021 and
  Lehtonen pages 005/006/012;
- tests around maximality/counterexample witnesses if converted into
  operational route contracts.

Contract implication: ASP saturation or optimization must prove it avoids the
observed global-complete-extension blow-up. Correct maximality encoding is not
enough.

### `experiment/aba-preferred-maximality-backend`

Touched paths included `src/argumentation/aba_sat.py`,
`tests/test_aba_incremental_paper_properties.py`, the hard-bucket runner, and
`workstreams/aba-preferred-maximality-backend-workstream.md`. An unrelated
dialectical-chess workstream was present and is rejected as out of scope.

Rejected production path: removing the stable-extension precheck and routing
preferred SAT directly into the existing support-aware CEGAR grow/maximality
path. This did not implement the true three-valued complete-labelling PrefSat
surface. T1 and T3 remained all-timeout across all backends, T5 was on the
timeout path, and the targeted gate failed.

Useful salvage:

- failure record distinguishing the approximated CEGAR route from the actual
  Cerutti complete-labelling target architecture;
- C1 rebaseline evidence: in that branch state C1 was an all-timeout stable
  hard row, not a SAT-only stable witness bug;
- page-image citations for Lehtonen 2021, Egly 2010, Cerutti 2013/2015,
  Niskanen/Jarvisalo 2020, and Baroni/Giacomin 2005;
- hard-bucket runner `--no-profile` status mode, already present on main.

Contract implication: the next PrefSat attempt must target the actual
three-valued complete-labelling architecture or first profile the changed SAT
timeout directly. Small semantic properties should be kept only as support for
operational contracts.

## Next Workstream Shape

The next preferred-row workstream should begin with contracts that make route
success measurable before implementation:

- structural route evidence for a dense preferred class, based only on argument
  shape;
- bounded solver-call or bounded-candidate-growth checks on small generated
  families;
- residual-reduction checks for grow/block algorithms;
- calibrated time contracts only where the local machine calibration supports
  them;
- explicit non-production contracts for semantically valid but benchmark-failed
  SAT/ASP candidates.

Only after those contracts exist should old semantic tests or page-cited solver
code be recreated.
