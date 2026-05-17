"""Argument graph construction and move selection for dialectical chess."""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SELECTOR_MODES = frozenset({"argument", "score", "grounded", "support", "categoriser", "optimizer"})
POSITIONAL_REASON_PREFIXES = (
    "center_control:",
    "development:",
    "file_control:",
    "king_safety:",
    "outpost:",
    "pawn_structure:",
    "piece_activity:",
)
TACTICAL_REASON_PREFIXES = (
    "terminal:",
    "tactical:",
    "material:",
    "procedural:",
    "smt:",
    "search:",
    "search_support:",
)
POSITIONAL_SCORE_BONUS = 25


@dataclass(frozen=True)
class MoveProbe:
    uci: str
    san: str
    score: int
    is_checkmate: bool
    gives_check: bool
    is_capture: bool
    captured_value: int
    promotion_value: int
    reasons: tuple[str, ...]
    objections: tuple[str, ...]
    reply_attacks: tuple[str, ...] = ()
    search_score: int | None = None
    search_line: tuple[str, ...] = ()
    smt_witnesses: tuple[str, ...] = ()
    optimizer_trace: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RootArgumentGraph:
    arguments: frozenset[str]
    defeats: frozenset[tuple[str, str]]
    move_arguments: dict[str, str]
    grounded_extension: frozenset[str]
    ranking: dict[str, Any]


def choose_move(
    probes: list[MoveProbe],
    graph: RootArgumentGraph | None = None,
    *,
    selector_mode: str = "argument",
) -> MoveProbe:
    if not probes:
        raise SystemExit("position has no legal moves")
    if selector_mode not in SELECTOR_MODES:
        raise ValueError(f"unknown selector_mode: {selector_mode}")
    graph = graph or build_root_argument_graph(probes)
    if selector_mode == "score":
        return sorted(probes, key=score_selection_key)[0]
    if selector_mode == "grounded":
        return sorted(grounded_candidates(probes, graph), key=score_selection_key)[0]
    if selector_mode == "support":
        return sorted(probes, key=lambda probe: support_selection_key(probe, graph))[0]
    if selector_mode == "categoriser":
        return sorted(probes, key=lambda probe: categoriser_selection_key(probe, graph))[0]
    if selector_mode == "optimizer":
        from dialectical_chess.optimizer import choose_optimized_move

        return choose_optimized_move(probes, graph)
    return sorted(
        grounded_candidates(probes, graph),
        key=lambda probe: selection_key(probe, graph),
    )[0]


def grounded_candidates(probes: list[MoveProbe], graph: RootArgumentGraph) -> list[MoveProbe]:
    accepted = [
        probe
        for probe in probes
        if graph.move_arguments[probe.uci] in graph.grounded_extension
    ]
    return accepted if accepted else probes


def score_selection_key(probe: MoveProbe) -> tuple[int, str]:
    return (-probe.score, probe.uci)


def selection_key(
    probe: MoveProbe,
    graph: RootArgumentGraph,
) -> tuple[Any, ...]:
    move_arg = graph.move_arguments[probe.uci]
    ranking_scores = graph.ranking.get("scores", {}) if graph.ranking.get("available") else {}
    move_rank = float(ranking_scores.get(move_arg, 0.0))
    mode = positional_support_mode(graph)
    accepted_tactical = accepted_tactical_support_count(probe, graph)
    accepted_positional = effective_positional_support_count(probe, graph, mode)
    accepted_defenses = sum(
        1
        for reply_attack in probe.reply_attacks
        if f"defense:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )
    unresolved_attacks = sum(
        1
        for reply_attack in probe.reply_attacks
        if f"reply_attack:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )
    if mode == "quiet":
        return (
            -move_rank,
            -accepted_tactical,
            unresolved_attacks,
            -accepted_positional,
            -accepted_defenses,
            -effective_score(probe, mode),
            probe.uci,
        )
    return (
        -accepted_tactical,
        unresolved_attacks,
        -material_or_promotion_gain(probe),
        -effective_score(probe, mode),
        -accepted_defenses,
        -move_rank,
        -accepted_positional,
        probe.uci,
    )


def support_selection_key(
    probe: MoveProbe,
    graph: RootArgumentGraph,
) -> tuple[Any, ...]:
    mode = positional_support_mode(graph)
    accepted_tactical = accepted_tactical_support_count(probe, graph)
    accepted_positional = effective_positional_support_count(probe, graph, mode)
    accepted_defenses = accepted_defense_count(probe, graph)
    unresolved_attacks = unresolved_attack_count(probe, graph)
    if mode == "quiet":
        return (
            -accepted_tactical,
            unresolved_attacks,
            -accepted_positional,
            -accepted_defenses,
            -effective_score(probe, mode),
            probe.uci,
        )
    return (
        -accepted_tactical,
        unresolved_attacks,
        -material_or_promotion_gain(probe),
        -effective_score(probe, mode),
        -accepted_defenses,
        -accepted_positional,
        probe.uci,
    )


def categoriser_selection_key(
    probe: MoveProbe,
    graph: RootArgumentGraph,
) -> tuple[Any, ...]:
    move_arg = graph.move_arguments[probe.uci]
    ranking_scores = graph.ranking.get("scores", {}) if graph.ranking.get("available") else {}
    move_rank = float(ranking_scores.get(move_arg, 0.0))
    mode = positional_support_mode(graph)
    if mode == "quiet":
        return (
            -move_rank,
            -accepted_tactical_support_count(probe, graph),
            unresolved_attack_count(probe, graph),
            -effective_positional_support_count(probe, graph, mode),
            -effective_score(probe, mode),
            probe.uci,
        )
    return (
        -accepted_tactical_support_count(probe, graph),
        unresolved_attack_count(probe, graph),
        -material_or_promotion_gain(probe),
        -effective_score(probe, mode),
        -move_rank,
        -effective_positional_support_count(probe, graph, mode),
        probe.uci,
    )


def accepted_support_count(probe: MoveProbe, graph: RootArgumentGraph) -> int:
    return sum(
        1
        for reason in probe.reasons
        if f"reason:{probe.uci}:{reason}" in graph.grounded_extension
    )


def accepted_tactical_support_count(probe: MoveProbe, graph: RootArgumentGraph) -> int:
    return _accepted_reason_count(probe, graph, is_tactical_reason)


def accepted_positional_support_count(probe: MoveProbe, graph: RootArgumentGraph) -> int:
    return _accepted_reason_count(probe, graph, is_positional_reason)


def effective_positional_support_count(
    probe: MoveProbe,
    graph: RootArgumentGraph,
    mode: str | None = None,
) -> int:
    if mode is None:
        mode = positional_support_mode(graph)
    if mode != "quiet":
        return 0
    return accepted_positional_support_count(probe, graph)


def positional_support_mode(graph: RootArgumentGraph, *, include_positional: bool = True) -> str:
    if not include_positional:
        return "disabled"
    if any(
        argument.startswith("reason:")
        and is_tactical_reason(argument.split(":", 2)[2])
        and argument in graph.grounded_extension
        for argument in graph.arguments
    ):
        return "tactical_gated"
    return "quiet"


def effective_score(probe: MoveProbe, mode: str) -> int:
    if mode == "quiet":
        return probe.score
    return probe.score - POSITIONAL_SCORE_BONUS * positional_reason_count(probe)


def positional_reason_count(probe: MoveProbe) -> int:
    return sum(1 for reason in probe.reasons if is_positional_reason(reason))


def material_or_promotion_gain(probe: MoveProbe) -> int:
    return probe.captured_value + probe.promotion_value


def is_positional_reason(reason: str) -> bool:
    return reason.startswith(POSITIONAL_REASON_PREFIXES)


def is_tactical_reason(reason: str) -> bool:
    if reason.startswith("smt:fork:"):
        parts = reason.split(":")
        return len(parts) == 4 and parts[2].isdigit() and parts[3].lstrip("-").isdigit()
    if reason.startswith("search_line:"):
        return False
    return reason.startswith(TACTICAL_REASON_PREFIXES)


def _accepted_reason_count(
    probe: MoveProbe,
    graph: RootArgumentGraph,
    predicate,
) -> int:
    return sum(
        1
        for reason in probe.reasons
        if predicate(reason)
        and f"reason:{probe.uci}:{reason}" in graph.grounded_extension
    )


def accepted_defense_count(probe: MoveProbe, graph: RootArgumentGraph) -> int:
    return sum(
        1
        for reply_attack in probe.reply_attacks
        if f"defense:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )


def unresolved_attack_count(probe: MoveProbe, graph: RootArgumentGraph) -> int:
    return sum(
        1
        for reply_attack in probe.reply_attacks
        if f"reply_attack:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )


def build_root_argument_graph(probes: list[MoveProbe]) -> RootArgumentGraph:
    arguments: set[str] = set()
    defeats: set[tuple[str, str]] = set()
    move_args = {probe.uci: f"move:{probe.uci}" for probe in probes}

    for probe in probes:
        move_arg = move_args[probe.uci]
        arguments.add(move_arg)
        for reason in probe.reasons:
            reason_arg = f"reason:{probe.uci}:{reason}"
            arguments.add(reason_arg)
            if reason == "terminal:checkmate":
                for other in probes:
                    if other.uci != probe.uci:
                        defeats.add((reason_arg, move_args[other.uci]))
        for objection in probe.objections:
            objection_arg = f"{objection}:{probe.uci}"
            arguments.add(objection_arg)
            defeats.add((objection_arg, move_arg))
        for reply_attack in probe.reply_attacks:
            reply_arg = f"reply_attack:{probe.uci}:{reply_attack}"
            arguments.add(reply_arg)
            defeats.add((reply_arg, move_arg))
            if ":defended:" in reply_attack:
                defense_arg = f"defense:{probe.uci}:{reply_attack}"
                arguments.add(defense_arg)
                defeats.add((defense_arg, reply_arg))

    frozen_arguments = frozenset(arguments)
    frozen_defeats = frozenset(defeats)
    grounded_extension = local_grounded_extension(frozen_arguments, frozen_defeats)
    ranking = local_argumentation_ranking(frozen_arguments, frozen_defeats)
    return RootArgumentGraph(
        arguments=frozen_arguments,
        defeats=frozen_defeats,
        move_arguments=move_args,
        grounded_extension=grounded_extension,
        ranking=ranking,
    )


def build_argument_payload(
    probes: list[MoveProbe],
    graph: RootArgumentGraph | None = None,
) -> dict[str, Any]:
    graph = graph or build_root_argument_graph(probes)
    return {
        "arguments": sorted(graph.arguments),
        "defeats": sorted([list(pair) for pair in graph.defeats]),
        "move_scores": [asdict(probe) for probe in probes],
        "move_arguments": dict(sorted(graph.move_arguments.items())),
        "grounded_extension": sorted(graph.grounded_extension),
        "argumentation_ranking": graph.ranking,
    }


def local_argumentation_ranking(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> dict[str, Any]:
    imported = import_local_argumentation()
    if isinstance(imported, str):
        return {"available": False, "reason": imported}
    ArgumentationFramework, _grounded_extension, categoriser_scores = imported
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)
    result = categoriser_scores(framework)
    return {
        "available": True,
        "scores": dict(sorted(result.scores.items())),
        "ranking": [sorted(tier) for tier in result.ranking],
        "semantics": result.semantics,
    }


def local_grounded_extension(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    imported = import_local_argumentation()
    if isinstance(imported, str):
        return frozenset()
    ArgumentationFramework, grounded_extension, _categoriser_scores = imported
    framework = ArgumentationFramework(arguments=arguments, defeats=defeats)
    return grounded_extension(framework)


def import_local_argumentation() -> tuple[Any, Any, Any] | str:
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from argumentation.dung import ArgumentationFramework, grounded_extension
        from argumentation.ranking import categoriser_scores
    except ImportError as exc:
        return str(exc)
    return ArgumentationFramework, grounded_extension, categoriser_scores
