"""Measure exact collective-attack SCC shape on baseline-timeout dev frameworks.

This development-only diagnostic neither invokes solver workers nor records solved or
wall-clock metrics. It uses the frozen probe-5 reference semantics and fails closed.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from itertools import combinations
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterator, NoReturn

from argumentation.interop.iccma import parse_aba
from argumentation.structured.aba.aba import ABAFramework, AssumptionSet
from argumentation.structured.aba.aba_support_model import _minimal_supports

if __package__:
    from scripts import aba_scc_composition_reference as reference
else:
    import aba_scc_composition_reference as reference

CollectiveFramework = reference.CollectiveFramework
ComponentBoundary = reference.ComponentBoundary
ReferenceCapExceeded = reference.ReferenceCapExceeded
ReferenceCaps = reference.ReferenceCaps


DATA_ROOT = Path("data/iccma/2023")
BASELINE_COLUMNS = ("instance", "subtrack", "status", "run1", "run2", "run3")


class MeasurementFailure(RuntimeError):
    """Raised when an input or exact operational contract cannot be trusted."""


@dataclass(frozen=True)
class BaselineTimeoutFramework:
    relative_path: str
    manifest_assumptions: int
    manifest_atoms: int
    sorted_index: int
    baseline_timeout_subtracks: tuple[str, ...]


@dataclass(frozen=True)
class UsefulSccParticipation:
    useful_scc_indices: tuple[int, ...]
    inter_scc_attack_count: int
    cross_scc_collective_tail_count: int
    maximum_cross_scc_tail_width: int


@dataclass
class _ShapeAccumulator:
    branch_state_count: int = 0
    maximum_exact_conditioned_residual: int = 0
    maximum_full_boundary_items: int = 0


def reject_holdout_path(path: Path) -> None:
    """Reject a holdout locator lexically, before any filesystem access."""
    if any("holdout" in part.casefold() for part in path.parts):
        raise MeasurementFailure(f"holdout path rejected: {path}")


def require_cap(field: str, value: int, limit: int) -> None:
    if value > limit:
        raise MeasurementFailure(f"{field} cap exceeded: {value:,} > {limit:,}")


def has_strict_residual_reduction(
    normalized_assumption_count: int,
    maximum_exact_conditioned_residual: int,
) -> bool:
    return maximum_exact_conditioned_residual < normalized_assumption_count


def full_boundary_item_count(boundary: ComponentBoundary) -> int:
    """Count every stored boundary item, including conditioned tails and M."""
    conditioned_items = sum(
        len(item.original.tail) + 1 + len(item.residual_tail)
        for item in boundary.attacks
    )
    return (
        len(boundary.component)
        + len(boundary.selected)
        + len(boundary.attacked)
        + len(boundary.defeated)
        + len(boundary.provisionally_defeated)
        + len(boundary.undefeated)
        + len(boundary.undefeated_or_provisional)
        + len(boundary.candidates)
        + conditioned_items
        + len(boundary.mitigated)
    )


def useful_scc_participation(
    collective: CollectiveFramework,
) -> UsefulSccParticipation:
    component_of = {
        assumption: index
        for index, component in enumerate(collective.components)
        for assumption in component
    }
    useful: set[int] = set()
    inter_scc_attacks = []
    for attack in collective.attacks:
        participants = {component_of[attack.target]}
        participants.update(component_of[source] for source in attack.tail)
        if len(participants) < 2:
            continue
        useful.update(participants)
        inter_scc_attacks.append(attack)
    widths = [len(attack.tail) for attack in inter_scc_attacks]
    return UsefulSccParticipation(
        useful_scc_indices=tuple(sorted(useful)),
        inter_scc_attack_count=len(inter_scc_attacks),
        cross_scc_collective_tail_count=len(inter_scc_attacks),
        maximum_cross_scc_tail_width=max(widths, default=0),
    )


def load_baseline_timeout_frameworks(
    manifest_path: Path,
    baseline_record_path: Path,
) -> tuple[BaselineTimeoutFramework, ...]:
    reject_holdout_path(manifest_path)
    reject_holdout_path(baseline_record_path)
    manifest = _load_manifest(manifest_path)
    baseline_rows = _load_baseline_rows(baseline_record_path)

    instances = manifest["instances"]
    subtracks = tuple(sorted(manifest["metric_config"]["subtracks"]))
    by_leaf: dict[str, dict[str, Any]] = {}
    for row in instances:
        relative_path = _required_str(row, "relative_path", "manifest instance")
        reject_holdout_path(Path(relative_path))
        leaf = Path(relative_path).name
        if leaf in by_leaf:
            raise MeasurementFailure(f"ambiguous manifest instance basename: {leaf}")
        _required_int(row, "assumptions", "manifest instance")
        _required_int(row, "atoms", "manifest instance")
        _required_int(row, "sorted_index", "manifest instance")
        by_leaf[leaf] = row

    expected = {(leaf, subtrack) for leaf in by_leaf for subtrack in subtracks}
    actual = set(baseline_rows)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise MeasurementFailure(
            f"baseline/manifest row mismatch: missing={missing!r}; extra={extra!r}"
        )

    timeout_subtracks: dict[str, list[str]] = {}
    for (leaf, subtrack), status in baseline_rows.items():
        if status == "timeout":
            timeout_subtracks.setdefault(leaf, []).append(subtrack)

    if not timeout_subtracks:
        raise MeasurementFailure("baseline contains no timeout frameworks")
    selected = []
    for leaf in sorted(
        timeout_subtracks, key=lambda item: str(by_leaf[item]["relative_path"])
    ):
        row = by_leaf[leaf]
        selected.append(
            BaselineTimeoutFramework(
                relative_path=str(row["relative_path"]),
                manifest_assumptions=int(row["assumptions"]),
                manifest_atoms=int(row["atoms"]),
                sorted_index=int(row["sorted_index"]),
                baseline_timeout_subtracks=tuple(sorted(timeout_subtracks[leaf])),
            )
        )
    return tuple(selected)


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MeasurementFailure(f"cannot parse manifest {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MeasurementFailure("manifest root must be an object")
    if payload.get("partition") != "development":
        raise MeasurementFailure("manifest partition must be exactly 'development'")
    metric_config = payload.get("metric_config")
    instances = payload.get("instances")
    if not isinstance(metric_config, dict) or not isinstance(instances, list):
        raise MeasurementFailure("manifest missing metric_config or instances")
    subtracks = metric_config.get("subtracks")
    if (
        not isinstance(subtracks, list)
        or not subtracks
        or not all(isinstance(item, str) and item for item in subtracks)
        or len(set(subtracks)) != len(subtracks)
    ):
        raise MeasurementFailure("manifest subtracks must be unique nonempty strings")
    if not instances or not all(isinstance(item, dict) for item in instances):
        raise MeasurementFailure("manifest instances must be nonempty objects")
    return payload


def _load_baseline_rows(path: Path) -> dict[tuple[str, str], str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise MeasurementFailure(f"cannot read baseline record {path}: {exc}") from exc
    header_indices = [
        index
        for index, line in enumerate(lines)
        if _table_cells(line) == BASELINE_COLUMNS
    ]
    if len(header_indices) != 1:
        raise MeasurementFailure(
            f"baseline result table is ambiguous or missing: found {len(header_indices)}"
        )
    index = header_indices[0]
    if index + 1 >= len(lines) or not _is_separator_row(lines[index + 1], 6):
        raise MeasurementFailure("baseline result table separator is missing")
    rows: dict[tuple[str, str], str] = {}
    for line in lines[index + 2 :]:
        cells = _table_cells(line)
        if cells is None:
            break
        if len(cells) != 6:
            raise MeasurementFailure(f"malformed baseline result row: {line}")
        instance, subtrack, status, *runs = cells
        if (
            not instance
            or not subtrack
            or status
            not in {
                "solved",
                "timeout",
                "skipped",
                "solver_error",
                "protocol_error",
            }
        ):
            raise MeasurementFailure(f"invalid baseline result row: {line}")
        try:
            tuple(float(value) for value in runs)
        except ValueError as exc:
            raise MeasurementFailure(f"invalid baseline run value: {line}") from exc
        key = (instance, subtrack)
        if key in rows:
            raise MeasurementFailure(f"duplicate baseline result row: {key!r}")
        rows[key] = status
    if not rows:
        raise MeasurementFailure("baseline result table has no rows")
    return rows


def _table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def _is_separator_row(line: str, width: int) -> bool:
    cells = _table_cells(line)
    return (
        cells is not None
        and len(cells) == width
        and all(re.fullmatch(r":?-{3,}:?", cell) is not None for cell in cells)
    )


def _required_str(row: dict[str, Any], field: str, location: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise MeasurementFailure(f"{location} missing string field {field!r}")
    return value


def _required_int(row: dict[str, Any], field: str, location: str) -> int:
    value = row.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise MeasurementFailure(
            f"{location} missing nonnegative integer field {field!r}"
        )
    return value


def _subsets_lazy(items: AssumptionSet) -> Iterator[AssumptionSet]:
    ordered = tuple(sorted(items, key=repr))
    for size in range(len(ordered) + 1):
        for choice in combinations(ordered, size):
            yield frozenset(choice)


def _measure_branches(
    collective: CollectiveFramework,
    *,
    preferred: bool,
    accumulator: _ShapeAccumulator,
) -> None:
    trace = reference._TraceBuilder()

    def visit(component_index: int, selected: AssumptionSet) -> None:
        accumulator.branch_state_count += 1
        require_cap(
            "branch_state_count",
            accumulator.branch_state_count,
            collective.caps.branch_states,
        )
        if component_index == len(collective.components):
            return
        component = collective.components[component_index]
        attacked_before = reference._attacked_by(collective.attacks, selected)
        try:
            boundary = reference._condition_boundary(
                collective, component, selected, attacked_before, trace
            )
        except ReferenceCapExceeded as exc:
            raise MeasurementFailure(str(exc)) from exc
        trace.boundaries.clear()
        full_items = full_boundary_item_count(boundary)
        accumulator.maximum_full_boundary_items = max(
            accumulator.maximum_full_boundary_items, full_items
        )
        require_cap(
            "maximum_full_boundary_items",
            full_items,
            collective.caps.boundary_items,
        )
        accumulator.maximum_exact_conditioned_residual = max(
            accumulator.maximum_exact_conditioned_residual,
            len(boundary.undefeated_or_provisional),
        )
        choices = (
            boundary.candidates if preferred else boundary.undefeated_or_provisional
        )
        for local in _subsets_lazy(choices):
            extended = selected | local
            attacked_now = attacked_before | reference._active_local_targets(
                boundary, local
            )
            if preferred:
                if not reference._locally_admissible(
                    collective.attacks, component, local, attacked_now
                ):
                    continue
            elif not reference._locally_stable(component, local, attacked_now):
                continue
            visit(component_index + 1, extended)

    visit(0, frozenset())


def _cap_status(
    value: int | None, limit: int, *, reached: bool = True
) -> dict[str, Any]:
    if not reached:
        status = "not_reached"
    elif value is not None and value <= limit:
        status = "within_cap"
    else:
        status = "exceeded"
    return {"value": value, "limit": limit, "status": status}


def _failure_field(message: str) -> str:
    for field in (
        "collective_attack_count",
        "branch_state_count",
        "maximum_full_boundary_items",
        "boundary item",
    ):
        if field in message:
            return "maximum_full_boundary_items" if field == "boundary item" else field
    return "measurement_failure"


def _resolve_framework_path(relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise MeasurementFailure(f"unsafe manifest relative_path: {relative_path}")
    path = DATA_ROOT / "extracted" / "instances" / relative
    reject_holdout_path(path)
    if not path.is_file():
        raise MeasurementFailure(f"framework path missing: {path}")
    return path


def _measure_framework(
    selected: BaselineTimeoutFramework,
    caps: ReferenceCaps,
) -> dict[str, Any]:
    path = _resolve_framework_path(selected.relative_path)
    try:
        framework = parse_aba(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise MeasurementFailure(f"cannot parse framework {path}: {exc}") from exc
    if not isinstance(framework, ABAFramework):
        raise MeasurementFailure(f"parser returned non-ABA framework for {path}")
    if len(framework.assumptions) != selected.manifest_assumptions:
        raise MeasurementFailure(
            "manifest/framework assumption row mismatch: "
            f"{selected.relative_path}: {selected.manifest_assumptions} != "
            f"{len(framework.assumptions)}"
        )

    supports = _minimal_supports(framework)
    support_count = sum(
        len(supports.get(framework.contrary[target], frozenset()))
        for target in framework.assumptions
    )
    base: dict[str, Any] = {
        **asdict(selected),
        "normalized_assumption_count": None,
        "support_count": support_count,
        "normalized_collective_attack_count": None,
        "scc_count": None,
        "scc_sizes": None,
        "useful_scc_count": None,
        "useful_scc_indices": None,
        "inter_scc_attack_count": None,
        "cross_scc_collective_tail_count": None,
        "maximum_cross_scc_tail_width": None,
        "maximum_exact_conditioned_residual": None,
        "strict_residual_reduction": None,
        "branch_state_count": None,
        "maximum_full_boundary_items": None,
        "cap_status": {
            "collective_attack_count": _cap_status(
                support_count, caps.collective_attacks
            ),
            "branch_state_count": _cap_status(None, caps.branch_states, reached=False),
            "maximum_full_boundary_items": _cap_status(
                None, caps.boundary_items, reached=False
            ),
        },
        "status": "measured",
        "failure_field": None,
        "failure": None,
    }
    try:
        require_cap("collective_attack_count", support_count, caps.collective_attacks)
        collective = reference.build_collective_framework(framework, caps=caps)
        participation = useful_scc_participation(collective)
        accumulator = _ShapeAccumulator()
        _measure_branches(collective, preferred=False, accumulator=accumulator)
        _measure_branches(collective, preferred=True, accumulator=accumulator)
        base.update(
            {
                "normalized_assumption_count": len(collective.assumptions),
                "normalized_collective_attack_count": len(collective.attacks),
                "scc_count": len(collective.components),
                "scc_sizes": [len(component) for component in collective.components],
                "useful_scc_count": len(participation.useful_scc_indices),
                "useful_scc_indices": list(participation.useful_scc_indices),
                "inter_scc_attack_count": participation.inter_scc_attack_count,
                "cross_scc_collective_tail_count": (
                    participation.cross_scc_collective_tail_count
                ),
                "maximum_cross_scc_tail_width": (
                    participation.maximum_cross_scc_tail_width
                ),
                "maximum_exact_conditioned_residual": (
                    accumulator.maximum_exact_conditioned_residual
                ),
                "strict_residual_reduction": has_strict_residual_reduction(
                    len(collective.assumptions),
                    accumulator.maximum_exact_conditioned_residual,
                ),
                "branch_state_count": accumulator.branch_state_count,
                "maximum_full_boundary_items": (
                    accumulator.maximum_full_boundary_items
                ),
                "cap_status": {
                    "collective_attack_count": _cap_status(
                        support_count, caps.collective_attacks
                    ),
                    "branch_state_count": _cap_status(
                        accumulator.branch_state_count, caps.branch_states
                    ),
                    "maximum_full_boundary_items": _cap_status(
                        accumulator.maximum_full_boundary_items,
                        caps.boundary_items,
                    ),
                },
            }
        )
    except MeasurementFailure as exc:
        field = _failure_field(str(exc))
        base["status"] = "cap_exceeded"
        base["failure_field"] = field
        base["failure"] = str(exc)
        if field == "branch_state_count":
            base["branch_state_count"] = caps.branch_states + 1
            base["cap_status"][field] = _cap_status(
                caps.branch_states + 1, caps.branch_states
            )
        elif field == "maximum_full_boundary_items":
            match = re.search(r"([\d,]+) > ([\d,]+)", str(exc))
            value = (
                int(match.group(1).replace(",", ""))
                if match
                else caps.boundary_items + 1
            )
            base["maximum_full_boundary_items"] = value
            base["cap_status"][field] = _cap_status(value, caps.boundary_items)
    return base


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--baseline-record", required=True, type=Path)
    parser.add_argument("--only-baseline-timeouts", action="store_true")
    parser.add_argument("--collective-attack-cap", required=True, type=int)
    parser.add_argument("--branch-state-cap", required=True, type=int)
    parser.add_argument("--boundary-item-cap", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def _abort(message: str) -> NoReturn:
    print(f"measurement failed closed: {message}", file=sys.stderr)
    raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if not args.only_baseline_timeouts:
            raise MeasurementFailure("--only-baseline-timeouts is required")
        for path in (args.manifest, args.baseline_record, args.output):
            reject_holdout_path(path)
        caps = ReferenceCaps(
            collective_attacks=args.collective_attack_cap,
            branch_states=args.branch_state_cap,
            boundary_items=args.boundary_item_cap,
        )
        if min(asdict(caps).values()) <= 0:
            raise MeasurementFailure("all caps must be positive")
        selected = load_baseline_timeout_frameworks(args.manifest, args.baseline_record)
        rows = [_measure_framework(row, caps) for row in selected]
        payload = {
            "schema_version": 1,
            "measurement": "probe-5 collective-attack SCC operational shape",
            "scope": "development baseline-timeout frameworks only",
            "manifest": args.manifest.as_posix(),
            "baseline_record": args.baseline_record.as_posix(),
            "data_root": DATA_ROOT.as_posix(),
            "caps": asdict(caps),
            "row_count": len(rows),
            "rows": rows,
            "cap_failure": any(row["status"] != "measured" for row in rows),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except MeasurementFailure as exc:
        _abort(str(exc))
    print(json.dumps(payload, sort_keys=True))
    return 1 if payload["cap_failure"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
