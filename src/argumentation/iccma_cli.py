"""Command-line entry point for ICCMA-style AF and ABA solving."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence, TextIO

from argumentation.aba import ABAFramework
from argumentation.aspic import Literal
from argumentation.iccma import parse_aba, parse_af
from argumentation.labelling import ExactEnumerationExceeded
from argumentation.solver import (
    AcceptanceSolverSuccess,
    SingleExtensionSolverSuccess,
    solve_aba_acceptance,
    solve_aba_single_extension,
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
        text = args.file.read_text(encoding="utf-8")
        kind = _instance_kind(text)
        if kind == "aba":
            return _solve_aba_cli(
                text=text,
                task=task,
                semantics=semantics,
                query_argument=args.argument,
                backend=args.backend,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        framework = parse_af(text)
        if task == "SE":
            return _solve_af_single_extension(
                framework=framework,
                semantics=semantics,
                backend=_af_backend(args.backend, semantics),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        if args.argument is None:
            print(f"{task} tasks require -a/--argument", file=sys.stderr)
            return 2
        return _solve_af_acceptance(
            framework=framework,
            semantics=semantics,
            task="credulous" if task == "DC" else "skeptical",
            query=args.argument,
            backend=_af_backend(args.backend, semantics),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except (OSError, ValueError, ExactEnumerationExceeded) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="argumentation.iccma_cli",
        description="Solve ICCMA-style abstract argumentation tasks.",
    )
    parser.add_argument("-p", "--problem", required=True, help="ICCMA problem, e.g. SE-ST")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="Path to an ICCMA p af or p aba input file",
    )
    parser.add_argument("-a", "--argument", help="Query argument for DC/DS tasks")
    parser.add_argument(
        "--backend",
        choices=("auto", "native", "sat"),
        default="auto",
        help="In-package backend to use",
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


def _instance_kind(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[:2] == ["p", "af"]:
            return "af"
        if parts[:2] == ["p", "aba"]:
            return "aba"
        break
    raise ValueError("ICCMA input must start with a p af or p aba header")


def _af_backend(requested: str, semantics: str) -> str:
    if requested == "auto":
        return "sat" if semantics == "stable" else "native"
    return requested


def _solve_af_single_extension(
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


def _solve_af_acceptance(
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


def _solve_aba_cli(
    *,
    text: str,
    task: str,
    semantics: str,
    query_argument: str | None,
    backend: str,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    if backend == "sat":
        print("ABA tasks do not support --backend sat", file=stderr)
        return 2
    framework = parse_aba(text)
    if task == "SE":
        return _solve_aba_single_extension(
            framework=framework,
            semantics=semantics,
            stdout=stdout,
            stderr=stderr,
        )
    if query_argument is None:
        print(f"{task} tasks require -a/--argument", file=stderr)
        return 2
    query = _aba_query(framework, query_argument)
    return _solve_aba_acceptance(
        framework=framework,
        semantics=semantics,
        task="credulous" if task == "DC" else "skeptical",
        query=query,
        stdout=stdout,
        stderr=stderr,
    )


def _solve_aba_single_extension(
    *,
    framework: ABAFramework,
    semantics: str,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    result = solve_aba_single_extension(
        framework,
        semantics=semantics,
        backend="native",
    )
    if isinstance(result, SingleExtensionSolverSuccess):
        if result.extension is None:
            print("NO", file=stdout)
        else:
            print(_aba_witness_line(framework, result.extension), file=stdout)
        return 0
    print(result.reason, file=stderr)
    return 1


def _solve_aba_acceptance(
    *,
    framework: ABAFramework,
    semantics: str,
    task: str,
    query: Literal,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=task,
        query=query,
        backend="native",
    )
    if isinstance(result, AcceptanceSolverSuccess):
        print("YES" if result.answer else "NO", file=stdout)
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


def _aba_witness_line(framework: ABAFramework, extension: frozenset[object]) -> str:
    literal_ids = _aba_literal_ids(framework)
    ids: list[str] = []
    for item in extension:
        if not isinstance(item, Literal):
            raise ValueError("ABA solver returned a non-literal witness member")
        if item not in framework.assumptions:
            continue
        ids.append(literal_ids[item])
    return "w" + "".join(f" {atom_id}" for atom_id in sorted(ids, key=_numeric_sort_key))


def _aba_query(framework: ABAFramework, atom_id: str) -> Literal:
    by_id = {value: literal for literal, value in _aba_literal_ids(framework).items()}
    try:
        return by_id[atom_id]
    except KeyError as exc:
        raise ValueError(f"query atom is not in framework language: {atom_id!r}") from exc


def _aba_literal_ids(framework: ABAFramework) -> dict[Literal, str]:
    numeric = {
        literal: literal.atom.predicate
        for literal in framework.language
        if not literal.negated
        and not literal.atom.arguments
        and literal.atom.predicate.isdigit()
    }
    if len(numeric) == len(framework.language):
        return numeric
    return {
        literal: str(index)
        for index, literal in enumerate(sorted(framework.language, key=repr), start=1)
    }


def _numeric_sort_key(value: str) -> tuple[int, str]:
    return (int(value), "") if value.isdigit() else (sys.maxsize, value)


if __name__ == "__main__":
    raise SystemExit(main())
