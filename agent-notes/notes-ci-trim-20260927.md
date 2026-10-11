CI checkpoint: isolated worktree C:/Users/Q/code/argumentation-ci, branch ci/trim-python-matrix.
PR https://github.com/ctoth/argumentation/pull/83 is open and unmerged; head e2cbbaba5922402814d1ac376193ac83eaaab33d.
Restricted pushes to main, retained Python 3.11/3.14, deduplicated static/build checks, added locked sync, cancellation, timeout, action pins and Dependabot.
Hosted run 36301959093 passed both jobs: each 3266 passed, 7 skipped, 1 xfailed; local actionlint, zizmor, Pyright, import contracts and build passed. No blocker.
Follow-up: reproduced existing sensitivity xfail at tests/gradual/test_sensitivity.py:311; it encodes a disproven attack-removal monotonicity conjecture. Explained to user; no further change requested. Checkpoint remains uncommitted.
