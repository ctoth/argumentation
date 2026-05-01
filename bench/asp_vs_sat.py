"""Run small ASP-vs-reference backend benchmarks and write CSV output."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from time import perf_counter

from argumentation.aba_asp import solve_aba_with_backend
from argumentation.aspic_encoding import solve_aspic_with_backend

from bench.instance_gen import aba_chain, aspic_chain


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="out/asp-vs-reference.csv")
    parser.add_argument("--sizes", nargs="*", type=int, default=[5, 10, 20, 40])
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for size in args.sizes:
        rows.extend(_run_aba(size, args.timeout))
        rows.extend(_run_aspic(size, args.timeout))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["family", "size", "semantics", "backend", "status", "extensions", "seconds"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _run_aba(size: int, timeout: float) -> list[dict[str, str]]:
    framework = aba_chain(size)
    rows = []
    for semantics in ("complete", "stable", "preferred"):
        for backend in ("support_reference", "asp"):
            start = perf_counter()
            result = solve_aba_with_backend(
                framework,
                backend=backend,
                semantics=semantics,
                timeout_seconds=timeout,
            )
            rows.append(_row("aba", size, semantics, backend, result.status, len(result.extensions), start))
    return rows


def _run_aspic(size: int, timeout: float) -> list[dict[str, str]]:
    system, kb, pref = aspic_chain(size)
    rows = []
    for semantics in ("grounded", "complete", "stable", "preferred"):
        for backend in ("materialized_reference", "asp"):
            start = perf_counter()
            result = solve_aspic_with_backend(
                system,
                kb,
                pref,
                backend=backend,
                semantics=semantics,
                timeout_seconds=timeout,
            )
            rows.append(_row("aspic", size, semantics, backend, result.status, len(result.extensions), start))
    return rows


def _row(
    family: str,
    size: int,
    semantics: str,
    backend: str,
    status: str,
    extension_count: int,
    start: float,
) -> dict[str, str]:
    return {
        "family": family,
        "size": str(size),
        "semantics": semantics,
        "backend": backend,
        "status": status,
        "extensions": str(extension_count),
        "seconds": f"{perf_counter() - start:.6f}",
    }


if __name__ == "__main__":
    main()
