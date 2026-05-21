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

## Retroactive protocol audit

Protocol status: `promotion no-go; diagnosis incomplete`.

This record explains the branch pivot, but it does not include profiler-backed
failure analysis for the learned SAT route itself. It is valid route history,
not a completed mechanism-level experiment failure.

Required follow-up: any return to learned SAT routing needs a focused profile
or telemetry comparison against the completion SAT baseline before another
variant is implemented.
