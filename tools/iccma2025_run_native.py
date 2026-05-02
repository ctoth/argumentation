from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import lzma
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


DATA_ROOT = Path("data") / "iccma" / "2025"

AF_KINDS = frozenset({"af", "apx", "tgf", "compressed_apx", "compressed_tgf"})

TASK_TO_SEMANTICS = {
    "CO": "complete",
    "GR": "grounded",
    "PR": "preferred",
    "ST": "stable",
    "SST": "semi-stable",
    "STG": "stage",
    "ID": "ideal",
    "CF2": "cf2",
}

DEFAULT_AF_SUBTRACKS = (
    "DC-CO",
    "DC-PR",
    "DC-ST",
    "DC-SST",
    "DS-PR",
    "DS-ST",
    "DS-SST",
    "SE-CO",
    "SE-GR",
    "SE-PR",
    "SE-ST",
    "SE-SST",
    "SE-ID",
)

RESULT_FIELDS = [
    "track",
    "subtrack",
    "instance_kind",
    "instance",
    "backend",
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
    backend: str
    iccma_binary: str | None
    max_af_arguments: int
    max_aba_assumptions: int
    timeout_seconds: float
    progress: bool


def main(argv: list[str] | None = None) -> int:
    if argv and argv[0] == "_worker":
        return worker_main(argv[1:])
    parser = argparse.ArgumentParser(
        description="Run bounded native or ICCMA-backed algorithms on ICCMA 2025 data."
    )
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    parser.add_argument("--backend", choices=["auto", "native", "iccma"], default="auto")
    parser.add_argument(
        "--iccma-binary",
        default=os.environ.get("ICCMA_AF_SOLVER"),
        help="ICCMA AF solver binary for --backend iccma; defaults to ICCMA_AF_SOLVER.",
    )
    parser.add_argument("--max-af-arguments", type=int, default=100)
    parser.add_argument("--max-aba-assumptions", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--label", default="native-bounded")
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable per-row JSON progress logs on stderr.",
    )
    args = parser.parse_args(argv)

    config = RunConfig(
        root=args.root,
        backend=args.backend,
        iccma_binary=args.iccma_binary,
        max_af_arguments=args.max_af_arguments,
        max_aba_assumptions=args.max_aba_assumptions,
        timeout_seconds=args.timeout_seconds,
        progress=not args.no_progress,
    )
    rows = run_native(config)
    output_dir = config.root / "runs"
    output_dir.mkdir(parents=True, exist_ok=True)
    contest_tag = infer_contest_tag(config.root)
    json_path = output_dir / f"{contest_tag}-{args.label}.json"
    csv_path = output_dir / f"{contest_tag}-{args.label}.csv"
    summary_path = output_dir / f"{contest_tag}-{args.label}-summary.json"
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
    manifest_path, task_matrix_path = discover_manifest_paths(config.root)
    manifest = load_json(manifest_path)
    task_matrix = (
        load_json(task_matrix_path)
        if task_matrix_path is not None
        else infer_task_matrix(config.root, manifest)
    )
    jobs = [
        (instance, task)
        for instance in manifest
        if normalized_instance_kind(instance) in {"af", "aba"}
        for task in task_matrix
        if task["instance_kind"] == normalized_instance_kind(instance)
    ]
    rows: list[dict[str, Any]] = []
    for index, (instance, task) in enumerate(jobs, start=1):
        row = run_or_skip(config, instance, task)
        rows.append(row)
        if config.progress:
            log_progress(row, index=index, total=len(jobs))
    return rows


def infer_contest_tag(root: Path) -> str:
    if root.name.isdigit():
        return f"iccma-{root.name}"
    manifests_dir = root / "manifests"
    manifest_paths = sorted(manifests_dir.glob("iccma-*-manifest.json"))
    if manifest_paths:
        return manifest_paths[0].name.removesuffix("-manifest.json")
    return "iccma"


def discover_manifest_paths(root: Path) -> tuple[Path, Path | None]:
    manifests_dir = root / "manifests"
    manifest_paths = sorted(manifests_dir.glob("iccma-*-manifest.json"))
    if len(manifest_paths) != 1:
        raise FileNotFoundError(
            f"expected exactly one ICCMA manifest in {manifests_dir}, found {len(manifest_paths)}"
        )
    contest_tag = manifest_paths[0].name.removesuffix("-manifest.json")
    task_matrix_path = manifests_dir / f"{contest_tag}-task-matrix.json"
    return manifest_paths[0], task_matrix_path if task_matrix_path.exists() else None


def normalized_instance_kind(instance: dict[str, Any]) -> str:
    kind = instance["kind"]
    return "af" if kind in AF_KINDS else kind


def infer_task_matrix(root: Path, manifest: list[dict[str, Any]]) -> list[dict[str, str]]:
    has_af = any(normalized_instance_kind(instance) == "af" for instance in manifest)
    if not has_af:
        return []
    subtracks = infer_af_subtracks(root)
    return [
        {"track": "legacy", "subtrack": subtrack, "instance_kind": "af"}
        for subtrack in subtracks
    ]


def infer_af_subtracks(root: Path) -> tuple[str, ...]:
    result_files = sorted((root / "extracted" / "results").glob("*.results"))
    subtracks = [
        path.name.removesuffix(".results")
        for path in result_files
        if supported_runner_subtrack(path.name.removesuffix(".results"))
    ]
    if subtracks:
        return tuple(dict.fromkeys(subtracks))
    return DEFAULT_AF_SUBTRACKS


def supported_runner_subtrack(subtrack: str) -> bool:
    parts = subtrack.split("-", maxsplit=1)
    return len(parts) == 2 and parts[0] in {"DC", "DS", "SE"} and parts[1] in TASK_TO_SEMANTICS


def log_progress(row: dict[str, Any], *, index: int, total: int) -> None:
    event = {
        "event": "iccma_row",
        "index": index,
        "total": total,
        "track": row["track"],
        "subtrack": row["subtrack"],
        "instance_kind": row["instance_kind"],
        "instance": row["instance"],
        "backend": row["backend"],
        "status": row["status"],
        "reason": row["reason"],
        "elapsed_seconds": row["elapsed_seconds"],
        "answer": row["answer"],
    }
    print(json.dumps(event, sort_keys=True), file=sys.stderr, flush=True)


def run_or_skip(
    config: RunConfig,
    instance: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    base = {**base_result(instance, task), "backend": config.backend}
    if (
        normalized_instance_kind(instance) == "af"
        and config.max_af_arguments >= 0
        and instance.get("arguments_or_atoms") is not None
        and int(instance["arguments_or_atoms"]) > config.max_af_arguments
    ):
        return {
            **base,
            "status": "skipped",
            "reason": f"af_argument_cap>{config.max_af_arguments}",
        }
    if (
        normalized_instance_kind(instance) == "aba"
        and instance.get("assumptions") is not None
        and int(instance["assumptions"]) > config.max_aba_assumptions
    ):
        return {
            **base,
            "status": "skipped",
            "reason": f"aba_assumption_cap>{config.max_aba_assumptions}",
        }
    job = {
        "root": str(config.root),
        "backend": config.backend,
        "iccma_binary": config.iccma_binary,
        "solver_timeout_seconds": config.timeout_seconds,
        "instance": instance,
        "task": task,
    }
    started = time.perf_counter()
    result = run_child(job, timeout_seconds=config.timeout_seconds + 10.0)
    elapsed = time.perf_counter() - started
    return {
        **base,
        **result,
        "elapsed_seconds": f"{elapsed:.6f}",
    }


def run_child(job: dict[str, Any], *, timeout_seconds: float) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".json",
        delete=False,
    ) as handle:
        json.dump(job, handle)
        job_path = Path(handle.name)
    try:
        process = subprocess.Popen(
            [sys.executable, __file__, "_worker", str(job_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        def collect_stdout() -> None:
            assert process.stdout is not None
            stdout_lines.extend(process.stdout.readlines())

        def forward_stderr() -> None:
            assert process.stderr is not None
            for line in process.stderr:
                stderr_lines.append(line)
                print(line, end="", file=sys.stderr, flush=True)

        stdout_thread = threading.Thread(target=collect_stdout, daemon=True)
        stderr_thread = threading.Thread(target=forward_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        try:
            returncode = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)
            return {
                "status": "timeout",
                "reason": f"timeout>{timeout_seconds}",
                "error": None,
            }
        stdout_thread.join()
        stderr_thread.join()
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "reason": f"timeout>{timeout_seconds}",
            "error": None,
        }
    finally:
        job_path.unlink(missing_ok=True)
    stdout = "".join(stdout_lines)
    stderr = "".join(stderr_lines)
    if returncode != 0:
        return {
            "status": "error",
            "reason": "worker_nonzero_exit",
            "error": (stderr or stdout).strip(),
        }
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "reason": "worker_bad_json",
            "error": f"{exc}: {stdout!r}",
        }


def worker_main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("_worker requires a job json path", file=sys.stderr)
        return 2
    job = load_json(Path(argv[0]))
    print(json.dumps(worker_solve(job), sort_keys=True))
    return 0


def worker_solve(job: dict[str, Any]) -> dict[str, Any]:
    try:
        if normalized_instance_kind(job["instance"]) == "af":
            result = solve_af_job(job)
        else:
            result = solve_aba_job(job)
    except BaseException as exc:
        result = {
            "status": "error",
            "reason": type(exc).__name__,
            "error": str(exc),
        }
    return result


def resolve_instance_path(root: Path, instance: dict[str, Any]) -> Path:
    instances_root = root / "extracted" / "instances"
    relative = Path(instance["relative_path"])
    direct = instances_root / relative
    if direct.exists():
        return direct

    archive_prefix = archive_directory_prefix(instance.get("archive"))
    if archive_prefix is not None:
        archived = instances_root / archive_prefix / relative
        if archived.exists():
            return archived

    matches = sorted(
        candidate
        for candidate in instances_root.rglob(relative.name)
        if candidate.parts[-len(relative.parts):] == relative.parts
        or candidate.name == relative.name
    )
    if matches:
        return matches[0]
    raise FileNotFoundError(f"could not resolve instance path: {instance['relative_path']}")


def archive_directory_prefix(archive: str | None) -> str | None:
    if archive is None:
        return None
    if archive.startswith("benchmarks-") and len(archive) == len("benchmarks-a"):
        return archive[-1].upper()
    return None


def read_instance_text(path: Path) -> str:
    if path.name.lower().endswith(".lzma"):
        return lzma.open(path, mode="rt", encoding="utf-8", errors="ignore").read()
    return path.read_text(encoding="utf-8", errors="ignore")


def find_query_path(instance_path: Path) -> Path | None:
    candidates = [Path(str(instance_path) + ".arg")]
    if instance_path.suffix:
        candidates.append(instance_path.with_suffix(".arg"))
    name = instance_path.name
    if name.endswith(".apx.lzma"):
        candidates.append(instance_path.with_name(name.removesuffix(".apx.lzma") + ".apx_arg.lzma"))
    if name.endswith(".tgf.lzma"):
        candidates.append(instance_path.with_name(name.removesuffix(".tgf.lzma") + ".tgf_arg.lzma"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def solve_af_job(job: dict[str, Any]) -> dict[str, Any]:
    from argumentation.iccma import parse_af, parse_apx, parse_tgf
    from argumentation.solver import (
        AcceptanceSolverSuccess,
        ICCMAConfig,
        SATConfig,
        SingleExtensionSolverSuccess,
        SolverBackendError,
        SolverBackendUnavailable,
        SolverProtocolError,
        solve_dung_acceptance,
        solve_dung_single_extension,
    )

    root = Path(job["root"])
    instance = job["instance"]
    task = job["task"]
    path = resolve_instance_path(root, instance)
    query_path = find_query_path(path)
    problem, semantics = split_subtrack(task["subtrack"])
    text = read_instance_text(path)
    if instance["kind"] in {"apx", "compressed_apx"}:
        framework = parse_apx(text)
    elif instance["kind"] in {"tgf", "compressed_tgf"}:
        framework = parse_tgf(text)
    else:
        framework = parse_af(text)
    backend = job["backend"]
    iccma_config = None
    if backend == "iccma":
        binary = job.get("iccma_binary")
        if not binary:
            return {
                "status": "unavailable",
                "reason": "missing ICCMA solver configuration",
                "error": "Pass --iccma-binary or set ICCMA_AF_SOLVER.",
            }
        iccma_config = ICCMAConfig(
            binary=binary,
            timeout_seconds=float(job["solver_timeout_seconds"]),
        )
    sat_config = SATConfig(
        trace_sink=sat_trace_sink(
            instance=instance,
            task=task,
            framework=framework,
        ),
        metadata=sat_trace_metadata(instance=instance, task=task),
    )
    if problem == "SE":
        result = solve_dung_single_extension(
            framework,
            semantics=semantics,
            backend=backend,
            iccma=iccma_config,
            sat=sat_config,
        )
        if isinstance(result, SingleExtensionSolverSuccess):
            return solved_single_extension(result.extension)
        if isinstance(result, SolverBackendUnavailable):
            return unavailable_result(result.reason, result.install_hint)
        if isinstance(result, SolverBackendError):
            return solver_error_result(result.reason, result.details)
        if isinstance(result, SolverProtocolError):
            return protocol_error_result(result.reason, result.details)
        raise TypeError(f"unknown solver result: {result!r}")
    query = read_instance_text(query_path).strip() if query_path is not None else None
    if query is None:
        return {"status": "skipped", "reason": "missing_query", "error": None}
    result = solve_dung_acceptance(
        framework,
        semantics=semantics,
        task=acceptance_task(problem),
        query=query,
        backend=backend,
        iccma=iccma_config,
        sat=sat_config,
    )
    if isinstance(result, AcceptanceSolverSuccess):
        return solved_acceptance(result)
    if isinstance(result, SolverBackendUnavailable):
        return unavailable_result(result.reason, result.install_hint)
    if isinstance(result, SolverBackendError):
        return solver_error_result(result.reason, result.details)
    if isinstance(result, SolverProtocolError):
        return protocol_error_result(result.reason, result.details)
    raise TypeError(f"unknown solver result: {result!r}")


def sat_trace_metadata(
    *,
    instance: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, object]:
    problem, semantics = split_subtrack(task["subtrack"])
    return {
        "instance": instance["relative_path"],
        "track": task["track"],
        "subtrack": task["subtrack"],
        "problem": problem,
        "semantics": semantics,
        "task": "single-extension" if problem == "SE" else acceptance_task(problem),
        "year": infer_year(instance, task),
    }


def sat_trace_sink(
    *,
    instance: dict[str, Any],
    task: dict[str, Any],
    framework: Any,
):
    metadata = sat_trace_metadata(instance=instance, task=task)

    def emit(check: Any) -> None:
        event = {
            "event": "sat_check",
            "instance": metadata["instance"],
            "track": metadata["track"],
            "subtrack": metadata["subtrack"],
            "problem": metadata["problem"],
            "semantics": metadata["semantics"],
            "task": metadata["task"],
            "year": metadata["year"],
            "arguments": check.argument_count,
            "attacks": check.attack_count,
            "utility_name": check.utility_name,
            "assumptions_count": check.assumptions_count,
            "result": check.result,
            "elapsed_ms": f"{check.elapsed_ms:.6f}",
            "model_extension_size": check.model_extension_size,
        }
        print(json.dumps(event, sort_keys=True), file=sys.stderr, flush=True)

    return emit


def infer_year(instance: dict[str, Any], task: dict[str, Any]) -> str | None:
    for value in (instance.get("contest"), task.get("contest"), instance.get("year")):
        if value is None:
            continue
        text = str(value)
        for token in text.replace("-", " ").split():
            if token.isdigit() and len(token) == 4:
                return token
    return None


def solve_aba_job(job: dict[str, Any]) -> dict[str, Any]:
    from argumentation.aspic import GroundAtom, Literal
    from argumentation.iccma import parse_aba
    from argumentation.solver import (
        AcceptanceSolverSuccess,
        ICCMAConfig,
        SingleExtensionSolverSuccess,
        SolverBackendError,
        SolverBackendUnavailable,
        SolverProtocolError,
        solve_aba_acceptance,
        solve_aba_single_extension,
    )

    root = Path(job["root"])
    instance = job["instance"]
    task = job["task"]
    path = resolve_instance_path(root, instance)
    query_path = Path(str(path) + ".query")
    problem, semantics = split_subtrack(task["subtrack"])
    framework = parse_aba(read_instance_text(path))
    backend = job["backend"]
    iccma_config = None
    if backend == "iccma":
        binary = job.get("iccma_binary")
        if not binary:
            return {
                "status": "unavailable",
                "reason": "missing ICCMA solver configuration",
                "error": "Pass --iccma-binary or set ICCMA_AF_SOLVER.",
            }
        iccma_config = ICCMAConfig(
            binary=binary,
            timeout_seconds=float(job["solver_timeout_seconds"]),
        )
    if problem == "SE":
        result = solve_aba_single_extension(
            framework,
            semantics=semantics,
            backend=backend,
            iccma=iccma_config,
        )
        if isinstance(result, SingleExtensionSolverSuccess):
            return solved_single_extension(result.extension)
        if isinstance(result, SolverBackendUnavailable):
            return unavailable_result(result.reason, result.install_hint)
        if isinstance(result, SolverBackendError):
            return solver_error_result(result.reason, result.details)
        if isinstance(result, SolverProtocolError):
            return protocol_error_result(result.reason, result.details)
        raise TypeError(f"unknown solver result: {result!r}")
    query = None
    if query_path.exists():
        query_name = query_path.read_text(encoding="utf-8").strip()
        query = Literal(GroundAtom(query_name))
    if query is None:
        return {"status": "skipped", "reason": "missing_query", "error": None}
    result = solve_aba_acceptance(
        framework,
        semantics=semantics,
        task=acceptance_task(problem),
        query=query,
        backend=backend,
        iccma=iccma_config,
    )
    if isinstance(result, AcceptanceSolverSuccess):
        return solved_acceptance(result)
    if isinstance(result, SolverBackendUnavailable):
        return unavailable_result(result.reason, result.install_hint)
    if isinstance(result, SolverBackendError):
        return solver_error_result(result.reason, result.details)
    if isinstance(result, SolverProtocolError):
        return protocol_error_result(result.reason, result.details)
    raise TypeError(f"unknown solver result: {result!r}")


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
    return solved_single_extension(witness, extension_count=len(extension_sets))


def solved_single_extension(
    witness: frozenset[Any] | None,
    *,
    extension_count: int | None = None,
) -> dict[str, Any]:
    return {
        "status": "solved",
        "reason": None,
        "answer": None,
        "extension_count": extension_count,
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


def solved_acceptance(result) -> dict[str, Any]:
    witness = result.witness if result.answer else result.counterexample
    return {
        "status": "solved",
        "reason": None,
        "answer": str(result.answer).lower(),
        "extension_count": None,
        "witness_size": len(witness) if witness is not None else None,
        "witness": extension_to_text(witness),
        "error": None,
    }


def unavailable_result(reason: str, install_hint: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "reason": reason,
        "error": install_hint,
    }


def solver_error_result(reason: str, details: dict[str, str]) -> dict[str, Any]:
    return {
        "status": "solver_error",
        "reason": reason,
        "error": json.dumps(details, sort_keys=True),
    }


def protocol_error_result(reason: str, details: dict[str, str]) -> dict[str, Any]:
    return {
        "status": "protocol_error",
        "reason": reason,
        "error": json.dumps(details, sort_keys=True),
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


def acceptance_task(problem: str) -> str:
    if problem == "DC":
        return "credulous"
    if problem == "DS":
        return "skeptical"
    raise ValueError(f"unsupported acceptance problem: {problem}")


def base_result(instance: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    return {
        "track": task["track"],
        "subtrack": task["subtrack"],
        "instance_kind": instance["kind"],
        "instance": instance["relative_path"],
        "backend": None,
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
    sys.exit(main(sys.argv[1:]))
