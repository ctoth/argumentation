# Completion SAT learned route

Date: 2026-05-20

Status: kept on experiment branch; not promoted to `main` in the verified state.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `bb46498` Add completion SAT learned route workstream.
- `52ad3b2` Require completion SAT learned route contracts.
- `dd9667e` Use completion SAT for learned sparse ABA route.
- `5512441` Preload completion SAT singleton attacks.
- `7886f75` Account for completion SAT singleton probes.
- `721a967` Use CaDiCaL for sparse completion SAT.
- `c1f8c4d` Optimize completion SAT loop clauses.

Hypothesis: completion SAT, seeded with singleton attack information and using
CaDiCaL, would be the strongest known route for the sparse narrow hard class.

Gate: targeted learned SAT contract tests and focused five-row fixture replay.

Outcome: kept on the branch baseline.

Reason: this became the strongest verified branch path: targeted tests passed
and the focused gate reached four solved rows with one remaining timeout in
the prior run record. It was not yet merged to `main` when this file was
written.
