"""Command-line entry point for ICCMA-style AF solving."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence, TextIO

from argumentation.iccma import parse_af
from argumentation.labelling import ExactEnumerationExceeded
from argumentation.solver import (
    AcceptanceSolverSuccess,
    SingleExtensionSolverSuccess,
    solve_dung_acceptance,
    solve_dung_single_extension,
)


PROBLEM_SEMANTICS = {
    "CO": "complete",
    "GR": "grounded",
    "PR": "preferred",
    "ST": "stable",
    "SST": "semi-stable",
    "STG": "stage",
    "ID": "ideal",
    "CF2": "cf2",
}

TASKS = {"DC", "DS", "SE"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        task, semantics = _parse_problem(args.problem)
        framework = parse_af(args.file.read_text(encoding="utf-8"))
        if task == "SE":
            return _solve_single_extension(
                framework=framework,
                semantics=semantics,
                backend=args.backend,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        if args.argument is None:
            print(f"{task} tasks require -a/--argument", file=sys.stderr)
            return 2
        return _solve_acceptance(
            framework=framework,
            semantics=semantics,
            task="credulous" if task == "DC" else "skeptical",
            query=args.argument,
            backend=args.backend,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except (OSError, ValueError, ExactEnumerationExceeded) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="argumentation.iccma_cli",
        description="Solve ICCMA-style abstract argumentation framework tasks.",
    )
    parser.add_argument("-p", "--problem", required=True, help="ICCMA problem, e.g. SE-ST")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="Path to an ICCMA p af input file",
    )
    parser.add_argument("-a", "--argument", help="Query argument for DC/DS tasks")
    parser.add_argument(
        "--backend",
        choices=("native", "sat"),
        default="native",
        help="In-package exact backend to use",
    )
    return parser


def _parse_problem(problem: str) -> tuple[str, str]:
    parts = problem.upper().split("-", maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"ICCMA problem must look like TASK-SEMANTICS: {problem!r}")
    task, semantics_code = parts
    if task not in TASKS:
        raise ValueError(f"unsupported ICCMA AF task: {task}")
    semantics = PROBLEM_SEMANTICS.get(semantics_code)
    if semantics is None:
        raise ValueError(f"unsupported ICCMA AF semantics code: {semantics_code}")
    return task, semantics


def _solve_single_extension(
    *,
    framework,
    semantics: str,
    backend: str,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    result = solve_dung_single_extension(
        framework,
        semantics=semantics,
        backend=backend,
    )
    if isinstance(result, SingleExtensionSolverSuccess):
        if result.extension is None:
            print("NO", file=stdout)
        else:
            print(_witness_line(result.extension), file=stdout)
        return 0
    print(result.reason, file=stderr)
    return 1


def _solve_acceptance(
    *,
    framework,
    semantics: str,
    task: str,
    query: str,
    backend: str,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    result = solve_dung_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=query,
        backend=backend,
    )
    if isinstance(result, AcceptanceSolverSuccess):
        if result.answer:
            print("YES", file=stdout)
            if task == "credulous":
                print(_witness_line(result.witness), file=stdout)
        else:
            print("NO", file=stdout)
            if task == "skeptical":
                print(_witness_line(result.counterexample), file=stdout)
        return 0
    print(result.reason, file=stderr)
    return 1


def _witness_line(extension: frozenset[object] | None) -> str:
    if extension is None:
        raise ValueError("solver did not return a required certificate")
    return "w" + "".join(f" {argument}" for argument in _sorted_arguments(extension))


def _sorted_arguments(extension: frozenset[object]) -> list[str]:
    arguments = [str(argument) for argument in extension]
    if all(argument.isdigit() for argument in arguments):
        return sorted(arguments, key=int)
    return sorted(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
