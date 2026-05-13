# Wave C4 fixes — 2026-05-12

- P1a: aba.py _defends — removed `attacker and` guard so empty attacker set considered. Done.
- P1b: aba_incremental.py grounded_extension — repoint to grounded_assumption_set_via_supports. In progress (import swapped).
- TODO: update grounded_extension() body, add regression test, P2 assertion, P3 doc annotation, delete bench_scc_b2.py, run suite x2, ruff+pyright, commit, write report.
- bench_scc_b2.py is the only tracked stray root .py file.

## checkpoint 2
- P1a/P1b done. Regression test added to tests/test_aba_multishot.py: _fact_contrary_frameworks + test_grounded_fact_contrary_is_conflict_free + test_solve_aba_grounded_fact_contrary_via_backend. Uses _grounded_reference = min complete via support_extensions (support_extensions doesn't do "grounded").
- Next: run the new test, then P2 (test_aba_preprocessing.py:467), P3 doc, delete bench_scc_b2.py, full suite x2, ruff+pyright, commit, report.

## checkpoint 3
- P2 done: replaced strict equality with native_aba.admissible checks on both. (tests/test_aba_preprocessing.py ~459)
- P3 done: added SUPERSEDED note + row annotations in reports/graph-speedup-wave-c2a-aba-preprocessing.md.
- Pending: rm bench_scc_b2.py, wait for bg test bok1cpuzg, full suite x2, ruff+pyright, commit, write report.

## checkpoint 4
- All code/doc/test edits done. ruff+pyright clean on aba.py, aba_incremental.py, test_aba_multishot.py, test_aba_preprocessing.py. bench_scc_b2.py git-removed.
- Full suite run 1 in bg (byobj0kls); monitor script was broken (no pgrep), need to poll the output file.
- Then run 2, then commit, then write report.

## checkpoint 5 — DONE
- Committed: 598d505 (after one amend). Report references it. Suite 1 failed (kernel ideal AF, pre-existing/unrelated), 2641 passed x2. ruff+pyright clean. Adding a tiny follow-up commit for the report's final hash line.
