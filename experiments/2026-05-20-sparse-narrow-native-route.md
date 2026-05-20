# Sparse narrow ABA native route

Date: 2026-05-20

Status: kept on `main`.

Branch: `main`.

Evidence commits:
- `764a6a8` Add sparse narrow ABA SAT fix workstream.
- `c1bc5ab` Add sparse narrow ABA route contracts.
- `4b4ef6f` Add sparse narrow ABA native SAT contracts.
- `0768469` Fix sparse narrow native SAT contract order.
- `46718c1` Add sparse narrow ABA fixture runner.
- `7c10702` Add sparse narrow ABA route policy.
- `6068044` Add sparse narrow ABA native SAT backend.
- `d01b696` Route sparse narrow ABA auto tasks to native SAT.
- `3e16f83` Correct sparse narrow ABA route contracts.
- `fdf3c31` Use unique sparse narrow route fixtures.
- `6a3bf6c` Keep sparse narrow route contract dispatch-only.
- `c96731e` Make sparse narrow fixture runner directly executable.
- `9b2712a` Align sparse narrow route ratio with telemetry.
- `ca53b46` Run sparse narrow fixture rows exactly.

Hypothesis: sparse, narrow, high-cycle ABA rows needed a native SAT path
selected from argument-shape telemetry rather than broad solver dispatch.

Gate: route contracts, native SAT contracts, exact fixture replay, and
dispatch-only route ratio telemetry.

Outcome: kept on `main`.

Reason: it established the correct owned surface for later experiments:
shape-based routing and a native SAT backend. It did not finish the hard row
class; it made failures measurable and isolated.
