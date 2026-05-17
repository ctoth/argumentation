"""Chess adapter for generic argumentation optimization semantics."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

from dialectical_chess.arguments import (
    MoveProbe,
    RootArgumentGraph,
    accepted_defense_count,
    accepted_positional_support_count,
    accepted_tactical_support_count,
    effective_score,
    effective_positional_support_count,
    grounded_candidates,
    positional_support_mode,
    selection_key,
    unresolved_attack_count,
)


def choose_optimized_move(
    probes: list[MoveProbe],
    graph: RootArgumentGraph,
    *,
    include_positional: bool = True,
) -> MoveProbe:
    """Select a chess move through ``argumentation.optimization``.

    The generic optimizer enforces Dung-style argument constraints; this adapter
    only maps chess evidence into objective features.
    """

    optimization = _import_argumentation_optimization()
    if isinstance(optimization, str):
        selected = sorted(grounded_candidates(probes, graph), key=lambda probe: selection_key(probe, graph))[0]
        return replace(
            selected,
            optimizer_trace={"status": "unavailable", "fallback": "argument", "reason": optimization},
        )

    ArgumentationFramework, OptimizationFeature, OptimizationObjective, OptimizationPolicy, optimize_framework = optimization
    framework = ArgumentationFramework(
        arguments=graph.arguments,
        defeats=graph.defeats,
    )
    policy = OptimizationPolicy(
        semantics="conflict_free",
        candidates=frozenset(graph.move_arguments.values()),
        objectives=(
            OptimizationObjective("terminal_mate", direction="maximize", priority=0),
            OptimizationObjective("unresolved_reply_attacks", direction="minimize", priority=1),
            OptimizationObjective("accepted_tactical_support", direction="maximize", priority=2),
            OptimizationObjective("material_gain", direction="maximize", priority=3),
            OptimizationObjective("accepted_defenses", direction="maximize", priority=4),
            OptimizationObjective("search_score", direction="maximize", priority=5),
            OptimizationObjective("positional_support_effective", direction="maximize", priority=6),
            OptimizationObjective("base_score_effective", direction="maximize", priority=7),
        ),
    )
    position_mode = positional_support_mode(graph, include_positional=include_positional)
    features = tuple(
        feature
        for probe in probes
        for feature in _optimizer_features(
            probe,
            graph,
            OptimizationFeature,
            position_mode=position_mode,
        )
    )
    result = optimize_framework(framework, policy, features)
    if result.status != "optimal" or result.selected_candidate is None:
        selected = sorted(grounded_candidates(probes, graph), key=lambda probe: selection_key(probe, graph))[0]
        return replace(
            selected,
            optimizer_trace={
                "status": result.status,
                "fallback": "argument",
                "trace": result.trace,
            },
        )

    uci_by_argument = {argument: uci for uci, argument in graph.move_arguments.items()}
    selected_uci = uci_by_argument[result.selected_candidate]
    selected = next(probe for probe in probes if probe.uci == selected_uci)
    return replace(
        selected,
        optimizer_trace={
            "status": result.status,
            "selected_candidate": result.selected_candidate,
            "selected_arguments": sorted(result.selected_arguments),
            "objective_values": result.objective_values,
            "positional_support_mode": position_mode,
            "trace": result.trace,
        },
    )


def _optimizer_features(
    probe: MoveProbe,
    graph: RootArgumentGraph,
    feature_type,
    *,
    position_mode: str,
):
    move_arg = graph.move_arguments[probe.uci]
    positional_support_raw = accepted_positional_support_count(probe, graph)
    positional_support_effective = effective_positional_support_count(probe, graph, position_mode)
    tactical_support = accepted_tactical_support_count(probe, graph)
    return (
        feature_type(move_arg, "terminal_mate", 1 if probe.is_checkmate or "terminal:checkmate" in probe.reasons else 0),
        feature_type(move_arg, "unresolved_reply_attacks", unresolved_attack_count(probe, graph)),
        feature_type(move_arg, "accepted_tactical_support", tactical_support),
        feature_type(move_arg, "accepted_defenses", accepted_defense_count(probe, graph)),
        feature_type(move_arg, "material_gain", probe.captured_value + probe.promotion_value),
        feature_type(move_arg, "search_score", 0 if probe.search_score is None else probe.search_score),
        feature_type(move_arg, "positional_support_raw", positional_support_raw),
        feature_type(move_arg, "positional_support_effective", positional_support_effective),
        feature_type(move_arg, "base_score_effective", effective_score(probe, position_mode)),
    )


def _import_argumentation_optimization():
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from argumentation.dung import ArgumentationFramework
        from argumentation.optimization import (
            OptimizationFeature,
            OptimizationObjective,
            OptimizationPolicy,
            optimize_framework,
        )
    except ImportError as exc:
        return str(exc)
    return (
        ArgumentationFramework,
        OptimizationFeature,
        OptimizationObjective,
        OptimizationPolicy,
        optimize_framework,
    )
