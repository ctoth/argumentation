# ICCMA timeout investigation

## Facts
- Full 60s/jobs8 run on 052775e: 5425 solved, 1969 timeouts across 7394 rows.
- abcgen accounts for 507 ABA timeouts, including all 120 DC-CO rows.
- Harness diagnostics merged locally as baabafd after 103 interop tests passed.
- A 3s real-worker dump found abcgen DC-CO inside minimal-support enumeration.

## Competing hypotheses
1. ABA complete acceptance spends the budget expanding minimal supports, before SAT search.
2. AF hard families spend the budget constructing encodings rather than searching.
3. Some families genuinely spend most of the budget in solver search.

## Operational contracts before optimization
- Measurement: attach py-spy to the PID published by the real worker, require a
  nonempty sampled profile, preserve stdout/results, terminate and reap the tree.
- Proposed ABA route contract (pending profile evidence): auto complete acceptance
  with Clingo available must not call minimal-support enumeration; it must solve
  using a query-directed call rather than enumerate extensions. Missing Clingo
  must preserve the SAT fallback. Semantic checks compare against native oracles.
- No optimization is promoted on a timeout-only result. Compare before/after
  sampled costs and a frozen set of representative benchmark rows.

## Current state
Three repairs implemented and verified. The frozen 320-row DC-CO gate is complete.
The ABA solver path was unchanged during the gate; concurrent AF/parser edits do
not affect ABA execution. Results below distinguish recovered tasks from the
remaining diagnosed timeouts.

## Evidence and repairs

Artifacts are in `data/iccma/2025/runs/diagnosis-20260927/` in the primary checkout.
`tools/profile_iccma_timeout_cases.py` attaches to the actual worker PID, samples
for up to 15 seconds, checks for nonempty samples, and terminates/reaps the tree.

### Complete credulous ABA acceptance

Representative: `abcgen_c25_atoms25_asms25_mra3_mbs2_cp0.8_ins2.aba`, DC-CO.

| Route | Sampled seconds | Dominant measured cost | Result |
|---|---:|---|---|
| baseline auto | 14.75 | 9.85 minimal supports; 4.23 admissible constraints | still running at profile cutoff; historical timeout at 60s |
| baseline explicit ASP | 14.94 | 14.52 complete-extension enumeration | still running at profile cutoff |
| repaired auto | 1.35 | 0.45 grounding; 0.45 one-model solve | solved NO, one solver call |

Times are sampled durations, not calibrated end-to-end speedup estimates.
The baseline ASP route already had an unused query helper; switching backends
alone was insufficient because dispatch still enumerated all complete models.
The repair wires that helper, propagates telemetry and incomplete-search status,
preserves grounded-reduct query classification and witness lifting, and selects
the route for auto DC-CO when Clingo is available. Explicit SAT and the fallback
without Clingo remain available.

Operational tests failed first (seven failures), then passed: no support or
extension enumeration, at most one solver call, valid lifted witnesses. Generated
small frameworks compare each literal against the native complete oracle, both
with and without preprocessing. The incomplete-search test requires timeout,
never a false negative.

### Residual ABA timeout diagnosis

Representative: `abcgen_c25_atoms25_asms35_mra3_mbs2_cp0.8_ins1.aba`, DC-CO.
The same worker was sampled before and after (`aba-hard-baseline` and
`aba-hard-fixed`). Baseline: 7.42/14.99s in support expansion and 7.15s in
constraint construction. Repaired: 13.72/14.98s in `_solve_one` / Clingo search,
0.83s constructing/grounding the control, zero support/model enumeration.
The 60s timeout dump independently shows that same search call.
The intended operational invariant changed; the remaining bottleneck is
query-constrained search. This residual failure is diagnosed, not a reason to
reinstate the old path. The next target would be the encoding/search workload on
this fixed case, with solver statistics and an operational contract first.

### Dense AF parsing

Baseline real-worker profile on `Large-result_b11.af` (20,859,200 attacks):
14.74/14.98 sampled seconds in `parse_af`, including 5.37s validating repeated
endpoint IDs. The fixed profile still spends 14.82/14.99s parsing, but no longer
calls repeated-ID validation. That giant-instance solve is not claimed fixed.

The parser now uses the header's canonical ID objects for edge endpoints.
Operational contract: a dense 120-vertex graph performs no more than 120 numeric
ID validations and retains canonical endpoint objects. Baseline called the
validator 28,800 times. Existing malformed-input and round-trip tests still pass.

On real `Medium-result_b20.af` (1,434 vertices, 843,510 attacks), separate parser
processes using `tools/measure_iccma_af_parser.py` measured:

| Metric | Baseline | Fixed |
|---|---:|---:|
| Parse wall seconds (one measurement) | 2.9081 | 1.3087 |
| Retained endpoint string objects | 1,682,557 | 1,434 |
| Retained endpoint string bytes | 74,599,775 | 63,423 |

Canonical serialized graph hashes match:
`7cd5d1cf32afd0cfdf4bc8bd9da7552b40e784fc2b44a9bed0f46e1033453ccb`.
The timing is a local measurement, not a universal speedup claim. String counts
exclude edge tuples and graph containers. Remaining dense-input parsing and
downstream graph/solver work remain targets; the measured allocation invariant
and validation cost have changed.

### AF preferred witness construction

`crusti_g2io_125_0.5_31_17.af`, SE-PR baseline: 12.73/14.98 sampled seconds in
`add_complete_labelling`, including Z3 expression coercion. A longer baseline
profile (`crusti-baseline-long`) ran to 59.99 sampled seconds without a result:
55.96s constructing complete labellings, including **40.99s in redundant
conflict-free constraint construction**, and no solver check reached.

The complete equations already imply conflict-freeness on every defeat:
`out(target)` is the disjunction of its attackers' `in` values, while `in(target)`
and `out(target)` cannot both hold. Removed the additional per-edge clauses when
the conflict relation is contained in defeats. Additional independent attacks
still use the explicit conflict-free encoding. The regression counts at most
three assertions per vertex (old code: 460 assertions for 20 vertices; new: 60),
checks idempotence of subsequent conflict-free setup, and tests the separate
attack relation.

Repaired profile (`crusti-fixed`) finished with a preferred extension of size
126 in 34.00 sampled seconds: 16.41s complete encoding, zero conflict-free
reconstruction, 6.95s in solver checks. The graph parsing improvement is also
present (0.43s vs 1.25s), so this is a combined end-to-end result; the 40.99s
deleted cost and assertion-count contract specifically establish the effect of
removing redundant clauses. Full solving suite: 338 passed, 3 skipped.
The unprofiled 60s single-row runner gate also passed: **solved in 34.095s**,
witness size 126, artifact label `crusti-complete-encoding-fix-20260927`.

## Final validation
- ABA and selected solver/CLI checks: 1546 passed, 3 skipped.
- Follow-up route tests including incomplete-search handling: 11 passed.
- Interop/CLI after parser repair: 112 passed, 1 skipped.
- Full solving suite after AF encoding repair: 338 passed, 3 skipped.
- Pyright with the repository's .venv interpreter: 0 errors.
- Scoped Ruff passed; whitespace checked with CR-at-EOL allowed for existing
  CRLF-tracked source files.
- Full DC-CO gate: frozen manifest in `experiments/iccma-20260927-aba-dcco-manifest.json`;
  60s outer deadline, four workers, all 320 ABA instances. Baseline used eight
  workers and earlier code, so no isolated wall-time speedup claim is made from
  that comparison. Some regression checks and diagnostic probes overlapped the
  gate; counts and answers are the promotion measure, not isolated timing gains.

| DC-CO cohort | Baseline solved / timeout | Fixed solved / timeout |
|---|---:|---:|
| abcgen (120) | 0 / 120 | 72 / 48 |
| other ABA (200) | 160 / 40 | 197 / 3 |
| total (320) | 160 / 160 | 269 / 51 |

**109 recovered timeouts, zero lost solves, zero changed existing answers.** All
269 solved answers agree with the unanimous available YES/NO answers from the
cached official results (`iccma25_aba_results.csv`, excluding timeout/memout
records); none lack an answer or have conflicting official answers. This is an
answer comparison, not certificate validation or an official competition score.
Maximum reported solver calls is one. Results:

- `data/iccma/2025/runs/iccma-2025-dcco-query-fix-20260927.{json,csv}`
- `data/iccma/2025/runs/diagnosis-20260927/dcco-comparison.json`
- `data/iccma/2025/runs/iccma-2025-crusti-complete-encoding-fix-20260927.json`

Promotion decision: accept these scoped repairs on operational contracts,
semantic tests, before/after real-worker profiles, and completed gates. The 51
remaining ABA timeouts are unresolved. The measured hard abcgen representative
now spends its budget in Clingo search; further encoding/search work requires a
new operational contract. Dense-AF parsing is smaller but not eliminated, and
the repaired AF complete encoding still costs 16.41 sampled seconds on the
crusti representative. These are concrete remaining targets, not claims that
the entire ICCMA timeout population has been fixed.
