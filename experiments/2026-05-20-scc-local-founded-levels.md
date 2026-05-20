# SCC-local founded levels

Date: 2026-05-20

Status: failed and removed.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `0936d01` Add SCC-local founded level mapping.
- `680eccf` Restrict founded levels to large SCCs.
- `a82c413` Remove failed SCC level mapping.

Hypothesis: founded-level variables local to SCCs would constrain completion
SAT models enough to reduce hard-row search.

Gate: focused five-row fixture replay.

Outcome: failed.

Reason: the broad level mapping regressed the gate; restricting it avoided
some damage but did not solve the remaining hard row. The whole level-mapping
path was removed from the branch.
