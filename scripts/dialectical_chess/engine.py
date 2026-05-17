"""Unified engine API for dialectical chess move decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dialectical_chess.arguments import (
    MoveProbe,
    RootArgumentGraph,
    build_root_argument_graph,
    choose_move,
)
from dialectical_chess.probe import probe_moves


@dataclass(frozen=True)
class EngineSettings:
    dialectic_depth: int = 1
    search_depth: int = 0
    search_backend: str = "negamax"
    smt_mate: bool = True


@dataclass(frozen=True)
class EngineDecision:
    move_uci: str
    selected: MoveProbe | None

    @property
    def score(self) -> int | None:
        return None if self.selected is None else self.selected.score


@dataclass(frozen=True)
class EngineAnalysis:
    probes: tuple[MoveProbe, ...]
    graph: RootArgumentGraph
    decision: EngineDecision


class DialecticalChessEngine:
    """Reusable engine surface used by UCI, benchmarks, and probe adapters."""

    def __init__(self, settings: EngineSettings | None = None) -> None:
        self.settings = settings or EngineSettings()

    def analyze(self, board: Any) -> EngineAnalysis:
        probes = tuple(
            probe_moves(
                board,
                dialectic_depth=self.settings.dialectic_depth,
                search_depth=self.settings.search_depth,
                search_backend=self.settings.search_backend,
                smt_mate=self.settings.smt_mate,
            )
        )
        graph = build_root_argument_graph(list(probes))
        selected = choose_move(list(probes), graph) if probes else None
        decision = EngineDecision(
            move_uci="0000" if selected is None else selected.uci,
            selected=selected,
        )
        return EngineAnalysis(probes=probes, graph=graph, decision=decision)

    def choose_move(self, board: Any) -> EngineDecision:
        return self.analyze(board).decision
