"""Run a pytest target under multiple PYTHONHASHSEED values.

Used to prove hashseed-independence of ordering-sensitive tests, e.g.::

    uv run scripts/run_hashseed_matrix.py \
        tests/test_collapsed_profile_summary.py

Runs the target once per seed in a fresh interpreter (PYTHONHASHSEED only
takes effect at interpreter startup) and prints a PASS/FAIL matrix.
Exits nonzero if any seed fails.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


DEFAULT_SEEDS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)


def run_matrix(target: str, seeds: tuple[int, ...]) -> dict[int, bool]:
    results: dict[int, bool] = {}
    for seed in seeds:
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = str(seed)
        env.pop("PYTEST_ADDOPTS", None)
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:randomly", target],
            env=env,
            capture_output=True,
            text=True,
        )
        results[seed] = completed.returncode == 0
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="pytest target (file or node id)")
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="PYTHONHASHSEED values to test (default: 0..9)",
    )
    args = parser.parse_args(argv)

    results = run_matrix(args.target, tuple(args.seeds))
    for seed, passed in results.items():
        print(f"PYTHONHASHSEED={seed}: {'PASS' if passed else 'FAIL'}")
    failures = [seed for seed, passed in results.items() if not passed]
    print(
        f"{len(results) - len(failures)}/{len(results)} seeds passed"
        + (f"; failing seeds: {failures}" if failures else "")
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
