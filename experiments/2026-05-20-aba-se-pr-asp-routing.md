# ABA SE-PR ASP auto routing

## Branch

- `exp/aba-se-pr-asp-routing`

## Hypothesis

Since explicit ASP solved one preferred timeout row that `auto` and explicit SAT
timed out on, routing sparse/narrow `SE-PR` auto through ASP would improve the
full 10x10 fixture from `9/20` solved to at least `10/20` solved.

## Commits and Changed Paths

- `ddaaff5` `tests/test_aba_sparse_narrow_route_contract.py`
  - Changed preferred sparse/narrow auto route contract to require ASP/clingo.
  - Added explicit preferred `backend="sat"` native SAT preservation test.
- `6c30f97` `src/argumentation/solver.py`
  - Deleted the preferred sparse/narrow auto `"sat"` override in
    `_auto_aba_backend_for_framework`.

These source/test commits were not promoted because the metric gate failed.

## Gates

Route contract red check before production edit:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Outcome: `1 failed, 6 passed`. Preferred sparse/narrow auto still called native
SAT.

Route contract after production edit:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py
```

Outcome: `7 passed in 0.97s`.

Focused regression gate:

```powershell
uv run pytest -q tests\test_aba_sparse_narrow_route_contract.py tests\test_aba_sparse_narrow_native_sat.py tests\test_solver_availability.py
```

Outcome: `49 passed in 1.47s`.

Full 10x10 gate:

```powershell
uv run tools\run_aba_10x10_fixture.py --fixture tests\manifests\iccma2025-abcgen-10x10.json --timeout-seconds 30 --backend auto --output-json data\iccma\2025\runs\aba-se-pr-asp-routing-10x10.json --event-log-path data\iccma\2025\runs\aba-se-pr-asp-routing-10x10.events.jsonl
```

Outcome: `9` solved, `11` timeout, `14` clingo solver calls, `0` native SAT
routes.

The pass requirement was at least `10` solved and at most `10` timeouts. This
gate failed.

## What Happened

The preferred rows did route through ASP, and the small preferred rows solved
with `solver="clingo_multishot"`. The boundary preferred row
`ABAs/abcgen_c7_atoms150_asms100_mra3_mbs2_cp0.8_ins1.aba` timed out in the
full 10x10 fixture at `30.009533` seconds, even though it had solved in the
isolated ASP-vs-SAT measurement near the timeout boundary.

## Generated Diagnostics

Generated and not committed:

- `data/iccma/2025/runs/aba-se-pr-asp-routing-10x10.json`
- `data/iccma/2025/runs/aba-se-pr-asp-routing-10x10.events.jsonl`

## Decision

Abandon the production route change.

Why:

- The operational metric did not improve the full fixture.
- The isolated preferred ASP win is too close to the timeout boundary to justify
  changing production routing.
- Keeping the source delta would replace a passing production route with an
  unproven one.

Next useful experiment is not blanket `SE-PR` ASP routing. The better target is
the boundary preferred row itself: either reduce ASP preferred solve time below
the 30 second gate with an operational contract, or leave `SE-PR` auto on the
current route.

