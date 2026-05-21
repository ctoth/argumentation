# Sparse ABA loop formulas and ranked closure

Date: 2026-05-20

Status: partially kept, failed strengthening reverted on `main`.

Branch: `main`.

Evidence commits:
- `47deb57` Encode sparse narrow stable ABA with loop formulas.
- `d65abf9` Learn component loop formulas for sparse ABA.
- `adf521f` Strengthen sparse ABA loop clauses.
- `9ddb563` Revert regressing sparse ABA loop strengthening.
- `612a385` Add ranked closure to sparse ABA SAT.
- `ed6b06d` Revert "Add ranked closure to sparse ABA SAT".

Hypothesis: foundedness-style loop constraints and ranked closure could make
the sparse stable search converge faster.

Gate: focused sparse narrow fixture replay and regression checks.

Outcome: basic loop-formula work remained, but strengthening and ranked
closure were reverted.

Reason: the stronger loop clauses and ranked closure changed the operational
shape in the wrong direction under the gate. The recorded lesson is not
"more constraints are faster"; the useful part must be contract-checked by
row shape and solver behavior.

## Retroactive protocol audit

Protocol status: partially kept result; failed strengthening diagnosis
incomplete.

The basic loop-formula work remained guarded by tests and gates, but the failed
strengthening/ranked-closure slices do not have profiler-backed explanation in
this record. Treat those failed slices as promotion no-go, not complete
mechanism-level failures.

Required follow-up: any stronger loop/ranked-closure retry must compare solver
telemetry or profile evidence before and after the added constraints.
