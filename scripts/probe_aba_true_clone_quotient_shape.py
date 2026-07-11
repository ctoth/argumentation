"""Probe 8 Gate B deterministic true-clone structural-shape diagnostic.

This module never computes supports or semantics and never invokes a solver.
Color refinement only proposes assumption buckets.  The committed Gate A
fix-outside verifier is the sole authority for every certified transposition.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from math import log2
from pathlib import Path
import subprocess
import sys
import time
import tracemalloc
from typing import TypeAlias, cast

from argumentation.interop.iccma import parse_aba
from scripts.aba_true_clone_quotient_reference import (
    SemanticBounds,
    normalize_framework,
    process_memory_limit,
    verify_fix_outside_transposition,
)


NodeId: TypeAlias = str
Incidence: TypeAlias = tuple[str, NodeId, NodeId]
ROW_NAMES = (
    "aba_2000_0.3_10_10_0.aba",
    "aba_2000_0.3_10_10_1.aba",
)
ROW_WALL_SECONDS = 5.0
ROW_CPU_SECONDS = 5.0
OUTER_WALL_SECONDS = 15.0
MEMORY_BYTES = 512 * 1024 * 1024


@dataclass(frozen=True)
class ParsedNormalized:
    colors: Mapping[NodeId, str]
    incidences: frozenset[Incidence]
    assumptions: tuple[NodeId, ...]


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _parse_normalized(serialized: str) -> ParsedNormalized:
    raw = cast(dict[str, object], json.loads(serialized))
    node_rows = cast(list[list[str]], raw["nodes"])
    incidence_rows = cast(list[list[str]], raw["incidences"])
    assumptions = tuple(sorted(cast(list[str], raw["assumptions"])))
    colors = {row[0]: row[1] for row in node_rows}
    incidences = frozenset((row[0], row[1], row[2]) for row in incidence_rows)
    if len(colors) != len(node_rows) or not set(assumptions) <= set(colors):
        raise ValueError("invalid complete normalized graph")
    return ParsedNormalized(colors, incidences, assumptions)


def _refine(
    graph: ParsedNormalized,
) -> tuple[dict[NodeId, int], int, list[dict[str, object]]]:
    neighbors: dict[NodeId, list[tuple[str, NodeId]]] = {
        node: [] for node in graph.colors
    }
    for kind, source, target in graph.incidences:
        neighbors[source].append((f"{kind}:out", target))
        neighbors[target].append((f"{kind}:in", source))

    palette = {
        color: index for index, color in enumerate(sorted(set(graph.colors.values())))
    }
    colors = {node: palette[color] for node, color in graph.colors.items()}
    rounds = 0
    while True:
        signatures = {
            node: (
                colors[node],
                tuple(sorted((edge, colors[other]) for edge, other in neighbors[node])),
            )
            for node in sorted(graph.colors)
        }
        unique = {
            signature: index
            for index, signature in enumerate(sorted(set(signatures.values())))
        }
        refined = {node: unique[signature] for node, signature in signatures.items()}
        if all(refined[node] == colors[node] for node in colors):
            break
        colors = refined
        rounds += 1

    buckets: dict[int, list[NodeId]] = defaultdict(list)
    for node in graph.assumptions:
        buckets[colors[node]].append(node)
    candidates = [
        {"color": color, "members": sorted(members), "size": len(members)}
        for color, members in sorted(buckets.items())
        if len(members) > 1
    ]
    return colors, rounds, candidates


def _certificate_row(
    normalized_sha256: str,
    left: NodeId,
    right: NodeId,
) -> dict[str, object]:
    payload = {
        "normalized_sha256": normalized_sha256,
        "left": left,
        "right": right,
        "fixes_every_other_node": True,
        "preserves_all_colors": True,
        "preserves_all_incidences": True,
    }
    return {**payload, "certificate_sha256": _digest(payload)}


def _certify(
    serialized: str,
    normalized_sha256: str,
    candidates: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    verified: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    classes: list[dict[str, object]] = []
    for bucket in candidates:
        members = tuple(cast(list[str], bucket["members"]))
        accepted_pairs: set[frozenset[NodeId]] = set()
        rows: dict[frozenset[NodeId], dict[str, object]] = {}
        for left, right in combinations(members, 2):
            certificate = verify_fix_outside_transposition(serialized, left, right)
            pair = frozenset({left, right})
            if certificate is None:
                rejected.append({"left": left, "right": right})
                continue
            row = _certificate_row(normalized_sha256, left, right)
            verified.append(row)
            accepted_pairs.add(pair)
            rows[pair] = row

        pending = set(members)
        while pending:
            start = min(pending)
            component = {start}
            changed = True
            while changed:
                changed = False
                for node in sorted(pending - component):
                    if any(
                        frozenset({node, member}) in accepted_pairs
                        for member in component
                    ):
                        component.add(node)
                        changed = True
            pending -= component
            if len(component) < 2:
                continue
            ordered = tuple(sorted(component))
            required = [frozenset(pair) for pair in combinations(ordered, 2)]
            if any(pair not in accepted_pairs for pair in required):
                raise RuntimeError(
                    "verified transpositions do not form a complete class"
                )
            certificates = [rows[pair] for pair in required]
            class_payload = {
                "members": list(ordered),
                "size": len(ordered),
                "certificates": certificates,
            }
            classes.append({**class_payload, "class_sha256": _digest(class_payload)})
    classes.sort(key=lambda item: cast(list[str], item["members"]))
    return verified, rejected, classes


def _rule_templates(
    graph: ParsedNormalized,
    classes: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    representative: dict[NodeId, str] = {}
    for item in classes:
        members = cast(list[str], item["members"])
        token = "class:" + _digest(members)
        representative.update({member: token for member in members})

    rule_nodes = sorted(
        node for node, color in graph.colors.items() if color.startswith("rule:")
    )
    by_rule: dict[NodeId, list[Incidence]] = {node: [] for node in rule_nodes}
    for incidence in graph.incidences:
        kind, source, target = incidence
        if source in by_rule:
            by_rule[source].append((kind, source, target))

    grouped: dict[str, dict[str, object]] = {}
    for rule in rule_nodes:
        shape = {
            "rule_color": graph.colors[rule],
            "incidences": sorted(
                [kind, representative.get(target, target)]
                for kind, _, target in by_rule[rule]
            ),
        }
        key = _digest(shape)
        if key not in grouped:
            grouped[key] = {
                "template_sha256": key,
                "template": shape,
                "multiplicity": 0,
                "original_rule_nodes": [],
            }
        grouped[key]["multiplicity"] = cast(int, grouped[key]["multiplicity"]) + 1
        cast(list[str], grouped[key]["original_rule_nodes"]).append(rule)

    quotient = [grouped[key] for key in sorted(grouped)]
    reconstructed = sorted(
        rule
        for template in quotient
        for rule in cast(list[str], template["original_rule_nodes"])
    )
    return {
        "original_count": len(rule_nodes),
        "quotient_count": len(quotient),
        "quotient_templates": quotient,
        "reconstructs_original_multiset": reconstructed == rule_nodes,
        "reconstruction_sha256": _digest(reconstructed),
    }


def analyze_normalized_shape(serialized: str) -> dict[str, object]:
    """Analyze one complete Gate A serialization without semantic reasoning."""
    graph = _parse_normalized(serialized)
    normalized_sha256 = sha256(serialized.encode()).hexdigest()
    _, rounds, candidates = _refine(graph)
    verified, rejected, classes = _certify(serialized, normalized_sha256, candidates)

    revalidated = all(
        verify_fix_outside_transposition(
            serialized, cast(str, row["left"]), cast(str, row["right"])
        )
        is not None
        and row
        == _certificate_row(
            normalized_sha256, cast(str, row["left"]), cast(str, row["right"])
        )
        for item in classes
        for row in cast(list[dict[str, object]], item["certificates"])
    )
    class_sizes = [cast(int, item["size"]) for item in classes]
    singleton_count = len(graph.assumptions) - sum(class_sizes)
    original_states = 1 << len(graph.assumptions)
    quotient_states = 1 << singleton_count
    for size in class_sizes:
        quotient_states *= size + 1
    templates = _rule_templates(graph, classes)
    return {
        "normalized_sha256": normalized_sha256,
        "counts": {
            "assumptions": len(graph.assumptions),
            "rules": sum(color.startswith("rule:") for color in graph.colors.values()),
            "literals": sum(
                color.endswith("_literal") for color in graph.colors.values()
            ),
            "nodes": len(graph.colors),
            "incidences": len(graph.incidences),
        },
        "refinement_rounds": rounds,
        "candidate_buckets": candidates,
        "verified_transpositions": verified,
        "rejected_transpositions": rejected,
        "certified_classes": classes,
        "certified_class_count": len(classes),
        "largest_class": max(class_sizes, default=1),
        "multiplicity_state_counts": {
            "original": str(original_states),
            "quotient": str(quotient_states),
        },
        "unceiled_symmetric_decision_reduction": (
            len(graph.assumptions) - log2(quotient_states)
        ),
        "rule_templates": templates,
        "all_certificates_revalidated": revalidated,
    }


def _worker(path: Path) -> int:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    tracemalloc.start()
    with process_memory_limit(MEMORY_BYTES):
        raw = path.read_bytes()
        framework = parse_aba(raw.decode("utf-8"))
        normalized = normalize_framework(
            framework,
            bounds=SemanticBounds(
                assumptions=10_000,
                rules=100_000,
                literals=100_000,
                body_width=10_000,
            ),
        )
        shape = analyze_normalized_shape(normalized.serialized)
    _, peak = tracemalloc.get_traced_memory()
    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    cap_status = {
        "wall_seconds_limit": ROW_WALL_SECONDS,
        "cpu_seconds_limit": ROW_CPU_SECONDS,
        "memory_bytes_limit": MEMORY_BYTES,
        "wall_within_cap": elapsed_wall <= ROW_WALL_SECONDS,
        "cpu_within_cap": elapsed_cpu <= ROW_CPU_SECONDS,
        "memory_within_cap": peak <= MEMORY_BYTES,
    }
    if not all(
        cast(bool, value)
        for key, value in cap_status.items()
        if key.endswith("within_cap")
    ):
        raise RuntimeError("row resource cap breached")
    payload = {
        "path": path.as_posix(),
        "input_sha256": sha256(raw).hexdigest(),
        **shape,
        "elapsed_wall_seconds": elapsed_wall,
        "elapsed_cpu_seconds": elapsed_cpu,
        "peak_traced_memory_bytes": peak,
        "cap_status": cap_status,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def _run(rows: Sequence[Path], output: Path) -> int:
    allowed = set(ROW_NAMES)
    if len(rows) != 2 or {path.name for path in rows} != allowed:
        raise ValueError("exactly the two frozen Probe 8 rows are required")
    started = time.perf_counter()
    results: list[dict[str, object]] = []
    for path in sorted(rows):
        remaining = OUTER_WALL_SECONDS - (time.perf_counter() - started)
        if remaining <= 0:
            raise TimeoutError("15-second outer cap breached")
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.probe_aba_true_clone_quotient_shape",
                "--worker",
                str(path.resolve()),
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=min(ROW_WALL_SECONDS, remaining),
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"row failed closed: {path.as_posix()}: {completed.stderr.strip()}"
            )
        try:
            results.append(cast(dict[str, object], json.loads(completed.stdout)))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"unparseable row telemetry: {path.as_posix()}") from exc
    survivors = [
        row
        for row in results
        if cast(int, row["certified_class_count"]) > 0
        and cast(int, cast(dict[str, object], row["rule_templates"])["quotient_count"])
        < cast(int, cast(dict[str, object], row["rule_templates"])["original_count"])
    ]
    selected = (
        min(
            survivors,
            key=lambda row: (
                -cast(float, row["unceiled_symmetric_decision_reduction"]),
                cast(str, row["path"]),
            ),
        )
        if survivors
        else None
    )
    payload = {
        "probe": "ICCMA 2023 Probe 8 Gate B",
        "usage": {"triage_probes": "7/8", "full_experiments": "0/3"},
        "shape_predicts_speedup": False,
        "outcome": "GATE B PASS" if survivors else "STRUCTURAL KILL",
        "selected_row": None if selected is None else selected["path"],
        "solver_diagnostic_authorized": bool(survivors),
        "outer_elapsed_wall_seconds": time.perf_counter() - started,
        "outer_wall_seconds_limit": OUTER_WALL_SECONDS,
        "rows": results,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rows", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args(argv)
    if args.worker is not None:
        return _worker(args.worker)
    if args.output is None:
        parser.error("--output is required")
    return _run(args.rows, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
