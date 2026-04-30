from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import multiprocessing as mp
from pathlib import Path
import queue
import sys
import time
from typing import Any


DATA_ROOT = Path("data") / "iccma" / "2025"

TASK_TO_SEMANTICS = {
    "CO": "complete",
    "PR": "preferred",
    "ST": "stable",
    "SST": "semi-stable",
    "ID": "ideal",
}

RESULT_FIELDS = [
    "track",
    "subtrack",
    "instance_kind",
    "instance",
    "status",
    "reason",
    "elapsed_seconds",
    "answer",
    "extension_count",
    "witness_size",
    "witness",
    "arguments_or_atoms",
    "attacks",
    "assumptions",
    "rules",
    "contraries",
    "error",
]


@dataclass(frozen=True)
class RunConfig:
    root: Path
    max_af_arguments: int
    max_aba_assumptions: int
    timeout_seconds: float


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run bounded native argumentation algorithms on ICCMA 2025 data."
    )
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    parser.add_argument("--max-af-arguments", type=int, default=100)
    parser.add_argument("--max-aba-assumptions", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--label", default="native-bounded")
    args = parser.parse_args(argv)

    config = RunConfig(
        root=args.root,
        max_af_arguments=args.max_af_arguments,
        max_aba_assumptions=args.max_aba_assumptions,
        timeout_seconds=args.timeout_seconds,
    )
    rows = run_native(config)
    output_dir = config.root / "runs"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"iccma-2025-{args.label}.json"
    csv_path = output_dir / f"iccma-2025-{args.label}.csv"
    summary_path = output_dir / f"iccma-2025-{args.label}-summary.json"
    json_path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(csv_path, rows)
    summary = summarize(rows)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {summary_path}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def run_native(config: RunConfig) -> list[dict[str, Any]]:
    manifest = load_json(config.root / "manifests" / "iccma-2025-manifest.json")
    task_matrix = load_json(config.root / "manifests" / "iccma-2025-task-matrix.json")
    rows: list[dict[str, Any]] = []
    for instance in manifest:
        if instance["kind"] not in {"af", "aba"}:
            continue
        for task in task_matrix:
            if task["instance_kind"] != instance["kind"]:
                continue
            rows.append(run_or_skip(config, instance, task))
    return rows


def run_or_skip(
    config: RunConfig,
    instance: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    base = base_result(instance, task)
    if instance["kind"] == "af" and int(instance["arguments_or_atoms"]) > config.max_af_arguments:
        return {
            **base,
            "status": "skipped",
            "reason": f"af_argument_cap>{config.max_af_arguments}",
        }
    if instance["kind"] == "aba" and int(instance["assumptions"]) > config.max_aba_assumptions:
        return {
            **base,
            "status": "skipped",
            "reason": f"aba_assumption_cap>{config.max_aba_assumptions}",
        }
    job = {
        "root": str(config.root),
        "instance": instance,
        "task": task,
    }
    started = time.perf_counter()
    result = run_child(job, timeout_seconds=config.timeout_seconds)
    elapsed = time.perf_counter() - started
    return {
        **base,
        **result,
        "elapsed_seconds": f"{elapsed:.6f}",
    }


def run_child(job: dict[str, Any], *, timeout_seconds: float) -> dict[str, Any]:
    context = mp.get_context("spawn")
    results = context.Queue()
    process = context.Process(target=worker_entry, args=(job, results))
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "status": "timeout",
            "reason": f"timeout>{timeout_seconds}",
            "error": None,
        }
    try:
        return results.get_nowait()
    except queue.Empty:
        return {
            "status": "error",
            "reason": "worker_no_result",
            "error": f"worker exited with code {process.exitcode}",
        }


def worker_entry(job: dict[str, Any], results) -> None:
    try:
        if job["instance"]["kind"] == "af":
            result = solve_af_job(job)
        else:
            result = solve_aba_job(job)
    except BaseException as exc:
        result = {
            "status": "error",
            "reason": type(exc).__name__,
            "error": str(exc),
        }
    results.put(result)


def solve_af_job(job: dict[str, Any]) -> dict[str, Any]:
    from argumentation.iccma import parse_af
    from argumentation.semantics import extensions

    root = Path(job["root"])
    instance = job["instance"]
    task = job["task"]
    path = root / "extracted" / "instances" / instance["relative_path"]
    query_path = Path(str(path) + ".arg")
    problem, semantics = split_subtrack(task["subtrack"])
    framework = parse_af(path.read_text(encoding="utf-8"))
    extension_sets = extensions(framework, semantics=semantics)
    query = query_path.read_text(encoding="utf-8").strip() if query_path.exists() else None
    return solve_from_extensions(problem, extension_sets, query=query)


def solve_aba_job(job: dict[str, Any]) -> dict[str, Any]:
    from argumentation.aba import (
        complete_extensions,
        derives,
        preferred_extensions,
        stable_extensions,
    )
    from argumentation.aspic import GroundAtom, Literal
    from argumentation.iccma import parse_aba

    root = Path(job["root"])
    instance = job["instance"]
    task = job["task"]
    path = root / "extracted" / "instances" / instance["relative_path"]
    query_path = Path(str(path) + ".query")
    problem, semantics = split_subtrack(task["subtrack"])
    framework = parse_aba(path.read_text(encoding="utf-8"))
    if semantics == "complete":
        extension_sets = complete_extensions(framework)
    elif semantics == "preferred":
        extension_sets = preferred_extensions(framework)
    elif semantics == "stable":
        extension_sets = stable_extensions(framework)
    else:
        raise ValueError(f"unsupported ABA semantics: {semantics}")
    query = None
    if query_path.exists():
        query_name = query_path.read_text(encoding="utf-8").strip()
        query = Literal(GroundAtom(query_name))
    if problem == "SE":
        return solved_se(extension_sets)
    if query is None:
        return {"status": "skipped", "reason": "missing_query", "error": None}
    accepted_by_extension = tuple(derives(framework, extension, query) for extension in extension_sets)
    return solved_decision(problem, extension_sets, accepted_by_extension)


def solve_from_extensions(
    problem: str,
    extension_sets: tuple[frozenset[str], ...],
    *,
    query: str | None,
) -> dict[str, Any]:
    if problem == "SE":
        return solved_se(extension_sets)
    if query is None:
        return {"status": "skipped", "reason": "missing_query", "error": None}
    accepted_by_extension = tuple(query in extension for extension in extension_sets)
    return solved_decision(problem, extension_sets, accepted_by_extension)


def solved_se(extension_sets) -> dict[str, Any]:
    witness = first_extension(extension_sets)
    return {
        "status": "solved",
        "reason": None,
        "answer": None,
        "extension_count": len(extension_sets),
        "witness_size": len(witness) if witness is not None else None,
        "witness": extension_to_text(witness),
        "error": None,
    }


def solved_decision(
    problem: str,
    extension_sets,
    accepted_by_extension: tuple[bool, ...],
) -> dict[str, Any]:
    if problem == "DC":
        answer = any(accepted_by_extension)
        witness = next(
            (extension for extension, accepted in zip(extension_sets, accepted_by_extension) if accepted),
            None,
        )
    elif problem == "DS":
        answer = bool(accepted_by_extension) and all(accepted_by_extension)
        witness = next(
            (extension for extension, accepted in zip(extension_sets, accepted_by_extension) if not accepted),
            None,
        )
    else:
        raise ValueError(f"unsupported problem: {problem}")
    return {
        "status": "solved",
        "reason": None,
        "answer": str(answer).lower(),
        "extension_count": len(extension_sets),
        "witness_size": len(witness) if witness is not None else None,
        "witness": extension_to_text(witness),
        "error": None,
    }


def first_extension(extension_sets) -> frozenset[Any] | None:
    if not extension_sets:
        return None
    return sorted(
        extension_sets,
        key=lambda extension: (len(extension), tuple(sorted(map(repr, extension)))),
    )[0]


def extension_to_text(extension: frozenset[Any] | None) -> str | None:
    if extension is None:
        return None
    return " ".join(sorted((repr(item) for item in extension), key=natural_key))


def natural_key(value: str) -> tuple[int, int | str]:
    return (0, int(value)) if value.isdigit() else (1, value)


def split_subtrack(subtrack: str) -> tuple[str, str]:
    problem, code = subtrack.split("-", maxsplit=1)
    return problem, TASK_TO_SEMANTICS[code]


def base_result(instance: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    return {
        "track": task["track"],
        "subtrack": task["subtrack"],
        "instance_kind": instance["kind"],
        "instance": instance["relative_path"],
        "status": None,
        "reason": None,
        "elapsed_seconds": None,
        "answer": None,
        "extension_count": None,
        "witness_size": None,
        "witness": None,
        "arguments_or_atoms": instance.get("arguments_or_atoms"),
        "attacks": instance.get("attacks"),
        "assumptions": instance.get("assumptions"),
        "rules": instance.get("rules"),
        "contraries": instance.get("contraries"),
        "error": None,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_track: dict[str, int] = {}
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
        by_track[row["track"]] = by_track.get(row["track"], 0) + 1
    return {
        "total_rows": len(rows),
        "by_status": by_status,
        "by_track": by_track,
    }


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
