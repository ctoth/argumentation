"""End-to-end probe of the production SE-ST path on the exp-4B named rows.

Calls exactly what tools/iccma2025_run_native.py's solve_aba_job calls
(`solve_aba_single_extension` with backend=auto) and times it, printing the
route metadata and witness size. Run on branch code to demonstrate the named
rows solving; run detached at main to demonstrate the hang (with an external
kill).

Usage:
    uv run scripts/probe_aba_sest_named_row.py
"""

from __future__ import annotations

import time
from pathlib import Path

from argumentation.interop.iccma import parse_aba
from argumentation.solving.solver import (
    SingleExtensionSolverSuccess,
    solve_aba_single_extension,
)

DATA_ROOT = Path(
    r"C:\Users\Q\code\argumentation\data\iccma\2025\extracted\instances\ABAs"
)
NAMED_ROWS = ("aba_2000_0.1_5_5_1.aba", "aba_2000_0.1_5_5_6.aba")


def main() -> None:
    for name in NAMED_ROWS:
        framework = parse_aba((DATA_ROOT / name).read_text(encoding="utf-8"))
        started = time.perf_counter()
        result = solve_aba_single_extension(
            framework, semantics="stable", backend="auto"
        )
        elapsed = time.perf_counter() - started
        if isinstance(result, SingleExtensionSolverSuccess):
            witness = result.extension
            solver = (result.metadata or {}).get("solver")
            preprocessing = (result.metadata or {}).get("preprocessing")
            print(
                f"{name}: solved in {elapsed:.3f}s "
                f"witness_size={None if witness is None else len(witness)} "
                f"solver={solver} preprocessing={preprocessing}"
            )
        else:
            print(f"{name}: {type(result).__name__} after {elapsed:.3f}s: {result!r}")


if __name__ == "__main__":
    main()
