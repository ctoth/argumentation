# Clingo 5.8.0 -> 5.8.2 bump (2026-09-28)

- Branch: deps/clingo-5.8.2 (from main 985d456)
- `uv lock --upgrade-package clingo`: only clingo changed in uv.lock (5.8.0 -> 5.8.2)
- `uv sync` installed clingo 5.8.2; also removed stray python-chess 1.999 (not in lock)
- Full pytest: 3537 passed, 4 skipped, 1 xfailed (logs/clingo-5.8.2-pytest.log)
- Perf contracts (calibrated, opt-in): 8 passed. Committed c189539.
- A/B of 22 clingo-backed test files (1467 tests), alternating: 5.8.0 219.5s/220.8s, 5.8.2 213.9s/217.7s. Env restored to 5.8.2. DONE (not pushed).
- (old) Next: opt-in wall-clock perf contracts (ARGUMENTATION_PERF_CONTRACTS=1, calibrated via tools/perf_calibrate.py), then commit.
