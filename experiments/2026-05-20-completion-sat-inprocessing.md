# Completion SAT CaDiCaL inprocessing

Date: 2026-05-20

Status: failed and reverted.

Branch: `exp/aba-sparse-narrow-learned-sat`.

Evidence commits:
- `00d81e2` Add completion SAT inprocessing workstream.
- `b5f2716` Require learned SAT inprocessing telemetry.
- `bd9cf3b` Run CaDiCaL inprocessing for completion SAT.
- `105da14` Revert "Run CaDiCaL inprocessing for completion SAT".
- `8317568` Revert "Require learned SAT inprocessing telemetry".
- `0b36c55` Record failed completion SAT inprocessing.

Hypothesis: CaDiCaL inprocessing on the exact completion formula would simplify
the hard rows enough to improve the focused gate.

Gate: targeted tests and focused five-row fixture replay.

Outcome: failed.

Reason: inprocessing regressed the focused gate. Prior recorded result was
three solved and two timed out, including a row that slowed from about 1.2s to
timeout. The change was reverted.
