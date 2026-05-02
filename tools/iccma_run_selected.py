from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.iccma2025_run_native import run_child


def run_selected(
    *,
    root: Path,
    relative_path: str,
    kind: str,
    subtrack: str,
    backend: str,
    timeout_seconds: float,
    arguments_or_atoms: int | None = None,
    track: str = "legacy",
    instance_kind: str = "af",
    iccma_binary: str | None = None,
) -> dict[str, Any]:
    job = {
        "root": str(root),
        "backend": backend,
        "iccma_binary": iccma_binary,
        "solver_timeout_seconds": timeout_seconds,
        "instance": {
            "kind": kind,
            "relative_path": relative_path,
            "arguments_or_atoms": arguments_or_atoms,
        },
        "task": {
            "track": track,
            "subtrack": subtrack,
            "instance_kind": instance_kind,
        },
    }
    return run_child(job, timeout_seconds=timeout_seconds)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one ICCMA row through the native runner worker.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--relative-path", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--subtrack", required=True)
    parser.add_argument("--backend", default="auto")
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--arguments-or-atoms", type=int)
    parser.add_argument("--track", default="legacy")
    parser.add_argument("--instance-kind", default="af")
    parser.add_argument("--iccma-binary")
    args = parser.parse_args(argv)

    row = run_selected(
        root=args.root,
        relative_path=args.relative_path,
        kind=args.kind,
        subtrack=args.subtrack,
        backend=args.backend,
        timeout_seconds=args.timeout_seconds,
        arguments_or_atoms=args.arguments_or_atoms,
        track=args.track,
        instance_kind=args.instance_kind,
        iccma_binary=args.iccma_binary,
    )
    print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
