from __future__ import annotations

import argparse
from collections import OrderedDict
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from argumentation.structured.aba.aba_telemetry import (
    STRUCTURAL_TELEMETRY_KEYS,
    aba_structural_telemetry,
)
from argumentation.iccma import parse_aba
from tools.iccma2025_run_native import DATA_ROOT, read_instance_text, resolve_instance_path


NUMERIC_FEATURES = (
    "atoms",
    "assumptions",
    "rules",
    "contraries",
    "max_rule_body_width",
    "rule_head_fanin_max",
    "body_literal_fanout_max",
    "contrary_fanin_max",
    "contrary_fanout_max",
    "assumption_to_atom_ratio",
    "rule_to_assumption_ratio",
    "rule_dependency_scc_count",
    "rule_dependency_max_scc_size",
    "assumption_dependency_scc_count",
    "assumption_dependency_max_scc_size",
    "closure_probe_count",
    "closure_probe_max_growth",
)
TARGET_STRUCTURAL_CLUSTER = "sparse_assumption_language|narrow_rule_bodies"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a structural 10 timeout / 10 solved ABA fixture."
    )
    parser.add_argument("--root", type=Path, default=DATA_ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--event-log", type=Path, required=True)
    parser.add_argument("--sample-out", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = build_fixture(args.root, args.manifest, args.event_log)
    args.sample_out.parent.mkdir(parents=True, exist_ok=True)
    args.sample_out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.sample_out}")
    return 0


def build_fixture(root: Path, manifest_path: Path, event_log_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    events = _load_relevant_events(event_log_path)
    telemetry_by_instance = _telemetry_by_instance(root, manifest, events)
    candidates = [
        _candidate_from_event(event, manifest[event["instance"]], telemetry_by_instance[event["instance"]])
        for event in events
        if event["instance"] in manifest and event["instance"] in telemetry_by_instance
    ]
    timeout_candidates = [candidate for candidate in candidates if candidate["status"] == "timeout"]
    solved_candidates = [candidate for candidate in candidates if candidate["status"] == "solved"]
    if len(timeout_candidates) < 10 or len(solved_candidates) < 10:
        raise SystemExit(
            f"need at least 10 timeout and 10 solved candidates, got "
            f"{len(timeout_candidates)} timeout and {len(solved_candidates)} solved"
        )

    cluster_key = TARGET_STRUCTURAL_CLUSTER
    cluster_timeouts = [
        candidate for candidate in timeout_candidates
        if candidate["structural_cluster"] == cluster_key
    ]
    cluster_solved = [
        candidate for candidate in solved_candidates
        if candidate["structural_cluster"] == cluster_key
    ]
    if len(cluster_timeouts) < 10 or len(cluster_solved) < 10:
        raise SystemExit(
            f"structural cluster {cluster_key!r} has {len(cluster_timeouts)} timeout "
            f"and {len(cluster_solved)} solved rows; available clusters: "
            f"{_cluster_counts(timeout_candidates, solved_candidates)}"
        )
    selected_timeouts = _select_structural_timeouts(cluster_timeouts, limit=10)
    pairs = _pair_with_solved_matches(selected_timeouts, cluster_solved)
    selected_solved_ids = {pair["solved_row"] for pair in pairs}
    selected_rows = [
        *selected_timeouts,
        *[candidate for candidate in solved_candidates if candidate["row_id"] in selected_solved_ids],
    ]
    selected_rows = sorted(selected_rows, key=lambda row: (row["status"], row["row_id"]))
    _validate_payload(selected_rows, pairs)
    return {
        "source_event_log": str(event_log_path),
        "source_manifest": str(manifest_path),
        "selection": {
            "timeout_count": 10,
            "solved_count": 10,
            "method": "sparse_assumption_narrow_rule_nearest_match",
            "structural_cluster": cluster_key,
            "numeric_features": list(NUMERIC_FEATURES),
        },
        "rows": selected_rows,
        "pairs": pairs,
    }


def _load_manifest(path: Path) -> dict[str, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(row["relative_path"]): row
        for row in rows
        if row.get("kind") == "aba" and row.get("parse_status") == "ok"
    }


def _load_relevant_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        event = json.loads(raw_line)
        if event.get("event") != "iccma_row":
            continue
        if event.get("instance_kind") != "aba":
            continue
        if event.get("status") not in {"solved", "timeout"}:
            continue
        events.append(event)
    return events


def _telemetry_by_instance(
    root: Path,
    manifest: dict[str, dict[str, Any]],
    events: list[dict[str, Any]],
) -> dict[str, dict[str, object]]:
    instances = sorted({event["instance"] for event in events if event["instance"] in manifest})
    telemetry: dict[str, dict[str, object]] = {}
    for index, relative_path in enumerate(instances, start=1):
        if index == 1 or index % 25 == 0:
            print(
                f"telemetry {index}/{len(instances)} {relative_path}",
                file=sys.stderr,
                flush=True,
            )
        path = resolve_instance_path(root, manifest[relative_path])
        framework = parse_aba(read_instance_text(path))
        telemetry[relative_path] = aba_structural_telemetry(framework)
    return telemetry


def _candidate_from_event(
    event: dict[str, Any],
    manifest_row: dict[str, Any],
    telemetry: dict[str, object],
) -> dict[str, Any]:
    row_id = "|".join(
        [
            str(event.get("track")),
            str(event.get("subtrack")),
            str(event.get("instance")),
            str(event.get("status")),
        ]
    )
    return {
        "row_id": row_id,
        "track": event.get("track"),
        "subtrack": event.get("subtrack"),
        "status": event.get("status"),
        "instance_kind": event.get("instance_kind"),
        "structural_cluster": _structural_cluster(telemetry),
        "relative_path": event.get("instance"),
        "elapsed_seconds": event.get("elapsed_seconds"),
        "answer": event.get("answer"),
        "manifest": {
            "arguments_or_atoms": manifest_row.get("arguments_or_atoms"),
            "assumptions": manifest_row.get("assumptions"),
            "rules": manifest_row.get("rules"),
            "contraries": manifest_row.get("contraries"),
            "size": manifest_row.get("size"),
        },
        "telemetry": telemetry,
    }


def _structural_cluster(telemetry: dict[str, object]) -> str:
    density = (
        "dense_assumption_language"
        if float(telemetry["assumption_to_atom_ratio"]) >= 0.5
        else "sparse_assumption_language"
    )
    width = (
        "narrow_rule_bodies"
        if int(telemetry["max_rule_body_width"]) <= 3
        else "wide_rule_bodies"
    )
    return f"{density}|{width}"


def _cluster_counts(
    timeout_candidates: list[dict[str, Any]],
    solved_candidates: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for status, candidates in (
        ("timeout", timeout_candidates),
        ("solved", solved_candidates),
    ):
        for candidate in candidates:
            cluster = str(candidate["structural_cluster"])
            counts.setdefault(cluster, {"timeout": 0, "solved": 0})[status] += 1
    return dict(sorted(counts.items()))


def _select_structural_timeouts(candidates: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda row: (
            -_numeric(row, "assumptions"),
            -_numeric(row, "rules"),
            -_numeric(row, "rule_to_assumption_ratio"),
            -_numeric(row, "closure_probe_max_growth"),
            str(row["subtrack"]),
            str(row["row_id"]),
        ),
    )[:limit]


def _pair_with_solved_matches(
    timeout_rows: list[dict[str, Any]],
    solved_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    used_solved: set[str] = set()
    for timeout_row in timeout_rows:
        ranked = sorted(
            (
                (_distance(timeout_row, solved_row), solved_row)
                for solved_row in solved_rows
                if solved_row["row_id"] not in used_solved
            ),
            key=lambda item: (item[0], str(item[1]["subtrack"]), str(item[1]["row_id"])),
        )
        for distance, solved_row in ranked:
            decision_features = _decision_features(timeout_row, solved_row)
            if decision_features:
                used_solved.add(solved_row["row_id"])
                pairs.append(
                    {
                        "timeout_row": timeout_row["row_id"],
                        "solved_row": solved_row["row_id"],
                        "shared_features": _shared_features(timeout_row, solved_row),
                        "distinctive_features": sorted(decision_features),
                        "decision_features": decision_features,
                        "match_distance": distance,
                    }
                )
                break
        else:
            raise SystemExit(f"no structural solved match for {timeout_row['row_id']}")
    return pairs


def _distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    total = 0.0
    for feature in NUMERIC_FEATURES:
        left_value = _numeric(left, feature)
        right_value = _numeric(right, feature)
        scale = max(abs(left_value), abs(right_value), 1.0)
        total += abs(left_value - right_value) / scale
    return round(total, 6)


def _numeric(row: dict[str, Any], feature: str) -> float:
    value = row["telemetry"][feature]
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    return float(value)


def _decision_features(left: dict[str, Any], right: dict[str, Any]) -> OrderedDict[str, dict[str, object]]:
    features: OrderedDict[str, dict[str, object]] = OrderedDict()
    for feature in NUMERIC_FEATURES:
        left_value = left["telemetry"][feature]
        right_value = right["telemetry"][feature]
        if left_value != right_value:
            features[feature] = {
                "timeout": left_value,
                "solved": right_value,
            }
    return features


def _shared_features(left: dict[str, Any], right: dict[str, Any]) -> OrderedDict[str, object]:
    shared: OrderedDict[str, object] = OrderedDict()
    for feature in NUMERIC_FEATURES:
        if left["telemetry"][feature] == right["telemetry"][feature]:
            shared[feature] = left["telemetry"][feature]
    return shared


def _validate_payload(rows: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> None:
    if len([row for row in rows if row["status"] == "timeout"]) != 10:
        raise SystemExit("fixture must contain exactly 10 timeout rows")
    if len([row for row in rows if row["status"] == "solved"]) != 10:
        raise SystemExit("fixture must contain exactly 10 solved rows")
    if len(pairs) != 10:
        raise SystemExit("fixture must contain exactly 10 pairs")
    for row in rows:
        missing = STRUCTURAL_TELEMETRY_KEYS - set(row["telemetry"])
        if missing:
            raise SystemExit(f"missing telemetry keys: {sorted(missing)}")
    recurring: dict[str, int] = {}
    for pair in pairs:
        if not pair["distinctive_features"]:
            raise SystemExit("pair lacks structural distinctive features")
        for feature in pair["distinctive_features"]:
            recurring[feature] = recurring.get(feature, 0) + 1
    if not any(count >= 3 for count in recurring.values()):
        raise SystemExit("no structural feature recurs in at least three pairs")


if __name__ == "__main__":
    raise SystemExit(main())
