# Static SCC loop preload

Date: 2026-05-20

Status: failed and removed.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `cd2fd22` Preload sparse completion SCC loops.
- `9cd40ce` Remove failed static SCC loop preload.

Hypothesis: statically preloading SCC loop constraints would reduce completion
SAT search on sparse cyclic rows.

Gate: focused sparse fixture replay.

Outcome: failed.

Reason: the preload made the solver path worse under the focused gate. Static
SCC loop materialization is not a free win for this class.
