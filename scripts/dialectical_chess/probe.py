"""Move probing for dialectical chess."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dialectical_chess.arguments import MoveProbe
from dialectical_chess.board import OwnedBoard
from dialectical_chess.search import (
    OWNED_PIECE_VALUE,
    SearchSettings,
    bounded_reply_attacks,
    owned_capture_value,
    owned_is_capture,
    owned_is_checkmate,
    root_search_result,
)
from dialectical_chess.smt import SmtSettings, smt_mate_in_one_moves


@dataclass(frozen=True)
class ProbeSettings:
    dialectic_depth: int = 1
    search: SearchSettings = field(default_factory=SearchSettings)
    smt: SmtSettings = field(default_factory=SmtSettings)


def probe_moves(
    board: Any,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
) -> list[MoveProbe]:
    settings = ProbeSettings(
        dialectic_depth=dialectic_depth,
        search=SearchSettings(depth=search_depth, backend=search_backend),
        smt=SmtSettings(mate_in_one=smt_mate),
    )
    return probe_moves_with_settings(board, settings)


def probe_moves_with_settings(board: Any, settings: ProbeSettings) -> list[MoveProbe]:
    if settings.dialectic_depth < 0:
        raise ValueError("dialectic_depth must be non-negative")
    if settings.search.depth < 0:
        raise ValueError("search_depth must be non-negative")
    board = ensure_owned_board(board)
    legal_moves = sorted(board.legal_moves(), key=lambda move: move.uci())
    smt_mate_moves = (
        smt_mate_in_one_moves(board) if settings.smt.mate_in_one else frozenset()
    )
    probes = []
    for move in legal_moves:
        san = move.uci()
        is_capture = owned_is_capture(board, move)
        captured_value = owned_capture_value(board, move)
        promotion_value = OWNED_PIECE_VALUE.get(move.promotion or "", 0)
        child = board.apply(move)
        is_checkmate = owned_is_checkmate(child)
        gives_check = child.in_check(child.turn)

        reasons: list[str] = []
        objections: list[str] = []
        score = 0

        if is_checkmate:
            score += 1_000_000
            reasons.append("terminal:checkmate")
        if gives_check:
            score += 1_000
            reasons.append("tactical:check")
        if is_capture:
            score += captured_value
            reasons.append(f"material:capture:{captured_value}")
        if promotion_value:
            score += promotion_value
            reasons.append(f"material:promotion:{promotion_value}")
        smt_witnesses: list[str] = []
        if move.uci() in smt_mate_moves:
            score += 1_000_000
            reasons.append("smt:mate_in_one")
            smt_witnesses.append("mate_in_one")
        search_result = root_search_result(board, move, settings=settings.search)
        if search_result is not None:
            if search_result.score > 0:
                reasons.append(f"search:{settings.search.backend}:{search_result.score}")
            elif search_result.score < 0:
                objections.append(f"search:{settings.search.backend}:{search_result.score}")
            score += search_result.score
        reply_attacks = bounded_reply_attacks(
            board,
            move,
            reply_depth=settings.dialectic_depth,
        )
        if not reasons:
            objections.append("objection:no_immediate_tactical_warrant")

        probes.append(
            MoveProbe(
                uci=move.uci(),
                san=san,
                score=score,
                is_checkmate=is_checkmate,
                gives_check=gives_check,
                is_capture=is_capture,
                captured_value=captured_value,
                promotion_value=promotion_value,
                reasons=tuple(reasons),
                objections=tuple(objections),
                reply_attacks=reply_attacks,
                search_score=None if search_result is None else search_result.score,
                search_line=() if search_result is None else search_result.line,
                smt_witnesses=tuple(smt_witnesses),
            )
        )
    return sorted(probes, key=lambda probe: (-probe.score, probe.uci))


def ensure_owned_board(board: Any) -> OwnedBoard:
    if isinstance(board, OwnedBoard):
        return board
    return owned_board_from_fen(board.fen())


def owned_board_from_fen(fen: str) -> OwnedBoard:
    return OwnedBoard.from_fen(fen)
