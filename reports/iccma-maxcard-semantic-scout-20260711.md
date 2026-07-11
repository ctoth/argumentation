# Round-1 ICCMA max-cardinality SE-PR semantic scout

Date: 2026-07-11
Role: read-only semantic scout
Tracked HEAD inspected: `6929ab74d83ac8ea83a06200204b744e722442a0` (`main`)
Holdout: not accessed
Source changes, solver runs, and commits: none

## Decision

**KILL: invalid duplicate of an already implemented and diagnosed campaign
candidate.**

This is not a semantic refutation of the maximum-cardinality theorem. The
candidate is invalid for new Round-1 implementation research because committed
history already contains the exact one-shot construction and its failed
operational diagnosis.

Per the campaign invalidity rule, research stopped after establishing that
identity. No new implementation design, differential-contract design, source
inspection beyond the identifying committed records, or benchmark work was
performed.

## Exact committed precedent

The branch `experiment/aba-asp-saturation-preferred` contains the completed
workstream `workstreams/aba-asp-saturation-preferred-backend.md`. Its production
hypothesis was exactly the requested candidate:

- compute complete assumption sets with the Lehtonen `pi_com` encoding;
- add the global objective `#maximize { 1,X : in(X) }.`;
- wait for the proved optimum rather than return the first improving model;
- return that single optimized set through `find_preferred_extension` as the
  existing SE-PR single-extension result shape.

The implementation lineage is committed, including:

- `fe1c317` — `Add ABA ASP saturation properties`;
- `aa56b7c` — `Use ASP maximality for preferred witness`;
- `b6c9b1d` — `Return optimal preferred witness`;
- `408f4b0` — `Record failed ASP maximality gate`.

Thus this was not merely proposed. It was implemented, semantically gated,
benchmarked, and retained as a failed experiment record.

## Existing semantic and task diagnosis

The committed workstream records that the local semantic contract passed
(`16 passed in 3.17s`) and the broader preferred/regression gate passed
(`1061 passed in 124.54s`). The candidate was specifically a flat-ABA
single-extension preferred witness path. It did not claim canonical witness
identity, preferred enumeration, skeptical preferred acceptance, or ABA+
coverage.

The mathematical reason recorded by the campaign is the standard finite-set
implication: a globally maximum-cardinality complete set cannot have a strict
complete superset, so it is inclusion-maximal complete and therefore
preferred. The experiment encoded global optimality, not a heuristic
high-cardinality approximation.

Because the exact candidate has already passed its semantic gates, reopening
new cases for the empty framework, incomparable preferred extensions of
different sizes, cyclic or unfounded derivations, or the flat/ABA+ boundary
would not cure the diagnosed campaign failure. Those cases would be relevant
to a genuinely new encoding or expanded task surface, but adding them here
would improperly salvage an invalid duplicate into follow-up test work.

## Existing operational diagnosis

The targeted 30-second gate covered flat-ABA SE-PR rows T1, T3, T5, T6, and
T8. Every target timed out under `auto`, `asp`, and `sat`; zero required
preferred targets improved. Controls C1, C2, and C3 retained the recorded
solved routes. The branch therefore was not promoted.

Main records the same conclusion in
`reports/aba-preferred-salvage-inventory.md`: the rejected production path was
a "single ASP optimization over the Lehtonen complete program with `#maximize`
for preferred witnesses"; semantic and regression tests passed, but all five
hard preferred rows timed out. The recorded class-level diagnosis is that
global optimization over complete extensions does not solve the dense
preferred family.

## Contract disposition

No new executable semantic differential contracts are specified in this
scout. The user's conditional instruction requires stopping when the exact
candidate is already tried and diagnosed, and the committed workstream already
contains its semantic and operational gates. Designing another native/support
differential suite or extending the query surface would be new scope rather
than evidence that this candidate is untried.

A future campaign item must therefore be materially different from global
maximum-cardinality optimization over complete/admissible sets and must state
its own executable semantic and operational contracts before implementation.
