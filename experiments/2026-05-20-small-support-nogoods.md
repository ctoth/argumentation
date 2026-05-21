# Small support attack nogoods

Date: 2026-05-20

Status: kept on experiment branch.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commit:
- `c1cd687` Preload small support attack nogoods.

Hypothesis: support attacks of bounded small size can be compiled into
nogoods before SAT search, reducing candidate work without overloading the
solver.

Gate: targeted tests and focused five-row fixture replay.

Outcome: kept on the branch baseline.

Reason: small support nogoods were the best concrete improvement in the
completion SAT line. The later larger-support experiment was not kept, so the
recorded limit is small support only.

## Retroactive protocol audit

Protocol status: kept branch improvement; broader mechanism diagnosis partial.

This record identifies a kept boundary: small support nogoods helped enough to
remain in the branch baseline while larger support nogoods did not. It is a
valid comparative result, but it does not fully explain the SAT-search
mechanism.

Required follow-up: if expanding beyond small support, collect solver telemetry
that shows why the added nogoods reduce rather than worsen search.
