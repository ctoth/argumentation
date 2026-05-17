"""Unified engine API for dialectical chess move decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dialectical_chess.arguments import (
    MoveProbe,
    RootArgumentGraph,
    SELECTOR_MODES,
    build_root_argument_graph,
    choose_move,
)
from dialectical_chess.probe import probe_moves
from dialectical_chess.search import ReplyAnalysisSettings


@dataclass(frozen=True)
class EngineSettings:
    dialectic_depth: int = 1
    search_depth: int = 0
    search_backend: str = "negamax"
    smt_mate: bool = True
    smt_fork: bool = True
    selector_mode: str = "argument"
    positional_reasons: bool = True
    reply_analysis: ReplyAnalysisSettings = ReplyAnalysisSettings()

    def __post_init__(self) -> None:
        if self.selector_mode not in SELECTOR_MODES:
            raise ValueError(f"unknown selector_mode: {self.selector_mode}")


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
                smt_fork=self.settings.smt_fork,
                positional_reasons=self.settings.positional_reasons,
                reply_analysis=self.settings.reply_analysis,
            )
        )
        graph = build_root_argument_graph(list(probes))
        selected = choose_move(list(probes), graph, selector_mode=self.settings.selector_mode) if probes else None
        decision = EngineDecision(
            move_uci="0000" if selected is None else selected.uci,
            selected=selected,
        )
        return EngineAnalysis(probes=probes, graph=graph, decision=decision)

    def choose_move(self, board: Any) -> EngineDecision:
        return self.analyze(board).decision
