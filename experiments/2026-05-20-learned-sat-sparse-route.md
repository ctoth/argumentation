# Learned SAT sparse route

Date: 2026-05-20

Status: abandoned as the primary route; superseded by completion SAT work.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `4546a07` Add learned SAT salvage workstream.
- `8e6530e` Add sparse propagator focused fixture.
- `ffeb22a` Allow focused sparse fixture runs.
- `8f40c7c` Add learned SAT sparse narrow contracts.
- `9993a98` Add sparse learned SAT route predicate.
- `75253fe` Add sparse narrow learned SAT engine.
- `9bfe812` Route high cycle sparse ABA to learned SAT.

Hypothesis: a learned SAT engine for sparse narrow rows would outperform the
existing native route on the hard high-cycle cluster.

Gate: learned-route contracts plus focused sparse fixture replay.

Outcome: abandoned as the primary route.

Reason: the route created the right experimental surface but did not solve
the hard class. Later commits moved from this general learned route into the
more specific completion SAT direction.

Profiled failure evidence:
- Run artifacts:
  `data\iccma\2025\runs\shape-profile-learned-sat.json`,
  `data\iccma\2025\runs\shape-profile-learned-sat-reuse.json`,
  `data\iccma\2025\runs\shape-profile-learned-sat-bounded-coverage.json`,
  `data\iccma\2025\runs\shape-profile-learned-sat-direct.json`.
- These runs profiled the hard row
  `ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba` for about
  `10s` each and did not return a solved witness during the profile window.
- Relevant raw profile:
  `data\iccma\2025\profiles\aba-SE-ST-auto-abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba-d62d9f410a29.raw.txt`
- The dominant observed stack is
  `native_sparse_narrow_learned_sat_extension ->
  _native_sparse_narrow_learned_completion_stable_result -> stable_extension ->
  solve (pysat\solvers.py)`, with a sampled stack at `959`.
- Python route telemetry, completion construction, and support clause setup are
  visible but small compared with the solver stack.

Failure diagnosis: the general learned-SAT sparse route did not fail because
the routing predicate, closure reuse, or coverage wrapper was obviously eating
the runtime. It reached the intended SAT engine and then spent the profile
window in CDCL search. The pivot to completion SAT was justified because the
problem was formula/search shape, not another missing Python-side route tweak.

## Retroactive protocol audit

Protocol status: `promotion no-go; profiled family-level diagnosis complete`.

This record explains the branch pivot and now includes profiler-backed failure
analysis for the learned SAT route family. It is valid route history plus a
mechanism-level warning: the route reached SAT solving, and solving dominated.

Required follow-up: any return to learned SAT routing must state an operational
contract that changes formula/search behavior, not merely a different way to
enter the same SAT solve.
